"""AEOLUS intervention versions v1–v7 and the realworld_test "80%" configuration as physical actions.

Each device action is translated from the original code into what a device would physically do:

* Thermal RFD     -> heat the target region so its temperature anomaly reaches ΔT (buoyancy
                     b = g ΔT / T_ref). The heated air is then advected and mixed by the model.
* Momentum sink   -> remove air (mass sink). The original code added a pressure field, but an
                     imposed pressure field cannot move air in incompressible flow (see
                     test_pure_pressure_gradient_force_produces_no_flow), so the sink strength is
                     calibrated to produce the stated pressure deficit in still air.
* Inflow blackout -> drag on low-level radial (and vertical) wind at the same per-second rates the
                     original code applied per step.

Geometry and timing come from the commits listed in VERSIONS. Old step counts are converted to
seconds with the old time steps (main.py dt = 0.05 s; realworld_test dt = 0.25 s).
"""

from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np

from .model import AxisymmetricModel, Forcing, RHO_AIR, State

G, T_REF = 9.81, 288.0
OLD_DT_MAIN = 0.05


@dataclass(frozen=True)
class Version:
    name: str
    source: str                    # commit the parameters come from
    thermal_K: float = 0.0
    sink_Pa: float = 0.0           # negative = suction
    blackout: bool = True          # momentum sink always carried the surface blackout
    sink_permanent: bool = False   # v1 and the test-bed config never switched the sink off
    sink_off_after: float | None = None
    amplify: bool = False          # v1's velocity multiplication (not a physical action)
    active_s: float = 2.5          # 50 steps × 0.05 s
    decay_s: float = 2.0           # 40 steps × 0.05 s
    geometry: str = "main"         # "main" (main.py) or "testbed" (realworld_test adapter)
    testbed_braking: bool = False  # add the test bed's assumed spin-down terms (not device actions)
    fan_accel: float = 0.0         # outward push from a ring of ground-level fans (m/s²)
    fan_r: float = 1000.0          # ring radius (m)
    fan_width: float = 250.0       # radial half-width of the ring (m)
    fan_depth: float = 200.0       # depth of the blown layer (m)
    fan_on_s: float = 600.0        # fans run this long, then switch off
    cool_K: float = 0.0            # keep a low-level ring at least this much colder (K)
    cool_r: float = 1000.0         # ring radius (m)
    cool_width: float = 500.0      # radial half-width (m)
    cool_depth: float = 250.0      # depth of the cooled layer (m)
    cool_on_s: float = 600.0
    note: str = ""

    @property
    def total_s(self):
        return self.active_s + self.decay_s


VERSIONS = [
    Version("v1", "e2ff6e8", thermal_K=2.0, sink_Pa=-250.0, sink_permanent=True, amplify=True,
            note="velocity amplification during thermal phase; sink and blackout never switched off"),
    Version("v2/v3", "ed5dbec", thermal_K=2.0, sink_Pa=-250.0,
            note="v2 and v3 differ only in old-solver damping; same device actions"),
    Version("v4/v5", "524d31e", thermal_K=0.5, sink_Pa=-50.0,
            note="v4 and v5 differ only in the old metric; same device actions"),
    Version("v6 thermal-only", "88aa923 ablation", thermal_K=4.0, sink_Pa=0.0, blackout=False),
    Version("v6 momentum-only", "88aa923 ablation", thermal_K=0.0, sink_Pa=-500.0),
    Version("v6 both-high", "88aa923 ablation", thermal_K=4.0, sink_Pa=-500.0),
    Version("v7", "V7_RESULTS (2026-10-08)", thermal_K=4.0, sink_Pa=-50.0),
    Version("RW80", "b40a2c8 realworld_test", thermal_K=4.0, sink_Pa=-500.0, sink_permanent=True,
            sink_off_after=45.0, active_s=10.0, decay_s=10.0, geometry="testbed",
            note="test-bed device actions: 40+40 steps × 0.25 s heating ring; sink + blackout on for "
                 "the remaining 45 s of the 50 s test"),
    Version("RW80 + assumed braking", "b40a2c8 realworld_test", thermal_K=4.0, sink_Pa=-500.0,
            sink_permanent=True, sink_off_after=45.0, active_s=10.0, decay_s=10.0, geometry="testbed",
            testbed_braking=True,
            note="adds the test bed's imposed spin-down terms (0.15/s thermal 'disruption' and the "
                 "0.24/s 'equilibration' brake) on top of the device actions"),
]

