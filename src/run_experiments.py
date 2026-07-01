#!/usr/bin/env python3
"""HYGMA mechanism-first experiment launcher.

This launcher runs the current prioritized experiment batch:
1. 3m dynamic sanity runs to verify clustering actually happens.
2. 5m_vs_6m dynamic probe runs to verify grouping changes at scale.
3. 5m_vs_6m baseline comparisons (all_one / each_alone / qmix).

Logs are written under results/launcher_logs/<timestamp>/.
"""

from __future__ import annotations

import datetime
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(__file__).resolve().parent
DEFAULT_PYTHON = Path("D:/Soft/Anaconda/envs/hygma/python.exe")
TEST_INTERVAL = 5000
ATTENTION_RECORD_INTERVAL = 5000


def choose_python() -> str:
    override = os.environ.get("HYGMA_PYTHON")
    if override and Path(override).exists():
        return override
    if DEFAULT_PYTHON.exists():
        return str(DEFAULT_PYTHON)
    return sys.executable


def hygma_spec(
    tag: str,
    desc: str,
    map_name: str,
    t_max: int,
    seed: int,
    grouping_mode: str,
    clustering_interval: int,
    probe_mode: bool,
    probe_steps: int,
    probe_checks: int,
    probe_updates: int,
):
    args = [
        "--config=hygma",
        "--env-config=sc2",
        "with",
        f"env_args.map_name={map_name}",
        f"t_max={t_max}",
        f"test_interval={TEST_INTERVAL}",
        f"attention_record_interval={ATTENTION_RECORD_INTERVAL}",
        f"seed={seed}",
        f"grouping_mode={grouping_mode}",
        f"clustering_interval={clustering_interval}",
        f"clustering_probe_mode={'on' if probe_mode else 'off'}",
        f"clustering_min_steps={probe_steps}",
        f"clustering_min_checks={probe_checks}",
        f"clustering_min_updates={probe_updates}",
    ]
    return {"tag": tag, "desc": desc, "args": args}


def qmix_spec(tag: str, desc: str, map_name: str, t_max: int, seed: int):
    args = [
        "--config=qmix",
        "--env-config=sc2",
        "with",
        f"env_args.map_name={map_name}",
        f"t_max={t_max}",
        f"test_interval={TEST_INTERVAL}",
        f"seed={seed}",
    ]
    return {"tag": tag, "desc": desc, "args": args}


def qmix_hgcn_spec(tag, desc, map_name, t_max, seed, grouping_mode="each_alone"):
    args = [
        "--config=ablation_qmix_hgcn",
        "--env-config=sc2",
        "with",
        f"env_args.map_name={map_name}",
        f"t_max={t_max}",
        f"test_interval={TEST_INTERVAL}",
        f"seed={seed}",
        f"grouping_mode={grouping_mode}",
    ]
    return {"tag": tag, "desc": desc, "args": args}


def random_group_spec(tag, desc, map_name, t_max, seed):
    args = [
        "--config=hygma",
        "--env-config=sc2",
        "with",
        f"env_args.map_name={map_name}",
        f"t_max={t_max}",
        f"test_interval={TEST_INTERVAL}",
        f"seed={seed}",
        "grouping_mode=random",
        "learner=q_learner",
        "clustering_interval=5000",
        "clustering_probe_mode=off",
    ]
    return {"tag": tag, "desc": desc, "args": args}


def build_ablation_experiments():
    return [
        qmix_hgcn_spec("A1-1", "5m_vs_6m qmix+hgcn s1", "5m_vs_6m", 500000, 1),
        qmix_hgcn_spec("A1-2", "5m_vs_6m qmix+hgcn s2", "5m_vs_6m", 500000, 2),
        qmix_hgcn_spec("A1-3", "5m_vs_6m qmix+hgcn s3", "5m_vs_6m", 500000, 3),
        random_group_spec("B1-1", "5m_vs_6m random_group s1", "5m_vs_6m", 500000, 1),
        qmix_spec("C1a-2", "5m_vs_6m qmix s2", "5m_vs_6m", 500000, 2),
        qmix_spec("C1a-3", "5m_vs_6m qmix s3", "5m_vs_6m", 500000, 3),
        hygma_spec("C1b-2", "5m_vs_6m each_alone s2", "5m_vs_6m", 500000, 2,
                   grouping_mode="each_alone", clustering_interval=5000,
                   probe_mode=False, probe_steps=0, probe_checks=0, probe_updates=0),
        hygma_spec("C1b-3", "5m_vs_6m each_alone s3", "5m_vs_6m", 500000, 3,
                   grouping_mode="each_alone", clustering_interval=5000,
                   probe_mode=False, probe_steps=0, probe_checks=0, probe_updates=0),
    ]


