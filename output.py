"""Output management: checkpointing, HDF5 export, summary reports."""

import json
from pathlib import Path

import numpy as np

try:
    import h5py
    HAS_H5PY = True
except ImportError:
    HAS_H5PY = False


class OutputManager:
    """Handle simulation output: checkpoints, diagnostics, and summary export."""

    def __init__(self, output_dir: Path, checkpoint_interval: int = 20):
        """Initialize output manager.

        Args:
            output_dir: directory for output files
            checkpoint_interval: save full fields every N steps
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint_interval = checkpoint_interval
        self.metrics_log = {}
        self.step_count = 0

    def checkpoint(self, step: int, u_r, u_theta, u_z, p, metrics: dict):
        """Save checkpoint at current step.

        Args:
            step: time step index
            u_r, u_theta, u_z, p: flow fields
            metrics: diagnostic metrics dictionary
        """
        self.step_count = step

        # Log metrics to dictionary
        for key, val in metrics.items():
            if key not in self.metrics_log:
                self.metrics_log[key] = []
            self.metrics_log[key].append(float(val))

        # Optionally save full fields to HDF5
        if step % self.checkpoint_interval == 0:
            if HAS_H5PY:
                self._save_hdf5(step, u_r, u_theta, u_z, p, metrics)

    def _save_hdf5(self, step: int, u_r, u_theta, u_z, p, metrics: dict):
        """Save fields to HDF5 checkpoint."""
        checkpoint_path = self.output_dir / f"checkpoint_{step:06d}.h5"
        try:
            with h5py.File(checkpoint_path, "w") as f:
                f.create_dataset("u_r", data=u_r, compression="gzip", compression_opts=4)
                f.create_dataset("u_theta", data=u_theta, compression="gzip", compression_opts=4)
                f.create_dataset("u_z", data=u_z, compression="gzip", compression_opts=4)
                f.create_dataset("p", data=p, compression="gzip", compression_opts=4)
                # Store metrics as attributes
                for key, val in metrics.items():
                    try:
                        f.attrs[key] = float(val)
                    except (TypeError, ValueError):
                        pass
        except Exception as e:
            print(f"Warning: HDF5 checkpoint failed: {e}")

    def summarize(self, diagnostics, grid) -> dict:
        """Generate final summary report.

        Args:
            diagnostics: Diagnostics instance with history
            grid: CylindricalGrid instance

        Returns:
            Summary dictionary
        """
        summary = {
            "n_steps": self.step_count,
            "grid_shape": [grid.nx, grid.ntheta, grid.nz],
            "grid_params": {
                "r_min": float(grid.r_min),
                "r_max": float(grid.r_max),
                "z_max": float(grid.z_max),
            },
            "final_metrics": {},
            "time_series": self.metrics_log,
        }

        # Final values
        for key, values in self.metrics_log.items():
            if len(values) > 0:
                summary["final_metrics"][key] = values[-1]

        # Vorticity reduction
        reduction = diagnostics.vorticity_reduction()
        summary["final_metrics"]["vorticity_reduction_pct_final"] = reduction

        # Reformation check
        reformation = diagnostics.check_reformation()
        summary["reformation_detected"] = bool(reformation)

        # Save to JSON
        summary_path = self.output_dir / "summary.json"
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)

        # Also save as text
        self._write_text_summary(summary, diagnostics)

        return summary

    def _write_text_summary(self, summary: dict, diagnostics):
        """Write human-readable summary."""
        text_path = self.output_dir / "summary.txt"
        with open(text_path, "w") as f:
            f.write("=" * 70 + "\n")
            f.write("AEOLUS VORTEX DISRUPTION SIMULATION SUMMARY\n")
            f.write("=" * 70 + "\n\n")

            f.write("SIMULATION PARAMETERS:\n")
            f.write(f"  Total steps: {summary['n_steps']}\n")
            f.write(f"  Grid shape (r, θ, z): {summary['grid_shape']}\n")
            f.write(f"  Domain: r=[{summary['grid_params']['r_min']:.0f}, {summary['grid_params']['r_max']:.0f}] m, "
                   f"z=[0, {summary['grid_params']['z_max']:.0f}] m\n\n")

            f.write("FINAL METRICS:\n")
            final = summary["final_metrics"]
            if "core_vorticity" in final:
                f.write(f"  Core vorticity: {final['core_vorticity']:8.3f} 1/s\n")
            if "max_velocity" in final:
                f.write(f"  Maximum velocity: {final['max_velocity']:8.2f} m/s\n")
            if "circulation" in final:
                f.write(f"  Circulation: {final['circulation']:8.1f} m²/s\n")
            if "kinetic_energy" in final:
                f.write(f"  Kinetic energy: {final['kinetic_energy']:12.1f} J\n")
            if "divergence_rms" in final:
                f.write(f"  Divergence RMS: {final['divergence_rms']:.2e} (should be << 1)\n")

            f.write("\nVORTEX DISRUPTION SUCCESS METRICS:\n")
            if "vorticity_reduction_pct_final" in final:
                reduction = final["vorticity_reduction_pct_final"]
                f.write(f"  Core vorticity reduction: {reduction:6.1f}%\n")
                if reduction >= 70.0:
                    f.write(f"  ✓ TARGET ACHIEVED: ≥70% reduction\n")
                else:
                    f.write(f"  ✗ Target not met (need 70%)\n")

            f.write("\nREFORMATION CHECK:\n")
            if summary["reformation_detected"]:
                f.write(f"  ✗ VORTEX REFORMATION DETECTED (threshold: 20%)\n")
            else:
                f.write(f"  ✓ No reformation detected (vortex remains suppressed)\n")

            f.write("\nTIME SERIES EVOLUTION:\n")
            if "core_vorticity" in summary["time_series"]:
                vorticities = summary["time_series"]["core_vorticity"]
                if len(vorticities) > 1:
                    initial = vorticities[0]
                    final = vorticities[-1]
                    f.write(f"  Initial core vorticity: {initial:8.3f} 1/s\n")
                    f.write(f"  Final core vorticity:   {final:8.3f} 1/s\n")
                    f.write(f"  Change: {final - initial:+8.3f} 1/s\n")

            f.write("\n" + "=" * 70 + "\n")
            f.write("OUTPUT FILES:\n")
            f.write(f"  Summary (JSON): summary.json\n")
            f.write(f"  This report: summary.txt\n")
            f.write(f"  Checkpoints: checkpoint_*.h5 (if h5py available)\n")
            f.write("=" * 70 + "\n")
