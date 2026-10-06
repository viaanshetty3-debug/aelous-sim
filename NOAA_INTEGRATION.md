# AEOLUS Real-World Meteorological Data Integration

## Overview

This document describes the integration of real-world atmospheric data from NOAA's THREDDS server into the AEOLUS 3D tornado simulator. The integration allows the simulator to initialize its fluid dynamics grid with actual meteorological conditions rather than purely synthetic Rankine vortex profiles.

## Architecture Changes

### New Modules

#### `noaa_data_ingestion.py`
Handles fetching, preprocessing, and interpolating meteorological data from NOAA sources:

- **`NOAADataIngestion` class**: 
  - Connects to NOAA THREDDS via siphon.catalog (or mock data when unavailable)
  - Fetches GFS/HRRR model data over Tornado Alley bounding box (34°–36°N, 97°–99°W)
  - Queries variables: u-component wind, v-component wind, temperature
  - Caches data to minimize network calls
  - Implements graceful fallback to synthetic data if THREDDS unavailable

- **Data interpolation**:
  - Projects lat/lon Cartesian wind components (u, v) into cylindrical coordinates (u_r, u_θ)
  - Maps to simulation grid with Gaussian vertical decay (decays exponentially with height)
  - Handles 4D arrays (time, level, lat, lon) by selecting latest time and lowest level
  - Uses scipy.interpolate.griddata for spatial interpolation

#### `baseline.py` (Extended)
Added `MeteorologicalVortex` class:
- Blends real meteorological data with synthetic vortex overlay
- Supports three blend modes via `vortex_strength` parameter:
  - `vortex_strength=0.0`: Pure real-world data (realworld mode)
  - `vortex_strength=0.5`: Hybrid blend (hybrid mode)
  - Pure Rankine: No real data used (rankine mode)
- Computes pressure perturbations from blended velocity field
- Inherits vorticity diagnostics from RankineVortex

### Modified Modules

#### `main.py`
Added command-line option `--initialization`:
- `rankine`: Pure Rankine vortex baseline (original behavior)
- `realworld`: Pure NOAA data (no synthetic vortex overlay)
- `hybrid`: Blended 50% vortex + 50% real data

Example usage:
```bash
# Hybrid initialization
python3 main.py --initialization hybrid --n-steps 120 --grid-size 96

# Pure real-world data
python3 main.py --initialization realworld --n-steps 120

# Original baseline (default)
python3 main.py --initialization rankine --n-steps 120
```

#### `requirements.txt`
Added dependencies:
- `siphon>=0.9.0`: NOAA THREDDS data access
- `xarray>=2022.0.0`: NetCDF dataset handling
- `netCDF4>=1.5.0`: Low-level NetCDF I/O

## Fallback Behavior

The system gracefully degrades when NOAA THREDDS is unavailable or libraries are missing:

1. **Missing siphon/xarray**: Uses synthetic mock meteorological data (Tornado Alley wind pattern)
2. **Network timeout**: Falls back to cached data (if available)
3. **Data fetch failure**: Reverts to Rankine vortex baseline

This ensures the simulation loop never crashes due to external data source failures.

## Data Sources

### Primary (THREDDS)
```
https://thredds.ucar.edu/thredds/catalog/gfs/Global_0p25deg/latest.xml
```
- GFS (Global Forecast System) model, 0.25° resolution
- 3-hourly cycle, forecast variables up to 10 days
- Contains u/v wind components and temperature at multiple pressure levels

### Variables Fetched
1. **u-component_of_wind_height_above_ground**: Zonal (eastward) wind
2. **v-component_of_wind_height_above_ground**: Meridional (southward) wind
3. **Temperature_height_above_ground**: Air temperature

### Bounding Box
Default query region (Tornado Alley):
- North: 36.0°N
- South: 34.0°N
- East: -97.0°E (West of Mississippi)
- West: -99.0°E

Customizable via `NOAADataIngestion(bbox={'north': 36, ...})`

## Coordinate Transformation

### Cartesian to Cylindrical Conversion

The NOAA data arrives as Cartesian wind components (u, v) on a lat/lon grid. The ingestion module converts to cylindrical coordinates (u_r, u_θ) centered on the storm location:

```
u_r   =  u·cos(θ) + v·sin(θ)
u_θ   = -u·sin(θ) + v·cos(θ)
```

Where θ is the azimuthal angle relative to storm center.

### Vertical Profile

Surface wind data is extrapolated to 3D grid levels with Gaussian decay:
```
u(r,θ,z) = u_2d(r,θ) · exp(-2·(z/z_max)²)
```

This reflects typical decrease of surface wind with altitude.

## Testing

Three modes have been verified to work end-to-end:

### 1. Pure Rankine (Baseline)
```bash
python3 main.py --initialization rankine --n-steps 20 --grid-size 48
```
- Result: High vorticity (ω_core ≈ 0.10 1/s), peak velocity ≈ 88 m/s
- Behavior: Unchanged from original simulator

### 2. Pure Real-World Data
```bash
python3 main.py --initialization realworld --n-steps 20 --grid-size 48
```
- Result: Low vorticity (ω_core ≈ 0.00 1/s), peak velocity ≈ 6 m/s
- Behavior: Realistic ambient wind field from mock NOAA data
- Use case: Testing intervention effectiveness on shear-dominated flows

### 3. Hybrid Blend
```bash
python3 main.py --initialization hybrid --n-steps 20 --grid-size 48
```
- Result: Intermediate vorticity (ω_core ≈ 0.05 1/s), peak velocity ≈ 48 m/s
- Behavior: Tornado-like vortex embedded in realistic ambient conditions
- Use case: Most realistic scenario for intervention studies

## Performance Considerations

- **Data fetch**: ~1–2 seconds (network + parsing)
- **Interpolation**: ~0.5 seconds for 96³ grid
- **Memory overhead**: Cached dataset ~10 MB
- **Time step**: Unchanged (~0.05 s typical)

## Known Limitations

1. **Mock data**: When real libraries unavailable, uses synthetic Tornado Alley wind pattern (not a real event)
2. **Pressure level selection**: Currently takes lowest available level (typically 1000 hPa); user should verify appropriateness
3. **Time selection**: Automatically uses latest available forecast cycle; no historical events support yet
4. **No vertical velocity**: Surface data doesn't include updrafts; w=0 initially (solver generates secondary circulation)

## Future Enhancements

1. **Real event replay**: Query historical NEXRAD + observation data for specific past tornadoes
2. **Multi-level vertical interpolation**: Use all pressure levels to construct full 3D initial condition
3. **Real-time ingestion**: Stream NEXRAD/GLM/surface obs for live scenario playback
4. **Mesoscale model coupling**: Initialize from HRRR or ARPS model output for cloud-resolving details
5. **Parameter estimation**: Auto-detect peak velocity and core radius from data rather than hard-coding

## References

- Siphon documentation: https://unidata.github.io/siphon/
- THREDDS Data Server: https://www.unidata.ucar.edu/software/thredds/current/tds/
- GFS model info: https://www.ncei.noaa.gov/products/weather-global-forecast-system
