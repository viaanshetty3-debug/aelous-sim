"""Score the plane-delivery runs (early / upwind / 45 K) against their controls.

    python -m aeolus_axisym.plane_report results/axisym
"""
import json, sys
from pathlib import Path
import numpy as np
base = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("results/axisym")
FLEET_MT = 0.2  # world large-cargo fleet, one sortie (~2,000 aircraft x ~100 t)
def load(d, tag): 
    p = base / d / "runs" / f"{tag}.json"
    return json.loads(p.read_text())["history"] if p.exists() else None
def win(h, k, a, b):
    t = np.array([x["t_rel"] for x in h]); v = np.array([x[k] for x in h])
    s = (t >= a*60) & (t < b*60); return v[s].mean() if s.any() else float("nan")
def row(d, name, ctrl):
    tag = name.replace("/", "-").replace(" ", "_"); h = load(d, tag)
    if h is None: return f"| {name} | (missing) |"
    mt = h[-1].get("cool_J", 0.0) / 0.31e6 / 1e9
    s1, s2 = win(h, "wind_max_sfc", 10, 30), win(h, "wind_max_sfc", 30, 45)
    c1, c2 = win(ctrl, "wind_max_sfc", 10, 30), win(ctrl, "wind_max_sfc", 30, 45)
    sw = win(h, "v_max_low", 30, 45)
    fives = " ".join(f"{win(h,'wind_max_sfc',a,a+5):.0f}" for a in range(0, 45, 5))
    ok = "✓" if max(s1, s2) < 29 else ("partial" if s2 < 29 else "✗")
    return (f"| {name} | {mt:.2f} Mt ({mt/FLEET_MT:.1f}× fleet) | {s1:.1f} ({100*(s1/c1-1):+.0f}%) | "
            f"{s2:.1f} ({100*(s2/c2-1):+.0f}%) | {sw:.1f} | {ok} | {fives} |")
print("| Setup | Liquid air | Surface 10–30 min | Surface 30–45 min | Swirl 30–45 | Below EF0 | 5-min surface means 0→45 |")
print("|---|---|---|---|---|---|---|")
for d, names in [("m35_early", ["control", "early: 1km ring 10 K 10 min", "early: 1km ring 30 K 5 min", "early: mid-level 30 K 10 min"]),
                 ("m35", ["control", "upwind: 2.5km ring 10 K 15 min", "upwind: 2.5km ring 30 K 15 min", "eff I: mid-level 45 K 15 min", "eff H: mid-level 60 K 15 min"])]:
    ctrl = load(d, "control")
    for n in names: print(row(d, n, ctrl) if n != "control" else row(d, "control", ctrl).replace("0.00 Mt (0.0× fleet)", "—") + f"  <!-- {d} -->")
