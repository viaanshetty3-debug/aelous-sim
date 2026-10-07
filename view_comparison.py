#!/usr/bin/env python3
"""Display comparison of AEOLUS simulation metrics across modes."""

import json
import sys
from pathlib import Path


def extract_metrics(summary_path):
    """Extract metrics from summary.txt or summary.json."""
    metrics = {}

    if summary_path.with_suffix('.json').exists():
        with open(summary_path.with_suffix('.json')) as f:
            return json.load(f)

    if summary_path.exists():
        with open(summary_path) as f:
            for line in f:
                line = line.strip()
                if ':' not in line:
                    continue
                key, val = line.split(':', 1)
                key = key.strip().lower().replace(' ', '_')
                val = val.strip()
                try:
                    if 'e' in val or 'e+' in val:
                        metrics[key] = float(val)
                    elif '%' in val:
                        metrics[key] = float(val.rstrip('%'))
                    else:
                        metrics[key] = float(val)
                except (ValueError, IndexError):
                    pass

    return metrics


def main():
    modes = ['rankine_80', 'hybrid_80', 'realworld_80', 'rankine_160', 'hybrid_160', 'realworld_160']

    results = {}
    for mode in modes:
        summary = Path(f"results/{mode}/summary.txt")
        if summary.exists():
            results[mode] = extract_metrics(summary)
            print(f"✓ {mode}")
        else:
            print(f"✗ {mode} (not ready)")

    if not results:
        print("No simulation results yet.")
        return

    # Group by step count
    modes_80 = {k: v for k, v in results.items() if '80' in k}
    modes_160 = {k: v for k, v in results.items() if '160' in k}

    if modes_80:
        print("\n" + "=" * 100)
        print("80-STEP COMPARISON")
        print("=" * 100)
        print_table(modes_80)

    if modes_160:
        print("\n" + "=" * 100)
        print("160-STEP COMPARISON")
        print("=" * 100)
        print_table(modes_160)


def print_table(results_dict):
    """Print formatted comparison table."""
    if not results_dict:
        return

    modes = sorted(results_dict.keys())
    all_keys = set()
    for metrics in results_dict.values():
        all_keys.update(metrics.keys())

    key_order = [
        'core_vorticity', 'maximum_velocity', 'max_velocity', 'kinetic_energy',
        'circulation', 'core_vorticity_reduction', 'divergence_rms',
        'total_steps', 'grid_shape_(r,_θ,_z)'
    ]

    print(f"{'Metric':<40} | {' | '.join(f'{m:>25}' for m in modes)}")
    print("-" * 130)

    for key in key_order:
        if key not in all_keys:
            continue

        values = []
        for mode in modes:
            val = results_dict[mode].get(key)
            if val is not None:
                if isinstance(val, float):
                    if 'energy' in key or 'kin' in key:
                        values.append(f"{val:.3e}")
                    else:
                        values.append(f"{val:>10.4f}")
                else:
                    values.append(f"{str(val):>10}")
            else:
                values.append("N/A".center(10))

        label = key.replace('_', ' ').title()
        print(f"{label:<40} | {' | '.join(f'{v:>25}' for v in values)}")


if __name__ == "__main__":
    main()
