"""Detection layer: per-sensor detectors + fusion + threat + polygon.

Each detector exposes `detect(obs: Observation) -> list[Detection]`.
Detectors are stateless w.r.t. the public API but may hold internal
rolling buffers (e.g. STA/LTA windows) keyed by `source_id`.
"""

from .tectonic import SeismicDetector
from .dual_pol_radar import DualPolRadarDetector
from .infrasound import InfrasoundDetector
from .ground_truth import GroundTruthAggregator
from .weather_app_feeds import WeatherAppFeedDetector
from .signal_transport import SignalTransportDetector
from .fusion import FusionEngine
from .threat_model import StormScaleThreatModel
from .polygon import HyperLocalPolygonBuilder

__all__ = [
    "SeismicDetector",
    "DualPolRadarDetector",
    "InfrasoundDetector",
    "GroundTruthAggregator",
    "WeatherAppFeedDetector",
    "SignalTransportDetector",
    "FusionEngine",
    "StormScaleThreatModel",
    "HyperLocalPolygonBuilder",
]
