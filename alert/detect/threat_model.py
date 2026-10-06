"""Storm-scale threat modeling.

Takes a `ThreatAssessment` (which locates the hazard *now*) and projects
it forward:

- Storm motion vector (bearing, speed) estimated from radar centroid
  history or from storm-tracking metadata if available.
- Expected lifetime based on intensity + environmental shear proxy.
- Impact corridor as a widening cone along the motion vector.
- Peak-intensity trajectory (growing, mature, decaying) via a simple
  logistic model keyed to lead time.

The threat model has state: it remembers the past N centroid positions
per cluster so it can estimate motion. Each cluster is tracked by its
`threat_id` once the fusion engine stabilises on one.
"""

from __future__ import annotations

import math
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Dict, List, Tuple

from ..types import GeoPoint, ThreatAssessment, ThreatLevel


# ---------------------------------------------------------------------------
# Rolling per-threat track
# ---------------------------------------------------------------------------


@dataclass
class _Track:
    positions: Deque[Tuple[float, GeoPoint]] = field(default_factory=deque)  # (t, pt)
    intensity_history: Deque[float] = field(default_factory=deque)
    first_seen: float = 0.0
    last_level: ThreatLevel = ThreatLevel.NONE


class StormScaleThreatModel:
    """Projects a `ThreatAssessment` forward and fills motion fields."""

    HISTORY_LEN = 20                    # ~5 min at 15 s cadence
    DEFAULT_SPEED_MPS = 13.0            # climatological supercell speed

    def __init__(self) -> None:
        self._tracks: Dict[str, _Track] = {}

    # ------------------------------------------------------------------ api

    def update(self, assessment: ThreatAssessment) -> ThreatAssessment:
        if assessment.center is None:
            return assessment
        tr = self._tracks.setdefault(assessment.threat_id, _Track(first_seen=assessment.created_at))
        tr.positions.append((assessment.created_at, assessment.center))
        tr.intensity_history.append(assessment.peak_intensity_estimate)
        while len(tr.positions) > self.HISTORY_LEN:
            tr.positions.popleft()
        while len(tr.intensity_history) > self.HISTORY_LEN:
            tr.intensity_history.popleft()
        tr.last_level = assessment.level

        bearing, speed = self._estimate_motion(tr)
        assessment.motion_bearing_deg = bearing
        assessment.motion_speed_mps = speed
        assessment.expected_lifetime_s = self._estimate_lifetime(tr, assessment)
        return assessment

    def project_corridor(
        self,
        assessment: ThreatAssessment,
        lead_s: float = 1_800.0,
        base_half_width_m: float = 500.0,
        growth_per_minute_m: float = 150.0,
    ) -> List[Tuple[float, float]]:
        """Return a widening polygon ring (lon, lat) representing the
        expected impact corridor over the next `lead_s` seconds.

        The corridor is a trapezoid aligned with motion. Width grows with
        time to account for both forecast uncertainty and the storm's own
        drift. Caller passes to the polygon builder.
        """
        if assessment.center is None:
            return []
        bearing = math.radians(assessment.motion_bearing_deg)
        speed = max(assessment.motion_speed_mps, self.DEFAULT_SPEED_MPS / 2)
        tip_dist = speed * lead_s
        tip = _advance(assessment.center, bearing, tip_dist)
        tip_half = base_half_width_m + growth_per_minute_m * (lead_s / 60.0)
        base_half = base_half_width_m

        perp = bearing + math.pi / 2
        center = assessment.center
        p1 = _advance(center, perp, base_half)
        p2 = _advance(center, perp + math.pi, base_half)
        p3 = _advance(tip, perp + math.pi, tip_half)
        p4 = _advance(tip, perp, tip_half)
        # Return as (lon, lat) ring, closed.
        return [
            (p1.lon, p1.lat),
            (p2.lon, p2.lat),
            (p3.lon, p3.lat),
            (p4.lon, p4.lat),
            (p1.lon, p1.lat),
        ]

    # ------------------------------------------------------------ motion

    def _estimate_motion(self, tr: _Track) -> Tuple[float, float]:
        if len(tr.positions) < 2:
            return 0.0, self.DEFAULT_SPEED_MPS
        # Use oldest ↔ newest in the window to average out noise.
        t0, p0 = tr.positions[0]
        t1, p1 = tr.positions[-1]
        dt = t1 - t0
        if dt <= 0:
            return 0.0, self.DEFAULT_SPEED_MPS
        d = p0.haversine_m(p1)
        speed = d / dt
        # Bearing: north = 0°, east = 90°
        lat1 = math.radians(p0.lat)
        lat2 = math.radians(p1.lat)
        dlon = math.radians(p1.lon - p0.lon)
        y = math.sin(dlon) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
        bearing = (math.degrees(math.atan2(y, x)) + 360.0) % 360.0
        return bearing, speed

    # --------------------------------------------------------- lifetime

    def _estimate_lifetime(self, tr: _Track, assessment: ThreatAssessment) -> float:
        """Logistic model.

        - Base: 900 s (15 min) for a cell that just produced a HIGH posterior.
        - Multiplier: 1.0 for ADVISORY, 1.5 for WARNING, 2.5 for EMERGENCY.
        - Intensity (EF estimate): adds up to 20 min at EF4+.
        """
        base = 900.0
        lvl_mult = {
            ThreatLevel.ADVISORY: 1.0,
            ThreatLevel.WATCH:    1.2,
            ThreatLevel.WARNING:  1.5,
            ThreatLevel.EMERGENCY: 2.5,
        }.get(assessment.level, 1.0)
        intensity_bonus = max(0.0, assessment.peak_intensity_estimate - 2.0) * 300.0
        age = time.time() - tr.first_seen
        decay = math.exp(-max(0.0, age - 1800.0) / 1200.0)
        return (base * lvl_mult + intensity_bonus) * (0.5 + 0.5 * decay)


# ---------------------------------------------------------------------------
# Geographic helpers
# ---------------------------------------------------------------------------


def _advance(start: GeoPoint, bearing_rad: float, distance_m: float) -> GeoPoint:
    """Move `distance_m` along `bearing_rad` from `start`, flat-earth."""
    dlat = (distance_m * math.cos(bearing_rad)) / 111_320.0
    dlon = (distance_m * math.sin(bearing_rad)) / (
        111_320.0 * math.cos(math.radians(start.lat))
    )
    return GeoPoint(start.lat + dlat, start.lon + dlon)


__all__ = ["StormScaleThreatModel"]
