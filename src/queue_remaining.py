"""Remaining experiments: B1(retry), B4, A2, A4"""
import subprocess, os, sys, datetime

PY = r"D:\Soft\Anaconda\envs\hygma\python.exe"
SRC = r"D:\Project\paper\代码\HYGMA\src"
os.chdir(SRC)

experiments = [
    ("B1-retry", "5m_vs_6m dynamic (retry)",
     ["--config=hygma", "--env-config=sc2", "with",
      "env_args.map_name=5m_vs_6m", "t_max=100000", "test_interval=5000",
      "seed=1", "grouping_mode=dynamic", "clustering_interval=50000"]),
    ("B4", "5m_vs_6m QMIX baseline",
     ["--config=qmix", "--env-config=sc2", "with",
      "env_args.map_name=5m_vs_6m", "t_max=100000", "test_interval=5000", "seed=1"]),
    ("A2", "3m all_one (instrumented)",
     ["--config=hygma", "--env-config=sc2", "with",
      "env_args.map_name=3m", "t_max=100000", "test_interval=5000",
      "seed=1", "grouping_mode=all_one"]),
    ("A4", "3m QMIX baseline",
     ["--config=qmix", "--env-config=sc2", "with",
      "env_args.map_name=3m", "t_max=100000", "test_interval=5000", "seed=1"]),
]

print(f"Remaining: {len(experiments)} experiments")
print(f"Start: {datetime.datetime.now():%H:%M:%S}")
for i, (tag, desc, args) in enumerate(experiments):
    print(f"[{i+1}/{len(experiments)}] {tag}: {desc}  {datetime.datetime.now():%H:%M:%S}")
    sys.stdout.flush()
    p = subprocess.Popen([PY, "main.py"] + args)
    p.wait()
    rc = p.returncode
    print(f"  Done (exit={rc})  {datetime.datetime.now():%H:%M:%S}")
print(f"\nAll done! {datetime.datetime.now():%H:%M:%S}")
