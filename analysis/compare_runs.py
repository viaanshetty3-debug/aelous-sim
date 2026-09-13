"""Compare multiple simulation runs."""

import json
import sys
from pathlib import Path

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None


def main():
    if len(sys.argv) < 2:
        print("Usage: python compare_runs.py <run1> <run2> [run3 ...]")
        sys.exit(1)

    run_dirs = [Path(d) for d in sys.argv[1:]]
    summaries = {}

    for run_dir in run_dirs:
        summary_path = run_dir / "summary.json"
        if summary_path.exists():
            with open(summary_path) as f:
                summaries[run_dir.name] = json.load(f)

    if not summaries:
        print("No summary files found")
        sys.exit(1)

    if plt is None:
        print("matplotlib not installed; skipping plots")
        return

    # Compare vorticity evolution
    fig, ax = plt.subplots(figsize=(10, 6))
    for name, summary in summaries.items():
        time_series = summary.get("time_series", {})
        vort = time_series.get("core_vorticity", [])
        if vort:
            ax.plot(vort, label=name, marker=".")

    ax.set_xlabel("Step")
    ax.set_ylabel("Core Vorticity (s⁻¹)")
    ax.legend()
    ax.grid(True)
    fig.suptitle("Vorticity Comparison")
    plt.tight_layout()

    plot_path = Path("comparison.png")
    plt.savefig(plot_path, dpi=100)
    print(f"Comparison plot saved to {plot_path}")


if __name__ == "__main__":
    main()
