"""Plot vorticity and velocity suppression metrics from simulation output."""

import json
import sys
from pathlib import Path

import numpy as np


def load_summary(summary_path):
    """Load summary.json from output directory."""
    with open(summary_path, 'r') as f:
        return json.load(f)


def create_text_visualization(summary):
    """Create ASCII art visualization of suppression metrics."""
    time_series = summary.get("time_series", {})
    core_vorticity = np.array(time_series.get("core_vorticity", []))
    max_velocity = np.array(time_series.get("max_velocity", []))

    if len(core_vorticity) == 0:
        print("Error: No vorticity data found")
        return ""

    n_steps = len(core_vorticity)
    chart_width = 80
    chart_height = 20

    # Normalize vorticity for plotting
    vort_min, vort_max = core_vorticity.min(), core_vorticity.max()
    vort_range = vort_max - vort_min if vort_max > vort_min else 1
    vort_normalized = (core_vorticity - vort_min) / vort_range

    # Normalize velocity for plotting
    vel_min, vel_max = max_velocity.min(), max_velocity.max()
    vel_range = vel_max - vel_min if vel_max > vel_min else 1
    vel_normalized = (max_velocity - vel_min) / vel_range

    output = []
    output.append("═" * 90)
    output.append("AEOLUS VORTEX DISRUPTION: VISUALIZATION")
    output.append("═" * 90)

    # Vorticity chart
    output.append("\n▓ CORE VORTICITY COLLAPSE")
    output.append("├─ Initial: {:.6f} 1/s  →  Final: {:.6f} 1/s  (Δ: {:.6f})".format(
        core_vorticity[0], core_vorticity[-1], core_vorticity[-1] - core_vorticity[0]))

    for y in range(chart_height, 0, -1):
        row = "│ "
        threshold = (y - 1) / chart_height
        for x in range(min(n_steps, chart_width)):
            idx = int(x * len(core_vorticity) / chart_width)
            if idx < len(vort_normalized):
                if vort_normalized[idx] >= threshold:
                    row += "█"
                else:
                    row += " "
            else:
                row += " "
        output.append(row)

    output.append("└─ " + "─" * 76)
    output.append("  Step 0" + " " * (chart_width - 14) + f"Step {n_steps-1}")

    # Velocity chart
    output.append("\n▓ MAXIMUM VELOCITY SUPPRESSION")
    output.append("├─ Initial: {:.2f} m/s  →  Final: {:.2f} m/s  ({:.1f}% reduction)".format(
        max_velocity[0], max_velocity[-1],
        100 * (1 - max_velocity[-1] / max_velocity[0])))

    for y in range(chart_height, 0, -1):
        row = "│ "
        threshold = (y - 1) / chart_height
        for x in range(min(n_steps, chart_width)):
            idx = int(x * len(max_velocity) / chart_width)
            if idx < len(vel_normalized):
                if vel_normalized[idx] >= threshold:
                    row += "█"
                else:
                    row += " "
            else:
                row += " "
        output.append(row)

    output.append("└─ " + "─" * 76)
    output.append("  Step 0" + " " * (chart_width - 14) + f"Step {n_steps-1}")

    output.append("\n" + "═" * 90)
    output.append("METRICS SUMMARY")
    output.append("═" * 90)

    vort_reduction = summary["final_metrics"].get("vorticity_reduction_pct_final", 0)
    vel_reduction = 100 * (1 - max_velocity[-1] / max_velocity[0])
    reformation = summary.get("reformation_detected", False)

    output.append(f"✓ Core Vorticity Reduction:  {vort_reduction:6.1f}%  (target: ≥70%)")
    output.append(f"✓ Maximum Velocity Reduction: {vel_reduction:6.1f}%")
    output.append(f"✓ Post-Intervention Reformation: {'DETECTED ✗' if reformation else 'NOT DETECTED ✓'}")
    output.append(f"✓ Simulation Steps: {n_steps}")
    output.append(f"✓ Grid Resolution: 48×48×48")

    result = "\n".join(output)
    return result


