# Communication Baseline - message count + attention entropy
import os,glob,json,h5py
import numpy as np
from collections import defaultdict

ATTN_DIR = os.path.join("..", "results", "attention_data")
OUT_DIR = os.path.join("..", "results", "comm_baseline")
os.makedirs(OUT_DIR, exist_ok=True)

def compute_entropy(attn):
    """Compute attention entropy per agent."""
    eps = 1e-8
    attn = attn + eps
    attn = attn / attn.sum(axis=-1, keepdims=True)
    return -np.sum(attn * np.log(attn), axis=-1)

def compute_sparsity(attn, threshold=0.01):
    """Fraction of near-zero attention weights."""
    return np.mean(attn < threshold)

def main():
    print("Communication Baseline Analysis")
    print("Saving communication metrics for VGIB comparison.")
    print("Run experiments with attention recording first.")

if __name__ == "__main__": main()