"""Score the outward-fan sweep: effect while the fans run, after they stop, and what they would cost.

    python -m aeolus_axisym.fan_report results/axisym/m35
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

from .experiment import load_state
from .model import AxisymmetricModel, RHO_AIR
from .report import series


def window_noise(ctrl, key, t0, t1, sigmas=2.0):
    """2-sigma relative difference between two runs that differ only by chance, for one time window."""
    t, c = series(ctrl, key)
    x = c - c.mean()
    ac = np.correlate(x, x, "full")[len(x) - 1:] / (x.var() * len(x))
    cut = int(np.argmax(ac < 0.05)) or len(ac)
    tau = (t[1] - t[0]) * (1 + 2 * np.sum(ac[1:cut]))
    return sigmas * np.sqrt(2) * c.std() * np.sqrt(tau / (t1 - t0)) / abs(c.mean())


def main(out_dir):
    out = Path(out_dir)
    ctrl = json.loads((out / "runs" / "control.json").read_text())
    cfg, _ = load_state(out / "mature.npz")
    m = AxisymmetricModel(cfg)
    rows = []
    for p in sorted((out / "runs").glob("fan_*.json")):
        r = json.loads(p.read_text())
        v = r["meta"]["params"]
        on = v["fan_on_s"]
        # Thrust and the ideal (momentum-theory) power to produce it: P = T^1.5 / sqrt(2 ρ A)
        shape = np.exp(-((m.rf[:, None] - v["fan_r"]) / v["fan_width"]) ** 2) * np.exp(-(m.zc[None, :] / v["fan_depth"]) ** 2)
        vol_u = 2 * np.pi * m.rf[:, None] * m.dr * m.dz
        thrust = RHO_AIR * v["fan_accel"] * float(np.sum(shape * vol_u))
        area = 2 * np.pi * v["fan_r"] * v["fan_depth"]
        p_ideal = thrust ** 1.5 / np.sqrt(2 * RHO_AIR * area)
        row = {"accel": v["fan_accel"], "thrust_MN": thrust / 1e6, "power_GW": p_ideal / 1e9,
               "outflow_max": max(h.get("fan_outflow_max", 0.0) for h in r["history"] if h["t_rel"] < on)}
        t, x = series(r, "v_max_low"); _, c = series(ctrl, "v_max_low")
        n = min(len(x), len(c)); t, x, c = t[:n], x[:n], c[:n]
        for name, sel, (a, b) in [("during", t < on, (0, on)), ("after", t >= on, (on, t[-1]))]:
            row[name] = float(x[sel].mean() / c[sel].mean() - 1)
            row[name + "_wind"] = float(x[sel].mean()); row[name + "_ctrl"] = float(c[sel].mean())
            row[name + "_noise"] = float(window_noise(ctrl, "v_max_low", a, b))
        tp, xp = series(r, "p_deficit_hPa"); _, cp = series(ctrl, "p_deficit_hPa")
        row["during_p"] = float(xp[:n][t < on].mean() / cp[:n][t < on].mean() - 1)
        rows.append(row)
    rows.sort(key=lambda r: r["accel"])
    lines = ["| Fan push (m/s²) | Outward wind made (m/s) | Thrust (MN) | Minimum power (GW) | "
             "Peak wind while fans on (control) | Change | After fans off | Change |",
             "|---|---|---|---|---|---|---|---|"]
    f = lambda e, n: f"{100 * e:+.1f}%" + ("" if abs(e) > n else " ~")
    for r in rows:
        lines.append(f"| {r['accel']:g} | {r['outflow_max']:.1f} | {r['thrust_MN']:.0f} | {r['power_GW']:.1f} | "
                     f"{r['during_wind']:.1f} ({r['during_ctrl']:.1f}) | {f(r['during'], r['during_noise'])} | "
                     f"{r['after_wind']:.1f} ({r['after_ctrl']:.1f}) | {f(r['after'], r['after_noise'])} |")
    if rows:
        lines.append("")
        lines.append(f"+ = stronger tornado. '~' = within the 2-sigma noise floor "
                     f"(±{100 * rows[0]['during_noise']:.0f}% while on, ±{100 * rows[0]['after_noise']:.0f}% after).")
    (out / "fan_results.md").write_text("\n".join(lines) + "\n")
    (out / "fan_scores.json").write_text(json.dumps(rows, indent=1))
    print("\n".join(lines))


if __name__ == "__main__":
    main(sys.argv[1])
