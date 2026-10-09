#!/bin/zsh
# Run the control, two noise-floor runs and every intervention version from one mature tornado.
# Usage: aeolus_axisym/run_all.sh results/axisym/<spinup-dir> [t_obs_seconds] [parallel_jobs]
set -u
OUT=$1; TOBS=${2:-3000}; JOBS=${3:-7}
PY=${PYTHON:-.venv/bin/python}
mkdir -p "$OUT/logs"

specs=()
for v in "control" "null (0.001 K)" "null-b (0.001 K ring)" \
         "v1" "v2/v3" "v4/v5" "v6 thermal-only" "v6 momentum-only" "v6 both-high" "v7" \
         "RW80" "RW80 + assumed braking"; do
  specs+=("$v|")
done
for v in "v1" "v2/v3" "v4/v5" "v6 thermal-only" "v6 momentum-only" "v6 both-high" "v7"; do
  specs+=("$v|--extended")
done

run_one() {
  local v=${1%%|*} ext=${1#*|}
  local tag=${${v//\//-}// /_}${ext:+__60s}
  if $PY -m aeolus_axisym.experiment run --out "$OUT" --version "$v" ${=ext} --t-obs "$TOBS" \
       > "$OUT/logs/$tag.log" 2>&1; then
    echo "done: $v $ext"
  else
    echo "FAILED: $v $ext (see $OUT/logs/$tag.log)"
  fi
}

pids=()
for s in "${specs[@]}"; do
  # `jobs` inside $(...) can't see this shell's jobs, so track PIDs directly
  while true; do
    alive=()
    for p in $pids; do kill -0 $p 2>/dev/null && alive+=($p); done
    pids=($alive)
    (( ${#pids} < JOBS )) && break
    sleep 2
  done
  run_one "$s" &
  pids+=($!)
done
wait
echo "all runs finished"