NULL_VERSION = Version("null (0.001 K)", "noise floor", thermal_K=0.001, sink_Pa=0.0, blackout=False,
                       note="tiny heating to measure how much runs diverge from noise alone")
FAN_VERSIONS = [
    Version(f"fan {a:g} m/s2", "what-would-it-take", thermal_K=0.0, sink_Pa=0.0, blackout=False,
            fan_accel=a, note="ring of ground-level fans at r = 1 km blowing outward for 10 min")
    for a in (0.05, 0.2, 0.5, 1.0, 2.0)
]

COOL_VERSIONS = [
    Version(f"cool {k:g} K", "what-would-it-take", thermal_K=0.0, sink_Pa=0.0, blackout=False,
            cool_K=k, note="low-level cold ring at r = 1 km (a man-made cold pool) for 10 min")
    for k in (1.0, 3.0, 6.0, 10.0)
] + [
    # ~6x the cooling power of "cool 10 K": a much larger cold pool, or the same ring cooled far harder
    Version("cool 10 K wide", "what-would-it-take", thermal_K=0.0, sink_Pa=0.0, blackout=False, cool_K=10.0,
            cool_width=1000.0, cool_depth=500.0, note="10 C cold pool, ring twice as wide and deep"),
    Version("cool 10 K huge", "what-would-it-take", thermal_K=0.0, sink_Pa=0.0, blackout=False, cool_K=10.0,
            cool_r=1250.0, cool_width=1250.0, cool_depth=750.0, note="10 C cold pool out to ~2.5 km, 750 m deep"),
    Version("cool 60 K", "what-would-it-take", thermal_K=0.0, sink_Pa=0.0, blackout=False, cool_K=60.0,
            note="same ring as cool 10 K, cooled 6x harder (far beyond any natural cold pool)"),
]

NULL_VERSION_2 = Version("null-b (0.001 K ring)", "noise floor", thermal_K=0.001, sink_Pa=0.0, blackout=False,
                         geometry="testbed", active_s=10.0, decay_s=10.0,
                         note="second tiny perturbation at a different place, for a second noise sample")


def extended(v: Version, factor: float = 24.0) -> Version:
    """Same device, run for the 30–60 s injection the design spec (CLAUDE.md) calls for."""
    if v.geometry != "main":
        return v
    return replace(v, name=f"{v.name} (60 s)", active_s=v.active_s * factor, decay_s=v.decay_s * factor)


def _thermal_env(v: Version, t):
    if t < 0 or t >= v.total_s:
        return 0.0
    if t < v.active_s:
        return 1.0
    f = (t - v.active_s) / v.decay_s
    return float(np.exp(-2.0 * f) * (1.0 - 0.3 * f))


def _sink_env(v: Version, t):
    if t < 0:
        return 0.0
    if v.sink_permanent:
        return 1.0 if (v.sink_off_after is None or t < v.sink_off_after) else 0.0
    if t >= v.total_s:
        return 0.0
    if t < v.active_s:
        return 1.0
    return float(np.exp(-2.0 * (t - v.active_s) / v.decay_s))


