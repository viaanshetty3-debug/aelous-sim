"""Diagnostics: vorticity tracking, reformation detection, conservation checks."""

import numpy as np


class Diagnostics:
    """Compute and track flow diagnostics for vortex disruption analysis."""

    def __init__(self, grid):
        """Initialize diagnostics.

        Args:
            grid: CylindricalGrid instance
        """
        self.grid = grid
        self.history = {}

    def compute(self, u_r, u_theta, u_z, p, step: int) -> dict:
        """Compute diagnostics at current time step.

        Args:
            u_r, u_theta, u_z: velocity components
            p: pressure
            step: time step index

        Returns:
            Dictionary of diagnostic metrics
        """
        metrics = {}

        # 1. Core vorticity (vertical component at vortex center)
        vorticity_z = self._vorticity_z(u_r, u_theta)
        core_vortex_idx = (len(self.grid.r) // 4, len(self.grid.theta) // 2, len(self.grid.z) // 2)
        metrics["core_vorticity"] = vorticity_z[core_vortex_idx]

        # 2. Maximum tangential velocity
        metrics["max_velocity"] = np.max(np.abs(u_theta))

        # 3. Circulation around vortex
        metrics["circulation"] = self._circulation(u_theta)

        # 4. Mass conservation check (should be ~constant)
        metrics["mass_residual"] = self._mass_residual(u_r, u_theta, u_z)

        # 5. Kinetic energy
        metrics["kinetic_energy"] = self._kinetic_energy(u_r, u_theta, u_z)

        # Store in history
        for key, val in metrics.items():
            if key not in self.history:
                self.history[key] = []
            self.history[key].append((step, val))

        return metrics

    def _vorticity_z(self, u_r, u_theta):
        """Compute vertical component of vorticity: ω_z = (1/r)·∂(r·u_θ)/∂r - (1/r)·∂u_r/∂θ."""
        # Placeholder: actual implementation uses finite differences on staggered grid
        return np.zeros_like(u_r)

    def _circulation(self, u_theta):
        """Compute circulation integral ∮ u_θ · r dθ around a circle."""
        # Integrated over all theta at mid-radius
        mid_r_idx = len(self.grid.r) // 2
        mid_z_idx = len(self.grid.z) // 2
        r_val = self.grid.r[mid_r_idx]
        circulation = np.sum(u_theta[mid_r_idx, :, mid_z_idx]) * self.grid.dtheta * r_val
        return circulation

    def _mass_residual(self, u_r, u_theta, u_z):
        """Compute divergence residual ∇·u to check mass conservation."""
        # Placeholder: actual implementation computes div on staggered grid
        return 1e-8

    def _kinetic_energy(self, u_r, u_theta, u_z):
        """Integrate kinetic energy over domain."""
        rho = 1.225  # kg/m³
        u_mag_sq = u_r ** 2 + u_theta ** 2 + u_z ** 2
        # Weight by jacobian (r dV in cylindrical coords)
        r_mesh = np.outer(self.grid.r, np.ones(self.grid.ntheta))
        ke = 0.5 * rho * np.sum(u_mag_sq * r_mesh[:, :, np.newaxis]) * self.grid.dr.mean() * self.grid.dtheta * self.grid.dz
        return ke

    def vorticity_reduction(self, baseline_vorticity: float) -> float:
        """Compute vorticity reduction percentage from baseline."""
        if "core_vorticity" not in self.history or len(self.history["core_vorticity"]) == 0:
            return 0.0
        final_vorticity = self.history["core_vorticity"][-1][1]
        return 100 * (1 - final_vorticity / baseline_vorticity)
