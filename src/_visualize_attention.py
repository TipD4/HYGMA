# Visualize HGCN Attention - heatmaps + within/cross group analysis
import os,glob,h5py
import numpy as np
import matplotlib;matplotlib.use("Agg")
import matplotlib.pyplot as plt

ATTN_DIR = os.path.join("..", "results", "attention_data")
FIG_DIR = os.path.join("..", "results", "_figures")
os.makedirs(FIG_DIR, exist_ok=True)

def load_attention_files():
    """Load all HDF5 attention files."""
    files = glob.glob(os.path.join(ATTN_DIR, "*.h5"))
    print(f"Found {len(files)} attention files")
    return files

def compute_within_cross(attn_matrix, groups):
    """Compute within-group vs cross-group attention."""
    n_agents, n_groups = attn_matrix.shape[-2:]
    agent_to_group = {}
    for g_idx, group in enumerate(groups):
        for agent in group:
            agent_to_group[agent] = g_idx
    within = []; cross = []
    for a in range(n_agents):
        for g in range(n_groups):
            val = attn_matrix[0, a, g]
            if agent_to_group.get(a) == g: within.append(val)
            else: cross.append(val)
    return np.mean(within) if within else 0, np.mean(cross) if cross else 0

def main():
    print("HGCN Attention Visualization")
    files = load_attention_files()
    if not files:
        print("No attention files found. Run experiments first.")
        return
    for fp in files:
        print(f"Processing: {fp}")

if __name__ == "__main__": main()