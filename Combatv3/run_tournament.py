#!/usr/bin/env python3
"""
Standalone Renown tournament runner.

Runs the main (and optionally playstyle) tournament OUTSIDE the Jupyter notebook, so the heavy
generation happens in a clean process that releases all its memory on exit. Pair with closing
Chrome/other RAM hogs for maximum headroom. The notebook then just LOADS the output for analysis.

Usage (from the Combatv3 folder):
    python run_tournament.py
    python run_tournament.py --mpc-min 1 --mpc-max 9 --stratify 40 --runs 100
    python run_tournament.py --csv loadouts_gen_1_9.csv          # use a saved pool instead of generating
    python run_tournament.py --no-playstyle                      # skip the playstyle tournament
    python run_tournament.py --frac-note                         # just print load advice and exit

Output (written to OUT_DIR, default ./lab_out):
    matchups.parquet/.csv, summary.csv, tactic_matrix.csv   (main)
    matchups_playstyle.*, summary_playstyle.csv, ...         (if playstyle enabled)
    loadouts_gen_<min>_<max>.parquet/.csv                    (the generated pool, reusable)

Rows scale ~quadratically with build count, so STRATIFY controls file size/runtime/RAM the most:
80/MPC ~= 4x the rows of 40/MPC. Start at 40 if memory is tight.
"""
import os, sys, time, argparse, random
from collections import Counter, defaultdict

# Make sure the project modules import (run from the Combatv3 dir, or edit this path).
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import numpy as np
import pandas as pd
import renown_combat, vectorized_combat, loadouts, playstyles, batch_engine


def save_pool(pool, basename):
    rows = [{
        "name": l.name, "retinue": l.retinue, "weapon": l.weapon,
        "shield": l.shield or "", "armor": l.armor, "ranged": l.ranged or "",
        "has_tiltyard": l.has_tiltyard, "size": l.size,
        "extra_tags": ",".join(l.extra_tags),
        "upkeep_per_retinue": l.upkeep_per_retinue,
        "playstyle": l.playstyle or "",
        "tiltyard_mastery": getattr(l, "tiltyard_mastery", False),
        "pursuits": "|".join(sorted(l.pursuits)),
        "military_pursuit_count": l.military_pursuit_count,
        "domain_count": l.domain_count,
    } for l in pool]
    df = pd.DataFrame(rows)
    df.to_parquet(basename + ".parquet", index=False)
    df.to_csv(basename + ".csv", index=False)
    print(f"  Saved pool -> {basename}.parquet (+ .csv)")


def stratify(pool, per_mpc, seed=2026, budget_metric="mpc"):
    rng = random.Random(seed)
    def _budget(l):
        if budget_metric == "total":
            return len(l.pursuits) if l.pursuits else 0
        return getattr(l, "military_pursuit_count", 0)
    by_mpc = defaultdict(list)
    for l in pool:
        by_mpc[_budget(l)].append(l)
    out = []
    for mpc, builds in sorted(by_mpc.items()):
        by_ret = defaultdict(list)
        for b in builds:
            by_ret[b.retinue].append(b)
        q = per_mpc // max(1, len(by_ret))
        pick = []
        for r in by_ret:
            rng.shuffle(by_ret[r]); pick += by_ret[r][:q]
        rng.shuffle(builds)
        for b in builds:
            if len(pick) >= per_mpc:
                break
            if b not in pick:
                pick.append(b)
        out += pick[:per_mpc]
    return out


