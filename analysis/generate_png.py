"""Generate PNG visualization without matplotlib using PIL."""

import json
import numpy as np
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("Warning: PIL not available, will create text-based output only")


def create_png_visualization(summary_json_path, output_png_path):
    """Create PNG visualization using PIL."""
    if not HAS_PIL:
        print("PIL/Pillow not installed. Install with: pip install pillow")
        return False

    # Load data
    with open(summary_json_path) as f:
        summary = json.load(f)

    ts = summary.get("time_series", {})
    vorticity = np.array(ts.get("core_vorticity", []))
    velocity = np.array(ts.get("max_velocity", []))

    if len(vorticity) == 0:
        print("No vorticity data found")
        return False

    # Image parameters
    img_width, img_height = 1200, 900
    margin = 60
    plot_width = img_width - 2 * margin
    plot_height = (img_height - 3 * margin) // 2

    # Create image
    img = Image.new('RGB', (img_width, img_height), color='white')
    draw = ImageDraw.Draw(img)

    # Colors
    color_bg = (255, 255, 255)
    color_grid = (220, 220, 220)
    color_title = (20, 20, 80)
    color_vort = (0, 0, 200)
    color_vel = (200, 0, 0)
    color_text = (40, 40, 40)

    def draw_plot(y_offset, data, color, title, y_label, min_val, max_val):
        """Draw a single plot panel."""
        # Title
        draw.text((margin, y_offset - 40), title, fill=color_title)

        # Plot bounds
        x_min, x_max = margin, margin + plot_width
        y_min = y_offset + plot_height
        y_max = y_offset

        # Draw grid
        for i in range(11):
            x = x_min + (x_max - x_min) * i / 10
            draw.line([(x, y_min), (x, y_max)], fill=color_grid, width=1)
            y = y_min - (y_min - y_max) * i / 10
            draw.line([(x_min, y), (x_max, y)], fill=color_grid, width=1)

        # Draw axes
        draw.line([(x_min, y_min), (x_max, y_min)], fill=color_text, width=2)  # x-axis
        draw.line([(x_min, y_min), (x_min, y_max)], fill=color_text, width=2)  # y-axis

        # Plot data
        n_points = len(data)
        val_range = max_val - min_val if max_val > min_val else 1
        points = []

        for i, val in enumerate(data):
            x = x_min + (x_max - x_min) * i / (n_points - 1)
            normalized = (val - min_val) / val_range
            y = y_min - (y_min - y_max) * normalized
            points.append((x, y))

        # Draw line
        if len(points) > 1:
            draw.line(points, fill=color, width=2)

        # Draw points
        for x, y in points[::max(1, len(points) // 20)]:
            draw.ellipse([(x-3, y-3), (x+3, y+3)], fill=color, outline=color)

        # Labels
        draw.text((x_min - 50, y_max - 15), y_label, fill=color_text)
        draw.text((x_min - 20, y_min + 10), "0", fill=color_text)
        draw.text((x_max - 10, y_min + 10), f"{n_points-1}", fill=color_text)

        # Value labels
        draw.text((x_min - 70, y_max - 10), f"{max_val:.2f}", fill=color_text)
        draw.text((x_min - 70, y_min - 10), f"{min_val:.2f}", fill=color_text)

    # Draw title
    draw.text((margin, 10), "AEOLUS VORTEX DISRUPTION: VORTICITY COLLAPSE PROFILE", fill=color_title)

    # Draw vorticity plot
    draw_plot(
        margin + 50,
        vorticity,
        color_vort,
        "CORE VORTICITY COLLAPSE",
        "Vorticity (1/s)",
        vorticity.min(),
        vorticity.max()
    )

    # Draw velocity plot
    draw_plot(
        margin + 50 + plot_height + margin,
        velocity,
        color_vel,
        "MAXIMUM VELOCITY SUPPRESSION",
        "Velocity (m/s)",
        velocity.min(),
        velocity.max()
    )

    # Add metrics text
    vort_reduction = summary["final_metrics"].get("vorticity_reduction_pct_final", 0)
    vel_reduction = 100 * (1 - velocity[-1] / velocity[0])

    metrics_text = (
        f"Results: Vorticity Reduction = {vort_reduction:.1f}% | "
        f"Velocity Reduction = {vel_reduction:.1f}% | "
        f"Steps = {len(vorticity)}"
    )
    draw.text((margin, img_height - 30), metrics_text, fill=color_text)

    # Save
    img.save(output_png_path)
    print(f"✓ PNG saved: {output_png_path}")
    return True


def main():
    import sys

    if len(sys.argv) < 2:
        summary_path = Path("results/both/summary.json")
        output_path = Path("results/both/vorticity_collapse_profile.png")
    else:
        summary_path = Path(sys.argv[1])
        output_path = summary_path.parent / "vorticity_collapse_profile.png"
        if len(sys.argv) > 2:
            output_path = Path(sys.argv[2])

    if not summary_path.exists():
        print(f"Error: {summary_path} not found")
        return 1

    if not HAS_PIL:
        print("PIL not available - attempting to install pillow...")
        import subprocess
        try:
            subprocess.run(["pip", "install", "-q", "pillow"], check=True)
            from PIL import Image, ImageDraw
            print("✓ Pillow installed")
        except Exception as e:
            print(f"Failed to install pillow: {e}")
            return 1

    print(f"Generating PNG from: {summary_path}")
    success = create_png_visualization(str(summary_path), str(output_path))

    return 0 if success else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
