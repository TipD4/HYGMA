#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="${SCRIPT_DIR}/src"
RESULTS_DIR="${SCRIPT_DIR}/results"
STAMP="$(date +%Y-%m-%d_%H-%M-%S)"
RUN_DIR="${RESULTS_DIR}/server_launcher/ablation_batch_${STAMP}"
LOG_FILE="${RUN_DIR}/launcher.log"
PID_FILE="${RUN_DIR}/launcher.pid"

MODE="background"
if [[ "${1:-}" == "--foreground" ]]; then
    MODE="foreground"
    shift
fi

mkdir -p "${RUN_DIR}"
mkdir -p "${RESULTS_DIR}/sacred"
mkdir -p "${RESULTS_DIR}/models"

# --- conda activation (same pattern as mechanism batch) ---
CONDA_EXE=""
for candidate in \
    "${HOME}/Tool/anaconda3/bin/conda" \
    "${HOME}/miniconda3/bin/conda" \
    "${HOME}/anaconda3/bin/conda" \
    /opt/conda/bin/conda \
    /usr/local/anaconda3/bin/conda; do
    if [[ -x "${candidate}" ]]; then
        CONDA_EXE="${candidate}"
        break
    fi
done

CONDA_SH="$(dirname "${CONDA_EXE}")/../etc/profile.d/conda.sh"
if [[ -f "${CONDA_SH}" ]]; then
    source "${CONDA_SH}"
fi
conda activate hygma 2>/dev/null || conda activate base 2>/dev/null || true

export SC2PATH="${SC2PATH:-${HOME}/StarCraftII}"

echo "=== HYGMA Mechanism Attribution Batch ==="
echo "Stamp:    ${STAMP}"
echo "Run dir:  ${RUN_DIR}"
echo "Python:   $(which python)"
echo ""

if [[ "${MODE}" == "background" ]]; then
    echo "Starting in background (PID to ${PID_FILE})"
    nohup python "${SRC_DIR}/run_experiments.py" --ablation \
        > "${LOG_FILE}" 2>&1 &
    echo $! > "${PID_FILE}"
    echo "Monitor: tail -f ${LOG_FILE}"
else
    python "${SRC_DIR}/run_experiments.py" --ablation \
        2>&1 | tee "${LOG_FILE}"
fi
