#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="${SCRIPT_DIR}/src"
RESULTS_DIR="${SCRIPT_DIR}/results"
STAMP="$(date +%Y-%m-%d_%H-%M-%S)"
RUN_DIR="${RESULTS_DIR}/server_launcher/mechanism_batch_${STAMP}"
LOG_FILE="${RUN_DIR}/launcher.log"
PID_FILE="${RUN_DIR}/launcher.pid"

MODE="background"
if [[ "${1:-}" == "--foreground" ]]; then
    MODE="foreground"
    shift
fi

mkdir -p "${RUN_DIR}"
mkdir -p "${RESULTS_DIR}/clustering_logs"
mkdir -p "${RESULTS_DIR}/attention_data"
mkdir -p "${RESULTS_DIR}/sacred"
mkdir -p "${RESULTS_DIR}/models"

if [[ -z "${SC2PATH:-}" ]]; then
    export SC2PATH="${HOME}/StarCraftII"
fi

echo "===================================================="
echo " HYGMA mechanism-first server launcher"
echo " Started: $(date '+%Y-%m-%d %H:%M:%S')"
echo " Mode: ${MODE}"
echo " SC2PATH: ${SC2PATH}"
echo " Run dir: ${RUN_DIR}"
echo "===================================================="

activate_hygma_env() {
    if [[ "${CONDA_DEFAULT_ENV:-}" == "hygma" ]]; then
        return 0
    fi

    local candidates=(
        "${HOME}/anaconda3"
        "${HOME}/miniconda3"
        "/opt/conda"
        "/opt/anaconda3"
        "/usr/local/anaconda3"
        "/mnt/storage/qianhaoming/Tool/anaconda3"
        "${HOME}/Tool/anaconda3"
    )

    local conda_sh=""
    for base in "${candidates[@]}"; do
        if [[ -f "${base}/etc/profile.d/conda.sh" ]]; then
            conda_sh="${base}/etc/profile.d/conda.sh"
            break
        fi
    done

    if [[ -z "${conda_sh}" ]]; then
        echo "ERROR: Cannot find conda.sh. Set HYGMA_PYTHON or activate the hygma env manually."
        exit 1
    fi

    # shellcheck disable=SC1090
    source "${conda_sh}"
    conda activate hygma
}

if [[ -n "${HYGMA_PYTHON:-}" ]]; then
    PYTHON_BIN="${HYGMA_PYTHON}"
else
    activate_hygma_env
    PYTHON_BIN="$(command -v python)"
fi

if [[ ! -x "${PYTHON_BIN}" ]]; then
    echo "ERROR: Python executable not found: ${PYTHON_BIN}"
    exit 1
fi

cd "${SCRIPT_DIR}"

echo "Python: ${PYTHON_BIN}"
echo "Launcher script: ${SRC_DIR}/run_experiments.py"
echo "Log file: ${LOG_FILE}"

CMD=("${PYTHON_BIN}" "${SRC_DIR}/run_experiments.py")

if [[ "${MODE}" == "foreground" ]]; then
    {
        echo "COMMAND: ${CMD[*]}"
        "${CMD[@]}"
    } 2>&1 | tee "${LOG_FILE}"
else
    nohup "${CMD[@]}" > "${LOG_FILE}" 2>&1 &
    PID=$!
    echo "${PID}" > "${PID_FILE}"
    echo "Started in background."
    echo "PID: ${PID}"
    echo "PID file: ${PID_FILE}"
    echo "Tail log with: tail -f ${LOG_FILE}"
fi
