"""Score intervention runs against a no-intervention control run.

Usage:
    python analysis/score_vs_control.py results/fixed/control results/fixed/v7 results/fixed/both_high ...

The first directory is the control. For each run it reports:
  * sustained reduction: |ω_core| at the final step vs the control's |ω_core| at the same step.
    This is the intervention's own effect; natural decay of the vortex is cancelled out.
  * final kinetic energy split into spin (u_θ), inflow (u_r) and vertical (u_z),
    from the last saved checkpoint, so spurious vertical motion can't hide in the total.
"""

import glob
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from grid import CylindricalGrid  # noqa: E402

RHO = 1.225


def final_core_vorticity(run_dir):
    with open(Path(run_dir) / "summary.json") as f:
        return abs(json.load(f)["time_series"]["core_vorticity"][-1])


def ke_split(run_dir):
    checkpoints = sorted(glob.glob(str(Path(run_dir) / "checkpoint_*.h5")))
    if not checkpoints:
        return None
    import h5py

    with h5py.File(checkpoints[-1]) as h:
        fields = {k: h[k][()] for k in ("u_r", "u_theta", "u_z")}
    nx, ntheta, nz = fields["u_r"].shape
    grid = CylindricalGrid(nx=nx, ntheta=ntheta, nz=nz)
    dV = np.zeros(nx)
    dV[: len(grid.dr)] = grid.r_c * grid.dr * grid.dtheta * grid.dz
    dV = dV[:, None, None]
    return {k: 0.5 * RHO * np.sum(v ** 2 * dV) / 1e9 for k, v in fields.items()}


def main(control_dir, *run_dirs):
    omega_control = final_core_vorticity(control_dir)
    print(f"{'run':<16}{'|ω| final':>10}{'vs control':>12}{'KE spin':>10}{'KE inflow':>11}{'KE vert':>10}  (KE ×10⁹ J)")
    for run in (control_dir, *run_dirs):
        omega = final_core_vorticity(run)
        reduction = (omega_control - omega) / omega_control * 100.0
        ke = ke_split(run) or {"u_theta": float("nan"), "u_r": float("nan"), "u_z": float("nan")}
        print(f"{Path(run).name:<16}{omega:>10.4f}{reduction:>+11.1f}%"
              f"{ke['u_theta']:>10.0f}{ke['u_r']:>11.0f}{ke['u_z']:>10.0f}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(*sys.argv[1:])
