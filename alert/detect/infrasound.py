"""Predictive infrasound monitoring.

Mature tornadoes radiate sub-audible (0.5-10 Hz) acoustic energy that
propagates for 50-250 km and — importantly — begins radiating **minutes
before** debris is lofted and often before a visible funnel reaches the
ground. The signal is quasi-tonal with a Doppler-shifted center frequency
tied to the circulation's radius of maximum winds.

This module processes a time-aligned stack from a multi-element array
(typically 4-6 microbarometers, 50-500 m aperture) and runs:

1. **Beamforming** by delay-and-sum across element pairs to estimate the
   azimuth of arrival (AoA) of coherent 0.5-10 Hz energy.
2. **F-detector / cross-correlation** to compute coherence; low coherence
   = ambient noise, high coherence + tornadic spectrum = detection.
3. **Spectral peak tracking** in the 1-6 Hz band. A persistent (> 60 s)
   narrowband peak with slowly drifting center frequency is the primary
   predictive feature.
4. **Bearing-to-range triangulation** when two or more arrays agree.

Observation payload (per array):
  - ``samples``: list[list[float]], shape (N_elements, N_samples)
  - ``element_offsets_m``: list[(x, y)] relative to array centroid
  - ``sample_rate_hz``: float
  - ``array_name``: str
"""

from __future__ import annotations

import cmath
import math
from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Dict, List, Sequence, Tuple

from ..types import (
    Detection,
    GeoPoint,
    Observation,
    SensorKind,
)


# ---------------------------------------------------------------------------
# Internal state
# ---------------------------------------------------------------------------


@dataclass
class _ArrayState:
    peak_freq_hist: Deque[float] = field(default_factory=deque)
    peak_power_hist: Deque[float] = field(default_factory=deque)
    bearing_hist: Deque[float] = field(default_factory=deque)
    coherence_hist: Deque[float] = field(default_factory=deque)
    last_time: float = 0.0


# ---------------------------------------------------------------------------
# Detector
# ---------------------------------------------------------------------------