def main():
    ap = argparse.ArgumentParser(description="Run the Renown tournament outside the notebook.")
    ap.add_argument("--out", default=os.path.join(HERE, "lab_out"), help="output dir")
    ap.add_argument("--csv", default=None, help="load a saved pool CSV instead of generating")
    ap.add_argument("--mpc-min", type=int, default=1, help="min MPC for generation")
    ap.add_argument("--mpc-max", type=int, default=9, help="max MPC for generation")
    ap.add_argument("--stratify", default="all",
                    help="builds per MPC bucket (an integer like 40), or 'all'/0/'none' for the full pool. "
                         "Default 'all' = no stratification.")
    ap.add_argument("--runs", type=int, default=100, help="n_runs for all tournaments")
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 4) - 2))
    ap.add_argument("--slot-budget", default="auto",
                    help="batch block memory budget (slots/block). 'auto' = size from free RAM; "
                         "or an integer (e.g. 500000). Bigger = faster but more memory.")
    ap.add_argument("--no-playstyle", action="store_true", help="skip the playstyle tournament")
    ap.add_argument("--no-save-pool", action="store_true", help="don't write the generated pool CSV")
    ap.add_argument("--balanced", action="store_true",
                    help="use balanced_validation_pool (balanced per retinue x MPC, all tiers, full "
                         "legal gear cross, retinue floors/caps ignored) instead of archetype_pool.")
    ap.add_argument("--per-cell", default="none",
                    help="balanced mode only: cap per (retinue x MPC) cell (int), or 'none'/0 for the "
                         "full cross (~4340 builds). Default 'none'.")
    ap.add_argument("--drop-shield-tier", action="store_true",
                    help="balanced mode only: drop the shield-tier>=weapon-tier rule.")
    ap.add_argument("--budget-metric", default="mpc", choices=["mpc", "total"],
                    help="generator mode: bound/stratify the pool by 'mpc' (pursuit count minus "
                         "Efficient-X discounts) or 'total' (raw pursuit count = total_investment). "
                         "Ignored in balanced mode.")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    vectorized_combat.invalidate_tactic_tables()
    random.seed(2026); np.random.seed(2026)

    # ── Build or load the pool ──
    if args.csv and os.path.exists(args.csv):
        pool = loadouts.archetype_pool(csv_path=args.csv)
        print(f"Loaded {len(pool)} loadouts from {args.csv}")
    elif args.balanced:
        _pc = str(args.per_cell).strip().lower()
        per_cell = None if _pc in ("none", "0", "all", "") else int(_pc)
        pool = loadouts.balanced_validation_pool(
            mpc_min=args.mpc_min, mpc_max=args.mpc_max, per_cell=per_cell,
            keep_shield_tier_rule=not args.drop_shield_tier, verbose=True)
        print(f"Balanced validation pool: {len(pool)} builds "
              f"(MPC {args.mpc_min}-{args.mpc_max}, per_cell={per_cell})")
        if not args.no_save_pool:
            tag = f"bal_{args.mpc_min}_{args.mpc_max}" + (f"_pc{per_cell}" if per_cell else "_full")
            save_pool(pool, os.path.join(args.out, f"loadouts_{tag}"))
    else:
        if args.csv:
            print(f"  ({args.csv} not found — generating instead)")
        pool = loadouts.archetype_pool(min_pursuit_cost=args.mpc_min, max_pursuit_cost=args.mpc_max,
                                       budget_metric=args.budget_metric)
        print(f"Generated {len(pool)} loadouts ({args.budget_metric} {args.mpc_min}-{args.mpc_max})")
        if not args.no_save_pool:
            save_pool(pool, os.path.join(args.out, f"loadouts_gen_{args.mpc_min}_{args.mpc_max}"))

    print("By retinue:", dict(Counter(l.retinue for l in pool).most_common()))

    # Resolve --stratify: "all"/"none"/"0" -> no stratification; otherwise an int per-MPC cap.
    # Balanced pool is already balanced per cell, so stratify is skipped there unless explicitly set.
    _s = str(args.stratify).strip().lower()
    strat_n = None if _s in ("all", "none", "0", "") else int(_s)
    if args.balanced and strat_n:
        print(f"(balanced mode: ignoring --stratify {strat_n}; pool already balanced per cell)")
        strat_n = None

    # ── Stratify ──
    if strat_n:
        pool = stratify(pool, strat_n, budget_metric=args.budget_metric)
        print(f"Stratified to {len(pool)} builds ({strat_n}/{args.budget_metric} bucket)")
        _bk = (lambda l: len(l.pursuits) if l.pursuits else 0) if args.budget_metric == "total" \
              else (lambda l: l.military_pursuit_count)
        print(f"  per-{args.budget_metric}:", dict(sorted(Counter(_bk(l) for l in pool).items())))
    else:
        print(f"No stratification — using full pool of {len(pool)} builds")

    n_pairs_est = len(pool) * (len(pool) - 1)
    print(f"\nPool: {len(pool)} builds  (~{n_pairs_est:,} raw pairs before monument filter)")
    print(f"Workers: {args.workers}  |  n_runs: {args.runs}\n")

    # Resolve slot budget: "auto" -> None (engine auto-sizes from free RAM); else int.
    _sb = str(args.slot_budget).strip().lower()
    slot_budget = None if _sb in ("auto", "none", "") else int(_sb)

    # ── Main tournament ──
    t0 = time.time()
    batch_engine.run_mode_batched(
        pool, mode="random", n_runs=args.runs,
        output_dir=args.out, suffix="", base_seed=2026,
        verbose=True, n_workers=args.workers, slot_budget=slot_budget)
    print(f"Main tournament complete in {time.time()-t0:.0f}s")

    # ── Playstyle tournament ──
    if not args.no_playstyle:
        style_pool = [l._replace(playstyle=playstyles.assign_default_playstyle(l)) for l in pool]
        try:
            style_pool.extend(loadouts.kt_twins(pool))
        except Exception:
            pass
        t0 = time.time()
        batch_engine.run_mode_batched(
            style_pool, mode="playstyle", n_runs=args.runs,
            output_dir=args.out, suffix="_playstyle", base_seed=2026,
            verbose=True, n_workers=args.workers, slot_budget=slot_budget)
        print(f"Playstyle tournament complete in {time.time()-t0:.0f}s")

    print(f"\nDone. Files in {args.out}")
    print("In the notebook, run cell 2 then cell 15 to load (set MATCHUP_FRAC=0.3 if still RAM-tight).")


if __name__ == "__main__":
    main()