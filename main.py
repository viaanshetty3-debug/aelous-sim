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
    parser.add_argument("--stable-grid-override", action="store_true",
                        help="Force 48³ grid for long-duration runs (>100 steps) to ensure stability")
    parser.add_argument("--cfl-target", type=float, default=0.7,
                        help="Target Courant number for adaptive time stepping (default 0.7)")
    parser.add_argument("--divergence-limit", type=float, default=0.05,
                        help="Divergence RMS threshold for incompressibility correction (default 0.05)")
    args = parser.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)

    # GRID SCALING OVERRIDE: Use stable 48³ for long-duration runs
    if args.stable_grid_override or args.n_steps > 100:
        if args.grid_size > 48:
            original_grid = args.grid_size
            args.grid_size = 48
            logging.info(f"Grid scaling override: {original_grid}³ → 48³ for long-duration stability")
            print(f"[STABILITY] Overriding grid to 48³ (from {original_grid}³) for {args.n_steps}-step run")

    print(f"Initializing Aeolus vortex solver (High-Fidelity Mode)...")
    print(f"  Grid: {args.grid_size}³")
    print(f"  Domain: r=[100, 2000]m, z=[0, 3000]m")
    print(f"  Time step: {args.dt} s (adaptive CFL limiter enabled)")
    print(f"  Physics: Wind Shear + LHR + Precip Drag")
    print(f"  Initialization: {args.initialization}")
    print(f"  Interventions: {args.intervention}")
    print(f"  Stability: CFL target={args.cfl_target}, Divergence limit={args.divergence_limit}")
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
    # Includes adaptive time stepping and divergence correction
    solver = NavierStokesSolver(
        grid=grid, dt=args.dt, enable_shear=True,
        enable_lhr=True, enable_precip=True,
        enable_adaptive_dt=True, cfl_target=args.cfl_target,
        divergence_limit=args.divergence_limit
    )

    # Set up interventions with reduced thresholds (test minimum viable)
    interventions = []
    if args.intervention in ("thermal", "both"):
        # Minimal thermal RFD: 0.5K buoyancy (minimal energy injection)
        interventions.append(ThermalRFDIntervention(
            grid=grid,
            peak_anomaly=0.5,  # Minimal: 0.5K (from 2K, reduced 75%)
            active_duration_steps=50,  # 50 steps full strength
            decay_duration_steps=40,  # 40 steps decay
        ))
    if args.intervention in ("momentum", "both"):
        # Minimal momentum sink: -50 Pa (light pressure deficit)
        interventions.append(MomentumSinkIntervention(
            grid=grid,
            pressure_deficit=-50.0,  # Minimal: -50 Pa (from -250 Pa, reduced 80%)
            active_duration_steps=50,  # Match thermal RFD
            decay_duration_steps=40,   # Match thermal RFD decay
        ))

    # Set up diagnostics and output
    diagnostics = Diagnostics(grid=grid, baseline_vorticity=baseline_vorticity)
    output = OutputManager(output_dir=args.output)

    print("Step     Core Vorticity    Max Velocity    Kinetic Energy    Reduction    Div.RMS    dt")
    print("-" * 95)

    # Time stepping loop
    for step in range(args.n_steps):
        # Apply interventions
        for intervention in interventions:
            u_r, u_theta, u_z, p = intervention.apply(u_r, u_theta, u_z, p, step=step)

        # Solve Navier-Stokes (includes adaptive CFL and divergence correction)
        u_r, u_theta, u_z, p = solver.step(u_r, u_theta, u_z, p)

        # Measure diagnostics
        metrics = diagnostics.compute(u_r, u_theta, u_z, p, step=step)
        metrics['divergence_rms'] = solver.last_divergence_rms
        metrics['dt_current'] = solver.dt

        # Save checkpoint
        output.checkpoint(step, u_r, u_theta, u_z, p, metrics)

        if step % 10 == 0:
            diagnostics.print_summary(step)
            # Print stability metrics
            div_status = "✓" if solver.last_divergence_rms < args.divergence_limit else "⚠"
            print(f"  [{div_status}] Divergence RMS: {solver.last_divergence_rms:.2e} | dt={solver.dt:.4f}s | CFL adjustments: {solver.dt_reduction_count}")

    # Final summary
    summary = output.summarize(diagnostics, grid)

    print("-" * 72)
    print(f"\nSimulation complete!")
    print(f"Output directory: {args.output}")
    print(f"Summary: {args.output / 'summary.txt'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
