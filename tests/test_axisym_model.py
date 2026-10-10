"""Verification of the axisymmetric tornado model against exact results."""

import numpy as np
import pytest

from aeolus_axisym import AxisymmetricModel, Forcing, ModelConfig, RHO_AIR


def lamb_oseen_M(r, M0, nu, t):
    return M0 * (1.0 - np.exp(-r ** 2 / (4 * nu * t)))


def _lamb_oseen_run(nr, nu=50.0, M0=2.0e4, t0=450.0, T=300.0):
    cfg = ModelConfig(R=3000.0, H=200.0, nr=nr, nz=2, nu=nu, kappa=nu,
                      no_slip_bottom=False, sponge_rate=0.0, courant=0.4)
    m = AxisymmetricModel(cfg)
    st = m.initial_state(lambda R, Z: lamb_oseen_M(R, M0, nu, t0))
    while st.t < T - 1e-9:
        st = m.step(st, min(m.stable_dt(st), T - st.t))
    exact = lamb_oseen_M(m.rc[:, None], M0, nu, t0 + T)
    v_err = np.abs(st.M - exact) / m.rc[:, None]
    v_max = np.max(exact / m.rc[:, None])
    # The exact solution is for an unbounded domain; the model has a stress-free wall at R,
    # so compare only away from it (r < 0.75 R).
    interior = m.rc < 0.75 * cfg.R
    return m, st, float(np.max(v_err[interior]) / v_max)


def test_projection_is_exactly_divergence_free():
    m = AxisymmetricModel(ModelConfig(nr=40, nz=30, R=2000, H=1500))
    rng = np.random.default_rng(0)
    u = rng.normal(size=(41, 30)); w = rng.normal(size=(40, 31))
    m.set_outer_inflow(None)
    m.project(u, w, 1.0)
    assert np.max(np.abs(m.divergence(u, w))) < 1e-10


def test_mass_sink_projection_matches_sink_and_is_supplied_at_outer_wall():
    m = AxisymmetricModel(ModelConfig(nr=40, nz=30, R=2000, H=1500))
    sink = 1e-3 * np.exp(-((m.RC - 600) / 200) ** 2 - ((m.ZC - 700) / 200) ** 2)
    u = np.zeros((41, 30)); w = np.zeros((40, 31))
    m.set_outer_inflow(sink)
    m.project(u, w, 1.0, sink)
    assert np.max(np.abs(m.divergence(u, w) + sink)) < 1e-10
    inflow = -2 * np.pi * m.cfg.R * np.sum(u[-1]) * m.dz
    assert inflow == pytest.approx(np.sum(sink * m.vol), rel=1e-12)


def test_pure_pressure_gradient_force_produces_no_flow():
    """An imposed pressure field (gradient force) is absorbed entirely by pressure."""
    m = AxisymmetricModel(ModelConfig(nr=40, nz=30, R=2000, H=1500, sponge_rate=0.0))
    st = m.initial_state()
    phi = -500.0 / RHO_AIR * np.exp(-((m.RC - 800) / 500) ** 2 - ((m.ZC - 750) / 300) ** 2)
    body_r = np.zeros((41, 30)); body_z = np.zeros((40, 31))
    body_r[1:-1] = -(phi[1:] - phi[:-1]) / m.dr
    body_z[:, 1:-1] = -(phi[:, 1:] - phi[:, :-1]) / m.dz
    f = Forcing(body_r=body_r, body_z=body_z)
    for _ in range(20):
        st = m.step(st, 0.2, f)
    assert np.max(np.abs(st.u)) < 1e-9 and np.max(np.abs(st.w)) < 1e-9


def test_lamb_oseen_vortex_decay_matches_exact_solution():
    _, _, err = _lamb_oseen_run(nr=120)
    assert err < 2e-3


def test_lamb_oseen_converges_at_second_order():
    _, _, e_coarse = _lamb_oseen_run(nr=40)
    _, _, e_fine = _lamb_oseen_run(nr=80)
    assert e_coarse / e_fine > 3.0


def test_pressure_is_in_cyclostrophic_balance():
    m, st, _ = _lamb_oseen_run(nr=120)
    pi = m.pressure(st)[:, 0]
    v = st.M[:, 0] / m.rc
    # exact balance: dπ/dr = v²/r  ->  π(r) − π(R) = −∫_r^R v²/r dr
    integrand = v ** 2 / m.rc
    expected = -np.concatenate([np.cumsum((integrand[::-1][:-1] + integrand[::-1][1:]) / 2 * m.dr)[::-1], [0.0]])
    interior = m.rc < 0.75 * m.cfg.R
    got = pi - pi[-1]
    got, expected = got - got[interior][-1], expected - expected[interior][-1]
    got, expected = got[interior], expected[interior]
    assert np.max(np.abs(got - expected)) / np.max(np.abs(expected)) < 0.01


def test_angular_momentum_and_heat_conserved_in_closed_stress_free_box():
    cfg = ModelConfig(R=2000, H=2000, nr=50, nz=50, nu=20, kappa=20,
                      no_slip_bottom=False, sponge_rate=0.0)
    m = AxisymmetricModel(cfg)
    st = m.initial_state(lambda R, Z: lamb_oseen_M(R, 1.5e4, 20.0, 600.0))
    st.b = 0.2 * np.exp(-((m.RC) / 300) ** 2 - ((m.ZC - 500) / 300) ** 2)
    M0 = np.sum(st.M * m.vol); B0 = np.sum(st.b * m.vol)
    for _ in range(150):
        st = m.step(st, m.stable_dt(st))
    assert np.max(np.abs(st.w)) > 1.0  # meridional circulation actually developed
    assert abs(np.sum(st.M * m.vol) - M0) / abs(M0) < 1e-10
    assert abs(np.sum(st.b * m.vol) - B0) / abs(B0) < 1e-10


def test_unforced_flow_only_loses_kinetic_energy():
    cfg = ModelConfig(R=2000, H=2000, nr=50, nz=50, nu=20, kappa=20, sponge_rate=0.0)
    m = AxisymmetricModel(cfg)
    st = m.initial_state(lambda R, Z: lamb_oseen_M(R, 1.5e4, 20.0, 600.0))
    rng = np.random.default_rng(1)
    st.u[1:-1] = rng.normal(scale=2.0, size=st.u[1:-1].shape)
    m.set_outer_inflow(None); m.project(st.u, st.w, 1.0)
    ke = [m.kinetic_energy(st)["total"]]
    for _ in range(100):
        st = m.step(st, m.stable_dt(st))
        ke.append(m.kinetic_energy(st)["total"])
    assert np.all(np.diff(ke) <= 1e-9 * ke[0])
