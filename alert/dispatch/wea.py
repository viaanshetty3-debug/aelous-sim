"""Wireless Emergency Alerts dispatcher.

Writes a CAP v1.2 message and submits it to a Cell Broadcast Centre (CBC)
over a direct SMPP-style channel. In production this is prearranged with
each carrier; here we expose a `CBCGateway` protocol so tests can inject
a mock gateway.

Latency budget for life-threat alerts:
  - CAP build       : ≤  5 ms
  - gateway submit  : ≤ 100 ms
  - carrier fan-out : ≤ 3 s (SLA)
  - device wake     : ≤ 1 s

End-to-end CAP → device: p95 ≤ 4 s.
"""

from __future__ import annotations

import html
import time
import xml.sax.saxutils as _xmlutils
from dataclasses import dataclass
from typing import List, Protocol

from ..types import (
    Alert,
    AlertChannel,
    ThreatAssessment,
    ThreatLevel,
    WarningPolygon,
)


class CBCGateway(Protocol):
    """Protocol for a carrier Cell Broadcast gateway client."""

    def submit(self, cap_xml: str, h3_cells: List[str]) -> dict:
        ...


# ---------------------------------------------------------------------------
# Default mock gateway (prints and records; used in prototype)
# ---------------------------------------------------------------------------


@dataclass
class InMemoryCBCGateway:
    name: str = "mock-cbc"
    submissions: list = None

    def __post_init__(self) -> None:
        if self.submissions is None:
            self.submissions = []

    def submit(self, cap_xml: str, h3_cells: List[str]) -> dict:
        self.submissions.append({"cap_xml_len": len(cap_xml), "cell_count": len(h3_cells)})
        return {"status": "accepted", "cell_count": len(h3_cells), "gateway": self.name}


# ---------------------------------------------------------------------------
# CAP builder
# ---------------------------------------------------------------------------


SEVERITY_MAP = {
    ThreatLevel.ADVISORY: "Minor",
    ThreatLevel.WATCH: "Moderate",
    ThreatLevel.WARNING: "Severe",
    ThreatLevel.EMERGENCY: "Extreme",
    ThreatLevel.NONE: "Unknown",
}

URGENCY_MAP = {
    ThreatLevel.ADVISORY: "Future",
    ThreatLevel.WATCH: "Expected",
    ThreatLevel.WARNING: "Immediate",
    ThreatLevel.EMERGENCY: "Immediate",
    ThreatLevel.NONE: "Unknown",
}


def build_cap(
    threat: ThreatAssessment,
    polygon: WarningPolygon,
    headline: str,
    body: str,
    language: str = "en-US",
) -> str:
    pts = " ".join(f"{lat:.5f},{lon:.5f}" for lon, lat in polygon.vertices)
    sev = SEVERITY_MAP.get(threat.level, "Unknown")
    urg = URGENCY_MAP.get(threat.level, "Unknown")
    cap = f"""<?xml version="1.0" encoding="UTF-8"?>
<alert xmlns="urn:oasis:names:tc:emergency:cap:1.2">
  <identifier>{threat.threat_id}</identifier>
  <sender>aeolus-alert@aeolus.local</sender>
  <sent>{_rfc3339(polygon.issued_at)}</sent>
  <status>Actual</status>
  <msgType>Alert</msgType>
  <scope>Public</scope>
  <info>
    <language>{_xml(language)}</language>
    <category>Met</category>
    <event>{_xml(threat.hazard.title())} {sev}</event>
    <urgency>{urg}</urgency>
    <severity>{sev}</severity>
    <certainty>Observed</certainty>
    <effective>{_rfc3339(polygon.issued_at)}</effective>
    <expires>{_rfc3339(polygon.expires_at)}</expires>
    <headline>{_xml(headline)}</headline>
    <description>{_xml(body)}</description>
    <area>
      <areaDesc>Hyper-local {threat.hazard} impact corridor</areaDesc>
      <polygon>{pts}</polygon>
    </area>
  </info>
</alert>"""
    return cap


def _xml(s: str) -> str:
    return _xmlutils.escape(s, {'"': "&quot;", "'": "&apos;"})


def _rfc3339(t: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------


class WEADispatcher:
    """Carrier cell-broadcast dispatcher."""

    MAX_CHARS_WEA = 360                 # modern WEA 3.0 cap

    def __init__(self, gateway: CBCGateway | None = None) -> None:
        self.gateway = gateway or InMemoryCBCGateway()

    def dispatch(
        self,
        threat: ThreatAssessment,
        polygon: WarningPolygon,
        language: str = "en-US",
    ) -> Alert:
        headline, body = _compose_wea_text(threat)
        cap = build_cap(threat, polygon, headline, body, language=language)

        t0 = time.perf_counter()
        result = self.gateway.submit(cap, polygon.h3_cells)
        dt = time.perf_counter() - t0

        return Alert(
            threat_id=threat.threat_id,
            polygon_id=polygon.polygon_id,
            channel=AlertChannel.WEA_CBC,
            headline=headline,
            body=body,
            language=language,
            severity=threat.level,
            cap_xml=cap,
            delivered_at=time.time(),
            delivery_latency_s=dt,
            reach_estimate=polygon.population_estimate,
        )


def _compose_wea_text(threat: ThreatAssessment) -> tuple[str, str]:
    hazard = threat.hazard.title()
    if threat.level is ThreatLevel.EMERGENCY:
        headline = f"{hazard.upper()} EMERGENCY — TAKE SHELTER NOW"
    elif threat.level is ThreatLevel.WARNING:
        headline = f"{hazard} Warning — Take Shelter Immediately"
    elif threat.level is ThreatLevel.WATCH:
        headline = f"{hazard} Watch — Be Prepared"
    else:
        headline = f"{hazard} Advisory"
    body = (
        f"{hazard} detected near "
        f"{threat.center.lat:.3f},{threat.center.lon:.3f} "
        f"moving {int(threat.motion_bearing_deg):03d}° at "
        f"{threat.motion_speed_mps:.0f} m/s. "
        "Move to interior lowest-floor room. Avoid windows."
    )
    body = body[: WEADispatcher.MAX_CHARS_WEA]
    return headline, body


__all__ = [
    "WEADispatcher",
    "CBCGateway",
    "InMemoryCBCGateway",
    "build_cap",
]
