# Axisymmetric model: charts and videos

Generated from `results/axisym/m35` (the raw runs are git-ignored; regenerate with the commands in
[`AXISYM_RESULTS.md`](../../AXISYM_RESULTS.md)).

- [`timeseries.png`](timeseries.png): peak wind and central pressure drop for every v1–v7 / RW80 run vs the
  no-intervention control over 50 simulated minutes.
- [`results_table.md`](results_table.md): full per-metric table for v1–v7 and RW80.
- [`fan_results.md`](fan_results.md): the outward-fan sweep.

## Videos

Each video compares one intervention (bottom row) with the untouched tornado (top row) over the first 10
simulated minutes. 1 s of video = 30 s of simulation. Left: vertical slice through the tornado's centre
(the dark column in the middle is the calm core; the bright bands either side are the spinning walls).
Right: top-down view ~50 m above the ground. Colours are horizontal wind speed with EF-scale bands.

- [`videos/v6_momentum-only__60s_vs_control.mp4`](videos/v6_momentum-only__60s_vs_control.mp4): −500 Pa suction for 60 s
- [`videos/RW80_vs_control.mp4`](videos/RW80_vs_control.mp4): the realworld_test "80%" configuration
- [`videos/v7__60s_vs_control.mp4`](videos/v7__60s_vs_control.mp4): v7 with 60 s injection
