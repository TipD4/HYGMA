import json, os

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results', 'sacred')

def load_info(rid):
    try:
        cfg = json.load(open(os.path.join(BASE, rid, 'config.json')))
        info = json.load(open(os.path.join(BASE, rid, 'info.json')))
        return cfg, info
    except:
        return None, None

def vals(key, info):
    items = info.get(key, [])
    if not items:
        return []
    if isinstance(items[0], dict):
        return [x['value'] for x in items]
    return items

def last_val(key, info):
    v = vals(key, info)
    return v[-1] if v else None

def max_val(key, info):
    v = vals(key, info)
    return max(v) if v else None

# Scan runs
all_runs = []
for rid in sorted(os.listdir(BASE), key=lambda x: int(x) if x.isdigit() else 0):
    cfg, info = load_info(rid)
    if cfg is None or info is None:
        continue
    all_runs.append((rid, cfg, info))

print("HYGMA Core Mechanism Verification")
print("=" * 70)
print(f"Runs analyzed: {len(all_runs)}")

# Stage 2: Clustering Liveness
print("\n" + "=" * 70)
print("Stage 2: Clustering Liveness (dynamic mode only)")
print("-" * 70)

for rid, cfg, info in all_runs:
    mode = cfg.get('grouping_mode', '')
    if mode != 'dynamic':
        continue
    m = cfg['env_args']['map_name']
    t = cfg.get('t_max', 0)
    cc = last_val('clustering_check_count', info) or 0
    uc = last_val('clustering_update_count', info) or 0
    tm = last_val('clustering_total_moved_cum', info) or 0
    ng = last_val('clustering_num_groups', info) or 0
    n_pts = len(vals('test_battle_won_mean', info))
    pk_check = cc / (t/1000) if t > 0 else 0
    pk_upd = uc / (t/1000) if t > 0 else 0
    status = "COMPLETE" if n_pts >= (t // 5000) else f"IN PROGRESS ({n_pts}/{(t//5000)} pts)"
    
    print(f"Run {rid}: {m} s={cfg.get('seed','?')} t={t} [{status}]")
    print(f"  checks={cc} ({pk_check:.1f}/1K), updates={uc} ({pk_upd:.1f}/1K)")
    print(f"  total_moved={tm}, final_groups={ng}")
    if cc == 0 and status == "COMPLETE":
        print(f"  ** BUG CONFIRMED: clustering never triggered (training_steps bug) **")

# Stage 1: Battle Won
print("\n" + "=" * 70)
print("Stage 1: Battle Won Comparison")
print("-" * 70)

results = {}
for rid, cfg, info in all_runs:
    m = cfg['env_args']['map_name']
    mode = cfg.get('grouping_mode', cfg.get('name', '?'))
    bw = max_val('test_battle_won_mean', info)
    ret = max_val('test_return_mean', info)
    n_pts = len(vals('test_battle_won_mean', info))
    label = f"{m}_{mode}"
    if label not in results or n_pts > results[label]['n_pts']:
        results[label] = {'rid': rid, 'bw_max': bw, 'ret_max': ret, 'n_pts': n_pts}

print(f"{'Config':<25s} {'Run':>4s} {'BW Max':>8s} {'Ret Max':>10s} {'Pts':>4s}")
print("-" * 55)
for label in sorted(results.keys()):
    r = results[label]
    bws = f"{r['bw_max']:.1%}" if r['bw_max'] and r['bw_max'] <= 1 else f"{r['bw_max']:.3f}" if r['bw_max'] else "N/A"
    print(f"{label:<25s} {r['rid']:>4s} {bws:>8s} {r["ret_max"] if r["ret_max"] else "N/A"} {r['n_pts']:>4d}")

# Stage 3: Gain Decomposition
print("\n" + "=" * 70)
print("Stage 3: Gain Decomposition")
print("-" * 70)

for m in ['3m', '5m']:
    qmix = results.get(f'{m}_qmix', {})
    all1 = results.get(f'{m}_all_one', {})
    dyna = results.get(f'{m}_dynamic', {})
    if not qmix or not all1:
        print(f"{m}: incomplete (missing QMIX or all_one)")
        continue
    hgcn_gain = (all1.get('bw_max', 0) or 0) - (qmix.get('bw_max', 0) or 0)
    grp_gain = (dyna.get('bw_max', 0) or 0) - (all1.get('bw_max', 0) or 0) if dyna else 0
    print(f"{m}: QMIX={qmix.get('bw_max',0):.1%} +HGCN={hgcn_gain:+.1%} =all_one={all1.get('bw_max',0):.1%}")
    if dyna:
        print(f"    all_one={all1.get('bw_max',0):.1%} +grouping={grp_gain:+.1%} =dynamic={dyna.get('bw_max',0):.1%}")
    print(f"    Primary contributor: {'HGCN' if hgcn_gain > abs(grp_gain)*2 else 'Both' if abs(grp_gain) > 0.02 else 'HGCN only'}")

print("\nDone.")
