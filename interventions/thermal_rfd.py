"""Dynamic Thermodynamic RFD intervention: realistic thermal perturbation decay."""

import numpy as np


class ThermalRFDIntervention:
    """Inject and decay localized buoyancy to disrupt RFD circulation.

    Uses dynamic temperature envelope that realistically decays via:
    - Convective transport (carried upward)
    - Diffusive mixing (lateral spreading)
    - Time-dependent strength modulation
    """

    def __init__(
        self,
        grid,
        injection_z_frac: float = 0.7,
        injection_r_scale: float = 1.5,
        peak_anomaly: float = 4.0,
        t_ref: float = 288.0,
        active_duration_steps: int = 40,
        decay_duration_steps: int = 40,
        duration_steps: int = None,
        g: float = 9.81,
    ):
        """Initialize dynamic thermal RFD intervention.

        Args:
            grid: CylindricalGrid instance
            injection_z_frac: normalized z-level for injection (0-1)
            injection_r_scale: radial extent (multiple of 500m core radius)
            peak_anomaly: peak temperature perturbation (K)
            t_ref: reference temperature (K)
            active_duration_steps: steps of full-strength injection
            decay_duration_steps: steps of decay after active period
            duration_steps: optional alias for total duration
            g: gravitational acceleration (m/s²)
        """
        self.grid = grid
        self.injection_z_frac = injection_z_frac
        self.injection_r_scale = injection_r_scale
        self.peak_anomaly = peak_anomaly
        self.t_ref = t_ref
        if duration_steps is not None:
            self.active_duration = duration_steps
            self.decay_duration = 0
        else:
            self.active_duration = active_duration_steps
            self.decay_duration = decay_duration_steps
        self.total_duration = self.active_duration + self.decay_duration
        self.g = g

        # Diffusion parameter for envelope spread
        self.diffusion_scale = 1.2  # increases effective size with time

    def _temperature_envelope(self, step: int):
        """Dynamic temperature envelope with realistic decay.

        Phase 1 (0 to active_duration): Constant source at peak
        Phase 2 (active_duration to total_duration): Exponential decay with diffusion

        Returns:
            Multiplier for current temperature anomaly (0 to 1)
        """
        if step >= self.total_duration:
            return 0.0

        if step < self.active_duration:
            # Active injection phase
            return 1.0
        else:
            # Decay phase: exponential decay with diffusion broadening
            decay_step = step - self.active_duration
            decay_fraction = decay_step / self.decay_duration
            # Exponential decay: e^(-2*t)
            decay_exp = np.exp(-2.0 * decay_fraction)
            # Diffusion broadening (strength decreases, area increases)
            # Effective anomaly = initial * exp(-decay) to simulate transport
            return decay_exp * (1.0 - 0.3 * decay_fraction)  # slower than pure decay

    def _convection_transport(self, step: int):
        """Vertical rise rate of thermal plume due to buoyancy.

        As buoyant air rises, injection center shifts upward.

        Returns:
            Vertical displacement (m) from original injection height
        """
        if step >= self.total_duration:
            return 0.0

        # Rise velocity ~0.3 m/s (based on buoyancy)
        rise_velocity = 0.3 * self.peak_anomaly / self.t_ref  # m/s
        displacement = rise_velocity * step * 0.15  # approximate

        # Cap displacement at domain height
        return min(displacement, 0.4 * self.grid.z_max)

    def apply(self, u_r, u_theta, u_z, p, step: int):
        """Apply dynamic thermal perturbation with realistic evolution.

        Mechanism:
        1. Localized heat injection → positive ΔT
        2. Buoyancy: b = g·ΔT/T_ref → upward acceleration
        3. Thermal plume rises and diffuses
        4. Strength decays exponentially

        Args:
            u_r, u_theta, u_z: velocity components
            p: pressure
            step: current time step

        Returns:
            Modified u_r, u_theta, u_z, p
        """
        if step > self.total_duration:
            return u_r, u_theta, u_z, p

        # Get current envelope strength and convective displacement
        envelope = self._temperature_envelope(step)
        displacement = self._convection_transport(step)

        if envelope < 1e-6:
            return u_r, u_theta, u_z, p

        # Injection location (shifts upward due to convection)
        z_inject_base = self.injection_z_frac * self.grid.z_max
        z_inject = min(z_inject_base + displacement, self.grid.z_max - 100)
        r_inject = self.injection_r_scale * 500.0  # nominal 500m core radius

        # Envelope spatial extent (expands with time)
        time_factor = (step / max(1, self.total_duration)) if self.total_duration > 0 else 0
        sigma_r = r_inject / 2.5 * (1.0 + 0.3 * time_factor)  # radial diffusion
        sigma_z = self.grid.z_max / 8.0 * (1.0 + 0.5 * time_factor)  # vertical diffusion

        # Create mesh
        r_mesh, theta_mesh, z_mesh = np.meshgrid(
            self.grid.r, self.grid.theta, self.grid.z, indexing="ij"
        )

        # Gaussian spatial distribution (envelope)
        r_dist = r_mesh
        z_dist = np.abs(z_mesh - z_inject)

        spatial_mask = np.exp(
            -(r_dist ** 2) / (2 * sigma_r ** 2)
            - (z_dist ** 2) / (2 * sigma_z ** 2)
        )

        # Temperature anomaly with envelope and decay
        current_anomaly = self.peak_anomaly * envelope

        # Buoyancy acceleration: b = g·ΔT/T_ref
        buoyancy_accel = self.g * current_anomaly / self.t_ref

        # Apply buoyancy directly to vertical momentum
        u_z_increment = spatial_mask * buoyancy_accel * 0.3  # conservative coupling

        u_z = u_z + u_z_increment

        # Secondary effect: turbulence/mixing enhancement in active phase
        if step < self.active_duration:
            # Enhanced diffusion in plume region
            diffusion_boost = 0.15 * spatial_mask
            u_r = u_r * (1.0 + 0.1 * diffusion_boost)
            u_theta = u_theta * (1.0 + 0.05 * diffusion_boost)

        return u_r, u_theta, u_z, p

    def compute_buoyancy_field(self, step: int):
        """Compute buoyancy field for diagnostics."""
        if step > self.total_duration:
            return np.zeros((self.grid.nx, self.grid.ntheta, self.grid.nz))

        envelope = self._temperature_envelope(step)
        displacement = self._convection_transport(step)

        if envelope < 1e-6:
            return np.zeros((self.grid.nx, self.grid.ntheta, self.grid.nz))

        z_inject_base = self.injection_z_frac * self.grid.z_max
        z_inject = min(z_inject_base + displacement, self.grid.z_max - 100)
        r_inject = self.injection_r_scale * 500.0

        time_factor = (step / max(1, self.total_duration)) if self.total_duration > 0 else 0
        sigma_r = r_inject / 2.5 * (1.0 + 0.3 * time_factor)
        sigma_z = self.grid.z_max / 8.0 * (1.0 + 0.5 * time_factor)

        r_mesh, _, z_mesh = np.meshgrid(
            self.grid.r, self.grid.theta, self.grid.z, indexing="ij"
        )

        r_dist = r_mesh
        z_dist = np.abs(z_mesh - z_inject)

        spatial_mask = np.exp(
            -(r_dist ** 2) / (2 * sigma_r ** 2)
            - (z_dist ** 2) / (2 * sigma_z ** 2)
        )

        current_anomaly = self.peak_anomaly * envelope
        buoyancy_accel = self.g * current_anomaly / self.t_ref

        return spatial_mask * buoyancy_accel * 0.3
