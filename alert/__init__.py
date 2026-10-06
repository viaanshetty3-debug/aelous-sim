"""AEOLUS-ALERT: ultra-fast weather warning alert system.

This package implements the detection, fusion, threat-modeling, polygon,
and dispatch layers described in FAST_WARNING_ALERT_SYSTEM.md.

Modules are prototype-grade: real algorithms with synthetic input adapters
so the pipeline is end-to-end runnable without live radar / seismic feeds.
"""

from .types import (
    Observation,
    SensorKind,
    Detection,
    DetectionConfidence,
    ThreatAssessment,
    ThreatLevel,
    WarningPolygon,
    Alert,
    AlertChannel,
)

__all__ = [
    "Observation",
    "SensorKind",
    "Detection",
    "DetectionConfidence",
    "ThreatAssessment",
    "ThreatLevel",
    "WarningPolygon",
    "Alert",
    "AlertChannel",
]
