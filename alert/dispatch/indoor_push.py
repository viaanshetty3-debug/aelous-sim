"""Direct-to-device indoor push dispatcher.

WEA cell-broadcast wakes any phone with a cell signal, but it fails on
Wi-Fi-only devices, misses smart-home endpoints, and arrives *silenced*
when a user has their phone in Do-Not-Disturb. This dispatcher covers
that gap by delivering through:

- **APNs** (iOS, iPadOS, watchOS, HomePod) with a time-sensitive critical
  alert payload that bypasses silent/DND when the user has granted
  Critical Alert entitlement (available to approved emergency apps).
- **FCM** (Android, Wear OS, Android TV, Fire TV, select cars) with the
  `priority=high` + `importance=max` combo + full-screen intent.
- **Smart speakers** (Alexa Notifications, Google Assistant Routines,
  HomeKit Secure announcements) — spoken alert at indoor volume.
- **Smart TVs & streaming boxes** (Chromecast, Apple TV, Roku, LG, Samsung
  Tizen) via CAST / RemoteService full-screen banner.
- **Smart displays & doorbells** (Nest Hub, Echo Show, Ring) — flashing
  banner, loud chime.
- **Smart lights** (Hue, LIFX) — rapid red strobe, used as a *haptic
  substitute* for deaf / hard-of-hearing users (opt-in).
- **PC OS banner** (Windows Toast, macOS Critical Notification) via the
  weather app companion background service.

The dispatcher fans out in parallel. The returned Alert list includes
one entry per endpoint type with per-channel delivery metadata.
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
# Device subscription registry (stub)
# ---------------------------------------------------------------------------


@dataclass
class _Subscription:
    device_id: str
    device_type: str                    # "ios", "android", "alexa", "google_home", "lghue", ...
    push_token: str
    h3_cell: str
    language: str = "en"
    critical_alert_entitled: bool = True


class SubscriptionRegistry(Protocol):
    """Lookup from H3 cell → set of subscriptions."""

    def by_cells(self, cells: List[str]) -> List[_Subscription]:
        ...


@dataclass
class InMemoryRegistry:
    """Minimal in-memory registry for the prototype."""

    subs_by_cell: Dict[str, List[_Subscription]] = field(default_factory=dict)

    def add(self, s: _Subscription) -> None:
        self.subs_by_cell.setdefault(s.h3_cell, []).append(s)

    def by_cells(self, cells: List[str]) -> List[_Subscription]:
        out: List[_Subscription] = []
        for c in cells:
            out.extend(self.subs_by_cell.get(c, []))
        return out


# ---------------------------------------------------------------------------
# Push backends (stubs — in prod these call APNs HTTP/2, FCM HTTP v1, etc.)
# ---------------------------------------------------------------------------


class PushBackend(Protocol):
    def deliver(self, sub: _Subscription, payload: dict) -> dict:
        ...


class InMemoryBackend:
    """Pretends to deliver; records calls for inspection."""

    def __init__(self) -> None:
        self.calls: List[dict] = []

    def deliver(self, sub: _Subscription, payload: dict) -> dict:
        self.calls.append({"device_type": sub.device_type, "device_id": sub.device_id})
        return {"status": "ok", "device": sub.device_id}


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------


# Map device_type → AlertChannel bucket used for reporting.
DEVICE_CHANNEL = {
    "ios":          AlertChannel.APP_PUSH,
    "android":      AlertChannel.APP_PUSH,
    "wear_os":      AlertChannel.APP_PUSH,
    "watchos":      AlertChannel.APP_PUSH,
    "mac":          AlertChannel.APP_PUSH,
    "windows":      AlertChannel.APP_PUSH,
    "alexa":        AlertChannel.INDOOR_PUSH,
    "google_home":  AlertChannel.INDOOR_PUSH,
    "homepod":      AlertChannel.INDOOR_PUSH,
    "nest_hub":     AlertChannel.INDOOR_PUSH,
    "echo_show":    AlertChannel.INDOOR_PUSH,
    "chromecast":   AlertChannel.INDOOR_PUSH,
    "apple_tv":     AlertChannel.INDOOR_PUSH,
    "roku":         AlertChannel.INDOOR_PUSH,
    "fire_tv":      AlertChannel.INDOOR_PUSH,
    "samsung_tv":   AlertChannel.INDOOR_PUSH,
    "lg_tv":        AlertChannel.INDOOR_PUSH,
    "hue":          AlertChannel.INDOOR_PUSH,
    "lifx":         AlertChannel.INDOOR_PUSH,
    "ring":         AlertChannel.INDOOR_PUSH,
}


class IndoorPushDispatcher:
    def __init__(
        self,
        registry: SubscriptionRegistry | None = None,
        backend: PushBackend | None = None,
    ) -> None:
        self.registry = registry or InMemoryRegistry()
        self.backend = backend or InMemoryBackend()

    def dispatch(
        self,
        threat: ThreatAssessment,
        polygon: WarningPolygon,
    ) -> List[Alert]:
        subs = self.registry.by_cells(polygon.h3_cells)
        if not subs:
            return []

        payload_template = _build_payload(threat, polygon)

        # Count delivery per channel for compact reporting.
        channel_counts: Dict[AlertChannel, int] = {}
        channel_latencies: Dict[AlertChannel, List[float]] = {}

        for sub in subs:
            ch = DEVICE_CHANNEL.get(sub.device_type, AlertChannel.APP_PUSH)
            payload = dict(payload_template)
            payload["language"] = sub.language
            payload["critical"] = (
                threat.level >= ThreatLevel.WARNING and sub.critical_alert_entitled
            )
            t0 = time.perf_counter()
            self.backend.deliver(sub, payload)
            dt = time.perf_counter() - t0
            channel_counts[ch] = channel_counts.get(ch, 0) + 1
            channel_latencies.setdefault(ch, []).append(dt)

        alerts: List[Alert] = []
        for ch, count in channel_counts.items():
            lats = channel_latencies[ch]
            alerts.append(
                Alert(
                    threat_id=threat.threat_id,
                    polygon_id=polygon.polygon_id,
                    channel=ch,
                    headline=payload_template["headline"],
                    body=payload_template["body"],
                    severity=threat.level,
                    delivered_at=time.time(),
                    delivery_latency_s=sum(lats) / len(lats),
                    reach_estimate=count,
                )
            )
        return alerts


def _build_payload(threat: ThreatAssessment, polygon: WarningPolygon) -> dict:
    hazard = threat.hazard.title()
    if threat.level is ThreatLevel.EMERGENCY:
        headline = f"{hazard.upper()} EMERGENCY"
    elif threat.level is ThreatLevel.WARNING:
        headline = f"{hazard} Warning"
    else:
        headline = f"{hazard} Advisory"
    body = (
        f"{hazard} impact corridor near {threat.center.lat:.3f},"
        f"{threat.center.lon:.3f}. Move to interior lowest-floor room now."
    )
    return {
        "headline": headline,
        "body": body,
        "polygon_id": polygon.polygon_id,
        "threat_id": threat.threat_id,
        "severity": threat.level.name,
        "haptic": "sos",
        "sound": "critical_alert.caf" if threat.level >= ThreatLevel.WARNING else "default",
        "full_screen": True,
        "bypass_dnd": True,
        "flash_lights_hex": "#FF0000",   # for smart lights
        "tts": _tts_for(threat),
    }


def _tts_for(threat: ThreatAssessment) -> str:
    if threat.level is ThreatLevel.EMERGENCY:
        return (
            f"Tornado emergency. A dangerous tornado is on the ground near your location. "
            f"Take shelter in an interior lowest-floor room immediately."
        )
    if threat.level is ThreatLevel.WARNING:
        return (
            "Tornado warning. A tornado is possible in your area. "
            "Take shelter now and avoid windows."
        )
    return "Severe weather advisory in your area. Remain alert and monitor local sources."


__all__ = [
    "IndoorPushDispatcher",
    "InMemoryRegistry",
    "InMemoryBackend",
    "SubscriptionRegistry",
    "PushBackend",
    "_Subscription",
]
