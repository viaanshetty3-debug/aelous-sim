"""End-to-end AEOLUS-ALERT prototype driver.

Synthesises one plausible tornadic event and runs it through the entire
pipeline:

   radar obs ─┐
    seismic ──┤
  infrasound ─┼─► detectors ─► fusion ─► threat model ─► polygon ─► dispatch
 ground truth─┤
  weather app ┤
  signal ─────┘

Prints a latency / reach report so you can see what the pipeline would
produce under this scenario.

Run:
    python -m alert.prototype_run
"""

from __future__ import annotations

import math
import random
import time
from typing import List

from .types import (
    Alert,
    AlertChannel,
    Detection,
    GeoPoint,
    Observation,
    SensorKind,
    ThreatAssessment,
    ThreatLevel,
)
from .detect import (
    DualPolRadarDetector,
    FusionEngine,
    GroundTruthAggregator,
    HyperLocalPolygonBuilder,
    InfrasoundDetector,
    SeismicDetector,
    SignalTransportDetector,
    StormScaleThreatModel,
    WeatherAppFeedDetector,
)
from .dispatch import (
    IndoorPushDispatcher,
    SystemIntegrationDispatcher,
    WEADispatcher,
)
from .dispatch.indoor_push import InMemoryRegistry, _Subscription
from .dispatch.wea import build_cap


# ---------------------------------------------------------------------------
# Synthetic scenario: EF3 near Moore, OK moving NE at 15 m/s
# ---------------------------------------------------------------------------


SCENARIO_LAT = 35.3395
SCENARIO_LON = -97.4867
RADAR_LAT, RADAR_LON = 35.2333, -97.4778  # KTLX Twin Lakes
RADAR_RANGE_M = 20_000.0


def _radar_payload() -> dict:
    """Synthesise a tilt with a mesocyclone + TDS at the tornado location."""
    azimuths = [i * 1.0 for i in range(360)]
    ranges = [i * 250.0 for i in range(1, 400)]  # 100 km reach, 250 m gates
    Zh = [[20.0 for _ in ranges] for _ in azimuths]
    V = [[0.0 for _ in ranges] for _ in azimuths]
    Zdr = [[0.5 for _ in ranges] for _ in azimuths]
    rho_hv = [[0.98 for _ in ranges] for _ in azimuths]
    Kdp = [[0.0 for _ in ranges] for _ in azimuths]
    SW = [[1.0 for _ in ranges] for _ in azimuths]

    tgt_az_deg = _bearing_from(RADAR_LAT, RADAR_LON, SCENARIO_LAT, SCENARIO_LON)
    tgt_range_m = _distance_m(RADAR_LAT, RADAR_LON, SCENARIO_LAT, SCENARIO_LON)
    tgt_az = int(round(tgt_az_deg)) % 360
    tgt_rng = int(round(tgt_range_m / 250.0))

    # Mesocyclone/TVS: gate-to-gate shear across azimuth tgt_az↔tgt_az+1
    for d in range(-2, 3):
        az1 = (tgt_az + d) % 360
        az2 = (az1 + 1) % 360
        for dr in range(-2, 3):
            r = tgt_rng + dr
            if 0 <= r < len(ranges):
                V[az1][r] = -40.0
                V[az2][r] =  40.0  # 80 m/s couplet — TVS-strength
                Zh[az1][r] = 55.0
                Zh[az2][r] = 55.0

    # TDS: tight patch at tornado center
    for d in range(-1, 2):
        for dr in range(-1, 2):
            az = (tgt_az + d) % 360
            r = tgt_rng + dr
            if 0 <= r < len(ranges):
                Zh[az][r] = 52.0
                Zdr[az][r] = 0.1
                rho_hv[az][r] = 0.55

    # Hook echo: a reflectivity appendage leading into the hook on the
    # rear-right flank.
    for i in range(8):
        az = (tgt_az - 10 - i) % 360
        r = tgt_rng + i
        if 0 <= r < len(ranges):
            Zh[az][r] = 42.0

    return {
        "elevation_deg": 0.5,
        "gate_spacing_m": 250.0,
        "azimuths_deg": azimuths,
        "ranges_m": ranges,
        "Zh": Zh, "V": V, "SW": SW, "Zdr": Zdr, "rho_hv": rho_hv, "Kdp": Kdp,
    }


