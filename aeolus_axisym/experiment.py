"""Run intervention versions against a no-intervention control from the same mature tornado.

    python -m aeolus_axisym.experiment spinup  --out results/axisym --t-end 1500
    python -m aeolus_axisym.experiment run     --out results/axisym --version v7 [--extended]
    python -m aeolus_axisym.experiment run     --out results/axisym --version control
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import time
from pathlib import Path

import numpy as np

from .interventions import COOL_VERSIONS, FAN_VERSIONS, NULL_VERSION, NULL_VERSION_2, VERSIONS, Device, extended
from .model import AxisymmetricModel, EnergyLedger, ModelConfig, State
from .tornado import diagnostics, spin_up, tornado_config


def save_state(path: Path, cfg: ModelConfig, st: State):
    np.savez(path, u=st.u, w=st.w, M=st.M, b=st.b, t=st.t, cfg=json.dumps(dataclasses.asdict(cfg)))


def load_state(path: Path):
    d = np.load(path)
    cfg = ModelConfig(**json.loads(str(d["cfg"])))
    return cfg, State(d["u"], d["w"], d["M"], d["b"], float(d["t"]))


def find_version(name: str, is_extended: bool):
    if name == "control":
        return None
    for v in VERSIONS + FAN_VERSIONS + COOL_VERSIONS + [NULL_VERSION, NULL_VERSION_2]:
        if v.name == name:
            return extended(v) if is_extended else v
    raise SystemExit(f"unknown version {name!r}; choose from {[v.name for v in VERSIONS]}")


def run(out: Path, version_name: str, is_extended: bool, t_obs: float, every: float, log=print):
    cfg, st = load_state(out / "mature.npz")
    m = AxisymmetricModel(cfg)
    v = find_version(version_name, is_extended)
    d0 = diagnostics(m, st)
    device = Device(v, m, core_radius=d0["r_core"]) if v is not None else None
    ledger = EnergyLedger()
    t_start = st.t
    hist, next_t, wall = [], t_start, time.time()
    while True:
        rel = st.t - t_start
        if st.t >= next_t - 1e-9:
            d = diagnostics(m, st); d["t_rel"] = rel
            d.update(heat_J=ledger.heat_J, removed_air_kg=ledger.removed_air_kg, damping_J=ledger.damping_J,
                     fan_J=ledger.extra.get("fan_J", 0.0), cool_J=ledger.extra.get("cool_J", 0.0))
            if v is not None and v.fan_accel:
                # outward wind the fans produce: max radial velocity in the fan layer near the ring
                near = (np.abs(m.rf - v.fan_r) < 2 * v.fan_width)
                d["fan_outflow_max"] = float(st.u[near][:, m.zc < v.fan_depth].max())
            hist.append(d)
            next_t += every
            if len(hist) % 12 == 1:
                log(f"[{version_name}{' 60s' if is_extended else ''}] t+{rel:6.1f}s v_low={d['v_max_low']:6.2f} "
                    f"Δp={d['p_deficit_hPa']:5.1f} hPa ({time.time() - wall:4.0f}s wall)")
        if rel >= t_obs - 1e-9:
            break
        dt = m.stable_dt(st)
        # land exactly on device on/off edges and report times
        edges = [next_t - st.t, t_start + t_obs - st.t]
        if v is not None:
            edges += [t_start + e - st.t for e in (v.active_s, v.total_s, v.sink_off_after or -1,
                                                   v.fan_on_s if v.fan_accel else -1,
                                                   v.cool_on_s if v.cool_K else -1) if e > rel]
        dt = min([dt] + [e for e in edges if e > 1e-9])
        f = device.forcing(rel, st) if device is not None else None
        st = m.step(st, dt, f, ledger)
    meta = {"version": version_name, "extended": is_extended,
            "params": dataclasses.asdict(v) if v is not None else None,
            "sink_amp_per_s": device.sink_amp if device is not None else 0.0,
            "core_radius_at_start": d0["r_core"], "t_start": t_start, "t_obs": t_obs}
    tag = version_name.replace("/", "-").replace(" ", "_") + ("__60s" if is_extended else "")
    (out / "runs").mkdir(parents=True, exist_ok=True)
    (out / "runs" / f"{tag}.json").write_text(json.dumps({"meta": meta, "history": hist}))
    return hist


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("spinup"); s.add_argument("--out", type=Path, required=True)
    s.add_argument("--t-end", type=float, default=1500.0); s.add_argument("--set", default="{}")
    r = sub.add_parser("run"); r.add_argument("--out", type=Path, required=True)
    r.add_argument("--version", required=True); r.add_argument("--extended", action="store_true")
    r.add_argument("--t-obs", type=float, default=900.0); r.add_argument("--every", type=float, default=5.0)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    if a.cmd == "spinup":
        cfg = tornado_config(**json.loads(a.set))
        m, st, hist = spin_up(cfg, a.t_end, report_every=30.0, log=lambda x: print(x, flush=True))
        save_state(a.out / "mature.npz", cfg, st)
        (a.out / "spinup.json").write_text(json.dumps(hist))
    else:
        run(a.out, a.version, a.extended, a.t_obs, a.every, log=lambda x: print(x, flush=True))


if __name__ == "__main__":
    main()
