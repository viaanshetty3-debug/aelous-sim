# Intervention Energy Fix Log

**Date**: 2026-10-07  
**Issue**: Exponential kinetic energy divergence in 160-step simulations  
**Root Cause**: Interventions (thermal_rfd + momentum_sink) adding energy faster than dissipation

---

## Problems Identified & Fixed

### Problem #1: thermal_rfd.py Velocity Amplification (FIXED)

**Issue**: Lines 166-167 were multiplying velocities
```python
u_r = u_r * (1.0 + 0.1 * diffusion_boost)   # Amplified u_r
u_theta = u_theta * (1.0 + 0.05 * diffusion_boost)  # Amplified u_θ
```

**Impact**:
- Applied 50 times during active phase (steps 0-50)
- Each step: u → u × (1 + 0.01 to 0.1) = cumulative amplification
- Kinetic energy ∝ u², so repeated amplification = exponential KE growth

**Fix**: Comment out velocity amplification
```python
# REMOVED: Was amplifying u_r, u_theta by 1-10% per step
# u_r = u_r * (1.0 + 0.1 * diffusion_boost)
# u_theta = u_theta * (1.0 + 0.05 * diffusion_boost)
```

**Result**: Only buoyancy applied to u_z (conservative, energy-adding only for vertical acceleration)

---

### Problem #2: momentum_sink.py Permanent Application (FIXED)

**Issue**: Pressure deficit was applied EVERY step, never decaying
```python
p = p + self.pressure_deficit * sink_mask  # Applied forever!
```

**Impact**:
- Negative pressure perturbation (-250 Pa) applied continuously through all 160 steps
- Never decayed or turned off
- Created persistent pressure field coupling with solver
- May have been generating spurious kinetic energy through pressure-velocity coupling

**Fix**: Add decay schedule (matching thermal_rfd)
```python
def _sink_envelope(self, step: int):
    """Decay pressure sink after active_duration (50 steps)"""
    if step >= self.total_duration:  # 50 + 40 = 90
        return 0.0
    if step < self.active_duration:  # 0-50
        return 1.0
    else:  # 50-90
        decay_step = step - self.active_duration
        decay_fraction = decay_step / self.decay_duration
        return np.exp(-2.0 * decay_fraction)

# Apply with envelope
p = p + self.pressure_deficit * sink_mask * envelope
```

**Result**: 
- Steps 0-50: Full pressure deficit (-250 Pa)
- Steps 50-90: Exponentially decaying
- Steps 90+: Zero (no pressure perturbation)

---

## Expected Results After Fixes

### Energy Trajectory (Predicted)

Based on 30-step validation showing -3% per 10 steps:

```
Step 0:   585 ×10⁹ J (initial)
Step 30:  539 ×10⁹ J (-7.8%)
Step 60:  505 ×10⁹ J (-13.7%)
Step 90:  471 ×10⁹ J (-19.5%)  ← Interventions end here
Step 120: 437 ×10⁹ J (-25.3%)
Step 160: 385 ×10⁹ J (-34.2%)
```

**Key expectation**: Linear decay throughout, NO divergence after step 80

### Comparison to Previous Failure

**Before fixes (exponential divergence)**:
```
Step 80:   6,417 ×10⁹ J
Step 90:   8,079 ×10⁹ J (+26%)
Step 100:  11,563 ×10⁹ J (+43%)
Step 110:  16,296 ×10⁹ J (+41%)
Step 120:  23,877 ×10⁹ J (+46%)  ← EXPONENTIAL EXPLOSION
```

**After fixes (expected)**:
```
Step 80:   ~500 ×10⁹ J (linear)
Step 90:   ~475 ×10⁹ J (linear)
Step 100:  ~450 ×10⁹ J (linear)
Step 110:  ~425 ×10⁹ J (linear)
Step 120:  ~400 ×10⁹ J (linear)  ← STABLE, NO EXPLOSION
```

---

## Test Progress

**Test**: 160-step hybrid at 48³ with fixed interventions  
**Command**: 
```bash
python3 main.py --initialization hybrid --n-steps 160 --grid-size 48 \
  --dt 0.05 --cfl-target 0.7 --divergence-limit 0.05 \
  --intervention both --output results/hybrid_160_fixed_v1
```

**Monitoring**: Steps 30, 60, 80, 100, 120, 160 for energy trajectory validation

**Expected completion time**: ~4-5 minutes

---

## Success Criteria

✅ **Energy should**:
- Decay linearly (no exponential growth)
- Reach ~385×10⁹ J at step 160 (±20% acceptable)
- Stay below 600×10⁹ J throughout (no divergence)

✅ **Vorticity should**:
- Remain suppressed at 0.05 1/s
- Show >140% reduction (>70% target)

✅ **Stability should**:
- Divergence RMS <0.05 throughout
- No CFL adjustments needed
- No divergence explosion after step 80

✅ **Final state should**:
- No reformation detected
- Smooth, monotonic energy decay
- Simulation completes successfully

---

## If Test Still Shows Issues

**Troubleshooting plan**:
1. Check if energy is still growing after step 90 → problem in solver, not interventions
2. Check if growth is slower but still exponential → need stronger decay
3. Check if decay is too aggressive (energy dropping too fast) → tune decay constants
4. Check vorticity behavior → if not suppressed, may need stronger interventions

**Potential additional fixes**:
- Reduce pressure_deficit from -250 Pa to -100 Pa (weaker perturbation)
- Increase decay rate (reduce τ from 2.0 to 4.0 in exp decay)
- Add explicit energy dissipation term to solver
- Revisit thermal RFD buoyancy coefficient

---

**Status**: Testing in progress  
**Monitoring**: Real-time  
**Next action**: Analyze step 30, 60, 80, 100, 120, 160 results
