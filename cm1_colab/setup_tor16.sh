#!/bin/bash
# Rebuild CM1 on a fresh Colab VM and launch the stronger-shear control run "tor16"
# (r_low=16 quarter-circle hodograph, no cooling), with automatic Drive backup.
# Prereq: Drive mounted at /content/drive (python: drive.mount('/content/drive')).
# Usage: bash /content/setup_tor16.sh > /content/setup.log 2>&1 &
set -u
RUN=tor16
D=/content/drive/MyDrive/aeolus_cm1
mkdir -p "$D/$RUN" "$D/scripts" || { echo "DRIVE NOT MOUNTED"; exit 1; }
cp /content/cm1run.py /content/mksnd.py /content/patch_aeo.py /content/setup_tor16.sh "$D/scripts/"

# 1. build CM1 (gfortran + OpenMP)
cd /content
[ -d CM1 ] || git clone -q --depth 1 https://github.com/NCAR/CM1
cd /content/CM1/src && make -j8 FC=gfortran USE_OPENMP=true > /content/build.log 2>&1
echo "BUILD EXIT=$?"; ls -la /content/CM1/run/cm1.exe || exit 1
git -C /content/CM1 rev-parse HEAD > "$D/scripts/cm1_commit.txt"

# 2. sounding: WK thermo, qv cap 15 g/kg, r_low=16; shift winds by Bunkers motion (grid follows storm, imove=0)
cd /content
python3 - <<'EOF'
import re, subprocess
out = subprocess.run(['python3', '/content/mksnd.py', '/content/snd_r16', '15', '16'], capture_output=True, text=True).stdout
print(out)
cx, cy = map(float, re.search(r'umove=(-?[\d.]+) vmove=(-?[\d.]+)', out).groups())
L = open('/content/snd_r16').read().splitlines()
new = [L[0]] + [f"{float(a):10.1f} {float(b):10.4f} {float(c):10.5f} {float(u)-cx:9.3f} {float(v)-cy:9.3f}"
                for a, b, c, u, v in (l.split() for l in L[1:])]
open('/content/CM1/run/input_sounding', 'w').write('\n'.join(new) + '\n')
print('shifted by', cx, cy)
EOF
head -3 /content/CM1/run/input_sounding

# 3. launch (same settings as the lost tor125, but sounding r16 and 3 h)
export OMP_NUM_THREADS=8
python3 /content/cm1run.py start $RUN nx=292 ny=292 nz=49 dx=125.0 dy=125.0 dtl=0.75 adapt_dt=1 \
  rstfrq=600.0 timax=10800.0 \
  stretch_x=1 dx_inner=125.0 dx_outer=1875.0 nos_x_len=24000.0 tot_x_len=124000.0 \
  stretch_y=1 dy_inner=125.0 dy_outer=1875.0 nos_y_len=24000.0 tot_y_len=124000.0 \
  stretch_z=1 ztop=17750.0 str_bot=500.0 str_top=3250.0 dz_bot=50.0 dz_top=500.0 \
  isnd=7 imove=0 bbc=3 sfcmodel=1 cecd=1 cnstcd=0.005 pertflx=1 || exit 1
R=/content/runs/$RUN
cp $R/namelist.input $R/input_sounding "$D/$RUN/"

# 4. backup loop: every 10 min copy stats + log, and the newest complete restart set (older ones removed on Drive)
while pgrep -f "cm1.exe namelist.input" > /dev/null; do
  sleep 600
  cp $R/cm1out_stats.ctl $R/cm1out_stats.dat $R/cm1.log "$D/$RUN/" 2>/dev/null
  n=$(ls $R/cm1rst_*_x.dat 2>/dev/null | tail -1 | sed -E 's/.*cm1rst_([0-9]+)_x.dat/\1/')
  if [ -n "$n" ] && [ ! -f "$D/$RUN/cm1rst_${n}_x.dat" ]; then
    sleep 60
    cp $R/cm1rst_${n}_*.dat "$D/$RUN/" && find "$D/$RUN" -name 'cm1rst_*' ! -name "cm1rst_${n}_*" -delete
    echo "$(date -u +%T) backed up restart $n"
  fi
done
cp $R/cm1out_stats.ctl $R/cm1out_stats.dat $R/cm1.log "$D/$RUN/"
echo "RUN ENDED $(date -u)"; tail -3 $R/cm1.log
