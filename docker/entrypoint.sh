#!/bin/bash
# HYGMA Docker Entrypoint
# Checks SMAC setup, then executes the provided command

echo "========================================"
echo " HYGMA Mechanism Verification Container"
echo "========================================"
echo " Python:  $(python3 --version)"
echo " PyTorch: $(python3 -c 'import torch; print(torch.__version__)')"
echo " CUDA:    $(python3 -c 'import torch; print(torch.cuda.is_available())')"
echo " SC2PATH: ${SC2PATH}"
echo ""

# Check SC2
if [ -f "${SC2PATH}/SC2_x64" ] || [ -f "${SC2PATH}/StarCraftII.exe" ]; then
    echo "[OK] StarCraft II found at ${SC2PATH}"
else
    echo "[WARN] StarCraft II NOT found at ${SC2PATH}"
    echo "       Run: download_sc2.sh to install"
    echo ""
fi

# Check SMAC maps
MAP_DIR="${SC2PATH}/Maps/SMAC_Maps"
if [ -d "$MAP_DIR" ]; then
    MAP_COUNT=$(ls "$MAP_DIR" 2>/dev/null | wc -l)
    echo "[OK] SMAC maps found: ${MAP_COUNT} directories"
else
    echo "[WARN] SMAC maps not found at ${MAP_DIR}"
    echo "       Run: python3 -m smac.bin.map_list  to check"
    echo ""
fi

echo "========================================"
exec "$@"
