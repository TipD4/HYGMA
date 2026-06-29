#!/bin/bash
set -e

# === Auto-detect paths from script location ===
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="${SCRIPT_DIR}/src"

echo '==============================================='
echo ' HYGMA Mechanism Verification - Auto Pipeline'
echo ' Started:' $(date '+%Y-%m-%d %H:%M:%S')
echo '==============================================='

# === SC2 path (override with env var if set) ===
if [ -z "${SC2PATH}" ]; then
    SC2PATH="${HOME}/StarCraftII"
    export SC2PATH
fi

# === Conda activation (auto-detect or skip if already in conda) ===
if [ -z "${CONDA_DEFAULT_ENV}" ]; then
    # Try common conda locations
    for conda_base in "${HOME}/Tool/anaconda3" "${HOME}/anaconda3" "${HOME}/miniconda3" /opt/conda; do
        if [ -f "${conda_base}/etc/profile.d/conda.sh" ]; then
            source "${conda_base}/etc/profile.d/conda.sh"
            break
        fi
    done
fi
# Activate hygma env if not already active
if [ "${CONDA_DEFAULT_ENV}" != "hygma" ]; then
    conda activate hygma 2>/dev/null || echo "Warning: could not activate hygma conda env, using current python"
fi

cd "${SRC}"

# ---- Phase 1: Stage A experiments (100K, 3 runs) ----
echo ''
echo '[1/5] Running Stage A experiments...'
python queue_verify_stageA.py
echo '[1/5] Done'

# ---- Check gate ----
echo ''
echo '[2/5] Checking clustering gate...'
python -c "
import csv, os
fp = os.path.join('..', 'results', 'clustering_logs', '5m_vs_6m_dynamic_seed1.csv')
if os.path.exists(fp):
    rows = list(csv.DictReader(open(fp)))
    uc = int(rows[-1].get('update_count', 0)) if rows else 0
    cc = int(rows[-1].get('check_count', 0)) if rows else 0
    print(f'  check_count={cc}, update_count={uc}')
    if uc == 0:
        print('  GATE: FAIL - clustering never updated groups')
        print('  CSV content:')
        for r in rows: print('   ', r.get('rejection_reason','?'))
    else:
        print('  GATE: PASS - clustering triggered and changed groups')
"

# ---- Phase 2: Analysis ----
echo ''
echo '[3/5] Running clustering analysis...'
cd "${SCRIPT_DIR}"
python src/_analyze_clustering.py

echo ''
echo '[4/5] Running synthesis (Q1-Q5 + Evidence Chain)...'
python src/_synthesize_answers.py

# ---- Phase 3: Stage B only if gate passed ----
echo ''
echo '[5/5] Decision...'
python -c "
import csv, os
fp = 'results/clustering_logs/5m_vs_6m_dynamic_seed1.csv'
if os.path.exists(fp):
    rows = list(csv.DictReader(open(fp)))
    uc = int(rows[-1].get('update_count', 0)) if rows else 0
    if uc > 0:
        print('  Clustering confirmed working. Run Stage B (500K) next:')
        print('    cd ${SRC}')
        print('    python queue_verify_stageB.py')
    else:
        print('  Clustering NOT working. Do NOT run Stage B yet.')
        print('  Send stageA.log to developer for debugging.')
"

echo ''
echo '==============================================='
echo ' Pipeline Complete:' $(date '+%Y-%m-%d %H:%M:%S')
echo ' Logs: results/clustering_logs/'
echo ' Figures: results/_figures/'
echo '==============================================='
