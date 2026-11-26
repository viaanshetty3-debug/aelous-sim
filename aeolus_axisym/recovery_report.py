"""Measure cooling suppression and recovery without hiding threshold crossings in averages.

    python -m aeolus_axisym.recovery_report results/axisym/m35 \
        --version 'eff H: mid-level 60 K 15 min' \
        --version 'upwind: 2.5km ring 30 K 15 min'

Durations and means use piecewise-linear interpolation between diagnostic samples.
They describe sampled model winds, not observed EF damage ratings or 3-second gusts.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from .report import control_noise, load, series

THRESHOLD = 29.0
LIQUID_AIR_J_PER_KG = 0.31e6
KEY = "wind_max_sfc"


def wind_series(run):
    t, wind = series(run, KEY)
    if (len(t) < 2 or not np.all(np.isfinite(t)) or not np.all(np.isfinite(wind))
            or np.any(np.diff(t) <= 0)):
        raise ValueError("Wind history needs at least two finite, increasing samples")
    return t, wind


def clip_series(t, values, start, end):
    if not t[0] <= start < end <= t[-1]:
        raise ValueError("Requested window is not fully covered by the history")
    inside = (t > start) & (t < end)
    times = np.r_[start, t[inside], end]
    return times, np.interp(times, t, values)


def time_mean(t, values):
    return float(np.sum(np.diff(t) * (values[:-1] + values[1:]) / 2) / (t[-1] - t[0]))


def below_intervals(t, wind, threshold=THRESHOLD):
    """Intervals strictly below threshold, with crossings interpolated in time."""
    intervals = []
    for a, b, x, y in zip(t[:-1], t[1:], wind[:-1], wind[1:]):
        if x >= threshold and y >= threshold:
            continue
        start, end = float(a), float(b)
        if (x < threshold) != (y < threshold):
            crossing = float(a + (threshold - x) * (b - a) / (y - x))
            if x < threshold:
                end = crossing
            else:
                start = crossing
        if intervals and intervals[-1][1] == start and x < threshold:
            intervals[-1][1] = end
        else:
            intervals.append([start, end])
    return intervals


def window_summary(run, ctrl, start, end):
    t, wind = wind_series(run)
    ct, cw = wind_series(ctrl)
    t, wind = clip_series(t, wind, start, end)
    ct, cw = clip_series(ct, cw, start, end)
    mean, control_mean = time_mean(t, wind), time_mean(ct, cw)
    intervals = below_intervals(t, wind)
    duration = sum(b - a for a, b in intervals)
    # The existing noise estimator assumes uniformly spaced control diagnostics.
    full_t, full_w = wind_series(ctrl)
    noise = None
    if (np.allclose(np.diff(full_t), np.diff(full_t)[0])
            and abs(full_w.mean()) > 0 and full_w.var() > 0):
        tau = control_noise(ctrl, KEY)["tau_s"]
        noise = float(2 * np.sqrt(2) * full_w.std()
                      * np.sqrt(tau / (end - start)) / abs(full_w.mean()))
    change = mean / control_mean - 1 if control_mean != 0 else None
    return {
        "start_s": start, "end_s": end,
        "mean_wind_m_s": mean, "control_mean_wind_m_s": control_mean,
        "change_vs_control": change, "noise_2sigma": noise,
        "above_noise": abs(change) > noise if change is not None and noise is not None else None,
        "max_wind_m_s": float(wind.max()),
        "below_threshold_s": duration, "below_threshold_fraction": duration / (end - start),
        "longest_below_s": max((b - a for a, b in intervals), default=0.0),
        "below_intervals_s": intervals,
        "below_at_end": bool(wind[-1] < THRESHOLD),
    }


def summarize(run, ctrl):
    if run["meta"]["t_start"] != ctrl["meta"]["t_start"]:
        raise ValueError("Intervention and control must start at the same simulation time")
    t, _ = wind_series(run)
    ct, _ = wind_series(ctrl)
    if ct[0] > t[0] or ct[-1] < t[-1]:
        raise ValueError("Control must cover the full intervention observation period")
    params = run["meta"]["params"]
    off = float(params["cool_on_s"])
    windows = []
    # Report only complete 15-minute windows, never label a partial window as complete.
    for start in np.arange(0.0, t[-1], 900.0):
        if start >= t[0] and start + 900 <= t[-1]:
            windows.append(window_summary(run, ctrl, float(start), float(start + 900)))
    post = window_summary(run, ctrl, max(off, float(t[0])), float(t[-1])) if t[-1] > max(off, t[0]) else None
    cooling = max(float(h["cool_J"]) for h in run["history"])
    if not np.isfinite(cooling) or cooling < 0:
        raise ValueError("Cooling energy must be finite and nonnegative")
    return {
        "version": run["meta"]["version"], "cooling_off_s": off,
        "observation_end_s": float(t[-1]), "cooling_TJ": cooling / 1e12,
        "liquid_air_Mt": cooling / LIQUID_AIR_J_PER_KG / 1e9,
        "windows": windows, "post_cooling": post,
    }


def markdown(rows):
    lines = [
        "# Cooling suppression and recovery", "",
        "Surface wind is the model's peak horizontal wind at z ≤ 100 m. The 29 m/s threshold",
        "is a comparison marker, not an observed EF rating. Means and threshold durations are",
        "time-weighted using linear interpolation between saved samples; shorter excursions may be missed.",
        "All windows use the same time span in the intervention and control. '~' means the change",
        "is within the existing control-variability 2σ estimate; this is not uncertainty from repeated runs.", "",
        "| Setup | Window (min) | Mean (control), m/s | Change | 2σ noise | Maximum, m/s | Time below 29 m/s | Longest interval below (min) |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        for w in row["windows"]:
            change = "n/a" if w["change_vs_control"] is None else f"{100*w['change_vs_control']:+.1f}%"
            change += " ~" if w["above_noise"] is False else ""
            noise = "n/a" if w["noise_2sigma"] is None else f"±{100*w['noise_2sigma']:.1f}%"
            lines.append(f"| {row['version']} | {w['start_s']/60:g}–{w['end_s']/60:g} | "
                         f"{w['mean_wind_m_s']:.1f} ({w['control_mean_wind_m_s']:.1f}) | {change} | {noise} | "
                         f"{w['max_wind_m_s']:.1f} | {100*w['below_threshold_fraction']:.1f}% | {w['longest_below_s']/60:.1f} |")
    lines += ["", "## Cooling cost and follow-up", ""]
    for row in rows:
        post = row["post_cooling"]
        text = (f"- **{row['version']}**: {row['cooling_TJ']:.1f} TJ, "
                f"{row['liquid_air_Mt']:.2f} Mt liquid-air equivalent; cooling stops at "
                f"{row['cooling_off_s']/60:g} min, observation ends at {row['observation_end_s']/60:g} min.")
        if post:
            text += (f" During follow-up, {100*post['below_threshold_fraction']:.1f}% of time is below "
                     f"29 m/s; the longest interval lasts {post['longest_below_s']/60:.1f} min.")
            if post["below_at_end"]:
                text += " Wind is below the threshold at the final sample; later recovery is unknown."
        else:
            text += " No post-cooling observation is available."
        lines.append(text)
    lines += ["", "Liquid-air equivalent uses 0.31 MJ/kg, matching previous reports. These are single runs",
              "in the axisymmetric Boussinesq model; strong cooling remains a qualitative experiment.", ""]
    return "\n".join(lines)


def plot(selected, ctrl, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(11, 5))
    end = max(wind_series(r)[0][-1] for r in selected)
    t, w = wind_series(ctrl)
    keep = t <= end
    ax.plot(t[keep] / 60, w[keep], color="black", alpha=0.6, label="Control")
    for run in selected:
        t, w = wind_series(run)
        line, = ax.plot(t / 60, w, label=run["meta"]["version"], linewidth=1.3)
        off = run["meta"]["params"]["cool_on_s"]
        if t[0] <= off <= t[-1]:
            ax.plot(off / 60, np.interp(off, t, w), "o", color=line.get_color())
    ax.axhline(THRESHOLD, linestyle="--", color="grey", label="29 m/s comparison threshold")
    ax.set(xlabel="Minutes since intervention start", ylabel="Peak horizontal surface wind (m/s)",
           title="Cooling follow-up — dots mark cooling switched off")
    ax.grid(alpha=0.2)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("out", type=Path, help="Experiment directory containing runs/control.json")
    parser.add_argument("--version", action="append", help="Cooling version to include (repeatable; default: all)")
    parser.add_argument("--dest", type=Path, help="Report directory; defaults to the experiment directory")
    args = parser.parse_args(argv)
    runs = load(args.out)
    if "control" not in runs:
        parser.error("Missing runs/control.json")
    cooling = [r for r in runs.values() if (r["meta"].get("params") or {}).get("cool_K", 0) > 0]
    if args.version:
        missing = set(args.version) - {r["meta"]["version"] for r in cooling}
        if missing:
            parser.error(f"Missing cooling runs: {', '.join(sorted(missing))}")
        cooling = [r for r in cooling if r["meta"]["version"] in args.version]
    if not cooling:
        parser.error("No cooling runs found")
    try:
        rows = [summarize(r, runs["control"]) for r in cooling]
    except (ValueError, KeyError) as exc:
        parser.error(str(exc))
    dest = args.dest or args.out
    dest.mkdir(parents=True, exist_ok=True)
    report = markdown(rows)
    (dest / "recovery_report.json").write_text(json.dumps(rows, indent=2, allow_nan=False) + "\n")
    (dest / "recovery_report.md").write_text(report)
    plot(cooling, runs["control"], dest / "recovery_timeseries.png")
    print(report)


if __name__ == "__main__":
    main()
