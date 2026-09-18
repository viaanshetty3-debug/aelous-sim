#!/usr/bin/env python3
"""Enhanced interactive dashboard using prompt_toolkit (Termux-friendly)."""

import numpy as np
import threading
import time
from typing import List, Dict
from collections import deque

from grid import CylindricalGrid
from baseline import RankineVortex
from solver import NavierStokesSolver
from interventions import ThermalRFDIntervention, MomentumSinkIntervention
from diagnostics import Diagnostics


class EnhancedDashboard:
    """Real-time interactive dashboard for vortex solver control with live feedback."""

    def __init__(self, max_steps: int = 120, grid_size: int = 32):
        """Initialize dashboard."""
        # Grid & solver setup
        self.grid = CylindricalGrid(nx=grid_size, ntheta=grid_size, nz=grid_size)
        rankine = RankineVortex(grid=self.grid, core_radius=500, max_velocity=90, add_shear=True)
        self.u_r, self.u_theta, self.u_z, self.p = rankine.initialize()
        self.baseline_vorticity = rankine.compute_core_vorticity(self.u_theta)

        self.solver = NavierStokesSolver(
            grid=self.grid, dt=0.05,
            enable_shear=True, enable_lhr=True, enable_precip=True
        )
        self.diagnostics = Diagnostics(grid=self.grid, baseline_vorticity=self.baseline_vorticity)

        # Control state
        self.thermal_enabled = True
        self.momentum_pressure = -250.0  # Pa, range: -100 to -500
        self.step = 0
        self.max_steps = max_steps
        self.paused = False
        self.running = True

        # Metrics tracking
        self.vorticity_history = deque(maxlen=50)
        self.pressure_history = deque(maxlen=50)

        # Create initial interventions
        self._update_interventions()

    def _update_interventions(self):
        """Update intervention modules based on current settings."""
        self.interventions = []

        if self.thermal_enabled:
            self.interventions.append(
                ThermalRFDIntervention(
                    grid=self.grid,
                    peak_anomaly=2.0,
                    active_duration_steps=50,
                    decay_duration_steps=40,
                )
            )

        self.interventions.append(
            MomentumSinkIntervention(
                grid=self.grid,
                pressure_deficit=self.momentum_pressure
            )
        )

    def _step_simulation(self):
        """Execute one solver time step."""
        # Apply interventions
        for intervention in self.interventions:
            self.u_r, self.u_theta, self.u_z, self.p = intervention.apply(
                self.u_r, self.u_theta, self.u_z, self.p, step=self.step
            )

        # Solve Navier-Stokes
        self.u_r, self.u_theta, self.u_z, self.p = self.solver.step(
            self.u_r, self.u_theta, self.u_z, self.p
        )

        # Compute diagnostics
        metrics = self.diagnostics.compute(self.u_r, self.u_theta, self.u_z, self.p, step=self.step)
        self.vorticity_history.append(metrics["vorticity_reduction_pct"])
        self.pressure_history.append(self.momentum_pressure)

        self.step += 1

    def _draw_bar_chart(self, width: int = 60) -> str:
        """Generate ASCII bar chart of vorticity reduction."""
        if not self.vorticity_history:
            return "  [No data yet]\n"

        output = "\n  ╔═══ Core Vorticity Reduction (%) ═══╗\n"
        max_reduction = 150.0
        chart_height = min(8, len(self.vorticity_history))
        start_idx = max(0, len(self.vorticity_history) - chart_height)

        for i, idx in enumerate(range(start_idx, len(self.vorticity_history))):
            reduction = list(self.vorticity_history)[idx]
            bar_len = int((reduction / max_reduction) * width)
            bar_len = min(bar_len, width)
            bar = "█" * bar_len + "░" * (width - bar_len)
            output += f"  │ Step {self.step - chart_height + i:3d}: {reduction:6.1f}% │{bar}│\n"

        output += "  ╚" + "═" * (len(output.split('\n')[1]) - 5) + "╝\n"
        return output

    def _draw_metrics(self) -> str:
        """Generate current metrics display."""
        if self.step == 0:
            return "  [Simulation starting...]\n"

        metrics = self.diagnostics.history
        output = "\n  ╔═══ Live Metrics ═══╗\n"

        if metrics:
            vort = metrics.get("core_vorticity", [])[-1][1] if metrics.get("core_vorticity") else 0.0
            vel = metrics.get("max_velocity", [])[-1][1] if metrics.get("max_velocity") else 0.0
            ke = metrics.get("kinetic_energy", [])[-1][1] if metrics.get("kinetic_energy") else 0.0
            red = metrics.get("vorticity_reduction_pct", [])[-1][1] if metrics.get("vorticity_reduction_pct") else 0.0

            output += f"  │ Core Vorticity:      {vort:8.3f} 1/s      │\n"
            output += f"  │ Max Velocity:        {vel:8.3f} m/s      │\n"
            output += f"  │ Kinetic Energy:      {ke:10.1f} J        │\n"
            output += f"  │ Reduction:           {red:8.1f} %         │\n"

        output += "  ╚════════════════════╝\n"
        return output

    def _draw_controls(self) -> str:
        """Generate control panel display."""
        thermal_indicator = "✓ ON " if self.thermal_enabled else "✗ OFF"
        status_indicator = "⏸ PAUSED" if self.paused else "▶ RUNNING"

        output = "\n  ╔═══ Controls ═══╗\n"
        output += f"  │ [T] Thermal RFD:  {thermal_indicator}        │\n"
        output += f"  │ [+/-] Pressure:   {self.momentum_pressure:6.0f} Pa      │\n"
        output += f"  │ Status: {status_indicator}                │\n"
        output += "  ╚═════════════════╝\n"
        output += "\n  Keyboard:\n"
        output += "   T     - Toggle Thermal RFD\n"
        output += "   +/-   - Adjust pressure (-100 to -500 Pa)\n"
        output += "   Space - Pause/Resume\n"
        output += "   Q     - Quit\n"

        return output

    def display(self) -> str:
        """Generate full dashboard display."""
        output = "\n" + "=" * 75 + "\n"
        output += f"  AEOLUS Interactive Dashboard  │  Step {self.step}/{self.max_steps}\n"
        output += "=" * 75 + "\n"

        output += self._draw_bar_chart()
        output += self._draw_metrics()
        output += self._draw_controls()

        if self.step >= self.max_steps:
            output += "\n  ✓ Simulation complete.\n"

        return output

    def handle_input(self, key: str) -> bool:
        """Handle single keypress. Returns False to quit."""
        key_upper = key.upper()

        if key_upper == 'Q':
            return False
        elif key_upper == 'T':
            self.thermal_enabled = not self.thermal_enabled
            self._update_interventions()
            print(f"Thermal RFD toggled: {'ON' if self.thermal_enabled else 'OFF'}")
        elif key_upper in ['+', '=']:
            self.momentum_pressure = min(-100.0, self.momentum_pressure + 25.0)
            self._update_interventions()
            print(f"Pressure adjusted: {self.momentum_pressure:.0f} Pa")
        elif key_upper == '-' or key_upper == '_':
            self.momentum_pressure = max(-500.0, self.momentum_pressure - 25.0)
            self._update_interventions()
            print(f"Pressure adjusted: {self.momentum_pressure:.0f} Pa")
        elif key == ' ':
            self.paused = not self.paused
            print(f"Simulation {'paused' if self.paused else 'resumed'}")
        else:
            return True

        return True

    def run_interactive(self):
        """Run dashboard with interactive control."""
        print("\n" + "=" * 75)
        print("  AEOLUS INTERACTIVE DASHBOARD")
        print("=" * 75)
        print("\nStarting simulation...")
        print("Press keys to control (T, +/-, Space, Q)")
        print("\nSimulation running (output will update every 5 steps)...\n")

        last_display = 0
        display_interval = 5

        try:
            while self.running and self.step < self.max_steps:
                # Step simulation if not paused
                if not self.paused:
                    self._step_simulation()

                # Display update
                if (self.step - last_display) >= display_interval or self.step == self.max_steps:
                    print("\033[2J\033[H")  # Clear screen
                    print(self.display())
                    last_display = self.step

                time.sleep(0.05)

        except KeyboardInterrupt:
            print("\n\nSimulation interrupted by user.")
            self.running = False

        print("\n" + "=" * 75)
        print("  Simulation Complete")
        print("=" * 75)
        print(self.display())


def main():
    """Entry point."""
    import sys

    print("\n" + "=" * 75)
    print("  AEOLUS INTERACTIVE DASHBOARD")
    print("  Tornado Electromagnetic Intervention System")
    print("=" * 75 + "\n")

    # Check for command-line arguments
    max_steps = 120
    grid_size = 32

    if len(sys.argv) > 1:
        try:
            max_steps = int(sys.argv[1])
        except ValueError:
            pass

    print(f"Configuration:")
    print(f"  Grid size: {grid_size}³")
    print(f"  Max steps: {max_steps}")
    print(f"  Time step: 0.05 s")
    print(f"  Total simulation time: ~{max_steps * 0.05:.1f} s\n")

    dashboard = EnhancedDashboard(max_steps=max_steps, grid_size=grid_size)

    print("Running simulation...")
    dashboard.run_interactive()


if __name__ == "__main__":
    main()
