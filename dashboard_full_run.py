"""
Background full-run worker for the Streamlit dashboard.

Run with:
    python dashboard_full_run.py --config lab_out_dashboard/runs/<run_id>/config.json
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from copy import deepcopy
from datetime import datetime
import json
import multiprocessing as mp
import os
from pathlib import Path
import random
import sys
import time
import traceback
from typing import Any

import numpy as np
import pandas as pd

import horde_mode
import loadouts
import playstyles
from rules_config import RulesConfig
import tournament_vec
from vectorized_combat import run_matchup_vec


TERMINAL_STATUSES = {"complete", "failed", "cancelled"}


class CancelRequested(Exception):
    pass


class ProgressReporter:
    def __init__(self, run_dir: Path):
        self.run_dir = run_dir
        self.progress_path = run_dir / "progress.json"
        self.cancel_path = run_dir / "cancel.request"
        self.started = time.time()
        self.pid = None

    def cancel_requested(self) -> bool:
        return self.cancel_path.exists()

    def check_cancelled(self, phase: str, completed: int, total: int) -> None:
        if self.cancel_requested():
            self.write(status="cancelled", phase=phase, completed=completed, total=total)
            raise CancelRequested()

    def write(
        self,
        *,
        status: str = "running",
        phase: str,
        completed: int,
        total: int,
        current_label: str = "",
        matchups_completed: int = 0,
        battles_completed: int = 0,
        error: str = "",
        artifacts: dict[str, str] | None = None,
    ) -> None:
        elapsed = max(0.001, time.time() - self.started)
        done_ratio = completed / total if total else 0.0
        eta = elapsed / done_ratio - elapsed if done_ratio > 0 and status not in TERMINAL_STATUSES else 0.0
        payload = {
            "status": status,
            "phase": phase,
            "completed": int(completed),
            "total": int(total),
            "elapsed_sec": round(elapsed, 2),
            "eta_sec": round(max(0.0, eta), 2),
            "matchups_per_sec": round(matchups_completed / elapsed, 2) if matchups_completed else 0.0,
            "battles_per_sec": round(battles_completed / elapsed, 2) if battles_completed else 0.0,
            "current_label": current_label,
            "last_update": datetime.now().isoformat(timespec="seconds"),
            "error": error,
            "pid": self.pid,
            "artifacts": artifacts or {},
        }
        tmp = self.progress_path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        tmp.replace(self.progress_path)


def log(message: str) -> None:
    print(f"[{datetime.now().isoformat(timespec='seconds')}] {message}", flush=True)


def load_config(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    required = {"run_id", "run_type", "rules_path", "output_dir", "storage_format"}
    missing = required - set(data)
    if missing:
        raise ValueError(f"Missing config keys: {sorted(missing)}")
    if data["storage_format"] != "parquet":
        raise ValueError("dashboard_full_run only supports storage_format='parquet'")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def matchup_record(ld_a, ld_b, result: dict[str, Any]) -> dict[str, Any]:
    a_pursuits = getattr(ld_a, "pursuits", frozenset())
    b_pursuits = getattr(ld_b, "pursuits", frozenset())
    return {
        "a_name": ld_a.name,
        "b_name": ld_b.name,
        "a_wins": int(result["a_wins"]),
        "b_wins": int(result["b_wins"]),
        "mut_wipe": int(result["mut_wipe"]),
        "indecisive": int(result["indecisive"]),
        "avg_skirm": float(result["avg_skirm"]),
        "avg_a_rem": float(result["avg_a_rem"]),
        "avg_b_rem": float(result["avg_b_rem"]),
        "avg_a_killed_combat": float(result["avg_a_killed_combat"]),
        "avg_a_killed_shake": float(result["avg_a_killed_shake"]),
        "avg_a_killed_rout": float(result["avg_a_killed_rout"]),
        "avg_b_killed_combat": float(result["avg_b_killed_combat"]),
        "avg_b_killed_shake": float(result["avg_b_killed_shake"]),
        "avg_b_killed_rout": float(result["avg_b_killed_rout"]),
        "a_wipe_combat": int(result["a_wipe_combat"]),
        "a_wipe_shake": int(result["a_wipe_shake"]),
        "a_wipe_rout": int(result["a_wipe_rout"]),
        "b_wipe_combat": int(result["b_wipe_combat"]),
        "b_wipe_shake": int(result["b_wipe_shake"]),
        "b_wipe_rout": int(result["b_wipe_rout"]),
        "a_shield_destroyed_rate": float(result.get("a_shield_destroyed_rate", 0.0)),
        "b_shield_destroyed_rate": float(result.get("b_shield_destroyed_rate", 0.0)),
        "a_retinue": ld_a.retinue,
        "a_weapon": ld_a.weapon or "",
        "a_shield": ld_a.shield or "",
        "a_armor": ld_a.armor,
        "a_ranged": ld_a.ranged or "",
        "a_tiltyard": bool(ld_a.has_tiltyard),
        "a_size": int(ld_a.size),
        "a_tags": ",".join(ld_a.extra_tags),
        "a_playstyle": ld_a.playstyle or "Random",
        "b_retinue": ld_b.retinue,
        "b_weapon": ld_b.weapon or "",
        "b_shield": ld_b.shield or "",
        "b_armor": ld_b.armor,
        "b_ranged": ld_b.ranged or "",
        "b_tiltyard": bool(ld_b.has_tiltyard),
        "b_size": int(ld_b.size),
        "b_tags": ",".join(ld_b.extra_tags),
        "b_playstyle": ld_b.playstyle or "Random",
        "a_military_pursuit_count": int(getattr(ld_a, "military_pursuit_count", 0)),
        "a_domain_count": int(getattr(ld_a, "domain_count", 0)),
        "a_pursuits": "|".join(sorted(a_pursuits)),
        "b_military_pursuit_count": int(getattr(ld_b, "military_pursuit_count", 0)),
        "b_domain_count": int(getattr(ld_b, "domain_count", 0)),
        "b_pursuits": "|".join(sorted(b_pursuits)),
    }


def summary_frame(summary: dict[str, dict[str, Any]], n_runs: int) -> pd.DataFrame:
    rows = []
    for name, item in summary.items():
        ld = item["loadout"]
        n_battles = max(1, int(item["n_battles"]))
        wins = int(item["wins"])
        losses = int(item["losses"])
        mut_wipe = int(item["mut_wipe"])
        indecisive = int(item["indecisive"])
        decisive_total = wins + losses
        n_opps = (n_battles // n_runs) or 1
        avg_self_rem = float(item["rem_self"]) / n_opps
        avg_opp_rem = float(item["rem_opp"]) / n_opps
        army_upkeep = int(ld.upkeep_per_retinue) * int(ld.size)
        pursuits = getattr(ld, "pursuits", frozenset())
        rows.append({
            "name": name,
            "retinue": ld.retinue,
            "weapon": ld.weapon or "",
            "shield": ld.shield or "",
            "armor": ld.armor,
            "ranged": ld.ranged or "",
            "tiltyard": bool(ld.has_tiltyard),
            "size": int(ld.size),
            "tags": ",".join(ld.extra_tags),
            "playstyle": ld.playstyle or "Random",
            "wins": wins,
            "losses": losses,
            "mut_wipe": mut_wipe,
            "indecisive": indecisive,
            "n_battles": n_battles,
            "win_rate": wins / n_battles,
            "loss_rate": losses / n_battles,
            "decisive_rate": (wins + losses + mut_wipe) / n_battles,
            "decisive_win_rate": wins / decisive_total if decisive_total else 0.0,
            "avg_self_survivors": avg_self_rem,
            "avg_opp_survivors": avg_opp_rem,
            "kill_efficiency": avg_self_rem - avg_opp_rem,
            "upkeep_per_retinue": int(ld.upkeep_per_retinue),
            "army_upkeep": army_upkeep,
            "wins_per_1000_upkeep": wins / (army_upkeep / 1000) if army_upkeep else 0.0,
            "military_pursuit_count": int(getattr(ld, "military_pursuit_count", 0)),
            "domain_count": int(getattr(ld, "domain_count", 0)),
            "pursuits": "|".join(sorted(pursuits)),
        })
    return pd.DataFrame(rows)


def tactic_matrix_frame(counts: np.ndarray, a_wins: np.ndarray, b_wins: np.ndarray, tactics: list[str]) -> pd.DataFrame:
    rows = []
    for i, a_tactic in enumerate(tactics):
        for j, b_tactic in enumerate(tactics):
            n = int(counts[i, j])
            aw = int(a_wins[i, j])
            bw = int(b_wins[i, j])
            stale = max(0, n - aw - bw)
            rows.append({
                "a_tactic": a_tactic,
                "b_tactic": b_tactic,
                "n_battles": n,
                "a_wins": aw,
                "b_wins": bw,
                "a_win_rate": aw / n if n else 0.0,
                "b_win_rate": bw / n if n else 0.0,
                "stalemate_rate": stale / n if n else 0.0,
            })
    return pd.DataFrame(rows)


def write_parquet(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False, engine="pyarrow")


def run_tournament_parquet(
    *,
    pool,
    rules: RulesConfig,
    data_dir: Path,
    phase: str,
    output_suffix: str,
    n_runs: int,
    n_workers: int,
    seed: int,
    reporter: ProgressReporter,
) -> dict[str, str]:
    n_loadouts = len(pool)
    matchups_dir = data_dir / f"matchups{output_suffix}"
    matchups_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        ld.name: {
            "wins": 0,
            "losses": 0,
            "mut_wipe": 0,
            "indecisive": 0,
            "rem_self": 0.0,
            "rem_opp": 0.0,
            "n_battles": 0,
            "loadout": ld,
        }
        for ld in pool
    }

    tactic_pair_count = np.zeros((len(rules.tactics), len(rules.tactics)), dtype=np.int64)
    tactic_pair_a_wins = np.zeros_like(tactic_pair_count)
    tactic_pair_b_wins = np.zeros_like(tactic_pair_count)

    completed_rows = 0
    matchups_completed = 0
    battles_completed = 0
    reporter.write(status="running", phase=phase, completed=0, total=n_loadouts)
    log(f"{phase}: {n_loadouts} loadouts, n_runs={n_runs}, workers={n_workers}")

    def handle_row(i: int, row_results) -> None:
        nonlocal completed_rows, matchups_completed, battles_completed
        ld_a = pool[i]
        records = []
        for j, result in row_results:
            ld_b = pool[j]
            records.append(matchup_record(ld_a, ld_b, result))
            tournament_vec._update_summary(summary, ld_a.name, result, n_runs, mirror=(i == j))
            if "first_skirm_tactic_pair" in result:
                tactic_pair_count[:] = tactic_pair_count + result["first_skirm_tactic_pair"]
                tactic_pair_a_wins[:] = tactic_pair_a_wins + result["first_skirm_tactic_a_wins"]
                tactic_pair_b_wins[:] = tactic_pair_b_wins + result["first_skirm_tactic_b_wins"]
        write_parquet(pd.DataFrame(records), matchups_dir / f"part-row-{i:06d}.parquet")
        completed_rows += 1
        matchups_completed += len(records)
        battles_completed += len(records) * n_runs
        reporter.write(
            status="running",
            phase=phase,
            completed=completed_rows,
            total=n_loadouts,
            current_label=ld_a.name,
            matchups_completed=matchups_completed,
            battles_completed=battles_completed,
        )
        reporter.check_cancelled(phase, completed_rows, n_loadouts)

    if n_workers <= 1:
        for i, ld_a in enumerate(pool):
            row_results = []
            for j, ld_b in enumerate(pool):
                if i != j and tournament_vec._unique_conflict(ld_a, ld_b):
                    continue
                result = run_matchup_vec(
                    ld_a,
                    ld_b,
                    n_runs=n_runs,
                    seed=seed + i * n_loadouts + j,
                    a_playstyle=ld_a.playstyle,
                    b_playstyle=ld_b.playstyle,
                    rules=rules,
                )
                row_results.append((j, result))
            handle_row(i, row_results)
    else:
        tasks = [(i, ld_a, pool, n_runs, seed, n_loadouts, rules) for i, ld_a in enumerate(pool)]
        with mp.Pool(n_workers, initializer=tournament_vec._init_worker, initargs=(rules,)) as workers:
            for i, row_results in workers.imap_unordered(tournament_vec._process_row, tasks, chunksize=1):
                handle_row(i, row_results)

    summary_path = data_dir / f"summary{output_suffix}.parquet"
    tactic_path = data_dir / f"tactic_matrix{output_suffix}.parquet"
    write_parquet(summary_frame(summary, n_runs), summary_path)
    write_parquet(tactic_matrix_frame(tactic_pair_count, tactic_pair_a_wins, tactic_pair_b_wins, rules.tactics), tactic_path)
    log(f"{phase}: wrote {summary_path} and {tactic_path}")
    return {
        f"summary{output_suffix}": str(summary_path),
        f"matchups{output_suffix}": str(matchups_dir),
        f"tactic_matrix{output_suffix}": str(tactic_path),
    }


def stratified_sample(pool, sample_size: int, seed: int, per_bucket: int = 2):
    by_bucket = defaultdict(list)
    for ld in pool:
        by_bucket[(ld.retinue, getattr(ld, "military_pursuit_count", 0))].append(ld)
    rng = random.Random(seed)
    sample = []
    for loadouts_in_bucket in by_bucket.values():
        sample.extend(rng.sample(loadouts_in_bucket, min(len(loadouts_in_bucket), per_bucket)))
    if len(sample) > sample_size:
        sample = rng.sample(sample, sample_size)
    return sample


def with_forced_tactic_playstyles(rules: RulesConfig) -> RulesConfig:
    forced = deepcopy(rules)
    for idx, tactic in enumerate(forced.tactics):
        weights = [0.0] * len(forced.tactics)
        weights[idx] = 1.0
        forced.static_playstyles[f"_Forced_{idx}"] = {
            "primaries": [idx],
            "weights": weights,
            "initiate_rate": 0.5,
            "disable_fatigue_fallback": True,
            "description": f"Forced {tactic}",
        }
    return forced


def forced_name(idx: int) -> str:
    return f"_Forced_{idx}"


def run_forced_tactics_parquet(
    *,
    pool,
    rules: RulesConfig,
    data_dir: Path,
    n_runs: int,
    sample_size: int,
    seed: int,
    reporter: ProgressReporter,
) -> dict[str, str]:
    sample = stratified_sample(pool, sample_size, seed)
    forced_rules = with_forced_tactic_playstyles(rules)
    n_tactics = len(rules.tactics)
    win_rate_grid = np.zeros((n_tactics, n_tactics), dtype=np.float64)
    survival_grid = np.zeros_like(win_rate_grid)
    skirm_grid = np.zeros_like(win_rate_grid)
    indec_grid = np.zeros_like(win_rate_grid)
    phase = "forced_tactics"
    reporter.write(status="running", phase=phase, completed=0, total=len(sample))
    log(f"{phase}: sample={len(sample)}, n_runs={n_runs}")

    for ld_idx, ld in enumerate(sample):
        for i, a_tactic in enumerate(rules.tactics):
            for j, b_tactic in enumerate(rules.tactics):
                result = run_matchup_vec(
                    ld,
                    ld,
                    n_runs=n_runs,
                    seed=seed + ld_idx * 49 + i * n_tactics + j,
                    a_playstyle=forced_name(i),
                    b_playstyle=forced_name(j),
                    rules=forced_rules,
                )
                win_rate_grid[i, j] += result["a_wins"] / n_runs if n_runs else 0.0
                survival_grid[i, j] += result["avg_a_rem"]
                skirm_grid[i, j] += result["avg_skirm"]
                indec_grid[i, j] += result["indecisive"] / n_runs if n_runs else 0.0
        completed = ld_idx + 1
        reporter.write(
            status="running",
            phase=phase,
            completed=completed,
            total=len(sample),
            current_label=ld.name,
            matchups_completed=completed * n_tactics * n_tactics,
            battles_completed=completed * n_tactics * n_tactics * n_runs,
        )
        reporter.check_cancelled(phase, completed, len(sample))

    denom = max(1, len(sample))
    rows = []
    for i, a_tactic in enumerate(rules.tactics):
        for j, b_tactic in enumerate(rules.tactics):
            rows.append({
                "a_tactic": a_tactic,
                "b_tactic": b_tactic,
                "win_rate": win_rate_grid[i, j] / denom,
                "survival": survival_grid[i, j] / denom,
                "skirm": skirm_grid[i, j] / denom,
                "indecisive_rate": indec_grid[i, j] / denom,
            })
    path = data_dir / "forced_tactics.parquet"
    write_parquet(pd.DataFrame(rows), path)
    log(f"{phase}: wrote {path}")
    return {"forced_tactics": str(path)}


def run_horde_parquet(
    *,
    pool,
    rules: RulesConfig,
    data_dir: Path,
    n_runs: int,
    sample_size: int,
    max_waves: int,
    seed: int,
    reporter: ProgressReporter,
) -> dict[str, str]:
    sample = stratified_sample(pool, sample_size, seed)
    phase = "horde"
    reporter.write(status="running", phase=phase, completed=0, total=len(sample))
    log(f"{phase}: sample={len(sample)}, n_runs={n_runs}, waves={max_waves}")
    rows = []
    for i, ld in enumerate(sample):
        result = horde_mode.run_horde(ld, sample, n_runs=n_runs, max_waves=max_waves, seed=seed + i * 1009, rules=rules)
        wave_of_wipe = result["wave_of_wipe"]
        break_even = result["break_even_wave"]
        rows.append({
            "name": ld.name,
            "retinue": ld.retinue,
            "weapon": ld.weapon or "",
            "shield": ld.shield or "",
            "armor": ld.armor,
            "ranged": ld.ranged or "",
            "mpc": int(getattr(ld, "military_pursuit_count", 0)),
            "domain_count": int(getattr(ld, "domain_count", 0)),
            "mean_waves": float(wave_of_wipe.mean()),
            "median_waves": float(np.median(wave_of_wipe)),
            "p_survive_all": float((wave_of_wipe > max_waves).sum() / n_runs),
            "mean_spoils": float(result["cumulative_spoils"].mean()),
            "mean_losses_value": float(result["cumulative_losses_value"].mean()),
            "initial_muster_cost": float(result["initial_muster_cost"]),
            "mean_net_profit": float((result["cumulative_spoils"] - result["initial_muster_cost"] - result["cumulative_remuster_cost"]).mean()),
            "p_breaks_even": float((break_even <= max_waves).sum() / n_runs),
            "final_size_mean": float(result["per_run_final_size"].mean()),
        })
        completed = i + 1
        reporter.write(
            status="running",
            phase=phase,
            completed=completed,
            total=len(sample),
            current_label=ld.name,
            matchups_completed=completed * max_waves,
            battles_completed=completed * max_waves * n_runs,
        )
        reporter.check_cancelled(phase, completed, len(sample))

    path = data_dir / "horde_survival.parquet"
    write_parquet(pd.DataFrame(rows), path)
    log(f"{phase}: wrote {path}")
    return {"horde_survival": str(path)}


def build_base_pool(rules: RulesConfig):
    log("Generating loadout pool")
    pool = loadouts.archetype_pool(rules=rules)
    log(f"Generated {len(pool)} loadouts")
    return pool


def build_playstyle_pool(pool, rules: RulesConfig):
    style_pool = []
    for ld in pool:
        style_pool.append(ld._replace(playstyle=playstyles.assign_default_playstyle(ld, rules=rules)))
    twins = loadouts.kt_twins(pool, rules=rules)
    style_pool.extend(twins)
    log(f"Playstyle pool: {len(style_pool)} loadouts ({len(twins)} KT twins)")
    return style_pool


def run_from_config(config_path: Path) -> None:
    config = load_config(config_path)
    run_dir = Path(config["output_dir"]).resolve()
    data_dir = run_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    reporter = ProgressReporter(run_dir)
    reporter.pid = str(os.getpid())
    reporter.write(status="running", phase="startup", completed=0, total=1)

    artifacts: dict[str, str] = {}
    run_type = config["run_type"]
    if run_type not in {"main", "playstyle", "forced_tactics", "horde", "all_compute"}:
        raise ValueError(f"Unknown run_type: {run_type}")
    rules = RulesConfig.from_json(config["rules_path"])
    pool = build_base_pool(rules)
    if config.get("pool_limit"):
        pool = pool[: int(config["pool_limit"])]
        log(f"Applied pool_limit={len(pool)}")
    seed = int(config.get("seed", 2026))
    n_workers = int(config.get("n_workers", 1))

    if run_type in ("main", "all_compute"):
        artifacts.update(run_tournament_parquet(
            pool=pool,
            rules=rules,
            data_dir=data_dir,
            phase="main",
            output_suffix="_main",
            n_runs=int(config.get("n_runs_main", 100)),
            n_workers=n_workers,
            seed=seed,
            reporter=reporter,
        ))
    if run_type in ("playstyle", "all_compute"):
        style_pool = build_playstyle_pool(pool, rules)
        artifacts.update(run_tournament_parquet(
            pool=style_pool,
            rules=rules,
            data_dir=data_dir,
            phase="playstyle",
            output_suffix="_playstyle",
            n_runs=int(config.get("n_runs_playstyle", 100)),
            n_workers=n_workers,
            seed=seed + 100_000,
            reporter=reporter,
        ))
    if run_type in ("forced_tactics", "all_compute"):
        artifacts.update(run_forced_tactics_parquet(
            pool=pool,
            rules=rules,
            data_dir=data_dir,
            n_runs=int(config.get("n_runs_forced", 100)),
            sample_size=int(config.get("forced_sample_size", 60)),
            seed=seed,
            reporter=reporter,
        ))
    if run_type in ("horde", "all_compute"):
        artifacts.update(run_horde_parquet(
            pool=pool,
            rules=rules,
            data_dir=data_dir,
            n_runs=int(config.get("n_runs_horde", 50)),
            sample_size=int(config.get("horde_sample_size", 60)),
            max_waves=int(config.get("horde_waves", 8)),
            seed=seed,
            reporter=reporter,
        ))

    reporter.write(status="complete", phase="complete", completed=1, total=1, artifacts=artifacts)
    write_json(run_dir / "artifacts.json", artifacts)
    log("Run complete")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    config_path = Path(args.config).resolve()
    run_dir = Path(load_config(config_path)["output_dir"]).resolve()
    reporter = ProgressReporter(run_dir)
    reporter.pid = str(__import__("os").getpid())
    try:
        run_from_config(config_path)
        return 0
    except CancelRequested:
        log("Run cancelled")
        return 2
    except Exception as exc:
        tb = traceback.format_exc()
        log(tb)
        reporter.write(status="failed", phase="failed", completed=0, total=1, error=str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
