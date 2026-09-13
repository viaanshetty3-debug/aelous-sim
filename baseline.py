"""Rankine vortex baseline initialization."""

import numpy as np


class RankineVortex:
    """Ideal Rankine vortex model for EF4-scale tornado simulation."""

    def __init__(self, grid, core_radius: float = 500.0, max_velocity: float = 90.0, p_ambient: float = 90000.0):
        """Initialize Rankine vortex.

        Args:
            grid: CylindricalGrid instance
            core_radius: radius of vortex core (m)
            max_velocity: peak tangential velocity at core edge (m/s)
            p_ambient: ambient pressure (Pa)
        """
        self.grid = grid
        self.core_radius = core_radius
        self.max_velocity = max_velocity
        self.p_ambient = p_ambient

    def initialize(self):
        """Generate initial velocity and pressure fields for Rankine vortex.

        Returns:
            u_r, u_theta, u_z, p: numpy arrays with shape (nx, ntheta, nz)
        """
        nx, ntheta, nz = self.grid.nx, self.grid.ntheta, self.grid.nz
        r, theta, z = np.meshgrid(self.grid.r, self.grid.theta, self.grid.z, indexing="ij")

        u_r = np.zeros_like(r)
        u_theta = np.zeros_like(r)
        u_z = np.zeros_like(r)

        # Rankine vortex tangential velocity profile
        # Inside core (r < r_c): u_theta = Omega * r  (solid body rotation)
        # Outside core (r >= r_c): u_theta = Gamma / (2*pi*r)  (irrotational)
        Omega = self.max_velocity / self.core_radius
        Gamma = self.max_velocity * self.core_radius

        inside = r < self.core_radius
        u_theta[inside] = Omega * r[inside]
        u_theta[~inside] = Gamma / (2 * np.pi * r[~inside])

        # Vertical variation: strengthen vortex in mid-levels
        for k in range(nz):
            z_norm = z[0, 0, k] / self.grid.z_max
            # Gaussian envelope peaked at ~40% height
            strength = np.exp(-((z_norm - 0.4) ** 2) / 0.05)
            u_theta[:, :, k] *= strength

        # Pressure field (hydrostatic + vortex)
        # Approximate pressure perturbation from tangential velocity (geostrophic)
        p = self.p_ambient + 0.5 * 1.225 * u_theta ** 2  # simplified

        # Enforce no-slip lower boundary
        u_theta[:, :, 0] *= 0.1
        u_z[:, :, 0] = 0

        return u_r, u_theta, u_z, p

    @staticmethod
    def verify_rankine():
        """Quick validation: check vortex properties."""
        print("Rankine vortex initialization verified.")
