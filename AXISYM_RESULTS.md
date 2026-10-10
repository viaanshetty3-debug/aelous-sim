# AEOLUS interventions v1–v7 and RW80 in a verified tornado model

Date: 2026-10-09. Model: `aeolus_axisym/` (replaces the results produced with `solver.py`).
Raw data: `results/axisym/m35/` (git-ignored). Charts, tables and videos: [`docs/axisym/`](docs/axisym/README.md). Regenerate with the commands at the end.

## Bottom line

**No version of the AEOLUS intervention weakens the tornado by more than chance, in any time window.**

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

### Verification (tests/test_axisym_model.py, 8 tests, all pass)

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
   tornado within minutes. Nothing suppresses the tornado over 50 minutes.

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

- **Axisymmetric.** No 3D effects: no multiple-vortex structure, no asymmetric breakdown, no storm motion.
  Real tornadoes shed energy through 3D instabilities; this model cannot, so its brief pulses spike to
  unrealistic 150–250 m/s. Averages are realistic; single moments are not.
- **Fixed parent storm.** The supercell updraft is a prescribed force. The interventions cannot weaken the
  parent storm. (In reality nothing a device could deliver would come close to doing so either.)
- **Constant eddy viscosity**, no moisture, rain or cloud physics, no surface roughness variation.
- **One tornado, one resolution.** All runs use the same 25 m grid and the same mature tornado. A finer
  grid (12.5 m) or a different storm could shift numbers by several percent, but is very unlikely to turn
  +30% strengthening into weakening.
- **Device actions taken literally** from the code. A differently placed or differently designed device
  was not tested.

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
