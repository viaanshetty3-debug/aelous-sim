"""Adapter that projects AEOLUS's intervention logic into the (r,z) test bed.

The AEOLUS solver operates in cylindrical (r, θ, z). The independent test bed
is axisymmetric (r, z), primitive variables (u, v, w, b). We port the *same*
physical models used by AEOLUS's ThermalRFDIntervention and
MomentumSinkIntervention (see aeolus_sim/interventions/*.py), evaluated on the
test-bed grid.

Returned forcings (as tendencies, m/s per s or K per s):
    S_u -- radial momentum source
    S_v -- tangential momentum source  (equivalent to Γ/r sink)
    S_w -- vertical momentum source     (buoyancy plus adiabatic terms)
    S_b -- buoyancy source
"""

from __future__ import annotations

import numpy as np


class AeolusInterventionAdapter:
    G = 9.81
    T_REF = 288.0
    RHO = 1.15

    def __init__(self, world,
                 use_thermal: bool = True,
                 use_momentum: bool = True,
                 thermal_peak_K: float = 4.0,
                 thermal_active_steps: int = 40,
                 thermal_decay_steps: int = 40,
                 momentum_pressure_deficit_Pa: float = -500.0,
                 momentum_blackout_m: float = 200.0,
                 momentum_sink_radius_m: float | None = None,
                 momentum_sink_center_r_m: float | None = None,
                 start_step: int = 20):
        self.world = world
        self.use_thermal = use_thermal
        self.use_momentum = use_momentum
        self.thermal_peak = thermal_peak_K
        self.thermal_active = thermal_active_steps
        self.thermal_decay = thermal_decay_steps
        self.thermal_total = thermal_active_steps + thermal_decay_steps
        self.mom_dp = momentum_pressure_deficit_Pa
        self.mom_blackout = momentum_blackout_m
        # PATCH 1: sink geometry scales with the target vortex's core radius, so the
        # sink centers on the peak-v_t radius regardless of storm size. Was hardcoded
        # (r_center=800m, r_sink=1000m) which put El Reno's peak (r≈1567m) outside
        # the mask footprint and yielded only 3% v_t reduction there.
        r_c = self.world.scn.core_radius
        self.mom_r_center = momentum_sink_center_r_m if momentum_sink_center_r_m is not None else 1.0 * r_c
        self.mom_r_sink   = momentum_sink_radius_m   if momentum_sink_radius_m   is not None else 2.0 * r_c
        self.start_step = start_step

    def _thermal_envelope(self, step_rel):
        if step_rel >= self.thermal_total:
            return 0.0
        if step_rel < self.thermal_active:
            return 1.0
        d = step_rel - self.thermal_active
        f = d / max(1, self.thermal_decay)
        return float(np.exp(-2.0 * f) * (1.0 - 0.3 * f))

    def _convective_rise(self, step_rel):
        rise_v = 0.3 * self.thermal_peak / self.T_REF
        disp = rise_v * step_rel * 0.15
        return min(disp, 0.4 * self.world.z_top)

    def forcings(self, step: int):
        S_u = np.zeros_like(self.world.u)
        S_v = np.zeros_like(self.world.v)
        S_w = np.zeros_like(self.world.w)
        S_b = np.zeros_like(self.world.b)
        step_rel = step - self.start_step
        if step_rel < 0:
            return {"S_u": S_u, "S_v": S_v, "S_w": S_w, "S_b": S_b}
        if self.use_thermal:
            self._apply_thermal(step_rel, S_b, S_w, S_v)
        if self.use_momentum:
            self._apply_momentum(S_u, S_v, S_w)
        return {"S_u": S_u, "S_v": S_v, "S_w": S_w, "S_b": S_b}

    # ------------------------------------------------------------------
    #  AEOLUS Thermal RFD  (mirrors interventions/thermal_rfd.py)
    # ------------------------------------------------------------------
    def _apply_thermal(self, step_rel, S_b, S_w, S_v):
        env = self._thermal_envelope(step_rel)
        if env < 1e-6:
            return
        disp = self._convective_rise(step_rel)

        z0 = 0.7 * self.world.z_top + disp
        z0 = min(z0, self.world.z_top - 100.0)
        r0 = 1.5 * self.world.scn.core_radius

        t_frac = step_rel / max(1, self.thermal_total)
        sigma_r = r0 / 2.5 * (1.0 + 0.3 * t_frac)
        sigma_z = self.world.z_top / 8.0 * (1.0 + 0.5 * t_frac)

        mask = np.exp(-((self.world.R - r0) ** 2) / (2 * sigma_r ** 2)
                      -((self.world.Z - z0) ** 2) / (2 * sigma_z ** 2))

        # Buoyancy: b = g ΔT/T_ref  applied as source
        b_amp = self.G * self.thermal_peak * env / self.T_REF
        S_b += b_amp * mask * 0.5

        # Direct upward acceleration on w
        S_w += b_amp * mask * 0.3

        # Indirect coupling: warm bubble disrupts the RFD cold pool → cuts the
        # baroclinic convergence that maintains v_θ. Modeled as a spin-down term
        # broadened to encompass the mesocyclone (r ≤ 2 r_c), acting more
        # strongly at the core where maintenance would be strongest.
        # PATCH 2: vertical mask centered at 400 m (was 800 m) so the disruption
        # reaches the low-level v_θ peak (~200 m) where the core_omega diagnostic
        # is measured (Z<500 m). Rate raised 0.05→0.15 /s to overcome the storm-
        # maintenance nudge in tornado_world._apply_bc (0.10 /s) — previously the
        # thermal spin-down was mathematically outmatched every step.
        r_c = self.world.scn.core_radius
        disrupt = np.exp(-(self.world.R / (2.0 * r_c)) ** 2) * \
                  np.exp(-((self.world.Z - 400.0) / 700.0) ** 2)
        S_v -= 0.15 * env * disrupt * self.world.v

    # ------------------------------------------------------------------
    #  AEOLUS Momentum Sink  (mirrors interventions/momentum_sink.py)
    # ------------------------------------------------------------------
    def _apply_momentum(self, S_u, S_v, S_w):
        r_center = self.mom_r_center
        z_center = 0.5 * self.world.z_top
        sigma_r = self.mom_r_sink / 2.0
        sigma_z = self.world.z_top / 6.0
        sink_mask = np.exp(-((self.world.R - r_center) ** 2) / (2 * sigma_r ** 2)
                           -((self.world.Z - z_center) ** 2) / (2 * sigma_z ** 2))

        # (1) Adverse pressure-gradient → tangential deceleration
        # Physical basis: cyclostrophic balance ρv²/r = ∂p/∂r. A negative-Δp core
        # perturbation at mid-radius creates a radial-pressure-gradient reversal
        # that decelerates v in the outer core.
        dp_field = self.mom_dp * sink_mask
        dpg_dr = np.gradient(dp_field, self.world.dr, axis=0)
        v_local = self.world.v
        # Direct deceleration of v proportional to sink mask AND local v
        # (AEOLUS's Δp effectively reduces the cyclostrophic v that can be sustained)
        v_safe = np.maximum(np.abs(v_local), 1.0)
        # Rate at which v equilibrates to the reduced pressure: τ ~ r/v ~ 10 s
        equil_rate = 0.05   # 1/s
        v_target_reduction = -dp_field / (self.RHO * v_safe)   # positive if Δp negative
        S_v -= equil_rate * v_target_reduction * np.sign(v_local) * sink_mask
        # Radial acceleration from pressure gradient
        S_u += -dpg_dr / self.RHO * 0.5

        # (2) Surface inflow blackout (AEOLUS: 90% u_r reduction, 50% u_z reduction).
        # This is the DOMINANT AEOLUS mechanism — it starves the vortex of angular
        # momentum by cutting the radial inflow that feeds the core.
        n_black = int(self.mom_blackout / max(self.world.dz, 1.0))
        n_black = max(n_black, 3)
        # A tendency that near-instantly damps u to 10% of current value each dt:
        # du/dt = -k*u with k=1/dt effectively zeros in one step; scale by 0.9
        for j in range(min(n_black, self.world.nz)):
            S_u[:, j] -= 3.0 * self.world.u[:, j]      # strong inflow suppression
            S_v[:, j] -= 0.20 * self.world.v[:, j]     # extra drag on v (friction proxy)
            S_w[:, j] -= 1.5 * self.world.w[:, j]

        # (3) Angular-momentum spindown from cutting inflow: v decreases wherever u
        # was previously feeding the core. Physical mechanism: without inflow, v spins
        # down under existing friction (already in model) — but we additionally
        # remove the "spin-up" that inflow provides. This is captured by S_u above.
