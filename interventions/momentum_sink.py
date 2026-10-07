"""Momentum sink intervention: tangential suction sink + surface inflow blackout."""

import numpy as np


class MomentumSinkIntervention:
    """Apply localized pressure/velocity sinks to disrupt tangential circulation.

    Mechanism 1: Pressure sink creates adverse pressure gradient → suppresses flow
    Mechanism 2: Surface inflow blackout prevents boundary layer recovery
    """

    def __init__(
        self,
        grid,
        pressure_deficit: float = -500.0,
        blackout_depth_m: float = 200.0,
        sink_radius: float = 1000.0,
        sink_center_r: float = 800.0,
        active_duration_steps: int = 50,
        decay_duration_steps: int = 40,
    ):
        """Initialize momentum sink intervention.

        Args:
            grid: CylindricalGrid instance
            pressure_deficit: pressure perturbation at sink (Pa, negative = suction)
            blackout_depth_m: vertical depth of surface inflow blackout (m)
            sink_radius: radial scale of suction sink (m)
            sink_center_r: radial location of sink (m)
            active_duration_steps: steps of full-strength sink (default 50)
            decay_duration_steps: steps of decay after active period (default 40)
        """
        self.grid = grid
        self.pressure_deficit = pressure_deficit
        self.blackout_depth_m = blackout_depth_m
        self.sink_radius = sink_radius
        self.sink_center_r = sink_center_r
        self.active_duration = active_duration_steps
        self.decay_duration = decay_duration_steps
        self.total_duration = active_duration_steps + decay_duration_steps

        # Find grid indices for blackout zone
        self.blackout_k_max = np.argmin(np.abs(self.grid.z - blackout_depth_m))

    def _sink_envelope(self, step: int):
        """Compute sink strength envelope with decay.

        Phase 1 (0 to active_duration): Full strength
        Phase 2 (active_duration to total_duration): Exponential decay
        Phase 3 (after total_duration): Zero

        Returns:
            Multiplier for current sink strength (0 to 1)
        """
        if step >= self.total_duration:
            return 0.0

        if step < self.active_duration:
            return 1.0
        else:
            # Decay phase: exponential decay
            decay_step = step - self.active_duration
            decay_fraction = decay_step / max(1, self.decay_duration)
            return np.exp(-2.0 * decay_fraction)

    def apply(self, u_r, u_theta, u_z, p, step: int):
        """Apply momentum sink and surface inflow blackout with decay.

        Args:
            u_r, u_theta, u_z: velocity components
            p: pressure
            step: current time step

        Returns:
            Modified u_r, u_theta, u_z, p
        """
        # Get envelope strength (decays after active_duration)
        envelope = self._sink_envelope(step)

        if envelope < 1e-6:
            return u_r, u_theta, u_z, p

        # Create mesh for spatial localization
        r_mesh, theta_mesh, z_mesh = np.meshgrid(
            self.grid.r, self.grid.theta, self.grid.z, indexing="ij"
        )

        # (1) PRESSURE SINK: localized suction in mid-levels
        # Radial Gaussian centered at sink_center_r
        r_sink_dist = np.abs(r_mesh - self.sink_center_r)
        sigma_r_sink = self.sink_radius / 2.0
        sink_mask_r = np.exp(-(r_sink_dist ** 2) / (2 * sigma_r_sink ** 2))

        # Vertical Gaussian centered at mid-height
        z_center = 0.5 * self.grid.z_max
        sigma_z_sink = self.grid.z_max / 6.0
        sink_mask_z = np.exp(-((z_mesh - z_center) ** 2) / (2 * sigma_z_sink ** 2))

        sink_mask = sink_mask_r * sink_mask_z

        # Apply pressure deficit with envelope decay
        p = p + self.pressure_deficit * sink_mask * envelope

        # (2) SURFACE INFLOW BLACKOUT (z < blackout_depth_m)
        # Suppress radial inflow at surface by setting u_r ≈ 0
        blackout_mask = z_mesh < self.grid.z[self.blackout_k_max]
        u_r = u_r * (1.0 - 0.9 * blackout_mask * envelope)  # reduce by 90% during active phase

        # Also suppress low-level vertical velocity to inhibit boundary layer recovery
        u_z[:, :, :self.blackout_k_max] *= (1.0 - 0.5 * envelope * np.ones_like(u_z[:, :, :self.blackout_k_max]))

        return u_r, u_theta, u_z, p

    def get_sink_mask(self):
        """Return sink spatial mask for diagnostics."""
        r_mesh, _, z_mesh = np.meshgrid(
            self.grid.r, self.grid.theta, self.grid.z, indexing="ij"
        )

        r_sink_dist = np.abs(r_mesh - self.sink_center_r)
        sigma_r_sink = self.sink_radius / 2.0
        sink_mask_r = np.exp(-(r_sink_dist ** 2) / (2 * sigma_r_sink ** 2))

        z_center = 0.5 * self.grid.z_max
        sigma_z_sink = self.grid.z_max / 6.0
        sink_mask_z = np.exp(-((z_mesh - z_center) ** 2) / (2 * sigma_z_sink ** 2))

        return sink_mask_r * sink_mask_z

    def get_blackout_mask(self):
        """Return surface blackout mask for diagnostics."""
        _, _, z_mesh = np.meshgrid(
            self.grid.r, self.grid.theta, self.grid.z, indexing="ij"
        )
        return z_mesh < self.grid.z[self.blackout_k_max]
