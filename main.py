"""Entry point for Aeolus vortex disruption simulation."""

import argparse
import sys
from pathlib import Path

from grid import CylindricalGrid
from baseline import RankineVortex
from solver import NavierStokesSolver
from interventions import ThermalRFDIntervention, MomentumSinkIntervention
from diagnostics import Diagnostics
from output import OutputManager


def main():
    parser = argparse.ArgumentParser(description="3D incompressible Navier-Stokes vortex solver")
    parser.add_argument("--intervention", choices=["none", "thermal", "momentum", "both"], default="both")
    parser.add_argument("--output", type=Path, default=Path("results/both"))
    parser.add_argument("--core-radius", type=float, default=500.0)
    parser.add_argument("--max-velocity", type=float, default=90.0)
    parser.add_argument("--grid-size", type=int, default=64)
    parser.add_argument("--dt", type=float, default=0.1)
    parser.add_argument("--n-steps", type=int, default=100)
    args = parser.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)

    # Initialize grid
    grid = CylindricalGrid(nx=args.grid_size, ntheta=args.grid_size, nz=args.grid_size)

    # Initialize Rankine vortex baseline
    rankine = RankineVortex(
        grid=grid,
        core_radius=args.core_radius,
        max_velocity=args.max_velocity,
    )
    u, v, w, p = rankine.initialize()

    # Set up solver
    solver = NavierStokesSolver(grid=grid, dt=args.dt)

    # Set up interventions
    interventions = []
    if args.intervention in ("thermal", "both"):
        interventions.append(ThermalRFDIntervention(grid=grid))
    if args.intervention in ("momentum", "both"):
        interventions.append(MomentumSinkIntervention(grid=grid))

    # Set up diagnostics and output
    diagnostics = Diagnostics(grid=grid)
    output = OutputManager(output_dir=args.output)

    # Time stepping loop
    for step in range(args.n_steps):
        # Apply interventions
        for intervention in interventions:
            u, v, w, p = intervention.apply(u, v, w, p, step=step)

        # Solve Navier-Stokes
        u, v, w, p = solver.step(u, v, w, p)

        # Measure diagnostics
        metrics = diagnostics.compute(u, v, w, p, step=step)

        # Save checkpoint
        output.checkpoint(step, u, v, w, p, metrics)

        if step % 10 == 0:
            print(f"Step {step}/{args.n_steps} | Vorticity: {metrics['core_vorticity']:.2f} s^-1")

    # Final summary
    summary = output.summarize(diagnostics)
    print(f"\nSimulation complete. Summary saved to {args.output / 'summary.txt'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