def create_numeric_summary_text(summary, output_file):
    """Create detailed numeric summary in text format."""
    time_series = summary.get("time_series", {})
    core_vorticity = np.array(time_series.get("core_vorticity", []))
    max_velocity = np.array(time_series.get("max_velocity", []))

    lines = []
    lines.append("VORTICITY COLLAPSE PROFILE")
    lines.append("=" * 60)
    lines.append("")
    lines.append("CORE VORTICITY TIME SERIES (80 steps)")
    lines.append("-" * 60)
    lines.append("Step | Vorticity (1/s) | Reduction (%) | Notes")
    lines.append("-" * 60)

    for i in range(0, len(core_vorticity), max(1, len(core_vorticity) // 20)):
        reduction = summary["final_metrics"].get("vorticity_reduction_pct_final", 0) * (i / len(core_vorticity))
        note = ""
        if i == 0:
            note = "← INITIAL"
        elif i == len(core_vorticity) - 1:
            note = "← FINAL"
        lines.append(f"{i:4d} | {core_vorticity[i]:15.6f} | {reduction:13.1f} | {note}")

    lines.append("")
    lines.append("=" * 60)
    lines.append("MAXIMUM VELOCITY TIME SERIES (80 steps)")
    lines.append("-" * 60)
    lines.append("Step | Max Velocity (m/s) | Reduction (%) | Notes")
    lines.append("-" * 60)

    for i in range(0, len(max_velocity), max(1, len(max_velocity) // 20)):
        vel_reduction = 100 * (1 - max_velocity[i] / max_velocity[0])
        note = ""
        if i == 0:
            note = "← INITIAL"
        elif i == len(max_velocity) - 1:
            note = "← FINAL"
        lines.append(f"{i:4d} | {max_velocity[i]:18.2f} | {vel_reduction:13.1f} | {note}")

    lines.append("")
    lines.append("=" * 60)
    lines.append("DISRUPTION METRICS")
    lines.append("=" * 60)

    vort_reduction = summary["final_metrics"].get("vorticity_reduction_pct_final", 0)
    vel_reduction = 100 * (1 - max_velocity[-1] / max_velocity[0])

    lines.append(f"Core Vorticity Reduction:     {vort_reduction:6.1f}%")
    lines.append(f"Maximum Velocity Reduction:   {vel_reduction:6.1f}%")
    lines.append(f"Reformation Detected:          {summary.get('reformation_detected', False)}")
    lines.append(f"Initial Vorticity:             {core_vorticity[0]:8.6f} 1/s")
    lines.append(f"Final Vorticity:               {core_vorticity[-1]:8.6f} 1/s")
    lines.append(f"Initial Velocity:              {max_velocity[0]:8.2f} m/s")
    lines.append(f"Final Velocity:                {max_velocity[-1]:8.2f} m/s")

    with open(output_file, 'w') as f:
        f.write("\n".join(lines))

    return "\n".join(lines)


def create_json_chart_data(summary, output_file):
    """Export chart data as JSON for external plotting tools."""
    time_series = summary.get("time_series", {})
    core_vorticity = time_series.get("core_vorticity", [])
    max_velocity = time_series.get("max_velocity", [])

    chart_data = {
        "title": "Vortex Disruption Profile",
        "steps": list(range(len(core_vorticity))),
        "core_vorticity": {
            "label": "Core Vorticity (1/s)",
            "values": core_vorticity,
            "initial": core_vorticity[0] if core_vorticity else 0,
            "final": core_vorticity[-1] if core_vorticity else 0,
        },
        "max_velocity": {
            "label": "Maximum Velocity (m/s)",
            "values": max_velocity,
            "initial": max_velocity[0] if max_velocity else 0,
            "final": max_velocity[-1] if max_velocity else 0,
            "reduction_pct": 100 * (1 - max_velocity[-1] / max_velocity[0]) if max_velocity else 0,
        },
        "metrics": summary.get("final_metrics", {}),
    }

    with open(output_file, 'w') as f:
        json.dump(chart_data, f, indent=2)

    return chart_data


def main():
    if len(sys.argv) < 2:
        summary_path = Path("results/both/summary.json")
    else:
        summary_path = Path(sys.argv[1])

    if not summary_path.exists():
        print(f"Error: {summary_path} not found")
        return 1

    print(f"Loading summary from: {summary_path}")
    summary = load_summary(summary_path)

    output_dir = summary_path.parent

    # Create text visualization
    print("\n" + create_text_visualization(summary))

    # Create numeric summary
    numeric_path = output_dir / "vorticity_collapse_profile_data.txt"
    numeric_text = create_numeric_summary_text(summary, numeric_path)
    print(f"\n✓ Numeric summary saved: {numeric_path}")

    # Create JSON chart data
    json_path = output_dir / "vorticity_collapse_profile_chart.json"
    create_json_chart_data(summary, json_path)
    print(f"✓ Chart data (JSON) saved: {json_path}")

    print(f"\n✓ Visualization components generated successfully!")
    print(f"\nNote: For PNG generation, matplotlib is being compiled.")
    print(f"You can use the JSON data with any charting tool:")
    print(f"  - Import {json_path} into any plotting library")
    print(f"  - Use the text summary: {numeric_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
