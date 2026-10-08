# Theoretical Analysis: Why Increasing Interventions Degrades Reduction

**Question**: At 4K thermal + -500Pa momentum, sustained reduction decreases. Why?

**Proposed Mechanisms**:

---

## Mechanism 1: Thermal Over-Injection (Too Much Buoyancy)

### How It Works
1. **Low thermal (0.5K)**: Gentle buoyancy destabilizes RFD inversion
   - Warm air rises smoothly
   - Creates sustained updraft
   - Feeds vortex disruption gradually
   
2. **High thermal (4K)**: Aggressive buoyancy creates shear
   - Warm air accelerates upward
   - Creates strong vertical jets
   - Disrupts vortex too violently
   - Vortex fragments or re-organizes around jets

### Physical Signature
- **Vorticity field**: Becomes asymmetric, multiple cores
- **Energy**: Can spike (shear-driven instability)
- **Circulation**: Reverses or oscillates
- **Divergence**: Increases (complex 3D structure)

### Why It Fails
```
Low thermal:    Gradual suppression → sustained reduction
High thermal:   Violent disruption → vortex re-organizes → reformation
```

---

## Mechanism 2: Momentum Sink Counter-Rotation (Overcorrection)

### How It Works
1. **Low momentum (-50Pa)**: Gentle pressure sink
   - Removes some tangential velocity
   - Vortex weakens gradually
   - Adjustment is smooth

2. **High momentum (-500Pa)**: Strong pressure sink
   - Creates anti-cyclonic circulation (opposite spin)
   - At surface: strong inflow (removing cyclonic wind)
   - At mid-level: counter-rotating vortex develops
   - Result: Vortex suppressed, but counter-vortex created

### Physical Signature
- **Vorticity**: Changes sign in some regions
- **Circulation**: Reverses direction
- **Flow pattern**: Anti-cyclonic in lower levels
- **Divergence**: High (opposing circulations create shear)

### Why It Fails
```
Low momentum:   Removes tangential wind → vortex weakens
High momentum:  Creates opposing vortex → Cancels net vorticity but creates instability
```

---

## Mechanism 3: Interaction Instability (Thermal + Momentum Conflict)

### How It Works
1. **Thermal alone (4K)**: Lifts air vertically
2. **Momentum alone (-500Pa)**: Converges air horizontally inward
3. **Both together**: 
   - Buoyant air wants to go UP
   - Pressure sink wants to go IN
   - Result: SHEAR between vertical and radial circulation
   - This shear creates vortex sheet instabilities

### Physical Mechanism: Kelvin-Helmholtz Instability

```
         ↑ ↑ (Buoyant updraft from thermal)
    ─────────────────
  ← ← ← (Radial inflow from momentum sink)
    ─────────────────
         
Creates horizontal shear layer
         ↓ Rolls up into small vortices
         ↓ Disrupts coherent structure
         ↓ Reduces net vorticity reduction
```

### Why It Fails
```
Individual mechanisms: Work OK in isolation
Combined: Spatial/temporal conflict creates instability
Result: Effective vortex suppression worse than either alone
```

---

## Mechanism 4: Energy Coupling Feedback (Nonlinear)

### How It Works
1. **Strong thermal** injects buoyancy energy (vertical KE increase)
2. **Strong momentum** removes kinetic energy (pressure-velocity coupling)
3. **Mismatch**: Energy injection ≠ Energy removal
4. **Result**: Net energy growth or oscillation

### Physical Signature
```
Energy vs Time (both high):
  
  Step 30:   600×10⁹ J (intervention starting)
  Step 50:   800×10⁹ J (growing—interactions amplify)
  Step 100:  900×10⁹ J (peak, then...) 
  Step 160:  700×10⁹ J (but vorticity not suppressed)
  
  → High energy + low vorticity = unphysical state
```

### Why It Fails
```
v5 (low both):      Balanced energy extraction → sustained suppression
Both high:          Unbalanced forces → energy growth → vortex survives
```

---

