> ⚠️ **Superseded (2026-10-10).** The numbers in this document came from the old `solver.py`, which had three bugs that produced them: a runaway latent-heat updraft, a 2π error in the initial vortex, and a vorticity baseline measured differently from every later step (worth ~60% "reduction" before anything happened). In a rebuilt, verified model, no AEOLUS version (v1–v7 or the realworld_test 80% configuration) weakens the tornado beyond chance, and suction makes it stronger. See [AXISYM_RESULTS.md](AXISYM_RESULTS.md). This document is kept as project history.

# Ablation Results Quick Reference Guide

**Use this when results arrive to quickly identify the culprit**

---

## Result Template

```
Baseline (0.5K, -50Pa):     85.6% ← Reference
Thermal only (4K, 0Pa):     ???%  → Δ = ??? - 85.6%
Momentum only (0K, -500Pa): ???%  → Δ = ??? - 85.6%
Both high (4K, -500Pa):     ???%  → Δ = ??? - 85.6%
```

---

## Decision Key

### If Thermal Only INCREASES:
```
Thermal only: >85.6%
→ Thermal helps! More heat better.
→ But both-high decreases → MOMENTUM is the problem
→ Action: Use 4K thermal + lower momentum (-100Pa)
```

### If Thermal Only DECREASES:
```
Thermal only: <85.6%
→ Thermal hurts! Too much heat is bad.
→ Action: Use lower thermal (0.25K) instead
```

### If Momentum Only INCREASES:
```
Momentum only: >85.6%
→ Momentum helps! Stronger sink better.
→ But both-high decreases → THERMAL is the problem
→ Action: Use 0K thermal + higher momentum
```

### If Momentum Only DECREASES:
```
Momentum only: <85.6%
→ Momentum hurts! Too strong creates counter-vortex.
→ Action: Use lower momentum (-100Pa instead of -500Pa)
```

### If BOTH Individual & Combined DECREASE:
```
Thermal only:  <85.6% (hurts)
Momentum only: <85.6% (hurts)
Both high:     Even worse

→ INTERACTION: They fight each other
→ Action: Stagger timing or spatial separation
```

---

## Culprit Identification Chart

```
                Thermal Only    Momentum Only    Both High       CULPRIT
                ────────────    ─────────────    ─────────       ─────
Case 1:         ↑ (90%)         ↑ (92%)          ↓ (75%)         Both conflict → Interaction ⚠
Case 2:         ↑ (90%)         ↓ (70%)          ↓ (65%)         Momentum ✗
Case 3:         ↓ (70%)         ↑ (92%)          ↓ (65%)         Thermal ✗
Case 4:         ↓ (70%)         ↓ (70%)          ↓ (60%)         Both bad (use lower both)
Case 5:         ↑ (92%)         ↑ (90%)          ↑ (95%)         Both help! (unexpected)
```

---

## Quick Diagnosis Flowchart

```
                START: Results Arrived
                         |
        Is Both-High < Baseline (85.6%)?
               /                    \
             YES                    NO
              |                      |
              v                      v
      Problem confirmed      NO PROBLEM! Use both high
      
    Is Thermal-Only > Baseline?
           /          \
         YES          NO
          |            |
          v            v
    Is Momentum-    THERMAL IS PROBLEM
    Only < Base?    (Use 0K or 0.25K)
       /   \
     YES   NO
      |     |
      v     v
   BOTH  MOMENTUM
   CONFLICT  IS
   (Stagger) PROBLEM
           (Use -100Pa)
```

---

## Action Table

```
If You Find...                  Then Try...                  Expected Outcome
─────────────────               ───────────                  ──────────────────
Thermal hurts (< baseline)      Reduce thermal 0.5K → 0.25K  Better balance
Momentum hurts (< baseline)     Reduce momentum -500 → -100Pa Smoother suppression
Both conflict (worse combined)  Stagger: thermal 0-50, then   Avoid conflict period
                                momentum 50-100
Both hurt individually          Use both low                  Find stable region
Both help individually          Use both high                 Pursue this direction
```

---

## Follow-Up Tests (Based on Findings)

### If Thermal is Problem:
```
v6a: 0.25K thermal, -50Pa momentum
v6b: 0.5K thermal x 30 steps (shorter), -50Pa momentum
Test which is better
```

### If Momentum is Problem:
```
v6a: 0.5K thermal, -100Pa momentum
v6b: 0.5K thermal, -50Pa momentum x 100 steps (longer)
Test which is better
```

### If Interaction is Problem:
```
v6a: Staggered (thermal 0-50, momentum 50-100)
v6b: Spatial separation (thermal in core, momentum in ring)
v6c: Sequential (let thermal finish, then add momentum)
Test which avoids conflict
```

### If Both Help:
```
v6a: Higher both (6K thermal, -750Pa momentum)
v6b: Higher both (8K thermal, -1000Pa momentum)
Find saturation point
```

---

## Key Insight

The ablation study shows us **the answer to your question**:
- Thermal-only tells you if heat injection helps
- Momentum-only tells you if pressure sink helps
- Their combination tells you if they interfere

Once you know which is the culprit, the fix becomes obvious:
- **Thermal problem** → reduce or shorten thermal
- **Momentum problem** → reduce or shorten momentum
- **Interaction problem** → separate them (stagger in time, or space)

---

## Wait Time Estimate

Ablation tests running 4 × 160 steps:
- Baseline: ✓ Complete (15 min)
- Thermal only: ⏳ ~15 min remaining
- Momentum only: ⏳ ~15 min remaining
- Both high: ⏳ ~15 min remaining

**Total**: Should be done in ~45 minutes from baseline completion

**Current**: Baseline done ~[WAITING FOR OTHERS]
**ETA**: Full results in ~[LESS THAN 1 HOUR]

Once ablation_results.json appears, I'll immediately analyze and show you which mechanism is the culprit + recommended fix.
