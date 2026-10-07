"""Compare metrics across multiple AEOLUS simulation runs.

Extracts summary statistics from checkpoint files and generates
a comprehensive comparison table across initialization modes.
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt


def load_summary(output_dir: Path) -> Dict:
    """Load simulation summary from output directory.

    Args:
        output_dir: Path to results directory (e.g., results/hybrid_160)

    Returns:
        Dict with metrics from summary.json or summary.txt
    """
    summary_json = output_dir / "summary.json"
    summary_txt = output_dir / "summary.txt"

    if summary_json.exists():
        with open(summary_json) as f:
            return json.load(f)

    # Fallback: parse summary.txt
    if summary_txt.exists():
        with open(summary_txt) as f:
            content = f.read()
            # Extract key metrics
            metrics = {}
            for line in content.split('\n'):
                if 'Core vorticity:' in line:
                    try:
                        metrics['core_vorticity'] = float(line.split(':')[1].split()[0])
                    except:
                        pass
                elif 'Maximum velocity:' in line:
                    try:
                        metrics['max_velocity'] = float(line.split(':')[1].split()[0])
                    except:
                        pass
                elif 'Kinetic energy:' in line:
                    try:
                        metrics['kinetic_energy'] = float(line.split(':')[1].split()[0])
                    except:
                        pass
                elif 'Core vorticity reduction:' in line:
                    try:
                        metrics['vorticity_reduction'] = float(line.split(':')[1].strip().rstrip('%'))
                    except:
                        pass
            return metrics

    return {}


def compare_runs(result_dirs: List[Path]) -> Tuple[Dict, Dict]:
    """Compare metrics across multiple simulation runs.

    Args:
        result_dirs: List of output directory paths

    Returns:
        (metrics_dict, comparison_stats)
    """
    all_metrics = {}

    for result_dir in result_dirs:
        mode = result_dir.name.replace('_160', '')
        all_metrics[mode] = load_summary(result_dir)
        print(f"Loaded {mode}: {all_metrics[mode]}")

    # Compute comparison statistics
    comparison = {}

    if 'rankine' in all_metrics and 'hybrid' in all_metrics:
        rankine_ke = all_metrics['rankine'].get('kinetic_energy', 0)
        hybrid_ke = all_metrics['hybrid'].get('kinetic_energy', 0)
        if rankine_ke > 0:
            comparison['ke_reduction_rankine_to_hybrid'] = (
                (rankine_ke - hybrid_ke) / rankine_ke * 100
            )

        rankine_vort = all_metrics['rankine'].get('core_vorticity', 0)
        hybrid_vort = all_metrics['hybrid'].get('core_vorticity', 0)
        if rankine_vort > 0:
            comparison['vorticity_ratio_hybrid_to_rankine'] = hybrid_vort / rankine_vort

    if 'realworld' in all_metrics and 'hybrid' in all_metrics:
        real_ke = all_metrics['realworld'].get('kinetic_energy', 0)
        hybrid_ke = all_metrics['hybrid'].get('kinetic_energy', 0)
        if real_ke > 0:
            comparison['ke_ratio_hybrid_to_realworld'] = hybrid_ke / real_ke

        real_vel = all_metrics['realworld'].get('max_velocity', 0)
        hybrid_vel = all_metrics['hybrid'].get('max_velocity', 0)
        if real_vel > 0:
            comparison['velocity_ratio_hybrid_to_realworld'] = hybrid_vel / real_vel

    return all_metrics, comparison


def print_comparison_table(all_metrics: Dict, comparison: Dict):
    """Print formatted comparison table."""
    print("\n" + "=" * 90)
    print("AEOLUS 160-STEP SIMULATION COMPARISON")
    print("=" * 90)

    modes = list(all_metrics.keys())

    # Find all unique metric keys
    all_keys = set()
    for metrics in all_metrics.values():
        all_keys.update(metrics.keys())

    # Print header
    print(f"{'Metric':<35} | {' | '.join(f'{m:>20}' for m in modes)}")
    print("-" * 90)

    # Print each metric
    metric_labels = {
        'core_vorticity': 'Core Vorticity (1/s)',
        'max_velocity': 'Max Velocity (m/s)',
        'kinetic_energy': 'Kinetic Energy (J)',
        'vorticity_reduction': 'Vorticity Reduction (%)',
        'circulation': 'Circulation (m²/s)',
        'divergence_rms': 'Divergence RMS',
    }

    for key in sorted(all_keys):
        label = metric_labels.get(key, key)
        values = []
        for mode in modes:
            val = all_metrics[mode].get(key, None)
            if val is not None:
                if isinstance(val, float):
                    if key == 'kinetic_energy':
                        values.append(f"{val:.3e}")
                    else:
                        values.append(f"{val:.4f}")
                else:
                    values.append(str(val))
            else:
                values.append("N/A")

        print(f"{label:<35} | {' | '.join(f'{v:>20}' for v in values)}")

    print("\n" + "=" * 90)
    print("RELATIVE METRICS")
    print("=" * 90)

    for key, val in sorted(comparison.items()):
        if isinstance(val, float):
            print(f"{key:<40}: {val:+.2f}")
        else:
            print(f"{key:<40}: {val}")


def main():
    """Run comparison across three initialization modes."""
    result_dirs = [
        Path("results/rankine_160"),
        Path("results/hybrid_160"),
        Path("results/realworld_160"),
    ]

    # Check which directories exist
    existing_dirs = [d for d in result_dirs if d.exists()]

    if not existing_dirs:
        print("No simulation results found. Run simulations first:")
        print("  python3 main.py --initialization rankine --n-steps 160 --output results/rankine_160")
        print("  python3 main.py --initialization hybrid --n-steps 160 --output results/hybrid_160")
        print("  python3 main.py --initialization realworld --n-steps 160 --output results/realworld_160")
        return

    print(f"Found {len(existing_dirs)}/{len(result_dirs)} result directories")

    all_metrics, comparison = compare_runs(existing_dirs)
    print_comparison_table(all_metrics, comparison)

    # Try to plot if matplotlib available
    try:
        plot_comparison(all_metrics)
    except Exception as e:
        print(f"Could not generate plots: {e}")


def plot_comparison(all_metrics: Dict):
    """Generate comparison plots."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    modes = list(all_metrics.keys())

    # Plot 1: Kinetic Energy
    ax = axes[0, 0]
    ke_values = [all_metrics[m].get('kinetic_energy', 0) for m in modes]
    ax.bar(modes, ke_values, color=['blue', 'green', 'orange'][:len(modes)])
    ax.set_ylabel('Kinetic Energy (J)')
    ax.set_title('Final Kinetic Energy by Mode')
    ax.ticklabel_format(style='scientific', axis='y')

    # Plot 2: Vorticity
    ax = axes[0, 1]
    vort_values = [all_metrics[m].get('core_vorticity', 0) for m in modes]
    ax.bar(modes, vort_values, color=['blue', 'green', 'orange'][:len(modes)])
    ax.set_ylabel('Core Vorticity (1/s)')
    ax.set_title('Core Vorticity by Mode')

    # Plot 3: Max Velocity
    ax = axes[1, 0]
    vel_values = [all_metrics[m].get('max_velocity', 0) for m in modes]
    ax.bar(modes, vel_values, color=['blue', 'green', 'orange'][:len(modes)])
    ax.set_ylabel('Max Velocity (m/s)')
    ax.set_title('Maximum Velocity by Mode')

    # Plot 4: Vorticity Reduction
    ax = axes[1, 1]
    reduc_values = [all_metrics[m].get('vorticity_reduction', 0) for m in modes]
    ax.bar(modes, reduc_values, color=['blue', 'green', 'orange'][:len(modes)])
    ax.set_ylabel('Reduction (%)')
    ax.set_title('Vorticity Reduction by Mode')
    ax.axhline(y=70, color='r', linestyle='--', label='Target (70%)')
    ax.legend()

    plt.tight_layout()
    plt.savefig('results/comparison_160step.png', dpi=150, bbox_inches='tight')
    print(f"Saved comparison plot: results/comparison_160step.png")


if __name__ == "__main__":
    main()
