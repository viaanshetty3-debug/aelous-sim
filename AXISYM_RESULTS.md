# AEOLUS interventions v1–v7 and RW80 in a simplified axisymmetric tornado model

Date: 2026-10-09. Model: `aeolus_axisym/` (replaces the results produced with `solver.py`).
Raw data: `results/axisym/m35/` (git-ignored). Charts, tables and videos: [`docs/axisym/`](docs/axisym/README.md). Regenerate with the commands at the end.

> **Read this first.** Every result below describes how one simplified model vortex responds. The model is
> axisymmetric, is driven by a fixed parent-storm force that nothing can weaken, and uses a constant eddy
> viscosity. Its tests show the numerics are correct, not that it behaves like a real tornado. See
> [Limitations](#limitations) for how each simplification can change the results.

## Bottom line

**In this model, no version of the AEOLUS intervention weakens the tornado by more than chance, in any time window.**

- **Heating (thermal RFD)** has no measurable effect at any strength (0.5–4 K) or duration (4.5 s or ~108 s).
- **Suction + inflow blackout** makes the tornado **stronger** while it runs: the 60-second versions raise
  the mean peak wind in the first 10 minutes from 67 m/s to 80–89 m/s (+19 to +33%). Once the device stops,
  the tornado returns to its normal behaviour.
- **Leaving the suction on (v1)** turns the tornado into a much stronger one: mean peak wind 173–177 m/s
  vs 68 m/s, central pressure drop 187–197 hPa vs 43 hPa (+155% wind, +334% pressure drop).
- **The test-bed configuration that reported 80% sustained reduction (RW80)** makes the tornado 26%
  *stronger* in the first 10 minutes and has no measurable lasting effect (+6.8%, within noise). Even
  with the test bed's assumed spin-down terms added back in, the lasting effect is −3.4%, within noise.
- The largest apparent "reductions" (−60 to −73% at single moments) are **noise**: a run nudged by just
  0.001 K also differs from the control by up to 154% at single moments, because the tornado pulses.

## The model

Axisymmetric (radius × height) incompressible Boussinesq Navier–Stokes with swirl: the standard setup
used in tornado-vortex research (Rotunno 1979; Fiedler 1994; Lewellen et al.).

| Item | Choice |
|---|---|
| Equations | full momentum (incl. centrifugal v²/r), angular momentum M = r·v in flux form, buoyancy, exact continuity |
| Grid | 160 × 160, 25 m spacing, 4 km × 4 km domain |
| Numerics | staggered grid, 3rd-order upwind advection, SSP-RK3, exact pressure projection after every stage |
| Turbulence | constant eddy viscosity and diffusivity, 25 m²/s |
| Ground | no-slip |
| Parent storm | fixed upward body force aloft (peak 0.9 m/s² at 2.5 km, 1 km wide), stands in for the supercell updraft |
| Environment | outer sponge holds angular momentum at 3.5×10⁴ m²/s (the rotating mesocyclone) |

No artificial damping, velocity clipping or energy "safety" steps.

### Numerical verification (tests/test_axisym_model.py, 8 tests, all pass)

These tests check that the code solves the equations above correctly. They say nothing about whether those
equations describe a real tornado well; see [Limitations](#limitations).

| Test | Result |
|---|---|
| Mass conservation after projection | divergence ≤ 10⁻¹⁰ (round-off) |
| Lamb–Oseen vortex vs exact solution (25 m grid) | max error 0.063% of peak wind |
| Convergence order (50 → 25 m) | error ratio 3.75 (2nd order = 4) |
| Pressure vs cyclostrophic balance ρv²/r | within 1% |
| Total angular momentum and heat, closed box | conserved to 10⁻¹⁰ |
| Unforced flow | kinetic energy never increases |
| Mass sink | divergence equals sink exactly; inflow at outer wall balances it to 10⁻¹² |
| Imposed pressure field (gradient force) | produces exactly zero flow (see "momentum sink" below) |

### The simulated tornado (control, 50 minutes)

| | Model | Observed EF4 tornadoes |
|---|---|---|
| Mean peak wind, z ≤ 500 m | 68 m/s (sd 18) | 74–89 m/s (EF4 band) |
| Mean peak wind, z ≤ 100 m | 65 m/s | — |
| Core radius | ~190–290 m | 100–500 m |
| Mean central pressure drop | 43 hPa | ~20–100 hPa |

This is a plausibility check, not validation. The parent-storm push and environmental angular momentum
were adjusted over several spin-ups during setup (logs are git-ignored) until the tornado fell in these ranges, so the
match is by construction.

The vortex pulses (core contracts and breaks down every ~40 s), as real tornadoes do. Its averages are
realistic; its brief peak spikes (up to 150–250 m/s) are not. See Limitations.

## How each version was translated

Parameters are taken from the commits listed. Old step counts were converted with the old time steps
(main.py: 0.05 s; realworld_test: 0.25 s).

| Version | Source | Heating | Suction (pressure deficit) | Blackout | Timing as coded |
|---|---|---|---|---|---|
| v1 | e2ff6e8 | 2 K, on axis at 2.1 km | −250 Pa, ring at r = 800 m, z = 1.5 km | z < 200 m, r < 2 km | heat 2.5 s + 2 s decay; **suction + blackout never switched off**; also multiplied wind speed during heating (not physical) |
| v2/v3 | ed5dbec | 2 K | −250 Pa | yes | 2.5 s + 2 s decay for both |
| v4/v5 | 524d31e | 0.5 K | −50 Pa | yes | 2.5 s + 2 s |
| v6 thermal-only | ablation | 4 K | — | — | 2.5 s + 2 s |
| v6 momentum-only | ablation | — | −500 Pa | yes | 2.5 s + 2 s |
| v6 both-high | ablation | 4 K | −500 Pa | yes | 2.5 s + 2 s |
| v7 | V7_RESULTS | 4 K | −50 Pa | yes | 2.5 s + 2 s |
| RW80 | b40a2c8 (realworld_test) | 4 K ring at 1.5 × core radius | −500 Pa centred on the core radius | z < 200 m, r < 3 km | heat 10 s + 10 s; suction + blackout on for 45 s |
| RW80 + assumed braking | b40a2c8 | as RW80, plus the test bed's imposed spin-down terms (0.15/s "thermal disruption" and the 0.24/s "equilibration" brake) | | | |

Every v1–v7 version was also run with **60 s injection** (60 s + 48 s decay), the duration the design spec
in CLAUDE.md calls for, since the coded 4.5 s is far shorter than any tornado timescale.

**Device physics:**
- *Heating*: the target region's temperature anomaly is raised to ΔT; the warm air then moves and mixes freely.
- *Suction*: modelled as **air removal** (a mass sink) with strength set so the still-air pressure deficit
  equals the version's value. An imposed pressure field by itself cannot move air in incompressible flow;
  the test suite shows it produces exactly zero flow, so the literal reading of the old code would have
  no effect at all.
- *Blackout*: drag on low-level radial and vertical wind at the same per-second rates the old code applied.

## Results

All runs start from the same mature tornado (t = 30 min of spin-up) and run 50 minutes, the project's
own "no reformation for ≥ 50 model minutes" criterion. Change in **mean peak wind (z ≤ 500 m)** relative to
the control over the same period; **+ = stronger tornado**. `~` = within the 2-sigma noise floor.

**Noise floor (2σ)**, from the control's own variability (sd 18 m/s, autocorrelation time 40 s): two runs that
differ only by chance disagree by up to **±8.9%** over 50 min, **±19.8%** over the first 10 min,
**±28%** over the last 5 min.

| Version | 50-min mean | First 10 min | Last 5 min | Mean wind first 10 min (control 67.1) | Mean pressure drop 50 min (control 43.1 hPa) | Heat used (kt TNT) | Air removed (million t) |
|---|---|---|---|---|---|---|---|
| v1 | **+155%** | **+108%** | **+168%** | 139.5 m/s | 187 hPa | 0.51 | 1,993 |
| v1 (60 s) | **+161%** | **+140%** | **+166%** | 161.3 | 197 | 2.43 | 1,993 |
| v2/v3 | −3.5% ~ | −4.0% ~ | −13.6% ~ | 64.5 | 43.1 | 0.51 | 2.5 |
| v2/v3 (60 s) | +0.1% ~ | +19.4% ~ | −16.4% ~ | 80.1 | 47.2 | 1.66 | 60 |
| v4/v5 | −3.0% ~ | −5.3% ~ | −16.0% ~ | 63.6 | 44.7 | 0.13 | 1.1 |
| v4/v5 (60 s) | −2.4% ~ | +9.4% ~ | −17.4% ~ | 73.4 | 46.3 | 0.32 | 27 |
| v6 thermal-only | −4.4% ~ | +1.1% ~ | −18.2% ~ | 67.9 | 44.1 | 0.98 | 0 |
| v6 thermal-only (60 s) | −0.3% ~ | +2.6% ~ | −8.0% ~ | 68.9 | 45.6 | 1.92 | 0 |
| v6 momentum-only | +1.2% ~ | −3.6% ~ | −12.1% ~ | 64.7 | 43.2 | 0 | 3.6 |
| v6 momentum-only (60 s) | +6.5% ~ | **+32.3%** | −9.2% ~ | 88.8 | 45.5 | 0 | 85 |
| v6 both-high | −1.4% ~ | −2.9% ~ | −8.0% ~ | 65.1 | 44.4 | 1.05 | 3.6 |
| v6 both-high (60 s) | +5.3% ~ | **+32.8%** | −14.4% ~ | 89.2 | 47.2 | 3.93 | 85 |
| v7 | −0.9% ~ | −5.5% ~ | +0.1% ~ | 63.4 | 43.5 | 1.00 | 1.1 |
| v7 (60 s) | +4.6% ~ | +11.2% ~ | −9.5% ~ | 74.6 | 48.3 | 2.53 | 27 |
| RW80 | +6.8% ~ | **+26.5%** | +0.3% ~ | 84.9 | 46.0 | 1.30 | 8.8 |
| RW80 + assumed braking | −3.4% ~ | +17.3% ~ | −18.0% ~ | 78.8 | 44.1 | 1.30 | 8.8 |

The two 0.001 K "null" runs give 50-min means of −1.4% and −1.8%, consistent with the noise floor.
Full per-metric table (surface wind, vorticity, circulation, EF ratings): `results/axisym/m35/results_table.md`.
Time series of every run: `results/axisym/m35/timeseries.png`.

## What the results mean

1. **Heating does nothing measurable.** 0.5–4 K of warming aloft is tiny next to the parent storm's
   updraft forcing (equivalent to ~25 K of buoyancy). Warm air rising on the axis joins the updraft that
   already feeds the tornado. If anything, physics predicts slight strengthening, consistent with
   observations that tornadic storms tend to have warmer rear-flank downdrafts (Markowski et al. 2002).

2. **Suction strengthens the tornado.** Removing air around the vortex draws more air inward. Inflowing air
   conserves angular momentum, so it spins faster as it moves in, like a skater pulling in their arms.
   This is the same mechanism that makes tornadoes in the first place. The blackout, which slows
   low-level wind, does not prevent the strengthening.

3. **The longer the suction runs, the stronger the tornado.** 4.5 s: no detectable effect. ~108 s:
   +19 to +33% during the first 10 minutes. Permanent (v1): +155%, an EF5-class vortex. v1's velocity
   multiplication (2.5 s) is unlikely to be the cause: v2/v3 has the same suction switched off after 4.5 s
   and shows no lasting effect, while v1 with 60 s of multiplication ends up about the same as v1.

4. **Effects do not persist.** Once a device switches off, the parent storm and environment restore the
   tornado within minutes. Nothing suppresses the tornado over 50 minutes. Part of this is built into the
   model: the parent-storm push is fixed and never weakens, so it always works to rebuild the vortex.

5. **Why the test bed reported 80%.** In `realworld_test`, the momentum sink (a) cut the model's own
   "keep the tornado alive" forcing by 90% wherever it acted, and (b) applied a direct braking term whose
   rate was tuned until reduction exceeded 80%. Neither is something a device does. With only the device's
   physical actions, RW80 makes the tornado stronger. Adding the assumed braking terms back in cancels that
   strengthening but still produces no reduction beyond noise.

## Scale of the devices

| | Amount | For comparison |
|---|---|---|
| 4 K heating, 60 s (v6 thermal-only 60 s) | 1.9 kt TNT of heat | ~1/8 of the Hiroshima bomb |
| −50 Pa suction for 4.5 s (v4/v5, v7) | 1.1 million t of air removed | ~300,000 t/s while on |
| −500 Pa suction for 60 s (v6 60 s) | 85 million t of air removed | ~1 million t/s while on |
| v1, suction never switched off | 2.0 billion t over 50 min | |

A pressure deficit is small (500 Pa is 0.5% of atmospheric pressure), but holding it over a region a
kilometre across means moving air through an area of ~10⁷ m² at tens of m/s.

## Limitations

The model is built to be checkable, not complete. The passing tests show the numerics are right; nothing
here has been validated against how a real tornado responds to an intervention. Each simplification below
can move the results, in a direction that is often unknown.

- **Axisymmetric (radius × height only).** Everything is identical at every angle around the axis.
  - Interventions are full rings around the tornado. A real release would cover one side, and air could
    flow around it. The "upwind" runs are rings 2–3 km out, not upwind patches.
  - There is no rear-flank downdraft, no storm motion, no multiple-vortex structure and no asymmetric
    breakdown. Real tornadoes shed energy through 3D instabilities; this model cannot, so brief pulses spike
    to unrealistic 150–250 m/s. Window averages are more meaningful than single moments.
  - An attempt to repeat the cooling test in 3D with CM1 has not yet produced a tornado
    ([`cm1_colab/README.md`](cm1_colab/README.md)).
- **Fixed parent-storm force.** The supercell updraft is a prescribed upward push (peak 0.9 m/s² at
  2.5 km), identical in every run and unaffected by anything below it.
  - The storm cannot respond. Cold inflow might weaken a real storm's updraft, making cooling more effective
    than shown; or the storm might reorganize and produce a new tornado nearby, making it less effective.
    The model cannot distinguish these.
  - Because the push never fades, the model tends to rebuild the vortex once a device stops. Findings that
    "the tornado recovers" or "striking early only delays it" are partly a consequence of this.
  - The "~25 K equivalent" strength of the storm, used to explain why 60 °C cooling worked and 10 °C did
    not, is a property of this prescribed force, not a measured storm.
- **Constant eddy viscosity and diffusivity (25 m²/s).** Real turbulent mixing varies by orders of
  magnitude.
  - Cold, stable air near the ground mixes much less than warm, turbulent air. The model mixes the cooled
    air at the same rate as everything else, which changes how far it spreads and how long it stays cold,
    the key process in every cooling result.
  - In vortex models of this kind, tornado strength depends on the assumed viscosity and surface friction
    (e.g. Fiedler 1994). No run has tested how the results change with a different value.
- **Boussinesq approximation.** Density changes are assumed small. Cooling by 60 °C or more changes density
  by ~20%, well outside that range, so all strong-cooling results are qualitative.
- **No moisture, rain or cloud physics**, and a uniform, no-slip ground with no roughness variation.
- **One tornado, one resolution, single runs.** All interventions start from the same mature tornado on the
  same 25 m grid, and each version was run once. A second, more strongly rotating storm was spun up but no
  interventions were run on it. A finer grid or a different storm could change the numbers; how much is untested.
- **Tuned setup.** The storm push and environmental spin were chosen to give an EF4-like control tornado,
  so its resemblance to real tornadoes is not independent evidence for the model.
- **Device actions taken literally** from the code. A differently placed or differently designed device
  was not tested.

**What would test the model's realism:** repeating the key runs with half and double the eddy viscosity,
from the second storm and on a finer grid; and a 3D model in which the parent storm can respond (see
[good first issues](docs/good-first-issues.md)).

## Reproduce

```bash
python -m pytest tests/test_axisym_model.py -v
python -m aeolus_axisym.experiment spinup --out results/axisym/m35 --t-end 1800 --set '{"M_inf": 35000}'
aeolus_axisym/run_all.sh results/axisym/m35 3000 7        # 19 runs, 50 model minutes each
python -m aeolus_axisym.report results/axisym/m35
python -m aeolus_axisym.movie record --out results/axisym/m35 --version control   # then render, see movie.py
```

## Follow-up: "what would it take?" (2026-10-09)

Two further devices, chosen because physics suggests they are the only directions that could weaken a
tornado. Both run for 10 minutes, then switch off; 30 minutes simulated; same mature tornado and control.
Noise floor (2σ): ±20% while on (10-min window), ±14% after (20-min window).

### Outward fans (cut the inflow)

A ring of fans at r = 1 km blowing outward through the lowest 200 m. Without fans that zone carries
inflow of ~15 m/s (up to 32 m/s) toward the tornado.

| Fan push | Wind at the fan ring | Minimum fan power (momentum theory) | Tornado while on | After off |
|---|---|---|---|---|
| 0.05 m/s² | 31 m/s outward | 0.1 GW | −1.2% ~ | +0.1% ~ |
| 0.2 m/s² | 34 m/s outward | 0.7 GW | −4.3% ~ | +0.9% ~ |
| 0.5 m/s² | 38 m/s outward | 2.7 GW | −3.5% ~ | +1.9% ~ |
| 1 m/s² | 44 m/s outward | 7.6 GW | −9.2% ~ | +2.7% ~ |
| 2 m/s² | 75 m/s outward | 21.5 GW | −2.9% ~ | −0.8% ~ |

Reversing the low-level inflow into a 75 m/s outward blast (thrust ~1,100 MN, about 2,000 jumbo-jet
engines) does not measurably weaken the tornado, and there is no trend with fan strength.

### Low-level cooling (a man-made cold pool)

A ring of near-ground air (centred r = 1 km, ~1 km wide, 250 m deep) held at least ΔT colder than its
surroundings. Real storm cold pools are 3–10 °C and are a known way tornadoes end.

| Cooling | Heat removed (power) | Water if done by evaporation | Tornado while on | After off | Pressure drop while on |
|---|---|---|---|---|---|
| 1 °C | 20 GW | 8 t/s | −2.3% ~ | −2.4% ~ | −2.6% ~ |
| 3 °C | 56 GW | 23 t/s | −6.0% ~ | −6.9% ~ | −5.5% ~ |
| 6 °C | 106 GW | 43 t/s | −9.9% ~ | −5.7% ~ | −6.4% ~ |
| 10 °C | 168 GW | 67 t/s | −14.2% ~ | −11.7% ~ | −12.5% ~ |

Each value is individually within the noise floor, but unlike every other device the four strengths all
point the same way and grow steadily with the amount of cooling (minutes 2–10 of cooling: −0%, −3%, −7%,
−12%, −18% from 0 to 10 °C). A shared-control bias cannot produce a dose–response like that (other
devices average about −2.5% in the same window). This is **suggestive evidence that cooling weakens the
tornado, but not proof**, and even the strongest case is ~15%, far from the 70% target.

Cost of the 10 °C case: 168 GW of continuous cooling, about a third of the average output of all US power
plants, or 67 tonnes of water evaporated per second. The inflow air feeding tornadoes is usually close to
saturated, so that much evaporation is not physically available, and the evaporated water condenses again
in the updraft, returning its heat to the storm.

To confirm the cooling trend: run each strength several times from different mature states and/or cool for
longer (30+ min), then compare the spread of results.

### Cooling at ~6× the power (2026-10-09)

Three ways to put roughly 6× the cooling power of "cool 10 K" (168 GW) into the low-level inflow:

| Run | Cooling power | Tornado while on | Minutes 10–30 (after) | Last 5 min | Pressure drop while on |
|---|---|---|---|---|---|
| 10 °C ring (reference) | 168 GW | −14% ~ | −12% ~ | | −13% |
| 10 °C, ring 2× wider and deeper | 651 GW (3.9×) | −16% ~ | **−18%** | −16% ~ | −17% |
| 10 °C, cold pool out to ~2.5 km, 750 m deep | 1,402 GW (8.3×) | −13% ~ | **−25%** | −10% ~ (recovered) | −21% |
| **Same ring cooled by 60 °C** | **1,031 GW (6.1×)** | **−36%** | **−64%** | **−72%** | **−57%** |

Noise floor (2σ): ±20% while on, ±14% for minutes 10–30, ±28% for the last 5 minutes.

5-minute mean peak wind, 60 °C run vs control (m/s): 54/69, 33/66, 28/67, 26/65, 22/65, 20/71. The
tornado collapses below EF0 strength and does not recover in the 20 minutes after cooling stops (the cold,
dense air stays pooled near the ground). This is the first and only intervention in this study that
weakens the tornado by a large margin beyond noise.

> **Correction (2026-11-26).** These are 5-minute means of the peak wind up to 500 m. They do not show that
> every sample stayed below 29 m/s, near-surface winds had excursions above it, and the run is too short to
> establish permanent suppression. See "Recovery audit" below.

**What made the difference is how cold, not how much power.** The large 10 °C pools used as much or more
power and only weakened the tornado temporarily (it recovered within ~20 minutes). A plausible explanation,
not yet tested: the parent-storm forcing in this model is equivalent to ~26 °C of warmth, so air cooled by
10 °C can still be lifted into the updraft while air cooled by 60 °C cannot. A 20–40 °C sweep would test
that threshold.

**Caveats.**
- 60 °C of cooling is far beyond any natural cold pool (3–10 °C). It would take 25 °C inflow air to −35 °C.
- That is outside the model's Boussinesq approximation (density changes of ~20% vs the assumed few %), so
  the 60 °C numbers are qualitative.
- Evaporating water can only cool air to its wet-bulb temperature, a few °C in the humid air that feeds
  tornadoes, so this cannot be done with water. It would need refrigeration or a cryogen: roughly
  3,000 tonnes of liquid nitrogen per second (≈1.7 million tonnes over 10 minutes).
- The heat removed in 10 minutes, 6×10¹⁴ J, equals ~150 kilotons of TNT, and would have to be dumped
  somewhere other than into the storm.
- Single runs from one tornado; repeats from other mature states would confirm the size of the effect.

### Smaller rings cooled harder (2026-10-10)

Can a smaller ring, cooled more, get the same result with less power? Same protocol (10 min on, 30 min total).
Power is the average over the 10 minutes of cooling.

| Run | Ring | Avg cooling power | While on | Minutes 10–30 | Last 5 min |
|---|---|---|---|---|---|
| 60 °C ring (from above) | r = 1 km, ~1 km wide, 250 m deep | 1,031 GW | **−36%** | **−64%** | **−72%** |
| small, 30 °C | r = 500 m, ~500 m wide, 125 m deep | 136 GW | **−26%** | **−22%** | −12% ~ |
| small, 60 °C | same | 171 GW | **−28%** | **−24%** | −6% ~ |
| small, 100 °C | same | 197 GW | **−30%** | **−33%** | −21% ~ |
| tiny, 60 °C | r = 300 m, ~300 m wide, 100 m deep | 114 GW | **−27%** | −14% ~ | −14% ~ |
| tiny, 100 °C | same | 131 GW | **−29%** | **−18%** | −11% ~ |

Noise floor (2σ): ±20% while on, ±14% for minutes 10–30, ±28% for the last 5 minutes.

5-minute mean peak wind, run / control (m/s):

| Run | 0–5 | 5–10 | 10–15 | 15–20 | 20–25 | 25–30 |
|---|---|---|---|---|---|---|
| small, 30 °C | 59/69 | 41/66 | 36/67 | 49/65 | 61/65 | 63/71 |
| small, 100 °C | 53/69 | 42/66 | 36/67 | 39/65 | 47/65 | 56/71 |
| tiny, 60 °C | 55/69 | 43/66 | 45/67 | 56/65 | 68/65 | 61/71 |
| 60 °C 1 km ring | 54/69 | 33/66 | 28/67 | 26/65 | 22/65 | 20/71 |

Findings:
- **Small, very cold rings weaken the tornado ~30% while running, for ~1/7 of the power** of the ring that
  collapsed it (114–197 GW vs 1,031 GW). Per gigawatt this is about twice as effective as the 10 °C ring
  (−14% for 168 GW).
- **But the tornado recovers** within 10–20 minutes of the cooling stopping. Only the large 60 °C ring kept
  it down.
- **Colder beyond ~30 °C barely helps a small ring** (−26% → −30% from 30 to 100 °C). So the earlier idea
  that the inflow just has to be colder than the storm can lift (~26 °C here) is incomplete: the cold air
  also has to cover a large enough area, or last long enough, to keep undercutting the tornado. The large
  ring builds a big, persistent pool of cold air; small rings make little cold air that is soon mixed away.
- Even the cheapest effective case (tiny ring, 114 GW) is roughly a quarter of the average output of all US
  power plants, continuously, at ground level within 300 m of the tornado.
- 60–100 °C of cooling is far outside the model's Boussinesq approximation; those runs are qualitative.

### Small rings cooled for 30 minutes (2026-10-10)

The 10-minute small-ring runs weakened the tornado ~30% but it recovered once cooling stopped. Here the same
rings stay on for 30 minutes; 45 minutes simulated. Power is the average over the 30 minutes of cooling
(it falls over time because a weaker tornado draws in less warm air to cool).

| Run | Avg power | Energy (kt TNT) | 0–10 min | 10–30 min | 30–45 min (off) | Last 5 min |
|---|---|---|---|---|---|---|
| small ring, 30 °C | 97 GW | 42 | **−26%** | **−48%** | **−36%** | −27% ~ |
| small ring, 100 °C | 129 GW | 56 | **−30%** | **−43%** | **−55%** | **−53%** |
| tiny ring, 60 °C | 94 GW | 40 | **−27%** | **−42%** | **−31%** | −28% ~ |
| 1 km ring, 60 °C, 10 min (from above) | 1,031 GW | 148 | −36% | −64% | — | −72% |

Noise floor (2σ): ±20% (0–10 min), ±14% (10–30), ±16% (30–45), ±28% (last 5).

5-minute mean peak wind, run / control (m/s):

| Run | 0–5 | 5–10 | 10–15 | 15–20 | 20–25 | 25–30 | 30–35 | 35–40 | 40–45 |
|---|---|---|---|---|---|---|---|---|---|
| small, 30 °C | 59/69 | 41/66 | 35/67 | 37/65 | 37/65 | 31/71 | 36/68 | 45/69 | 51/69 |
| small, 100 °C | 53/69 | 42/66 | 39/67 | 40/65 | 38/65 | 36/71 | 32/68 | 30/69 | 32/69 |
| tiny, 60 °C | 55/69 | 43/66 | 38/67 | 40/65 | 40/65 | 39/71 | 42/68 | 50/69 | 50/69 |

Findings:
- **Keeping the cooling on keeps the tornado's swirl down**: roughly 35–40 m/s against 65–71 m/s for the
  control. (Correction: total near-ground wind fell much less, e.g. 47.6 vs 64.6 m/s for the 30 °C ring
  over minutes 10–30, because of cold-air outflow; see "Surface winds and efficiency" below.)
- **For about 1/8 of the power** of the 1 km 60 °C ring (94–129 GW vs 1,031 GW), and about a third of its
  total energy. The large ring still goes further (down to ~20 m/s).
- **After the cooling stops**, the 30 °C small ring and the tiny ring start recovering within ~10 minutes.
  The 100 °C small ring stays down (~30 m/s) for the 15 minutes observed.
- Caveats as before: 30–100 °C of cooling is far beyond natural cold pools and outside the model's
  Boussinesq approximation (qualitative only), and these are single runs from one tornado. ~100 GW is still
  about a fifth of the average output of all US power plants, delivered continuously at ground level
  within ~500 m of a tornado.

### How cold must a small ring be to push the tornado below EF0? (2026-10-10)

> **Correction (later the same day).** This section measured the tornado's *swirl* (peak tangential wind,
> z ≤ 500 m). The total horizontal wind near the ground (z ≤ 100 m) tells a different story for small rings:
> the 110 °C and 125 °C runs still had **~60 m/s surface winds** (control: 67 m/s), because the very cold,
> dense air rushes outward along the ground like a downburst. So the small rings traded the tornado's spin
> for a cold-air blast and did **not** bring damaging winds below EF0. See "Surface winds and efficiency"
> below.

**Target.** "Completely disrupted" is taken as the mean peak wind (z ≤ 500 m) over minutes 30–45 falling
below the EF0 threshold, 29 m/s. The control averages 68.8 m/s in that window, so the target is a
**57.9% reduction**.

**Prediction.** Fitting the two earlier small-ring runs (30 °C → 36.3%, 100 °C → 54.6%) gives 112 °C
(linear) to 124 °C (logarithmic).

**Test.** Small ring (r = 500 m, ~500 m wide, 125 m deep), cooling on for 30 minutes, 45 minutes simulated:

| Cooling | Avg power | Energy (kt TNT) | Mean peak wind, 30–45 min | Reduction | Below EF0? | 5-min means 0→45 min (m/s) |
|---|---|---|---|---|---|---|
| 30 °C | 97 GW | 42 | 43.9 m/s | 36.3% | no | 59 41 35 37 37 31 36 45 51 |
| 100 °C | 129 GW | 56 | 31.2 m/s | 54.6% | no (just above) | 53 42 39 40 38 36 32 30 32 |
| **110 °C** | **114 GW** | **49** | **26.0 m/s** | **62.2%** | **yes** | 53 43 39 36 36 31 26 26 26 |
| **125 °C** | **149 GW** | **64** | **27.0 m/s** | **60.7%** | **yes** | 52 44 40 40 39 32 28 26 28 |
| 150 °C | 176 GW | 76 | 30.1 m/s | 56.2% | no (just above) | 52 44 41 38 35 34 33 31 27 |

Control: 68.8 m/s; noise floor (2σ) for this window ±16%. Central pressure drop over minutes 30–45: 18–19 hPa
for the 110–150 °C runs vs 46 hPa for the control.

Findings:
- **The prediction held:** both runs inside the predicted 112–124 °C range (110 and 125 °C) brought the
  tornado below EF0 for the whole 30–45 minute window.
- **But the effect saturates.** From 100 °C upward the result sits at 26–31 m/s regardless of temperature
  (150 °C ended slightly above the line). The small ring's effect levels off right around the EF0
  threshold, so whether it lands just below or just above is within run-to-run variation. Colder does not
  push further; a larger cold region does (the 1 km 60 °C ring reached ~20 m/s).
- **"Below EF0" is not "gone".** A weak vortex remains (26–31 m/s, ~19 hPa pressure drop).
- **Cost:** ~110–150 GW for 30 minutes (~50–65 kt TNT of heat removed), at ground level within ~750 m of
  the tornado, using air cooled to roughly −85 to −100 °C. This is far beyond natural cold pools and
  outside the model's Boussinesq approximation, so the numbers are qualitative.

### Surface winds and efficiency (2026-10-10)

What damages buildings is the total horizontal wind near the ground, not only the swirl. Comparing both, and
the total cooling each setup needs, expressed as liquid air (≈0.31 MJ absorbed per kg as it boils and warms
to about −85 °C):

| Setup | Window | Swirl z ≤ 500 m | **Surface wind z ≤ 100 m** | Total cooling | Liquid air |
|---|---|---|---|---|---|
| Control | 10–30 / 30–45 min | 67 / 69 m/s | 65 / 67 m/s | — | — |
| Small ring 110 °C, 30 min | 30–45 min | 26.0 | **59.5** ✗ | 205 TJ | 0.66 Mt |
| Small ring 110 °C, **15 min** | 30–45 min | 43.0 | 59.3 ✗ | 146 TJ | 0.47 Mt |
| Disk under the tornado, 40 °C, 30 min | 10–30 min | 33.1 | 48.5 ✗ | 188 TJ | 0.61 Mt |
| **1 km ring, 60 °C, 10 min** | 10–30 min | 24.0 | **25.5** ✓ | 618 TJ | 2.0 Mt |
| **Mid-altitude (600 m) ring, 60 °C, 30 min** | 30–45 min | 27.4 | **21.1** ✓ | 1,182 TJ | 3.8 Mt |
| Mid-altitude (600 m) ring, 110 °C, 30 min | 30–45 min | 34.9 | 20.6 | 3,267 TJ | 10.5 Mt |

(✓ = surface wind below the EF0 threshold, 29 m/s.)

- **Cold released at the ground next to the tornado creates a downburst.** Small rings and the cold disk
  cut the swirl but leave ~50–60 m/s winds at the surface.
- **Two setups bring mean surface winds below EF0:** the large 1 km ring (cold spread over a wide area) and cold
  injected ~600 m up (it spreads and mixes before reaching the ground). The mid-altitude version gives the
  lowest surface winds and keeps the coldest air away from people.
- **Least cold that works so far: ~2 million tonnes of liquid air** (1 km ring, 10 min). Mid-altitude costs
  about twice that. Shorter bursts and milder temperatures over the wide ring have not been tried yet.
- Colder is not better at mid-altitude: 110 °C needed ~3× the cooling of 60 °C and did no better, because
  colder air sinks out of the injection zone faster and has to be replaced.
- These are single runs at temperatures outside the model's Boussinesq approximation; treat as qualitative.

#### Round 2: using less cold (2026-10-10)

| Setup | Liquid air | Surface wind 10–30 min | Surface wind 30–45 min | Surface-wind 5-min means 0→45 (m/s) |
|---|---|---|---|---|
| **Mid-altitude (600 m) ring, 60 °C, 15 min** | **2.26 Mt** | 30.1 | **18.3** ✓ | 58 46 39 34 25 22 19 14 22 |
| Mid-altitude ring, 60 °C, 30 min (round 1) | 3.81 Mt | 37.1 | 21.1 ✓ | 58 46 39 38 40 32 24 20 19 |
| 1 km ring, 60 °C, 10 min (round 1) | 2.00 Mt | 25.5 ✓ | — | 44 31 32 25 26 19 |
| 1 km ring, 60 °C, 5 min | 1.59 Mt | 31.5 | 39.2 ✗ | 44 32 34 28 34 30 37 38 42 |
| Mid-altitude ring, 30 °C, 30 min | 1.67 Mt | 41.4 | 46.1 ✗ | 57 42 40 40 42 44 48 47 44 |
| 1 km ring, 30 °C, 10 min | 0.87 Mt | 44.9 | 51.4 ✗ | 49 39 40 45 46 49 50 51 53 |

Control surface wind: 64.6 (10–30 min), 66.9 (30–45 min). Noise floor (2σ) for surface wind: ±12% and ±14%.

- **Best so far: cold injected ~600 m up, 60 °C, for 15 minutes.** Five-minute mean surface winds are 14–22 m/s from minute
  20 to 45, with the coldest air kept aloft. It needs 40% less cold than running it for 30 minutes.
- **About 60 °C is needed**: 30 °C failed at both the ground and mid-altitude. The threshold lies between them.
- **About 2 million tonnes of liquid air is the minimum found** for mean surface winds below EF0. Shorter or milder
  versions let the tornado recover.

### Could aircraft deliver it? (2026-10-13)

Idea: AI-guided heavy aircraft that hold assigned positions relative to the moving tornado and release liquid
air there. Tracking is a good fit for automation, but carrying capacity is the limit. The best setup above needs
2.26 Mt in 15 minutes (~2,500 t/s). The largest cargo aircraft carry ~130 t, so that is ~17,000 loads (~19
releases per second), and **all ~2,000 large cargo aircraft in the world carry ~0.2 Mt in one sortie**. The
injection point (600 m up, 500 m from the tornado) is also inside the storm, where shear, hail and downbursts
endanger aircraft. So three tests asked whether a fleet-sized dose could work, or whether aircraft could stay
outside the storm:

1. **Early:** cool before the tornado forms (from the same spin-up at t = 120 s, swirl 17.5 m/s;
   compared with a control from that same moment).
2. **Upwind:** release in a ring 2–3 km out, outside the storm core, so the storm's inflow carries the cold in.
3. **Milder:** the mid-altitude ring at 45 °C instead of 60 °C.

| Setup | Liquid air (× fleet sortie) | Surface wind 10–30 min | Surface wind 30–45 min | Swirl 30–45 | Below EF0 | Surface-wind 5-min means 0→45 (m/s) |
|---|---|---|---|---|---|---|
| Control from early state | — | 62.8 | 63.1 | 65.3 | ✗ | 46 61 66 61 60 64 60 65 64 |
| Early: 1 km ring, 10 °C, 10 min | 0.38 Mt (1.9×) | 45.8 (−27%) | 59.9 (−5%) | 64.1 | ✗ | 42 48 38 44 50 51 54 64 62 |
| Early: 1 km ring, 30 °C, 5 min | 0.42 Mt (2.1×) | 37.4 (−41%) | 60.8 (−4%) | 64.3 | ✗ | 36 31 23 34 41 51 62 58 62 |
| Early: 600 m up, 30 °C, 10 min | 0.39 Mt (1.9×) | 42.7 (−32%) | 62.2 (−1%) | 65.7 | ✗ | 42 48 34 37 46 53 57 65 64 |
| Control (mature) | — | 64.6 | 66.9 | 68.8 | ✗ | 65 62 65 64 63 67 63 69 68 |
| **Upwind: 2.5 km ring, 30 °C, 15 min** | **2.90 Mt (14.5×)** | **23.1 (−64%)** | **24.4 (−64%)** | 27.9 | **✓** | 64 43 36 26 18 13 24 19 30 |
| Upwind: 2.5 km ring, 10 °C, 15 min | 2.43 Mt (12.1×) | 43.3 (−33%) | 42.0 (−37%) | 44.2 | ✗ | 66 59 47 44 43 40 41 45 40 |
| Mid-altitude, 45 °C, 15 min | 1.63 Mt (8.1×) | 36.4 (−44%) | 37.5 (−44%) | 25.8 | ✗ | 57 45 39 39 37 31 31 40 42 |
| Mid-altitude, 60 °C, 15 min (eff H) | 2.26 Mt (11.3×) | 30.1 (−53%) | 18.3 (−73%) | 21.9 | ✓ after 20 min | 58 46 39 34 25 22 19 14 22 |

Noise floor (2σ) for surface wind: ±12–14%. Scored with `python -m aeolus_axisym.plane_report results/axisym`.

- **Striking before the tornado forms only delays it.** All three early doses (~0.4 Mt) held surface winds to
  23–50 m/s while cooling, then the parent storm rebuilt a full-strength tornado within ~15 minutes. The storm,
  not the tornado, is the engine; as long as its warm inflow returns, so does the tornado.
- **The upwind ring lowers mean surface winds outside the modeled vortex core.** Cooling a ring 2–3 km out by 30 °C brought
  mean surface winds below 29 m/s over minutes 15–30 and 30–45, with excursions above that threshold
  (pressure drop 4.7 hPa vs 46 in the control over 30–45 min). This model does not establish aircraft flight safety.
  It needs ~2.9 Mt, ~30% more than the mid-altitude ring, but at a milder temperature, at ground level far from
  the vortex, and in calmer air. By minute 40–45 the surface wind is creeping back up (30 m/s), so a longer or
  repeated release would be needed to hold it down.
- **45 °C at mid-altitude is not enough**: it halves the wind (~37 m/s) but stays EF1. The threshold there is
  between 45 and 60 °C.
- **Aircraft delivery is still ~11–15× short.** No dose within one sortie of the world's cargo fleet (~0.2 Mt)
  kept the tornado below EF0. The upwind result means the delivery problem is now "ground-level release over
  a wide area outside the storm", which suits fixed ground infrastructure or many low-flying aircraft better
  than precision strikes near the vortex.
- Caveats: the model is axisymmetric, so "upwind" here is a full ring; a real release would cover only the
  inflow sector (less material, but untested). The outer edge of the 2.5 km ring approaches the model's
  far-field sponge (3.2 km). Single runs, qualitative.

Reproduce the early state with
`python -m aeolus_axisym.experiment spinup --out results/axisym/m35_early --t-end 120 --set '{"M_inf": 35000.0}'`,
then run the control and the `early:` versions with `--out results/axisym/m35_early --t-obs 2700`.

### Recovery audit: averages versus sustained suppression (2026-10-13)

Reanalysis of the existing saved histories, **not new simulation runs**, using
`aeolus_axisym.recovery_report`. The earlier “below EF0” check compared window means; a mean below
29 m/s does not imply that the wind stayed below it. The report now integrates means and time below
the threshold using linear interpolation between 5-second diagnostic samples, with matched control
windows. Excursions between samples remain unresolved; these model winds are not measured EF ratings.

| Setup | Window | Mean surface wind (control) | Maximum sample | Time below 29 m/s | Liquid-air equivalent |
|---|---|---|---|---|---|
| 1 km ring, 60 °C, 10 min | 15–30 min | 23.4 (64.4) m/s | 36.0 m/s | 81.4% | 2.00 Mt |
| Mid-altitude, 60 °C, 15 min | 30–45 min | 18.3 (66.9) m/s | 28.6 m/s | 100% | 2.26 Mt |
| Upwind ring, 30 °C, 15 min | 30–45 min | 24.4 (66.9) m/s | 37.8 m/s | 73.1% | 2.90 Mt |

The existing control-variability estimate gives a ±14.4% noise floor for these 15-minute mean
comparisons; all three mean reductions exceed it. This does not replace uncertainty from repeated runs.
After cooling stops, the longest uninterrupted interval below 29 m/s is 7.8 minutes for the 1 km ring,
19.9 minutes for the mid-altitude setup, and 14.4 minutes for the upwind ring. The mid-altitude interval
extends to the end of the recording, so its eventual duration is unknown. All three end below the
threshold, but **none establishes permanent suppression**: the 1 km recording ends at 30 minutes and
the other two at 45 minutes. The next experiment should extend all three and their matched control
to the same longer observation period, then repeat from different initial storm phases.

Full tables and reproduction command: [recovery report](docs/axisym/recovery/recovery_report.md) and
[chart index](docs/axisym/README.md). The JSON export includes each below-threshold interval for review.

### Leaving the mid-altitude cooling on: `sustained: mid-level 60 K`

Same geometry as the mid-altitude (600 m) ring at 60 °C, but cooling stays on for the whole 50-minute run
instead of 15 minutes. One run, compared with the same control.

| Setup | Liquid air | Window (min) | Mean surface wind (control) | Maximum sample | Time below 29 m/s |
|---|---|---|---|---|---|
| 15 minutes | 2.26 Mt | 15–30 | 27.1 (64.4) m/s | 44.4 m/s | 66.0% |
| Sustained | 4.48 Mt by 50 min | 15–30 | 36.4 (64.4) m/s | 45.5 m/s | 10.7% |
| 15 minutes | 2.26 Mt | 30–45 | 18.3 (66.9) m/s | 28.6 m/s | 100% |
| Sustained | 4.48 Mt by 50 min | 30–45 | 21.7 (66.9) m/s | 36.0 m/s | 87.5% |

Five-minute mean surface winds for the sustained run, 0→50 min (m/s, time-weighted): 57 46 39 38 40 32 25 24
16 22.

- **Leaving the cooling on did no better**, although it used about twice as much cold. Its means over minutes
  15–30 and 30–45 were higher than the 15-minute version's. The 30–45 difference (about 5% of the control
  mean) is well within the ±14% noise floor, and the 15–30 difference (about 14%) is about the size of it, so
  this does not show that longer cooling is worse.
- **It held every sample below 29 m/s only late in the run:** over minutes 45–50 all samples were below it
  (mean 21.9 m/s, maximum 25.8 m/s), but 36.0 m/s occurred during minutes 30–45.
- **This does not answer the recovery question.** Cooling never stops in this run, and the 15-minute run ends
  at 45 minutes. Whether the tornado returns after that is untested.

Reproduce the comparison from the saved runs:

```bash
python -m aeolus_axisym.recovery_report results/axisym/m35 \
  --version 'sustained: mid-level 60 K' --version 'eff H: mid-level 60 K 15 min' --dest results/axisym/sustained
```

To rerun the simulation itself:

```bash
python -m aeolus_axisym.experiment run --out results/axisym/m35 --version 'sustained: mid-level 60 K' --t-obs 3000
```

### 3D check (2026-11)

Attempts to reproduce a tornado in the 3D model CM1 have not produced one, so no intervention has been tested in
3D. See [`cm1_colab/README.md`](cm1_colab/README.md).
