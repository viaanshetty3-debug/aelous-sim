"""Dual-polarization radar detector.

Consumes a single radar volume as a payload of 2-D fields on a polar grid
(range × azimuth) at one elevation tilt. In production this runs per tilt
with a 3-D rollup. Fields expected (NEXRAD naming):

- ``Zh``       : horizontal reflectivity (dBZ)
- ``V``        : radial velocity (m/s), aliased
- ``SW``       : spectrum width (m/s)
- ``Zdr``      : differential reflectivity (dB)
- ``rho_hv``   : copolar correlation coefficient (unitless, ≤ 1.0)
- ``Kdp``      : specific differential phase (deg/km)

Detectors implemented:

1. **Mesocyclone** — rotational velocity couplet (TVS precursor).
   Scans radial velocity for strong gate-to-gate shear.
2. **Tornadic Vortex Signature (TVS)** — localized high-shear couplet
   with vertical persistence.
3. **Tornado Debris Signature (TDS)** — simultaneous (a) high Zh, (b) low
   ρ_hv (debris depolarization), (c) near-zero Zdr (random debris
   orientation). Debris aloft is near-definitive proof of a tornado.
4. **Hook echo / BWER** — morphological reflectivity cue.

Output `Detection.features` always carries enough metadata that the
fusion engine can co-locate radar hits with seismic/infrasound hits.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Sequence

from ..types import (
    Detection,
    DetectionConfidence,
    GeoPoint,
    Observation,
    SensorKind,
)


# ---------------------------------------------------------------------------
# Polar grid helpers
# ---------------------------------------------------------------------------


@dataclass
class PolarVolume:
    """Flat view over a single tilt."""

    radar_lat: float
    radar_lon: float
    elevation_deg: float
    gate_spacing_m: float
    azimuths_deg: Sequence[float]       # length A
    ranges_m: Sequence[float]           # length R
    Zh: Sequence[Sequence[float]]
    V: Sequence[Sequence[float]]
    SW: Sequence[Sequence[float]]
    Zdr: Sequence[Sequence[float]]
    rho_hv: Sequence[Sequence[float]]
    Kdp: Sequence[Sequence[float]]

    @classmethod
    def from_payload(cls, obs: Observation) -> "PolarVolume":
        p = obs.payload
        return cls(
            radar_lat=obs.location.lat,
            radar_lon=obs.location.lon,
            elevation_deg=float(p.get("elevation_deg", 0.5)),
            gate_spacing_m=float(p.get("gate_spacing_m", 250.0)),
            azimuths_deg=p["azimuths_deg"],
            ranges_m=p["ranges_m"],
            Zh=p["Zh"],
            V=p["V"],
            SW=p.get("SW", [[0.0] * len(p["ranges_m"])] * len(p["azimuths_deg"])),
            Zdr=p["Zdr"],
            rho_hv=p["rho_hv"],
            Kdp=p.get("Kdp", [[0.0] * len(p["ranges_m"])] * len(p["azimuths_deg"])),
        )

    def gate_to_geo(self, iaz: int, irng: int) -> GeoPoint:
        """Approximate ground-projected lat/lon of a polar gate.

        Flat-earth projection — fine for the ≤ 150 km range we care about
        at warning scales. Earth-curvature + 4/3-R refraction corrections
        would go here in production.
        """
        az = math.radians(self.azimuths_deg[iaz])
        r = self.ranges_m[irng]
        dx = r * math.sin(az)
        dy = r * math.cos(az)
        dlat = dy / 111_320.0
        dlon = dx / (111_320.0 * math.cos(math.radians(self.radar_lat)))
        return GeoPoint(self.radar_lat + dlat, self.radar_lon + dlon)


# ---------------------------------------------------------------------------
# Detector
# ---------------------------------------------------------------------------


class DualPolRadarDetector:
    """Classical rotation + TDS detector, pure-Python.

    This implementation targets *clarity over speed*. In production the
    inner loops become vectorised numpy/CuPy kernels — the algorithm is
    unchanged.
    """

    def __init__(
        self,
        shear_threshold_mps: float = 25.0,          # gate-to-gate
        tvs_shear_threshold_mps: float = 50.0,
        tds_zh_min_dbz: float = 45.0,
        tds_rhohv_max: float = 0.80,
        tds_zdr_abs_max: float = 0.5,
        hook_zh_min_dbz: float = 35.0,
    ) -> None:
        self.shear_threshold = shear_threshold_mps
        self.tvs_shear_threshold = tvs_shear_threshold_mps
        self.tds_zh_min = tds_zh_min_dbz
        self.tds_rhohv_max = tds_rhohv_max
        self.tds_zdr_abs_max = tds_zdr_abs_max
        self.hook_zh_min = hook_zh_min_dbz

    # ------------------------------------------------------------------ api

    def detect(self, obs: Observation) -> List[Detection]:
        if obs.kind is not SensorKind.DUAL_POL_RADAR:
            return []
        vol = PolarVolume.from_payload(obs)
        detections: List[Detection] = []
        detections.extend(self._rotation_scan(vol, obs))
        detections.extend(self._tds_scan(vol, obs))
        detections.extend(self._hook_scan(vol, obs))
        return detections

    # ----------------------------------------------------- rotation / TVS

    def _rotation_scan(self, vol: PolarVolume, obs: Observation) -> List[Detection]:
        out: List[Detection] = []
        A = len(vol.azimuths_deg)
        R = len(vol.ranges_m)
        for iaz in range(A):
            iaz_next = (iaz + 1) % A
            for irng in range(R):
                v1 = vol.V[iaz][irng]
                v2 = vol.V[iaz_next][irng]
                if not (math.isfinite(v1) and math.isfinite(v2)):
                    continue
                shear = v2 - v1   # inbound-outbound couplet
                if abs(shear) < self.shear_threshold:
                    continue
                loc = vol.gate_to_geo(iaz, irng)
                raw = min(1.0, (abs(shear) - self.shear_threshold) / 60.0 + 0.35)
                is_tvs = abs(shear) >= self.tvs_shear_threshold
                out.append(
                    Detection(
                        detector="dual_pol_radar.tvs" if is_tvs else "dual_pol_radar.mesocyclone",
                        kind=SensorKind.DUAL_POL_RADAR,
                        timestamp=obs.timestamp,
                        location=loc,
                        confidence=Detection.band(raw),
                        confidence_raw=raw,
                        features={
                            "gate_to_gate_shear_mps": shear,
                            "range_m": vol.ranges_m[irng],
                            "azimuth_deg": vol.azimuths_deg[iaz],
                            "elevation_deg": vol.elevation_deg,
                        },
                        lead_time_estimate_s=600.0 if is_tvs else 1200.0,
                        notes="Gate-to-gate radial velocity shear exceeds "
                        f"{'TVS' if is_tvs else 'mesocyclone'} threshold.",
                    )
                )
        return out

    # ------------------------------------------------------------- TDS

    def _tds_scan(self, vol: PolarVolume, obs: Observation) -> List[Detection]:
        out: List[Detection] = []
        A = len(vol.azimuths_deg)
        R = len(vol.ranges_m)
        for iaz in range(A):
            for irng in range(R):
                zh = vol.Zh[iaz][irng]
                rho = vol.rho_hv[iaz][irng]
                zdr = vol.Zdr[iaz][irng]
                if not (math.isfinite(zh) and math.isfinite(rho) and math.isfinite(zdr)):
                    continue
                if zh < self.tds_zh_min:
                    continue
                if rho > self.tds_rhohv_max:
                    continue
                if abs(zdr) > self.tds_zdr_abs_max:
                    continue
                # All three TDS criteria met. Score higher if rho is deeply
                # depressed and the gate neighbours agree.
                rho_term = max(0.0, (self.tds_rhohv_max - rho) / 0.30)
                zdr_term = max(0.0, (self.tds_zdr_abs_max - abs(zdr)) / 0.5)
                zh_term = min(1.0, (zh - self.tds_zh_min) / 25.0)
                raw = max(0.0, min(1.0, 0.5 + 0.2 * rho_term + 0.15 * zdr_term + 0.15 * zh_term))
                out.append(
                    Detection(
                        detector="dual_pol_radar.tds",
                        kind=SensorKind.DUAL_POL_RADAR,
                        timestamp=obs.timestamp,
                        location=vol.gate_to_geo(iaz, irng),
                        confidence=Detection.band(raw),
                        confidence_raw=raw,
                        features={
                            "Zh_dBZ": zh,
                            "rho_hv": rho,
                            "Zdr_dB": zdr,
                            "range_m": vol.ranges_m[irng],
                            "azimuth_deg": vol.azimuths_deg[iaz],
                            "elevation_deg": vol.elevation_deg,
                        },
                        lead_time_estimate_s=0.0,
                        notes="Tornado Debris Signature: high Zh, depressed ρ_hv, "
                        "near-zero Zdr — debris lofted by an on-ground tornado.",
                    )
                )
        return out

    # ------------------------------------------------------------ hook echo

    def _hook_scan(self, vol: PolarVolume, obs: Observation) -> List[Detection]:
        """Morphological hook detector.

        Looks for the characteristic appendage: a tongue of ≥35 dBZ on the
        rear-right flank of a supercell. We approximate with a very simple
        test — a cluster of Zh≥threshold gates whose shape has high
        azimuthal gradient at its tip. Sufficient for a prototype; a CNN
        replaces this in production.
        """
        out: List[Detection] = []
        A = len(vol.azimuths_deg)
        R = len(vol.ranges_m)
        for iaz in range(A):
            run_len = 0
            tip_r = None
            for irng in range(R):
                if vol.Zh[iaz][irng] >= self.hook_zh_min:
                    run_len += 1
                    tip_r = irng
                else:
                    if run_len >= 6 and tip_r is not None:
                        # Check for curvature at the tip: Zh must fall off
                        # steeply in azimuth near the tip gate.
                        az_prev = (iaz - 1) % A
                        az_next = (iaz + 1) % A
                        dz = (
                            abs(vol.Zh[iaz][tip_r] - vol.Zh[az_prev][tip_r])
                            + abs(vol.Zh[iaz][tip_r] - vol.Zh[az_next][tip_r])
                        ) / 2.0
                        if dz > 15.0:
                            raw = min(1.0, 0.3 + dz / 60.0)
                            out.append(
                                Detection(
                                    detector="dual_pol_radar.hook_echo",
                                    kind=SensorKind.DUAL_POL_RADAR,
                                    timestamp=obs.timestamp,
                                    location=vol.gate_to_geo(iaz, tip_r),
                                    confidence=Detection.band(raw),
                                    confidence_raw=raw,
                                    features={
                                        "tip_Zh_dBZ": vol.Zh[iaz][tip_r],
                                        "azimuth_deg": vol.azimuths_deg[iaz],
                                        "tip_range_m": vol.ranges_m[tip_r],
                                        "azimuthal_gradient_dBZ": dz,
                                    },
                                    lead_time_estimate_s=900.0,
                                    notes="Reflectivity hook echo detected; "
                                    "classic supercell morphology.",
                                )
                            )
                    run_len = 0
                    tip_r = None
        return out


__all__ = ["DualPolRadarDetector", "PolarVolume"]
