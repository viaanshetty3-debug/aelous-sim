# AEOLUS: can we weaken a tornado?

AEOLUS is a student research project that asks a simple question: **could a device near a tornado
weaken it?** It started with promising-looking simulations (85–117% "reduction"), found that those
numbers came from solver bugs, and rebuilt the simulator from scratch, verifying it against exact
solutions, to get an honest answer.

## What we found

All results come from a simplified tornado model ([`aeolus_axisym/`](aeolus_axisym/)) whose numerics are
checked against exact solutions. Each run is compared with an untouched control tornado and a measured
noise floor. **Read [what the model can and cannot tell you](#what-the-model-can-and-cannot-tell-you)
before quoting any number below.**

| Idea | What happened to the tornado | Cost |
|---|---|---|
| Heat the air (0.5–4 °C) | Nothing measurable | up to ~4 kilotons of TNT worth of heat |
| Suck air out (−50 to −500 Pa) | **Got stronger**: +30% while running, +155% if left on | up to ~1 million tonnes of air removed per second |
| Fans blowing outward | Nothing, even with a 75 m/s outward blast | ~20 GW |
| Cool the inflow 10 °C | ~15% weaker while running, then recovers | ~170 GW |
| Cool a 1 km ring by 60 °C | Mean surface wind fell below 29 m/s during minutes 15–30, with excursions above it | ~1,000 GW (twice the average output of all US power plants) |

The short version, within this model: the tornado is fed by a parent storm far larger than any of the
devices, and most ways of pushing on the air fed it. Only making the inflow air much colder than the
storm can lift weakened it, and that took about a terawatt of cooling.

The latest follow-up analysis distinguishes low average winds from sustained suppression. Cooling at
600 m altitude for 15 minutes kept every saved surface-wind sample below 29 m/s during minutes 30–45,
using 2.26 Mt of liquid-air equivalent. The upwind ring averaged below that threshold but exceeded it
for about 27% of the same window. Recovery after 45 minutes is untested. See the
[recovery report and chart](docs/axisym/recovery/recovery_report.md).

## What the model can and cannot tell you

The model is deliberately simple, so that its numerics can be checked exactly. Three simplifications
matter most:

| Simplification | What it means | How it can change the results |
|---|---|---|
| **Axisymmetric** (radius × height only) | Every quantity is the same at every angle around the tornado. | A "ring" of cooling surrounds the tornado completely; a real release would cover one side and could be bypassed. "Upwind" can only be modeled as a full ring. There is no rear-flank downdraft, storm motion or multiple-vortex structure, and brief pulses reach unrealistic 150–250 m/s. |
| **Fixed parent-storm force** | The supercell updraft is a constant upward push aloft, the same in every run. Nothing in the model can weaken or strengthen it. | The storm cannot respond to the intervention. A real storm could be weakened by cold inflow (cooling would work better than shown) or could produce a new tornado elsewhere (it would work worse). Because the push never fades, the model tends to rebuild the tornado once a device stops; "the tornado recovers" is partly built in. |
| **Constant eddy viscosity** (25 m²/s everywhere) | Turbulent mixing is the same in calm air, in the tornado core and in cold, stable air near the ground. | Real cold, stable air mixes much less, so it would spread and stay cold differently from the model. In models of this kind, tornado strength also depends on the assumed viscosity and surface friction. How the results change if it is halved or doubled has not been tested. |

There is also no moisture, rain or cloud physics, and cooling of 60 °C lies outside the model's
Boussinesq approximation, so those runs are qualitative.

**What the tests show, and what they don't.** The tests in `tests/test_axisym_model.py` pass, which shows
that the code solves the model's equations correctly: mass is conserved, a known vortex matches its exact
solution to 0.06%, and errors shrink at the expected rate as the grid is refined. They do not show that the
model behaves like a real tornado. Its control tornado falls inside the observed EF4 ranges, but the
storm push and environmental spin were adjusted during setup until it did, so that match is not
independent evidence. No run has been compared with observations of a real tornado's response to
anything.

Treat every result here as **how this simplified vortex responds**: useful for spotting ideas that work against
well-understood physics (suction strengthened the vortex by the same spin-up mechanism that makes real
tornadoes) and for estimating scale, but not as a prediction
of what would happen to a real tornado.

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
| `tests/test_axisym_model.py` | Numerical checks against exact solutions (mass, Lamb–Oseen vortex, pressure balance, conservation); they test the code, not the realism of the model |
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
