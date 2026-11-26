# 3D storm attempts with CM1 (no tornado yet)

The axisymmetric model cannot represent 3D features such as a rear-flank downdraft, so we tried to grow a
tornado in [CM1](https://github.com/NCAR/CM1) on Colab (8 vCPU, 125 m inner grid) to test cooling there.
**No run produced a tornado, so no cooling has been tested in 3D.** This says nothing for or against the
2D cooling results.

| Run | Setup | Simulated time | Peak surface vertical vorticity | Outcome |
|---|---|---|---|---|
| `t125` | grid following the storm (`do_adapt_move`) | crashed at 75 min | 0.014 s⁻¹ | Setup error: the storm left the fine grid |
| `tor125` | fixed grid, surface friction, 0–1 km SRH 341 m²/s² | 120 min | 0.017 s⁻¹ | No tornado |
| `tor16` | as `tor125`, 0–1 km SRH 491 m²/s² | 177 of 180 min (last backup) | 0.017 s⁻¹ | No tornado |

For reference, we looked for roughly 0.1 s⁻¹ or more together with a surface pressure drop. In `tor16`,
10 m wind peaked at 28 m/s, 1 km vorticity at 0.048 s⁻¹ and the lowest surface pressure was 991 hPa.
The `tor125` raw output was lost when the Colab VM was recycled; its numbers come from notes taken at the time.

## Scripts

- `mksnd.py`: writes the input sounding (reconstructed after the VM loss).
- `cm1run.py`: launches runs and prints diagnostics.
- `patch_aeo.py`: adds the cooling intervention to CM1's `solve1.F`; compiled during the first attempts but never applied in a run.
- `setup_tor16.sh`: builds CM1 on a fresh Colab VM, launches `tor16` and backs it up to Drive.

CM1 commit used for `tor16`: `a33cd28c206adb010995f3ffb65aada150d9b1b9`.
