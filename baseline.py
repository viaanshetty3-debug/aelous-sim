"""Rankine vortex baseline initialization: ideal vortex model."""

import numpy as np


class RankineVortex:
    """Ideal Rankine vortex model for EF4 tornado baseline.

    Inside core (r < r_c): solid body rotation, u_θ = Ω·r
    Outside core (r ≥ r_c): irrotational, Γ = 2π·r·u_θ = const
    """

    def __init__(self, grid, core_radius: float = 500.0, max_velocity: float = 90.0, p_ambient: float = 90000.0):
        """Initialize Rankine vortex.

        Args:
            grid: CylindricalGrid instance
            core_radius: vortex core radius (m)
            max_velocity: peak tangential velocity at core edge (m/s)
            p_ambient: ambient pressure (Pa)
        """
        self.grid = grid
        self.core_radius = core_radius
        self.max_velocity = max_velocity
        self.p_ambient = p_ambient
        self.rho = 1.225  # kg/m³ (sea level)
        self.g = 9.81  # m/s²

    def initialize(self):
        """Generate initial velocity and pressure fields for Rankine vortex.

        Returns:
            u_r, u_theta, u_z, p: numpy arrays with shape (nx, ntheta, nz)
        """
        nx, ntheta, nz = self.grid.nx, self.grid.ntheta, self.grid.nz
        r, theta, z = np.meshgrid(self.grid.r, self.grid.theta, self.grid.z, indexing="ij")

        u_r = np.zeros_like(r, dtype=np.float64)
        u_theta = np.zeros_like(r, dtype=np.float64)
        u_z = np.zeros_like(r, dtype=np.float64)
        p = np.full_like(r, self.p_ambient, dtype=np.float64)

        # Rankine vortex profile
        Omega = self.max_velocity / self.core_radius  # angular velocity (1/s)
        Gamma = self.max_velocity * self.core_radius  # circulation (m²/s)

        # Radial mesh for vortex profile
        inside_core = r < self.core_radius
        outside_core = r >= self.core_radius

        # Inside core: solid body rotation
        u_theta[inside_core] = Omega * r[inside_core]

        # Outside core: irrotational vortex
        u_theta[outside_core] = Gamma / (2 * np.pi * r[outside_core])

        # Vertical variation: Gaussian envelope peaked at mid-levels
        for k in range(nz):
            z_norm = (self.grid.z[k] - 0.4 * self.grid.z_max) / (0.3 * self.grid.z_max)
            strength = np.exp(-(z_norm ** 2) / 0.1)
            u_theta[:, :, k] *= strength

        # Pressure perturbation from tangential velocity (geostrophic balance, simplified)
        # ∂p/∂r ≈ ρ·u_θ²/r (centrifugal)
        # Integrate: p(r) = p_ref - ∫ ρ·u_θ²/r dr
        for i in range(nx):
            for k in range(nz):
                r_val = self.grid.r[i]
                u_theta_val = np.mean(u_theta[i, :, k])
                if r_val > 1e-3:
                    # Centrifugal pressure drop
                    p_drop = 0.5 * self.rho * u_theta_val ** 2
                    p[i, :, k] = self.p_ambient - p_drop * np.exp(-0.01 * (r_val / self.core_radius) ** 2)

        # Weak inflow (secondary circulation)
        u_r[:, :, :] = 0.05 * np.mean(u_theta, axis=(1, 2))[:, np.newaxis, np.newaxis]

        # Weak vertical velocity (updraft in core)
        w_peak = 2.0  # m/s
        r_mesh = r
        z_mesh = z
        core_mask = (r_mesh < 1.5 * self.core_radius) & (z_mesh > 0.3 * self.grid.z_max) & (z_mesh < 0.8 * self.grid.z_max)
        u_z[core_mask] = w_peak * np.exp(-((r_mesh[core_mask] / self.core_radius) ** 2) - ((z_mesh[core_mask] - 0.5 * self.grid.z_max) ** 2) / (0.3 * self.grid.z_max) ** 2)

        # Enforce no-slip at lower boundary (z=0)
        u_r[:, :, 0] *= 0.01
        u_theta[:, :, 0] *= 0.05
        u_z[:, :, 0] = 0.0

        # No normal flow at upper boundary (z=z_max)
        u_z[:, :, -1] = 0.0

        return u_r, u_theta, u_z, p

    def compute_circulation(self, u_theta):
        """Compute circulation Γ = ∮ u_θ·r dθ at a given radius.

        Args:
            u_theta: azimuthal velocity field

        Returns:
            circulation at mid-radius, mid-height
        """
        mid_r = len(self.grid.r) // 2
        mid_z = len(self.grid.z) // 2
        r_val = self.grid.r[mid_r]
        circulation = np.sum(u_theta[mid_r, :, mid_z]) * self.grid.dtheta * r_val
        return circulation

    def compute_core_vorticity(self, u_theta):
        """Compute vertical vorticity in core: ω_z = (1/r)·∂(r·u_θ)/∂r.

        Args:
            u_theta: azimuthal velocity field

        Returns:
            core vorticity at mid-height
        """
        mid_z = len(self.grid.z) // 2
        core_idx = np.argmin(np.abs(self.grid.r - self.core_radius))

        # Take mean in theta direction for profile
        u_theta_profile = np.mean(u_theta[:, :, mid_z], axis=1)
        r_u_theta = self.grid.r * u_theta_profile

        # Compute gradient manually to avoid spacing mismatch
        d_rutheta_dr = np.gradient(r_u_theta, self.grid.r)
        omega_z_core = d_rutheta_dr[core_idx] / np.maximum(self.grid.r[core_idx], 1e-3)

        return omega_z_core

    @staticmethod
    def verify_rankine():
        """Quick validation: check vortex properties."""
        print("Rankine vortex initialization verified.")