def _seismic_payload(active: bool) -> dict:
    """Synthetic 1-s window of ground velocity + band powers."""
    fs = 100.0
    n = int(fs)
    samples = []
    for i in range(n):
        # Baseline microseism + tornadic 4 Hz tone if active
        noise = random.gauss(0, 1e-7)
        if active:
            tornado = 2e-6 * math.sin(2 * math.pi * 4.0 * i / fs)
        else:
            tornado = 0.0
        samples.append(noise + tornado)
    return {
        "samples": samples,
        "sample_rate_hz": fs,
        "channel": "BHZ",
        "tornado_band_power": 4e-12 if active else 1e-14,
        "microseism_power": 1e-13,
    }


def _infrasound_payload(active: bool) -> dict:
    fs = 50.0
    n = int(fs)
    # 4-element square array, 100 m aperture
    offsets = [(-50, -50), (50, -50), (50, 50), (-50, 50)]
    base_signals: List[List[float]] = []
    bearing = _bearing_from(SCENARIO_LAT, SCENARIO_LON, SCENARIO_LAT - 0.1, SCENARIO_LON - 0.1)
    theta = math.radians(bearing)
    kx, ky = math.sin(theta), math.cos(theta)
    for ox, oy in offsets:
        s = []
        delay = (ox * kx + oy * ky) / 343.0  # s
        for i in range(n):
            t = i / fs - delay
            noise = random.gauss(0, 0.05)
            tone = 0.6 * math.sin(2 * math.pi * 3.5 * t) if active else 0.0
            s.append(tone + noise)
        base_signals.append(s)
    return {
        "samples": base_signals,
        "element_offsets_m": offsets,
        "sample_rate_hz": fs,
        "array_name": "AEO01",
    }


def _ground_truth_obs(now: float, tier: str, offset_m: float, phenomenon: str) -> Observation:
    bearing = random.uniform(0, 2 * math.pi)
    dlat = (offset_m * math.cos(bearing)) / 111_320.0
    dlon = (offset_m * math.sin(bearing)) / (
        111_320.0 * math.cos(math.radians(SCENARIO_LAT))
    )
    return Observation(
        kind=SensorKind.GROUND_TRUTH,
        source_id=f"spotter-{tier}-{random.randint(0, 999)}",
        timestamp=now,
        location=GeoPoint(SCENARIO_LAT + dlat, SCENARIO_LON + dlon),
        payload={
            "reporter_tier": tier,
            "phenomenon": phenomenon,
            "note": f"{phenomenon} observed by {tier}",
        },
    )


def _weather_app_obs(now: float, offset_m: float, vendor: str) -> Observation:
    bearing = random.uniform(0, 2 * math.pi)
    dlat = (offset_m * math.cos(bearing)) / 111_320.0
    dlon = (offset_m * math.sin(bearing)) / (
        111_320.0 * math.cos(math.radians(SCENARIO_LAT))
    )
    return Observation(
        kind=SensorKind.WEATHER_APP,
        source_id=f"pws-{vendor}-{random.randint(0, 99999)}",
        timestamp=now,
        location=GeoPoint(SCENARIO_LAT + dlat, SCENARIO_LON + dlon),
        payload={
            "pressure_hpa": 973.0,
            "pressure_tendency_hpa_per_min": -2.5,
            "wind_speed_mps": 18.0,
            "wind_gust_mps": 35.0,
            "temperature_c": 22.0,
            "temperature_tendency_c_per_min": -4.0,
            "feed_vendor": vendor,
            "feed_contains_official_warning": False,
            "feed_warning_hazard": "",
        },
    )


def _signal_obs(now: float, transport: str, text: str) -> Observation:
    return Observation(
        kind=SensorKind.SOCIAL,
        source_id=f"{transport}-feed",
        timestamp=now,
        location=GeoPoint(SCENARIO_LAT, SCENARIO_LON),
        payload={
            "transport": transport,
            "text": text,
            "polygon_centroid": (SCENARIO_LAT, SCENARIO_LON),
        },
    )


# ---------------------------------------------------------------------------
# Geographic helpers
# ---------------------------------------------------------------------------


def _distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    return GeoPoint(lat1, lon1).haversine_m(GeoPoint(lat2, lon2))


