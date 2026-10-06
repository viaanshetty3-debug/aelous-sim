"""Signal-transport detector.

The alert signal is routed over *many* channels — radio, TV, EAS, cell
broadcast, OS-level push, open internet, news-wire APIs, social posts.
Each channel is a possible *ingest* too: breaking-news crawlers, local
TV meteorologists issuing their own warnings before NWS, verified X/
Threads accounts of chase teams, etc.

This module listens to those back-channels and converts them into
Detections. Treat it as "signal in the wild" — someone *already* said
something, now we rate how trustworthy that voice is.

Supported transports (payload field ``transport``):

- ``nws_product_feed``   (official NWS text products: TOR, SVR, SVS, LSR)
- ``broadcast_tv``       (local TV station emergency crawler)
- ``broadcast_radio``    (NOAA weather radio relay, local AM/FM)
- ``news_wire``          (AP, Reuters, Bloomberg)
- ``verified_social``    (verified account: NWS office, chaser, media)
- ``unverified_social``  (viral post, not verified)
- ``isp_banner``         (ISP-level DNS/CDN notice we injected)
- ``internet_rss``       (newspaper RSS, blog, aggregator)

Each transport has a prior trust weight and we check keyword classifiers
plus simple NLP cues ("confirmed", "on the ground", "visible rotation",
"take shelter now").
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List

from ..types import (
    Detection,
    GeoPoint,
    Observation,
    SensorKind,
)


TRANSPORT_PRIORS: Dict[str, float] = {
    "nws_product_feed":   0.97,
    "broadcast_tv":       0.80,
    "broadcast_radio":    0.75,
    "news_wire":          0.70,
    "verified_social":    0.70,
    "unverified_social":  0.30,
    "isp_banner":         0.60,
    "internet_rss":       0.45,
}


# Keywords that materially raise confidence when present
POSITIVE_PATTERNS = [
    (re.compile(r"\btornado emergency\b", re.I), 0.35),
    (re.compile(r"\bconfirmed tornado\b", re.I), 0.30),
    (re.compile(r"\blarge and (?:extremely )?dangerous\b", re.I), 0.25),
    (re.compile(r"\bon the ground\b", re.I), 0.20),
    (re.compile(r"\btake shelter (now|immediately)\b", re.I), 0.20),
    (re.compile(r"\bdebris (ball|signature)\b", re.I), 0.20),
    (re.compile(r"\bparticularly dangerous situation\b", re.I), 0.25),
    (re.compile(r"\bPDS\b"), 0.20),
    (re.compile(r"\brotation (?:visible|aloft)\b", re.I), 0.15),
]


# Keywords that lower confidence (hedged language)
HEDGE_PATTERNS = [
    (re.compile(r"\bpossible\b", re.I), -0.10),
    (re.compile(r"\brumou?r\b", re.I), -0.20),
    (re.compile(r"\bunconfirmed\b", re.I), -0.15),
    (re.compile(r"\bno damage reported\b", re.I), -0.10),
]


class SignalTransportDetector:
    """Converts channel-arriving human text into graded detections."""

    def detect(self, obs: Observation) -> List[Detection]:
        if obs.kind is not SensorKind.SOCIAL:
            return []
        transport = str(obs.payload.get("transport", "unverified_social"))
        text = str(obs.payload.get("text", ""))
        prior = TRANSPORT_PRIORS.get(transport, 0.3)

        bonus = 0.0
        matched: List[str] = []
        for pat, w in POSITIVE_PATTERNS:
            if pat.search(text):
                bonus += w
                matched.append(pat.pattern)
        for pat, w in HEDGE_PATTERNS:
            if pat.search(text):
                bonus += w
                matched.append(pat.pattern)

        raw = max(0.0, min(1.0, prior + bonus))
        if raw < 0.2:
            return []    # too weak to even surface

        # NWS products get special treatment: they are, by definition, the
        # authoritative signal. If a TOR product is in the stream, bind
        # the detection to its stated polygon centroid when available.
        location = obs.location
        if transport == "nws_product_feed" and "polygon_centroid" in obs.payload:
            lat, lon = obs.payload["polygon_centroid"]
            location = GeoPoint(lat, lon)

        return [
            Detection(
                detector=f"signal_transport.{transport}",
                kind=SensorKind.SOCIAL,
                timestamp=obs.timestamp,
                location=location,
                confidence=Detection.band(raw),
                confidence_raw=raw,
                features={
                    "transport_prior": prior,
                    "keyword_bonus": bonus,
                    "match_count": float(len(matched)),
                },
                notes=f"Transport={transport}; keywords matched: {matched[:3]}",
            )
        ]


__all__ = ["SignalTransportDetector", "TRANSPORT_PRIORS"]
