import json
for run_id in ['12','13','14','15','16','17','10','11']:
    cfg = json.load(open(f'd:/Project/paper/代码/HYGMA/results/sacred/{run_id}/config.json'))
    ci = cfg.get('clustering_interval', 'N/A')
    gm = cfg.get('grouping_mode', 'dynamic')
    seed = cfg.get('seed', 'N/A')
    print(f'Run {run_id}: seed={seed}  interval={ci}  grouping_mode={gm}')
