#!/bin/bash
# Run complete comparison suite: 80-step and 160-step simulations for all modes

set -e

STEPS_SHORT=80
STEPS_LONG=160
GRID_SIZE=96

echo "======================================================================"
echo "AEOLUS COMPARATIVE SIMULATION SUITE"
echo "======================================================================"
echo "Grid: ${GRID_SIZE}³"
echo "Interventions: thermal + momentum (both)"
echo ""

# 80-step runs (quicker, for validation)
echo "PHASE 1: Quick 80-step validation runs"
echo "--------------------------------------"

for mode in rankine realworld hybrid; do
    echo ""
    echo "Running ${mode}_${STEPS_SHORT}..."
    output_dir="results/${mode}_${STEPS_SHORT}"
    python3 main.py \
        --initialization "${mode}" \
        --n-steps "${STEPS_SHORT}" \
        --grid-size "${GRID_SIZE}" \
        --intervention both \
        --output "${output_dir}" 2>&1 | tail -20
done

echo ""
echo "PHASE 1 complete. Showing 80-step comparison:"
python3 view_comparison.py

# 160-step runs (full fidelity)
echo ""
echo "======================================================================"
echo "PHASE 2: Full 160-step production runs"
echo "--------------------------------------"

for mode in rankine realworld hybrid; do
    echo ""
    echo "Running ${mode}_${STEPS_LONG}..."
    output_dir="results/${mode}_${STEPS_LONG}"
    python3 main.py \
        --initialization "${mode}" \
        --n-steps "${STEPS_LONG}" \
        --grid-size "${GRID_SIZE}" \
        --intervention both \
        --output "${output_dir}" 2>&1 | tail -20
done

echo ""
echo "PHASE 2 complete. Showing full 160-step comparison:"
python3 view_comparison.py

echo ""
echo "======================================================================"
echo "COMPARISON SUITE COMPLETE"
echo "======================================================================"
echo "Results:"
ls -lh results/*/summary.txt | awk '{print $9, "(" $5 ")"}'
