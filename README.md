# AEOLUS: can we weaken a tornado?

AEOLUS is a student research project that asks a simple question: **could a device near a tornado
weaken it?** It started with promising-looking simulations (85–117% "reduction"), found that those
numbers came from solver bugs, and rebuilt the simulator from scratch, verifying it against exact
solutions, to get an honest answer.

## What we found

All results come from a verified axisymmetric tornado model ([`aeolus_axisym/`](aeolus_axisym/)), compared
against an untouched control tornado and a measured noise floor.

| Idea | What happened to the tornado | Cost |
|---|---|---|
| Heat the air (0.5–4 °C) | Nothing measurable | up to ~4 kilotons of TNT worth of heat |
| Suck air out (−50 to −500 Pa) | **Got stronger**: +30% while running, +155% if left on | up to ~1 million tonnes of air removed per second |
| Fans blowing outward | Nothing, even with a 75 m/s outward blast | ~20 GW |
| Cool the inflow 10 °C | ~15% weaker while running, then recovers | ~170 GW |
| Cool a 1 km ring by 60 °C | **Collapsed below EF0 and stayed down** | ~1,000 GW (twice the average output of all US power plants) |

The short version: tornadoes are fed by a storm far larger than anything we can build, and most ways
of pushing on the air feed them. Only making the inflow air much colder than the storm can lift
worked, and it needs about a terawatt of cooling.

- Full write-up, verification and limitations: [`AXISYM_RESULTS.md`](AXISYM_RESULTS.md)
- Charts and side-by-side videos: [`docs/axisym/`](docs/axisym/README.md)

## Quick start

Requires Python 3.10+.

```bash
git clone https://github.com/viaanshetty3-debug/aelous-sim.git
cd aelous-sim
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Verify the solver against exact solutions (~10 s)
python -m pytest tests/test_axisym_model.py -v

# A small, fast experiment (~3 min): grow a tornado, run a control and one intervention, compare
python -m aeolus_axisym.experiment spinup --out results/demo --t-end 600 --set '{"nr": 80, "nz": 80}'
python -m aeolus_axisym.experiment run --out results/demo --version control --t-obs 300
python -m aeolus_axisym.experiment run --out results/demo --version "cool 10 K" --t-obs 300
python -m aeolus_axisym.report results/demo
```

The demo uses a coarse 50 m grid and short runs, so its numbers are noisy. The published results use a
25 m grid and 30–50 minute runs; see "Reproduce" in [`AXISYM_RESULTS.md`](AXISYM_RESULTS.md).

## Repository layout

| Path | What it is |
|---|---|
| `aeolus_axisym/` | **The current simulator**: model, tornado setup, interventions, experiments, reports, videos |
| `tests/test_axisym_model.py` | Verification against exact solutions (mass, Lamb–Oseen vortex, pressure balance, conservation) |
| `AXISYM_RESULTS.md` | Current results |
| `docs/axisym/` | Charts, tables and comparison videos |
| `alert/`, `FAST_WARNING_ALERT_SYSTEM.md` | AEOLUS-ALERT: a design for much faster tornado warnings |
| `realworld_test/` | An independent 2D test bed used earlier (its 80% result relied on tuned assumptions) |
| `main.py`, `solver.py`, … | The original 3D solver. Kept for history; its intervention results are superseded |
| `HARDWARE_PLAN.md`, `main.ino`, `CHAMBER_LAYOUT.md` | Tabletop vortex-chamber hardware plans |

## Contributing

Contributions are very welcome, from physics experiments to speed-ups to visualizations.
Start with [`CONTRIBUTING.md`](CONTRIBUTING.md) and the [good first issues](docs/good-first-issues.md).

## License

[MIT](LICENSE)
