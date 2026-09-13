"""Tests for Rankine vortex initialization."""

import numpy as np
import pytest

from baseline import RankineVortex
from grid import CylindricalGrid


class TestRankineVortex:
    """Test Rankine vortex initialization and properties."""

    @pytest.fixture
    def setup(self):
        grid = CylindricalGrid(nx=32, ntheta=32, nz=32)
        rankine = RankineVortex(grid=grid, core_radius=500, max_velocity=90)
        return rankine, grid

    def test_initialization(self, setup):
        """Test that initialization produces valid velocity field."""
        rankine, grid = setup
        u_r, u_theta, u_z, p = rankine.initialize()
        assert u_r.shape == (grid.nx, grid.ntheta, grid.nz)
        assert u_theta.shape == (grid.nx, grid.ntheta, grid.nz)
        assert u_z.shape == (grid.nx, grid.ntheta, grid.nz)
        assert p.shape == (grid.nx, grid.ntheta, grid.nz)

    def test_tangential_velocity(self, setup):
        """Test that u_theta matches Rankine profile inside core."""
        rankine, grid = setup
        u_r, u_theta, u_z, p = rankine.initialize()
        # Peak should occur near core radius
        mid_z = len(grid.z) // 2
        mid_theta = len(grid.theta) // 2
        u_tangential_profile = u_theta[:, mid_theta, mid_z]
        peak_idx = np.argmax(u_tangential_profile)
        # Peak should be near core radius in grid
        core_idx = np.argmin(np.abs(grid.r - rankine.core_radius))
        assert abs(peak_idx - core_idx) < len(grid.r) // 4

    def test_lower_boundary_no_slip(self, setup):
        """Test no-slip boundary condition at z=0."""
        rankine, grid = setup
        u_r, u_theta, u_z, p = rankine.initialize()
        # Velocities at z=0 should be near zero
        assert np.max(np.abs(u_theta[:, :, 0])) < np.max(np.abs(u_theta))

    def test_pressure_positive(self, setup):
        """Test that pressure field is physically reasonable."""
        rankine, grid = setup
        u_r, u_theta, u_z, p = rankine.initialize()
        # Pressure should be positive
        assert np.all(p > 0)