def _bearing_from(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    y = math.sin(dl) * math.cos(p2)
    x = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    return (math.degrees(math.atan2(y, x)) + 360.0) % 360.0


# ---------------------------------------------------------------------------
# Pipeline driver
# ---------------------------------------------------------------------------


def main() -> None:
    random.seed(0xA0E70)
    print("\n" + "=" * 72)
    print(" AEOLUS-ALERT prototype — synthetic Moore OK supercell ")
    print("=" * 72)

    # Build detectors
    radar = DualPolRadarDetector()
    seismic = SeismicDetector()
    infrasound = InfrasoundDetector(min_persistence_s=10.0)
    ground = GroundTruthAggregator()
    pws = WeatherAppFeedDetector()
    signal = SignalTransportDetector()
    fusion = FusionEngine()
    threat_model = StormScaleThreatModel()
    polygon_builder = HyperLocalPolygonBuilder()

    # Build dispatchers (with a seeded in-memory indoor-push registry)
    registry = InMemoryRegistry()
    # Seed ~500 fake subscriptions across the expected impact corridor
    for _ in range(500):
        dlat = random.uniform(-0.1, 0.1)
        dlon = random.uniform(-0.1, 0.1)
        c = f"pseudo8_{SCENARIO_LAT + dlat:.4f}_{SCENARIO_LON + dlon:.4f}"
        dt = random.choice([
            "ios", "android", "alexa", "google_home", "apple_tv", "roku",
            "hue", "nest_hub", "mac", "windows",
        ])
        registry.add(_Subscription(
            device_id=f"dev-{random.randint(0, 9999999):07d}",
            device_type=dt,
            push_token="stub-token",
            h3_cell=c,
        ))
    wea = WEADispatcher()
    indoor = IndoorPushDispatcher(registry=registry)
    sysint = SystemIntegrationDispatcher()

    # ---- Build the observation stream for one minute of event, 1 obs/sec
    t_start = time.time()
    all_detections: List[Detection] = []
    detector_fire_counts = {}

    def _run_detector(name, det_fn, obs):
        dets = det_fn(obs)
        detector_fire_counts[name] = detector_fire_counts.get(name, 0) + len(dets)
        return dets

    # Pre-populate a few seconds of seismic/infrasound history so persistence
    # thresholds unlock during the "live" window.
    for i in range(30):
        t = t_start - 30 + i
        seis_obs = Observation(
            kind=SensorKind.SEISMIC,
            source_id="OK.KS01",
            timestamp=t,
            location=GeoPoint(SCENARIO_LAT - 0.05, SCENARIO_LON - 0.05),
            payload=_seismic_payload(active=(i > 10)),
        )
        all_detections += _run_detector("seismic", seismic.detect, seis_obs)

        infra_obs = Observation(
            kind=SensorKind.INFRASOUND,
            source_id="AEO01",
            timestamp=t,
            location=GeoPoint(SCENARIO_LAT - 0.08, SCENARIO_LON - 0.08),
            payload=_infrasound_payload(active=(i > 5)),
        )
        all_detections += _run_detector("infrasound", infrasound.detect, infra_obs)

    # One radar sweep (new volume every ~60 s on NEXRAD, but single sweep
    # is enough for prototype).
    radar_obs = Observation(
        kind=SensorKind.DUAL_POL_RADAR,
        source_id="KTLX",
        timestamp=t_start,
        location=GeoPoint(RADAR_LAT, RADAR_LON),
        payload=_radar_payload(),
    )
    radar_dets = _run_detector("dual_pol_radar", radar.detect, radar_obs)
    all_detections += radar_dets

    # Ground truth: one trained spotter + a crowd cluster
    all_detections += _run_detector(
        "ground_truth",
        ground.detect,
        _ground_truth_obs(t_start + 5, "trained_spotter", 1_200.0, "tornado_on_ground"),
    )
    for _ in range(4):
        all_detections += _run_detector(
            "ground_truth",
            ground.detect,
            _ground_truth_obs(t_start + 10 + random.randint(0, 60), "amateur_report", 1_800.0, "funnel_cloud"),
        )

    # PWS cluster of pressure/wind anomalies
    for vendor in ("apple", "google", "wu"):
        for _ in range(3):
            all_detections += _run_detector(
                "weather_app",
                pws.detect,
                _weather_app_obs(t_start + 10, 1_500.0, vendor),
            )

    # Signal transports
    all_detections += _run_detector(
        "signal_transport",
        signal.detect,
        _signal_obs(
            t_start + 12,
            "nws_product_feed",
            "TORNADO EMERGENCY for central Cleveland County. "
            "This is a particularly dangerous situation. Large and extremely dangerous "
            "tornado confirmed on the ground.",
        ),
    )
    all_detections += _run_detector(
        "signal_transport",
        signal.detect,
        _signal_obs(
            t_start + 13,
            "broadcast_tv",
            "Breaking: Tornado on the ground near Moore. Take shelter now.",
        ),
    )
    all_detections += _run_detector(
        "signal_transport",
        signal.detect,
        _signal_obs(
            t_start + 14,
            "verified_social",
            "Chase team confirms large tornado on the ground, rotation visible.",
        ),
    )

    # ---- Fuse
    threats = fusion.fuse(all_detections, hazard="tornado")
    threats = [threat_model.update(t) for t in threats]

    # Pick the strongest threat for dispatch
    threats.sort(key=lambda t: (t.level, t.confidence), reverse=True)
    if not threats:
        print("No threats fused — scenario failed to trigger.")
        return
    top = threats[0]

    # ---- Build polygon
    corridor = threat_model.project_corridor(top, lead_s=1200.0)
    polygon = polygon_builder.build(top, corridor)

    # ---- Dispatch (all channels in parallel in production; sequential here)
    cap_xml = build_cap(top, polygon, _headline_for(top), _body_for(top))
    alerts: List[Alert] = []
    alerts.append(wea.dispatch(top, polygon))
    alerts.extend(indoor.dispatch(top, polygon))
    alerts.extend(sysint.dispatch(top, polygon, cap_xml))

    # ---- Report
    print(f"\nDetections produced: {len(all_detections)}")
    for name, n in sorted(detector_fire_counts.items(), key=lambda kv: -kv[1]):
        print(f"   {name:<20} {n:>4}")

    print(f"\nFused threats: {len(threats)}")
    for t in threats:
        print(
            f"   id={t.threat_id[:8]}  level={t.level.name:<9}"
            f"  conf={t.confidence:.2f}  EF~{t.peak_intensity_estimate:.1f}"
            f"  motion={t.motion_bearing_deg:5.1f}°@{t.motion_speed_mps:.1f} m/s"
        )

    print(f"\nTop threat polygon:")
    print(f"   polygon_id       : {polygon.polygon_id[:12]}")
    print(f"   H3 cells         : {len(polygon.h3_cells)}")
    print(f"   pop. estimate    : {polygon.population_estimate:,}")
    print(f"   valid until      : +{(polygon.expires_at - polygon.issued_at):.0f}s")

    print(f"\nDispatched alerts: {len(alerts)}")
    total_reach = 0
    worst_latency = 0.0
    by_channel = {}
    for a in alerts:
        by_channel.setdefault(a.channel, []).append(a)
        total_reach += a.reach_estimate
        if a.delivery_latency_s is not None:
            worst_latency = max(worst_latency, a.delivery_latency_s)

    for ch, lst in by_channel.items():
        reach = sum(x.reach_estimate for x in lst)
        avg_lat = sum((x.delivery_latency_s or 0) for x in lst) / len(lst) * 1000.0
        print(f"   {ch.value:<18} n={len(lst):<3} reach≈{reach:>12,}  avg_latency={avg_lat:6.2f} ms")

    print(f"\nTotal estimated reach: ~{total_reach:,} device-touches")
    print(f"Max per-channel latency: {worst_latency*1000:.2f} ms (prototype in-memory)")

    print("\n" + "=" * 72)
    print(" End of run. ")
    print("=" * 72 + "\n")


def _headline_for(t: ThreatAssessment) -> str:
    if t.level is ThreatLevel.EMERGENCY:
        return "TORNADO EMERGENCY — TAKE SHELTER NOW"
    if t.level is ThreatLevel.WARNING:
        return "Tornado Warning — Take Shelter Immediately"
    return f"{t.hazard.title()} {t.level.name.title()}"


def _body_for(t: ThreatAssessment) -> str:
    return (
        f"{t.hazard.title()} detected near {t.center.lat:.3f},{t.center.lon:.3f} "
        f"moving {int(t.motion_bearing_deg):03d}° at {t.motion_speed_mps:.0f} m/s."
    )


if __name__ == "__main__":
    main()
