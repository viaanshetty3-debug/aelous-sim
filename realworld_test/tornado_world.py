"""Independent real-world tornado simulator — axisymmetric primitive-variable.

This is a physics engine INDEPENDENT of the AEOLUS solver, used as an external
test bed for AEOLUS's intervention logic. It implements a reduced-order
axisymmetric (r, z) tornado model of the Sullivan / Ward / Fiedler family,
tracking primitive variables (u, v, w, b, q_l, p') on a uniform staggered grid.

Design goals
------------
* Independent code base — not a wrapper around AEOLUS.
* Physically defensible: mass-continuous flow, angular-momentum conservation
  under viscous/friction losses, buoyant convection, precipitation microphysics.
* Scenario-driven: 5 real-storm environmental soundings + stochastic ensembles.
* Robust to intervention forcings from the AEOLUS adapter.

Prognostic variables
--------------------
    u(r, z, t)   radial velocity                 m/s
    v(r, z, t)   tangential velocity             m/s
    w(r, z, t)   vertical velocity               m/s
    b(r, z, t)   buoyancy (g θ'/θ_0)             m/s²
    q_l(r, z, t) liquid-water mixing ratio       g/kg
    p'(r, z, t)  perturbation pressure           Pa   (diagnosed)

Governing equations (axisymmetric, Boussinesq)
----------------------------------------------
    Du/Dt = v²/r  - ∂p'/∂r / ρ + ν ∇²u + S_u
    Dv/Dt = -u v / r          + ν ∇²v - drag  + S_v
    Dw/Dt = -∂p'/∂z / ρ  + b  + ν ∇²w - precip_drag + S_w
    Db/Dt = -N² w  - α q_l    + κ ∇²b + S_b
    Dq_l/Dt = C(w) - P(q_l)
    ∇·u = (1/r)∂(ru)/∂r + ∂w/∂z = 0     -- enforced by pressure projection

Time integration: explicit RK2 for advection/buoyancy, explicit for viscous,
projection step (SOR Poisson) for pressure to satisfy continuity.
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass


# ---------------------------------------------------------------------------
#  Scenario presets (based on published EF-scale environmental soundings)
# ---------------------------------------------------------------------------

@dataclass
class Scenario:
    name: str
    ef_scale: str
    cape: float             # J/kg
    shear_0_1km: float      # m/s
    shear_0_6km: float      # m/s
    lcl_height: float       # m
    rfd_temp_deficit: float # K
    peak_vt_target: float   # m/s
    core_radius: float      # m
    surface_roughness: float
    turb_intensity: float
    inflow_speed: float


SCENARIOS = [
    Scenario("Andover_KS_2022",   "EF3",       2400,15,32,  800, 3.0, 70.0, 350,0.15,0.25,18),
    Scenario("Moore_OK_2013",     "EF5",       4200,22,42,  650, 5.5, 95.0, 520,0.20,0.35,25),
    Scenario("El_Reno_OK_2013",   "EF3-wedge", 3800,18,38,  900, 4.0,135.0,1600,0.10,0.40,22),
    Scenario("Joplin_MO_2011",    "EF5",       3500,19,36,  750, 4.5, 90.0, 600,0.25,0.30,21),
    Scenario("Tuscaloosa_AL_2011","EF4",       2900,17,34, 1000, 3.8, 82.0, 450,0.30,0.28,19),
]


# ---------------------------------------------------------------------------
#  Simulator
# ---------------------------------------------------------------------------

class TornadoWorld:
    G       = 9.81
    THETA_0 = 300.0
    N_SQ    = 1.0e-4
    NU      = 8.0         # m²/s eddy viscosity (tornado-scale)
    KAPPA   = 6.0         # m²/s eddy diffusivity for buoyancy
    ALPHA_PRECIP = 0.1    # (m/s²) per (g/kg)
    CONDENSATION_RATE = 0.02
    PRECIP_RATE = 0.005
    RHO = 1.15

    def __init__(self, scenario: Scenario,
                 nr: int = 80, nz: int = 50,
                 r_max: float = 3000.0, z_top: float = 3000.0,
                 dt: float = 0.25, seed: int = 42):
        self.scn = scenario
        self.nr, self.nz = nr, nz
        self.r_max, self.z_top = r_max, z_top
        self.dt = dt
        self.rng = np.random.default_rng(seed)

        # uniform grid
        self.r = np.linspace(20.0, r_max, nr)   # start off axis to avoid 1/r singularity
        self.z = np.linspace(0.0, z_top, nz)
        self.dr = float(self.r[1] - self.r[0])
        self.dz = float(self.z[1] - self.z[0])
        self.R, self.Z = np.meshgrid(self.r, self.z, indexing="ij")

        # state
        self.u = np.zeros((nr, nz))
        self.v = np.zeros((nr, nz))
        self.w = np.zeros((nr, nz))
        self.b = np.zeros((nr, nz))
        self.q_l = np.zeros((nr, nz))
        self.p  = np.zeros((nr, nz))

        # intervention coupling: momentum sink can attenuate storm maintenance nudge
        self.maintenance_scale = np.ones((nr, nz))

        # history
        self.history = {"t": [], "peak_vt": [], "core_omega": [], "min_p_deficit": [],
                        "ke": [], "circulation_1km": [], "peak_w": [], "peak_u_in": []}

        self._initialize_baseline()

    # ------------------------------------------------------------------
    #  Baseline: quasi-steady tornado + storm-scale updraft
    # ------------------------------------------------------------------

    def _initialize_baseline(self):
        scn = self.scn
        r_c = scn.core_radius
        v_peak = scn.peak_vt_target

        # Burgers-Rott tangential profile normalized so max is exactly v_peak at r=r_c.
        # v(r) = (v_peak/K) * (r_c/r) * (1 - exp(-1.256 (r/r_c)²)),  K = 1 - e^{-1.256} ≈ 0.716
        r_norm = self.R / r_c
        env_r = (1.0 - np.exp(-1.256 * r_norm ** 2))
        K = 1.0 - np.exp(-1.256)
        v_r = (v_peak / K) * (1.0 / np.maximum(r_norm, 0.05)) * env_r
        v_r = np.minimum(v_r, v_peak * 1.02)

        # Vertical envelope: peaks near ground (200 m), decays aloft
        vert = np.exp(-((self.Z - 200.0) / 800.0) ** 2)
        vert = np.clip(vert, 0.15, 1.0)
        self.v = v_r * vert

        # Radial inflow: mass-continuous with updraft mass flux M(z)
        # Storm-scale updraft: peaks at ~1500 m
        z_up = 1500.0
        w_amp = 0.02 * scn.cape  # ~60 m/s at CAPE=3000 (peak in-updraft)
        w_amp = min(w_amp, 45.0)
        w_r = np.exp(-(self.R / (0.6 * r_c)) ** 2) * \
              np.exp(-((self.Z - z_up) / 900.0) ** 2)
        self.w = w_amp * w_r

        # Radial inflow from continuity: (1/r) d(r u)/dr = -dw/dz
        # Solve r*u(r,z) = -∫_0^r r' dw/dz dr'    (approx via cumulative)
        dw_dz = np.gradient(self.w, self.dz, axis=1)
        ru = -np.cumsum(self.R * dw_dz, axis=0) * self.dr
        self.u = ru / np.maximum(self.R, 1.0)
        # inflow strongest in lowest 500 m
        inflow_env = np.exp(-((self.Z - 100.0) / 400.0) ** 2)
        self.u = self.u * (0.3 + 0.7 * inflow_env)
        # cap
        self.u = np.clip(self.u, -0.9 * scn.inflow_speed, 0.5 * scn.inflow_speed)

        # buoyancy: CAPE-consistent warm core
        cape_norm = scn.cape / 3000.0
        self.b = cape_norm * 0.15 * np.exp(-(self.R / (2 * r_c)) ** 2) \
                                  * np.exp(-((self.Z - 1500.0) / 800.0) ** 2)

        # RFD cold pool
        rfd_r0 = 1.5 * r_c
        rfd_z0 = 300.0
        self.b += (-scn.rfd_temp_deficit * self.G / self.THETA_0) * \
                  np.exp(-((self.R - rfd_r0) / (0.6 * r_c)) ** 2
                         -((self.Z - rfd_z0) / 400.0) ** 2)

        # liquid water — cloud around updraft
        self.q_l = 4.0 * np.exp(-(self.R / (3 * r_c)) ** 2) \
                       * np.exp(-((self.Z - 1200.0) / 700.0) ** 2)

        # turbulent perturbations
        pert = self.rng.standard_normal(self.u.shape) * scn.turb_intensity
        self.u += 0.5 * pert
        self.v += 0.3 * pert
        self.w += 0.3 * pert
        self.b += 0.003 * pert

        # initial pressure from cyclostrophic balance: dp/dr ~ ρ v²/r
        rho = self.RHO
        integrand = rho * self.v ** 2 / np.maximum(self.R, 1.0)
        # integrate from r_max inward
        p_col = -np.cumsum(integrand[::-1, :], axis=0)[::-1] * self.dr
        self.p = p_col
        # add hydrostatic buoyancy contribution
        self.p -= rho * np.cumsum(self.b, axis=1) * self.dz

        # Enforce mass continuity via one pressure-projection step
        self._pressure_project()

    # ------------------------------------------------------------------
    #  Time step
    # ------------------------------------------------------------------

    def step(self, intervention_forcings=None):
        if intervention_forcings is None:
            intervention_forcings = {}
        # Convert AEOLUS-style forcings to primitive-var sources.
        # S_eta targeting azimuthal vorticity translates roughly to a Δv source
        # via η_φ = ∂u/∂z - ∂w/∂r (we don't invert exactly, but couple as small tendency)
        S_u = intervention_forcings.get("S_u", np.zeros_like(self.u))
        S_v = intervention_forcings.get("S_v", np.zeros_like(self.v))
        S_w = intervention_forcings.get("S_w", np.zeros_like(self.w))
        S_b = intervention_forcings.get("S_b", np.zeros_like(self.b))

        # ---- RK2 predictor step
        u0, v0, w0, b0, q0 = self.u.copy(), self.v.copy(), self.w.copy(), self.b.copy(), self.q_l.copy()
        du1, dv1, dw1, db1, dq1 = self._rhs(u0, v0, w0, b0, q0, S_u, S_v, S_w, S_b)
        u_m = u0 + 0.5 * self.dt * du1
        v_m = v0 + 0.5 * self.dt * dv1
        w_m = w0 + 0.5 * self.dt * dw1
        b_m = b0 + 0.5 * self.dt * db1
        q_m = q0 + 0.5 * self.dt * dq1

        # ---- corrector
        du2, dv2, dw2, db2, dq2 = self._rhs(u_m, v_m, w_m, b_m, q_m, S_u, S_v, S_w, S_b)
        self.u = u0 + self.dt * du2
        self.v = v0 + self.dt * dv2
        self.w = w0 + self.dt * dw2
        self.b = b0 + self.dt * db2
        self.q_l = q0 + self.dt * dq2

        # bounds and BCs
        self._apply_bc()
        self._clip_state()

        # pressure projection to enforce continuity
        self._pressure_project()

    def _rhs(self, u, v, w, b, q_l, S_u, S_v, S_w, S_b):
        R = np.maximum(self.R, 1.0)

        # advection (upwind)
        du = -self._adv(u, u, w) + v ** 2 / R + self.NU * self._lap(u) + S_u
        dv = -self._adv(v, u, w) - u * v / R  + self.NU * self._lap(v) - self._surf_drag(v) + S_v
        dw = -self._adv(w, u, w) + b - self.ALPHA_PRECIP * q_l * 0.1 \
             + self.NU * self._lap(w) + S_w
        db_dt = -self._adv(b, u, w) - self.N_SQ * w - self.ALPHA_PRECIP * q_l \
                + self.KAPPA * self._lap(b) + S_b
        # microphysics
        condensation = self.CONDENSATION_RATE * np.maximum(w - 0.3, 0.0) * 2.0
        precip = self.PRECIP_RATE * q_l
        dq = -self._adv(q_l, u, w) + condensation - precip

        return du, dv, dw, db_dt, dq

    def _adv(self, f, u, w):
        # first-order upwind
        f_r = np.where(u > 0,
                       (f - np.roll(f, 1, axis=0)) / self.dr,
                       (np.roll(f, -1, axis=0) - f) / self.dr)
        f_z = np.where(w > 0,
                       (f - np.roll(f, 1, axis=1)) / self.dz,
                       (np.roll(f, -1, axis=1) - f) / self.dz)
        return u * f_r + w * f_z

    def _lap(self, f):
        d2r = (np.roll(f, -1, axis=0) - 2*f + np.roll(f, 1, axis=0)) / self.dr**2
        d2z = (np.roll(f, -1, axis=1) - 2*f + np.roll(f, 1, axis=1)) / self.dz**2
        return d2r + d2z

    def _surf_drag(self, v):
        z0 = self.scn.surface_roughness
        drag = np.zeros_like(v)
        n_drag = min(8, self.nz)
        for j in range(n_drag):
            z_j = max(self.z[j], 10.0 * z0)   # keep log argument > 10 to bound cd
            cd = (0.4 / np.log(z_j / z0)) ** 2
            cd = min(cd, 0.02)                 # cap drag coefficient
            drag[:, j] = cd * v[:, j] * np.abs(v[:, j]) / max(self.dz * 3.0, 1.0)
        return drag

    def _apply_bc(self):
        # axis (r=0-like): u=0, v=0 for symmetry
        self.u[0, :] = 0.0
        self.v[0, :] *= 0.2

        # Far-field lateral forcing: hold environmental inflow + storm-scale
        # updraft near the domain edge. This mimics the parent supercell
        # supplying the tornado with angular momentum and mass flux.
        inflow_prof = -self.scn.inflow_speed * \
                      np.exp(-((self.z - 200.0) / 400.0) ** 2)
        self.u[-1, :] = 0.5 * self.u[-1, :] + 0.5 * inflow_prof
        env_v = 0.6 * self.scn.peak_vt_target * self.scn.core_radius / self.r_max
        self.v[-1, :] = 0.7 * self.v[-1, :] + 0.3 * env_v * \
                        np.exp(-((self.z - 200.0) / 500.0) ** 2)
        self.b[-1, :] *= 0.99
        # ground: w=0
        self.w[:, 0] = 0.0
        # top: w matches near-top value (free-slip ∂w/∂z=0)
        self.w[:, -1] = self.w[:, -2] * 0.9

        # Storm maintenance: nudge core-region v_θ toward a target derived from
        # the parent-storm environment. τ ~ 10 s — interventions must overcome it.
        r_c = self.scn.core_radius
        z_target = np.exp(-((self.z - 200.0) / 800.0) ** 2)
        # Bell-shaped radial target profile centered at r_c
        r_target = np.exp(-((self.r - r_c) / (0.8 * r_c)) ** 2)
        target_v = self.scn.peak_vt_target * r_target[:, None] * z_target[None, :] * 0.95
        nudge_rate = 0.1
        maintenance_mask = np.exp(-((self.R - r_c) / (1.5 * r_c)) ** 2) * \
                           (self.Z < 1500.0).astype(float)
        self.v = self.v + self.dt * nudge_rate * (target_v - self.v) * maintenance_mask * self.maintenance_scale

    def _clip_state(self):
        self.u = np.clip(self.u, -60.0, 60.0)
        self.v = np.clip(self.v, -150.0, 150.0)
        self.w = np.clip(self.w, -50.0, 80.0)
        self.b = np.clip(self.b, -0.5, 0.5)
        self.q_l = np.clip(self.q_l, 0.0, 15.0)

    # ------------------------------------------------------------------
    #  Pressure projection (SOR Poisson for divergence)
    # ------------------------------------------------------------------

    def _pressure_project(self):
        """Solve ∇²φ = ρ/dt · div(u), then u -= dt/ρ · ∇φ.

        Vectorized Jacobi (~80 sweeps).
        """
        R = np.maximum(self.R, 1.0)
        ru = self.R * self.u
        div_r = np.gradient(ru, self.dr, axis=0) / R
        div_z = np.gradient(self.w, self.dz, axis=1)
        div = div_r + div_z

        rhs = (self.RHO / max(self.dt, 1e-6)) * div
        phi = np.zeros_like(self.p)

        dr2, dz2 = self.dr ** 2, self.dz ** 2
        denom = 2.0 / dr2 + 2.0 / dz2

        for _ in range(60):
            phi_r_p = np.roll(phi,  1, axis=0)
            phi_r_m = np.roll(phi, -1, axis=0)
            phi_z_p = np.roll(phi,  1, axis=1)
            phi_z_m = np.roll(phi, -1, axis=1)
            val = ((phi_r_p + phi_r_m) / dr2
                 + (phi_z_p + phi_z_m) / dz2
                 + (phi_r_m - phi_r_p) / (2 * self.dr * R)
                 - rhs) / denom
            phi_new = 0.5 * phi + 0.5 * val
            # Neumann BCs (zero-gradient)
            phi_new[0, :]  = phi_new[1, :]
            phi_new[-1, :] = phi_new[-2, :]
            phi_new[:, 0]  = phi_new[:, 1]
            phi_new[:, -1] = phi_new[:, -2]
            phi = phi_new

        dphi_dr = np.gradient(phi, self.dr, axis=0)
        dphi_dz = np.gradient(phi, self.dz, axis=1)
        self.u -= (self.dt / self.RHO) * dphi_dr
        self.w -= (self.dt / self.RHO) * dphi_dz
        self.p += phi

    # ------------------------------------------------------------------
    #  Diagnostics
    # ------------------------------------------------------------------

    def diagnose_metrics(self, t):
        peak_vt = float(np.max(np.abs(self.v)))
        rv = self.R * self.v
        omega_z = np.gradient(rv, self.dr, axis=0) / np.maximum(self.R, 1.0)
        z_mask = self.Z < 500.0
        r_mask = self.R < self.scn.core_radius
        mask = z_mask & r_mask
        core_omega = float(np.mean(omega_z[mask]))
        # cyclostrophic pressure deficit at 100 m
        j_100 = int(min(4, self.nz-1))
        v_100 = self.v[:, j_100]
        dp = float(-self.RHO * np.sum(v_100 ** 2 / np.maximum(self.r, 1.0)) * self.dr)
        # kinetic energy in bottom 1 km (axisymmetric integral)
        z_1km = self.Z < 1000.0
        u_mag_sq = self.u ** 2 + self.v ** 2 + self.w ** 2
        ke = float(0.5 * self.RHO * np.sum(u_mag_sq * z_1km * self.R * self.dr * self.dz) * 2 * np.pi)
        # circulation at core_radius, z ~ 100 m
        i_c = int(np.argmin(np.abs(self.r - self.scn.core_radius)))
        circ_1km = float(2 * np.pi * self.r[i_c] * self.v[i_c, j_100])
        peak_w = float(np.max(self.w))
        peak_u_in = float(np.min(self.u))

        self.history["t"].append(t)
        self.history["peak_vt"].append(peak_vt)
        self.history["core_omega"].append(core_omega)
        self.history["min_p_deficit"].append(dp)
        self.history["ke"].append(ke)
        self.history["circulation_1km"].append(circ_1km)
        self.history["peak_w"].append(peak_w)
        self.history["peak_u_in"].append(peak_u_in)
        return {"t": t, "peak_vt": peak_vt, "core_omega": core_omega,
                "min_p_deficit": dp, "ke": ke, "circ_1km": circ_1km,
                "peak_w": peak_w, "peak_u_in": peak_u_in}