class InfrasoundDetector:
    """Beamformer + spectral tracker over a microbarometer array."""

    SPEED_OF_SOUND_MPS = 343.0
    LOW_HZ = 0.5
    HIGH_HZ = 10.0
    TORNADIC_HZ_MIN = 1.0
    TORNADIC_HZ_MAX = 6.0

    def __init__(
        self,
        coherence_threshold: float = 0.55,
        min_persistence_s: float = 60.0,
        history_len: int = 300,
    ) -> None:
        self.coherence_threshold = coherence_threshold
        self.min_persistence_s = min_persistence_s
        self.history_len = history_len
        self._state: Dict[str, _ArrayState] = {}

    # ------------------------------------------------------------------ api

    def detect(self, obs: Observation) -> List[Detection]:
        if obs.kind is not SensorKind.INFRASOUND:
            return []
        samples: List[List[float]] = list(obs.payload["samples"])
        offsets: List[Tuple[float, float]] = list(obs.payload["element_offsets_m"])
        fs = float(obs.payload["sample_rate_hz"])
        state = self._state.setdefault(obs.source_id, _ArrayState())

        bearing_deg, coherence = self._beamform(samples, offsets, fs)
        peak_freq, peak_power = self._dominant_peak(samples[0], fs)

        state.bearing_hist.append(bearing_deg)
        state.coherence_hist.append(coherence)
        state.peak_freq_hist.append(peak_freq)
        state.peak_power_hist.append(peak_power)
        for buf in (
            state.bearing_hist,
            state.coherence_hist,
            state.peak_freq_hist,
            state.peak_power_hist,
        ):
            while len(buf) > self.history_len:
                buf.popleft()
        state.last_time = obs.timestamp

        # Persistence check: how long has a tornadic-band peak been coherent?
        persist = self._persistence_s(state, obs.timestamp, fs)
        bearing_stable = self._bearing_stability_deg(state) < 10.0

        detections: List[Detection] = []
        if (
            coherence >= self.coherence_threshold
            and self.TORNADIC_HZ_MIN <= peak_freq <= self.TORNADIC_HZ_MAX
            and persist >= self.min_persistence_s
            and bearing_stable
        ):
            # Confidence rises with coherence, persistence, and spectral tone.
            raw = min(
                1.0,
                0.35
                + 0.30 * (coherence - self.coherence_threshold) / (1.0 - self.coherence_threshold)
                + 0.20 * min(1.0, persist / (3 * self.min_persistence_s))
                + 0.15 * min(1.0, peak_power / 1.0),
            )
            detections.append(
                Detection(
                    detector="infrasound.tornadic_tone",
                    kind=SensorKind.INFRASOUND,
                    timestamp=obs.timestamp,
                    location=obs.location,   # array centroid; range comes from fusion
                    confidence=Detection.band(raw),
                    confidence_raw=raw,
                    features={
                        "bearing_deg": bearing_deg,
                        "coherence": coherence,
                        "peak_freq_hz": peak_freq,
                        "peak_power": peak_power,
                        "persistence_s": persist,
                    },
                    # Infrasound often precedes radar debris signatures by
                    # 3-15 minutes — hence this is the "predictive" layer.
                    lead_time_estimate_s=600.0,
                    notes=f"Coherent {peak_freq:.1f} Hz tornadic tone from bearing "
                    f"{bearing_deg:.0f}° for {persist:.0f}s.",
                )
            )
        return detections

    # ----------------------------------------------------------- beamforming

    def _beamform(
        self,
        samples: Sequence[Sequence[float]],
        offsets: Sequence[Tuple[float, float]],
        fs: float,
    ) -> Tuple[float, float]:
        """Delay-and-sum beamformer over a coarse azimuth grid.

        Returns (best_bearing_deg, coherence in [0,1]).
        """
        if len(samples) < 2:
            return 0.0, 0.0
        n = min(len(s) for s in samples)
        best_power = 0.0
        best_bearing = 0.0
        total_power = sum(_rms(s[:n]) ** 2 for s in samples) + 1e-12
        for bearing in range(0, 360, 5):
            theta = math.radians(bearing)
            kx, ky = math.sin(theta), math.cos(theta)
            summed = [0.0] * n
            for s, (ox, oy) in zip(samples, offsets):
                # Delay for a plane wave arriving from `bearing`
                delay_s = (ox * kx + oy * ky) / self.SPEED_OF_SOUND_MPS
                shift = int(round(delay_s * fs))
                for i in range(n):
                    j = i - shift
                    if 0 <= j < n:
                        summed[i] += s[j]
            p = _rms(summed) ** 2
            if p > best_power:
                best_power = p
                best_bearing = float(bearing)
        coherence = min(1.0, best_power / (len(samples) * total_power / len(samples)))
        return best_bearing, coherence

    # ------------------------------------------------------- spectral peak

    def _dominant_peak(self, signal: Sequence[float], fs: float) -> Tuple[float, float]:
        """Return (peak frequency Hz, peak power) in the 0.5-10 Hz band.

        Naive DFT because we care about ~20 bins, not thousands. For a
        prototype this is clearer than importing numpy; swap for ``np.fft``
        trivially.
        """
        n = len(signal)
        if n < 32:
            return 0.0, 0.0
        best_f = 0.0
        best_p = 0.0
        # Scan only the band of interest (coarse 0.1 Hz grid).
        f = self.LOW_HZ
        while f <= self.HIGH_HZ:
            w = 2.0 * math.pi * f / fs
            acc = complex(0.0, 0.0)
            for k, x in enumerate(signal):
                acc += x * cmath.exp(-1j * w * k)
            p = abs(acc) ** 2 / (n * n)
            if p > best_p:
                best_p = p
                best_f = f
            f += 0.1
        return best_f, best_p

    # ------------------------------------------------------- persistence

    def _persistence_s(self, state: _ArrayState, now: float, fs: float) -> float:
        """How many seconds back the tornadic-band peak has been continuous.

        We assume one observation ~ 1 second of signal (chunked upstream).
        """
        count = 0
        for freq, coh in zip(reversed(state.peak_freq_hist), reversed(state.coherence_hist)):
            if (
                self.TORNADIC_HZ_MIN <= freq <= self.TORNADIC_HZ_MAX
                and coh >= self.coherence_threshold
            ):
                count += 1
            else:
                break
        return float(count)

    def _bearing_stability_deg(self, state: _ArrayState) -> float:
        if len(state.bearing_hist) < 5:
            return 999.0
        recent = list(state.bearing_hist)[-10:]
        mean = sum(recent) / len(recent)
        return math.sqrt(sum((b - mean) ** 2 for b in recent) / len(recent))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _rms(signal: Sequence[float]) -> float:
    if not signal:
        return 0.0
    return math.sqrt(sum(x * x for x in signal) / len(signal))


__all__ = ["InfrasoundDetector"]
