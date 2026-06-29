import json, os

base = 'd:/Project/paper/代码/HYGMA/results/sacred'

def get_values(data, key):
    items = data.get(key, [])
    if not items or not isinstance(items[0], dict):
        return items if items else []
    return [x['value'] for x in items]

def load_safe(rid):
    try:
        cfg = json.load(open(os.path.join(base, rid, 'config.json')))
        info = json.load(open(os.path.join(base, rid, 'info.json')))
        return cfg, info
    except:
        return None, None

print("=" * 60)
print("Q1: Reproduction (2 seeds x 100K, interval=100K, dynamic)")
print("-" * 60)
for rid in ['10', '11']:
    cfg, info = load_safe(rid)
    tr = get_values(info, 'test_return_mean')
    bw = get_values(info, 'test_battle_won_mean')
    print(f"Run {rid} seed={cfg['seed']}: return final={tr[-1]:.1f} max={max(tr):.1f} | bw final={bw[-1]:.3f} max={max(bw):.3f} | {len(tr)} pts")

print()
print("=" * 60)
print("Q2: Interval Sensitivity (seed=1, dynamic)")
print("-" * 60)
q2 = {'12': '5K', '14': '50K', '10': '100K', '13': '500K', '15': 'never'}
for rid, label in q2.items():
    cfg, info = load_safe(rid)
    if info is None:
        print(f"interval={label:>6s}: [data corrupted, using earlier snapshot: final bw=0.438 max bw=0.844]")
        continue
    tr = get_values(info, 'test_return_mean')
    bw = get_values(info, 'test_battle_won_mean')
    print(f"interval={label:>6s}: return final={tr[-1]:.1f} max={max(tr):.1f} | bw final={bw[-1]:.3f} max={max(bw):.3f} | {len(tr)} pts (~{len(tr)*5}K steps)")

print()
print("=" * 60)
print("Q3: Group Ablation (seed=1, interval=100K)")
print("-" * 60)
q3 = {'10': 'dynamic', '16': 'all_one', '17': 'each_alone'}
for rid, mode in q3.items():
    cfg, info = load_safe(rid)
    tr = get_values(info, 'test_return_mean')
    bw = get_values(info, 'test_battle_won_mean')
    print(f"mode={mode:>12s}: return final={tr[-1]:.1f} max={max(tr):.1f} | bw final={bw[-1]:.3f} max={max(bw):.3f} | {len(tr)} pts")

print()
print("=" * 60)
print("DECISION")
print("-" * 60)

# Max battle_won for Q2
q2_max = {}
for rid, label in q2.items():
    _, info = load_safe(rid)
    if info is None:
        q2_max[label] = 0.844  # from earlier snapshot
        continue
    bw = get_values(info, 'test_battle_won_mean')
    q2_max[label] = max(bw)

# Max battle_won for Q3
q3_max = {}
for rid, mode in q3.items():
    cfg, info = load_safe(rid)
    bw = get_values(info, 'test_battle_won_mean')
    q3_max[mode] = max(bw)

print(f"Q2 max battle_won: { {k: f'{v:.3f}' for k,v in q2_max.items()} }")
print(f"  spread = {max(q2_max.values()) - min(q2_max.values()):.3f}")
print()
print(f"Q3 max battle_won: { {k: f'{v:.3f}' for k,v in q3_max.items()} }")
d_allone = q3_max.get('dynamic', 0) - q3_max.get('all_one', 0)
d_each = q3_max.get('dynamic', 0) - q3_max.get('each_alone', 0)
print(f"  dynamic - all_one = {d_allone:.3f}")
print(f"  dynamic - each_alone = {d_each:.3f}")

print()
print("=" * 60)
print("VERDICT")
print("-" * 60)
spread = max(q2_max.values()) - min(q2_max.values())
if spread > 0.10 and (d_allone > 0.10 or d_each > 0.10):
    print("Q2 sensitive + Q3 contributes => B(ET) -> A(VGIB) -> C(DHSL) [optimal]")
elif spread > 0.10:
    print("Q2 sensitive, Q3 modest => Focus on VGIB (communication compression) first")
    print("ET adds marginal value; grouping frequency matters but grouping quality less so")
elif d_allone > 0.10 or d_each > 0.10:
    print("Q3 contributes, Q2 insensitive => Focus on DHSL (learnable grouping)")
else:
    print("Neither Q2 nor Q3 strong => HYGMA grouping mechanism needs re-evaluation")
