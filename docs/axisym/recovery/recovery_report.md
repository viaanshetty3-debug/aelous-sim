# Cooling suppression and recovery

Surface wind is the model's peak horizontal wind at z ≤ 100 m. The 29 m/s threshold
is a comparison marker, not an observed EF rating. Means and threshold durations are
time-weighted using linear interpolation between saved samples; shorter excursions may be missed.
All windows use the same time span in the intervention and control. '~' means the change
is within the existing control-variability 2σ estimate; this is not uncertainty from repeated runs.

| Setup | Window (min) | Mean (control), m/s | Change | 2σ noise | Maximum, m/s | Time below 29 m/s | Longest interval below (min) |
|---|---|---|---|---|---|---|---|
| cool 60 K | 0–15 | 35.7 (64.0) | -44.2% | ±14.4% | 84.5 | 19.0% | 1.9 |
| cool 60 K | 15–30 | 23.4 (64.4) | -63.7% | ±14.4% | 36.0 | 81.4% | 7.8 |
| eff H: mid-level 60 K 15 min | 0–15 | 47.3 (64.0) | -26.0% | ±14.4% | 92.3 | 0.0% | 0.0 |
| eff H: mid-level 60 K 15 min | 15–30 | 27.1 (64.4) | -58.0% | ±14.4% | 44.4 | 66.0% | 4.9 |
| eff H: mid-level 60 K 15 min | 30–45 | 18.3 (66.9) | -72.7% | ±14.4% | 28.6 | 100.0% | 15.0 |
| upwind: 2.5km ring 30 K 15 min | 0–15 | 47.3 (64.0) | -26.0% | ±14.4% | 97.1 | 14.6% | 1.8 |
| upwind: 2.5km ring 30 K 15 min | 15–30 | 19.0 (64.4) | -70.6% | ±14.4% | 37.8 | 93.0% | 12.1 |
| upwind: 2.5km ring 30 K 15 min | 30–45 | 24.4 (66.9) | -63.5% | ±14.4% | 37.8 | 73.1% | 7.2 |

## Cooling cost and follow-up

- **cool 60 K**: 618.5 TJ, 2.00 Mt liquid-air equivalent; cooling stops at 10 min, observation ends at 30 min. During follow-up, 66.7% of time is below 29 m/s; the longest interval lasts 7.8 min. Wind is below the threshold at the final sample; later recovery is unknown.
- **eff H: mid-level 60 K 15 min**: 699.5 TJ, 2.26 Mt liquid-air equivalent; cooling stops at 15 min, observation ends at 45 min. During follow-up, 83.0% of time is below 29 m/s; the longest interval lasts 19.9 min. Wind is below the threshold at the final sample; later recovery is unknown.
- **upwind: 2.5km ring 30 K 15 min**: 898.2 TJ, 2.90 Mt liquid-air equivalent; cooling stops at 15 min, observation ends at 45 min. During follow-up, 83.0% of time is below 29 m/s; the longest interval lasts 14.4 min. Wind is below the threshold at the final sample; later recovery is unknown.

Liquid-air equivalent uses 0.31 MJ/kg, matching previous reports. These are single runs
in the axisymmetric Boussinesq model; strong cooling remains a qualitative experiment.
