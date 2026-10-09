"""Tornado configuration, spin-up and per-step diagnostics."""

from __future__ import annotations

import time

import numpy as np

from .model import AxisymmetricModel, ModelConfig, RHO_AIR, State

# EF-scale 3-second-gust thresholds converted to m/s (lower bounds).
EF_THRESHOLDS = [(0, 29.0), (1, 38.5), (2, 49.6), (3, 60.8), (4, 74.2), (5, 89.4)]


def ef_rating(v):
    rating = None
    for ef, lo in EF_THRESHOLDS:
        if v >= lo:
            rating = ef
    return "below EF0" if rating is None else f"EF{rating}"


def tornado_config(**overrides) -> ModelConfig:
    """Vortex-chamber tornado: parent-storm updraft forcing + environmental angular momentum."""
    base = dict(R=4000.0, H=4000.0, nr=160, nz=160, nu=25.0, kappa=25.0,
                no_slip_bottom=True, driver_amp=0.9, driver_r=1000.0, driver_z=2500.0,
                driver_h=1000.0, M_inf=2.5e4, sponge_start=0.8, sponge_rate=1.0 / 30.0)
    base.update(overrides)
    return ModelConfig(**base)


def initial_swirl(cfg: ModelConfig):
    """Weak, broad, smooth rotation carrying the environmental angular momentum."""
    return lambda R, Z: cfg.M_inf * (1.0 - np.exp(-(R / 1500.0) ** 2))


def diagnostics(m: AxisymmetricModel, st: State, low_level=500.0, surface=100.0):
    v = st.M / m.rc[:, None]
    uc = 0.5 * (st.u[:-1] + st.u[1:])
    wc = 0.5 * (st.w[:, :-1] + st.w[:, 1:])
    low = m.zc <= low_level
    sfc = m.zc <= surface
    v_low = v[:, low]
    i_vmax, j_vmax = np.unravel_index(np.argmax(np.abs(v_low)), v_low.shape)
    horiz_sfc = np.sqrt(uc[:, sfc] ** 2 + v[:, sfc] ** 2)
    om = m.vorticity_z(st)
    pi = m.pressure(st)
    p_sfc = RHO_AIR * (pi[:, 0] - pi[-1, 0])          # Pa, relative to outer edge at the surface
    i1k = int(np.argmin(np.abs(m.rc - 1000.0)))
    ke = m.kinetic_energy(st)
    return {
        "t": st.t,
        "v_max_low": float(np.abs(v_low).max()),           # peak swirl, z ≤ 500 m
        "r_core": float(m.rc[i_vmax]),                     # radius of that peak
        "z_vmax": float(m.zc[low][j_vmax]),
        "wind_max_sfc": float(horiz_sfc.max()),             # peak horizontal wind, z ≤ 100 m
        "v_max_all": float(np.abs(v).max()),
        "w_max": float(wc.max()),
        "w_min": float(wc.min()),
        "u_in_max": float(-uc[:, low].min()),
        "omega_axis_low": float(om[0, low].max()),          # vertical vorticity on axis, z ≤ 500 m
        "omega_max_low": float(np.abs(om[:, low]).max()),
        "p_deficit_hPa": float(-p_sfc.min() / 100.0),       # central surface pressure drop
        "circ_1km": float(2 * np.pi * st.M[i1k, low].mean()),  # circulation at r = 1 km, m²/s
        "ke_swirl": ke["swirl"], "ke_radial": ke["radial"], "ke_vertical": ke["vertical"],
        "ke_total": ke["total"],
    }


def spin_up(cfg: ModelConfig, t_end: float, report_every=60.0, state: State | None = None, log=print):
    m = AxisymmetricModel(cfg)
    st = state if state is not None else m.initial_state(initial_swirl(cfg))
    history = []
    next_report = st.t
    t0 = time.time()
    while st.t < t_end - 1e-9:
        if st.t >= next_report - 1e-9:
            d = diagnostics(m, st)
            history.append(d)
            log(f"t={st.t:7.1f}s  v_low={d['v_max_low']:6.1f} m/s @ r={d['r_core']:5.0f} m  "
                f"sfc wind={d['wind_max_sfc']:6.1f}  w_max={d['w_max']:5.1f}  "
                f"Δp={d['p_deficit_hPa']:5.1f} hPa  [{time.time() - t0:5.0f}s wall]")
            next_report += report_every
        st = m.step(st, min(m.stable_dt(st), t_end - st.t))
    history.append(diagnostics(m, st))
    return m, st, history
