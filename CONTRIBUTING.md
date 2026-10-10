# Contributing to AEOLUS

Thanks for your interest! AEOLUS is a student project testing whether a device could weaken a tornado.
All kinds of contributions help: new experiments, faster code, better visualizations, documentation,
and checking our physics.

## Setup

```bash
git clone https://github.com/viaanshetty3-debug/aelous-sim.git
cd aelous-sim
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m pytest tests/ -q        # everything should pass
```

The quick demo in the [README](README.md#quick-start) runs a small experiment in about 3 minutes.

## Where things are

- `aeolus_axisym/model.py`: the solver (axisymmetric Navier–Stokes with swirl, staggered grid, SSP-RK3,
  exact pressure projection)
- `aeolus_axisym/tornado.py`: the tornado setup (parent-storm forcing, environmental spin) and diagnostics
- `aeolus_axisym/interventions.py`: every device that has been tested, as a `Version`
- `aeolus_axisym/experiment.py`: spin-up and intervention runs
- `aeolus_axisym/report.py`, `fan_report.py`: scoring against the control and the noise floor
- `aeolus_axisym/movie.py`: videos
- `tests/test_axisym_model.py`: verification against exact solutions

The old 3D solver (`main.py`, `solver.py`) is kept for history only. Please don't base new results on it.

## Ground rules for experiments

These exist because the project's first results were wrong for exactly these reasons.

1. **Always compare against a no-intervention control** run from the same starting state, over the same
   time window. A drop from the starting value is not a result; tornadoes change on their own.
2. **Respect the noise floor.** The simulated tornado pulses, so two runs that differ only by chance can
   disagree by ±10–30% depending on the averaging window. Use the noise floor computed in
   `aeolus_axisym/report.py` and never report a "best moment".
3. **Model what a device physically does.** Heating heats, suction removes air, fans push air. Don't add
   terms that directly slow the tornado down unless that is itself the thing being tested.
4. **Say what it would cost.** Report the energy or power the device needs alongside its effect.
5. **Don't commit `results/`.** It's git-ignored. Put conclusions in `AXISYM_RESULTS.md` and small
   charts or videos in `docs/axisym/`.

Adding a new device is usually a new `Version(...)` entry in `interventions.py`, plus (if needed) a few lines
in `Device.forcing`. Run it with `python -m aeolus_axisym.experiment run --out <dir> --version "<name>"`.

## Changing the solver

If you touch `model.py`, run `python -m pytest tests/test_axisym_model.py -v` and include the output in your
PR. Changes that alter results should explain why the new behaviour is more physically correct, ideally
with a new verification test.

## Making a pull request

1. Fork the repo and create a branch (`git checkout -b my-change`).
2. Keep each PR focused on one thing.
3. Run `python -m pytest tests/ -q` before pushing.
4. Open the PR and fill in the template: what changed, why, and how you checked it.

New to open source? Look at the [good first issues](docs/good-first-issues.md), or open an issue to ask
a question. No question is too basic.
