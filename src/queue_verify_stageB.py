"""Stage B: Long Training (500K) — Observe long-term group dynamics.

ONLY run after Phase 2 confirms clustering works.

Four experiments on 5m_vs_6m:
  B1: dynamic seed=1 (500K, interval=5K)
  B2: dynamic seed=2 (500K, interval=5K)
  B3: all_one (500K)
  B4: each_alone (500K)
"""

import subprocess
import os
import sys
import datetime

SRC = os.path.dirname(os.path.abspath(__file__))
os.chdir(SRC)
PY = sys.executable

experiments = [
    ("B1", "5m_vs_6m dynamic (seed=1, 500K)",
     ["--config=hygma", "--env-config=sc2", "with",
      "env_args.map_name=5m_vs_6m", "t_max=500000", "test_interval=10000",
      "seed=1", "grouping_mode=dynamic", "clustering_interval=5000"]),
    ("B2", "5m_vs_6m dynamic (seed=2, 500K)",
     ["--config=hygma", "--env-config=sc2", "with",
      "env_args.map_name=5m_vs_6m", "t_max=500000", "test_interval=10000",
      "seed=2", "grouping_mode=dynamic", "clustering_interval=5000"]),
    ("B3", "5m_vs_6m all_one (500K)",
     ["--config=hygma", "--env-config=sc2", "with",
      "env_args.map_name=5m_vs_6m", "t_max=500000", "test_interval=10000",
      "seed=1", "grouping_mode=all_one"]),
    ("B4", "5m_vs_6m each_alone (500K)",
     ["--config=hygma", "--env-config=sc2", "with",
      "env_args.map_name=5m_vs_6m", "t_max=500000", "test_interval=10000",
      "seed=1", "grouping_mode=each_alone"]),
]

total = len(experiments)
print(f"=== Stage B: Long Training (500K steps) ===")
print(f"Queue: {total} experiments on 5m_vs_6m")
print(f"Expected clustering checks: ~{500000//5000} for dynamic runs")
print(f"Estimated: ~{total * 3} hours (@ ~74 step/s)")
print(f"Start: {datetime.datetime.now():%Y-%m-%d %H:%M:%S}")
print("=" * 60)

for i, (tag, desc, args) in enumerate(experiments):
    print(f"\n[{i+1}/{total}] {tag}: {desc}  {datetime.datetime.now():%H:%M:%S}")
    sys.stdout.flush()
    cmd = [PY, "main.py"] + args
    p = subprocess.Popen(cmd)
    p.wait()
    rc = p.returncode
    status = "OK" if rc == 0 else f"FAILED (exit={rc})"
    print(f"  {status}  {datetime.datetime.now():%H:%M:%S}")

print(f"\n=== Stage B Complete ===")
print(f"End: {datetime.datetime.now():%Y-%m-%d %H:%M:%S}")
