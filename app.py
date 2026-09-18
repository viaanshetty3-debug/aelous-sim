#!/usr/bin/env python3
"""
AEOLUS Interactive Web Dashboard
Real-time visualization and control of tornado electromagnetic intervention system
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from collections import deque
import time

from grid import CylindricalGrid
from baseline import RankineVortex
from solver import NavierStokesSolver
from interventions import ThermalRFDIntervention, MomentumSinkIntervention
from diagnostics import Diagnostics


# ============================================================================
# PAGE CONFIG & INITIALIZATION
# ============================================================================

st.set_page_config(
    page_title="AEOLUS Disruptor Control",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main { padding-top: 0; }
    .stMetric { text-align: center; }
    .activate-button {
        background-color: #ff4444 !important;
        font-size: 24px !important;
        font-weight: bold !important;
        padding: 30px !important;
        border-radius: 10px !important;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if "simulation_state" not in st.session_state:
    st.session_state.simulation_state = None
if "results" not in st.session_state:
    st.session_state.results = None
if "simulation_running" not in st.session_state:
    st.session_state.simulation_running = False


# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================

def draw_vacuum_truck():
    """Draw ASCII-style vacuum truck layout."""
    truck_svg = """
    <svg width="100%" height="250" viewBox="0 0 500 250" style="border: 2px solid #333; border-radius: 8px; background: linear-gradient(to bottom, #e8f4f8, #f0f0f0);">
        <!-- Truck body -->
        <rect x="50" y="80" width="400" height="90" fill="#ff6b6b" stroke="#333" stroke-width="3" rx="10"/>

        <!-- Cabin -->
        <rect x="50" y="50" width="80" height="60" fill="#444" stroke="#333" stroke-width="2" rx="5"/>
        <circle cx="70" cy="75" r="8" fill="#87ceeb"/> <!-- Window -->

        <!-- Wheels -->
        <circle cx="100" cy="180" r="20" fill="#333" stroke="#111" stroke-width="2"/>
        <circle cx="350" cy="180" r="20" fill="#333" stroke="#111" stroke-width="2"/>

        <!-- Suction nozzle -->
        <line x1="420" y1="120" x2="450" y2="100" stroke="#333" stroke-width="4"/>
        <circle cx="455" cy="95" r="12" fill="#90ee90" stroke="#333" stroke-width="2"/>

        <!-- Active indicator -->
        <circle cx="455" cy="95" r="18" fill="none" stroke="#ff0000" stroke-width="2" opacity="0.7">
            <animate attributeName="r" values="18;25;18" dur="1.5s" repeatCount="indefinite"/>
            <animate attributeName="stroke-width" values="2;1;2" dur="1.5s" repeatCount="indefinite"/>
        </circle>

        <!-- Pressure gauge -->
        <rect x="250" y="100" width="60" height="60" fill="#fff" stroke="#333" stroke-width="2" rx="5"/>
        <text x="280" y="140" text-anchor="middle" font-size="12" font-weight="bold">-250 Pa</text>
        <text x="280" y="155" text-anchor="middle" font-size="10" fill="#666">Vacuum</text>
    </svg>
    """
    return truck_svg


def draw_thermal_grid():
    """Draw thermal heater grid deployment map."""
    grid_svg = """
    <svg width="100%" height="250" viewBox="0 0 500 250" style="border: 2px solid #333; border-radius: 8px; background: linear-gradient(135deg, #fff9e6, #fff0e6);">
        <!-- Title -->
        <text x="250" y="25" text-anchor="middle" font-size="16" font-weight="bold">Thermal Heater Grid (Top-Down View)</text>

        <!-- Grid background -->
        <rect x="50" y="50" width="400" height="150" fill="#f5f5f5" stroke="#999" stroke-width="1" stroke-dasharray="5,5"/>

        <!-- Heater elements (arranged in grid) -->
        <!-- Row 1 -->
        <circle cx="100" cy="80" r="15" fill="#ff4444" opacity="0.8" stroke="#ff0000" stroke-width="2">
            <animate attributeName="opacity" values="0.8;1;0.8" dur="2s" repeatCount="indefinite"/>
        </circle>
        <circle cx="180" cy="80" r="15" fill="#ff6666" opacity="0.7" stroke="#ff3333" stroke-width="2">
            <animate attributeName="opacity" values="0.7;0.9;0.7" dur="2.2s" repeatCount="indefinite"/>
        </circle>
        <circle cx="260" cy="80" r="15" fill="#ff4444" opacity="0.8" stroke="#ff0000" stroke-width="2">
            <animate attributeName="opacity" values="0.8;1;0.8" dur="2s" repeatCount="indefinite"/>
        </circle>
        <circle cx="340" cy="80" r="15" fill="#ff6666" opacity="0.7" stroke="#ff3333" stroke-width="2">
            <animate attributeName="opacity" values="0.7;0.9;0.7" dur="2.2s" repeatCount="indefinite"/>
        </circle>
        <circle cx="420" cy="80" r="15" fill="#ff4444" opacity="0.8" stroke="#ff0000" stroke-width="2">
            <animate attributeName="opacity" values="0.8;1;0.8" dur="2s" repeatCount="indefinite"/>
        </circle>

        <!-- Row 2 -->
        <circle cx="100" cy="150" r="15" fill="#ff6666" opacity="0.7" stroke="#ff3333" stroke-width="2">
            <animate attributeName="opacity" values="0.7;0.9;0.7" dur="2.2s" repeatCount="indefinite"/>
        </circle>
        <circle cx="180" cy="150" r="15" fill="#ff4444" opacity="0.8" stroke="#ff0000" stroke-width="2">
            <animate attributeName="opacity" values="0.8;1;0.8" dur="2s" repeatCount="indefinite"/>
        </circle>
        <circle cx="260" cy="150" r="15" fill="#ff9999" opacity="0.6" stroke="#ff6666" stroke-width="2">
            <animate attributeName="opacity" values="0.6;0.8;0.6" dur="2.3s" repeatCount="indefinite"/>
        </circle>
        <circle cx="340" cy="150" r="15" fill="#ff4444" opacity="0.8" stroke="#ff0000" stroke-width="2">
            <animate attributeName="opacity" values="0.8;1;0.8" dur="2s" repeatCount="indefinite"/>
        </circle>
        <circle cx="420" cy="150" r="15" fill="#ff6666" opacity="0.7" stroke="#ff3333" stroke-width="2">
            <animate attributeName="opacity" values="0.7;0.9;0.7" dur="2.2s" repeatCount="indefinite"/>
        </circle>

        <!-- Connection lines -->
        <line x1="100" y1="80" x2="180" y2="80" stroke="#999" stroke-width="1" stroke-dasharray="3,3" opacity="0.5"/>
        <line x1="180" y1="80" x2="260" y2="80" stroke="#999" stroke-width="1" stroke-dasharray="3,3" opacity="0.5"/>
        <line x1="260" y1="80" x2="340" y2="80" stroke="#999" stroke-width="1" stroke-dasharray="3,3" opacity="0.5"/>
        <line x1="340" y1="80" x2="420" y2="80" stroke="#999" stroke-width="1" stroke-dasharray="3,3" opacity="0.5"/>

        <!-- Temperature label -->
        <text x="250" y="220" text-anchor="middle" font-size="12" font-weight="bold" fill="#ff4444">Peak Anomaly: +3K</text>
    </svg>
    """
    return grid_svg


# ============================================================================
# SIMULATION ENGINE
# ============================================================================

class AeolusSimulator:
    """High-fidelity solver integration for AEOLUS system."""

    def __init__(self, vacuum_pressure: float, thermal_anomaly: float, grid_size: int = 32):
        """Initialize simulator with current parameters."""
        self.grid = CylindricalGrid(nx=grid_size, ntheta=grid_size, nz=grid_size)
        rankine = RankineVortex(grid=self.grid, core_radius=500, max_velocity=90, add_shear=True)
        self.u_r, self.u_theta, self.u_z, self.p = rankine.initialize()
        self.baseline_vorticity = rankine.compute_core_vorticity(self.u_theta)

        self.solver = NavierStokesSolver(
            grid=self.grid, dt=0.05,
            enable_shear=True, enable_lhr=True, enable_precip=True
        )
        self.diagnostics = Diagnostics(grid=self.grid, baseline_vorticity=self.baseline_vorticity)

        self.vacuum_pressure = vacuum_pressure
        self.thermal_anomaly = thermal_anomaly
        self.step = 0
        self.history = {
            "steps": [],
            "vorticity": [],
            "reduction": [],
            "velocity": [],
            "energy": []
        }

        self._create_interventions()

    def _create_interventions(self):
        """Create intervention modules."""
        self.interventions = []

        # Thermal RFD with adjustable anomaly
        self.interventions.append(
            ThermalRFDIntervention(
                grid=self.grid,
                peak_anomaly=self.thermal_anomaly,
                active_duration_steps=50,
                decay_duration_steps=40,
            )
        )

        # Momentum sink with adjustable pressure
        self.interventions.append(
            MomentumSinkIntervention(
                grid=self.grid,
                pressure_deficit=self.vacuum_pressure
            )
        )

    def step(self) -> dict:
        """Execute one simulation step."""
        # Apply interventions
        for intervention in self.interventions:
            self.u_r, self.u_theta, self.u_z, self.p = intervention.apply(
                self.u_r, self.u_theta, self.u_z, self.p, step=self.step
            )

        # Solve Navier-Stokes
        self.u_r, self.u_theta, self.u_z, self.p = self.solver.step(
            self.u_r, self.u_theta, self.u_z, self.p
        )

        # Compute diagnostics
        metrics = self.diagnostics.compute(self.u_r, self.u_theta, self.u_z, self.p, step=self.step)

        # Store history
        self.history["steps"].append(self.step)
        self.history["vorticity"].append(metrics.get("core_vorticity", 0))
        self.history["reduction"].append(metrics.get("vorticity_reduction_pct", 0))
        self.history["velocity"].append(metrics.get("max_velocity", 0))
        self.history["energy"].append(metrics.get("kinetic_energy", 0))

        self.step += 1
        return metrics


def run_simulation(vacuum_pressure: float, thermal_anomaly: float, max_steps: int = 120):
    """Run full simulation and return results."""
    simulator = AeolusSimulator(vacuum_pressure, thermal_anomaly, grid_size=32)

    progress_bar = st.progress(0)
    status_text = st.empty()

    for step in range(max_steps):
        metrics = simulator.step()

        # Update UI
        progress = (step + 1) / max_steps
        progress_bar.progress(progress)
        status_text.text(f"⚡ Simulation running... Step {step + 1}/{max_steps} | "
                        f"Reduction: {metrics.get('vorticity_reduction_pct', 0):.1f}%")

        time.sleep(0.01)  # Small delay for visual feedback

    progress_bar.empty()
    status_text.empty()

    return simulator.history


def create_results_chart(history: dict) -> go.Figure:
    """Create comprehensive results visualization."""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Core Vorticity Reduction (%)", "Core Vorticity (1/s)",
                       "Maximum Velocity (m/s)", "Kinetic Energy (J)"),
        specs=[[{"type": "scatter"}, {"type": "scatter"}],
               [{"type": "scatter"}, {"type": "scatter"}]]
    )

    # Vorticity Reduction (primary metric)
    fig.add_trace(
        go.Scatter(
            x=history["steps"],
            y=history["reduction"],
            mode="lines+markers",
            name="Vorticity Reduction",
            line=dict(color="#ff4444", width=3),
            marker=dict(size=4),
            fill="tozeroy",
            fillcolor="rgba(255, 68, 68, 0.2)"
        ),
        row=1, col=1
    )
    fig.add_hline(y=100, line_dash="dash", line_color="green", row=1, col=1,
                  annotation_text="100% Suppression", annotation_position="right")

    # Core Vorticity
    fig.add_trace(
        go.Scatter(
            x=history["steps"],
            y=history["vorticity"],
            mode="lines+markers",
            name="Core Vorticity",
            line=dict(color="#4488ff", width=2),
            marker=dict(size=3)
        ),
        row=1, col=2
    )

    # Max Velocity
    fig.add_trace(
        go.Scatter(
            x=history["steps"],
            y=history["velocity"],
            mode="lines+markers",
            name="Max Velocity",
            line=dict(color="#ff9944", width=2),
            marker=dict(size=3)
        ),
        row=2, col=1
    )

    # Kinetic Energy
    fig.add_trace(
        go.Scatter(
            x=history["steps"],
            y=history["energy"],
            mode="lines+markers",
            name="Kinetic Energy",
            line=dict(color="#44ff44", width=2),
            marker=dict(size=3)
        ),
        row=2, col=2
    )

    # Update layout
    fig.update_xaxes(title_text="Time Step", row=1, col=1)
    fig.update_xaxes(title_text="Time Step", row=1, col=2)
    fig.update_xaxes(title_text="Time Step", row=2, col=1)
    fig.update_xaxes(title_text="Time Step", row=2, col=2)

    fig.update_yaxes(title_text="Reduction (%)", row=1, col=1)
    fig.update_yaxes(title_text="Vorticity (1/s)", row=1, col=2)
    fig.update_yaxes(title_text="Velocity (m/s)", row=2, col=1)
    fig.update_yaxes(title_text="Energy (J)", row=2, col=2)

    fig.update_layout(
        height=800,
        title_text="AEOLUS Intervention Results - Tornado Disruption Analysis",
        hovermode="x unified",
        showlegend=True
    )

    return fig


# ============================================================================
# MAIN UI
# ============================================================================

# Header
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 10px; color: white;">
        <h1>⚡ AEOLUS DISRUPTOR CONTROL ⚡</h1>
        <p style="font-size: 14px; margin: 5px;">Electromagnetic Tornado Intervention System</p>
        <p style="font-size: 12px; color: #ddd;">High-Fidelity Navier-Stokes Solver | Real-Time Physics Simulation</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Hardware Visualization Section
st.subheader("🚗 Physical Hardware Deployment")
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Vacuum Suction Truck (Mobile Unit)**")
    st.markdown(draw_vacuum_truck(), unsafe_allow_html=True)

with col2:
    st.markdown("**Thermal Heater Grid (Stationary Network)**")
    st.markdown(draw_thermal_grid(), unsafe_allow_html=True)

st.markdown("---")

# Control Panel
st.subheader("🎮 Intervention Parameters")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Vacuum Suction Force**")
    vacuum_pressure = st.slider(
        "Pressure Deficit (Pa)",
        min_value=-500,
        max_value=-100,
        value=-250,
        step=25,
        label_visibility="collapsed"
    )
    st.metric("Current Vacuum", f"{vacuum_pressure} Pa", delta=f"{vacuum_pressure - (-250)} Pa")

with col2:
    st.markdown("**Thermal Anomaly Strength**")
    thermal_anomaly = st.slider(
        "Temperature Anomaly (K)",
        min_value=0.5,
        max_value=5.0,
        value=3.0,
        step=0.5,
        label_visibility="collapsed"
    )
    st.metric("Current Anomaly", f"{thermal_anomaly:.1f} K", delta=f"{thermal_anomaly - 3.0:.1f} K")

with col3:
    st.markdown("**Simulation Duration**")
    max_steps = st.slider(
        "Time Steps",
        min_value=30,
        max_value=200,
        value=120,
        step=10,
        label_visibility="collapsed"
    )
    st.metric("Duration", f"{max_steps * 0.05:.1f} s", delta=f"{max_steps} steps @ 0.05 s/step")

st.markdown("---")

# Activation Section
st.subheader("🎯 Initiate Intervention")

col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    if st.button(
        "🔴 ACTIVATE DISRUPTOR 🔴",
        key="activate_button",
        use_container_width=True,
        type="primary"
    ):
        st.session_state.simulation_running = True

        with st.spinner("⚙️ Initializing solver..."):
            time.sleep(0.5)

        st.success("✓ Solver initialized")
        st.info(f"Running simulation with: Vacuum = {vacuum_pressure} Pa | Thermal = {thermal_anomaly:.1f} K")

        # Run simulation
        results = run_simulation(vacuum_pressure, thermal_anomaly, max_steps)
        st.session_state.results = results
        st.session_state.simulation_running = False
        st.success("✓ Simulation complete!")

st.markdown("---")

# Results Section
if st.session_state.results:
    st.subheader("📊 Real-Time Results Analysis")

    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)

    history = st.session_state.results
    final_reduction = history["reduction"][-1]
    peak_reduction = max(history["reduction"])
    final_vorticity = history["vorticity"][-1]
    peak_velocity = max(history["velocity"])

    with col1:
        st.metric(
            "Final Reduction",
            f"{final_reduction:.2f}%",
            delta=f"+{final_reduction - 100:.2f}%" if final_reduction > 100 else f"{final_reduction - 100:.2f}%",
            delta_color="off"
        )

    with col2:
        st.metric(
            "Peak Reduction",
            f"{peak_reduction:.2f}%",
            delta="Above 100%" if peak_reduction > 100 else "Below 100%"
        )

    with col3:
        st.metric(
            "Final Core Vorticity",
            f"{final_vorticity:.3f} 1/s",
            delta=f"{final_vorticity - history['vorticity'][0]:.3f} 1/s",
            delta_color="inverse"
        )

    with col4:
        st.metric(
            "Peak Velocity",
            f"{peak_velocity:.1f} m/s",
            delta=f"{peak_velocity - history['velocity'][0]:.1f} m/s",
            delta_color="inverse"
        )

    # Interactive Chart
    st.plotly_chart(create_results_chart(history), use_container_width=True, key="results_chart")

    # Summary Statistics
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Intervention Summary")
        st.write(f"""
        - **Initial Core Vorticity**: {history['vorticity'][0]:.4f} 1/s
        - **Final Core Vorticity**: {history['vorticity'][-1]:.4f} 1/s
        - **Total Reduction**: {final_reduction:.2f}%
        - **Peak Reduction**: {peak_reduction:.2f}% (at step {history['reduction'].index(peak_reduction)})
        - **Simulation Time**: {max_steps * 0.05:.1f} seconds
        """)

    with col2:
        st.subheader("Physical Parameters")
        st.write(f"""
        - **Vacuum Pressure**: {vacuum_pressure} Pa
        - **Thermal Anomaly**: {thermal_anomaly:.1f} K
        - **Grid Resolution**: 32³ cells
        - **Time Step**: 0.05 s
        - **Total Steps**: {max_steps}
        """)

else:
    if not st.session_state.simulation_running:
        st.info("👈 Click the **ACTIVATE DISRUPTOR** button to run the simulation")

st.markdown("---")

# Footer
st.markdown("""
<div style="text-align: center; color: #666; font-size: 12px; padding: 20px;">
    <p><strong>AEOLUS</strong> - Atmospheric Electromagnetic Tornado Disruption System</p>
    <p>High-Fidelity Navier-Stokes Solver | Cylindrical Coordinates (r, θ, z) | Incompressible Flow</p>
    <p style="color: #999;">Thermal RFD + Momentum Sink Interventions | Real-Time Dashboard</p>
</div>
""", unsafe_allow_html=True)
