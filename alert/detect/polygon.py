"""Hyper-localized warning polygon builder.

Takes a `ThreatAssessment` + a projected impact corridor and emits a
`WarningPolygon` whose H3 res-8 cell set is the targeting key for
dispatch. Properties:

- Polygons are *tight*: the goal is to minimise false-target volume so
  alert fatigue doesn't erode trust. We'd rather issue a 3 km × 20 km
  corridor than a 20 km × 60 km county-wide box.
- Polygons are *dynamic*: they re-issue every 60 s as the storm motion
  estimate updates. Each issuance supersedes the previous.
- Polygons carry a *population estimate* using an injected
  `PopulationEstimator` (gridded population, e.g. WorldPop at 100 m).

H3 is implemented in-tree with a stub: we approximate res-8 cells by
quantising lat/lon to a ~0.7 km grid. In production this calls the H3
library directly.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import Callable, List, Tuple

from ..types import GeoPoint, ThreatAssessment, WarningPolygon


# ---------------------------------------------------------------------------
# H3-ish quantiser (stand-in; real H3 at import time if available)
# ---------------------------------------------------------------------------


try:
    import h3                            # type: ignore

    def _polyfill(ring_lonlat: List[Tuple[float, float]], res: int = 8) -> List[str]:
        geo = {"type": "Polygon", "coordinates": [[(lat, lon) for lon, lat in ring_lonlat]]}
        return list(h3.polyfill(geo, res))
except Exception:  # pragma: no cover — fallback when h3 isn't installed
    _H3_PSEUDO_RES_M = 700.0

    def _polyfill(ring_lonlat: List[Tuple[float, float]], res: int = 8) -> List[str]:
        if not ring_lonlat:
            return []
        lats = [p[1] for p in ring_lonlat]
        lons = [p[0] for p in ring_lonlat]
        lat_min, lat_max = min(lats), max(lats)
        lon_min, lon_max = min(lons), max(lons)
        step_lat = _H3_PSEUDO_RES_M / 111_320.0
        mean_lat = (lat_min + lat_max) / 2.0
        step_lon = _H3_PSEUDO_RES_M / (111_320.0 * max(0.1, math.cos(math.radians(mean_lat))))
        cells: List[str] = []
        lat = lat_min
        while lat <= lat_max:
            lon = lon_min
            while lon <= lon_max:
                if _point_in_polygon(lon, lat, ring_lonlat):
                    cells.append(f"pseudo8_{lat:.4f}_{lon:.4f}")
                lon += step_lon
            lat += step_lat
        return cells


def _point_in_polygon(x: float, y: float, ring: List[Tuple[float, float]]) -> bool:
    inside = False
    n = len(ring)
    for i in range(n):
        x1, y1 = ring[i]
        x2, y2 = ring[(i + 1) % n]
        if ((y1 > y) != (y2 > y)) and (
            x < (x2 - x1) * (y - y1) / ((y2 - y1) + 1e-12) + x1
        ):
            inside = not inside
    return inside


# ---------------------------------------------------------------------------
# Population estimator interface
# ---------------------------------------------------------------------------


PopulationEstimator = Callable[[List[str]], int]
"""Takes an H3 cell list, returns an integer population estimate."""


def default_population_estimator(cells: List[str]) -> int:
    # 2 500 persons per 0.7 km² is roughly the median density inside tornado-
    # prone metropolitan corridors; replace with real gridded data in prod.
    return int(2500 * len(cells))


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------


class HyperLocalPolygonBuilder:
    def __init__(
        self,
        population_estimator: PopulationEstimator = default_population_estimator,
        validity_s: float = 60.0,
        h3_resolution: int = 8,
    ) -> None:
        self.population_estimator = population_estimator
        self.validity_s = validity_s
        self.h3_resolution = h3_resolution

    def build(
        self,
        assessment: ThreatAssessment,
        corridor_ring_lonlat: List[Tuple[float, float]],
    ) -> WarningPolygon:
        now = time.time()
        cells = _polyfill(corridor_ring_lonlat, res=self.h3_resolution)
        pop = self.population_estimator(cells)
        return WarningPolygon(
            threat_id=assessment.threat_id,
            issued_at=now,
            expires_at=now + self.validity_s,
            vertices=corridor_ring_lonlat,
            h3_cells=cells,
            population_estimate=pop,
        )


__all__ = ["HyperLocalPolygonBuilder", "PopulationEstimator", "default_population_estimator"]
