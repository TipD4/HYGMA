#!/bin/bash
set -e

echo "=== HYGMA Server Setup ==="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ---- Conda ----
echo ""
echo "[1/4] Setting up conda environment..."
if ! command -v conda &>/dev/null; then
    # Try to find and source conda
    for _c in /mnt/storage/qianhaoming/Tool/anaconda3 "${HOME}/anaconda3" "${HOME}/miniconda3" /opt/conda; do
        if [ -f "${_c}/etc/profile.d/conda.sh" ]; then
            source "${_c}/etc/profile.d/conda.sh"
            break
        fi
    done
fi

if conda env list | grep -q "^hygma "; then
    echo "  hygma env already exists, updating..."
    conda env update -f "${SCRIPT_DIR}/environment.yml" -n hygma
else
    echo "  Creating hygma env from environment.yml..."
    conda env create -f "${SCRIPT_DIR}/environment.yml"
fi

# ---- StarCraft II ----
echo ""
echo "[2/4] Checking StarCraft II..."
if [ -z "${SC2PATH}" ]; then
    SC2PATH="${HOME}/StarCraftII"
fi
if [ ! -d "${SC2PATH}" ]; then
    echo "  WARNING: SC2 not found at ${SC2PATH}"
    echo "  Set SC2PATH env var or install StarCraft II to ${HOME}/StarCraftII"
else
    echo "  SC2 found at ${SC2PATH}"
fi

# ---- SMAC maps ----
echo ""
echo "[3/4] Checking SMAC maps..."
SMAC_MAPS="${SC2PATH}/Maps/SMAC_Maps"
if [ ! -d "${SMAC_MAPS}" ]; then
    echo "  WARNING: SMAC maps not found. Download from:"
    echo "    https://github.com/oxwhirl/smac#installing-starcraft-ii"
else
    echo "  SMAC maps found at ${SMAC_MAPS}"
fi

# ---- Results dirs ----
echo ""
echo "[4/4] Creating results directories..."
mkdir -p "${SCRIPT_DIR}/results/clustering_logs"
mkdir -p "${SCRIPT_DIR}/results/_figures"
mkdir -p "${SCRIPT_DIR}/results/sacred"

echo ""
echo "=== Setup Complete ==="
echo "  conda activate hygma"
echo "  export SC2PATH=${SC2PATH}"
echo "  bash run_pipeline.sh"
