"""Weather-app feed detector.

Modern consumer weather apps (Apple Weather, Google Weather, The Weather
Channel, AccuWeather, Weather Underground, Windy, YR, DWD WarnWetter,
JMA Safety Tips, …) all expose two useful things:

1. **Ingest.** They aggregate observations from hyper-local personal
   weather stations (PWS). Apple Weather absorbed Dark Sky's PWS network;
   Google Weather licenses Weather Underground's ~250k PWS feed. These
   stations fill the mesonet gap at ~1-5 km resolution.

2. **Egress.** They are the single highest-reach channel on Earth for
   weather information. If AEOLUS-ALERT can push an "imminent tornado"
   banner into Apple Weather, Google Weather, and Windy simultaneously,
   it reaches billions of installed devices without needing any carrier
   or OS vendor cooperation beyond a signed data feed.

This module handles the *ingest* side. Egress lives in
`dispatch/system_integration.py`.

The detector consumes homogenised JSON payloads from a feed adapter and
produces two kinds of detections:

- **Hyper-local anomaly** when a tight cluster of PWS report rapid
  pressure drop, wind spike, or temperature plunge inconsistent with the
  surrounding mesoscale field.
- **App-reported official warning crosspost** when the feed is already
  carrying a government warning for the same cell — a positive feedback
  used only to boost confidence, never as a sole trigger.

Payload fields:
  - ``station_id``: str
  - ``pressure_hpa``: float
  - ``pressure_tendency_hpa_per_min``: float
  - ``wind_speed_mps``: float
  - ``wind_gust_mps``: float
  - ``temperature_c``: float
  - ``temperature_tendency_c_per_min``: float
  - ``feed_vendor``: str   ("apple" | "google" | "wu" | "windy" | ...)
  - ``feed_contains_official_warning``: bool
  - ``feed_warning_hazard``: str (if above True)
"""

from __future__ import annotations

import math
import statistics
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Deque, Dict, List

from ..types import (
    Detection,
    GeoPoint,
    Observation,
    SensorKind,
)


# ---------------------------------------------------------------------------
# Per-station rolling stats
# ---------------------------------------------------------------------------


@dataclass
class _PWS:
    pressure: Deque[float] = field(default_factory=deque)
    pressure_dt: Deque[float] = field(default_factory=deque)
    wind: Deque[float] = field(default_factory=deque)
    gust: Deque[float] = field(default_factory=deque)
    temp: Deque[float] = field(default_factory=deque)
    temp_dt: Deque[float] = field(default_factory=deque)
    last_t: float = 0.0


