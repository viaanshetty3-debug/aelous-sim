"""Momentum sink intervention: tangential suction + surface inflow blackout."""

import numpy as np


class MomentumSinkIntervention:
    """Apply localized pressure/velocity sinks to disrupt tangential circulation."""

    def __init__(
        self,
        grid,
        pressure_deficit: float = -500.0,
        blackout_depth: int = 10,
        sink_radius: float = 1000.0,
    ):
        """Initialize momentum sink intervention.

        Args:
            grid: CylindricalGrid instance
            pressure_deficit: pressure perturbation at sink location (Pa)
            blackout_depth: depth of surface inflow blackout (grid cells)
            sink_radius: radial extent of suction sink (m)
        """
        self.grid = grid
        self.pressure_deficit = pressure_deficit
        self.blackout_depth = blackout_depth
        self.sink_radius = sink_radius

    def apply(self, u_r, u_theta, u_z, p, step: int):
        """Apply momentum sink and surface inflow blackout.

        Args:
            u_r, u_theta, u_z: velocity components
            p: pressure
            step: current time step

        Returns:
            Modified u_r, u_theta, u_z, p
        """
        r_mesh, theta_mesh, z_mesh = np.meshgrid(
            self.grid.r, self.grid.theta, self.grid.z, indexing="ij"
        )

        # Localize sink to mid-domain radii and near-surface layer
        r_dist = r_mesh
        sink_mask = np.exp(-(r_dist ** 2) / (2 * (self.sink_radius ** 2)))
        z_surface_mask = np.zeros_like(z_mesh)
        z_surface_mask[:, :, :self.blackout_depth] = 1.0

        # Apply pressure perturbation during pressure-correction phase
        p += self.pressure_deficit * sink_mask * z_surface_mask

        # Suppress radial inflow at surface (blackout)
        u_r[:, :, :self.blackout_depth] *= (1 - z_surface_mask[:, :, :self.blackout_depth])

        return u_r, u_theta, u_z, p