def build_experiments():
    return [
        hygma_spec(
            tag="M1",
            desc="3m dynamic sanity seed1",
            map_name="3m",
            t_max=100000,
            seed=1,
            grouping_mode="dynamic",
            clustering_interval=5000,
            probe_mode=True,
            probe_steps=100000,
            probe_checks=20,
            probe_updates=1,
        ),
        hygma_spec(
            tag="M2",
            desc="3m dynamic sanity seed2",
            map_name="3m",
            t_max=100000,
            seed=2,
            grouping_mode="dynamic",
            clustering_interval=5000,
            probe_mode=True,
            probe_steps=100000,
            probe_checks=20,
            probe_updates=1,
        ),
        hygma_spec(
            tag="N1",
            desc="5m_vs_6m dynamic mechanism seed1",
            map_name="5m_vs_6m",
            t_max=500000,
            seed=1,
            grouping_mode="dynamic",
            clustering_interval=5000,
            probe_mode=True,
            probe_steps=500000,
            probe_checks=100,
            probe_updates=1,
        ),
        hygma_spec(
            tag="N2",
            desc="5m_vs_6m dynamic mechanism seed2",
            map_name="5m_vs_6m",
            t_max=500000,
            seed=2,
            grouping_mode="dynamic",
            clustering_interval=5000,
            probe_mode=True,
            probe_steps=500000,
            probe_checks=100,
            probe_updates=1,
        ),
        hygma_spec(
            tag="N3",
            desc="5m_vs_6m dynamic mechanism seed3",
            map_name="5m_vs_6m",
            t_max=500000,
            seed=3,
            grouping_mode="dynamic",
            clustering_interval=5000,
            probe_mode=True,
            probe_steps=500000,
            probe_checks=100,
            probe_updates=1,
        ),
        hygma_spec(
            tag="B1",
            desc="5m_vs_6m all_one baseline seed1",
            map_name="5m_vs_6m",
            t_max=500000,
            seed=1,
            grouping_mode="all_one",
            clustering_interval=5000,
            probe_mode=False,
            probe_steps=0,
            probe_checks=0,
            probe_updates=0,
        ),
        hygma_spec(
            tag="B2",
            desc="5m_vs_6m each_alone baseline seed1",
            map_name="5m_vs_6m",
            t_max=500000,
            seed=1,
            grouping_mode="each_alone",
            clustering_interval=5000,
            probe_mode=False,
            probe_steps=0,
            probe_checks=0,
            probe_updates=0,
        ),
        qmix_spec(
            tag="B3",
            desc="5m_vs_6m qmix baseline seed1",
            map_name="5m_vs_6m",
            t_max=500000,
            seed=1,
        ),
    ]


def write_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def append_jsonl(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def run_one(python_exe: str, exp: dict, run_dir: Path):
    start = datetime.datetime.now()
    log_path = run_dir / f"{exp['tag']}.log"
    cmd = [python_exe, "main.py"] + exp["args"]

    print(f"[{start:%Y-%m-%d %H:%M:%S}] START {exp['tag']}: {exp['desc']}")
    print("COMMAND:", " ".join(cmd))

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    with log_path.open("w", encoding="utf-8", buffering=1) as log_file:
        log_file.write(f"START {start.isoformat()}\n")
        log_file.write("COMMAND: " + " ".join(cmd) + "\n\n")
        process = subprocess.Popen(
            cmd,
            cwd=str(SRC),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=env,
        )

        assert process.stdout is not None
        for line in process.stdout:
            print(line, end="")
            log_file.write(line)

        return_code = process.wait()

    end = datetime.datetime.now()
    duration = end - start
    print(f"[{end:%Y-%m-%d %H:%M:%S}] END {exp['tag']} exit={return_code} duration={duration}")

    return {
        "tag": exp["tag"],
        "desc": exp["desc"],
        "return_code": return_code,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "duration_seconds": int(duration.total_seconds()),
        "log_path": str(log_path),
        "command": cmd,
    }


def main():
    python_exe = choose_python()
    if "--ablation" in sys.argv:
        experiments = build_ablation_experiments()
        batch_name = "ablation_batch"
    else:
        experiments = build_experiments()
        batch_name = "mechanism_batch"
    stamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    run_dir = ROOT / "results" / "launcher_logs" / f"{batch_name}_{stamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "created_at": datetime.datetime.now().isoformat(),
        "python_executable": python_exe,
        "root": str(ROOT),
        "src": str(SRC),
        "run_dir": str(run_dir),
        "experiments": experiments,
    }
    write_json(run_dir / "manifest.json", manifest)

    print(f"HYGMA mechanism-first batch: {len(experiments)} experiments")
    print(f"Python: {python_exe}")
    print(f"Logs:   {run_dir}")
    print()

    summary = []
    failed = []
    for idx, exp in enumerate(experiments, start=1):
        print(f"=== [{idx}/{len(experiments)}] {exp['tag']} {exp['desc']} ===")
        result = run_one(python_exe, exp, run_dir)
        summary.append(result)
        append_jsonl(run_dir / "summary.jsonl", result)
        if result["return_code"] != 0:
            failed.append(result["tag"])
        print()

    final_payload = {
        "finished_at": datetime.datetime.now().isoformat(),
        "failed_tags": failed,
        "ok": len(failed) == 0,
        "summary": summary,
    }
    write_json(run_dir / "final_summary.json", final_payload)

    print("Batch complete.")
    print(f"Summary: {run_dir / 'final_summary.json'}")
    if failed:
        print("Failed experiments:", ", ".join(failed))
    else:
        print("All experiments exited with code 0.")


if __name__ == "__main__":
    main()
