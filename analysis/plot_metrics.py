"""Plot time-series diagnostics from simulation output."""

import json
import sys
from pathlib import Path

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None


def main():
    if len(sys.argv) < 2:
        print("Usage: python plot_metrics.py <output_dir>")
        sys.exit(1)

    output_dir = Path(sys.argv[1])
    summary_path = output_dir / "summary.json"

    if not summary_path.exists():
        print(f"Error: {summary_path} not found")
        sys.exit(1)

    with open(summary_path) as f:
        summary = json.load(f)

    if plt is None:
        print("matplotlib not installed; skipping plots")
        return

    # Plot time series
    time_series = summary.get("time_series", {})
    if not time_series:
        print("No time series data found")
        return

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle("Vortex Disruption Diagnostics")

    keys = list(time_series.keys())
    for idx, (ax, key) in enumerate(zip(axes.flat, keys)):
        values = time_series[key]
        ax.plot(values, marker=".")
        ax.set_xlabel("Step")
        ax.set_ylabel(key)
        ax.grid(True)

    plt.tight_layout()
    plot_path = output_dir / "metrics.png"
    plt.savefig(plot_path, dpi=100)
    print(f"Plot saved to {plot_path}")


if __name__ == "__main__":
    main()
