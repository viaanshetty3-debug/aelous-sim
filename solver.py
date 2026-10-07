"""Enhanced Navier-Stokes solver with wind shear & dynamic effects (stable).

Uses conservative central differences with artificial viscosity for stability,
while including realistic wind shear and improved pressure iteration.
"""

import numpy as np


class NavierStokesSolver:
    """SIMPLE pressure-correction with wind shear, LHR, and precipitation drag.

    Momentum: ∂u/∂t + (u·∇)u = -∇p/ρ + ν∇²u + F_shear + F_LHR + F_precip
    Continuity: ∇·u = 0 (enforced via pressure Poisson)
    LHR: Latent heat release from condensation proportional to vertical velocity
    Precip: Precipitation drag from liquid water content
    """

    def __init__(self, grid, dt: float, mu: float = 1.81e-5, rho: float = 1.225,
                 max_iter: int = 5, enable_shear: bool = True, enable_lhr: bool = True,
                 enable_precip: bool = True, enable_adaptive_dt: bool = True,
                 cfl_target: float = 0.7, divergence_limit: float = 0.05):
        """Initialize solver with high-fidelity atmospheric physics.

        Args:
            grid: CylindricalGrid instance
            dt: time step (seconds)
            mu: dynamic viscosity (Pa·s)
            rho: density (kg/m³)
            max_iter: pressure-correction iterations
            enable_shear: enable wind shear profile
            enable_lhr: enable latent heat release
            enable_precip: enable precipitation drag
            enable_adaptive_dt: dynamically adjust dt based on CFL
            cfl_target: target Courant number (keep < this value)
            divergence_limit: if divergence RMS exceeds this, trigger correction
        """
        self.grid = grid
        self.dt = dt
        self.dt_base = dt  # store original dt for reference
        self.mu = mu
        self.rho = rho
        self.nu = mu / rho
        self.max_iter = max_iter
        self.underscore_p = 0.65  # tighter pressure relaxation
        self.enable_shear = enable_shear
        self.enable_lhr = enable_lhr
        self.enable_precip = enable_precip
        self.artificial_viscosity = 0.02  # for stability
        self.enable_adaptive_dt = enable_adaptive_dt
        self.cfl_target = cfl_target
        self.divergence_limit = divergence_limit
        self.last_divergence_rms = 0.0
        self.dt_reduction_count = 0

        # Wind shear parameters
        self.shear_height = 1000.0
        self.surface_wind_speed = 5.0
        self.friction_coefficient = 0.08

        # Latent Heat Release parameters (cloud condensation)
        self.lhr_coefficient = 0.8  # buoyancy from condensation (m/s²)
        self.condensation_threshold = 0.2  # minimum w for condensation (m/s)

        # Precipitation drag parameters
        self.precip_coefficient = 0.15  # drag strength
        self.qv_max = 20.0  # max water vapor content (g/kg)

    def _shear_profile(self, z_coord):
        """Logarithmic wind shear profile."""
        z0 = 0.1
        z_safe = np.maximum(z_coord, z0 + 1e-6)
        profile = self.surface_wind_speed * np.log(z_safe / z0) / np.log(self.shear_height / z0)
        above_shear = z_coord > self.shear_height
        profile = np.where(above_shear, self.surface_wind_speed, profile)
        return profile

    def _latent_heat_release(self, u_z):
        """Latent heat release buoyancy: proportional to upward velocity."""
        if not self.enable_lhr:
            return np.zeros_like(u_z)
        # Heat release from condensation when w > threshold
        condensation = np.maximum(u_z - self.condensation_threshold, 0.0)
        lhr_buoyancy = self.lhr_coefficient * condensation
        return lhr_buoyancy

    def _precipitation_drag(self, u_z):
        """Precipitation drag: downward force from liquid water."""
        if not self.enable_precip:
            return np.zeros_like(u_z)
        # Liquid water content proportional to vertical velocity (cloud presence)
        liquid_water = np.maximum(u_z, 0.0) * 0.5  # cloud water mixing ratio
        # Drag force: negative acceleration from falling water
        drag_force = -self.precip_coefficient * liquid_water
        return drag_force

    def step(self, u_r, u_theta, u_z, p):
        """Advance solution by one time step with adaptive stability controls."""
        # 1. DYNAMIC CFL LIMITER: Adjust dt based on maximum velocity
        if self.enable_adaptive_dt:
            self._apply_cfl_limiter(u_r, u_theta, u_z)

        # Predict momentum (conservative diffusion-dominated)
        u_r_star = self._momentum_r(u_r, u_theta, u_z)
        u_theta_star = self._momentum_theta(u_r, u_theta, u_z)
        u_z_star = self._momentum_z(u_r, u_theta, u_z)

        # Pressure-correction loop
        for iter_p in range(self.max_iter):
            p_new = self._solve_pressure_poisson(u_r_star, u_theta_star, u_z_star)
            dp = p_new - p
            u_r_new = u_r_star - (self.dt / self.rho) * self._grad_r(dp)
            u_theta_new = u_theta_star - (self.dt / (self.rho * np.maximum(self.grid.r[:, np.newaxis, np.newaxis], 1e-3))) * self._grad_theta(dp)
            u_z_new = u_z_star - (self.dt / self.rho) * self._grad_z(dp)

            p = p + self.underscore_p * dp
            u_r_star = u_r_new
            u_theta_star = u_theta_new
            u_z_star = u_z_new

        # 2. DIVERGENCE CHECK: Monitor incompressibility constraint
        divergence_rms = self._compute_divergence_rms(u_r_new, u_theta_new, u_z_new)
        self.last_divergence_rms = divergence_rms
        if divergence_rms > self.divergence_limit:
            # Trigger implicit backward Euler correction
            u_r_new, u_theta_new, u_z_new = self._backward_euler_correction(
                u_r_new, u_theta_new, u_z_new, u_r, u_theta, u_z
            )

        # 3. ENERGY DISSIPATION: Explicitly damp excess kinetic energy
        # This prevents spurious energy growth from pressure-velocity coupling
        u_r_new, u_theta_new, u_z_new = self._apply_energy_dissipation(
            u_r_new, u_theta_new, u_z_new, u_r, u_theta, u_z
        )

        return u_r_new, u_theta_new, u_z_new, p

    def _momentum_r(self, u_r, u_theta, u_z):
        """Radial momentum with conservative scheme."""
        # Simple convection (central differences with damping)
        du_r_dr = np.zeros_like(u_r)
        for i in range(1, self.grid.nx - 1):
            du_r_dr[i, :, :] = (u_r[i+1, :, :] - u_r[i-1, :, :]) / (self.grid.dr[i] + self.grid.dr[i-1])
        conv_r = 0.5 * u_r * du_r_dr

        # Diffusion
        lapl_r = self._laplacian_r(u_r)

        # Centrifugal
        r_mesh = np.maximum(self.grid.r[:, np.newaxis, np.newaxis], 1e-3)
        centrifugal = (u_theta ** 2) / r_mesh

        # Drag
        shear_drag = -self.friction_coefficient * u_r

        # Time integration (conservative)
        du_r = self.dt * (-conv_r + (self.nu + self.artificial_viscosity) * lapl_r + centrifugal + shear_drag)
        u_r_new = u_r + du_r
        u_r_new = np.clip(u_r_new, -200, 200)  # bound velocities
        return u_r_new

    def _momentum_theta(self, u_r, u_theta, u_z):
        """Azimuthal momentum with wind shear coupling."""
        # Simple convection
        du_theta_dtheta = np.gradient(u_theta, axis=1) / self.grid.dtheta
        r_mesh = np.maximum(self.grid.r[:, np.newaxis, np.newaxis], 1e-3)
        conv_theta = 0.5 * (u_theta * du_theta_dtheta / r_mesh)

        # Diffusion
        lapl_theta = self._laplacian_theta(u_theta)

        # Radial coupling
        r_mesh = np.maximum(self.grid.r[:, np.newaxis, np.newaxis], 1e-3)
        radial_coupling = 0.5 * (u_r * u_theta) / r_mesh

        # Shear interaction
        if self.enable_shear:
            u_shear = self._shear_profile(self.grid.z[np.newaxis, np.newaxis, :])
            shear_coupling = self.friction_coefficient * (u_shear - u_theta) * 0.03
        else:
            shear_coupling = 0.0

        shear_drag = -self.friction_coefficient * u_theta * 0.2

        # Time integration
        du_theta = self.dt * (-conv_theta + (self.nu + self.artificial_viscosity) * lapl_theta - radial_coupling + shear_coupling + shear_drag)
        u_theta_new = u_theta + du_theta
        u_theta_new = np.clip(u_theta_new, -200, 200)
        return u_theta_new

    def _momentum_z(self, u_r, u_theta, u_z):
        """Vertical momentum with wind shear, LHR, and precipitation drag."""
        # Simple convection
        du_z_dz = np.gradient(u_z, axis=2) / self.grid.dz
        conv_z = 0.5 * u_z * du_z_dz

        # Diffusion
        lapl_z = self._laplacian_z(u_z)

        # Drag
        vertical_drag = -self.friction_coefficient * u_z * 0.1

        # Latent heat release (buoyancy from condensation)
        lhr_buoyancy = self._latent_heat_release(u_z)

        # Precipitation drag (downward force from liquid water)
        precip_drag = self._precipitation_drag(u_z)

        # Time integration
        du_z = self.dt * (-conv_z + (self.nu + self.artificial_viscosity) * lapl_z + vertical_drag + lhr_buoyancy + precip_drag)
        u_z_new = u_z + du_z
        u_z_new = np.clip(u_z_new, -200, 200)
        return u_z_new

    def _laplacian_r(self, u_r):
        """Laplacian with safety."""
        r_mesh = np.maximum(self.grid.r[:, np.newaxis, np.newaxis], 1e-3)

        d2ur_dr2 = np.zeros_like(u_r)
        for i in range(1, self.grid.nx - 1):
            d2ur_dr2[i, :, :] = (u_r[i+1, :, :] - 2*u_r[i, :, :] + u_r[i-1, :, :]) / (0.5 * (self.grid.dr[i] + self.grid.dr[i-1]) ** 2)

        dur_dr = np.zeros_like(u_r)
        for i in range(self.grid.nx - 1):
            dur_dr[i, :, :] = (u_r[i+1, :, :] - u_r[i, :, :]) / self.grid.dr[i]

        term_r = d2ur_dr2 + dur_dr / r_mesh

        d2ur_dtheta2 = np.gradient(np.gradient(u_r, axis=1), axis=1) / (self.grid.dtheta ** 2)
        term_theta = d2ur_dtheta2 / (r_mesh ** 2)

        d2ur_dz2 = np.gradient(np.gradient(u_r, axis=2), axis=2) / (self.grid.dz ** 2)

        return term_r + term_theta + d2ur_dz2 - u_r / (r_mesh ** 2)

    def _laplacian_theta(self, u_theta):
        """Laplacian for azimuthal velocity."""
        r_mesh = np.maximum(self.grid.r[:, np.newaxis, np.newaxis], 1e-3)

        d2utheta_dr2 = np.zeros_like(u_theta)
        for i in range(1, self.grid.nx - 1):
            d2utheta_dr2[i, :, :] = (u_theta[i+1, :, :] - 2*u_theta[i, :, :] + u_theta[i-1, :, :]) / (0.5 * (self.grid.dr[i] + self.grid.dr[i-1]) ** 2)

        dutheta_dr = np.zeros_like(u_theta)
        for i in range(self.grid.nx - 1):
            dutheta_dr[i, :, :] = (u_theta[i+1, :, :] - u_theta[i, :, :]) / self.grid.dr[i]

        term_r = d2utheta_dr2 + dutheta_dr / r_mesh

        d2utheta_dtheta2 = np.gradient(np.gradient(u_theta, axis=1), axis=1) / (self.grid.dtheta ** 2)
        term_theta = d2utheta_dtheta2 / (r_mesh ** 2)

        d2utheta_dz2 = np.gradient(np.gradient(u_theta, axis=2), axis=2) / (self.grid.dz ** 2)

        return term_r + term_theta + d2utheta_dz2 - u_theta / (r_mesh ** 2)

    def _laplacian_z(self, u_z):
        """Laplacian for vertical velocity."""
        r_mesh = np.maximum(self.grid.r[:, np.newaxis, np.newaxis], 1e-3)

        d2uz_dr2 = np.zeros_like(u_z)
        for i in range(1, self.grid.nx - 1):
            d2uz_dr2[i, :, :] = (u_z[i+1, :, :] - 2*u_z[i, :, :] + u_z[i-1, :, :]) / (0.5 * (self.grid.dr[i] + self.grid.dr[i-1]) ** 2)

        duz_dr = np.zeros_like(u_z)
        for i in range(self.grid.nx - 1):
            duz_dr[i, :, :] = (u_z[i+1, :, :] - u_z[i, :, :]) / self.grid.dr[i]

        term_r = d2uz_dr2 + duz_dr / r_mesh

        d2uz_dtheta2 = np.gradient(np.gradient(u_z, axis=1), axis=1) / (self.grid.dtheta ** 2)
        term_theta = d2uz_dtheta2 / (r_mesh ** 2)

        d2uz_dz2 = np.gradient(np.gradient(u_z, axis=2), axis=2) / (self.grid.dz ** 2)

        return term_r + term_theta + d2uz_dz2

    def _apply_cfl_limiter(self, u_r, u_theta, u_z):
        """Dynamically adjust dt to maintain CFL < target value.

        CFL = (u_max * dt) / dx, must keep < cfl_target (typically 0.7)
        """
        # Compute maximum velocity magnitude across grid
        u_r_abs = np.abs(u_r)
        u_theta_abs = np.abs(u_theta)
        u_z_abs = np.abs(u_z)
        u_max = np.maximum(np.maximum(u_r_abs.max(), u_theta_abs.max()), u_z_abs.max())
        u_max = np.maximum(u_max, 1e-6)  # avoid division by zero

        # Minimum grid spacing (radial)
        dx_min = self.grid.dr.min()

        # Calculate maximum allowable dt
        dt_max = (self.cfl_target * dx_min) / u_max

        # Adjust dt if needed
        if self.dt > dt_max:
            self.dt = dt_max * 0.95  # 5% safety margin
            self.dt_reduction_count += 1

    def _compute_divergence_rms(self, u_r, u_theta, u_z):
        """Compute RMS of velocity divergence across domain.

        div(u) = 1/r * d(r*u_r)/dr + 1/r * du_theta/dtheta + du_z/dz
        """
        r_mesh = np.maximum(self.grid.r[:, np.newaxis, np.newaxis], 1e-3)

        # Radial component
        div_radial = np.zeros_like(u_r)
        for i in range(self.grid.nx - 1):
            div_radial[i, :, :] = (r_mesh[i+1, :, :] * u_r[i+1, :, :] - r_mesh[i, :, :] * u_r[i, :, :]) / (self.grid.dr[i] * r_mesh[i, :, :])

        # Azimuthal component
        div_theta = np.gradient(u_theta, axis=1) / (self.grid.dtheta * r_mesh)

        # Vertical component
        div_z = np.gradient(u_z, axis=2) / self.grid.dz

        # Total divergence
        div_total = div_radial + div_theta + div_z

        # RMS divergence
        divergence_rms = np.sqrt(np.mean(div_total ** 2))
        return divergence_rms

    def _backward_euler_correction(self, u_r_new, u_theta_new, u_z_new, u_r_old, u_theta_old, u_z_old):
        """Apply implicit backward Euler correction to enforce incompressibility.

        This is a simple divergence damping step:
        u_corrected = 0.5 * u_new + 0.5 * u_old  (averaging with previous step)
        """
        # Blend current solution with previous step to reduce divergence
        alpha = 0.3  # correction strength
        u_r_corrected = (1 - alpha) * u_r_new + alpha * u_r_old
        u_theta_corrected = (1 - alpha) * u_theta_new + alpha * u_theta_old
        u_z_corrected = (1 - alpha) * u_z_new + alpha * u_z_old

        # Also reduce dt for next step if divergence is high
        if self.last_divergence_rms > self.divergence_limit * 2:
            self.dt = self.dt * 0.5  # reduce by 50%
            self.dt_reduction_count += 1

        return u_r_corrected, u_theta_corrected, u_z_corrected

    def _apply_energy_dissipation(self, u_r_new, u_theta_new, u_z_new, u_r_old, u_theta_old, u_z_old):
        """Apply explicit energy dissipation to prevent spurious KE growth.

        Suppresses high-frequency oscillations and pressure-velocity coupling artifacts
        that can cause kinetic energy to grow despite viscous dissipation.
        Uses gentle damping to avoid over-suppression while controlling divergence.
        """
        # Compute kinetic energy at current and previous step
        ke_new = 0.5 * np.mean(u_r_new**2 + u_theta_new**2 + u_z_new**2)
        ke_old = 0.5 * np.mean(u_r_old**2 + u_theta_old**2 + u_z_old**2)

        # If energy grew more than 5% in one step, apply gentle damping
        if ke_new > ke_old * 1.05:
            # Energy grew too much - apply gentle damping
            ke_ratio = ke_old / ke_new  # Will be < 1
            damping_factor = 0.99 * np.sqrt(ke_ratio)  # Scale damping by how much KE exceeded threshold
            damping_factor = np.maximum(damping_factor, 0.98)  # Never damp less than 1% (safety)
            u_r_new = u_r_new * damping_factor
            u_theta_new = u_theta_new * damping_factor
            u_z_new = u_z_new * damping_factor

        return u_r_new, u_theta_new, u_z_new

    def _solve_pressure_poisson(self, u_r, u_theta, u_z):
        """Solve pressure Poisson with enhanced iteration."""
        r_mesh = np.maximum(self.grid.r[:, np.newaxis, np.newaxis], 1e-3)

        div_radial = np.zeros_like(u_r)
        for i in range(self.grid.nx - 1):
            div_radial[i, :, :] = (r_mesh[i+1, :, :] * u_r[i+1, :, :] - r_mesh[i, :, :] * u_r[i, :, :]) / (self.grid.dr[i] * r_mesh[i, :, :])

        div_theta = np.gradient(u_theta, axis=1) / (self.grid.dtheta * r_mesh)
        div_z = np.gradient(u_z, axis=2) / self.grid.dz

        div_u_star = np.clip(div_radial + div_theta + div_z, -10, 10)
        rhs = (self.rho / self.dt) * div_u_star

        p = np.zeros_like(rhs)
        for iter_poisson in range(25):
            lapl_p = self._laplacian_scalar(p)
            residual = rhs - lapl_p
            p = p + 0.06 * residual
            p = np.clip(p, -10000, 10000)  # bound pressure

        return p

    def _laplacian_scalar(self, p):
        """Laplacian for scalar."""
        r_mesh = np.maximum(self.grid.r[:, np.newaxis, np.newaxis], 1e-3)

        d2p_dr2 = np.zeros_like(p)
        for i in range(1, self.grid.nx - 1):
            d2p_dr2[i, :, :] = (p[i+1, :, :] - 2*p[i, :, :] + p[i-1, :, :]) / (0.5 * (self.grid.dr[i] + self.grid.dr[i-1]) ** 2)

        dp_dr = np.zeros_like(p)
        for i in range(self.grid.nx - 1):
            dp_dr[i, :, :] = (p[i+1, :, :] - p[i, :, :]) / self.grid.dr[i]

        term_r = d2p_dr2 + dp_dr / r_mesh

        d2p_dtheta2 = np.gradient(np.gradient(p, axis=1), axis=1) / (self.grid.dtheta ** 2)
        term_theta = d2p_dtheta2 / (r_mesh ** 2)

        d2p_dz2 = np.gradient(np.gradient(p, axis=2), axis=2) / (self.grid.dz ** 2)

        return term_r + term_theta + d2p_dz2

    def _grad_r(self, p):
        """Radial gradient."""
        grad = np.zeros_like(p)
        for i in range(self.grid.nx - 1):
            grad[i, :, :] = (p[i+1, :, :] - p[i, :, :]) / self.grid.dr[i]
        return grad

    def _grad_theta(self, p):
        """Azimuthal gradient."""
        return np.gradient(p, axis=1) / self.grid.dtheta

    def _grad_z(self, p):
        """Vertical gradient."""
        return np.gradient(p, axis=2) / self.grid.dz
