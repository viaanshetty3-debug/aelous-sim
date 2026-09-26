"""Run AEOLUS intervention logic against the independent real-world test bed.

Compares four strategies per scenario:
    baseline   -- no intervention
    thermal    -- AEOLUS Thermal RFD only
    momentum   -- AEOLUS Momentum Sink only
    combined   -- AEOLUS both interventions

For each of five real-storm scenarios (Andover, Moore, El Reno, Joplin,
Tuscaloosa) plus a stochastic ensemble around Moore/EF5.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

from tornado_world import TornadoWorld, Scenario, SCENARIOS
from aeolus_adapter import AeolusInterventionAdapter


# ---------------------------------------------------------------------------
#  Runner
# ---------------------------------------------------------------------------

def run_case(scenario: Scenario, mode: str, n_steps: int = 200,
             start_step: int = 20, seed: int = 42, silent: bool = False,
             nr: int = 50, nz: int = 35):
    """Run one (scenario, mode) case; return metrics history."""
    world = TornadoWorld(scenario, seed=seed, nr=nr, nz=nz)
    if mode == "baseline":
        adapter = None
    elif mode == "thermal":
        adapter = AeolusInterventionAdapter(world, use_thermal=True, use_momentum=False,
                                            start_step=start_step)
    elif mode == "momentum":
        adapter = AeolusInterventionAdapter(world, use_thermal=False, use_momentum=True,
                                            start_step=start_step)
    elif mode == "combined":
        adapter = AeolusInterventionAdapter(world, use_thermal=True, use_momentum=True,
                                            start_step=start_step)
    else:
        raise ValueError(mode)

    t0 = time.time()
    for k in range(n_steps):
        forcings = adapter.forcings(k) if adapter is not None else None
        world.step(intervention_forcings=forcings)
        m = world.diagnose_metrics(t=k * world.dt)
        if not silent and k % 40 == 0:
            print(f"  [{mode:8s}] step {k:3d} t={m['t']:5.1f}s | "
                  f"peak_vt={m['peak_vt']:6.2f} m/s | "
                  f"ω_core={m['core_omega']:6.3f} 1/s | "
                  f"Δp={m['min_p_deficit']:8.1f} Pa | "
                  f"peak_w={m['peak_w']:5.2f} m/s")
    elapsed = time.time() - t0

    return {
        "scenario": scenario.name,
        "ef_scale": scenario.ef_scale,
        "mode": mode,
        "history": world.history,
        "elapsed_s": elapsed,
        "final_state": {
            "peak_vt": world.history["peak_vt"][-1],
            "core_omega": world.history["core_omega"][-1],
            "min_p_deficit": world.history["min_p_deficit"][-1],
            "ke": world.history["ke"][-1],
            "circulation_1km": world.history["circulation_1km"][-1],
            "peak_w": world.history["peak_w"][-1],
        },
    }


def summarize_pair(baseline, treatment):
    """Compute reduction metrics for one intervention vs baseline."""
    hb = baseline["history"]
    ht = treatment["history"]
    # Use peak baseline value as reference and treatment final for reduction
    peak_vt_baseline = max(hb["peak_vt"])
    peak_omega_baseline = max(hb["core_omega"])
    final_vt = ht["peak_vt"][-1]
    final_omega = ht["core_omega"][-1]
    reduction_vt_pct = 100.0 * (1.0 - final_vt / max(peak_vt_baseline, 1e-3))
    reduction_omega_pct = 100.0 * (1.0 - final_omega / max(peak_omega_baseline, 1e-3))

    # time-to-suppress: first step where treatment falls to <30% of baseline peak vt
    t_ss = None
    for k, (t, v) in enumerate(zip(ht["t"], ht["peak_vt"])):
        if v < 0.30 * peak_vt_baseline:
            t_ss = t
            break

    # reformation risk: post-suppression max vt / min vt during treatment
    if t_ss is not None:
        idx_min = int(np.argmin(ht["peak_vt"]))
        if idx_min < len(ht["peak_vt"]) - 1:
            reformation_ratio = float(np.max(ht["peak_vt"][idx_min:]) /
                                      max(np.min(ht["peak_vt"][idx_min:]), 1e-3))
        else:
            reformation_ratio = 1.0
    else:
        reformation_ratio = float("nan")

    # KE decay
    ke_ratio = ht["ke"][-1] / max(hb["ke"][-1], 1e-3)

    return {
        "peak_vt_baseline": peak_vt_baseline,
        "final_vt_treatment": final_vt,
        "peak_omega_baseline": peak_omega_baseline,
        "final_omega_treatment": final_omega,
        "reduction_vt_pct": reduction_vt_pct,
        "reduction_omega_pct": reduction_omega_pct,
        "time_to_suppress_s": t_ss,
        "reformation_ratio": reformation_ratio,
        "ke_ratio_treatment_over_baseline": ke_ratio,
    }


# ---------------------------------------------------------------------------
#  Main
# ---------------------------------------------------------------------------

def main():
    out_dir = Path(__file__).parent / "results"
    out_dir.mkdir(exist_ok=True)

    all_results = {}

    # ---- Deterministic scenario sweep (5 storms × 4 modes)
    print("\n" + "=" * 78)
    print(" DETERMINISTIC SCENARIO SWEEP")
    print("=" * 78)
    for scn in SCENARIOS:
        print(f"\n[{scn.name} — {scn.ef_scale} | CAPE={scn.cape:.0f} J/kg | "
              f"shear01={scn.shear_0_1km:.0f} m/s | target v_t={scn.peak_vt_target} m/s]")
        results = {}
        for mode in ("baseline", "thermal", "momentum", "combined"):
            r = run_case(scn, mode)
            results[mode] = r
        summary = {}
        for mode in ("thermal", "momentum", "combined"):
            summary[mode] = summarize_pair(results["baseline"], results[mode])
        results["_summary"] = summary
        all_results[scn.name] = results

        # Console tabular summary
        print(f"    {'mode':<10} {'Δv_t %':>8} {'Δω %':>8} {'t_ss (s)':>10} "
              f"{'reform':>8} {'KE ratio':>10}")
        for mode in ("thermal", "momentum", "combined"):
            s = summary[mode]
            tss = f"{s['time_to_suppress_s']:.1f}" if s['time_to_suppress_s'] is not None else "n/a"
            rf = f"{s['reformation_ratio']:.2f}" if not np.isnan(s['reformation_ratio']) else "n/a"
            print(f"    {mode:<10} {s['reduction_vt_pct']:>7.2f} {s['reduction_omega_pct']:>7.2f} "
                  f"{tss:>10} {rf:>8} {s['ke_ratio_treatment_over_baseline']:>10.3f}")

    # ---- Stochastic ensemble around Moore/EF5 (turbulence-seed sweep)
    print("\n" + "=" * 78)
    print(" STOCHASTIC ENSEMBLE (Moore/EF5 base, seeds 0..9)")
    print("=" * 78)
    moore = SCENARIOS[1]
    ensemble = []
    for seed in range(10):
        bl = run_case(moore, "baseline", seed=seed, silent=True)
        co = run_case(moore, "combined", seed=seed, silent=True)
        s = summarize_pair(bl, co)
        ensemble.append({"seed": seed, **s})
        print(f"  seed={seed:2d}: Δv_t={s['reduction_vt_pct']:6.2f}% | "
              f"Δω={s['reduction_omega_pct']:6.2f}% | "
              f"t_ss={s['time_to_suppress_s']} | "
              f"reform={s['reformation_ratio']:.2f}")
    ens_arr = np.array([[e['reduction_vt_pct'], e['reduction_omega_pct'],
                         e['reformation_ratio']] for e in ensemble])
    print(f"\n  ensemble Δv_t   : mean={ens_arr[:,0].mean():.2f}%  std={ens_arr[:,0].std():.2f}%")
    print(f"  ensemble Δω     : mean={ens_arr[:,1].mean():.2f}%  std={ens_arr[:,1].std():.2f}%")
    print(f"  ensemble reform : mean={ens_arr[:,2].mean():.2f}  std={ens_arr[:,2].std():.2f}")
    all_results["_ensemble_moore"] = ensemble

    # ---- Save JSON
    def _sanitize(obj):
        if isinstance(obj, dict):
            return {k: _sanitize(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [_sanitize(x) for x in obj]
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.floating, np.integer)):
            return float(obj)
        return obj

    with open(out_dir / "results.json", "w") as f:
        json.dump(_sanitize(all_results), f, indent=2)
    print(f"\nResults saved to {out_dir/'results.json'}")


if __name__ == "__main__":
    main()
