"""Record field snapshots and render control-vs-intervention MP4 videos.

    python -m aeolus_axisym.movie record --out results/axisym/m35 --version control
    python -m aeolus_axisym.movie record --out results/axisym/m35 --version v7 --extended
    python -m aeolus_axisym.movie render --out results/axisym/m35 --case v7__60s
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from .experiment import find_version, load_state
from .interventions import Device, _sink_env, _thermal_env
from .model import AxisymmetricModel, EnergyLedger
from .tornado import EF_THRESHOLDS, diagnostics, ef_rating

R_SHOW = 2000.0   # m, radius shown
Z_SHOW = 2600.0   # m, height shown (heater sits at ~2.1 km)


def tag_for(version: str, extended: bool):
    return version.replace("/", "-").replace(" ", "_") + ("__60s" if extended else "")


def record(out: Path, version: str, extended: bool, t_len: float, every: float, log=print):
    cfg, st = load_state(out / "mature.npz")
    m = AxisymmetricModel(cfg)
    v = find_version(version, extended)
    d0 = diagnostics(m, st)
    dev = Device(v, m, core_radius=d0["r_core"]) if v is not None else None
    nr = int(np.searchsorted(m.rc, R_SHOW)); nz = int(np.searchsorted(m.zc, Z_SHOW))
    frames = {k: [] for k in ("u", "v", "w", "t", "vmax", "heat_on", "sink_on")}
    t0, next_t, ledger = st.t, st.t, EnergyLedger()
    while True:
        rel = st.t - t0
        if st.t >= next_t - 1e-9:
            uc = 0.5 * (st.u[:-1] + st.u[1:]); wc = 0.5 * (st.w[:, :-1] + st.w[:, 1:])
            frames["u"].append(uc[:nr, :nz].astype(np.float32))
            frames["v"].append((st.M / m.rc[:, None])[:nr, :nz].astype(np.float32))
            frames["w"].append(wc[:nr, :nz].astype(np.float32))
            frames["t"].append(rel)
            frames["vmax"].append(diagnostics(m, st)["v_max_low"])
            frames["heat_on"].append(_thermal_env(v, rel) if v is not None and v.thermal_K else 0.0)
            frames["sink_on"].append(_sink_env(v, rel) if v is not None and v.sink_Pa else 0.0)
            if len(frames["t"]) % 60 == 1:
                log(f"[{version}] recording t+{rel:5.0f}s")
            next_t += every
        if rel >= t_len - 1e-9:
            break
        dt = min(m.stable_dt(st), next_t - st.t)
        if v is not None:
            dt = min([dt] + [t0 + e - st.t for e in (v.active_s, v.total_s, v.sink_off_after or -1)
                             if t0 + e - st.t > 1e-9])
        st = m.step(st, dt, dev.forcing(rel, st) if dev else None, ledger)
    extra = {}
    if dev is not None:
        extra["sink_shape"] = dev.sink_shape[:nr, :nz].astype(np.float32)
        extra["thermal_mask"] = dev.thermal_mask(0.0)[:nr, :nz].astype(np.float32)
    (out / "movie").mkdir(exist_ok=True)
    np.savez_compressed(out / "movie" / f"{tag_for(version, extended)}.npz",
                        rc=m.rc[:nr], zc=m.zc[:nz], label=find_label(version, extended),
                        **{k: np.array(vv) for k, vv in frames.items()}, **extra)


def find_label(version, extended):
    return "No intervention (control)" if version == "control" else version + (" — 60 s injection" if extended else "")


def _ef_label(v):
    return ef_rating(v).replace("below EF0", "<EF0")


def render(out: Path, case: str, fps: int = 30):
    import imageio_ffmpeg
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.animation import FFMpegWriter
    matplotlib.rcParams["animation.ffmpeg_path"] = imageio_ffmpeg.get_ffmpeg_exe()

    C = np.load(out / "movie" / "control.npz")
    X = np.load(out / "movie" / f"{case}.npz")
    rc, zc = C["rc"], C["zc"]
    n = min(len(C["t"]), len(X["t"]))
    vmax_c = 100.0
    cmap = plt.get_cmap("turbo")

    fig = plt.figure(figsize=(16, 9), dpi=100, facecolor="#111")
    gs = fig.add_gridspec(2, 3, width_ratios=[1.35, 1.0, 0.04], left=0.045, right=0.93, top=0.88,
                          bottom=0.06, wspace=0.12, hspace=0.28)
    title = fig.text(0.5, 0.955, "", ha="center", color="white", fontsize=17, weight="bold")
    fig.text(0.5, 0.915, "Axisymmetric AEOLUS tornado model · 1 s of video = 30 s of simulated time",
             ha="center", color="#bbb", fontsize=11)

    # top-down sampling grid
    g = np.linspace(-1500, 1500, 241)
    GX, GY = np.meshgrid(g, g)
    GR = np.hypot(GX, GY)
    j_sfc = int(np.argmin(np.abs(zc - 50.0)))
    q = np.linspace(-1350, 1350, 13)
    QX, QY = np.meshgrid(q, q); QR = np.maximum(np.hypot(QX, QY), 1.0)

    panels = []
    for row, (D, is_case) in enumerate([(C, False), (X, True)]):
        ax_s = fig.add_subplot(gs[row, 0]); ax_t = fig.add_subplot(gs[row, 1])
        for ax in (ax_s, ax_t):
            ax.set_facecolor("black")
            ax.tick_params(colors="#aaa", labelsize=8)
            for s in ax.spines.values():
                s.set_color("#555")
        sec = np.zeros((len(zc), 2 * len(rc)))
        im_s = ax_s.imshow(sec, origin="lower", extent=[-rc[-1] / 1e3, rc[-1] / 1e3, 0, zc[-1] / 1e3],
                           cmap=cmap, vmin=0, vmax=vmax_c, aspect="auto", interpolation="bilinear")
        sub_r = slice(2, len(rc), 6); sub_z = slice(1, len(zc), 6)
        xr = np.concatenate([-rc[sub_r][::-1], rc[sub_r]]) / 1e3
        QZ, QXR = np.meshgrid(zc[sub_z] / 1e3, xr, indexing="ij")
        qv_s = ax_s.quiver(QXR, QZ, np.zeros_like(QXR), np.zeros_like(QZ), color="white", alpha=0.6,
                           scale=700, width=0.0018)
        ax_s.set_xlabel("distance from tornado center (km)", color="#aaa", fontsize=9)
        ax_s.set_ylabel("height (km)", color="#aaa", fontsize=9)
        im_t = ax_t.imshow(np.zeros_like(GR), origin="lower", extent=[-1.5, 1.5, -1.5, 1.5], cmap=cmap,
                           vmin=0, vmax=vmax_c, interpolation="bilinear")
        qv_t = ax_t.quiver(QX / 1e3, QY / 1e3, np.zeros_like(QX), np.zeros_like(QY), color="white",
                           alpha=0.6, scale=900, width=0.003)
        ax_t.set_xlabel("km", color="#aaa", fontsize=9)
        ax_s.set_title("Side view: vertical slice through the tornado", color="#ddd", fontsize=10, loc="left")
        ax_t.set_title("Top-down view at ~50 m above ground", color="#ddd", fontsize=10, loc="left")
        name = fig.text(0.04, 0.905 - row * 0.455 + (0 if row == 0 else 0.005), "", color="white",
                        fontsize=13, weight="bold")
        stat = ax_s.text(0.01, 0.97, "", transform=ax_s.transAxes, color="white", fontsize=11, va="top",
                         bbox=dict(facecolor="black", alpha=0.6, edgecolor="none"))
        dev = ax_s.text(0.99, 0.97, "", transform=ax_s.transAxes, color="#ffcc66", fontsize=10, va="top",
                        ha="right", bbox=dict(facecolor="black", alpha=0.6, edgecolor="none"))
        contours = []
        panels.append(dict(D=D, case=is_case, im_s=im_s, qv_s=qv_s, im_t=im_t, qv_t=qv_t, name=name,
                           stat=stat, dev=dev, ax_s=ax_s, contours=contours, sub_r=sub_r, sub_z=sub_z))
    cax = fig.add_subplot(gs[:, 2])
    cb = fig.colorbar(panels[0]["im_s"], cax=cax)
    cb.set_label("horizontal wind speed (m/s)", color="#ddd")
    cb.ax.tick_params(colors="#aaa")
    for ef, lo in EF_THRESHOLDS:
        if lo < vmax_c:
            cax.axhline(lo, color="white", lw=0.8)
            cax.text(-0.4, lo, f"EF{ef}", color="white", fontsize=8, va="bottom", ha="right",
                     transform=cax.get_yaxis_transform())

    writer = FFMpegWriter(fps=fps, codec="libx264", bitrate=6000, extra_args=["-pix_fmt", "yuv420p"])
    out_mp4 = out / "movie" / f"{case}_vs_control.mp4"
    with writer.saving(fig, str(out_mp4), dpi=100):
        for k in range(n):
            t = float(C["t"][k])
            title.set_text(f"{str(X['label'])}   vs   no intervention        t = +{t:4.0f} s")
            for P in panels:
                D = P["D"]
                u, v, w = D["u"][k], D["v"][k], D["w"][k]
                spd = np.sqrt(u ** 2 + v ** 2).T                         # (z, r)
                P["im_s"].set_data(np.concatenate([spd[:, ::-1], spd], axis=1))
                us = u[P["sub_r"], P["sub_z"]].T; ws = w[P["sub_r"], P["sub_z"]].T
                P["qv_s"].set_UVC(np.concatenate([-us[:, ::-1], us], axis=1),
                                  np.concatenate([ws[:, ::-1], ws], axis=1))
                prof = np.sqrt(u[:, j_sfc] ** 2 + v[:, j_sfc] ** 2)
                P["im_t"].set_data(np.interp(GR, rc, prof, right=prof[-1]))
                ur = np.interp(QR, rc, u[:, j_sfc]); vt = np.interp(QR, rc, v[:, j_sfc])
                P["qv_t"].set_UVC(ur * QX / QR - vt * QY / QR, ur * QY / QR + vt * QX / QR)
                vm = float(D["vmax"][k])
                P["name"].set_text(str(D["label"]))
                P["stat"].set_text(f"peak wind (z≤500 m): {vm:5.1f} m/s  {_ef_label(vm)}")
                for c in P["contours"]:
                    c.remove()
                P["contours"].clear()
                if P["case"]:
                    on = []
                    if D["heat_on"][k] > 0:
                        on.append(f"HEATING ON ({100 * D['heat_on'][k]:.0f}%)")
                        P["contours"].append(_mirror_contour(P["ax_s"], rc, zc, D["thermal_mask"], "#ff6644"))
                    if D["sink_on"][k] > 0:
                        on.append(f"SUCTION + BLACKOUT ON ({100 * D['sink_on'][k]:.0f}%)")
                        P["contours"].append(_mirror_contour(P["ax_s"], rc, zc, D["sink_shape"], "#66ccff"))
                    P["dev"].set_text("   ".join(on) if on else "device off")
            writer.grab_frame(facecolor=fig.get_facecolor())
    plt.close(fig)
    return out_mp4


def _mirror_contour(ax, rc, zc, field, color):
    xr = np.concatenate([-rc[::-1], rc]) / 1e3
    f = np.concatenate([field[::-1], field], axis=0).T
    return ax.contour(xr, zc / 1e3, f, levels=[0.5], colors=[color], linewidths=1.5, linestyles="--")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("record"); r.add_argument("--out", type=Path, required=True)
    r.add_argument("--version", required=True); r.add_argument("--extended", action="store_true")
    r.add_argument("--t-len", type=float, default=600.0); r.add_argument("--every", type=float, default=1.0)
    v = sub.add_parser("render"); v.add_argument("--out", type=Path, required=True)
    v.add_argument("--case", required=True)
    a = ap.parse_args()
    if a.cmd == "record":
        record(a.out, a.version, a.extended, a.t_len, a.every, log=lambda s: print(s, flush=True))
    else:
        print(render(a.out, a.case))


if __name__ == "__main__":
    main()
