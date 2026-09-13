"""Incompressible Navier-Stokes solver using pressure-correction (SIMPLE)."""

import numpy as np
from scipy.sparse import diags
from scipy.sparse.linalg import cg


class NavierStokesSolver:
    """Pressure-correction solver for 3D cylindrical incompressible flow."""

    def __init__(self, grid, dt: float, mu: float = 1.81e-5, rho: float = 1.225):
        """Initialize solver.

        Args:
            grid: CylindricalGrid instance
            dt: time step (seconds)
            mu: dynamic viscosity (Pa·s, default air at 15°C)
            rho: density (kg/m³, default air at sea level)
        """
        self.grid = grid
        self.dt = dt
        self.mu = mu
        self.rho = rho
        self.nu = mu / rho  # kinematic viscosity
        self._build_operators()

    def _build_operators(self):
        """Pre-build differential operators (Laplacian, divergence) on staggered grid."""
        # Placeholder: actual implementation would use sparse matrices for efficiency
        pass

    def step(self, u_r, u_theta, u_z, p):
        """Advance solution by one time step.

        Args:
            u_r, u_theta, u_z: velocity components (np.ndarray)
            p: pressure (np.ndarray)

        Returns:
            u_r, u_theta, u_z, p: updated fields
        """
        # 1. Predict velocities (explicit convection + viscosity)
        u_r_star = self._predict_momentum(u_r, u_theta, u_z, component="r")
        u_theta_star = self._predict_momentum(u_r, u_theta, u_z, component="theta")
        u_z_star = self._predict_momentum(u_r, u_theta, u_z, component="z")

        # 2. Solve pressure Poisson equation
        p_new = self._solve_pressure_poisson(u_r_star, u_theta_star, u_z_star, p)

        # 3. Correct velocities
        u_r_new = u_r_star - (self.dt / self.rho) * self._gradient_r(p_new)
        u_theta_new = u_theta_star - (self.dt / (self.rho * self.grid.r)) * self._gradient_theta(p_new)
        u_z_new = u_z_star - (self.dt / self.rho) * self._gradient_z(p_new)

        return u_r_new, u_theta_new, u_z_new, p_new

    def _predict_momentum(self, u_r, u_theta, u_z, component: str):
        """Predict momentum without pressure gradient (convection + diffusion)."""
        if component == "r":
            u = u_r
        elif component == "theta":
            u = u_theta
        else:
            u = u_z

        # Placeholder: actual implementation computes convection + diffusion
        return u

    def _solve_pressure_poisson(self, u_r, u_theta, u_z, p_init):
        """Solve ∇²p = ρ/Δt (∇·u*)."""
        # Placeholder: actual implementation uses iterative solver (CG, multigrid)
        return p_init

    def _gradient_r(self, p):
        """Radial gradient ∂p/∂r."""
        return np.gradient(p, axis=0)

    def _gradient_theta(self, p):
        """Azimuthal gradient (1/r)·∂p/∂θ."""
        return np.gradient(p, axis=1)

    def _gradient_z(self, p):
        """Vertical gradient ∂p/∂z."""
        return np.gradient(p, axis=2)
