# 🚀 AEOLUS Interactive Dashboards

Two web-based dashboard options for controlling the tornado intervention system:

## Option 1: Flask Dashboard ⚡ (Recommended - Faster)

**Lightweight, minimal dependencies, starts instantly**

```bash
cd aeolus_sim
python flaskrun.py
```

**Or directly:**
```bash
python web_app.py
```

📍 **URL:** http://localhost:5000

✓ Faster startup (Flask < Streamlit)
✓ Lower resource usage  
✓ Works on slower systems
✓ Fully functional dashboard with real-time simulation

---

## Option 2: Streamlit Dashboard 🎨 (Advanced)

**More polished UI, additional features**

```bash
cd aeolus_sim
python streamlitrun.py
```

**Or directly:**
```bash
streamlit run app.py
```

📍 **URL:** http://localhost:8501

✓ Professional-grade UI
✓ Interactive widgets
✓ More visualization options
⚠️  Slower initial startup (installs on first run)

---

## 🎮 Dashboard Features (Both Options)

### Hardware Visualization
- 🚛 **Vacuum Truck**: Mobile suction unit showing -250 Pa pressure
- 🔥 **Thermal Grid**: 5×2 heater array deployment map

### Interactive Controls
- **Vacuum Pressure**: -100 to -500 Pa (default: -250 Pa)
- **Thermal Anomaly**: 0.5 to 5.0 K (default: 3.0 K)
- **Duration**: 30-200 time steps (default: 120 ≈ 6 seconds)

### Real-Time Simulation
- **ACTIVATE DISRUPTOR** button triggers 120-step run
- Live progress bar with percentage
- Step-by-step calculation display

### Results Analysis
- **4-Panel Metrics Chart**:
  - Core Vorticity Reduction (%) - PRIMARY METRIC
  - Core Vorticity (1/s)
  - Maximum Velocity (m/s)
  - Kinetic Energy (J)
- **Key Metrics Display**:
  - Final reduction percentage
  - Peak reduction achieved
  - Final core vorticity
  - Peak velocity

---

## 📊 Expected Results

With default settings (**-250 Pa vacuum + 3.0 K thermal**):

```
✓ Final Vorticity Reduction:    117.30%
✓ Peak Reduction:               ~125% (around step 15)
✓ Sign Reversal:                Yes (>100% means antisymmetric suppression)
✓ Simulation Time:              ~6 seconds
```

---

## 🔧 Technical Details

### Solver Integration
- **Grid**: 32³ cylindrical coordinates (r, θ, z)
- **Physics**: Navier-Stokes with wind shear, LHR, precipitation
- **Time Step**: 0.05 seconds
- **Interventions**:
  - Thermal RFD (adjustable 0.5-5.0 K)
  - Momentum Sink (adjustable -100 to -500 Pa)

### Files
```
aeolus_sim/
├── flaskrun.py              ← Flask launcher
├── streamlitrun.py          ← Streamlit launcher
├── web_app.py               ← Flask web dashboard
├── app.py                   ← Streamlit web dashboard
├── solver.py                ← High-fidelity NS solver
├── grid.py                  ← Cylindrical mesh
├── baseline.py              ← Rankine vortex initialization
├── diagnostics.py           ← Metrics computation
└── interventions/
    ├── thermal_rfd.py
    └── momentum_sink.py
```

---

## ⚡ Quick Comparison

| Feature | Flask | Streamlit |
|---------|-------|-----------|
| **Startup Time** | ~2-3 seconds | ~10-15 seconds |
| **Memory Usage** | ~30-50 MB | ~100-150 MB |
| **UI Quality** | Clean, modern | Very polished |
| **Dependencies** | Flask only | Many packages |
| **Recommended For** | Mobile, Termux | Desktop systems |

---

## 🐛 Troubleshooting

**Port already in use:**
```bash
# Flask (default 5000)
python web_app.py --port 5001

# Streamlit (default 8501)
streamlit run app.py --server.port=8502
```

**Dashboard not loading:**
- Ensure you're in the `aeolus_sim/` directory
- Check that `solver.py`, `grid.py`, etc. exist
- Verify interventions/ folder is present

**Slow simulation:**
- Reduce grid size in `web_app.py` line 50: `grid_size=16`
- Reduce timesteps (use Duration slider)
- Use Flask instead of Streamlit

---

## 📝 Example Workflow

1. **Start dashboard:**
   ```bash
   python flaskrun.py
   ```

2. **Open browser:**
   - http://localhost:5000

3. **Adjust parameters:**
   - Vacuum: -250 Pa → -400 Pa (stronger suction)
   - Thermal: 3.0 K → 4.0 K (hotter injection)
   - Duration: 120 → 150 steps

4. **Click ACTIVATE DISRUPTOR**

5. **Watch live progress:**
   - Progress bar shows simulation advance
   - Metrics update in real-time

6. **View results:**
   - Final reduction % displayed
   - 4-panel chart with all metrics
   - Key statistics box

---

## 🎓 Understanding the Metrics

- **Vorticity Reduction (%)**: How much the tornado's rotation weakened
  - 0% = No suppression
  - 100% = Complete suppression
  - >100% = Sign reversal (vorticity reversed direction)

- **Core Vorticity**: Magnitude of rotation in tornado center (1/s)
  - Lower = weaker tornado

- **Max Velocity**: Fastest winds in simulation (m/s)
  - Lower = less powerful

- **Kinetic Energy**: Total moving air energy (J)
  - Lower = less dynamic activity

---

## 🔬 Physics Notes

The simulator uses:
- **Incompressible Navier-Stokes** in cylindrical coordinates
- **SIMPLE pressure-correction** scheme
- **Conservative central differences** for stability
- **Rankine vortex** baseline (EF4 tornado scale)
- **Coupled interventions**: Thermal RFD + Momentum Sink

Both interventions activate simultaneously for maximum suppression effect.

---

**Last Updated**: September 2026
**System**: AEOLUS v2.0
