"""Thermodynamic RFD intervention: buoyancy injection in rear-flank downdraft."""

import numpy as np


class ThermalRFDIntervention:
    """Inject localized positive thermal buoyancy to disrupt downdraft-driven circulation."""

    def __init__(
        self,
        grid,
        injection_z_frac: float = 0.8,
        injection_r_scale: float = 1.5,
        buoyancy_anomaly: float = 3.0,
        duration_steps: int = 60,
    ):
        """Initialize thermal intervention.

        Args:
            grid: CylindricalGrid instance
            injection_z_frac: z-level for injection (fraction of domain height)
            injection_r_scale: radial extent (multiple of core radius)
            buoyancy_anomaly: temperature perturbation (K)
            duration_steps: number of steps to apply intervention
        """
        self.grid = grid
        self.injection_z_frac = injection_z_frac
        self.injection_r_scale = injection_r_scale
        self.buoyancy_anomaly = buoyancy_anomaly
        self.duration_steps = duration_steps

    def apply(self, u_r, u_theta, u_z, p, step: int):
        """Apply thermal perturbation to momentum field (via buoyancy).

        Args:
            u_r, u_theta, u_z: velocity components
            p: pressure
            step: current time step

        Returns:
            Modified u_r, u_theta, u_z, p
        """
        if step > self.duration_steps:
            return u_r, u_theta, u_z, p

        # Locate injection region
        z_inject = self.injection_z_frac * self.grid.z_max
        r_inject = self.injection_r_scale * 500  # assume 500m core radius

        # Create Gaussian mask
        r_mesh, theta_mesh, z_mesh = np.meshgrid(
            self.grid.r, self.grid.theta, self.grid.z, indexing="ij"
        )
        r_dist = np.sqrt((r_mesh - r_inject) ** 2)
        z_dist = np.abs(z_mesh - z_inject)

        sigma_r, sigma_z = r_inject / 3, z_inject / 10
        mask = np.exp(-(r_dist ** 2 / (2 * sigma_r ** 2) + z_dist ** 2 / (2 * sigma_z ** 2)))

        # Add buoyancy-driven vertical velocity
        g = 9.81
        buoyancy_accel = g * self.buoyancy_anomaly / 288  # simplified (T_ref=288K)
        u_z += mask * buoyancy_accel * (self.duration_steps - step) / self.duration_steps

        return u_r, u_theta, u_z, p
