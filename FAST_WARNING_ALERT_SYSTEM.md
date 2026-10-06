# AEOLUS-ALERT: Ultra-Fast Weather Warning Alert System

## Overview

A pivot from physical vortex disruption to **mass-reach, low-latency warning dissemination**. Instead of trying to weaken a tornado after it forms, AEOLUS-ALERT focuses on shrinking the gap between *detection* and *every exposed person receiving an actionable warning*.

Target end-to-end latency (radar signature → device alert on an exposed user's screen):

| Stage | Legacy (NWS/WEA today) | AEOLUS-ALERT target |
|-------|------------------------|---------------------|
| Radar scan → signature flagged | 60–180 s | ≤ 10 s |
| Forecaster confirmation | 60–300 s | 0–15 s (auto-issue w/ confidence gating) |
| Message formatting + geo-targeting | 10–30 s | ≤ 1 s |
| Carrier distribution (WEA) | 30–120 s | ≤ 3 s (direct multicast) |
| Device render + sound | 1–10 s | ≤ 1 s |
| **Total** | **3–10 min** | **≤ 30 s** |

Headline goal: **cut warning lead-time delivery by ~10×** and **expand reached population by 3–5×** within the same warning polygon.

---

## Why This Instead of Vortex Disruption?

- Vortex-scale kinetic energy is ~10¹⁰–10¹¹ J. No currently feasible intervention delivers that in seconds without secondary hazards.
- Warning dissemination is a **software + protocol** problem — the physics is already solved.
- Each 1-minute reduction in warning latency is associated with measurable reductions in casualties for strong tornadoes (empirically supported by NWS post-storm surveys).
- Alerting infrastructure scales to *all* hazards: tornadoes, flash floods, wildfires, derechos, tsunamis — the same pipeline, same code paths.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  INGEST LAYER (edge-colocated with radar sites)             │
│  - NEXRAD Level II streams (every 60–180s, soon MESO-SAILS) │
│  - GOES-R GLM lightning (20 s cadence)                      │
│  - Phased-array radar pilots (MPAR, 30 s volume scans)      │
│  - Mesonet surface obs (1–5 min)                            │
│  - Crowd-sourced pressure/vibration from phones             │
└──────────────────┬──────────────────────────────────────────┘
                   │  gRPC / NATS JetStream (sub-100 ms fan-out)
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  DETECTION LAYER (stream processing, GPU inference)         │
│  - Hook/TVS/MESO classifier (CNN on reflectivity+velocity)  │
│  - Debris signature (correlation coefficient drop)          │
│  - Nowcast model (U-Net / FourCastNet variant)              │
│  - Confidence calibration + false-alarm suppressor          │
└──────────────────┬──────────────────────────────────────────┘
                   │  Only "high-confidence" events auto-issue
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  POLYGON + MESSAGE SERVICE                                  │
│  - H3 hex tiling at res 8 (~0.7 km²) for geo-targeting      │
│  - Storm-motion vector → dynamic polygon advection          │
│  - CAP v1.2 message assembly + language localization        │
└──────────────────┬──────────────────────────────────────────┘
                   │
    ┌──────────────┼──────────────────┬────────────────┐
    ▼              ▼                  ▼                ▼
┌─────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐
│  WEA/   │  │  Direct push │  │  Siren mesh  │  │  Partner    │
│  CMAS   │  │  (APNs/FCM)  │  │  (LoRa/5G    │  │  TV/radio   │
│  (cell  │  │  via app SDK │  │  broadcast)  │  │  EAS feeds  │
│  bcast) │  │              │  │              │  │             │
└─────────┘  └──────────────┘  └──────────────┘  └─────────────┘
```

Delivery is **fan-out parallel** — no single channel is a critical path.

---

## Key Latency Wins

### 1. Edge detection colocated with radar
Push the ML classifier to the radar site (or regional NOAA edge POP) so the detection decision is made before Level II bytes finish streaming to the central ingest. Saves 30–120 s of round-trip and queue time.

### 2. Confidence-gated auto-issue
Human-in-the-loop remains for *downgrade / cancel*, but issuance for high-confidence TVS + debris signatures is automatic. Keeps the forecaster's job as a safety net, not a serial bottleneck.

### 3. Cell-broadcast direct injection
Standard WEA pipeline hits carrier gateways which batch messages. A direct SMPP / CBC integration with carriers (prearranged, authenticated) lets us skip batching for life-threat alerts.

### 4. Device-side pre-warming
Companion app subscribes to its local H3 hex and keeps a persistent WebSocket. Alert delivery is a 200-byte push, not a full HTTP round-trip. Falls back to WEA if the app is uninstalled.

### 5. Dynamic polygon advection
Rather than issuing a static polygon valid for 30 minutes, we re-issue a thinner, forward-advected polygon every 60 s. Fewer false targets → less alert fatigue → more people trust the alert when it hits.

---

## Reach Expansion

| Mechanism | Who it reaches that WEA alone misses |
|-----------|---------------------------------------|
| LoRa siren mesh in rural counties | Residents outside cell coverage |
| Multi-language auto-translation (ES/VI/ZH/AR) | ~20M US residents w/ limited English |
| Accessibility: haptic + screen-reader CAP tags | Deaf / hard-of-hearing / blind users |
| In-vehicle integration (Android Auto / CarPlay) | Drivers who silence phones |
| Smart-speaker + smart-TV CAP consumers | Indoor users not on a phone |
| Opt-in SMS fallback for travelers | Visitors roaming on foreign SIMs |

Estimated additional reach vs. WEA-only: **+180M device-touches per major event** (continental US), roughly tripling the alerted population share in impacted counties.

---

## Module Skeleton (proposed, parallel to existing solver layout)

```
aeolus_sim/
├── alert/
│   ├── __init__.py
│   ├── ingest/
│   │   ├── nexrad_stream.py       # Level II → in-memory tensors
│   │   ├── glm_stream.py          # GOES-R lightning
│   │   └── mesonet.py             # surface obs pull
│   ├── detect/
│   │   ├── tvs_classifier.py      # CNN inference
│   │   ├── nowcast.py             # short-range precip/rotation nowcast
│   │   └── confidence.py          # calibration + FAR suppression
│   ├── polygon/
│   │   ├── h3_tiling.py           # hex-based targeting
│   │   └── advect.py              # storm-motion polygon update
│   ├── dispatch/
│   │   ├── cap_builder.py         # CAP v1.2 XML/JSON
│   │   ├── wea_cbc.py             # carrier cell broadcast
│   │   ├── push_fanout.py         # APNs/FCM
│   │   └── siren_mesh.py          # LoRa/5G broadcast
│   └── metrics/
│       ├── latency.py             # per-stage p50/p95/p99
│       └── reach.py               # device-touch estimation
└── FAST_WARNING_ALERT_SYSTEM.md
```

---

## Success Metrics

1. **p95 end-to-end latency ≤ 30 s** (radar signature → device render) in integration tests against replayed Level II archives (Moore 2013, Mayfield 2021, Rolling Fork 2023).
2. **False-alarm ratio ≤ current NWS baseline** (~0.70 for tornado warnings) — do not trade latency for noise.
3. **Reach ≥ 90%** of mobile devices within the warning polygon, measured via opt-in telemetry.
4. **Accessibility coverage**: every alert emits haptic, audio, visual, and screen-reader-tagged variants.
5. **Graceful degradation**: pipeline survives loss of any single channel (WEA, FCM/APNs, siren mesh) with ≤ 10 s added latency.

---

## Open Questions

- Legal authority to auto-issue without a human signoff varies by country; prototype assumes US NWS partnership and WMO-aligned CAP in international mode.
- Carrier SLAs for direct SMPP/CBC integration need prearrangement; worth piloting with one carrier in Tornado Alley.
- Nowcast ML confidence calibration under rare-event regimes (strong tornadoes are ~1 in 1000 severe storms) — needs sampling strategy that doesn't under-weight tails.
- Battery cost of persistent WebSocket on mobile; mitigation: push-only wake-up via FCM/APNs silent push, upgrade to WS on alert context.

---

## Status

Design document only. No implementation yet. See `alert/` scaffold proposal above for module layout if we proceed to prototype.
