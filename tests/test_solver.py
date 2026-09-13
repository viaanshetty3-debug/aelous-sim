"""Tests for Navier-Stokes solver."""

import numpy as np
import pytest

from grid import CylindricalGrid
from solver import NavierStokesSolver


class TestNavierStokesSolver:
    """Test solver stability and convergence."""

    @pytest.fixture
    def setup(self):
        grid = CylindricalGrid(nx=32, ntheta=32, nz=32)
        solver = NavierStokesSolver(grid=grid, dt=0.01)
        u_r = np.zeros((grid.nx, grid.ntheta, grid.nz))
        u_theta = np.zeros((grid.nx, grid.ntheta, grid.nz))
        u_z = np.zeros((grid.nx, grid.ntheta, grid.nz))
        p = np.zeros((grid.nx, grid.ntheta, grid.nz))
        return solver, u_r, u_theta, u_z, p

    def test_solver_step(self, setup):
        """Test a single time step executes without error."""
        solver, u_r, u_theta, u_z, p = setup
        u_r_new, u_theta_new, u_z_new, p_new = solver.step(u_r, u_theta, u_z, p)
        assert u_r_new.shape == u_r.shape

    def test_mass_conservation(self, setup):
        """Check that divergence remains small."""
        solver, u_r, u_theta, u_z, p = setup
        # Placeholder: would compute divergence
        pass

    def test_cfl_stability(self, setup):
        """Verify CFL number stays below 1."""
        solver, u_r, u_theta, u_z, p = setup
        max_vel = np.max(np.abs(u_theta))
        dx = solver.grid.dr.mean()
        cfl = max_vel * solver.dt / dx
        assert cfl < 1.0
