import json, os

base = 'd:/Project/paper/代码/HYGMA/results/sacred'
for run_id in sorted(os.listdir(base), key=lambda x: int(x) if x.isdigit() else 0):
    fpath = os.path.join(base, run_id, 'info.json')
    if not os.path.exists(fpath):
        continue
    try:
        json.load(open(fpath))
        print(f"Run {run_id}: OK")
    except Exception as e:
        print(f"Run {run_id}: CORRUPT - {e}")
