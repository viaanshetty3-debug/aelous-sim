"""Output management: checkpointing, HDF5 export, summary reports."""

import json
from pathlib import Path

import numpy as np

try:
    import h5py
except ImportError:
    h5py = None


class OutputManager:
    """Handle simulation output: checkpoints, diagnostics, and summary export."""

    def __init__(self, output_dir: Path, checkpoint_interval: int = 10):
        """Initialize output manager.

        Args:
            output_dir: directory for output files
            checkpoint_interval: save full fields every N steps
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint_interval = checkpoint_interval
        self.metrics_log = {}

    def checkpoint(self, step: int, u_r, u_theta, u_z, p, metrics: dict):
        """Save checkpoint at current step.

        Args:
            step: time step index
            u_r, u_theta, u_z, p: flow fields
            metrics: diagnostic metrics dictionary
        """
        # Log metrics to dictionary
        for key, val in metrics.items():
            if key not in self.metrics_log:
                self.metrics_log[key] = []
            self.metrics_log[key].append(float(val))

        # Optionally save full fields to HDF5
        if step % self.checkpoint_interval == 0:
            if h5py is not None:
                self._save_hdf5(step, u_r, u_theta, u_z, p, metrics)

    def _save_hdf5(self, step: int, u_r, u_theta, u_z, p, metrics: dict):
        """Save fields to HDF5 checkpoint."""
        checkpoint_path = self.output_dir / f"checkpoint_{step:06d}.h5"
        try:
            with h5py.File(checkpoint_path, "w") as f:
                f.create_dataset("u_r", data=u_r)
                f.create_dataset("u_theta", data=u_theta)
                f.create_dataset("u_z", data=u_z)
                f.create_dataset("p", data=p)
                # Store metrics as attributes
                for key, val in metrics.items():
                    f.attrs[key] = float(val)
        except Exception as e:
            print(f"Warning: HDF5 checkpoint failed: {e}")

    def summarize(self, diagnostics) -> dict:
        """Generate final summary report.

        Args:
            diagnostics: Diagnostics instance with history

        Returns:
            Summary dictionary
        """
        summary = {
            "final_metrics": {},
            "time_series": self.metrics_log,
            "vorticity_evolution": [],
        }

        # Final values
        for key, values in self.metrics_log.items():
            if len(values) > 0:
                summary["final_metrics"][key] = values[-1]

        # Save to JSON
        summary_path = self.output_dir / "summary.json"
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)

        # Also save as text
        self._write_text_summary(summary)

        return summary

    def _write_text_summary(self, summary: dict):
        """Write human-readable summary."""
        text_path = self.output_dir / "summary.txt"
        with open(text_path, "w") as f:
            f.write("=" * 60 + "\n")
            f.write("AEOLUS VORTEX DISRUPTION SIMULATION SUMMARY\n")
            f.write("=" * 60 + "\n\n")

            f.write("FINAL METRICS:\n")
            for key, val in summary["final_metrics"].items():
                f.write(f"  {key}: {val:.6e}\n")

            f.write("\nSUCCESS CRITERIA:\n")
            final_vort = summary["final_metrics"].get("core_vorticity", 0)
            if final_vort > 0:
                f.write(f"  Core vorticity reduction: {final_vort:.1f}%\n")
            f.write("\n")
