"""Stage 2 Analysis: 聚类活性统计 + Stage 1/3 结果汇总

从 sacred info.json 中提取：
- 聚类触发次数 (check_count)
- 实际分组更新次数 (update_count)
- 累计 agent 移动次数 (total_moved_cum)
- 每 1000 步统计
- Phase A/B 的 battle_won 对比
"""
import json
import os
import sys

base = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results', 'sacred')


def get_values(data, key):
    items = data.get(key, [])
    if not items:
        return []
    if isinstance(items, list) and isinstance(items[0], dict):
        return [(x['step'], x['value']) for x in items]
    return [(i, v) for i, v in enumerate(items)]


def load_safe(rid):
    try:
        cfg = json.load(open(os.path.join(base, rid, 'config.json')))
        info = json.load(open(os.path.join(base, rid, 'info.json')))
        return cfg, info
    except Exception:
        return None, None


def last_value(data, key):
    items = get_values(data, key)
    return items[-1][1] if items else None


def max_value(data, key):
    items = get_values(data, key)
    vals = [v for _, v in items]
    return max(vals) if vals else None


def print_section(title):
    print()
    print("=" * 70)
    print(title)
    print("-" * 70)


# ============================================================
# Stage 2: 聚类活性报告
# ============================================================
print_section("Stage 2: 聚类活性报告 (Clustering Liveness)")

map_modes = {
    '3m':     {'dynamic': None, 'all_one': '16', 'each_alone': '17'},
    '5m_vs_6m': {'dynamic': None, 'all_one': None, 'each_alone': None},
}

# Find the latest runs for each config
for rid in sorted(os.listdir(base), key=lambda x: int(x) if x.isdigit() else 0):
    cfg, _ = load_safe(rid)
    if cfg is None:
        continue
    map_name = cfg.get('env_args', {}).get('map_name', '')
    mode = cfg.get('grouping_mode', '')
    if map_name in map_modes and mode in map_modes[map_name]:
        map_modes[map_name][mode] = rid

print()
print(f"{'Map':<12s} {'Mode':<12s} {'Run':>4s} {'Check Ct':>8s} {'Update Ct':>9s} "
      f"{'Total Moved':>11s} {'Steps':>8s} {'Per 1K Chk':>10s} {'Per 1K Upd':>10s}")
print("-" * 90)

for map_name, modes in map_modes.items():
    for mode, rid in modes.items():
        if rid is None:
            continue
        cfg, info = load_safe(rid)
        if info is None:
            print(f"{map_name:<12s} {mode:<12s} {rid:>4s} [data not available]")
            continue

        check_ct = last_value(info, 'clustering_check_count') or 0
        update_ct = last_value(info, 'clustering_update_count') or 0
        total_moved = last_value(info, 'clustering_total_moved_cum') or 0
        t_max = cfg.get('t_max', 0)
        steps_k = t_max / 1000 if t_max > 0 else 0

        per_k_check = check_ct / steps_k if steps_k > 0 else 0
        per_k_update = update_ct / steps_k if steps_k > 0 else 0

        print(f"{map_name:<12s} {mode:<12s} {rid:>4s} {check_ct:>8d} {update_ct:>9d} "
              f"{total_moved:>11d} {t_max:>8d} {per_k_check:>10.2f} {per_k_update:>10.2f}")


# ============================================================
# Stage 1 & 3: Battle Won 对比
# ============================================================
print_section("Stage 1 & 3: Battle Won 对比")

# Map the known runs
known_runs = {
    # 3m (from previous experiments + new runs)
    '3m_dynamic': None,
    '3m_all_one': '16',
    '3m_each_alone': '17',
    '3m_qmix': None,
    # 5m_vs_6m
    '5m_dynamic': None,
    '5m_all_one': None,
    '5m_each_alone': None,
    '5m_qmix': None,
}

# Scan for matching runs
for rid in sorted(os.listdir(base), key=lambda x: int(x) if x.isdigit() else 0):
    cfg, _ = load_safe(rid)
    if cfg is None:
        continue
    map_name = cfg.get('env_args', {}).get('map_name', '')
    mode = cfg.get('grouping_mode', 'dynamic')
    alg = cfg.get('name', '')

    if map_name == '3m' and alg == 'hygma':
        key = f'3m_{mode}'
        if known_runs.get(key) is None:
            known_runs[key] = rid
    elif map_name == '3m' and alg == 'qmix':
        if known_runs.get('3m_qmix') is None:
            known_runs['3m_qmix'] = rid
    elif map_name == '5m_vs_6m' and alg == 'hygma':
        key = f'5m_{mode}'
        if known_runs.get(key) is None:
            known_runs[key] = rid
    elif map_name == '5m_vs_6m' and alg == 'qmix':
        if known_runs.get('5m_qmix') is None:
            known_runs['5m_qmix'] = rid

print()
print(f"{'Config':<20s} {'Run':>4s} {'BW Max':>7s} {'BW Final':>9s} {'Return Max':>11s} {'Return Final':>13s} {'Pts':>4s}")
print("-" * 75)

