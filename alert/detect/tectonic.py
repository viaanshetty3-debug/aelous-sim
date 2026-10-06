"""Tectonic / seismic anomaly detector.

Tornadoes and strong straight-line winds couple into the ground and produce
measurable seismic signatures in the 1-60 Hz band (Tatom et al. 1995;
Hubbard et al. 2017). Earthquakes themselves rarely trigger tornado alerts,
but *unusual* tectonic motion is useful for two reasons:

1. Co-seismic ground tilt can disturb boundary-layer convergence and
   occasionally correlates with later storm initiation (weak signal, used
   only as a soft prior in the fusion engine).
2. Many broadband seismometers deployed in tornado-prone states (TA/USArray
   legacy stations, OK Geological Survey network) record the ground-coupled
   infrasound of a mature tornado to ranges of ~25 km. This gives an
   independent "the funnel is on the ground RIGHT NOW" signal when radar
   geometry is poor (e.g. close-range cone of silence).

The detector consumes raw 3-component velocity samples at 100 Hz. It runs:

- STA/LTA trigger on the vertical channel (classic earthquake trigger).
- A band-limited spectrogram ratio in the tornado band (1-15 Hz vertical,
  check against 0.03-0.1 Hz microseism baseline) to separate tornadoes
  from true quakes.
- A rolling anomaly score vs. the station's own 24-hour baseline.

We keep per-station state in-memory. In production this moves to a
Redis / RocksDB tier so the detector is horizontally scalable.
"""

from __future__ import annotations

import math
import statistics
from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Dict, List

from ..types import (
    Detection,
    DetectionConfidence,
    GeoPoint,
    Observation,
    SensorKind,
)


# ---------------------------------------------------------------------------
# Internal per-station state
# ---------------------------------------------------------------------------


@dataclass
class _StationState:
    """Rolling buffers for one seismic station."""

    sta_window_s: float = 1.0           # short-term average window
    lta_window_s: float = 60.0          # long-term average window
    sample_rate_hz: float = 100.0
    sta_buf: Deque[float] = field(default_factory=deque)
    lta_buf: Deque[float] = field(default_factory=deque)
    tornado_band_buf: Deque[float] = field(default_factory=deque)   # 1-15 Hz power
    microseism_buf: Deque[float] = field(default_factory=deque)     # 0.03-0.1 Hz
    long_baseline: Deque[float] = field(default_factory=deque)      # 24-h ratio history
    last_detection_t: float = 0.0

    @property
    def sta_max(self) -> int:
        return int(self.sta_window_s * self.sample_rate_hz)

    @property
    def lta_max(self) -> int:
        return int(self.lta_window_s * self.sample_rate_hz)


# ---------------------------------------------------------------------------
# Detector
# ---------------------------------------------------------------------------


