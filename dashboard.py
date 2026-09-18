"""Interactive dashboard for real-time solver control and visualization."""

import curses
import numpy as np
import sys
from pathlib import Path

from grid import CylindricalGrid
from baseline import RankineVortex
from solver import NavierStokesSolver
from interventions import ThermalRFDIntervention, MomentumSinkIntervention
from diagnostics import Diagnostics


class InteractiveDashboard:
    """Real-time interactive dashboard for vortex solver control."""

    def __init__(self, stdscr):
        """Initialize dashboard with curses screen."""
        self.stdscr = stdscr
        curses.curs_set(0)  # Hide cursor
        self.stdscr.nodelay(True)  # Non-blocking input

        # Initialize solver state
        self.grid = CylindricalGrid(nx=64, ntheta=64, nz=64)
        rankine = RankineVortex(grid=self.grid, core_radius=500, max_velocity=90, add_shear=True)
        self.u_r, self.u_theta, self.u_z, self.p = rankine.initialize()
        self.baseline_vorticity = rankine.compute_core_vorticity(self.u_theta)

        self.solver = NavierStokesSolver(
            grid=self.grid, dt=0.05,
            enable_shear=True, enable_lhr=True, enable_precip=True
        )
        self.diagnostics = Diagnostics(grid=self.grid, baseline_vorticity=self.baseline_vorticity)

        # Intervention controls
        self.thermal_enabled = True
        self.momentum_pressure = -250.0  # Pa (controllable: -100 to -500)

        # State variables
        self.step = 0
        self.max_steps = 120
        self.paused = False
        self.show_help = False

        # Metrics history
        self.vorticity_history = []

        # Create interventions
        self._update_interventions()

    def _update_interventions(self):
        """Update interventions based on current settings."""
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

    def _draw_bar_chart(self, y_start, width=50):
        """Draw ASCII bar chart of vorticity reduction."""
        if not self.vorticity_history:
            return y_start

        max_reduction = 150.0
        chart_height = min(8, len(self.vorticity_history))

        self.stdscr.addstr(y_start, 2, "Core Vorticity Reduction (%):", curses.A_BOLD)
        y = y_start + 1

        # Show recent history (last 8 steps)
        start_idx = max(0, len(self.vorticity_history) - chart_height)

        for i, idx in enumerate(range(start_idx, len(self.vorticity_history))):
            reduction = self.vorticity_history[idx]
            bar_len = int((reduction / max_reduction) * width)
            bar_len = min(bar_len, width)

            bar = "█" * bar_len + "░" * (width - bar_len)

            label = f"Step {idx:3d}: {reduction:6.1f}% |{bar}|"
            try:
                self.stdscr.addstr(y, 2, label)
            except curses.error:
                pass
            y += 1

        return y + 1

    def _draw_metrics(self, y_start):
        """Draw current metrics panel."""
        if self.step > 0 and self.diagnostics.history:
            metrics = self.diagnostics.history

            vort = metrics.get("core_vorticity", [])[-1][1] if metrics.get("core_vorticity") else 0.0
            vel = metrics.get("max_velocity", [])[-1][1] if metrics.get("max_velocity") else 0.0
            ke = metrics.get("kinetic_energy", [])[-1][1] if metrics.get("kinetic_energy") else 0.0
            red = metrics.get("vorticity_reduction_pct", [])[-1][1] if metrics.get("vorticity_reduction_pct") else 0.0

            y = y_start
            self.stdscr.addstr(y, 2, "Current Metrics:", curses.A_BOLD)
            y += 1

            metrics_text = [
                f"  Core Vorticity:     {vort:8.3f} 1/s",
                f"  Max Velocity:       {vel:8.3f} m/s",
                f"  Kinetic Energy:     {ke:8.1f} J",
                f"  Reduction:          {red:8.1f} %",
            ]

            for text in metrics_text:
                try:
                    self.stdscr.addstr(y, 2, text)
                except curses.error:
                    pass
                y += 1

        return y_start + 6

    def _draw_controls(self, y_start):
        """Draw control panel."""
        y = y_start
        self.stdscr.addstr(y, 2, "Controls:", curses.A_BOLD)
        y += 1

        thermal_status = "ON" if self.thermal_enabled else "OFF"
        thermal_color = curses.A_BOLD if self.thermal_enabled else 0

        self.stdscr.addstr(y, 2, "  [T] Thermal RFD:    ", 0)
        self.stdscr.addstr(y, 22, thermal_status, thermal_color)
        y += 1

        self.stdscr.addstr(y, 2, f"  [±] Pressure:       {self.momentum_pressure:.0f} Pa")
        y += 1

        self.stdscr.addstr(y, 2, "  [SPACE] Pause/Run", 0)
        y += 1

        self.stdscr.addstr(y, 2, "  [?] Help  [Q] Quit", 0)
        y += 2

        status = "PAUSED" if self.paused else "RUNNING"
        status_attr = curses.A_REVERSE if self.paused else 0
        self.stdscr.addstr(y, 2, f"Status: {status}", status_attr)

        return y + 2

    def _draw_help(self, y_start):
        """Draw help panel."""
        help_text = [
            "KEYBOARD CONTROLS:",
            "",
            "  T       - Toggle Thermal RFD intervention on/off",
            "  +/=     - Increase pressure deficit (toward -500 Pa)",
            "  -/_     - Decrease pressure deficit (toward -100 Pa)",
            "  SPACE   - Pause/Resume simulation",
            "  UP/DOWN - Manual step (when paused)",
            "  Q       - Quit",
            "  ?       - Toggle this help",
            "",
            "The bar chart shows vorticity reduction % at each step.",
            "Positive values indicate successful suppression.",
            "A reduction >100% means sign reversal (antisymmetric).",
        ]

        y = y_start
        for line in help_text:
            try:
                self.stdscr.addstr(y, 2, line)
            except curses.error:
                pass
            y += 1

        return y

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

        # Measure diagnostics
        metrics = self.diagnostics.compute(self.u_r, self.u_theta, self.u_z, self.p, step=self.step)
        self.vorticity_history.append(metrics["vorticity_reduction_pct"])

        self.step += 1

    def _handle_input(self):
        """Handle keyboard input."""
        try:
            key = self.stdscr.getch()
        except:
            return

        if key == -1:
            return

        key_char = chr(key).upper()

        if key_char == 'Q':
            return False
        elif key_char == 'T':
            self.thermal_enabled = not self.thermal_enabled
            self._update_interventions()
        elif key_char in ['+', '=']:
            self.momentum_pressure = min(-100.0, self.momentum_pressure + 25.0)
            self._update_interventions()
        elif key_char in ['-', '_']:
            self.momentum_pressure = max(-500.0, self.momentum_pressure - 25.0)
            self._update_interventions()
        elif key == ord(' '):
            self.paused = not self.paused
        elif key == curses.KEY_UP and self.paused:
            if self.step < self.max_steps:
                self._step_simulation()
        elif key == curses.KEY_DOWN and self.paused:
            if self.step > 0:
                self.step -= 1
                self.vorticity_history.pop()
        elif key_char == '?':
            self.show_help = not self.show_help

        return True

    def _render(self):
        """Render dashboard to screen."""
        self.stdscr.clear()

        height, width = self.stdscr.getmaxyx()

        # Header
        header = f"AEOLUS Interactive Dashboard | Step {self.step}/{self.max_steps}"
        self.stdscr.addstr(0, 0, header, curses.A_REVERSE)
        self.stdscr.addstr(1, 0, "─" * width)

        y = 2

        # Show help or main display
        if self.show_help:
            y = self._draw_help(y)
        else:
            y = self._draw_bar_chart(y)
            y = self._draw_metrics(y)
            y = self._draw_controls(y)

        # Footer
        footer = "Press [?] for help | [Q] to quit"
        try:
            self.stdscr.addstr(height - 1, 0, footer, curses.A_DIM)
        except curses.error:
            pass

        self.stdscr.refresh()

    def run(self):
        """Main dashboard loop."""
        while self.step < self.max_steps:
            # Step simulation if not paused
            if not self.paused:
                self._step_simulation()

            # Handle input and render
            if not self._handle_input():
                break

            self._render()

            # Small delay to prevent CPU thrashing
            curses.napms(50)

        # Final render
        self._render()
        self.stdscr.addstr(self.stdscr.getmaxyx()[0] - 3, 2, "Simulation complete. Press [Q] to exit.")
        self.stdscr.refresh()

        # Wait for quit
        while True:
            try:
                key = self.stdscr.getch()
                if key != -1 and chr(key).upper() == 'Q':
                    break
            except:
                pass
            curses.napms(100)


def main():
    """Entry point."""
    curses.wrapper(lambda stdscr: InteractiveDashboard(stdscr).run())


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDashboard interrupted by user.")
        sys.exit(0)
