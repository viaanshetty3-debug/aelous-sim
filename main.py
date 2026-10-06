"""Entry point for Aeolus vortex disruption simulation."""

import argparse
import sys
import logging
from pathlib import Path

from grid import CylindricalGrid
from baseline import RankineVortex, MeteorologicalVortex
from noaa_data_ingestion import NOAADataIngestion
from solver import NavierStokesSolver
from interventions import ThermalRFDIntervention, MomentumSinkIntervention
from diagnostics import Diagnostics
from output import OutputManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def main():
    parser = argparse.ArgumentParser(description="3D incompressible Navier-Stokes vortex solver with high-fidelity physics")
    parser.add_argument("--intervention", choices=["none", "thermal", "momentum", "both"], default="both")
    parser.add_argument("--initialization", choices=["rankine", "realworld", "hybrid"], default="rankine",
                        help="rankine=hardcoded Rankine vortex, realworld=NOAA data, hybrid=blend both")
    parser.add_argument("--output", type=Path, default=Path("results/hifi"))
    parser.add_argument("--core-radius", type=float, default=500.0)
    parser.add_argument("--max-velocity", type=float, default=90.0)
    parser.add_argument("--grid-size", type=int, default=96)
    parser.add_argument("--dt", type=float, default=0.05)
    parser.add_argument("--n-steps", type=int, default=120)
    args = parser.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)

    print(f"Initializing Aeolus vortex solver (High-Fidelity Mode)...")
    print(f"  Grid: {args.grid_size}³")
    print(f"  Domain: r=[100, 2000]m, z=[0, 3000]m")
    print(f"  Time step: {args.dt} s")
    print(f"  Physics: Wind Shear + LHR + Precip Drag")
    print(f"  Initialization: {args.initialization}")
    print(f"  Interventions: {args.intervention}")
    print()

    # Initialize grid
    grid = CylindricalGrid(nx=args.grid_size, ntheta=args.grid_size, nz=args.grid_size)

    # Initialize vortex from selected source
    if args.initialization == "rankine":
        print("Using pure Rankine vortex baseline...")
        vortex = RankineVortex(
            grid=grid,
            core_radius=args.core_radius,
            max_velocity=args.max_velocity,
            add_shear=True,
        )
    elif args.initialization in ("realworld", "hybrid"):
        print(f"Fetching real meteorological data from NOAA THREDDS ('{args.initialization}' mode)...")
        noaa = NOAADataIngestion()
        vortex_strength = 0.0 if args.initialization == "realworld" else 0.5
        vortex = MeteorologicalVortex(
            grid=grid,
            noaa_ingester=noaa,
            core_radius=args.core_radius,
            max_velocity=args.max_velocity,
            vortex_strength=vortex_strength,
        )
    else:
        raise ValueError(f"Unknown initialization: {args.initialization}")

    u_r, u_theta, u_z, p = vortex.initialize()

    # Compute baseline vorticity for diagnostics
    baseline_vorticity = vortex.compute_core_vorticity(u_theta)
    print(f"Baseline core vorticity: {baseline_vorticity:.3f} 1/s")
    print()

    # Set up solver with high-fidelity physics (wind shear, LHR, precipitation drag)
    solver = NavierStokesSolver(
        grid=grid, dt=args.dt, enable_shear=True,
        enable_lhr=True, enable_precip=True
    )

    # Set up interventions with reduced thresholds (test minimum viable)
    interventions = []
    if args.intervention in ("thermal", "both"):
        # Reduced thermal RFD to test minimum threshold
        interventions.append(ThermalRFDIntervention(
            grid=grid,
            peak_anomaly=2.0,  # Reduced to 2K (from 4K) - test minimum
            active_duration_steps=50,  # 50 steps full strength
            decay_duration_steps=40,  # 40 steps decay
        ))
    if args.intervention in ("momentum", "both"):
        interventions.append(MomentumSinkIntervention(
            grid=grid,
            pressure_deficit=-250.0  # Reduced from -500 Pa (test minimum)
        ))

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
