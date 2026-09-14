"""Incompressible Navier-Stokes solver using SIMPLE pressure-correction scheme."""

import numpy as np


class NavierStokesSolver:
    """SIMPLE pressure-correction algorithm for 3D cylindrical incompressible flow.

    Momentum: ∂u/∂t + (u·∇)u = -∇p/ρ + ν∇²u
    Continuity: ∇·u = 0 (enforced via pressure Poisson)
    """

    def __init__(self, grid, dt: float, mu: float = 1.81e-5, rho: float = 1.225, max_iter: int = 3):
        """Initialize solver.

        Args:
            grid: CylindricalGrid instance
            dt: time step (seconds)
            mu: dynamic viscosity (Pa·s)
            rho: density (kg/m³)
            max_iter: pressure-correction iterations per time step
        """
        self.grid = grid
        self.dt = dt
        self.mu = mu
        self.rho = rho
        self.nu = mu / rho
        self.max_iter = max_iter
        self.underscore_p = 0.7  # pressure under-relaxation

    def step(self, u_r, u_theta, u_z, p):
        """Advance solution by one time step using SIMPLE.

        Args:
            u_r, u_theta, u_z: velocity components (shape: nx, ntheta, nz)
            p: pressure (shape: nx, ntheta, nz)

        Returns:
            u_r, u_theta, u_z, p: updated fields
        """
        # Predict momentum (explicit convection + diffusion, no pressure)
        u_r_star = self._momentum_r(u_r, u_theta, u_z)
        u_theta_star = self._momentum_theta(u_r, u_theta, u_z)
        u_z_star = self._momentum_z(u_r, u_theta, u_z)

        # Pressure-correction loop
        for iter_p in range(self.max_iter):
            # Solve pressure Poisson: ∇²p = ρ/Δt (∇·u*)
            p_new = self._solve_pressure_poisson(u_r_star, u_theta_star, u_z_star)

            # Correct velocities: u = u* - (Δt/ρ)∇p
            dp = p_new - p
            u_r_new = u_r_star - (self.dt / self.rho) * self._grad_r(dp)
            u_theta_new = u_theta_star - (self.dt / (self.rho * np.maximum(self.grid.r[:, np.newaxis, np.newaxis], 1e-3))) * self._grad_theta(dp)
            u_z_new = u_z_star - (self.dt / self.rho) * self._grad_z(dp)

            # Under-relax and update
            p = p + self.underscore_p * dp
            u_r_star = u_r_new
            u_theta_star = u_theta_new
            u_z_star = u_z_new

        return u_r_new, u_theta_new, u_z_new, p

    def _momentum_r(self, u_r, u_theta, u_z):
        """Radial momentum: ∂(r*u_r)/∂t + conv(u_r) - u_θ²/r = -∂p/∂r + ν·L(u_r)."""
        # Simple explicit step: diffusion + centrifugal term
        lapl_r = self._laplacian_r(u_r)

        # Centrifugal term: u_θ²/r
        r_mesh = np.maximum(self.grid.r[:, np.newaxis, np.newaxis], 1e-3)
        centrifugal = (u_theta ** 2) / r_mesh

        # Time integration
        du_r = self.dt * (self.nu * lapl_r + centrifugal)
        u_r_new = u_r + du_r
        return u_r_new

    def _momentum_theta(self, u_r, u_theta, u_z):
        """Azimuthal momentum: ∂(u_θ)/∂t + conv(u_θ) + (u_r*u_θ)/r = -(1/r)∂p/∂θ + ν·L(u_θ)."""
        # Simple explicit step: diffusion + radial coupling
        lapl_theta = self._laplacian_theta(u_theta)

        # Radial coupling: (u_r*u_θ)/r
        r_mesh = np.maximum(self.grid.r[:, np.newaxis, np.newaxis], 1e-3)
        radial_coupling = (u_r * u_theta) / r_mesh

        # Time integration
        du_theta = self.dt * (self.nu * lapl_theta - radial_coupling)
        u_theta_new = u_theta + du_theta
        return u_theta_new

    def _momentum_z(self, u_r, u_theta, u_z):
        """Vertical momentum: ∂u_z/∂t + conv(u_z) = -∂p/∂z + ν·L(u_z)."""
        # Simple explicit step: diffusion only
        lapl_z = self._laplacian_z(u_z)

        # Time integration
        du_z = self.dt * (self.nu * lapl_z)
        u_z_new = u_z + du_z
        return u_z_new

    def _laplacian_r(self, u_r):
        """Laplacian of radial velocity in cylindrical coords: ∇²u_r - u_r/r²."""
        r_mesh = np.maximum(self.grid.r[:, np.newaxis, np.newaxis], 1e-3)

        # ∂²u_r/∂r² approximation (simple 2nd order)
        d2ur_dr2 = np.zeros_like(u_r)
        for i in range(1, self.grid.nx - 1):
            d2ur_dr2[i, :, :] = (u_r[i+1, :, :] - 2*u_r[i, :, :] + u_r[i-1, :, :]) / (self.grid.dr[i] * self.grid.dr[i-1])

        dur_dr = np.zeros_like(u_r)
        for i in range(self.grid.nx - 1):
            dur_dr[i, :, :] = (u_r[i+1, :, :] - u_r[i, :, :]) / self.grid.dr[i]

        term_r = d2ur_dr2 + dur_dr / r_mesh

        # ∂²u_r/∂θ² / r²
        d2ur_dtheta2 = np.gradient(np.gradient(u_r, axis=1), axis=1) / (self.grid.dtheta ** 2)
        term_theta = d2ur_dtheta2 / (r_mesh ** 2)

        # ∂²u_r/∂z²
        d2ur_dz2 = np.gradient(np.gradient(u_r, axis=2), axis=2) / (self.grid.dz ** 2)

        return term_r + term_theta + d2ur_dz2 - u_r / (r_mesh ** 2)

    def _laplacian_theta(self, u_theta):
        """Laplacian of azimuthal velocity: ∇²u_θ - u_θ/r²."""
        r_mesh = np.maximum(self.grid.r[:, np.newaxis, np.newaxis], 1e-3)

        # ∂²u_θ/∂r²
        d2utheta_dr2 = np.zeros_like(u_theta)
        for i in range(1, self.grid.nx - 1):
            d2utheta_dr2[i, :, :] = (u_theta[i+1, :, :] - 2*u_theta[i, :, :] + u_theta[i-1, :, :]) / (self.grid.dr[i] * self.grid.dr[i-1])

        dutheta_dr = np.zeros_like(u_theta)
        for i in range(self.grid.nx - 1):
            dutheta_dr[i, :, :] = (u_theta[i+1, :, :] - u_theta[i, :, :]) / self.grid.dr[i]

        term_r = d2utheta_dr2 + dutheta_dr / r_mesh

        # ∂²u_θ/∂θ²/r²
        d2utheta_dtheta2 = np.gradient(np.gradient(u_theta, axis=1), axis=1) / (self.grid.dtheta ** 2)
        term_theta = d2utheta_dtheta2 / (r_mesh ** 2)

        # ∂²u_θ/∂z²
        d2utheta_dz2 = np.gradient(np.gradient(u_theta, axis=2), axis=2) / (self.grid.dz ** 2)

        return term_r + term_theta + d2utheta_dz2 - u_theta / (r_mesh ** 2)

    def _laplacian_z(self, u_z):
        """Laplacian of vertical velocity: ∇²u_z."""
        r_mesh = np.maximum(self.grid.r[:, np.newaxis, np.newaxis], 1e-3)

        # ∂²u_z/∂r²
        d2uz_dr2 = np.zeros_like(u_z)
        for i in range(1, self.grid.nx - 1):
            d2uz_dr2[i, :, :] = (u_z[i+1, :, :] - 2*u_z[i, :, :] + u_z[i-1, :, :]) / (self.grid.dr[i] * self.grid.dr[i-1])

        duz_dr = np.zeros_like(u_z)
        for i in range(self.grid.nx - 1):
            duz_dr[i, :, :] = (u_z[i+1, :, :] - u_z[i, :, :]) / self.grid.dr[i]

        term_r = d2uz_dr2 + duz_dr / r_mesh

        # ∂²u_z/∂θ²/r²
        d2uz_dtheta2 = np.gradient(np.gradient(u_z, axis=1), axis=1) / (self.grid.dtheta ** 2)
        term_theta = d2uz_dtheta2 / (r_mesh ** 2)

        # ∂²u_z/∂z²
        d2uz_dz2 = np.gradient(np.gradient(u_z, axis=2), axis=2) / (self.grid.dz ** 2)

        return term_r + term_theta + d2uz_dz2

    def _solve_pressure_poisson(self, u_r, u_theta, u_z):
        """Solve ∇²p = ρ/Δt (∇·u*) using Jacobi iteration."""
        # Divergence of predicted velocity
        r_mesh = np.maximum(self.grid.r[:, np.newaxis, np.newaxis], 1e-3)

        # ∇·u = (1/r)·∂(r·u_r)/∂r + (1/r)·∂u_θ/∂θ + ∂u_z/∂z
        div_radial = np.zeros_like(u_r)
        for i in range(self.grid.nx - 1):
            div_radial[i, :, :] = (r_mesh[i+1, :, :] * u_r[i+1, :, :] - r_mesh[i, :, :] * u_r[i, :, :]) / (self.grid.dr[i] * r_mesh[i, :, :])

        div_theta = np.gradient(u_theta, axis=1) / (self.grid.dtheta * r_mesh)
        div_z = np.gradient(u_z, axis=2) / self.grid.dz

        div_u_star = div_radial + div_theta + div_z
        rhs = (self.rho / self.dt) * div_u_star

        # Solve Laplacian with Jacobi iteration
        p = np.zeros_like(rhs)
        for iter_poisson in range(15):
            lapl_p = self._laplacian_scalar(p)
            residual = rhs - lapl_p
            p = p + 0.08 * residual  # small damping for stability

        return p

    def _laplacian_scalar(self, p):
        """Laplacian of scalar field."""
        r_mesh = np.maximum(self.grid.r[:, np.newaxis, np.newaxis], 1e-3)

        # ∂²p/∂r²
        d2p_dr2 = np.zeros_like(p)
        for i in range(1, self.grid.nx - 1):
            d2p_dr2[i, :, :] = (p[i+1, :, :] - 2*p[i, :, :] + p[i-1, :, :]) / (self.grid.dr[i] * self.grid.dr[i-1])

        dp_dr = np.zeros_like(p)
        for i in range(self.grid.nx - 1):
            dp_dr[i, :, :] = (p[i+1, :, :] - p[i, :, :]) / self.grid.dr[i]

        term_r = d2p_dr2 + dp_dr / r_mesh

        # ∂²p/∂θ²/r²
        d2p_dtheta2 = np.gradient(np.gradient(p, axis=1), axis=1) / (self.grid.dtheta ** 2)
        term_theta = d2p_dtheta2 / (r_mesh ** 2)

        # ∂²p/∂z²
        d2p_dz2 = np.gradient(np.gradient(p, axis=2), axis=2) / (self.grid.dz ** 2)

        return term_r + term_theta + d2p_dz2

    def _grad_r(self, p):
        """Radial gradient ∂p/∂r."""
        grad = np.zeros_like(p)
        for i in range(self.grid.nx - 1):
            grad[i, :, :] = (p[i+1, :, :] - p[i, :, :]) / self.grid.dr[i]
        return grad

    def _grad_theta(self, p):
        """Azimuthal gradient (1/r)·∂p/∂θ."""
        return np.gradient(p, axis=1) / self.grid.dtheta

    def _grad_z(self, p):
        """Vertical gradient ∂p/∂z."""
        return np.gradient(p, axis=2) / self.grid.dz