class WeatherAppFeedDetector:
    """PWS-cluster anomaly detector + official-warning crosspost listener."""

    BUFFER_LEN = 60                     # keep ~1 h at 1 Hz feature cadence
    PRESS_DROP_HPA_PER_MIN = 1.0        # strong gradient
    GUST_SPIKE_MPS = 25.0
    TEMP_DROP_C_PER_MIN = 3.0
    CLUSTER_RADIUS_M = 5_000.0
    MIN_CLUSTER = 3

    def __init__(self) -> None:
        self._pws: Dict[str, _PWS] = {}
        self._last_known_locations: Dict[str, GeoPoint] = {}

    # ------------------------------------------------------------------ api

    def detect(self, obs: Observation) -> List[Detection]:
        if obs.kind is not SensorKind.WEATHER_APP:
            return []
        p = obs.payload
        s = self._pws.setdefault(obs.source_id, _PWS())
        self._last_known_locations[obs.source_id] = obs.location
        s.last_t = obs.timestamp

        self._push(s.pressure, float(p.get("pressure_hpa", math.nan)))
        self._push(s.pressure_dt, float(p.get("pressure_tendency_hpa_per_min", 0.0)))
        self._push(s.wind, float(p.get("wind_speed_mps", 0.0)))
        self._push(s.gust, float(p.get("wind_gust_mps", 0.0)))
        self._push(s.temp, float(p.get("temperature_c", math.nan)))
        self._push(s.temp_dt, float(p.get("temperature_tendency_c_per_min", 0.0)))

        detections: List[Detection] = []

        # ---- station-local anomaly ----
        anomaly = 0.0
        reasons: List[str] = []
        if s.pressure_dt and s.pressure_dt[-1] <= -self.PRESS_DROP_HPA_PER_MIN:
            anomaly += 0.4
            reasons.append(f"ΔP {s.pressure_dt[-1]:+.1f} hPa/min")
        if s.gust and s.gust[-1] >= self.GUST_SPIKE_MPS:
            anomaly += 0.3
            reasons.append(f"gust {s.gust[-1]:.0f} m/s")
        if s.temp_dt and s.temp_dt[-1] <= -self.TEMP_DROP_C_PER_MIN:
            anomaly += 0.2
            reasons.append(f"ΔT {s.temp_dt[-1]:+.1f} °C/min")

        vendor = str(p.get("feed_vendor", "unknown"))
        if p.get("feed_contains_official_warning") and p.get("feed_warning_hazard") == "tornado":
            # The user's installed app is *already* showing a government
            # tornado warning. Treat as a soft confirmation, never a
            # standalone trigger (to avoid circular amplification).
            detections.append(
                Detection(
                    detector=f"weather_app.{vendor}.crosspost",
                    kind=SensorKind.WEATHER_APP,
                    timestamp=obs.timestamp,
                    location=obs.location,
                    confidence=Detection.band(0.55),
                    confidence_raw=0.55,
                    features={"vendor_prior": 1.0},
                    notes=f"{vendor} feed already carrying an official tornado warning here.",
                )
            )

        if anomaly > 0.0:
            raw = min(1.0, anomaly)
            detections.append(
                Detection(
                    detector=f"weather_app.{vendor}.pws_anomaly",
                    kind=SensorKind.WEATHER_APP,
                    timestamp=obs.timestamp,
                    location=obs.location,
                    confidence=Detection.band(raw),
                    confidence_raw=raw,
                    features={
                        "pressure_dpdt_hpa_per_min": s.pressure_dt[-1] if s.pressure_dt else 0.0,
                        "wind_gust_mps": s.gust[-1] if s.gust else 0.0,
                        "temp_dt_c_per_min": s.temp_dt[-1] if s.temp_dt else 0.0,
                        "anomaly_score": anomaly,
                    },
                    notes=f"PWS anomaly ({', '.join(reasons)}) on {vendor} feed.",
                )
            )

        # ---- spatial cluster check ----
        cluster_hit = self._cluster_scan(obs)
        if cluster_hit is not None:
            detections.append(cluster_hit)

        return detections

    # -------------------------------------------------------- cluster scan

    def _cluster_scan(self, obs: Observation) -> Detection | None:
        """Count how many *currently anomalous* PWS surround this report."""
        n = 0
        drops: List[float] = []
        for sid, state in self._pws.items():
            loc = self._last_known_locations.get(sid)
            if loc is None:
                continue
            if obs.location.haversine_m(loc) > self.CLUSTER_RADIUS_M:
                continue
            if obs.timestamp - state.last_t > 120.0:
                continue
            dp = state.pressure_dt[-1] if state.pressure_dt else 0.0
            gust = state.gust[-1] if state.gust else 0.0
            if dp <= -0.5 * self.PRESS_DROP_HPA_PER_MIN or gust >= 0.5 * self.GUST_SPIKE_MPS:
                n += 1
                drops.append(dp)
        if n < self.MIN_CLUSTER:
            return None
        raw = min(1.0, 0.3 + 0.08 * n + 0.05 * abs(statistics.median(drops) if drops else 0.0))
        return Detection(
            detector="weather_app.pws_cluster",
            kind=SensorKind.WEATHER_APP,
            timestamp=obs.timestamp,
            location=obs.location,
            confidence=Detection.band(raw),
            confidence_raw=raw,
            features={"cluster_size": float(n), "median_dp": float(statistics.median(drops) if drops else 0.0)},
            notes=f"{n} PWS within 5 km reporting simultaneous pressure/wind anomalies.",
        )

    # -------------------------------------------------------------- buffers

    def _push(self, buf: Deque[float], v: float) -> None:
        buf.append(v)
        while len(buf) > self.BUFFER_LEN:
            buf.popleft()


__all__ = ["WeatherAppFeedDetector"]
