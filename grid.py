"""Cylindrical (r, theta, z) grid discretization."""

import numpy as np


class CylindricalGrid:
    """Staggered cylindrical grid for incompressible flow solver.

    Grid variables stored at scalar (cell center) and velocity component locations.
    """

    def __init__(self, nx: int, ntheta: int, nz: int, r_min: float = 100, r_max: float = 2000, z_max: float = 3000):
        """Initialize cylindrical grid.

        Args:
            nx: radial grid points (velocity component r)
            ntheta: azimuthal grid points (periodic)
            nz: vertical grid points
            r_min: inner boundary radius (m)
            r_max: outer boundary radius (m)
            z_max: domain height (m)
        """
        self.nx, self.ntheta, self.nz = nx, ntheta, nz
        self.r_min, self.r_max = r_min, r_max
        self.z_max = z_max

        # Radial grid (uniform in log-space near axis to avoid singularity)
        self.r = np.logspace(np.log10(r_min), np.log10(r_max), nx)
        self.dr = np.diff(self.r)

        # Azimuthal grid (uniform)
        self.theta = np.linspace(0, 2 * np.pi, ntheta, endpoint=False)
        self.dtheta = 2 * np.pi / ntheta

        # Vertical grid (uniform)
        self.z = np.linspace(0, z_max, nz)
        self.dz = z_max / (nz - 1)

        # Staggered grid metric factors
        self._setup_metrics()

    def _setup_metrics(self):
        """Precompute Jacobians and metric tensors for cylindrical coords."""
        # In cylindrical coords: dx = dr, dy = r*dtheta, dz = dz
        # Jacobian factor at cell centers
        r_c = (self.r[:-1] + self.r[1:]) / 2  # cell centers
        self.jacobian_cell = r_c
        self.jacobian_face = self.r

    def distance(self, r1, theta1, z1, r2, theta2, z2) -> float:
        """Euclidean distance between two points in cylindrical coords (converted to Cartesian)."""
        x1, y1 = r1 * np.cos(theta1), r1 * np.sin(theta1)
        x2, y2 = r2 * np.cos(theta2), r2 * np.sin(theta2)
        return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)

    def velocity_to_cartesian(self, u_r, u_theta, u_z, theta):
        """Convert cylindrical velocity components to Cartesian at angle theta."""
        u_x = u_r * np.cos(theta) - u_theta * np.sin(theta)
        u_y = u_r * np.sin(theta) + u_theta * np.cos(theta)
        return u_x, u_y, u_z
