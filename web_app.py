#!/usr/bin/env python3
"""
AEOLUS Flask Web Dashboard - Lightweight alternative to Streamlit
Runs on any system with Python + Flask
"""

from flask import Flask, render_template_string, request, jsonify
import numpy as np
import json
from pathlib import Path
import sys
import threading

from grid import CylindricalGrid
from baseline import RankineVortex
from solver import NavierStokesSolver
from interventions import ThermalRFDIntervention, MomentumSinkIntervention
from diagnostics import Diagnostics


app = Flask(__name__)

# Global simulation state
simulation_state = {
    "running": False,
    "step": 0,
    "max_steps": 120,
    "progress": 0,
    "history": {
        "steps": [],
        "vorticity": [],
        "reduction": [],
        "velocity": [],
        "energy": []
    },
    "last_metrics": {}
}


class AeolusSimulator:
    """High-fidelity solver integration."""

    def __init__(self, vacuum_pressure: float, thermal_anomaly: float, grid_size: int = 32):
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

        self._create_interventions()

    def _create_interventions(self):
        self.interventions = []
        self.interventions.append(
            ThermalRFDIntervention(
                grid=self.grid,
                peak_anomaly=self.thermal_anomaly,
                active_duration_steps=50,
                decay_duration_steps=40,
            )
        )
        self.interventions.append(
            MomentumSinkIntervention(
                grid=self.grid,
                pressure_deficit=self.vacuum_pressure
            )
        )

    def step(self) -> dict:
        for intervention in self.interventions:
            self.u_r, self.u_theta, self.u_z, self.p = intervention.apply(
                self.u_r, self.u_theta, self.u_z, self.p, step=self.step
            )

        self.u_r, self.u_theta, self.u_z, self.p = self.solver.step(
            self.u_r, self.u_theta, self.u_z, self.p
        )

        metrics = self.diagnostics.compute(self.u_r, self.u_theta, self.u_z, self.p, step=self.step)
        self.step += 1
        return metrics


def run_simulation(vacuum_pressure, thermal_anomaly, max_steps):
    """Run simulation in background thread."""
    global simulation_state

    simulation_state["running"] = True
    simulation_state["step"] = 0
    simulation_state["max_steps"] = max_steps
    simulation_state["history"] = {
        "steps": [],
        "vorticity": [],
        "reduction": [],
        "velocity": [],
        "energy": []
    }

    simulator = AeolusSimulator(vacuum_pressure, thermal_anomaly, grid_size=32)

    for step in range(max_steps):
        if not simulation_state["running"]:
            break

        metrics = simulator.step()

        simulation_state["step"] = step + 1
        simulation_state["progress"] = int(100 * (step + 1) / max_steps)
        simulation_state["last_metrics"] = metrics

        # Store history
        simulation_state["history"]["steps"].append(step)
        simulation_state["history"]["vorticity"].append(metrics.get("core_vorticity", 0))
        simulation_state["history"]["reduction"].append(metrics.get("vorticity_reduction_pct", 0))
        simulation_state["history"]["velocity"].append(metrics.get("max_velocity", 0))
        simulation_state["history"]["energy"].append(metrics.get("kinetic_energy", 0))

    simulation_state["running"] = False


