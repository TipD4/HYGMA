"""Sequential experiment queue — clustering_interval=50000 so clustering actually fires."""
import subprocess, os, sys, datetime

SRC = os.path.dirname(os.path.abspath(__file__))
os.chdir(SRC)
PY = sys.executable

experiments = [
    ("B1", "5m_vs_6m dynamic",
     ["--config=hygma", "--env-config=sc2", "with",
      "env_args.map_name=5m_vs_6m", "t_max=100000", "test_interval=5000",
      "seed=1", "grouping_mode=dynamic", "clustering_interval=50000"]),
    ("B2", "5m_vs_6m all_one",
     ["--config=hygma", "--env-config=sc2", "with",
      "env_args.map_name=5m_vs_6m", "t_max=100000", "test_interval=5000",
      "seed=1", "grouping_mode=all_one"]),
    ("B3", "5m_vs_6m each_alone",
     ["--config=hygma", "--env-config=sc2", "with",
      "env_args.map_name=5m_vs_6m", "t_max=100000", "test_interval=5000",
      "seed=1", "grouping_mode=each_alone"]),
    ("B4", "5m_vs_6m QMIX baseline",
     ["--config=qmix", "--env-config=sc2", "with",
      "env_args.map_name=5m_vs_6m", "t_max=100000", "test_interval=5000", "seed=1"]),
    ("A2", "3m all_one (new instrumented)",
     ["--config=hygma", "--env-config=sc2", "with",
      "env_args.map_name=3m", "t_max=100000", "test_interval=5000",
      "seed=1", "grouping_mode=all_one"]),
    ("A4", "3m QMIX baseline",
     ["--config=qmix", "--env-config=sc2", "with",
      "env_args.map_name=3m", "t_max=100000", "test_interval=5000", "seed=1"]),
]

total = len(experiments)
print(f"Queue: {total} experiments")
print(f"Note: dynamic runs use clustering_interval=50000 (was 100000)")
print(f"  so clustering fires at ~50K and ~100K steps")
print(f"Estimated: ~{total * 40} min")
print(f"Start: {datetime.datetime.now():%H:%M:%S}")
print("-" * 60)

for i, (tag, desc, args) in enumerate(experiments):
    print(f"[{i+1}/{total}] {tag}: {desc}  {datetime.datetime.now():%H:%M:%S}")
    sys.stdout.flush()
    cmd = [PY, "main.py"] + args
    p = subprocess.Popen(cmd)
    p.wait()
    rc = p.returncode
    print(f"  Done (exit={rc})  {datetime.datetime.now():%H:%M:%S}")

print(f"\nAll done!  {datetime.datetime.now():%H:%M:%S}")
