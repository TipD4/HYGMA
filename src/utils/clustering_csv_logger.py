import csv
import json
import os


class ClusteringCSVLogger:
    """
    Crash-safe CSV logger for clustering events.
    Flushes after every row so data survives process termination.

    Path: results/clustering_logs/<map>_<mode>_seed<seed>.csv

    Columns:
        t_env, check_count, update_count, groups_updated,
        num_moved, num_groups, group_sizes, current_groups,
        silhouette_score, n_clusters_chosen, latency_ms,
        rejection_reason, stability_threshold, group_diversity_so_far
    """

    COLUMNS = [
        "t_env",
        "check_count",
        "update_count",
        "groups_updated",
        "num_moved",
        "num_groups",
        "group_sizes",
        "current_groups",
        "silhouette_score",
        "n_clusters_chosen",
        "latency_ms",
        "rejection_reason",
        "stability_threshold",
        "group_diversity_so_far",
    ]

    def __init__(self, log_dir, map_name, mode, seed):
        os.makedirs(log_dir, exist_ok=True)
        filename = f"{map_name}_{mode}_seed{seed}.csv"
        self.filepath = os.path.join(log_dir, filename)
        self.file = open(self.filepath, "w", newline="", encoding="utf-8")
        self.writer = csv.DictWriter(self.file, fieldnames=self.COLUMNS)
        self.writer.writeheader()
        self.file.flush()
        print(f"[ClusteringCSVLogger] Opened: {self.filepath}")

    def log_check(
        self,
        t_env,
        check_count,
        update_count,
        groups_updated,
        num_moved,
        num_groups,
        group_sizes,
        current_groups,
        silhouette_score,
        n_clusters_chosen,
        latency_ms,
        rejection_reason,
        stability_threshold,
        group_diversity_so_far,
    ):
        row = {
            "t_env": t_env,
            "check_count": check_count,
            "update_count": update_count,
            "groups_updated": groups_updated,
            "num_moved": num_moved,
            "num_groups": num_groups,
            "group_sizes": json.dumps(group_sizes),
            "current_groups": json.dumps(current_groups),
            "silhouette_score": silhouette_score,
            "n_clusters_chosen": n_clusters_chosen,
            "latency_ms": round(latency_ms, 3),
            "rejection_reason": rejection_reason,
            "stability_threshold": stability_threshold,
            "group_diversity_so_far": group_diversity_so_far,
        }
        self.writer.writerow(row)
        self.file.flush()

    def close(self):
        if self.file and not self.file.closed:
            self.file.close()
            print(f"[ClusteringCSVLogger] Closed: {self.filepath}")

    def __del__(self):
        self.close()