## Mechanism 5: Duration Mismatch (Timing)

### How It Works
Both interventions run for same window (50-step active + 40-step decay):

```
Timeline:
 0-50:   ACTIVE PHASE (full strength)
         Both thermal and momentum fighting
         Creates maximum shear/conflict
         
50-90:   DECAY PHASE
         Thermal: exp(-2(t-50)/40) → slower decay
         Momentum: exp(-2(t-50)/40) → same decay
         But vortex already weakened incorrectly
         
90-160:  POST-INTERVENTION
         No recovery possible
         Vortex in wrong state
```

### Why It Fails
```
Optimal: Suppress gently → let vortex weaken → watch it stay down
Both high: Suppress violently → vortex in unstable state → oscillates/reforms
```

---

## Predicted Ablation Results

Based on these mechanisms, I predict:

### Test 1: Baseline (0.5K, -50Pa)
**Prediction**: 85.6% reduction ✓
- Both mechanisms gentle
- No conflicts
- Sustained suppression

### Test 2: High Thermal Only (4K, 0Pa)
**Prediction**: 60-75% reduction (decrease)
- **Mechanism**: Over-injection creates asymmetry
- **Evidence**: 
  - Divergence increases (complex structure)
  - Circulation changes
  - Vorticity becomes multi-core
- **Conclusion**: Thermal over-drives disruption

### Test 3: High Momentum Only (0K, -500Pa)
**Prediction**: 70-80% reduction (slight decrease)
- **Mechanism**: Strong sink creates anti-vortex
- **Evidence**:
  - Vorticity changes sign (goes negative)
  - High divergence (opposing flows)
  - High kinetic energy (anti-vortex has energy)
- **Conclusion**: Momentum creates wrong type of suppression

### Test 4: Both High (4K, -500Pa)
**Prediction**: 50-70% reduction (significant decrease)
- **Mechanism**: Thermal + momentum conflict
- **Evidence**:
  - Worst of both worlds
  - Complex vorticity field
  - Possibly energy growth
  - Definitely high divergence
- **Conclusion**: Interaction instability dominates

---

## Hypothesis Ranking (Most to Least Likely)

1. **Interaction Instability** (60% probability)
   - Both-high worse than either individual
   - Shear-driven instabilities
   - Multi-mechanism conflict

2. **Thermal Over-Injection** (25% probability)
   - High thermal alone hurts
   - 4K is 8× nominal value
   - Disruption too aggressive

3. **Momentum Counter-Vortex** (10% probability)
   - -500Pa creates opposing circulation
   - Cancels vorticity but creates instability
   - Less likely because v5's -50Pa works OK

4. **Energy Coupling Feedback** (5% probability)
   - Nonlinear instability
   - Harder to detect
   - Would require energy analysis

---

## How to Distinguish (Ablation Results Will Show)

### If Test 2 (Thermal only) decreases:
→ **Thermal is part of problem**
→ Check: Is it solely thermal, or interaction?
→ Look at Test 3: if it doesn't decrease, then thermal + momentum interact

### If Test 3 (Momentum only) decreases:
→ **Momentum is part of problem**
→ Check: Is it -500Pa threshold, or any high value?
→ Look at Test 2: if it doesn't decrease, then momentum + thermal interact

### If both Test 2 & 3 unchanged (or improve):
→ **Interaction is sole problem**
→ Mechanism: They fight each other
→ Solution: Stagger, spatially separate, or use lower values together

### If both Test 2 & 3 worsen significantly:
→ **Multiple independent problems**
→ Can't just tune one parameter
→ Need combined approach (reduce both, stagger, redesign)

---

## Waiting for Ablation Results...

Once results are in, this framework will clearly identify:
1. **Which mechanism is dominant**
2. **How to fix it**
3. **Optimal parameter space**

The experiments will show whether:
- ✓ Individual mechanisms work
- ✗ They conflict when combined
- ⚠ One is fundamentally broken

This is textbook hypothesis testing + ablation study approach.
