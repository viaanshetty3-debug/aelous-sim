"""Axisymmetric incompressible tornado model (r, z) with swirl.

Equations (Boussinesq, constant eddy viscosity ν and diffusivity κ, no θ-dependence):

    Du/Dt = v²/r − ∂π/∂r + ν(∇²u − u/r²) + F_r
    DM/Dt = (ν/r) ∂/∂r( r³ ∂/∂r(M/r²) ) + ν ∂²M/∂z²        (M = r·v, angular momentum)
    Dw/Dt = −∂π/∂z + b + F_driver + ν∇²w + F_z
    Db/Dt = κ∇²b + Q
    (1/r) ∂(r u)/∂r + ∂w/∂z = −s                             (s ≥ 0: mass sink, 1/s)

π = p'/ρ is the kinematic pressure perturbation. M and b are advected in flux form, so total
angular momentum is conserved to round-off in a closed, stress-free domain.

Discretization: staggered (MAC) grid, 3rd-order upwind-biased advection, 2nd-order diffusion,
SSP-RK3 time stepping with an exact discrete projection after every stage (∇·u = −s to
round-off). The pressure Poisson operator is LU-factorized once.

Boundaries:
    axis r = 0      u = 0, v = 0, w and b symmetric
    outer r = R     free-slip wall; normal inflow only when a mass sink must be supplied
    bottom z = 0    no-slip (u = v = 0) or free-slip, w = 0
    top z = H       free-slip lid, w = 0

The tornado is maintained the way vortex-chamber models (Fiedler 1994; Rotunno 1979) do it:
a fixed upward body force aloft stands in for the parent storm's updraft, and an outer sponge
holds angular momentum at M_inf, standing in for the rotating environment (mesocyclone).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

RHO_AIR = 1.1  # kg/m³, near-surface air density used to convert π to Pa and energies to J


@dataclass
class ModelConfig:
    R: float = 4000.0            # domain radius (m)
    H: float = 4000.0            # domain height (m)
    nr: int = 160
    nz: int = 160
    nu: float = 25.0             # eddy viscosity (m²/s)
    kappa: float = 25.0          # eddy diffusivity for b (m²/s)
    no_slip_bottom: bool = True
    # Parent-storm updraft forcing (m/s²), Gaussian in r and z
    driver_amp: float = 0.0
    driver_r: float = 1000.0
    driver_z: float = 2500.0
    driver_h: float = 1000.0
    # Environmental angular momentum supplied by the outer sponge
    M_inf: float = 0.0           # r·v (m²/s)
    sponge_start: float = 0.8    # fraction of R where the sponge begins
    sponge_rate: float = 1.0 / 30.0  # 1/s at r = R
    courant: float = 0.5
    dt_max: float = 0.5


@dataclass
class State:
    u: np.ndarray   # (nr+1, nz)  radial faces
    w: np.ndarray   # (nr, nz+1)  vertical faces
    M: np.ndarray   # (nr, nz)    centers, M = r v
    b: np.ndarray   # (nr, nz)    centers, buoyancy (m/s²)
    t: float = 0.0

    def copy(self):
        return State(self.u.copy(), self.w.copy(), self.M.copy(), self.b.copy(), self.t)


@dataclass
class Forcing:
    """Time-dependent external actions applied during one step (all optional)."""
    sink: np.ndarray | None = None         # (nr, nz) mass sink rate s (1/s)
    heat_target: np.ndarray | None = None  # (nr, nz) b is raised to at least this (m/s²)
    cool_target: np.ndarray | None = None  # (nr, nz) b is lowered to at most this (m/s², ≤ 0)
    damp_u: np.ndarray | None = None       # (nr+1, nz) decay rate for u (1/s), negative = growth
    damp_w: np.ndarray | None = None       # (nr, nz+1) decay rate for w (1/s)
    damp_M: np.ndarray | None = None       # (nr, nz) decay rate for M (1/s), negative = growth
    body_r: np.ndarray | None = None       # (nr+1, nz) extra radial force (m/s²)
    body_z: np.ndarray | None = None       # (nr, nz+1) extra vertical force (m/s²)


@dataclass
class EnergyLedger:
    heat_J: float = 0.0          # thermal energy added by heating, ρ c_p ΔT dV
    removed_air_kg: float = 0.0  # mass removed by sinks
    damping_J: float = 0.0       # kinetic energy removed (+) or added (−) by damp_* actions
    extra: dict = field(default_factory=dict)


def _upwind3(p, vel, h, axis):
    """3rd-order upwind-biased derivative of a 2-cell-padded array along `axis`."""
    def sl(off):
        idx = [slice(None)] * p.ndim
        n = p.shape[axis] - 4
        idx[axis] = slice(2 + off, 2 + off + n)
        return p[tuple(idx)]
    d_pos = (2 * sl(1) + 3 * sl(0) - 6 * sl(-1) + sl(-2)) / (6 * h)
    d_neg = (-sl(2) + 6 * sl(1) - 3 * sl(0) - 2 * sl(-1)) / (6 * h)
    return np.where(vel >= 0, d_pos, d_neg)


def _face_value3(p, vel, axis):
    """3rd-order upwind-biased value at the n+1 faces of a 2-cell-padded center array."""
    def sl(off):
        idx = [slice(None)] * p.ndim
        n = p.shape[axis] - 4
        idx[axis] = slice(1 + off, 1 + off + n + 1)  # face k sits between centers k-1 and k
        return p[tuple(idx)]
    # face k: left cell = k-1 (sl(0)), right cell = k (sl(1))
    left = (-sl(-1) + 5 * sl(0) + 2 * sl(1)) / 6.0
    right = (2 * sl(0) + 5 * sl(1) - sl(2)) / 6.0
    return np.where(vel >= 0, left, right)


class AxisymmetricModel:
    def __init__(self, cfg: ModelConfig):
        self.cfg = c = cfg
        self.dr = c.R / c.nr
        self.dz = c.H / c.nz
        self.rc = (np.arange(c.nr) + 0.5) * self.dr          # cell-center radii
        self.rf = np.arange(c.nr + 1) * self.dr              # radial-face radii
        self.zc = (np.arange(c.nz) + 0.5) * self.dz
        self.zf = np.arange(c.nz + 1) * self.dz
        self.RC, self.ZC = np.meshgrid(self.rc, self.zc, indexing="ij")
        self.vol = 2 * np.pi * self.RC * self.dr * self.dz    # cell volumes (m³)

        # Driver at w-faces
        RW, ZW = np.meshgrid(self.rc, self.zf, indexing="ij")
        self.driver = c.driver_amp * np.exp(-(RW / c.driver_r) ** 2 - ((ZW - c.driver_z) / c.driver_h) ** 2)
        self.driver[:, 0] = self.driver[:, -1] = 0.0

        # Sponge rate at centers
        r_s = c.sponge_start * c.R
        x = np.clip((self.rc - r_s) / (c.R - r_s), 0.0, None)
        self.sponge = (c.sponge_rate * x ** 2)[:, None] * np.ones((1, c.nz))

        self.u_outer = 0.0
        self._build_poisson()

    # ------------------------------------------------------------------ Poisson
    def _build_poisson(self):
        c, dr, dz = self.cfg, self.dr, self.dz
        nr, nz = c.nr, c.nz
        idx = np.arange(nr * nz).reshape(nr, nz)
        rows, cols, vals = [], [], []

        def add(i_arr, j_arr, coef_self, nbr_i, nbr_j, coef):
            rows.extend(idx[i_arr, j_arr]); cols.extend(idx[nbr_i, nbr_j]); vals.extend(coef)
            rows.extend(idx[i_arr, j_arr]); cols.extend(idx[i_arr, j_arr]); vals.extend(-coef)

        I, J = np.meshgrid(np.arange(nr), np.arange(nz), indexing="ij")
        I, J = I.ravel(), J.ravel()
        # radial neighbours (zero flux through axis and outer wall)
        m = I < nr - 1
        add(I[m], J[m], None, I[m] + 1, J[m], self.rf[I[m] + 1] / (self.rc[I[m]] * dr * dr))
        m = I > 0
        add(I[m], J[m], None, I[m] - 1, J[m], self.rf[I[m]] / (self.rc[I[m]] * dr * dr))
        m = J < nz - 1
        add(I[m], J[m], None, I[m], J[m] + 1, np.full(m.sum(), 1.0 / dz ** 2))
        m = J > 0
        add(I[m], J[m], None, I[m], J[m] - 1, np.full(m.sum(), 1.0 / dz ** 2))
        L = sp.csr_matrix((vals, (rows, cols)), shape=(nr * nz, nr * nz))
        # Pin one cell to remove the constant null space
        L = L.tolil(); L[0, :] = 0; L[0, 0] = 1.0
        self._lu = spla.splu(L.tocsc())

    def divergence(self, u, w):
        dr, dz = self.dr, self.dz
        rf = self.rf[:, None]
        div_r = (rf[1:] * u[1:] - rf[:-1] * u[:-1]) / (self.rc[:, None] * dr)
        div_z = (w[:, 1:] - w[:, :-1]) / dz
        return div_r + div_z

    def _solve(self, rhs):
        rhs = rhs.ravel().copy()
        rhs[0] = 0.0
        return self._lu.solve(rhs).reshape(self.cfg.nr, self.cfg.nz)

    def set_outer_inflow(self, sink):
        """Outer-wall normal velocity that supplies exactly the mass removed by `sink`."""
        if sink is None:
            self.u_outer = 0.0
        else:
            removed = np.sum(sink * self.vol)          # m³/s
            self.u_outer = -removed / (2 * np.pi * self.cfg.R * self.cfg.H)

    def project(self, u, w, dt, sink=None):
        """Make (u, w) satisfy ∇·u = −sink exactly. Returns π increment φ (π = φ/dt scale)."""
        u[0, :] = 0.0
        u[-1, :] = self.u_outer
        w[:, 0] = 0.0
        w[:, -1] = 0.0
        target = 0.0 if sink is None else -sink
        phi = self._solve(self.divergence(u, w) - target)
        u[1:-1, :] -= (phi[1:, :] - phi[:-1, :]) / self.dr
        w[:, 1:-1] -= (phi[:, 1:] - phi[:, :-1]) / self.dz
        return phi / dt

    # ------------------------------------------------------------------ padding
    def _pad_center(self, a, bottom_odd):
        """Pad a cell-center field with 2 ghost cells per side (axis even, outer/top even)."""
        p = np.empty((a.shape[0] + 4, a.shape[1] + 4))
        p[2:-2, 2:-2] = a
        # axis: even reflection; outer: zero-gradient (even reflection)
        p[1, 2:-2], p[0, 2:-2] = a[0], a[1]
        p[-2, 2:-2], p[-1, 2:-2] = a[-1], a[-2]
        s = -1.0 if bottom_odd else 1.0
        p[:, 1], p[:, 0] = s * p[:, 2], s * p[:, 3]
        p[:, -2], p[:, -1] = p[:, -3], p[:, -4]
        return p

    def _pad_u(self, u):
        """u at radial faces: odd about axis (u[0] = 0), linear extrapolation at outer wall."""
        nb = self.cfg.no_slip_bottom
        p = np.empty((u.shape[0] + 4, u.shape[1] + 4))
        p[2:-2, 2:-2] = u
        p[1, 2:-2], p[0, 2:-2] = -u[1], -u[2]
        p[-2, 2:-2] = 2 * u[-1] - u[-2]
        p[-1, 2:-2] = 2 * u[-1] - u[-3]
        s = -1.0 if nb else 1.0
        p[:, 1], p[:, 0] = s * p[:, 2], s * p[:, 3]
        p[:, -2], p[:, -1] = p[:, -3], p[:, -4]
        return p

    def _pad_w(self, w):
        """w at vertical faces: even about axis and outer wall, odd about bottom/top (w = 0)."""
        p = np.empty((w.shape[0] + 4, w.shape[1] + 4))
        p[2:-2, 2:-2] = w
        p[1, 2:-2], p[0, 2:-2] = w[0], w[1]
        p[-2, 2:-2], p[-1, 2:-2] = w[-1], w[-2]
        p[:, 1], p[:, 0] = -p[:, 3], -p[:, 4]
        p[:, -2], p[:, -1] = -p[:, -4], -p[:, -5]
        return p

    # ------------------------------------------------------------------ tendencies
    def tendencies(self, st: State, f: Forcing | None):
        c, dr, dz = self.cfg, self.dr, self.dz
        nu, kap = c.nu, c.kappa
        u, w, M, b = st.u, st.w, st.M, st.b
        rc, rf = self.rc[:, None], self.rf[:, None]

        pu = self._pad_u(u)
        pw = self._pad_w(w)
        pM = self._pad_center(M, bottom_odd=c.no_slip_bottom)
        pb = self._pad_center(b, bottom_odd=False)

        # ---- u (interior radial faces 1..nr-1)
        ui = u[1:-1]
        w_at_u = 0.25 * (w[:-1, :-1] + w[1:, :-1] + w[:-1, 1:] + w[1:, 1:])  # (nr-1, nz)
        dudr = _upwind3(pu[:, 2:-2], u, dr, 0)[1:-1]
        dudz = _upwind3(pu[3:-3, :], w_at_u, dz, 1)
        v = M / rc
        v_at_u = 0.5 * (v[:-1] + v[1:])
        rfi = rf[1:-1]
        lap_u = ((rc[1:] * (u[2:] - u[1:-1]) - rc[:-1] * (u[1:-1] - u[:-2])) / (rfi * dr * dr)
                 - ui / rfi ** 2
                 + (pu[3:-3, 3:-1] - 2 * ui + pu[3:-3, 1:-3]) / dz ** 2)
        du = np.zeros_like(u)
        du[1:-1] = -(ui * dudr + w_at_u * dudz) + v_at_u ** 2 / rfi + nu * lap_u

        # ---- w (interior vertical faces 1..nz-1)
        wi = w[:, 1:-1]
        u_at_w = 0.25 * (u[:-1, :-1] + u[1:, :-1] + u[:-1, 1:] + u[1:, 1:])  # (nr, nz-1)
        dwdr = _upwind3(pw[:, 3:-3], u_at_w, dr, 0)
        dwdz = _upwind3(pw[2:-2, :], w, dz, 1)[:, 1:-1]
        lap_w = ((rf[1:] * (pw[3:-1, 3:-3] - wi) - rf[:-1] * (wi - pw[1:-3, 3:-3])) / (rc * dr * dr)
                 + (w[:, 2:] - 2 * wi + w[:, :-2]) / dz ** 2)
        b_at_w = 0.5 * (b[:, :-1] + b[:, 1:])
        dw = np.zeros_like(w)
        dw[:, 1:-1] = -(u_at_w * dwdr + wi * dwdz) + b_at_w + self.driver[:, 1:-1] + nu * lap_w

        # ---- scalars in flux form: ∂φ/∂t = −∇·(uφ) + φ∇·u  (equals −u·∇φ)
        div = self.divergence(u, w)

        def advect(pphi, phi):
            fr = u * _face_value3(pphi[:, 2:-2], u, 0)               # (nr+1, nz)
            fz = w * _face_value3(pphi[2:-2, :], w, 1)               # (nr, nz+1)
            fz[:, 0] = 0.0; fz[:, -1] = 0.0
            fr[0] = 0.0
            flux_div = (rf[1:] * fr[1:] - rf[:-1] * fr[:-1]) / (rc * dr) + (fz[:, 1:] - fz[:, :-1]) / dz
            return -flux_div + phi * div

        # M diffusion: (1/r) ∂r( r³ ∂r(M/r²) ) + ∂zz M, stress-free at axis and outer wall
        Mr2 = M / rc ** 2
        Fr = np.zeros((c.nr + 1, c.nz))
        Fr[1:-1] = rf[1:-1] ** 3 * (Mr2[1:] - Mr2[:-1]) / dr
        diff_M = (Fr[1:] - Fr[:-1]) / (rc * dr) + (pM[2:-2, 3:-1] - 2 * M + pM[2:-2, 1:-3]) / dz ** 2
        dM = advect(pM, M) + nu * diff_M - self.sponge * (M - c.M_inf)

        Fb = np.zeros((c.nr + 1, c.nz))
        Fb[1:-1] = rf[1:-1] * (b[1:] - b[:-1]) / dr
        diff_b = Fb[1:] - Fb[:-1]
        diff_b = diff_b / (rc * dr) + (pb[2:-2, 3:-1] - 2 * b + pb[2:-2, 1:-3]) / dz ** 2
        db = advect(pb, b) + kap * diff_b - self.sponge * b

        if f is not None:
            if f.body_r is not None:
                du[1:-1] += f.body_r[1:-1]
            if f.body_z is not None:
                dw[:, 1:-1] += f.body_z[:, 1:-1]
        return du, dw, dM, db

    # ------------------------------------------------------------------ stepping
    def stable_dt(self, st: State):
        c = self.cfg
        adv = np.max(np.abs(st.u)) / self.dr + np.max(np.abs(st.w)) / self.dz
        v = np.abs(st.M) / self.rc[:, None]
        inertial = np.max(2 * v / self.rc[:, None])          # inertial frequency near axis
        dt = c.courant / max(adv, 1e-12)
        dt = min(dt, 0.8 / max(inertial, 1e-12))
        dt = min(dt, 0.3 * min(self.dr, self.dz) ** 2 / max(c.nu, c.kappa, 1e-12))
        return min(dt, c.dt_max)

    def step(self, st: State, dt: float, f: Forcing | None = None, ledger: EnergyLedger | None = None):
        sink = None if f is None else f.sink
        self.set_outer_inflow(sink)

        def euler(s):
            du, dw, dM, db = self.tendencies(s, f)
            n = State(s.u + dt * du, s.w + dt * dw, s.M + dt * dM, s.b + dt * db, s.t)
            self.project(n.u, n.w, dt, sink)
            return n

        s1 = euler(st)
        s2e = euler(s1)
        s2 = State(0.75 * st.u + 0.25 * s2e.u, 0.75 * st.w + 0.25 * s2e.w,
                   0.75 * st.M + 0.25 * s2e.M, 0.75 * st.b + 0.25 * s2e.b, st.t)
        s3e = euler(s2)
        new = State(st.u / 3 + 2 * s3e.u / 3, st.w / 3 + 2 * s3e.w / 3,
                    st.M / 3 + 2 * s3e.M / 3, st.b / 3 + 2 * s3e.b / 3, st.t + dt)
        self.project(new.u, new.w, dt, sink)

        if f is not None:
            self._apply_actions(new, f, dt, ledger)
        if ledger is not None and sink is not None:
            ledger.removed_air_kg += RHO_AIR * np.sum(sink * self.vol) * dt
        if ledger is not None and f is not None and f.body_r is not None:
            # work done on the air by the radial body force (fans): ρ ∫ F·u dV dt
            vol_u = 2 * np.pi * self.rf[:, None] * self.dr * self.dz
            ledger.extra["fan_J"] = ledger.extra.get("fan_J", 0.0) + RHO_AIR * float(np.sum(f.body_r * new.u * vol_u)) * dt
        return new

    def _apply_actions(self, st: State, f: Forcing, dt: float, ledger: EnergyLedger | None):
        """Operator-split device actions: heating to a target and exponential damping/growth."""
        changed = False
        if f.heat_target is not None:
            add = np.maximum(f.heat_target - st.b, 0.0)
            st.b += add
            if ledger is not None:
                # ΔT = b T_ref / g ; energy = ρ c_p ΔT dV
                ledger.heat_J += RHO_AIR * 1005.0 * np.sum(add * 288.0 / 9.81 * self.vol)
        if f.cool_target is not None:
            remove = np.maximum(st.b - f.cool_target, 0.0)
            st.b -= remove
            if ledger is not None:
                ledger.extra["cool_J"] = ledger.extra.get("cool_J", 0.0) + \
                    RHO_AIR * 1005.0 * float(np.sum(remove * 288.0 / 9.81 * self.vol))
        # Kinetic energy taken out (+) or put in (−) by the drag/growth factors themselves
        vol_u = 2 * np.pi * self.rf[:, None] * self.dr * self.dz * np.ones((1, self.cfg.nz))
        vol_w = 2 * np.pi * self.rc[:, None] * self.dr * self.dz * np.ones((1, self.cfg.nz + 1))
        work = 0.0
        if f.damp_u is not None:
            new = st.u * np.exp(-f.damp_u * dt)
            work += 0.5 * RHO_AIR * np.sum((st.u ** 2 - new ** 2) * vol_u)
            st.u = new; changed = True
        if f.damp_w is not None:
            new = st.w * np.exp(-f.damp_w * dt)
            work += 0.5 * RHO_AIR * np.sum((st.w ** 2 - new ** 2) * vol_w)
            st.w = new; changed = True
        if f.damp_M is not None:
            new = st.M * np.exp(-f.damp_M * dt)
            work += 0.5 * RHO_AIR * np.sum(((st.M ** 2 - new ** 2) / self.rc[:, None] ** 2) * self.vol)
            st.M = new; changed = True
        if changed:
            self.project(st.u, st.w, dt, f.sink)
            if ledger is not None:
                ledger.damping_J += work

    # ------------------------------------------------------------------ diagnostics
    def kinetic_energy(self, st: State):
        uc = 0.5 * (st.u[:-1] + st.u[1:])
        wc = 0.5 * (st.w[:, :-1] + st.w[:, 1:])
        v = st.M / self.rc[:, None]
        e = lambda a: 0.5 * RHO_AIR * float(np.sum(a ** 2 * self.vol))
        out = {"radial": e(uc), "swirl": e(v), "vertical": e(wc)}
        out["total"] = out["radial"] + out["swirl"] + out["vertical"]
        return out

    def pressure(self, st: State, f: Forcing | None = None):
        """Diagnostic kinematic pressure π (m²/s²) consistent with the current state."""
        du, dw, _, _ = self.tendencies(st, f)
        du[0, :] = 0.0; du[-1, :] = 0.0
        dw[:, 0] = 0.0; dw[:, -1] = 0.0
        return self._solve(self.divergence(du, dw))

    def vorticity_z(self, st: State):
        """Vertical vorticity ω = (1/r) ∂M/∂r at cell centers (axis value from M ≈ ω r²/2)."""
        M = st.M
        om = np.empty_like(M)
        om[1:-1] = (M[2:] - M[:-2]) / (2 * self.dr) / self.rc[1:-1, None]
        om[0] = 2 * M[0] / self.rc[0] ** 2
        om[-1] = (M[-1] - M[-2]) / self.dr / self.rc[-1]
        return om

    def initial_state(self, M_profile=None):
        c = self.cfg
        u = np.zeros((c.nr + 1, c.nz))
        w = np.zeros((c.nr, c.nz + 1))
        M = np.zeros((c.nr, c.nz)) if M_profile is None else M_profile(self.RC, self.ZC)
        b = np.zeros((c.nr, c.nz))
        return State(u, w, M, b, 0.0)
