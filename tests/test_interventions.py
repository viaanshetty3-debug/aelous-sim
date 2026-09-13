"""Tests for disruption interventions."""

import numpy as np
import pytest

from grid import CylindricalGrid
from interventions import ThermalRFDIntervention, MomentumSinkIntervention


class TestThermalRFDIntervention:
    """Test thermal buoyancy injection."""

    @pytest.fixture
    def setup(self):
        grid = CylindricalGrid(nx=32, ntheta=32, nz=32)
        intervention = ThermalRFDIntervention(grid=grid, duration_steps=30)
        u_r = np.zeros((grid.nx, grid.ntheta, grid.nz))
        u_theta = np.zeros((grid.nx, grid.ntheta, grid.nz))
        u_z = np.zeros((grid.nx, grid.ntheta, grid.nz))
        p = np.zeros((grid.nx, grid.ntheta, grid.nz))
        return intervention, u_r, u_theta, u_z, p

    def test_intervention_applies(self, setup):
        """Test that intervention modifies velocity field."""
        intervention, u_r, u_theta, u_z, p = setup
        u_r_new, u_theta_new, u_z_new, p_new = intervention.apply(u_r, u_theta, u_z, p, step=10)
        # Vertical velocity should increase in injection region
        assert np.any(u_z_new > 0)

    def test_duration_respected(self, setup):
        """Test that intervention stops after duration."""
        intervention, u_r, u_theta, u_z, p = setup
        u_z_before = u_z.copy()
        u_r_out, u_theta_out, u_z_out, p_out = intervention.apply(
            u_r, u_theta, u_z, p, step=100
        )
        # After duration, should not modify
        np.testing.assert_array_equal(u_z_out, u_z_before)


class TestMomentumSinkIntervention:
    """Test momentum sink application."""

    @pytest.fixture
    def setup(self):
        grid = CylindricalGrid(nx=32, ntheta=32, nz=32)
        intervention = MomentumSinkIntervention(grid=grid)
        u_r = np.ones((grid.nx, grid.ntheta, grid.nz))
        u_theta = np.ones((grid.nx, grid.ntheta, grid.nz))
        u_z = np.zeros((grid.nx, grid.ntheta, grid.nz))
        p = np.zeros((grid.nx, grid.ntheta, grid.nz))
        return intervention, u_r, u_theta, u_z, p

    def test_sink_reduces_inflow(self, setup):
        """Test that sink reduces near-surface radial velocity."""
        intervention, u_r, u_theta, u_z, p = setup
        u_r_new, _, _, p_new = intervention.apply(u_r, u_theta, u_z, p, step=1)
        # Surface blackout should reduce u_r near z=0
        assert np.mean(u_r_new[:, :, :5]) < np.mean(u_r[:, :, :5])

    def test_pressure_perturbation(self, setup):
        """Test that sink applies pressure deficit."""
        intervention, u_r, u_theta, u_z, p = setup
        p_init = p.copy()
        _, _, _, p_new = intervention.apply(u_r, u_theta, u_z, p, step=1)
        # Pressure should be perturbed
        assert not np.allclose(p_new, p_init)
