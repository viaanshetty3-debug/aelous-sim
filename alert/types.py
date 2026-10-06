"""Shared dataclasses and enums for the AEOLUS-ALERT pipeline.

Every sensor produces `Observation`s; every detector emits `Detection`s;
the fusion engine produces a `ThreatAssessment`; the polygon service
produces a `WarningPolygon`; the dispatch layer emits `Alert`s on one or
more `AlertChannel`s.

All timestamps are UTC epoch seconds (float). All geographic coordinates
are WGS84 (lat °N, lon °E). All distances are meters, velocities m/s.
"""

from __future__ import annotations

import math
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum, IntEnum, auto
from typing import Any, Mapping


# ---------------------------------------------------------------------------
# Sensor and observation types
# ---------------------------------------------------------------------------


class SensorKind(Enum):
    """Enumerates every input modality the detection layer accepts."""

    DUAL_POL_RADAR = "dual_pol_radar"
    SEISMIC = "seismic"
    INFRASOUND = "infrasound"
    GROUND_TRUTH = "ground_truth"       # spotters, chasers, EM reports
    CROWDSOURCE = "crowdsource"         # phone pressure/accel/mic
    WEATHER_APP = "weather_app"         # Apple Weather / Google Weather feeds
    SATELLITE_GLM = "satellite_glm"     # GOES-R lightning
    MESONET = "mesonet"                 # surface obs
    SOCIAL = "social"                   # news, Twitter/X, forum streams


@dataclass(frozen=True)
class GeoPoint:
    """WGS84 point."""

    lat: float
    lon: float
    elevation_m: float = 0.0

    def haversine_m(self, other: "GeoPoint") -> float:
        """Great-circle distance in meters."""
        r = 6_371_000.0
        p1 = math.radians(self.lat)
        p2 = math.radians(other.lat)
        dp = math.radians(other.lat - self.lat)
        dl = math.radians(other.lon - self.lon)
        a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
        return 2 * r * math.asin(math.sqrt(a))


@dataclass
class Observation:
    """A single sample from one sensor.

    `payload` is a sensor-specific dict; downstream detectors know how to
    interpret it based on `kind`. Keeping payload loose avoids schema churn
    while we iterate — a production build would type each payload.
    """

    kind: SensorKind
    source_id: str                      # radar name, station id, device uuid, etc.
    timestamp: float                    # UTC epoch seconds
    location: GeoPoint
    payload: Mapping[str, Any]
    ingest_latency_s: float = 0.0       # time from sensor sample to our ingest
    observation_id: str = field(default_factory=lambda: uuid.uuid4().hex)


# ---------------------------------------------------------------------------
# Detections (per-sensor output)
# ---------------------------------------------------------------------------


class DetectionConfidence(IntEnum):
    """Discrete confidence bands used for gating auto-issuance.

    We keep ordinal rather than continuous outside the detectors so operators
    reading dashboards don't drown in false precision — fusion still uses
    the raw float internally.
    """

    NEGLIGIBLE = 0
    LOW = 1
    MODERATE = 2
    HIGH = 3
    VERY_HIGH = 4


@dataclass
class Detection:
    """A detector's assertion that *something* was found."""

    detector: str                       # module name, e.g. "dual_pol_radar.tds"
    kind: SensorKind
    timestamp: float
    location: GeoPoint
    confidence: DetectionConfidence
    confidence_raw: float               # continuous [0,1], used by fusion
    features: Mapping[str, float]       # arbitrary numeric features
    lead_time_estimate_s: float = 0.0   # how far in advance of impact (if applicable)
    notes: str = ""
    detection_id: str = field(default_factory=lambda: uuid.uuid4().hex)

    @staticmethod
    def band(raw: float) -> DetectionConfidence:
        """Bucket a continuous [0,1] confidence into bands."""
        if raw < 0.15:
            return DetectionConfidence.NEGLIGIBLE
        if raw < 0.35:
            return DetectionConfidence.LOW
        if raw < 0.60:
            return DetectionConfidence.MODERATE
        if raw < 0.85:
            return DetectionConfidence.HIGH
        return DetectionConfidence.VERY_HIGH


# ---------------------------------------------------------------------------
# Fused threat assessment
# ---------------------------------------------------------------------------


class ThreatLevel(IntEnum):
    NONE = 0
    ADVISORY = 1
    WATCH = 2
    WARNING = 3
    EMERGENCY = 4                       # "Tornado Emergency" / PDS equivalent


@dataclass
class ThreatAssessment:
    """Fused, calibrated threat picture at a point in time."""

    threat_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    created_at: float = field(default_factory=time.time)
    hazard: str = "tornado"             # tornado | flash_flood | derecho | ...
    level: ThreatLevel = ThreatLevel.NONE
    confidence: float = 0.0             # fused [0,1]
    center: GeoPoint | None = None
    motion_bearing_deg: float = 0.0     # true-north bearing of storm motion
    motion_speed_mps: float = 0.0
    peak_intensity_estimate: float = 0.0  # e.g. estimated EF rank in [0,5]
    expected_lifetime_s: float = 0.0
    contributing_detections: list[str] = field(default_factory=list)
    rationale: str = ""


# ---------------------------------------------------------------------------
# Warning polygon
# ---------------------------------------------------------------------------


@dataclass
class WarningPolygon:
    """Hyper-local warning polygon.

    `vertices` is a lon/lat ring (closed if first == last). `h3_cells` is
    the H3 res-8 cell set that approximately covers the polygon; the
    dispatch layer uses the cell set as the targeting key.
    """

    polygon_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    threat_id: str = ""
    issued_at: float = field(default_factory=time.time)
    expires_at: float = 0.0
    vertices: list[tuple[float, float]] = field(default_factory=list)  # (lon, lat)
    h3_cells: list[str] = field(default_factory=list)
    population_estimate: int = 0


# ---------------------------------------------------------------------------
# Alert dispatch
# ---------------------------------------------------------------------------


class AlertChannel(Enum):
    WEA_CBC = "wea_cbc"                 # cell broadcast
    APP_PUSH = "app_push"               # APNs/FCM
    INDOOR_PUSH = "indoor_push"         # smart speaker / TV / hub
    EAS = "eas"                         # Emergency Alert System (TV/radio)
    SIREN = "siren"
    HIGHWAY_SIGN = "highway_sign"       # DOT variable message signs
    NEWS_API = "news_api"               # press-wire push
    SOCIAL = "social"                   # X/Facebook/Threads posts
    WEATHER_APP = "weather_app"         # inject into Apple/Google weather feeds
    INTERNET_BANNER = "internet_banner" # ISP-level or CDN banners


@dataclass
class Alert:
    """A single alert message bound for one channel."""

    alert_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    threat_id: str = ""
    polygon_id: str = ""
    channel: AlertChannel = AlertChannel.WEA_CBC
    created_at: float = field(default_factory=time.time)
    headline: str = ""
    body: str = ""
    language: str = "en"
    severity: ThreatLevel = ThreatLevel.WARNING
    cap_xml: str = ""                   # populated by CAP builder
    delivered_at: float | None = None
    delivery_latency_s: float | None = None
    reach_estimate: int = 0


__all__ = [
    "SensorKind",
    "GeoPoint",
    "Observation",
    "DetectionConfidence",
    "Detection",
    "ThreatLevel",
    "ThreatAssessment",
    "WarningPolygon",
    "AlertChannel",
    "Alert",
]
