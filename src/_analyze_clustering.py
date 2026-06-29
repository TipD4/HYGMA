# HYGMA Clustering Analysis

import csv,json,os,sys,glob

from collections import Counter,defaultdict

import numpy as np

import matplotlib;matplotlib.use("Agg")

import matplotlib.pyplot as plt

from matplotlib.gridspec import GridSpec



CSV_DIR = os.path.join("..", "results", "clustering_logs")

FIG_DIR = os.path.join("..", "results", "_figures")

os.makedirs(FIG_DIR, exist_ok=True)



def load_all_csvs(csv_dir):

    results = {}

    for fp in glob.glob(os.path.join(csv_dir, "*.csv")):

        name = os.path.splitext(os.path.basename(fp))[0]

        rows = []

        with open(fp, "r", encoding="utf-8") as f:

            for row in csv.DictReader(f):

                rows.append(row)

        results[name] = rows

    return results



def compute_stats(rows):

    if not rows:

        return {"error":"no data"}

    stats = {}

    cc = int(rows[-1].get("check_count", 0))

    uc = int(rows[-1].get("update_count", 0))

    stats["check_count"] = cc

    stats["update_count"] = uc

    stats["num_rows"] = len(rows)

    stats["rejection_reasons"] = Counter(r.get("rejection_reason","unknown") for r in rows)

    stats["group_diversity"] = int(rows[-1].get("group_diversity_so_far", 0))

    sil_vals = []

    for r in rows:

        try:

            s = float(r.get("silhouette_score",""))

            if s == s:

                sil_vals.append(s)

        except:

            pass

    stats["silhouette_mean"] = np.mean(sil_vals) if sil_vals else float("nan")

    return stats



def print_verdict(stats):

    print("=" * 60)

    print("DYNAMIC GROUP VERDICT")

    print("=" * 60)

    uc = stats.get("update_count", 0)

    gd = stats.get("group_diversity", 0)

    print("  check_count: {0}".format(stats.get("check_count", 0)))

    print("  update_count: {0}".format(uc))

    print("  group_diversity (unique configs): {0}".format(gd))

    print("  rejection_reasons: {0}".format(dict(stats.get("rejection_reasons", {}))))

    print("  silhouette_mean: {0:.3f}".format(stats.get("silhouette_mean", float("nan"))))

    if uc >= 2 and gd >= 2:

        print("VERDICT: YES - Dynamic groups actually happened.")

        return True

    elif uc >= 1 or gd >= 1:

        print("VERDICT: BARELY - Groups changed but minimally.")

        return True

    else:

        print("VERDICT: NO - Dynamic groups did NOT happen.")

        return False

    print("=" * 60)




def main():
    import os,glob
    print("Loading CSVs from: " + CSV_DIR)
    results = load_all_csvs(CSV_DIR)
    if not results:
        print("No CSV files found.")
        return
    for name, rows in results.items():
        print(chr(10) + chr(45)*50)
        print("Experiment: " + name + " (" + str(len(rows)) + " rows)")
        stats = compute_stats(rows)
        for k,v in stats.items():
            print("  " + str(k) + ": " + str(v))
        print_verdict(stats)

if __name__ == "__main__":
    main()