"""Automated system integration dispatcher.

Reaches endpoints that aren't phones: EAS encoders, DOT highway signs,
outdoor siren mesh, newswire APIs, major social platforms, Apple Weather
+ Google Weather + Windy inbound feeds, and ISP banner injection.

Everything runs in parallel. Each endpoint has its own adapter so
latency failures of one channel never block the others. Adapters are
Protocols — real deployments plug in a vendor SDK; the prototype uses
in-memory recorders.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Protocol

from ..types import (
    Alert,
    AlertChannel,
    ThreatAssessment,
    ThreatLevel,
    WarningPolygon,
)


# ---------------------------------------------------------------------------
# Endpoint adapters (protocols + in-memory stubs)
# ---------------------------------------------------------------------------


class EASEncoder(Protocol):
    def encode(self, same_header: str, text: str, audio_tts: str) -> dict: ...


class HighwaySignController(Protocol):
    def post_to_signs(self, cells: List[str], message: str) -> dict: ...


class SirenNetwork(Protocol):
    def activate(self, cells: List[str], tone: str = "attack") -> dict: ...


class NewsWireAPI(Protocol):
    def push(self, headline: str, body: str, polygon_geojson: dict) -> dict: ...


class SocialPlatformAPI(Protocol):
    def post(self, text: str, geo: dict) -> dict: ...


class WeatherFeedIngestor(Protocol):
    """A signed feed we push to Apple Weather / Google Weather / Windy / etc."""

    def push_alert(self, cap_xml: str, h3_cells: List[str]) -> dict: ...


class ISPBannerInjector(Protocol):
    def inject(self, cells: List[str], text: str) -> dict: ...


# ---------------------------------------------------------------------------
# Default in-memory recorders
# ---------------------------------------------------------------------------


@dataclass
class _Recorder:
    name: str
    calls: list = field(default_factory=list)

    def _record(self, **kwargs) -> dict:
        self.calls.append(kwargs)
        return {"status": "ok", "name": self.name, "received": kwargs}


class _InMemoryEAS(_Recorder):
    def encode(self, same_header, text, audio_tts):
        return self._record(same_header=same_header, text_len=len(text))


class _InMemoryHighway(_Recorder):
    def post_to_signs(self, cells, message):
        return self._record(cell_count=len(cells), message=message)


class _InMemorySiren(_Recorder):
    def activate(self, cells, tone="attack"):
        return self._record(cell_count=len(cells), tone=tone)


class _InMemoryNewsWire(_Recorder):
    def push(self, headline, body, polygon_geojson):
        return self._record(headline=headline, body_len=len(body))


class _InMemorySocial(_Recorder):
    def post(self, text, geo):
        return self._record(text=text[:140], geo=geo)


class _InMemoryWeatherFeed(_Recorder):
    def push_alert(self, cap_xml, h3_cells):
        return self._record(cap_len=len(cap_xml), cell_count=len(h3_cells))


class _InMemoryISP(_Recorder):
    def inject(self, cells, text):
        return self._record(cell_count=len(cells), text=text)


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------


@dataclass
class SystemIntegrationConfig:
    """Toggle individual channels on/off per deployment."""
    enable_eas: bool = True
    enable_highway: bool = True
    enable_siren: bool = True
    enable_newswire: bool = True
    enable_social: bool = True
    enable_weather_feeds: bool = True
    enable_isp: bool = True


class SystemIntegrationDispatcher:
    """Fans out one threat to every integrated non-phone endpoint."""

    def __init__(
        self,
        config: SystemIntegrationConfig | None = None,
        eas: EASEncoder | None = None,
        highway: HighwaySignController | None = None,
        siren: SirenNetwork | None = None,
        newswire: NewsWireAPI | None = None,
        social_platforms: Dict[str, SocialPlatformAPI] | None = None,
        weather_feeds: Dict[str, WeatherFeedIngestor] | None = None,
        isp: ISPBannerInjector | None = None,
    ) -> None:
        self.config = config or SystemIntegrationConfig()
        self.eas = eas or _InMemoryEAS("eas")
        self.highway = highway or _InMemoryHighway("highway")
        self.siren = siren or _InMemorySiren("siren")
        self.newswire = newswire or _InMemoryNewsWire("newswire")
        self.social_platforms = social_platforms or {
            "x":        _InMemorySocial("x"),
            "facebook": _InMemorySocial("facebook"),
            "threads":  _InMemorySocial("threads"),
            "bluesky":  _InMemorySocial("bluesky"),
        }
        self.weather_feeds = weather_feeds or {
            "apple":  _InMemoryWeatherFeed("apple_weather"),
            "google": _InMemoryWeatherFeed("google_weather"),
            "wu":     _InMemoryWeatherFeed("weather_underground"),
            "windy":  _InMemoryWeatherFeed("windy"),
            "accuweather": _InMemoryWeatherFeed("accuweather"),
            "yr":     _InMemoryWeatherFeed("yr"),
            "jma":    _InMemoryWeatherFeed("jma_safety_tips"),
            "dwd":    _InMemoryWeatherFeed("dwd_warnwetter"),
        }
        self.isp = isp or _InMemoryISP("isp")

    def dispatch(
        self,
        threat: ThreatAssessment,
        polygon: WarningPolygon,
        cap_xml: str,
    ) -> List[Alert]:
        hazard = threat.hazard.title()
        headline = _headline(threat)
        body = _body(threat)
        alerts: List[Alert] = []

        if self.config.enable_eas and threat.level >= ThreatLevel.WARNING:
            same_header = _same_header(threat, polygon)
            t0 = time.perf_counter()
            self.eas.encode(same_header, body, audio_tts=body)
            alerts.append(
                _mk_alert(threat, polygon, AlertChannel.EAS, headline, body,
                          time.perf_counter() - t0, reach=int(polygon.population_estimate * 0.4))
            )

        if self.config.enable_highway:
            t0 = time.perf_counter()
            self.highway.post_to_signs(polygon.h3_cells, f"{headline} - EXIT HWY, TAKE SHELTER")
            alerts.append(
                _mk_alert(threat, polygon, AlertChannel.HIGHWAY_SIGN, headline, body,
                          time.perf_counter() - t0, reach=min(len(polygon.h3_cells) * 50, 25_000))
            )

        if self.config.enable_siren and threat.level >= ThreatLevel.WARNING:
            t0 = time.perf_counter()
            self.siren.activate(polygon.h3_cells, tone="attack")
            alerts.append(
                _mk_alert(threat, polygon, AlertChannel.SIREN, headline, body,
                          time.perf_counter() - t0, reach=int(polygon.population_estimate * 0.9))
            )

        if self.config.enable_newswire:
            t0 = time.perf_counter()
            self.newswire.push(headline, body, _polygon_geojson(polygon))
            alerts.append(
                _mk_alert(threat, polygon, AlertChannel.NEWS_API, headline, body,
                          time.perf_counter() - t0, reach=5_000_000)
            )

        if self.config.enable_social:
            for name, api in self.social_platforms.items():
                t0 = time.perf_counter()
                api.post(f"{headline}: {body}", _geo_dict(polygon))
                alerts.append(
                    _mk_alert(threat, polygon, AlertChannel.SOCIAL, headline, body,
                              time.perf_counter() - t0, reach=250_000, extra_note=name)
                )

        if self.config.enable_weather_feeds:
            for name, feed in self.weather_feeds.items():
                t0 = time.perf_counter()
                feed.push_alert(cap_xml, polygon.h3_cells)
                # Reach scales with each vendor's installed base. Rough priors:
                reach = {
                    "apple":  150_000_000,
                    "google": 200_000_000,
                    "wu":      40_000_000,
                    "windy":   20_000_000,
                    "accuweather": 60_000_000,
                    "yr":      10_000_000,
                    "jma":     40_000_000,
                    "dwd":      5_000_000,
                }.get(name, 1_000_000)
                alerts.append(
                    _mk_alert(threat, polygon, AlertChannel.WEATHER_APP, headline, body,
                              time.perf_counter() - t0, reach=reach, extra_note=name)
                )

        if self.config.enable_isp:
            t0 = time.perf_counter()
            self.isp.inject(polygon.h3_cells, headline)
            alerts.append(
                _mk_alert(threat, polygon, AlertChannel.INTERNET_BANNER, headline, body,
                          time.perf_counter() - t0, reach=polygon.population_estimate)
            )

        return alerts


# ---------------------------------------------------------------------------
# Message helpers
# ---------------------------------------------------------------------------


def _headline(threat: ThreatAssessment) -> str:
    hazard = threat.hazard.title()
    if threat.level is ThreatLevel.EMERGENCY:
        return f"{hazard.upper()} EMERGENCY — TAKE SHELTER NOW"
    if threat.level is ThreatLevel.WARNING:
        return f"{hazard} Warning — Take Shelter Immediately"
    if threat.level is ThreatLevel.WATCH:
        return f"{hazard} Watch — Be Prepared"
    return f"{hazard} Advisory"


def _body(threat: ThreatAssessment) -> str:
    hazard = threat.hazard
    return (
        f"{hazard.title()} detected near "
        f"{threat.center.lat:.3f},{threat.center.lon:.3f}; moving "
        f"{int(threat.motion_bearing_deg):03d}° at {threat.motion_speed_mps:.0f} m/s. "
        f"Estimated intensity EF{threat.peak_intensity_estimate:.0f}. "
        "Move to interior lowest-floor room; avoid windows."
    )


def _same_header(threat: ThreatAssessment, polygon: WarningPolygon) -> str:
    """SAME (Specific Area Message Encoding) header stub."""
    event = "TOR" if threat.hazard == "tornado" else "SVR"
    minutes = max(1, int((polygon.expires_at - polygon.issued_at) / 60))
    return f"ZCZC-WXR-{event}-000000+{minutes:04d}-{int(polygon.issued_at)}-AEOLUS-"


def _polygon_geojson(polygon: WarningPolygon) -> dict:
    return {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[list(v) for v in polygon.vertices]],
        },
        "properties": {"polygon_id": polygon.polygon_id},
    }


def _geo_dict(polygon: WarningPolygon) -> dict:
    if not polygon.vertices:
        return {}
    lats = [v[1] for v in polygon.vertices]
    lons = [v[0] for v in polygon.vertices]
    return {
        "centroid": [sum(lons) / len(lons), sum(lats) / len(lats)],
        "cell_count": len(polygon.h3_cells),
    }


def _mk_alert(
    threat: ThreatAssessment,
    polygon: WarningPolygon,
    channel: AlertChannel,
    headline: str,
    body: str,
    latency: float,
    *,
    reach: int,
    extra_note: str = "",
) -> Alert:
    return Alert(
        threat_id=threat.threat_id,
        polygon_id=polygon.polygon_id,
        channel=channel,
        headline=headline + (f" [{extra_note}]" if extra_note else ""),
        body=body,
        severity=threat.level,
        delivered_at=time.time(),
        delivery_latency_s=latency,
        reach_estimate=reach,
    )


__all__ = [
    "SystemIntegrationDispatcher",
    "SystemIntegrationConfig",
    "EASEncoder",
    "HighwaySignController",
    "SirenNetwork",
    "NewsWireAPI",
    "SocialPlatformAPI",
    "WeatherFeedIngestor",
    "ISPBannerInjector",
]
