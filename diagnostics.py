"""Diagnostics: vorticity tracking, reformation detection, conservation checks."""

import numpy as np


class Diagnostics:
    """Compute and track flow diagnostics for vortex disruption analysis."""

    def __init__(self, grid, baseline_vorticity: float = None):
        """Initialize diagnostics.

        Args:
            grid: CylindricalGrid instance
            baseline_vorticity: reference vorticity for reduction metric
        """
        self.grid = grid
        self.baseline_vorticity = baseline_vorticity or 2.0  # default: ~1 rev/30s
        self.history = {}

    def compute(self, u_r, u_theta, u_z, p, step: int) -> dict:
        """Compute diagnostics at current time step.

        Args:
            u_r, u_theta, u_z: velocity components (shape: nx, ntheta, nz)
            p: pressure (shape: nx, ntheta, nz)
            step: time step index

        Returns:
            Dictionary of diagnostic metrics
        """
        metrics = {}

        # (1) Core vorticity: ω_z = (1/r)·∂(r·u_θ)/∂r
        vorticity_z = self._vorticity_z(u_r, u_theta)
        mid_z = len(self.grid.z) // 2
        core_r_idx, core_theta_idx = self._find_vortex_center(vorticity_z[:, :, mid_z])
        metrics["core_vorticity"] = float(vorticity_z[core_r_idx, core_theta_idx, mid_z])

        # (2) Peak vorticity
        metrics["peak_vorticity"] = float(np.max(np.abs(vorticity_z)))

        # (3) Maximum tangential velocity
        metrics["max_velocity"] = float(np.max(np.abs(u_theta)))

        # (4) Circulation (∮ u_θ·r dθ around a circle at mid-radius)
        metrics["circulation"] = self._circulation(u_theta)

        # (5) Radial inflow (diagnostic: should be small)
        metrics["mean_radial_inflow"] = float(np.mean(np.abs(u_r)))

        # (6) Mass residual (divergence check)
        metrics["divergence_rms"] = self._divergence_rms(u_r, u_theta, u_z)

        # (7) Kinetic energy
        metrics["kinetic_energy"] = self._kinetic_energy(u_r, u_theta, u_z)

        # (8) Vorticity reduction (%) - protect against spin reversal and grid displacement
        abs_initial = abs(self.baseline_vorticity)
        abs_final = abs(metrics["core_vorticity"])
        if abs_initial > 1e-6:
            reduction = ((abs_initial - abs_final) / abs_initial) * 100.0
        else:
            reduction = 0.0
        metrics["vorticity_reduction_pct"] = float(max(0.0, min(100.0, reduction)))

        # Store in history
        for key, val in metrics.items():
            if key not in self.history:
                self.history[key] = []
            self.history[key].append((step, val))

        return metrics

    def _vorticity_z(self, u_r, u_theta):
        """Vertical vorticity: ω_z = (1/r)·∂(r·u_θ)/∂r - (1/r)·∂u_r/∂θ.

        In cylindrical coords, primary term is radial derivative of azimuthal momentum.
        """
        r_mesh = self.grid.r[:, np.newaxis, np.newaxis]
        r_safe = np.maximum(r_mesh, 1e-3)

        # Primary term: (1/r)·d(r·u_θ)/dr
        r_u_theta = r_mesh * u_theta

        # Compute radial derivative manually (linear interpolation to grid points)
        d_rutheta_dr = np.zeros_like(r_u_theta)
        for i in range(self.grid.nx - 1):
            d_rutheta_dr[i, :, :] = (r_u_theta[i+1, :, :] - r_u_theta[i, :, :]) / self.grid.dr[i]
        d_rutheta_dr[-1, :, :] = d_rutheta_dr[-2, :, :]  # extend last value

        term1 = d_rutheta_dr / r_safe

        # Secondary term: -(1/r)·∂u_r/∂θ
        du_r_dtheta = np.gradient(u_r, axis=1) / self.grid.dtheta
        term2 = -du_r_dtheta / r_safe

        omega_z = term1 + term2
        return omega_z

    def _find_vortex_center(self, vorticity_2d):
        """Dynamically locate vortex peak center in 2D vorticity field.

        Args:
            vorticity_2d: 2D vorticity field at mid-height (shape: nx, ntheta)

        Returns:
            Tuple (core_r_idx, core_theta_idx) of vortex center location
        """
        # Find peak vorticity magnitude
        abs_vorticity = np.abs(vorticity_2d)

        # Exclude inner edge (near singularity at r=0) and outer edge
        # Search in reasonable vortex core region (typically 1/8 to 1/3 of domain radius)
        r_min_idx = max(1, len(self.grid.r) // 8)
        r_max_idx = min(len(self.grid.r), len(self.grid.r) // 2)

        search_region = abs_vorticity[r_min_idx:r_max_idx, :]

        # Find peak vorticity in search region
        peak_idx_flat = np.argmax(search_region)
        peak_r_idx, peak_theta_idx = np.unravel_index(peak_idx_flat, search_region.shape)

        # Adjust to global indices
        core_r_idx = r_min_idx + peak_r_idx
        core_theta_idx = peak_theta_idx

        return int(core_r_idx), int(core_theta_idx)

    def _circulation(self, u_theta):
        """Compute circulation Γ = ∮ u_θ·r dθ at mid-radius, mid-height.

        Returns:
            circulation (m²/s)
        """
        mid_r = len(self.grid.r) // 2
        mid_z = len(self.grid.z) // 2
        r_val = self.grid.r[mid_r]
        u_theta_profile = u_theta[mid_r, :, mid_z]
        circulation = np.sum(u_theta_profile) * self.grid.dtheta * r_val
        return float(circulation)

    def _divergence_rms(self, u_r, u_theta, u_z):
        """Compute RMS divergence: ∇·u = (1/r)·∂(r·u_r)/∂r + (1/r)·∂u_θ/∂θ + ∂u_z/∂z.

        Should remain small for incompressible solver.
        """
        r_mesh = self.grid.r[:, np.newaxis, np.newaxis]
        r_safe = np.maximum(r_mesh, 1e-3)

        # Radial divergence: (1/r)·d(r·u_r)/dr
        r_u_r = r_mesh * u_r
        d_rur_dr = np.zeros_like(r_u_r)
        for i in range(self.grid.nx - 1):
            d_rur_dr[i, :, :] = (r_u_r[i+1, :, :] - r_u_r[i, :, :]) / self.grid.dr[i]
        d_rur_dr[-1, :, :] = d_rur_dr[-2, :, :]

        div_r = d_rur_dr / r_safe

        # Azimuthal divergence: (1/r)·∂u_θ/∂θ
        du_theta_dtheta = np.gradient(u_theta, axis=1) / self.grid.dtheta
        div_theta = du_theta_dtheta / r_safe

        # Vertical divergence: ∂u_z/∂z
        du_z_dz = np.gradient(u_z, axis=2) / self.grid.dz
        div_z = du_z_dz

        div_total = div_r + div_theta + div_z
        rms_div = float(np.sqrt(np.mean(div_total ** 2)))

        return rms_div

    def _kinetic_energy(self, u_r, u_theta, u_z):
        """Integrate kinetic energy: KE = (1/2)ρ ∫∫∫ |u|² dV.

        Volume element: dV = r dr dθ dz
        """
        rho = 1.225  # kg/m³
        u_mag_sq = u_r ** 2 + u_theta ** 2 + u_z ** 2

        # Weight by Jacobian (r) and integrate
        ke_total = 0.0
        for i in range(self.grid.nx - 1):
            r_avg = 0.5 * (self.grid.r[i] + self.grid.r[i+1])
            dr = self.grid.dr[i]
            u_mag_sq_avg = 0.5 * (u_mag_sq[i, :, :] + u_mag_sq[i+1, :, :])
            dv_element = r_avg * dr * self.grid.dtheta * self.grid.dz
            ke_total += np.sum(u_mag_sq_avg) * dv_element

        ke = 0.5 * rho * ke_total
        return float(ke)

    def vorticity_reduction(self) -> float:
        """Compute vorticity reduction from baseline (%).

        Uses absolute values to protect against spin reversal and grid displacement.

        Returns:
            Reduction percentage (0-100, capped at 100%)
        """
        if "core_vorticity" not in self.history or len(self.history["core_vorticity"]) == 0:
            return 0.0
        final_vorticity = self.history["core_vorticity"][-1][1]
        abs_initial = abs(self.baseline_vorticity)
        abs_final = abs(final_vorticity)
        if abs_initial > 1e-6:
            reduction = ((abs_initial - abs_final) / abs_initial) * 100.0
        else:
            reduction = 0.0
        return max(0.0, min(100.0, reduction))

    def check_reformation(self, threshold_pct: float = 20.0) -> bool:
        """Check if vortex is reforming post-intervention.

        Reformation = magnitude increase > threshold after reaching minimum.
        Uses absolute values to protect against spin reversal.

        Args:
            threshold_pct: threshold increase (%) to flag reformation

        Returns:
            True if reformation detected
        """
        if "core_vorticity" not in self.history or len(self.history["core_vorticity"]) < 10:
            return False

        vorticities = np.array([v[1] for v in self.history["core_vorticity"]])
        abs_vorticities = np.abs(vorticities)
        min_vort_mag = np.min(abs_vorticities)
        min_idx = np.argmin(abs_vorticities)

        # Check second half of time series
        if min_idx < len(abs_vorticities) // 2:
            return False

        later_vort_mags = abs_vorticities[min_idx:]
        abs_baseline = abs(self.baseline_vorticity)
        increase_pct = 100.0 * (np.max(later_vort_mags) - min_vort_mag) / (abs_baseline + 1e-6)

        return increase_pct > threshold_pct

    def print_summary(self, step: int):
        """Print diagnostic summary at current step."""
        if "core_vorticity" not in self.history:
            return

        history = self.history
        vort = history["core_vorticity"][-1][1] if history["core_vorticity"] else 0.0
        vel = history["max_velocity"][-1][1] if history["max_velocity"] else 0.0
        ke = history["kinetic_energy"][-1][1] if history["kinetic_energy"] else 0.0
        red = history["vorticity_reduction_pct"][-1][1] if "vorticity_reduction_pct" in history else 0.0

        print(f"Step {step:4d} | ω_core={vort:7.2f} 1/s | u_max={vel:6.2f} m/s | "
              f"KE={ke:9.1f} J | Reduction={red:5.1f}%")
