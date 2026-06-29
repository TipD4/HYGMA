"""5m_vs_6m only: dynamic + QMIX, 50K steps each"""
import subprocess, os, sys, datetime

PY = r"D:\Soft\Anaconda\envs\hygma\python.exe"
SRC = r"D:\Project\paper\代码\HYGMA\src"
os.chdir(SRC)

experiments = [
    ("B1", "5m_vs_6m dynamic (interval=25K)",
     ["--config=hygma", "--env-config=sc2", "with",
      "env_args.map_name=5m_vs_6m", "t_max=50000", "test_interval=5000",
      "seed=1", "grouping_mode=dynamic", "clustering_interval=25000"]),
    ("B4", "5m_vs_6m QMIX baseline",
     ["--config=qmix", "--env-config=sc2", "with",
      "env_args.map_name=5m_vs_6m", "t_max=50000", "test_interval=5000", "seed=1"]),
]

print(f"5m_vs_6m only: {len(experiments)} runs, ~{len(experiments)*20} min total")
print(f"Start: {datetime.datetime.now():%H:%M:%S}")
for tag, desc, args in experiments:
    print(f"[{tag}] {desc}  {datetime.datetime.now():%H:%M:%S}")
    sys.stdout.flush()
    p = subprocess.Popen([PY, "main.py"] + args)
    p.wait()
    print(f"  Done (exit={p.returncode})  {datetime.datetime.now():%H:%M:%S}")
print(f"Done! {datetime.datetime.now():%H:%M:%S}")
