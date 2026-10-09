"""Score intervention runs against the control and the noise floor; write tables and plots.

    python -m aeolus_axisym.report results/axisym
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

from .tornado import ef_rating

METRICS = [
    ("v_max_low", "Peak swirl wind, z ≤ 500 m", "m/s"),
    ("wind_max_sfc", "Peak horizontal wind, z ≤ 100 m", "m/s"),
    ("omega_max_low", "Peak vertical vorticity, z ≤ 500 m", "1/s"),
    ("p_deficit_hPa", "Central surface pressure drop", "hPa"),
    ("circ_1km", "Circulation at r = 1 km", "m²/s"),
]
TNT_J = 4.184e12  # 1 kiloton of TNT


def load(out: Path):
    runs = {}
    for p in sorted((out / "runs").glob("*.json")):
        d = json.loads(p.read_text())
        runs[p.stem] = d
    return runs


def series(run, key):
    h = run["history"]
    return np.array([x["t_rel"] for x in h]), np.array([x[key] for x in h])


def effect(run, ctrl, key, last=300.0):
    t, x = series(run, key)
    _, c = series(ctrl, key)
    n = min(len(x), len(c)); t, x, c = t[:n], x[:n], c[:n]
    rel = 1.0 - x / c                       # + means weaker than control
    tail = t >= t[-1] - last
    first = t <= 600.0
    return {
        "mean_all": float(1.0 - x.mean() / c.mean()),
        "first10": float(1.0 - x[first].mean() / c[first].mean()),
        "end": float(rel[-1]),
        "last5": float(1.0 - x[tail].mean() / c[tail].mean()),
        "peak": float(rel.max()),
        "worst": float(rel.min()),
        "t_peak": float(t[np.argmax(rel)]),
        "run_end": float(x[-1]), "ctrl_end": float(c[-1]),
        "run_last5": float(x[tail].mean()), "ctrl_last5": float(c[tail].mean()),
    }


WINDOWS = {"mean_all": None, "first10": 600.0, "last5": 300.0}


def control_noise(ctrl, key, sigmas=2.0):
    """2-sigma relative difference expected between two runs that differ only by chance.

    Uses the control's own variability and integrated autocorrelation time. Tiny-perturbation
    runs underestimate this early on because they take minutes to fall out of step with the control.
    """
    t, c = series(ctrl, key)
    x = c - c.mean()
    ac = np.correlate(x, x, "full")[len(x) - 1:] / (x.var() * len(x))
    cut = int(np.argmax(ac < 0.05)) or len(ac)
    tau = (t[1] - t[0]) * (1 + 2 * np.sum(ac[1:cut]))
    out = {}
    for name, w in WINDOWS.items():
        w = t[-1] if w is None else w
        out[name] = float(sigmas * np.sqrt(2) * c.std() * np.sqrt(tau / w) / abs(c.mean()))
    out["tau_s"] = float(tau)
    return out


def noise_floor(runs, ctrl):
    """Largest |difference| any tiny-perturbation run shows against the control, per statistic."""
    nulls = [r for k, r in runs.items() if k.startswith("null")]
    if not nulls:
        return None
    out = {}
    for key, _, _ in METRICS:
        es = [effect(n, ctrl, key) for n in nulls]
        out[key] = {s: max(abs(e[s]) for e in es) for s in ("end", "last5", "mean_all", "first10")}
        out[key]["any_time"] = max(max(abs(e["peak"]), abs(e["worst"])) for e in es)
    return out


def table(runs, ctrl, noise):
    rows = []
    for tag, r in runs.items():
        if tag == "control" or tag.startswith("null"):
            continue
        meta, last = r["meta"], r["history"][-1]
        row = {"tag": tag, "version": meta["version"] + (" (60 s)" if meta["extended"] else ""),
               "heat_kt": max(h["heat_J"] for h in r["history"]) / TNT_J,
               "air_Mt": max(h["removed_air_kg"] for h in r["history"]) / 1e9,
               "drag_work_GJ": last["damping_J"] / 1e9,
               "ef_end": ef_rating(last["wind_max_sfc"]),
               "ef_ctrl_end": ef_rating(ctrl["history"][-1]["wind_max_sfc"])}
        for key, _, _ in METRICS:
            e = effect(r, ctrl, key)
            row[key] = e
            if noise is not None:
                cn = control_noise(ctrl, key)
                for stat in ("mean_all", "first10", "last5"):
                    row[key][f"sig_{stat}"] = abs(e[stat]) > cn[stat]
                row[key]["noise_2sigma"] = cn
        rows.append(row)
    return rows


def plot(runs, ctrl, out: Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 1, figsize=(11, 8), sharex=True)
    for ax, key, label in [(axes[0], "v_max_low", "Peak swirl wind z ≤ 500 m (m/s)"),
                           (axes[1], "p_deficit_hPa", "Central surface pressure drop (hPa)")]:
        t, c = series(ctrl, key)
        ax.plot(t, c, color="black", lw=2.5, label="control (no intervention)", zorder=5)
        for tag, r in runs.items():
            if tag == "control":
                continue
            tt, x = series(r, key)
            ax.plot(tt, x, lw=1, alpha=0.8, label=r["meta"]["version"] + (" (60 s)" if r["meta"]["extended"] else ""),
                    ls=":" if tag.startswith("null") else "-")
        ax.set_ylabel(label); ax.grid(alpha=0.3)
    axes[1].set_xlabel("time since intervention start (s)")
    axes[0].legend(fontsize=7, ncol=3, loc="lower right")
    fig.tight_layout(); fig.savefig(out / "timeseries.png", dpi=130); plt.close(fig)


def write_markdown(rows, noise, ctrl, out: Path):
    c_end = ctrl["history"][-1]
    lines = ["Change vs control (+ = tornado STRONGER, − = weaker). '~' = within the 2-sigma noise floor "
             "(not distinguishable from chance). 'Best moment' is shown only to illustrate noise: "
             "tiny-perturbation runs reach similar values.",
             "",
             "| Version | Peak wind z≤500 m, whole-run mean | first 10 min | last 5 min | best moment | "
             "Pressure drop (whole run) | Circulation 1 km (whole run) | EF at end (control) | "
             "Heat (kt TNT) | Air removed (Mt) |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    fmt = lambda e: f"{-100 * e:+.1f}%"  # positive = stronger than control
    for r in rows:
        v = r["v_max_low"]
        g = lambda e, s: fmt(e[s]) + ("" if e.get(f"sig_{s}", True) else " ~")
        lines.append(f"| {r['version']} | {g(v, 'mean_all')} | {g(v, 'first10')} | {g(v, 'last5')} | "
                     f"{fmt(v['peak'])} at t+{v['t_peak']:.0f}s | {g(r['p_deficit_hPa'], 'mean_all')} | "
                     f"{g(r['circ_1km'], 'mean_all')} | {r['ef_end']} ({r['ef_ctrl_end']}) | "
                     f"{r['heat_kt']:.2f} | {r['air_Mt']:.2f} |")
    cn = control_noise(ctrl, "v_max_low")
    lines.append("")
    lines.append(f"2-sigma noise floor for peak wind (from control variability, autocorrelation time "
                 f"{cn['tau_s']:.0f} s): whole run ±{100 * cn['mean_all']:.1f}%, first 10 min "
                 f"±{100 * cn['first10']:.1f}%, last 5 min ±{100 * cn['last5']:.1f}%.")
    if noise:
        lines.append("")
        lines.append("Tiny-perturbation (0.001 K) runs vs control, for comparison: " + ", ".join(
            f"{k}: whole-run {100 * n['mean_all']:.1f}%, last-5-min {100 * n['last5']:.1f}%, any moment {100 * n['any_time']:.1f}%"
            for k, n in noise.items()))
    lines.append("")
    lines.append(f"Control at end: peak wind z≤500 m {c_end['v_max_low']:.1f} m/s, surface wind {c_end['wind_max_sfc']:.1f} m/s "
                 f"({ef_rating(c_end['wind_max_sfc'])}), pressure drop {c_end['p_deficit_hPa']:.1f} hPa, "
                 f"core radius {c_end['r_core']:.0f} m.")
    (out / "results_table.md").write_text("\n".join(lines) + "\n")
    return "\n".join(lines)


def main(out_dir):
    out = Path(out_dir)
    runs = load(out)
    ctrl = runs["control"]
    noise = noise_floor(runs, ctrl)
    rows = table(runs, ctrl, noise)
    (out / "scores.json").write_text(json.dumps({"rows": rows, "noise": noise}, indent=1))
    plot(runs, ctrl, out)
    print(write_markdown(rows, noise, ctrl, out))


if __name__ == "__main__":
    main(sys.argv[1])
