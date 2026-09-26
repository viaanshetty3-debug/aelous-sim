"""Generate summary plots from results.json."""

import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RESULTS_JSON = Path(__file__).parent / "results" / "results.json"
OUT_DIR = Path(__file__).parent / "results"

with open(RESULTS_JSON) as f:
    data = json.load(f)

scenarios = [k for k in data.keys() if not k.startswith("_")]
modes = ["baseline", "thermal", "momentum", "combined"]
colors = {"baseline":"#444", "thermal":"#e0632a", "momentum":"#2a8ce0", "combined":"#6a2ae0"}

# ---- Time-series peak_vt per scenario --------------------------------------
fig, axes = plt.subplots(2, 3, figsize=(14, 8))
axes = axes.flatten()
for i, scn in enumerate(scenarios):
    ax = axes[i]
    for m in modes:
        h = data[scn][m]["history"]
        ax.plot(h["t"], h["peak_vt"], color=colors[m], label=m, lw=1.6)
    ax.set_title(f"{scn} ({data[scn][m]['ef_scale']})", fontsize=10)
    ax.set_xlabel("t (s)")
    ax.set_ylabel("peak |v_θ| (m/s)")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=7, loc="upper right")
axes[-1].axis("off")
fig.suptitle("Peak tangential velocity — AEOLUS interventions vs. independent test bed",
             fontsize=12)
fig.tight_layout()
fig.savefig(OUT_DIR / "peak_vt_timeseries.png", dpi=110)
plt.close(fig)

# ---- Core vorticity per scenario -------------------------------------------
fig, axes = plt.subplots(2, 3, figsize=(14, 8))
axes = axes.flatten()
for i, scn in enumerate(scenarios):
    ax = axes[i]
    for m in modes:
        h = data[scn][m]["history"]
        ax.plot(h["t"], h["core_omega"], color=colors[m], label=m, lw=1.6)
    ax.set_title(scn, fontsize=10)
    ax.set_xlabel("t (s)")
    ax.set_ylabel("core ω_z (1/s)")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=7, loc="upper right")
axes[-1].axis("off")
fig.suptitle("Core vertical vorticity", fontsize=12)
fig.tight_layout()
fig.savefig(OUT_DIR / "core_omega_timeseries.png", dpi=110)
plt.close(fig)

# ---- Bar chart: intervention effect over baseline ---------------------------
fig, ax = plt.subplots(figsize=(11, 5))
x = np.arange(len(scenarios))
w = 0.25
metrics = {}
for m in ("thermal", "momentum", "combined"):
    vals = []
    for scn in scenarios:
        bh = data[scn]["baseline"]["history"]
        th = data[scn][m]["history"]
        peak_bl = max(bh["peak_vt"])
        # additional reduction attributable to intervention over natural decay
        extra = 100.0 * (bh["peak_vt"][-1] - th["peak_vt"][-1]) / peak_bl
        vals.append(extra)
    metrics[m] = vals

for i, m in enumerate(("thermal", "momentum", "combined")):
    ax.bar(x + (i-1) * w, metrics[m], w, label=m, color=colors[m])
ax.set_xticks(x)
ax.set_xticklabels([s.replace("_", "\n") for s in scenarios], fontsize=9)
ax.axhline(0, color="k", lw=0.5)
ax.set_ylabel("Additional peak v_θ reduction over baseline decay (%)")
ax.set_title("AEOLUS intervention effect vs. natural viscous decay")
ax.grid(alpha=0.3, axis="y")
ax.legend()
fig.tight_layout()
fig.savefig(OUT_DIR / "intervention_effect_bar.png", dpi=110)
plt.close(fig)

# ---- Pressure deficit time series ------------------------------------------
fig, axes = plt.subplots(2, 3, figsize=(14, 8))
axes = axes.flatten()
for i, scn in enumerate(scenarios):
    ax = axes[i]
    for m in modes:
        h = data[scn][m]["history"]
        ax.plot(h["t"], np.array(h["min_p_deficit"]) / 100.0,
                color=colors[m], label=m, lw=1.6)
    ax.set_title(scn, fontsize=10)
    ax.set_xlabel("t (s)")
    ax.set_ylabel("Δp (hPa)")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=7, loc="lower right")
axes[-1].axis("off")
fig.suptitle("Cyclostrophic core-pressure deficit", fontsize=12)
fig.tight_layout()
fig.savefig(OUT_DIR / "pressure_deficit_timeseries.png", dpi=110)
plt.close(fig)

# ---- Ensemble box plot -----------------------------------------------------
if "_ensemble_moore" in data:
    ens = data["_ensemble_moore"]
    reduc_vt = [e["reduction_vt_pct"] for e in ens]
    reduc_om = [e["reduction_omega_pct"] for e in ens]
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.boxplot([reduc_vt, reduc_om], tick_labels=["Δv_t %", "Δω %"])
    ax.set_title("Moore EF5 stochastic ensemble (10 seeds) — combined intervention")
    ax.set_ylabel("reduction from baseline peak (%)")
    ax.grid(alpha=0.3, axis="y")
    for i, vals in enumerate((reduc_vt, reduc_om)):
        ax.scatter([i+1]*len(vals), vals, alpha=0.5, s=20)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "ensemble_boxplot.png", dpi=110)
    plt.close(fig)

print("Plots written to", OUT_DIR)