class Device:
    """Builds the Forcing for a version at a given time since intervention start."""

    def __init__(self, v: Version, m: AxisymmetricModel, core_radius: float):
        self.v, self.m, self.r_c = v, m, core_radius
        RC, ZC = m.RC, m.ZC
        if v.geometry == "main":
            self.th_r0, self.th_sr, self.th_z0, self.th_sz = 0.0, 300.0, 2100.0, 375.0
            self.sk_r0, self.sk_sr, self.sk_z0, self.sk_sz = 800.0, 500.0, 1500.0, 500.0
            self.bl_rmax = 2000.0
        else:
            rc = core_radius
            self.th_r0, self.th_sr, self.th_z0, self.th_sz = 1.5 * rc, 0.6 * rc, 2100.0, 375.0
            self.sk_r0, self.sk_sr, self.sk_z0, self.sk_sz = rc, rc, 1500.0, 500.0
            self.bl_rmax = 3000.0
        self.sink_shape = np.exp(-((RC - self.sk_r0) ** 2) / (2 * self.sk_sr ** 2)
                                 - ((ZC - self.sk_z0) ** 2) / (2 * self.sk_sz ** 2))
        self.sink_amp = self._calibrate_sink(abs(v.sink_Pa)) if v.sink_Pa else 0.0
        self.low_u = (m.zc[None, :] < 200.0) & (m.rf[:, None] <= self.bl_rmax)
        self.low_w = (m.zf[None, :] < 200.0) & (m.rc[:, None] <= self.bl_rmax)
        self.low_c = (m.zc[None, :] < 200.0) & (m.rc[:, None] <= self.bl_rmax)

    def _calibrate_sink(self, dp_Pa):
        """Sink amplitude (1/s) whose still-air potential flow has a pressure deficit of dp_Pa."""
        m = self.m
        sink = self.sink_shape.copy()
        u = np.zeros_like(m.initial_state().u); w = np.zeros_like(m.initial_state().w)
        m.set_outer_inflow(sink)
        m.project(u, w, 1.0, sink)
        speed2 = (0.5 * (u[:-1] + u[1:])) ** 2 + (0.5 * (w[:, :-1] + w[:, 1:])) ** 2
        dp_unit = 0.5 * RHO_AIR * speed2.max()          # Bernoulli deficit for unit amplitude
        m.set_outer_inflow(None)
        return float(np.sqrt(dp_Pa / dp_unit))

    def thermal_mask(self, t):
        tf = min(max(t / self.v.total_s, 0.0), 1.0)
        sr = self.th_sr * (1 + 0.3 * tf)
        sz = self.th_sz * (1 + 0.5 * tf)
        return np.exp(-((self.m.RC - self.th_r0) ** 2) / (2 * sr ** 2)
                      - ((self.m.ZC - self.th_z0) ** 2) / (2 * sz ** 2))

    def forcing(self, t: float, st: State) -> Forcing | None:
        v, m = self.v, self.m
        f = Forcing()
        active = False

        env_t = _thermal_env(v, t)
        if v.thermal_K and env_t > 0:
            f.heat_target = G * v.thermal_K * env_t / T_REF * self.thermal_mask(t)
            active = True

        env_s = _sink_env(v, t)
        if v.sink_Pa and env_s > 0:
            f.sink = self.sink_amp * np.sqrt(env_s) * self.sink_shape   # Δp ∝ s²
            active = True
            if v.blackout:
                if v.geometry == "main":
                    k_u = -np.log(1 - 0.9 * env_s) / OLD_DT_MAIN
                    k_w = -np.log(1 - 0.5 * env_s) / OLD_DT_MAIN
                    k_M = 0.0
                else:
                    k_u, k_w, k_M = 3.0, 1.5, 0.2
                f.damp_u = k_u * self.low_u
                f.damp_w = k_w * self.low_w
                if k_M:
                    f.damp_M = k_M * self.low_c.astype(float)

        if v.amplify and 0 <= t < v.active_s:
            mask = self.thermal_mask(t)
            mask_u = np.zeros_like(st.u); mask_u[1:-1] = 0.5 * (mask[:-1] + mask[1:])
            grow_u = -np.log(1 + 0.1 * 0.15 * mask_u) / OLD_DT_MAIN
            grow_M = -np.log(1 + 0.05 * 0.15 * mask) / OLD_DT_MAIN
            f.damp_u = grow_u if f.damp_u is None else f.damp_u + grow_u
            f.damp_M = grow_M if f.damp_M is None else f.damp_M + grow_M
            active = True

        if v.testbed_braking and t >= 0:
            vel = st.M / m.rc[:, None]
            k = np.zeros_like(st.M)
            if env_t > 0:
                disrupt = np.exp(-(m.RC / (2 * self.r_c)) ** 2) * np.exp(-((m.ZC - 400.0) / 700.0) ** 2)
                k += 0.15 * env_t * disrupt
            if env_s > 0:
                vs = np.maximum(np.abs(vel), 1.0)
                k += 0.24 * abs(v.sink_Pa) * self.sink_shape / (1.15 * vs * vs)
            f.damp_M = k if f.damp_M is None else f.damp_M + k
            active = True

        if v.fan_accel and 0 <= t < v.fan_on_s:
            shape = np.exp(-((m.rf[:, None] - v.fan_r) / v.fan_width) ** 2) * np.exp(-(m.zc[None, :] / v.fan_depth) ** 2)
            f.body_r = v.fan_accel * shape
            active = True

        if v.cool_K and 0 <= t < v.cool_on_s:
            shape = np.exp(-((m.RC - v.cool_r) / v.cool_width) ** 2) * np.exp(-(m.ZC / v.cool_depth) ** 2)
            f.cool_target = -G * v.cool_K / T_REF * shape
            active = True

        return f if active else None
