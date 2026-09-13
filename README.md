# Aeolus Vortex Disruption Simulator

A 3D incompressible Navier-Stokes solver for modeling atmospheric vortex phenomena (EF4 tornadoes) and two synchronized disruption intervention modules.

## Quick Start

```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run full simulation with both interventions
python main.py --intervention both --output results/

# Run tests
python -m pytest tests/ -v

# Analyze results
python analysis/plot_metrics.py results/
```

## Project Goals

- Model EF4-scale Rankine vortex in cylindrical coordinates
- Achieve 70%+ core vorticity reduction via synchronized interventions
- Verify no post-intervention reformation over 50+ model minutes
- Maintain mass conservation and energy stability

## Simulation Modes

```bash
# Baseline (no intervention)
python main.py --intervention none --output results/baseline/

# Thermal RFD only
python main.py --intervention thermal --output results/thermal_only/

# Momentum sink only
python main.py --intervention momentum --output results/momentum_only/

# Both interventions (default)
python main.py --intervention both --output results/both/
```

See [CLAUDE.md](CLAUDE.md) for detailed architecture and parameter tuning.
