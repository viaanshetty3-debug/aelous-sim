"""Set up and launch CM1 runs on Colab, and summarise their stats files.

python cm1run.py start NAME key=value [key=value ...]   # copies run/, edits namelist, launches in background
python cm1run.py stats NAME                            # prints time series of key storm diagnostics
"""
import os, re, shutil, struct, subprocess, sys
from pathlib import Path

CM1 = Path("/content/CM1")
RUNS = Path("/content/runs")


def edit_namelist(text, changes):
    for key, val in changes.items():
        pat = re.compile(rf"^(\s*{re.escape(key)}\s*=\s*)([^,\n]*)(,?)", re.M)
        text, n = pat.subn(lambda m: f"{m.group(1)}{val}{m.group(3)}", text, count=1)
        if n != 1:
            raise SystemExit(f"namelist key not found: {key}")
    return text


def start(name, args):
    changes = dict(a.split("=", 1) for a in args)
    d = RUNS / name
    if d.exists():
        shutil.rmtree(d)
    shutil.copytree(CM1 / "run", d, symlinks=True)
    src = CM1 / "run/config_files/supercell/namelist.input"
    (d / "namelist.input").write_text(edit_namelist(src.read_text(), changes))
    exe = sorted((CM1 / "run").glob("cm1*.exe"), key=os.path.getmtime)[-1]
    env = dict(os.environ, OMP_NUM_THREADS=os.environ.get("OMP_NUM_THREADS", "8"), OMP_STACKSIZE="512M")
    cmd = f"ulimit -s unlimited; cd {d} && setsid nohup {exe} namelist.input < /dev/null > cm1.log 2>&1 &"
    subprocess.run(["bash", "-c", cmd], env=env, check=True)
    print(f"started {name} with {exe.name}: {changes}")


def read_ctl(ctl):
    lines = ctl.read_text().splitlines()
    names, nt, inside = [], None, False
    for ln in lines:
        parts = ln.split()
        if not parts:
            continue
        key = parts[0].lower()
        if key == "tdef":
            nt = int(parts[1])
        elif key == "vars":
            inside = True
        elif key == "endvars":
            inside = False
        elif inside:
            names.append((parts[0], " ".join(parts[3:])))
    return names, nt


def stats(name):
    d = RUNS / name
    ctl = d / "cm1out_stats.ctl"
    dat = d / "cm1out_stats.dat"
    if not dat.exists():
        print(open(d / "cm1.log").read()[-3000:])
        return
    names, _ = read_ctl(ctl)
    raw = dat.read_bytes()
    nv = len(names)
    n = len(raw) // (4 * nv)
    vals = struct.unpack(f"<{n * nv}f", raw[: n * nv * 4])
    want = ["wmax", "wspmax", "wsp0max", "sws", "vortsfc", "vort1km", "vort2km", "vort3km", "sfcprsmin",
            "ppmin", "uh", "maxsws"]
    idx = [i for i, (k, _) in enumerate(names) if k.lower() in want or "vort" in k.lower() or "wsp" in k.lower()
           or k.lower() in ("wmax", "ppmin", "sppmin", "psfcmin")]
    print("vars:", ", ".join(f"{names[i][0]}" for i in idx))
    print("descriptions:", "; ".join(f"{names[i][0]}={names[i][1]}" for i in idx))
    for t in range(n):
        row = vals[t * nv:(t + 1) * nv]
        print(t, " ".join(f"{row[i]:9.3f}" for i in idx))
    print(open(d / "cm1.log").read()[-600:])


if __name__ == "__main__":
    cmd, name, *rest = sys.argv[1:]
    {"start": start, "stats": lambda n, r: stats(n)}[cmd](name, rest)
