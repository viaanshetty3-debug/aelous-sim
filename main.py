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

    print(f"Initializing Aeolus vortex solver...")
    print(f"  Grid: {args.grid_size}³")
    print(f"  Domain: r=[100, 2000]m, z=[0, 3000]m")
    print(f"  Time step: {args.dt} s")
    print(f"  Interventions: {args.intervention}")
    print()

    # Initialize grid
    grid = CylindricalGrid(nx=args.grid_size, ntheta=args.grid_size, nz=args.grid_size)

    # Initialize Rankine vortex baseline
    rankine = RankineVortex(
        grid=grid,
        core_radius=args.core_radius,
        max_velocity=args.max_velocity,
    )
    u_r, u_theta, u_z, p = rankine.initialize()

    # Compute baseline vorticity for diagnostics
    baseline_vorticity = rankine.compute_core_vorticity(u_theta)
    print(f"Baseline core vorticity: {baseline_vorticity:.3f} 1/s")
    print()

    # Set up solver
    solver = NavierStokesSolver(grid=grid, dt=args.dt)

    # Set up interventions
    interventions = []
    if args.intervention in ("thermal", "both"):
        interventions.append(ThermalRFDIntervention(grid=grid))
    if args.intervention in ("momentum", "both"):
        interventions.append(MomentumSinkIntervention(grid=grid))

    # Set up diagnostics and output
    diagnostics = Diagnostics(grid=grid, baseline_vorticity=baseline_vorticity)
    output = OutputManager(output_dir=args.output)

    print("Step     Core Vorticity    Max Velocity    Kinetic Energy    Reduction")
    print("-" * 72)

    # Time stepping loop
    for step in range(args.n_steps):
        # Apply interventions
        for intervention in interventions:
            u_r, u_theta, u_z, p = intervention.apply(u_r, u_theta, u_z, p, step=step)

        # Solve Navier-Stokes
        u_r, u_theta, u_z, p = solver.step(u_r, u_theta, u_z, p)

        # Measure diagnostics
        metrics = diagnostics.compute(u_r, u_theta, u_z, p, step=step)

        # Save checkpoint
        output.checkpoint(step, u_r, u_theta, u_z, p, metrics)

        if step % 10 == 0:
            diagnostics.print_summary(step)

    # Final summary
    summary = output.summarize(diagnostics, grid)

    print("-" * 72)
    print(f"\nSimulation complete!")
    print(f"Output directory: {args.output}")
    print(f"Summary: {args.output / 'summary.txt'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
