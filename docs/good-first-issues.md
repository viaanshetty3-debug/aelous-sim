# Good first issues

Starter tasks for new contributors. Each one is self-contained. (Maintainer: post each as a GitHub issue
with the `good first issue` label, then link it here.)

---

## 1. Find the cooling threshold (20 / 30 / 40 °C on the 1 km ring)

**Labels:** `good first issue`, `experiment` · **Difficulty:** easy–medium · **Compute:** ~1 hour on a laptop

Cooling the 1 km ring by 10 °C weakened the tornado ~15% temporarily; cooling it by 60 °C collapsed it for
good. Somewhere in between is a threshold. A hypothesis in `AXISYM_RESULTS.md` says it is near the parent
storm's lifting strength (~26 °C equivalent).

- Add `Version`s for 20, 30 and 40 °C on the same ring as `cool 10 K` in `aeolus_axisym/interventions.py`.
- Run each for 30 minutes from `results/axisym/m35/mature.npz` (see "Reproduce" in `AXISYM_RESULTS.md`).
- Report while-on / after / last-5-minute changes vs the control, with the noise floor.

**Done when:** a table in `AXISYM_RESULTS.md` shows where the tornado stops recovering.

---

## 2. Fix the NOAA data download (404)

**Labels:** `good first issue`, `bug` · **Difficulty:** easy–medium

`noaa_data_ingestion.py` fetches `https://thredds.ucar.edu/thredds/catalog/gfs/Global_0p25deg/latest.xml`,
which now returns 404, so "hybrid" mode silently falls back to mock data.

- Find the current THREDDS catalog path for GFS 0.25° data.
- Update the URL and make the fallback log a clear warning.

**Done when:** `python main.py --initialization hybrid --n-steps 2` logs that real data was used.

---

## 3. Make the solver faster with Numba

**Labels:** `good first issue`, `performance` · **Difficulty:** medium

A 30-minute run takes ~13 minutes on a 4-core laptop. Most time is in `AxisymmetricModel.tendencies` and the
pressure solve (~41 ms per step at 160 × 160).

- Profile one step (`python -m cProfile`).
- Speed up the hot spots (e.g. Numba `@njit` kernels for advection/diffusion), keeping results identical.

**Done when:** `pytest tests/test_axisym_model.py` passes and a 100-step benchmark is at least 2× faster.

---

## 4. Draw a tornado that looks like a tornado (condensation funnel)

**Labels:** `good first issue`, `visualization` · **Difficulty:** medium

The current videos show wind speed in a vertical slice, which is accurate but doesn't look like a tornado.
A real funnel cloud is where the pressure drop is big enough for vapour to condense.

- In `aeolus_axisym/movie.py`, also record the pressure field.
- Draw the region where the pressure drop exceeds a chosen threshold (e.g. 20 hPa) as a grey-white funnel,
  ideally rotated into a 3D surface.

**Done when:** a short MP4 of the control tornado with a visible funnel is added to `docs/axisym/videos/`.

---

## 5. Repeat runs: how solid is the cooling result?

**Labels:** `experiment`, `statistics` · **Difficulty:** medium · **Compute:** a few hours

Every intervention so far was run once, from one mature tornado. Repeating runs from different starting
moments would give error bars.

- Add an option to `experiment.py spinup` that saves the state at several times (e.g. 25, 27.5, 30 min).
- Run the control and `cool 10 K` from each, then report the mean and spread of the effect.

**Done when:** `AXISYM_RESULTS.md` reports the cooling effect with an uncertainty from repeats.

---

## 6. Dose–response chart for the fan and cooling sweeps

**Labels:** `good first issue`, `visualization` · **Difficulty:** easy

Plot "change in peak wind vs power used" for every fan and cooling run, with the noise floor shaded, using
the data in `results/axisym/m35/runs/` (or the tables in `AXISYM_RESULTS.md`).

**Done when:** `docs/axisym/dose_response.png` exists and is linked from `docs/axisym/README.md`.

---

## 7. Does the grid resolution change the answer?

**Labels:** `experiment`, `verification` · **Difficulty:** medium · **Compute:** several hours

All results use a 25 m grid. Re-run the spin-up and the control at 12.5 m (`nr = nz = 320`) and compare the
tornado's average peak wind, core radius and pressure drop.

**Done when:** the comparison is added to the Limitations section of `AXISYM_RESULTS.md`.

---

## 8. Tests for AEOLUS-ALERT

**Labels:** `good first issue`, `tests` · **Difficulty:** easy

`alert/prototype_run.py` and `alert/types.py` have no tests.

- Add `tests/test_alert.py` covering the main data types and one end-to-end prototype run.

**Done when:** `pytest tests/test_alert.py` passes.

---

## 9. Explain the physics for students

**Labels:** `good first issue`, `documentation` · **Difficulty:** easy

Write `docs/physics.md`: in plain language, why suction strengthens a tornado (conservation of angular
momentum), why heating doesn't help, and why cold inflow can kill one. Diagrams welcome.

**Done when:** the page exists and is linked from the README.