for name, rid in sorted(known_runs.items()):
    if rid is None:
        print(f"{name:<20s} {'--':>4s} {'pending':>7s}")
        continue
    cfg, info = load_safe(rid)
    if info is None:
        print(f"{name:<20s} {rid:>4s} [corrupted]")
        continue

    bw_max = max_value(info, 'test_battle_won_mean')
    bw_items = get_values(info, 'test_battle_won_mean')
    bw_final = bw_items[-1][1] if bw_items else None
    ret_max = max_value(info, 'test_return_mean')
    ret_items = get_values(info, 'test_return_mean')
    ret_final = ret_items[-1][1] if ret_items else None
    n_pts = len(bw_items)

    print(f"{name:<20s} {rid:>4s} "
          f"{bw_max:>6.1%} " if bw_max is not None else f"{name:<20s} {rid:>4s} {'N/A':>7s}",
          end="")
    if bw_max is not None:
        print(f"{bw_max:>7.1%} " if bw_max <= 1 else f"{bw_max:>7.3f} ", end="")
        print(f"{bw_final:>7.1%} " if bw_final is not None and bw_final <= 1 else f"{bw_final:>7.3f} " if bw_final is not None else "  N/A   ", end="")
        print(f"{ret_max:>11.1f} {ret_final:>11.1f} " if ret_final is not None else f"  N/A   ", end="")
        print(f"{n_pts:>4d}")
    else:
        print()


# ============================================================
# Stage 3: 增益拆解
# ============================================================
print_section("Stage 3: 增益拆解 (Gain Decomposition)")

for map_name in ['3m', '5m']:
    qmix_key = f'{map_name}_qmix'
    allone_key = f'{map_name}_all_one'
    dynamic_key = f'{map_name}_dynamic'

    qmix_rid = known_runs.get(qmix_key)
    allone_rid = known_runs.get(allone_key)
    dynamic_rid = known_runs.get(dynamic_key)

    if not all([qmix_rid, allone_rid, dynamic_rid]):
        print(f"\n{map_name}: 数据不完整，跳过")
        continue

    qmix_bw = max_value(*[load_safe(qmix_rid)])[1] if load_safe(qmix_rid)[1] else None
    # Actually let me just load them properly
    _, qmix_info = load_safe(qmix_rid)
    _, allone_info = load_safe(allone_rid)
    _, dynamic_info = load_safe(dynamic_rid)

    qmix_bw = max_value(qmix_info, 'test_battle_won_mean') if qmix_info else None
    allone_bw = max_value(allone_info, 'test_battle_won_mean') if allone_info else None
    dynamic_bw = max_value(dynamic_info, 'test_battle_won_mean') if dynamic_info else None

    if qmix_bw is None or allone_bw is None or dynamic_bw is None:
        print(f"\n{map_name}: 数据不完整，跳过")
        continue

    hgcn_gain = allone_bw - qmix_bw
    group_gain = dynamic_bw - allone_bw

    print(f"\n{map_name}:")
    print(f"  QMIX baseline:          {qmix_bw:>6.1%}")
    print(f"  HYGMA + all_one:        {allone_bw:>6.1%}  (+{hgcn_gain:+.1%} HGCN)")
    print(f"  HYGMA + dynamic:        {dynamic_bw:>6.1%}  (+{group_gain:+.1%} grouping)")
    print(f"  QMIX → all_one 增益:    {hgcn_gain:>+.1%}")
    print(f"  all_one → dynamic 增益: {group_gain:>+.1%}")

    if hgcn_gain > 0.05 and group_gain <= 0.02:
        print(f"  → 结论: HGCN attention 是主要贡献，动态分组贡献有限")
    elif group_gain > 0.05:
        print(f"  → 结论: 动态分组有显著正向贡献")
    elif hgcn_gain <= 0.02:
        print(f"  → 结论: HGCN 贡献有限，需重新评估")


# ============================================================
# Stage 4: 路线判定
# ============================================================
print_section("Stage 4: 路线判定 (Research Direction)")

# Collect all available results
results = {}
for map_name in ['3m', '5m']:
    results[map_name] = {}
    for mode in ['dynamic', 'all_one', 'each_alone', 'qmix']:
        key = f'{map_name}_{mode}'
        rid = known_runs.get(key)
        if rid:
            _, info = load_safe(rid)
            if info:
                results[map_name][mode] = max_value(info, 'test_battle_won_mean')

# Decision logic
print()
for map_name in ['3m', '5m']:
    r = results.get(map_name, {})
    if 'dynamic' not in r or 'all_one' not in r:
        print(f"{map_name}: 数据不完整，无法判定")
        continue
    d = r['dynamic']
    a = r['all_one']
    e = r.get('each_alone')
    q = r.get('qmix')

    print(f"{map_name}: all_one={a:.1%}, dynamic={d:.1%}", end="")
    if e is not None:
        print(f", each_alone={e:.1%}", end="")
    if q is not None:
        print(f", QMIX={q:.1%}", end="")
    print()

    if d <= a + 0.02:  # dynamic not clearly better than all_one (allow 2% noise)
        print(f"  → dynamic ≤ all_one: 动态分组无显著优势")
    else:
        print(f"  → dynamic > all_one: 动态分组有正向贡献 (+{d-a:.1%})")

print()
print("综合判定:")
# Check both maps
if '3m' in results and '5m' in results:
    d3 = results['3m'].get('dynamic', 0)
    a3 = results['3m'].get('all_one', 0)
    d5 = results['5m'].get('dynamic', 0)
    a5 = results['5m'].get('all_one', 0)

    both_allone_win = (d3 <= a3 + 0.02) and (d5 <= a5 + 0.02)
    large_only = (d3 <= a3 + 0.02) and (d5 > a5 + 0.02)

    if both_allone_win:
        print("→ 两个地图上 dynamic ≤ all_one: 优先 VGIB (通信压缩)")
        print("→ 降低 ET/DHSL 优先级")
    elif large_only:
        print("→ 大规模地图 dynamic > all_one: VGIB + ET 并重")
        print("→ 恢复 ET/DHSL 方向")
    else:
        print("→ 结果不一致，需更多实验确认")

print()
print("=" * 70)
print("分析完成")
