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
    """Compute reduction metrics for one intervention vs baseline.

    Reports two distinct notions of effect (both intervention-attributable, i.e.
    baseline decay is factored out):
      * peak_*:      largest reduction observed at any instant vs baseline-at-same-t.
                     Captures transient interventions like thermal RFD.
      * sustained_*: reduction at final step vs baseline-at-final-step.
                     Captures whether the effect persists after intervention ends.

    Also reports the legacy "reported_*" number (drop from baseline peak, includes
    natural decay). Kept for continuity with older logs — do not use as headline.
    """
    hb, ht = baseline["history"], treatment["history"]
    tb = np.asarray(hb["t"])
    vb = np.asarray(hb["peak_vt"]);       wb = np.asarray(hb["core_omega"])
    vt = np.asarray(ht["peak_vt"]);       wt = np.asarray(ht["core_omega"])

    # Intervention-only time series (guard against baseline dropping to 0)
    io_v = 1.0 - vt / np.maximum(vb, 1e-3)
    io_w = 1.0 - wt / np.maximum(wb, 1e-3)

    peak_vt_reduction   = float(np.max(io_v)) * 100.0
    peak_om_reduction   = float(np.max(io_w)) * 100.0
    t_peak_vt = float(tb[int(np.argmax(io_v))])
    t_peak_om = float(tb[int(np.argmax(io_w))])
    sustained_vt = float(io_v[-1]) * 100.0
    sustained_om = float(io_w[-1]) * 100.0

    # Legacy "reported" number (kept but relabeled — includes natural decay)
    peak_vt_baseline = float(vb.max())
    peak_om_baseline = float(wb.max())
    reported_vt = 100.0 * (1.0 - vt[-1] / max(peak_vt_baseline, 1e-3))
    reported_om = 100.0 * (1.0 - wt[-1] / max(peak_om_baseline, 1e-3))

    # time-to-suppress: first t where treatment falls to <50% of baseline-at-same-t
    # (baseline-relative, so it fires even when the baseline is also decaying)
    below = np.where(io_v > 0.5)[0]
    t_ss = float(tb[below[0]]) if len(below) else None

    # reformation: only meaningful if the intervention achieved real suppression
    # first (>10% peak drop). Otherwise "recovery" just measures noise around the
    # baseline and would falsely flag as reformed.
    idx_min = int(np.argmax(io_v))
    if peak_vt_reduction < 10.0:
        recovery = float("nan"); reformed = None    # no effect to reform from
    elif idx_min < len(io_v) - 3:
        recovery = float(np.max(vt[idx_min:] / np.maximum(vb[idx_min:], 1e-3)))
        reformed = recovery > 0.90
    else:
        recovery = float("nan"); reformed = False

    ke_ratio = ht["ke"][-1] / max(hb["ke"][-1], 1e-3)

    return {
        "peak_vt_baseline": peak_vt_baseline,
        "peak_omega_baseline": peak_om_baseline,
        "final_vt_treatment": float(vt[-1]),
        "final_omega_treatment": float(wt[-1]),
        # intervention-only (baseline decay factored out) — USE THESE
        "peak_vt_reduction_pct": peak_vt_reduction,
        "peak_omega_reduction_pct": peak_om_reduction,
        "t_peak_vt_s": t_peak_vt,
        "t_peak_omega_s": t_peak_om,
        "sustained_vt_reduction_pct": sustained_vt,
        "sustained_omega_reduction_pct": sustained_om,
        # legacy — includes natural baseline decay, kept for continuity only
        "reported_vt_reduction_pct": reported_vt,
        "reported_omega_reduction_pct": reported_om,
        "time_to_suppress_s": t_ss,
        "reformation_recovery_ratio": recovery,
        "reformed": bool(reformed),
        "ke_ratio_treatment_over_baseline": ke_ratio,
    }


# ---------------------------------------------------------------------------
#  Main
# ---------------------------------------------------------------------------

def _sink_footprint_check(scn):
    """Return the momentum-sink footprint against the scenario's peak-v_t radius.

    Diagnostic guardrail — catches the class of bug where the sink is placed
    at a fixed radius that misses a wide-core storm (previously broke El Reno).
    """
    from aeolus_adapter import AeolusInterventionAdapter
    from tornado_world import TornadoWorld
    world = TornadoWorld(scn)
    adapter = AeolusInterventionAdapter(world)
    j100 = 4
    v_r_profile = world.v[:, j100]
    r_peak = float(world.r[int(np.argmax(np.abs(v_r_profile)))])
    center, sigma = adapter.mom_r_center, adapter.mom_r_sink / 2.0
    covered = abs(r_peak - center) < sigma
    return {"r_peak_vt": r_peak, "sink_center": center, "sink_sigma": sigma,
            "footprint_lo": center - sigma, "footprint_hi": center + sigma,
            "covers_peak": covered}