# ============================================================================
# ROUTES
# ============================================================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AEOLUS Disruptor Control</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
        }

        .header h1 {
            font-size: 48px;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }

        .header p {
            font-size: 16px;
            opacity: 0.9;
        }

        .content {
            padding: 40px;
        }

        .section {
            margin-bottom: 40px;
        }

        .section-title {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 20px;
            color: #333;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }

        .hardware-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 40px;
        }

        .hardware-box {
            border: 2px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            background: #f9f9f9;
        }

        .hardware-box h3 {
            margin-bottom: 15px;
            color: #667eea;
        }

        .truck-visual, .grid-visual {
            width: 100%;
            height: 200px;
            background: linear-gradient(to bottom, #e8f4f8, #f0f0f0);
            border: 1px solid #ccc;
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            color: #666;
        }

        .controls-grid {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 30px;
            margin-bottom: 40px;
        }

        .control-box {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            background: #f5f5f5;
        }

        .control-box label {
            display: block;
            font-weight: bold;
            margin-bottom: 10px;
            color: #333;
        }

        input[type="range"] {
            width: 100%;
            height: 6px;
            margin-bottom: 10px;
            cursor: pointer;
        }

        .control-value {
            font-size: 20px;
            font-weight: bold;
            color: #667eea;
            text-align: center;
            padding: 10px;
            background: white;
            border-radius: 6px;
            border: 1px solid #ddd;
        }

        .button-container {
            text-align: center;
            margin: 40px 0;
        }

        .activate-btn {
            background: linear-gradient(135deg, #ff4444, #cc0000);
            color: white;
            border: none;
            padding: 20px 60px;
            font-size: 24px;
            font-weight: bold;
            border-radius: 8px;
            cursor: pointer;
            box-shadow: 0 6px 20px rgba(255, 0, 0, 0.4);
            transition: all 0.3s;
        }

        .activate-btn:hover:not(:disabled) {
            transform: scale(1.05);
            box-shadow: 0 8px 30px rgba(255, 0, 0, 0.6);
        }

        .activate-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }

        .progress-container {
            margin: 20px 0;
            display: none;
        }

        .progress-bar {
            width: 100%;
            height: 30px;
            background: #e0e0e0;
            border-radius: 6px;
            overflow: hidden;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            width: 0%;
            transition: width 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 12px;
        }

        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }

        .metric-box {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }

        .metric-value {
            font-size: 32px;
            font-weight: bold;
            margin: 10px 0;
        }

        .metric-label {
            font-size: 12px;
            opacity: 0.9;
        }

        .chart-container {
            width: 100%;
            height: 600px;
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            margin-bottom: 30px;
        }

        .footer {
            background: #f5f5f5;
            padding: 20px;
            text-align: center;
            color: #666;
            font-size: 12px;
            border-top: 1px solid #ddd;
        }

        @media (max-width: 900px) {
            .hardware-grid, .controls-grid, .metrics-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚡ AEOLUS DISRUPTOR CONTROL ⚡</h1>
            <p>Electromagnetic Tornado Intervention System</p>
            <p style="font-size: 12px; margin-top: 10px;">High-Fidelity Navier-Stokes Solver | Real-Time Physics Simulation</p>
        </div>

        <div class="content">
            <!-- Hardware Section -->
            <div class="section">
                <div class="section-title">🚗 Physical Hardware Deployment</div>
                <div class="hardware-grid">
                    <div class="hardware-box">
                        <h3>Vacuum Suction Truck</h3>
                        <div class="truck-visual">
                            🚛 Mobile Unit<br>(-250 Pa Pressure)
                        </div>
                    </div>
                    <div class="hardware-box">
                        <h3>Thermal Heater Grid</h3>
                        <div class="grid-visual">
                            🔥 5×2 Array<br>(+3K Anomaly)
                        </div>
                    </div>
                </div>
            </div>

            <!-- Controls Section -->
            <div class="section">
                <div class="section-title">🎮 Intervention Parameters</div>
                <div class="controls-grid">
                    <div class="control-box">
                        <label for="vacuum">Vacuum Suction Force (Pa)</label>
                        <input type="range" id="vacuum" min="-500" max="-100" value="-250" step="25">
                        <div class="control-value" id="vacuum-value">-250 Pa</div>
                    </div>
                    <div class="control-box">
                        <label for="thermal">Thermal Anomaly (K)</label>
                        <input type="range" id="thermal" min="0.5" max="5.0" value="3.0" step="0.5">
                        <div class="control-value" id="thermal-value">3.0 K</div>
                    </div>
                    <div class="control-box">
                        <label for="steps">Simulation Duration (steps)</label>
                        <input type="range" id="steps" min="30" max="200" value="120" step="10">
                        <div class="control-value" id="steps-value">120 steps (~6s)</div>
                    </div>
                </div>
            </div>

            <!-- Activation Section -->
            <div class="section">
                <div class="section-title">🎯 Initiate Intervention</div>
                <div class="button-container">
                    <button class="activate-btn" id="activate-btn" onclick="activateDisruptor()">
                        🔴 ACTIVATE DISRUPTOR 🔴
                    </button>
                </div>
                <div class="progress-container" id="progress-container">
                    <div class="progress-bar">
                        <div class="progress-fill" id="progress-fill">0%</div>
                    </div>
                </div>
            </div>

            <!-- Results Section -->
            <div class="section" id="results-section" style="display:none;">
                <div class="section-title">📊 Real-Time Results Analysis</div>

                <div class="metrics-grid">
                    <div class="metric-box">
                        <div class="metric-label">Final Reduction</div>
                        <div class="metric-value" id="metric-reduction">—</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-label">Peak Reduction</div>
                        <div class="metric-value" id="metric-peak">—</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-label">Final Vorticity</div>
                        <div class="metric-value" id="metric-vorticity">—</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-label">Peak Velocity</div>
                        <div class="metric-value" id="metric-velocity">—</div>
                    </div>
                </div>

                <div class="chart-container">
                    <div id="chart"></div>
                </div>
            </div>
        </div>

        <div class="footer">
            <p><strong>AEOLUS</strong> - Atmospheric Electromagnetic Tornado Disruption System</p>
            <p>High-Fidelity Navier-Stokes Solver | Cylindrical Coordinates (r, θ, z) | Real-Time Dashboard</p>
        </div>
    </div>

    <script>
        // Update display values
        document.getElementById('vacuum').addEventListener('input', function() {
            document.getElementById('vacuum-value').textContent = this.value + ' Pa';
        });

        document.getElementById('thermal').addEventListener('input', function() {
            document.getElementById('thermal-value').textContent = parseFloat(this.value).toFixed(1) + ' K';
        });

        document.getElementById('steps').addEventListener('input', function() {
            const time = (this.value * 0.05).toFixed(1);
            document.getElementById('steps-value').textContent = this.value + ' steps (~' + time + 's)';
        });

        // Polling for simulation status
        let pollInterval;

        function pollStatus() {
            fetch('/api/status')
                .then(r => r.json())
                .then(data => {
                    if (data.running) {
                        document.getElementById('progress-fill').style.width = data.progress + '%';
                        document.getElementById('progress-fill').textContent = data.progress + '%';
                    } else if (data.history && data.history.steps.length > 0) {
                        updateResults(data.history);
                        clearInterval(pollInterval);
                        document.getElementById('activate-btn').disabled = false;
                    }
                });
        }

        function activateDisruptor() {
            const vacuum = document.getElementById('vacuum').value;
            const thermal = document.getElementById('thermal').value;
            const steps = document.getElementById('steps').value;

            document.getElementById('activate-btn').disabled = true;
            document.getElementById('progress-container').style.display = 'block';
            document.getElementById('progress-fill').style.width = '0%';
            document.getElementById('progress-fill').textContent = '0%';

            fetch('/api/simulate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    vacuum_pressure: parseFloat(vacuum),
                    thermal_anomaly: parseFloat(thermal),
                    max_steps: parseInt(steps)
                })
            }).then(r => r.json()).then(data => {
                if (data.success) {
                    pollInterval = setInterval(pollStatus, 500);
                }
            });
        }

        function updateResults(history) {
            const reduction = history.reduction;
            const vorticity = history.vorticity;
            const velocity = history.velocity;

            document.getElementById('metric-reduction').textContent = reduction[reduction.length - 1].toFixed(2) + '%';
            document.getElementById('metric-peak').textContent = Math.max(...reduction).toFixed(2) + '%';
            document.getElementById('metric-vorticity').textContent = vorticity[vorticity.length - 1].toFixed(4);
            document.getElementById('metric-velocity').textContent = Math.max(...velocity).toFixed(1) + ' m/s';

            document.getElementById('results-section').style.display = 'block';
            document.getElementById('progress-container').style.display = 'none';

            // Plot chart
            const trace1 = {x: history.steps, y: reduction, name: 'Vorticity Reduction', type: 'scatter', mode: 'lines+markers', line: {color: '#ff4444', width: 3}};
            const trace2 = {x: history.steps, y: vorticity, name: 'Core Vorticity', type: 'scatter', mode: 'lines', line: {color: '#4488ff'}, yaxis: 'y2'};

            Plotly.newPlot('chart', [trace1, trace2], {
                xaxis: {title: 'Time Step'},
                yaxis: {title: 'Reduction (%)', titlefont: {color: '#ff4444'}, tickfont: {color: '#ff4444'}},
                yaxis2: {title: 'Vorticity (1/s)', titlefont: {color: '#4488ff'}, tickfont: {color: '#4488ff'}, overlaying: 'y', side: 'right'},
                hovermode: 'x unified',
                plot_bgcolor: '#fafafa'
            });
        }
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/simulate', methods=['POST'])
def simulate():
    """Start simulation in background thread."""
    data = request.json
    vacuum = data.get('vacuum_pressure', -250)
    thermal = data.get('thermal_anomaly', 3.0)
    steps = data.get('max_steps', 120)

    if not simulation_state["running"]:
        thread = threading.Thread(
            target=run_simulation,
            args=(vacuum, thermal, steps),
            daemon=True
        )
        thread.start()
        return jsonify({"success": True})

    return jsonify({"success": False, "error": "Simulation already running"})


@app.route('/api/status')
def status():
    """Get simulation status."""
    return jsonify(simulation_state)


if __name__ == '__main__':
    print("\n" + "="*75)
    print("  ⚡ AEOLUS FLASK WEB DASHBOARD ⚡")
    print("="*75)
    print("\n📍 Starting Flask server...")
    print("   Open browser to: http://localhost:5000")
    print("   Press Ctrl+C to stop\n")
    print("="*75 + "\n")

    try:
        app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print("\n\n✓ Server stopped by user")
