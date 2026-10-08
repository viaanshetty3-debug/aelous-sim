# Ablation Study: Thermal vs Momentum Sink Degradation

**Question**: When increasing intervention strength (4K thermal + -500Pa momentum), why does sustained vorticity reduction decrease?

**Hypothesis**: One mechanism is counteracting the other.

---

## Test Design

Four 160-step simulations to isolate effects:

### Test 1: Baseline (v5) ✓ Known Good
- Thermal RFD: 0.5K
- Momentum sink: -50Pa
- **Expected**: Reduction ~85.6% (reference)

### Test 2: High Thermal Only
- Thermal RFD: 4K (8× stronger)
- Momentum sink: 0Pa (disabled)
- **Expected**: If thermal helps → reduction increases. If thermal hurts → reduction decreases.

### Test 3: High Momentum Only
- Thermal RFD: 0K (disabled)
- Momentum sink: -500Pa (10× stronger)
- **Expected**: If momentum helps → reduction increases. If momentum hurts → reduction decreases.

### Test 4: Both High (The Problem)
- Thermal RFD: 4K
- Momentum sink: -500Pa
- **Expected**: Reduction degrades (user observation)

---

## Analysis Approach

### Step 1: Compare Individual Effects

```
Baseline:           85.6% reduction
Thermal only:       ? % reduction  →  Δ_thermal = Thermal% - 85.6%
Momentum only:      ? % reduction  →  Δ_momentum = Momentum% - 85.6%
Both high:          <85.6%         →  ΔCombined = BothHigh% - 85.6%
```

### Step 2: Identify Culprit

**If thermal-only helps but both hurts:**
```
Thermal only:      +5%  (e.g., 90.6%)  ← Helps
Momentum only:     -15% (e.g., 70.6%)  ← Hurts
Both:              -10% (e.g., 75.6%)  ← Problem confirmed

CULPRIT: Momentum sink at -500Pa
```

**If momentum-only helps but both hurts:**
```
Thermal only:      -20% (e.g., 65.6%)  ← Hurts
Momentum only:     +10% (e.g., 95.6%)  ← Helps
Both:              -5%  (e.g., 80.6%)  ← Problem confirmed

CULPRIT: Thermal RFD at 4K
```

**If both individual and combined hurt:**
```
Thermal only:      -10% (e.g., 75.6%)  ← Both bad
Momentum only:     -20% (e.g., 65.6%)  ← Both bad
Both:              -25% (e.g., 60.6%)  ← Worse together

CULPRIT: Interaction effect (they interfere with each other)
```

### Step 3: Understand the Mechanism

Once culprit identified, analyze:
- **Energy**: Does high intervention create spurious energy growth?
- **Vorticity field**: Is suppression too aggressive, causing instability?
- **Circulation**: Is circulation being destroyed (removing stabilizing mechanism)?
- **Divergence**: Does divergence increase (numerical instability)?

---

## Expected Outcomes & Interpretations

### Scenario A: Thermal is the Problem

**Physical mechanism**:
- Heat injection creates too much buoyancy
- Radial expansion of warm air disrupts vortex structure
- Vortex breaks apart rather than suppressing smoothly
- Post-intervention reformation likely

**What to look for**:
- High thermal → lower reduction
- Core vorticity more erratic
- Higher divergence RMS
- Reformation detected

**Solution**: Use even lower thermal (0.25K) or shorten duration

---

### Scenario B: Momentum is the Problem

**Physical mechanism**:
- -500Pa pressure deficit too strong
- Creates counter-rotating vortex or secondary circulation
- Vortex suppressed but momentum sink induces opposite spin
- Result: No sustained reduction

**What to look for**:
- High momentum → lower reduction
- Core vorticity changes sign or oscillates
- Circulation reverses direction
- Higher divergence RMS

**Solution**: Cap momentum sink at -100 Pa or reduce duration

---

### Scenario C: Interaction Effect

**Physical mechanism**:
- Individual interventions work fine
- Combined: thermal pushes outward, momentum pulls inward
- Opposing forces destabilize flow
- Creates shear-driven instability

**What to look for**:
- Both-high worse than either individual
- Vorticity becomes strongly asymmetric
- Divergence spikes
- Energy grows (coupling instability)

**Solution**: Stagger interventions (thermal first, then momentum) or use different spatial distribution

---

## Metrics to Track

### Primary (Vorticity Reduction)
- Core vorticity: |ω_final|
- Reduction %: ((|ω_baseline| - |ω_final|) / |ω_baseline|) × 100

### Secondary (Energy)
- Kinetic energy trajectory
- Peak energy (should be controlled)
- Energy growth rate

### Tertiary (Stability)
- Divergence RMS (should stay < 0.1)
- CFL adjustments (should be stable)
- Reformation detection (should be "None")

### Quaternary (Physics)
- Circulation (should be maintained/suppressed smoothly)
- Asymmetry (should be low if mechanism healthy)
- Temporal evolution (smooth vs. oscillatory)

---

## Decision Tree

```
Run 4 simulations
    │
    ├─ Thermal-only higher? ──No──┐
    │                              │
    └─ Momentum-only lower? ────Yes┤
                                   │
                    MOMENTUM IS CULPRIT ←┘
                    
                    Action: Reduce momentum to -100 Pa
                    Or: Shorten decay phase
                    Or: Delay momentum until after thermal active
```

---

## Next Steps After Ablation

### If Thermal is Culprit
1. Run v6_low_thermal: 0.25K thermal, -50Pa momentum
2. Run v6_short_thermal: 0.5K for 30 steps (vs 50)
3. Compare reduction with v5

### If Momentum is Culprit
1. Run v6_low_momentum: 0.5K thermal, -100Pa momentum
2. Run v6_short_momentum: 0.5K thermal, -500Pa for 30 steps
3. Test staggered: thermal active steps 0-50, momentum active steps 25-75

### If Interaction is Culprit
1. Run v6_staggered: thermal 0-50, momentum 50-100
2. Run v6_spatial: thermal in core, momentum in outer ring
3. Analyze phase space (where conflicts occur)

---

## What This Tells Us

**For Portfolio**: Shows rigorous experimental methodology
- Systematic ablation study
- Hypothesis testing
- Root cause analysis
- Iterative refinement

**For Physics**: Reveals intervention limits
- Where does mechanism break down?
- What are physical constraints?
- How to design robust intervention?

**For Optimization**: Enables parameter tuning
- Optimal thermal strength
- Optimal momentum strength
- Optimal timing and phasing

---

## Expected Runtime

- Test 1 (Baseline): 15 min (already cached or quick re-run)
- Test 2 (Thermal only): 15 min
- Test 3 (Momentum only): 15 min
- Test 4 (Both high): 15 min
- **Total**: ~60 min

Analysis afterward: 30 min to digest results and formulate next steps.

---

**Status**: Ablation tests running...
**ETA**: ~60 minutes
**Next**: Full analysis and root cause identification