def main():
    out_dir = Path(__file__).parent / "results"
    out_dir.mkdir(exist_ok=True)

    all_results = {}

    # ---- Pre-flight: sink footprint vs peak-v_t radius per scenario
    print("\n" + "=" * 78)
    print(" PRE-FLIGHT — sink footprint vs peak-v_t radius per scenario")
    print("=" * 78)
    print(f"    {'scenario':<24} {'r_peak_vt':>10} {'sink center':>12} "
          f"{'σ_r':>6} {'footprint':>18} {'covers?':>8}")
    for scn in SCENARIOS:
        fp = _sink_footprint_check(scn)
        print(f"    {scn.name:<24} {fp['r_peak_vt']:>9.0f}m {fp['sink_center']:>11.0f}m "
              f"{fp['sink_sigma']:>5.0f}m [{fp['footprint_lo']:>5.0f},{fp['footprint_hi']:>5.0f}]m "
              f"{'✓' if fp['covers_peak'] else '✗ MISS':>8}")

    # ---- Deterministic scenario sweep (5 storms × 4 modes)
    print("\n" + "=" * 78)
    print(" DETERMINISTIC SCENARIO SWEEP")
    print(" Δω_peak: intervention-only reduction at moment of peak effect")
    print(" Δω_sust: intervention-only reduction sustained at simulation end")
    print(" reform : does treatment recover to >90% of baseline after peak?")
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

        # Console tabular summary — intervention-only numbers as headline
        print(f"    {'mode':<10} {'Δω_peak':>8} {'Δω_sust':>8} {'Δvt_peak':>9} "
              f"{'Δvt_sust':>9} {'t_ss(s)':>8} {'reform':>7}")
        for mode in ("thermal", "momentum", "combined"):
            s = summary[mode]
            tss = f"{s['time_to_suppress_s']:.1f}" if s['time_to_suppress_s'] is not None else "n/a"
            if s['reformed'] is None:
                rf = "n/e"          # no effect — reformation not applicable
            elif s['reformed']:
                rf = "YES"
            else:
                rf = "no"
            print(f"    {mode:<10} {s['peak_omega_reduction_pct']:>7.1f}% "
                  f"{s['sustained_omega_reduction_pct']:>7.1f}% "
                  f"{s['peak_vt_reduction_pct']:>8.1f}% "
                  f"{s['sustained_vt_reduction_pct']:>8.1f}% "
                  f"{tss:>8} {rf:>7}")
        # Note the legacy number so anyone comparing to old logs isn't confused
        s_comb = summary['combined']
        print(f"    (legacy 'reported' Δω incl. natural decay: "
              f"{s_comb['reported_omega_reduction_pct']:.1f}% — do NOT quote as intervention effect)")

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
        print(f"  seed={seed:2d}: Δω_peak={s['peak_omega_reduction_pct']:6.2f}% | "
              f"Δω_sust={s['sustained_omega_reduction_pct']:6.2f}% | "
              f"Δvt_peak={s['peak_vt_reduction_pct']:6.2f}% | "
              f"Δvt_sust={s['sustained_vt_reduction_pct']:6.2f}% | "
              f"reformed={'YES' if s['reformed'] else ('n/e' if s['reformed'] is None else 'no')}")
    ens_arr = np.array([[e['peak_omega_reduction_pct'], e['sustained_omega_reduction_pct'],
                         e['peak_vt_reduction_pct'],    e['sustained_vt_reduction_pct']]
                        for e in ensemble])
    print(f"\n  ensemble Δω_peak  : mean={ens_arr[:,0].mean():.2f}%  std={ens_arr[:,0].std():.2f}%")
    print(f"  ensemble Δω_sust  : mean={ens_arr[:,1].mean():.2f}%  std={ens_arr[:,1].std():.2f}%")
    print(f"  ensemble Δvt_peak : mean={ens_arr[:,2].mean():.2f}%  std={ens_arr[:,2].std():.2f}%")
    print(f"  ensemble Δvt_sust : mean={ens_arr[:,3].mean():.2f}%  std={ens_arr[:,3].std():.2f}%")
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
