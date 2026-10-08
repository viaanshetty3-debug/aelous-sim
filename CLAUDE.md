# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Aeolus Sim** is a 3D incompressible Navier-Stokes solver for modeling and disrupting atmospheric vortex phenomena (e.g., EF4 Rankine tornadoes). The solver operates on a cylindrical grid (r, θ, z) and includes two synchronized intervention modules designed to reduce core vorticity by 70%+.

## Core Architecture

### Main Components

- **Grid Engine** (`grid.py`): Cylindrical (r, θ, z) spatial discretization with staggered grid for velocity/pressure decoupling
- **Navier-Stokes Solver** (`solver.py`): Incompressible flow solver using pressure-correction (SIMPLE) scheme
  - Convection: 3rd-order QUICK or 2nd-order central differences
  - Diffusion: Central differences
  - Pressure: Poisson solver (conjugate gradient or multigrid)
- **Rankine Vortex Module** (`baseline.py`): Initializes EF4-scale vortex flow field with configurable peak tangential velocity and core radius
- **Thermodynamic RFD Intervention** (`interventions/thermal_rfd.py`): Injects localized positive buoyancy in rear-flank downdraft coordinates to destabilize temperature-density gradient
- **Momentum Sink Intervention** (`interventions/momentum_sink.py`): Applies tangential suction sink (-500 Pa) + surface-inflow blackout during pressure-correction loops
- **Diagnostics** (`diagnostics.py`): Real-time vorticity tracking, circulation measurements, post-intervention reformation detection
- **Output** (`output.py`): Exports time-series metrics and final dissipation summary

### Module Interaction

```
Rankine Baseline → Navier-Stokes Time Stepping
                 ↓
          Intervention 1: Thermal RFD (applies to momentum equations + energy)
          Intervention 2: Momentum Sink (applies during pressure correction)
                 ↓
          Diagnostics (measure vorticity, check reformation)
                 ↓
          Output (save metrics at checkpoints)
```

## Development Commands

### Setup
```bash
# Initialize environment
python -m venv venv
source venv/bin/activate
pip install numpy scipy matplotlib h5py

# Optional: for visualization during development
pip install mayavi  # 3D plotting, may require VTK
```

### Running

```bash
# Full simulation with both interventions
python main.py --intervention both --output results/

# Single intervention tests
python main.py --intervention thermal --output results/thermal_only/
python main.py --intervention momentum --output results/momentum_only/

# Baseline (no intervention) for comparison
python main.py --intervention none --output results/baseline/

# Custom parameters
python main.py --core-radius 500 --max-velocity 100 --grid-size 64 --dt 0.1 --intervention both

# Intervention strength (defaults are v5: 0.5 K / -50 Pa; v7 recommended: 4.0 K / -50 Pa)
python main.py --initialization hybrid --n-steps 160 --thermal-k=4.0 --momentum-pa=-50 --output results/v7
```

### Testing

```bash
# Run unit tests
python -m pytest tests/ -v

# Test individual modules
python -m pytest tests/test_solver.py -v
python -m pytest tests/test_interventions.py -v

# Validate Rankine vortex initialization
python -c "from baseline import verify_rankine; verify_rankine()"
```

### Visualization & Analysis

```bash
# Post-run analysis (generates plots from output)
python analysis/plot_metrics.py results/

# Compare interventions
python analysis/compare_runs.py results/baseline/ results/thermal_only/ results/momentum_only/ results/both/
```

## Key Parameters & Tuning

- **Grid resolution**: 64³ typical; 32³ for fast iteration, 128³ for production
- **Time step (dt)**: Must satisfy CFL (Δt ≤ dx / |u_max|), typically 0.01–0.1 seconds
- **Vortex parameters**:
  - Peak tangential velocity: 80–150 m/s (EF4 range ~90 m/s)
  - Core radius: 400–600 meters
  - Ambient pressure: 900 hPa
- **Thermal RFD injection**:
  - Location: z-level at 80% height, radial extent 1.5× core radius
  - Buoyancy perturbation: +2–5 K
  - Injection duration: 30–60 seconds
- **Momentum sink**:
  - Pressure deficit: -500 Pa (tunable)
  - Blackout zone: 5–10 grid cells at lower boundary
  - Activation: during pressure-correction phase only

## Success Metrics

1. **Core vorticity reduction**: ≥70% drop relative to baseline peak by t = simulation_end
2. **No post-intervention reformation**: Circulation should remain suppressed for ≥50 model minutes
3. **Mass conservation**: ∫∫∫ ρ dV = constant to machine precision
4. **Energy stability**: Kinetic energy should decay monotonically post-intervention (no spurious amplification)

## Code Organization

```
aeolus_sim/
├── CLAUDE.md
├── main.py                    # Entry point
├── grid.py                    # Cylindrical mesh + coordinate transforms
├── solver.py                  # Pressure-correction incompressible solver
├── baseline.py                # Rankine vortex initialization
├── interventions/
│   ├── __init__.py
│   ├── thermal_rfd.py        # Buoyancy injection
│   └── momentum_sink.py       # Pressure/velocity sinks
├── diagnostics.py             # Vorticity, circulation, reformation tracking
├── output.py                  # HDF5 checkpoints + summary export
├── analysis/
│   ├── plot_metrics.py        # Time-series + field plots
│   └── compare_runs.py        # Multi-run comparison
├── tests/
│   ├── test_solver.py
│   ├── test_interventions.py
│   └── test_baseline.py
└── results/                   # Output directory (git-ignored)
```

## Important Notes

- **CFL stability**: Monitor CFL number (|u|·dt/dx) during iteration; should stay < 1 for explicit convection
- **Pressure-velocity coupling**: Ensure SIMPLE iterations converge (check residuals); tune under-relaxation factors if diverging
- **Cylindrical coordinates**: Handle singularity at r=0 carefully (use r > ε or switch to Cartesian near axis if needed)
- **Intervention timing**: Both modules must activate *simultaneously* at t=t_start; staggered timing may reduce effectiveness
- **Output size**: 64³ grid at 100 time steps ~30–50 MB; use checkpoint intervals wisely for long runs

## References & Constraints

- Incompressibility enforced via Poisson equation for pressure
- No stratification (Boussinesq) unless thermal module is active
- Flat-earth beta=0 approximation (no Coriolis)
- Periodic BC in θ, no-slip walls at r_inner/r_outer and z=0/z_top (wall friction optional)
