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
    ):
        """Initialize momentum sink intervention.

        Args:
            grid: CylindricalGrid instance
            pressure_deficit: pressure perturbation at sink (Pa, negative = suction)
            blackout_depth_m: vertical depth of surface inflow blackout (m)
            sink_radius: radial scale of suction sink (m)
            sink_center_r: radial location of sink (m)
        """
        self.grid = grid
        self.pressure_deficit = pressure_deficit
        self.blackout_depth_m = blackout_depth_m
        self.sink_radius = sink_radius
        self.sink_center_r = sink_center_r

        # Find grid indices for blackout zone
        self.blackout_k_max = np.argmin(np.abs(self.grid.z - blackout_depth_m))

    def apply(self, u_r, u_theta, u_z, p, step: int):
        """Apply momentum sink and surface inflow blackout.

        Args:
            u_r, u_theta, u_z: velocity components
            p: pressure
            step: current time step (unused; sink is always active)

        Returns:
            Modified u_r, u_theta, u_z, p
        """
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

        # Apply pressure deficit
        p = p + self.pressure_deficit * sink_mask

        # (2) SURFACE INFLOW BLACKOUT (z < blackout_depth_m)
        # Suppress radial inflow at surface by setting u_r ≈ 0
        blackout_mask = z_mesh < self.grid.z[self.blackout_k_max]
        u_r = u_r * (1.0 - 0.9 * blackout_mask)  # reduce radial inflow by 90%

        # Also suppress low-level vertical velocity to inhibit boundary layer recovery
        u_z[:, :, :self.blackout_k_max] *= (1.0 - 0.5 * np.ones_like(u_z[:, :, :self.blackout_k_max]))

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
