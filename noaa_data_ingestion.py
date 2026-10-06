"""Real-world meteorological data ingestion from NOAA THREDDS server.

Fetches atmospheric conditions (wind, temperature) from NOAA GFS/HRRR models
over Tornado Alley region via siphon.catalog. Provides fallback to Rankine
vortex baseline if data fetch fails. Includes mock data source for testing.
"""

import numpy as np
import warnings
from datetime import datetime, timedelta
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# Try importing real libraries, degrade to mock if unavailable
try:
    import siphon.catalog
    HAS_SIPHON = True
except ImportError:
    HAS_SIPHON = False
    logger.debug("siphon not available; will use mock data for testing")


class NOAADataIngestion:
    """Fetch and preprocess real atmospheric data from NOAA THREDDS."""

    # Tornado Alley bounding box (lat/lon)
    DEFAULT_BBOX = {
        "north": 36.0,   # Oklahoma
        "south": 34.0,
        "east": -97.0,   # West of Mississippi
        "west": -99.0,
    }

    # THREDDS data sources to try (in priority order)
    DATA_SOURCES = [
        "https://thredds.ucar.edu/thredds/catalog.html",  # GFS/HRRR catalog root
    ]

    # Target variables from NetCDF
    VAR_NAMES = [
        "u-component_of_wind_height_above_ground",
        "v-component_of_wind_height_above_ground",
        "Temperature_height_above_ground",
    ]

    def __init__(self, bbox: Optional[dict] = None, timeout_s: float = 30.0):
        """Initialize NOAA data fetcher.

        Args:
            bbox: bounding box dict with keys 'north', 'south', 'east', 'west'.
                  Defaults to Tornado Alley.
            timeout_s: connection timeout in seconds.
        """
        self.bbox = bbox or self.DEFAULT_BBOX
        self.timeout_s = timeout_s
        self.last_fetch_time = None
        self.cached_data = None

    def fetch_latest_data(self) -> Optional[dict]:
        """Fetch latest available meteorological data from NOAA THREDDS.

        Returns:
            Dict with keys 'u_wind', 'v_wind', 'temperature', 'lon', 'lat', 'time'
            or None if fetch fails.
        """
        if not HAS_SIPHON:
            logger.warning("siphon not installed; using synthetic mock meteorological data for testing")
            return self._generate_mock_data()

        try:
            utc_now = datetime.utcnow()
            logger.info(f"Fetching NOAA data for {utc_now.isoformat()}Z...")

            # Try to connect to GFS dataset
            # Real deployment would iterate through available cycles
            try:
                from siphon.catalog import TDSCatalog
                cat_url = "https://thredds.ucar.edu/thredds/catalog/gfs/Global_0p25deg/latest.xml"
                catalog = TDSCatalog(cat_url)
                datasets = list(catalog.datasets)

                if not datasets:
                    logger.warning("No datasets found in GFS catalog")
                    return self._generate_mock_data()

                # Fetch from most recent available dataset
                dataset = datasets[0]
                access_url = dataset.access_urls.get("NetcdfSubset")

                if not access_url:
                    logger.warning("NetcdfSubset access not available")
                    return self._generate_mock_data()

                data = self._fetch_netcdf_subset(access_url)
                if data:
                    self.cached_data = data
                    self.last_fetch_time = utc_now
                    return data

            except Exception as e:
                logger.warning(f"GFS fetch failed: {e}; falling back to mock data")
                # Fallback: use cached data or mock
                if self.cached_data:
                    logger.info("Using cached meteorological data")
                    return self.cached_data
                return self._generate_mock_data()

        except Exception as e:
            logger.error(f"NOAA data fetch exception: {e}")
            return self._generate_mock_data()

    def _generate_mock_data(self) -> dict:
        """Generate synthetic but realistic meteorological data for testing.

        Simulates a wind field typical of Tornado Alley (south wind with
        some cyclonic shear) overlaid on a 2D lat/lon grid.

        Returns:
            Dict with mock u_wind, v_wind, temperature fields.
        """
        # Create a realistic grid for Tornado Alley
        lon = np.linspace(self.bbox["west"], self.bbox["east"], 25)
        lat = np.linspace(self.bbox["south"], self.bbox["north"], 25)
        lon_2d, lat_2d = np.meshgrid(lon, lat)

        # Mock wind pattern: southerly flow (positive v) with weak cyclonic shear
        u_wind = 3.0 * np.cos(lon_2d * np.pi / 180.0)  # weak east-west variation
        v_wind = 8.0 + 2.0 * np.sin((lon_2d + lat_2d) * np.pi / 180.0)  # southerly with shear

        # Mock temperature: cooler aloft, gradient from north to south
        temperature = 285.0 - 0.03 * (lat_2d - self.bbox["south"]) * 111.32 + 5.0 * np.sin(
            lon_2d * np.pi / 180.0
        )

        logger.info(f"Generated mock meteorological data: u_wind {u_wind.shape}, "
                    f"v_wind {v_wind.shape}, T {temperature.shape}")

        return {
            "u_wind": u_wind[np.newaxis, np.newaxis, :, :],  # (time, level, lat, lon)
            "v_wind": v_wind[np.newaxis, np.newaxis, :, :],
            "temperature": temperature[np.newaxis, np.newaxis, :, :],
            "lon": lon,
            "lat": lat,
            "time": datetime.utcnow(),
        }

    def _fetch_netcdf_subset(self, access_url: str) -> Optional[dict]:
        """Fetch NetCDF subset via WCS query.

        Args:
            access_url: THREDDS WCS access endpoint

        Returns:
            Dict of interpolated wind/temperature fields or None.
        """
        try:
            import xarray as xr
        except ImportError:
            logger.warning("xarray not installed; install via: pip install xarray")
            return None

        try:
            # Build WCS query string
            query_params = (
                f"?request=GetCapabilities"
                f"&north={self.bbox['north']}"
                f"&south={self.bbox['south']}"
                f"&east={self.bbox['east']}"
                f"&west={self.bbox['west']}"
                f"&vertCoord=1000"  # 1000 hPa pressure level
            )

            fetch_url = access_url + query_params
            logger.debug(f"Fetching from {fetch_url}")

            # Open dataset with timeout
            with xr.open_dataset(
                fetch_url,
                engine="netcdf4",
                decode_times=True,
                decode_coords="all",
            ) as ds:

                # Extract variables
                u_wind = None
                v_wind = None
                temperature = None

                for var_name in self.VAR_NAMES:
                    if var_name in ds.data_vars:
                        if "u-component" in var_name:
                            u_wind = ds[var_name].values
                        elif "v-component" in var_name:
                            v_wind = ds[var_name].values
                        elif "Temperature" in var_name:
                            temperature = ds[var_name].values

                if u_wind is None or v_wind is None:
                    logger.warning("Missing u or v wind components in dataset")
                    return None

                # Extract coordinate arrays
                lon = ds.coords.get("longitude", np.arange(u_wind.shape[-1]))
                lat = ds.coords.get("latitude", np.arange(u_wind.shape[-2]))

                logger.info(
                    f"Fetched data: u_wind {u_wind.shape}, "
                    f"v_wind {v_wind.shape}, T {temperature.shape if temperature is not None else 'None'}"
                )

                return {
                    "u_wind": u_wind,
                    "v_wind": v_wind,
                    "temperature": temperature,
                    "lon": lon,
                    "lat": lat,
                    "time": datetime.utcnow(),
                }

        except Exception as e:
            logger.error(f"NetCDF subset fetch failed: {e}")
            return None

    def interpolate_to_grid(
        self,
        data: dict,
        grid,
        center_lat: float = 35.34,
        center_lon: float = -97.49,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Interpolate fetched real-world data to cylindrical simulation grid.

        Projects lat/lon Cartesian wind components (u_wind, v_wind) into
        cylindrical coordinates (u_r, u_theta) centered on a target location.

        Args:
            data: dict from fetch_latest_data() with 'u_wind', 'v_wind', 'lon', 'lat'
            grid: CylindricalGrid instance
            center_lat, center_lon: storm center location (deg)

        Returns:
            (u_r, u_theta, u_z, temperature, u_theta_cartesian)
            - u_r, u_theta: radial, azimuthal velocity in cylindrical coords (m/s)
            - u_z: vertical velocity (default 0 from surface data)
            - temperature: interpolated temperature field
            - u_theta_cartesian: tangential velocity in Cartesian frame
        """
        try:
            from scipy.interpolate import griddata
        except ImportError:
            logger.warning("scipy not installed; install via: pip install scipy")
            return None

        u_wind = data.get("u_wind")
        v_wind = data.get("v_wind")
        temperature = data.get("temperature")
        lon = data.get("lon")
        lat = data.get("lat")

        if u_wind is None or v_wind is None:
            return None

        # Handle 4D arrays (time, level, lat, lon) -> take latest time, lowest level
        if u_wind.ndim == 4:
            u_wind = u_wind[-1, 0, :, :]  # latest time, lowest level
            v_wind = v_wind[-1, 0, :, :]
            if temperature is not None:
                temperature = temperature[-1, 0, :, :]
        elif u_wind.ndim == 3:
            u_wind = u_wind[0, :, :]  # take first/lowest level
            v_wind = v_wind[0, :, :]
            if temperature is not None:
                temperature = temperature[0, :, :]

        # Create lat/lon mesh for interpolation
        if lon.ndim == 1 and lat.ndim == 1:
            lon_2d, lat_2d = np.meshgrid(lon, lat)
        else:
            lon_2d, lat_2d = lon, lat

        # Flatten for scipy griddata
        points = np.column_stack([lon_2d.ravel(), lat_2d.ravel()])
        u_flat = u_wind.ravel()
        v_flat = v_wind.ravel()
        t_flat = temperature.ravel() if temperature is not None else None

        # Generate target points on cylindrical grid (convert to lat/lon)
        nx, ntheta, nz = grid.nx, grid.ntheta, grid.nz
        target_lons = []
        target_lats = []

        for i in range(nx):
            for j in range(ntheta):
                # Convert (r, theta) to Cartesian then to lat/lon offset
                r = grid.r[i]
                theta = grid.theta[j]
                dx = r * np.cos(theta)  # meters to deg (approximate)
                dy = r * np.sin(theta)
                dlat = dy / 111320.0  # 1 degree ~111.32 km
                dlon = dx / (111320.0 * np.cos(np.deg2rad(center_lat)))
                target_lats.append(center_lat + dlat)
                target_lons.append(center_lon + dlon)

        target_points = np.column_stack([target_lons, target_lats])

        # Interpolate wind components to grid
        try:
            u_interp = griddata(
                points, u_flat, target_points, method="linear", fill_value=0.0
            )
            v_interp = griddata(
                points, v_flat, target_points, method="linear", fill_value=0.0
            )
            t_interp = None
            if t_flat is not None:
                t_interp = griddata(
                    points, t_flat, target_points, method="linear", fill_value=280.0
                )
        except Exception as e:
            logger.error(f"Interpolation failed: {e}")
            return None

        # Reshape to grid
        u_interp = u_interp.reshape(nx, ntheta)
        v_interp = v_interp.reshape(nx, ntheta)

        # Convert Cartesian (u, v) to cylindrical (u_r, u_theta) at each point
        u_r_grid = np.zeros((nx, ntheta, nz))
        u_theta_grid = np.zeros((nx, ntheta, nz))

        for i in range(nx):
            for j in range(ntheta):
                theta = grid.theta[j]
                # Rotate Cartesian velocity to radial/azimuthal
                u_r_local = u_interp[i, j] * np.cos(theta) + v_interp[i, j] * np.sin(
                    theta
                )
                u_theta_local = -u_interp[i, j] * np.sin(theta) + v_interp[
                    i, j
                ] * np.cos(theta)

                # Replicate over height levels with decay
                for k in range(nz):
                    z_frac = grid.z[k] / grid.z_max
                    decay = np.exp(-2.0 * z_frac**2)  # Gaussian envelope
                    u_r_grid[i, j, k] = u_r_local * decay
                    u_theta_grid[i, j, k] = u_theta_local * decay

        u_z_grid = np.zeros((nx, ntheta, nz))  # No vertical velocity from surface data

        if t_interp is not None:
            t_interp = t_interp.reshape(nx, ntheta)
            t_grid = np.tile(t_interp[:, :, np.newaxis], (1, 1, nz))
        else:
            t_grid = 288.0 * np.ones((nx, ntheta, nz))  # Standard sea-level temp

        logger.info(
            f"Interpolated to grid: u_r range [{u_r_grid.min():.2f}, {u_r_grid.max():.2f}] m/s, "
            f"u_theta range [{u_theta_grid.min():.2f}, {u_theta_grid.max():.2f}] m/s"
        )

        return u_r_grid, u_theta_grid, u_z_grid, t_grid, u_interp

    def get_fallback_profile(self, grid) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Generate fallback Rankine vortex profile if data fetch fails.

        Returns:
            (u_r, u_theta, u_z) baseline fields
        """
        from baseline import RankineVortex

        rankine = RankineVortex(grid=grid, core_radius=500.0, max_velocity=90.0)
        u_r, u_theta, u_z, _ = rankine.initialize()
        logger.warning("Using Rankine vortex fallback profile")
        return u_r, u_theta, u_z
