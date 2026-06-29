"""Stage A: Mechanism Verification (100K) — Ensure clustering triggers.

Three experiments on 5m_vs_6m:
  A1: dynamic (clustering_interval=5000)
  A2: all_one (baseline)
  A3: each_alone (baseline)

Gate: After A1, check clustering_logs CSV for update_count > 0.
"""

import subprocess
import os
import sys
import datetime

PY = r"D:\Soft\Anaconda\envs\hygma\python.exe"
SRC = r"D:\Project\paper\代码\HYGMA\src"
os.chdir(SRC)

experiments = [
    ("A1", "5m_vs_6m dynamic (interval=5K)",
     ["--config=hygma", "--env-config=sc2", "with",
      "env_args.map_name=5m_vs_6m", "t_max=100000", "test_interval=10000",
      "seed=1", "grouping_mode=dynamic", "clustering_interval=5000"]),
    ("A2", "5m_vs_6m all_one",
     ["--config=hygma", "--env-config=sc2", "with",
      "env_args.map_name=5m_vs_6m", "t_max=100000", "test_interval=10000",
      "seed=1", "grouping_mode=all_one"]),
    ("A3", "5m_vs_6m each_alone",
     ["--config=hygma", "--env-config=sc2", "with",
      "env_args.map_name=5m_vs_6m", "t_max=100000", "test_interval=10000",
      "seed=1", "grouping_mode=each_alone"]),
]

total = len(experiments)
print(f"=== Stage A: Mechanism Verification (100K steps) ===")
print(f"Queue: {total} experiments on 5m_vs_6m")
print(f"Dynamic runs: clustering_interval=5000 (was 100000)")
print(f"Expected clustering checks: ~{100000//5000} during training")
print(f"Estimated: ~{total * 40} min (@ ~74 step/s)")
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

print(f"\n=== Stage A Complete ===")
print(f"End: {datetime.datetime.now():%Y-%m-%d %H:%M:%S}")
print(f"\nNEXT: Check results/clustering_logs/5m_vs_6m_dynamic_seed1.csv")
print(f"  If update_count > 0 -> proceed to Phase 2 analysis")
print(f"  If update_count == 0 -> investigate, fix, re-run before Phase 2")