class SeismicDetector:
    """STA/LTA + tornado-band ratio seismic anomaly detector.

    Expected observation payload fields (vertical channel):
      - ``samples``: list[float], ground velocity in m/s
      - ``sample_rate_hz``: float
      - ``tornado_band_power``: float, 1-15 Hz band power from upstream FFT
      - ``microseism_power``: float, 0.03-0.1 Hz band power
      - ``channel``: str, e.g. "BHZ"

    Upstream (edge DSP) is responsible for the FFT so this stage stays
    cheap. If the fields are absent we fall back to raw-sample STA/LTA.
    """

    def __init__(
        self,
        sta_window_s: float = 1.0,
        lta_window_s: float = 60.0,
        trigger_ratio: float = 4.0,
        tornado_band_ratio: float = 3.0,
        min_quiet_s: float = 30.0,
    ) -> None:
        self.sta_window_s = sta_window_s
        self.lta_window_s = lta_window_s
        self.trigger_ratio = trigger_ratio
        self.tornado_band_ratio = tornado_band_ratio
        self.min_quiet_s = min_quiet_s
        self._stations: Dict[str, _StationState] = {}

    # ------------------------------------------------------------------ api

    def detect(self, obs: Observation) -> List[Detection]:
        if obs.kind is not SensorKind.SEISMIC:
            return []

        state = self._stations.setdefault(
            obs.source_id,
            _StationState(
                sta_window_s=self.sta_window_s,
                lta_window_s=self.lta_window_s,
                sample_rate_hz=float(obs.payload.get("sample_rate_hz", 100.0)),
            ),
        )

        samples = list(obs.payload.get("samples", []))
        self._push_samples(state, samples)

        tb = float(obs.payload.get("tornado_band_power", 0.0))
        ms = float(obs.payload.get("microseism_power", 1e-12))
        state.tornado_band_buf.append(tb)
        state.microseism_buf.append(max(ms, 1e-12))
        while len(state.tornado_band_buf) > 600:
            state.tornado_band_buf.popleft()
        while len(state.microseism_buf) > 600:
            state.microseism_buf.popleft()

        detections: List[Detection] = []

        sta = _mean(state.sta_buf)
        lta = _mean(state.lta_buf)
        ratio = sta / lta if lta > 0 else 0.0

        tb_med = statistics.median(state.tornado_band_buf) if state.tornado_band_buf else 0.0
        ms_med = statistics.median(state.microseism_buf) if state.microseism_buf else 1e-12
        band_ratio = tb_med / ms_med if ms_med > 0 else 0.0
        state.long_baseline.append(band_ratio)
        while len(state.long_baseline) > 86_400:    # ~24 h at 1 Hz feature rate
            state.long_baseline.popleft()
        baseline = (
            statistics.median(state.long_baseline) if state.long_baseline else band_ratio
        )
        anomaly = band_ratio / baseline if baseline > 0 else 0.0

        quiet = (obs.timestamp - state.last_detection_t) > self.min_quiet_s

        # ---- Tornado-band ground coupling (primary tornado-relevant signal)
        if band_ratio > self.tornado_band_ratio and anomaly > 2.0 and quiet:
            raw = _sigmoid((band_ratio - self.tornado_band_ratio) * 0.6)
            detections.append(
                Detection(
                    detector="seismic.ground_coupled_vortex",
                    kind=SensorKind.SEISMIC,
                    timestamp=obs.timestamp,
                    location=obs.location,
                    confidence=Detection.band(raw),
                    confidence_raw=raw,
                    features={
                        "tornado_band_ratio": band_ratio,
                        "baseline_ratio": baseline,
                        "anomaly_factor": anomaly,
                        "sta_lta": ratio,
                    },
                    lead_time_estimate_s=0.0,  # this fires when funnel is already on ground
                    notes="Vertical-channel 1-15 Hz power anomaly consistent with "
                    "ground-coupled tornadic infrasound.",
                )
            )
            state.last_detection_t = obs.timestamp

        # ---- Unusual tectonic motion (soft prior, not a tornado trigger alone)
        if ratio > self.trigger_ratio and quiet:
            # Separate quakes (broadband, often lower frequency) from tornado hits
            quake_like = tb_med < 2 * ms_med and ratio > 6.0
            raw = _sigmoid((ratio - self.trigger_ratio) * 0.4)
            detections.append(
                Detection(
                    detector="seismic.sta_lta_trigger",
                    kind=SensorKind.SEISMIC,
                    timestamp=obs.timestamp,
                    location=obs.location,
                    confidence=Detection.band(raw * (0.5 if quake_like else 1.0)),
                    confidence_raw=raw * (0.5 if quake_like else 1.0),
                    features={
                        "sta_lta": ratio,
                        "tornado_band_ratio": band_ratio,
                        "classified_as_quake": float(quake_like),
                    },
                    notes=(
                        "Classical STA/LTA trigger; classified as tectonic quake "
                        "(down-weighted for tornado fusion)."
                        if quake_like
                        else "STA/LTA trigger of unknown origin; forwarded as "
                        "weak prior."
                    ),
                )
            )
            state.last_detection_t = obs.timestamp

        return detections

    # ------------------------------------------------------------- internals

    def _push_samples(self, state: _StationState, samples: list[float]) -> None:
        for s in samples:
            abs_s = abs(s)
            state.sta_buf.append(abs_s)
            state.lta_buf.append(abs_s)
            while len(state.sta_buf) > state.sta_max:
                state.sta_buf.popleft()
            while len(state.lta_buf) > state.lta_max:
                state.lta_buf.popleft()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _mean(buf: Deque[float]) -> float:
    if not buf:
        return 0.0
    return sum(buf) / len(buf)


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


__all__ = ["SeismicDetector"]
