"""Integrated ground-truthing.

Human and sensor-on-the-ground reports:

- **Trained spotters** (SKYWARN, ARES): short-form reports with lat/lon,
  phenomenon code, confidence tier.
- **Storm chasers**: streaming video with GPS; we accept a boolean
  "visually confirmed tornado" plus geotag.
- **Emergency management / dispatch**: 911 call clusters tagged with
  "funnel cloud" or "damage".
- **Crowdsourced phone sensors**: pressure (barometric drop), 3-axis
  accelerometer (ground shake), microphone (broadband wind noise).
- **Vehicle telemetry**: wiper rate, ABS triggers (hail), airbag deploys
  (debris strikes).

The aggregator applies two safeguards:

1. **Trust tiers.** Trained spotter > first-responder > verified chaser >
   anonymous crowdsource. Each tier has a prior.
2. **Spatial clustering.** Isolated reports are weak; a cluster of ≥3
   reports within a 2 km radius inside a 5-minute window is strong.
"""

from __future__ import annotations

import math
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Deque, Dict, List, Tuple

from ..types import (
    Detection,
    GeoPoint,
    Observation,
    SensorKind,
)


# ---------------------------------------------------------------------------
# Trust tiers
# ---------------------------------------------------------------------------


TRUST_PRIORS: Dict[str, float] = {
    "nws_employee": 0.95,
    "trained_spotter": 0.85,
    "first_responder": 0.80,
    "verified_chaser": 0.75,
    "broadcast_meteorologist": 0.90,
    "amateur_report": 0.45,
    "crowdsource_phone": 0.40,
    "vehicle_telemetry": 0.55,
    "anonymous": 0.25,
}


# ---------------------------------------------------------------------------
# Rolling cache of recent reports
# ---------------------------------------------------------------------------


@dataclass
class _Report:
    timestamp: float
    location: GeoPoint
    reporter_tier: str
    phenomenon: str                     # "funnel_cloud" | "tornado_on_ground" | "pressure_drop" | ...
    note: str = ""


@dataclass
class _ClusterKey:
    cell_lat: float
    cell_lon: float


class GroundTruthAggregator:
    """Aggregates all `GROUND_TRUTH` and `CROWDSOURCE` observations."""

    CLUSTER_RADIUS_M = 2_000.0
    CLUSTER_WINDOW_S = 300.0
    MIN_CLUSTER_SIZE = 3

    def __init__(self, history_window_s: float = 600.0) -> None:
        self.history_window_s = history_window_s
        self._reports: Deque[_Report] = deque()

    # ------------------------------------------------------------------ api

    def detect(self, obs: Observation) -> List[Detection]:
        if obs.kind not in (SensorKind.GROUND_TRUTH, SensorKind.CROWDSOURCE):
            return []
        self._expire(obs.timestamp)
        r = _Report(
            timestamp=obs.timestamp,
            location=obs.location,
            reporter_tier=str(obs.payload.get("reporter_tier", "anonymous")),
            phenomenon=str(obs.payload.get("phenomenon", "unknown")),
            note=str(obs.payload.get("note", "")),
        )
        self._reports.append(r)

        detections: List[Detection] = []

        # High-trust singleton: a trained spotter screaming "tornado on
        # ground" is actionable by itself.
        prior = TRUST_PRIORS.get(r.reporter_tier, 0.25)
        if r.phenomenon in ("tornado_on_ground", "funnel_cloud") and prior >= 0.75:
            raw = prior * (1.0 if r.phenomenon == "tornado_on_ground" else 0.75)
            detections.append(
                Detection(
                    detector=f"ground_truth.{r.reporter_tier}",
                    kind=obs.kind,
                    timestamp=obs.timestamp,
                    location=obs.location,
                    confidence=Detection.band(raw),
                    confidence_raw=raw,
                    features={"trust_prior": prior},
                    notes=f"High-trust single report: {r.phenomenon} ({r.note!r}).",
                )
            )

        # Spatial cluster scan around this report.
        nearby = [
            x for x in self._reports
            if obs.location.haversine_m(x.location) <= self.CLUSTER_RADIUS_M
            and abs(obs.timestamp - x.timestamp) <= self.CLUSTER_WINDOW_S
        ]
        if len(nearby) >= self.MIN_CLUSTER_SIZE:
            weighted = sum(TRUST_PRIORS.get(x.reporter_tier, 0.25) for x in nearby)
            raw = min(1.0, 0.3 + 0.1 * len(nearby) + 0.05 * weighted)
            detections.append(
                Detection(
                    detector="ground_truth.cluster",
                    kind=obs.kind,
                    timestamp=obs.timestamp,
                    location=_centroid([x.location for x in nearby]),
                    confidence=Detection.band(raw),
                    confidence_raw=raw,
                    features={
                        "cluster_size": float(len(nearby)),
                        "weighted_trust": weighted,
                        "radius_m": self.CLUSTER_RADIUS_M,
                        "window_s": self.CLUSTER_WINDOW_S,
                    },
                    notes=f"Spatial cluster of {len(nearby)} ground reports.",
                )
            )

        # Phone-sensor-only cue: sharp pressure drop is a classic tornado
        # fingerprint when correlated with low wind-noise RMS (eye-like).
        if obs.kind is SensorKind.CROWDSOURCE:
            dp_dt = float(obs.payload.get("pressure_dpdt_hpa_per_s", 0.0))
            vibration = float(obs.payload.get("vibration_rms", 0.0))
            if dp_dt < -0.5 and vibration > 0.08:
                raw = min(1.0, 0.3 + abs(dp_dt) * 0.4 + vibration * 2.0)
                detections.append(
                    Detection(
                        detector="crowdsource.phone_signature",
                        kind=SensorKind.CROWDSOURCE,
                        timestamp=obs.timestamp,
                        location=obs.location,
                        confidence=Detection.band(raw),
                        confidence_raw=raw,
                        features={
                            "pressure_dpdt_hpa_per_s": dp_dt,
                            "vibration_rms": vibration,
                        },
                        notes="Phone pressure drop + ground vibration — "
                        "tornado-adjacent signature.",
                    )
                )
        return detections

    # -------------------------------------------------------------- helpers

    def _expire(self, now: float) -> None:
        while self._reports and (now - self._reports[0].timestamp) > self.history_window_s:
            self._reports.popleft()


def _centroid(points: List[GeoPoint]) -> GeoPoint:
    if not points:
        return GeoPoint(0.0, 0.0)
    lat = sum(p.lat for p in points) / len(points)
    lon = sum(p.lon for p in points) / len(points)
    return GeoPoint(lat, lon)


__all__ = ["GroundTruthAggregator", "TRUST_PRIORS"]
