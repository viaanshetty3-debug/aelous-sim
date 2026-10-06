"""Multi-sensor fusion engine.

Combines Detections from every detector into a single calibrated hazard
posterior. The design keeps three properties:

1. **Spatial co-location** — detections only reinforce each other if they
   agree on *where*. A radar TDS 20 km from an infrasound bearing is less
   compelling than two signals pointing at the same lat/lon.
2. **Modality independence** — radar + infrasound + ground-truth are
   semi-independent error sources. We model this with a noisy-OR
   assuming per-modality false-alarm rates, so three *independent* HIGH
   detections drive posterior well above any single one.
3. **False-alarm suppression** — persistent 1-modality signals cost
   less than brief 3-modality concurrences; the fusion window is tight
   (currently 120 s).

Output: list[ThreatAssessment], one per spatially distinct cluster.
"""

from __future__ import annotations

import math
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Iterable, List

from ..types import (
    Detection,
    DetectionConfidence,
    GeoPoint,
    SensorKind,
    ThreatAssessment,
    ThreatLevel,
)


# ---------------------------------------------------------------------------
# Modality false-alarm rates (per-detection prior that a HIGH-band signal
# is a false alarm given no other evidence). Tuned to published literature;
# values are conservative placeholders.
# ---------------------------------------------------------------------------

MODALITY_FAR: Dict[SensorKind, float] = {
    SensorKind.DUAL_POL_RADAR: 0.25,
    SensorKind.INFRASOUND:     0.30,
    SensorKind.SEISMIC:        0.55,
    SensorKind.GROUND_TRUTH:   0.15,
    SensorKind.CROWDSOURCE:    0.60,
    SensorKind.WEATHER_APP:    0.50,
    SensorKind.SATELLITE_GLM:  0.70,
    SensorKind.MESONET:        0.65,
    SensorKind.SOCIAL:         0.65,
}


# ---------------------------------------------------------------------------
# Fusion engine
# ---------------------------------------------------------------------------


class FusionEngine:
    FUSION_RADIUS_M = 8_000.0           # join detections within 8 km
    FUSION_WINDOW_S = 120.0             # ...and within 2 min
    EMERGENCY_RAW_THRESHOLD = 0.92      # => Tornado Emergency
    WARNING_RAW_THRESHOLD = 0.70
    WATCH_RAW_THRESHOLD = 0.45
    ADVISORY_RAW_THRESHOLD = 0.20

    def fuse(
        self,
        detections: Iterable[Detection],
        *,
        hazard: str = "tornado",
    ) -> List[ThreatAssessment]:
        dets = [d for d in detections if d.confidence_raw > 0.0]
        if not dets:
            return []
        clusters = self._cluster(dets)
        return [self._assess(c, hazard) for c in clusters]

    # ---------------------------------------------------------- clustering

    def _cluster(self, dets: List[Detection]) -> List[List[Detection]]:
        """Greedy spatial-temporal clustering.

        Not DBSCAN — we favour explicit, debuggable behaviour over
        optimality at the scale (≤ a few hundred detections per minute).
        """
        clusters: List[List[Detection]] = []
        for d in sorted(dets, key=lambda x: x.timestamp):
            placed = False
            for c in clusters:
                anchor = c[0]
                if (
                    abs(d.timestamp - anchor.timestamp) <= self.FUSION_WINDOW_S
                    and d.location.haversine_m(anchor.location) <= self.FUSION_RADIUS_M
                ):
                    c.append(d)
                    placed = True
                    break
            if not placed:
                clusters.append([d])
        return clusters

    # ------------------------------------------------------------- assess

    def _assess(self, cluster: List[Detection], hazard: str) -> ThreatAssessment:
        # Per-modality: take max raw confidence per modality (independent events).
        per_mod: Dict[SensorKind, float] = defaultdict(float)
        contributing: List[str] = []
        for d in cluster:
            per_mod[d.kind] = max(per_mod[d.kind], d.confidence_raw)
            contributing.append(d.detection_id)

        # Noisy-OR fusion assuming conditional independence across modalities.
        prod_miss = 1.0
        for kind, conf in per_mod.items():
            far = MODALITY_FAR.get(kind, 0.5)
            # Treat the detection's raw as P(hazard | this modality fired),
            # subject to far-adjusted calibration.
            p_true = max(0.0, min(1.0, conf * (1.0 - far)))
            prod_miss *= (1.0 - p_true)
        posterior = 1.0 - prod_miss

        # Weight by modality diversity: 3 modalities confirming is better
        # than 3 very confident reports from one modality.
        diversity_bonus = min(0.15, 0.05 * (len(per_mod) - 1))
        posterior = min(1.0, posterior + diversity_bonus)

        level = self._level(posterior, per_mod)

        center = _weighted_centroid(cluster)

        # Lead time: take the max estimate across contributing detections.
        lead = max((d.lead_time_estimate_s for d in cluster), default=0.0)

        rationale_parts = []
        for kind, conf in sorted(per_mod.items(), key=lambda kv: -kv[1]):
            rationale_parts.append(f"{kind.value}={conf:.2f}")

        return ThreatAssessment(
            hazard=hazard,
            level=level,
            confidence=posterior,
            center=center,
            motion_bearing_deg=0.0,     # filled by StormScaleThreatModel
            motion_speed_mps=0.0,
            peak_intensity_estimate=self._estimate_intensity(per_mod, posterior),
            expected_lifetime_s=max(600.0, lead + 900.0),
            contributing_detections=contributing,
            rationale=f"posterior={posterior:.2f}, " + ", ".join(rationale_parts),
        )

    def _level(self, posterior: float, per_mod: Dict[SensorKind, float]) -> ThreatLevel:
        # Promote to EMERGENCY if a debris-on-the-ground signal is present
        # with corroboration.
        tds_present = per_mod.get(SensorKind.DUAL_POL_RADAR, 0.0) >= 0.75
        gt_strong = per_mod.get(SensorKind.GROUND_TRUTH, 0.0) >= 0.75
        if posterior >= self.EMERGENCY_RAW_THRESHOLD or (tds_present and gt_strong):
            return ThreatLevel.EMERGENCY
        if posterior >= self.WARNING_RAW_THRESHOLD:
            return ThreatLevel.WARNING
        if posterior >= self.WATCH_RAW_THRESHOLD:
            return ThreatLevel.WATCH
        if posterior >= self.ADVISORY_RAW_THRESHOLD:
            return ThreatLevel.ADVISORY
        return ThreatLevel.NONE

    def _estimate_intensity(self, per_mod: Dict[SensorKind, float], posterior: float) -> float:
        """Crude EF-scale estimate in [0, 5]."""
        base = 2.0 * posterior
        if per_mod.get(SensorKind.DUAL_POL_RADAR, 0.0) >= 0.9:
            base += 1.0
        if per_mod.get(SensorKind.INFRASOUND, 0.0) >= 0.8:
            base += 0.5
        if per_mod.get(SensorKind.GROUND_TRUTH, 0.0) >= 0.8:
            base += 1.0
        return max(0.0, min(5.0, base))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _weighted_centroid(dets: List[Detection]) -> GeoPoint:
    tw = sum(d.confidence_raw for d in dets) or 1.0
    lat = sum(d.location.lat * d.confidence_raw for d in dets) / tw
    lon = sum(d.location.lon * d.confidence_raw for d in dets) / tw
    return GeoPoint(lat, lon)


__all__ = ["FusionEngine", "MODALITY_FAR"]
