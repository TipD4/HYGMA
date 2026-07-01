#!/usr/bin/env python3
"""Analyze ablation experiment results from Sacred runs."""
import os, json, sys
from collections import defaultdict
import math

SACRED_DIR = os.path.join("..", "results", "sacred")

def load_run(run_id):
    d = os.path.join(SACRED_DIR, str(run_id))
    cfg = json.load(open(os.path.join(d, "config.json"), encoding="utf-8"))
    info = json.load(open(os.path.join(d, "info.json"), encoding="utf-8"))
    return cfg, info

def classify(cfg):
    name = cfg.get("name", "")
    gm = cfg.get("grouping_mode", "")
    lr = cfg.get("learner", "")
    mp = cfg.get("env_args", {}).get("map_name", "")
    if name == "qmix":
        return "QMIX"
    if name == "ablation_qmix_hgcn":
        return "QMIX+HGCN"
    if name == "hygma" and gm == "each_alone":
        return "HYGMA-each_alone"
    if name == "hygma" and gm == "all_one":
        return "HYGMA-all_one"
    if name == "hygma" and gm == "dynamic":
        return "HYGMA-dynamic"
    if name == "hygma" and gm == "random":
        return "HYGMA-random"
    return f"{name}_{gm}"

def get_final(vals, n=10):
    if not vals:
        return 0, 0
    recent = vals[-n:]
    return sum(v["value"] for v in recent) / len(recent), vals[-1]["value"]

def main():
    results = defaultdict(list)
    for rid in sorted(os.listdir(SACRED_DIR)):
        if not rid.isdigit():
            continue
        try:
            cfg, info = load_run(rid)
        except Exception:
            continue
        label = classify(cfg)
        seed = cfg.get("seed", "?")
        tr = info.get("test_return_mean", [])
        bw = info.get("test_battle_won_mean", [])
        if not tr:
            continue
        avg, final = get_final(tr)
        bw_avg, bw_final = get_final(bw)
        results[label].append({
            "seed": seed,
            "run_id": rid,
            "final_return": final,
            "avg_return_10": avg,
            "final_win_rate": bw_final,
            "avg_win_rate_10": bw_avg,
        })

    print("\\n=== Ablation Results Table ===")
    print(f"{'Model':<22} {'Seeds':<8} {'Return(mean+std)':<20} {'WinRate(mean+std)':<20}")
    print("-" * 70)
    for label in ["QMIX", "QMIX+HGCN", "HYGMA-each_alone", "HYGMA-all_one",
                   "HYGMA-dynamic", "HYGMA-random"]:
        items = results.get(label, [])
        if not items:
            continue
        seeds = len(items)
        returns = [it["final_return"] for it in items]
        win_rates = [it["final_win_rate"] for it in items]
        r_mean = sum(returns) / len(returns)
        r_std = math.sqrt(sum((x - r_mean)**2 for x in returns) / len(returns))
        w_mean = sum(win_rates) / len(win_rates) if win_rates[0] else 0
        w_std = math.sqrt(sum((x - w_mean)**2 for x in win_rates) / len(win_rates)) if win_rates[0] else 0
        print(f"{label:<22} {seeds:<8} {r_mean:>8.2f}+-{r_std:<8.2f} {w_mean:>8.4f}+-{w_std:<8.4f}")
    print()

    # Decision logic
    qm = results.get("QMIX", [])
    qh = results.get("QMIX+HGCN", [])
    ea = results.get("HYGMA-each_alone", [])
    ao = results.get("HYGMA-all_one", [])
    dy = results.get("HYGMA-dynamic", [])
    rd = results.get("HYGMA-random", [])

    qm_ret = sum(r["final_return"] for r in qm) / len(qm) if qm else 0
    qh_ret = sum(r["final_return"] for r in qh) / len(qh) if qh else 0
    ea_ret = sum(r["final_return"] for r in ea) / len(ea) if ea else 0
    ao_ret = sum(r["final_return"] for r in ao) / len(ao) if ao else 0
    dy_ret = sum(r["final_return"] for r in dy) / len(dy) if dy else 0
    rd_ret = sum(r["final_return"] for r in rd) / len(rd) if rd else 0

    print("\\n=== Mechanism Attribution Decision ===")
    hgcn_diff = qh_ret - qm_ret
    grouping_diff = (ao_ret - ea_ret) if ao and ea else 0
    dynamic_vs_each = (dy_ret - ea_ret) if dy else 0

    print(f"QMIX+HGCN vs QMIX delta: {hgcn_diff:+.2f}")
    print(f"all_one vs each_alone delta: {grouping_diff:+.2f}")
    if dy:
        print(f"dynamic vs each_alone delta: {dynamic_vs_each:+.2f}")
    if rd:
        print(f"random vs dynamic delta: {(rd_ret - dy_ret):+.2f}" if dy else f"random return: {rd_ret:.2f}")

    print()
    if hgcn_diff >= -1 and (ao_ret if ao else 0) < (ea_ret if ea else 0) - 2:
        print("Case 1: HGCN beneficial, grouping harmful -> CONDITIONAL (rework)")
    elif hgcn_diff < -1 and ea_ret >= qm_ret - 1:
        print("Case 2: HGCN harms performance -> REMOVE communication module")
    elif abs(hgcn_diff) <= 1 and (ao_ret if ao else 0) < (ea_ret if ea else 0) - 2:
        print("Case 3: HGCN neutral, grouping harmful -> CONDITIONAL (strip to lightweight)")
    else:
        print("INCONCLUSIVE: more seeds needed")


if __name__ == "__main__":
    main()
