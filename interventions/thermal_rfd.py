"""Thermodynamic RFD intervention: localized buoyancy injection into rear-flank downdraft."""

import numpy as np


class ThermalRFDIntervention:
    """Inject localized positive thermal buoyancy to disrupt RFD-driven circulation.

    Buoyancy force on vertical momentum: b = g·(ΔT/T_ref)
    Affects u_z momentum equation: ∂u_z/∂t = ... + b·mask
    """

    def __init__(
        self,
        grid,
        injection_z_frac: float = 0.7,
        injection_r_scale: float = 1.5,
        buoyancy_anomaly: float = 3.0,
        t_ref: float = 288.0,
        duration_steps: int = 60,
        g: float = 9.81,
    ):
        """Initialize thermal RFD intervention.

        Args:
            grid: CylindricalGrid instance
            injection_z_frac: normalized z-level for injection (0-1)
            injection_r_scale: radial extent (multiple of core radius ~500m)
            buoyancy_anomaly: temperature perturbation (K)
            t_ref: reference temperature for buoyancy (K)
            duration_steps: number of steps to apply intervention
            g: gravitational acceleration (m/s²)
        """
        self.grid = grid
        self.injection_z_frac = injection_z_frac
        self.injection_r_scale = injection_r_scale
        self.buoyancy_anomaly = buoyancy_anomaly
        self.t_ref = t_ref
        self.duration_steps = duration_steps
        self.g = g

    def apply(self, u_r, u_theta, u_z, p, step: int):
        """Apply thermal perturbation: buoyancy force on vertical momentum.

        Mechanism: Heat injection → positive ΔT → buoyancy b = g·ΔT/T_ref
        → upward acceleration in injection zone → suppresses downdraft.

        Args:
            u_r, u_theta, u_z: velocity components
            p: pressure
            step: current time step

        Returns:
            Modified u_r, u_theta, u_z, p
        """
        if step > self.duration_steps:
            return u_r, u_theta, u_z, p

        # Locate injection region: Gaussian at (r_inject, z_inject)
        z_inject = self.injection_z_frac * self.grid.z_max
        r_inject = self.injection_r_scale * 500.0  # 500m nominal core radius

        # Create mesh
        r_mesh, theta_mesh, z_mesh = np.meshgrid(
            self.grid.r, self.grid.theta, self.grid.z, indexing="ij"
        )

        # Distance from injection center (radial direction only, ignoring theta)
        r_dist = r_mesh

        # Gaussian mask in (r, z)
        sigma_r = r_inject / 2.5
        sigma_z = self.grid.z_max / 8.0
        mask = np.exp(
            -(r_dist ** 2) / (2 * sigma_r ** 2)
            - ((z_mesh - z_inject) ** 2) / (2 * sigma_z ** 2)
        )

        # Buoyancy acceleration: b = g·ΔT/T_ref
        buoyancy_accel = self.g * self.buoyancy_anomaly / self.t_ref  # m/s²

        # Fade out over injection duration
        decay = (self.duration_steps - step) / self.duration_steps

        # Add buoyancy force to vertical momentum (directly to u_z, not through p)
        u_z_increment = mask * buoyancy_accel * decay * 0.5  # conservative ramp

        u_z = u_z + u_z_increment

        return u_r, u_theta, u_z, p

    def compute_buoyancy_field(self, step: int):
        """Compute buoyancy field for diagnostics.

        Returns:
            buoyancy acceleration field at current step
        """
        if step > self.duration_steps:
            return np.zeros((self.grid.nx, self.grid.ntheta, self.grid.nz))

        z_inject = self.injection_z_frac * self.grid.z_max
        r_inject = self.injection_r_scale * 500.0

        r_mesh, _, z_mesh = np.meshgrid(
            self.grid.r, self.grid.theta, self.grid.z, indexing="ij"
        )

        sigma_r = r_inject / 2.5
        sigma_z = self.grid.z_max / 8.0
        mask = np.exp(
            -(r_mesh ** 2) / (2 * sigma_r ** 2)
            - ((z_mesh - z_inject) ** 2) / (2 * sigma_z ** 2)
        )

        buoyancy_accel = self.g * self.buoyancy_anomaly / self.t_ref
        decay = (self.duration_steps - step) / self.duration_steps

        return mask * buoyancy_accel * decay * 0.5
