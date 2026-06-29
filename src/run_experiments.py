"""HYGMA Experiment Launcher - runs experiments sequentially."""
import subprocess, sys, os, datetime

SRC = os.path.dirname(os.path.abspath(__file__))
PYTHON = sys.executable

experiments = [
    # Phase A: 3m
    ("A1", "3m dynamic (fixed)", ["--config=hygma", "--env-config=sc2", "with",
        "env_args.map_name=3m", "t_max=100000", "test_interval=5000",
        "seed=1", "grouping_mode=dynamic"]),
    ("A2", "3m all_one", ["--config=hygma", "--env-config=sc2", "with",
        "env_args.map_name=3m", "t_max=100000", "test_interval=5000",
        "seed=1", "grouping_mode=all_one"]),
    ("A4", "3m QMIX baseline", ["--config=qmix", "--env-config=sc2", "with",
        "env_args.map_name=3m", "t_max=100000", "test_interval=5000", "seed=1"]),
    # Phase B: 5m_vs_6m
    ("B1", "5m_vs_6m dynamic", ["--config=hygma", "--env-config=sc2", "with",
        "env_args.map_name=5m_vs_6m", "t_max=100000", "test_interval=5000",
        "seed=1", "grouping_mode=dynamic"]),
    ("B2", "5m_vs_6m all_one", ["--config=hygma", "--env-config=sc2", "with",
        "env_args.map_name=5m_vs_6m", "t_max=100000", "test_interval=5000",
        "seed=1", "grouping_mode=all_one"]),
    ("B3", "5m_vs_6m each_alone", ["--config=hygma", "--env-config=sc2", "with",
        "env_args.map_name=5m_vs_6m", "t_max=100000", "test_interval=5000",
        "seed=1", "grouping_mode=each_alone"]),
    ("B4", "5m_vs_6m QMIX baseline", ["--config=qmix", "--env-config=sc2", "with",
        "env_args.map_name=5m_vs_6m", "t_max=100000", "test_interval=5000", "seed=1"]),
]

total = len(experiments)
print(f"HYGMA Experiment Matrix: {total} experiments")
print(f"Estimated time: ~{total * 40} min\n")

os.chdir(SRC)
for i, (tag, desc, args) in enumerate(experiments):
    print(f"[{i+1}/{total}] {tag}: {desc}  {datetime.datetime.now():%H:%M:%S}")
    cmd = [PYTHON, "main.py"] + args
    p = subprocess.Popen(cmd)
    p.wait()
    rc = p.returncode
    print(f"       Done (exit {rc})  {datetime.datetime.now():%H:%M:%S}")
    if rc != 0:
        print(f"       WARNING: non-zero exit code!")

print(f"\nAll {total} experiments complete!")
print(f"Results in: {SRC}\..\results\sacred\\")
