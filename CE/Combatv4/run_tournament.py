#!/usr/bin/env python3
"""
Standalone Renown tournament runner.

Runs the tournaments OUTSIDE the Jupyter notebook, so the heavy generation happens in a clean process that
releases all its memory on exit. The notebook then just LOADS the output; the run ends by printing exactly what
to set in the notebook (OUT_DIR, the pool CSV, the pool settings) and where the build explorer pages are.

Usage (normally through CE/run_tournament_d10.bat):
    python run_tournament.py --holding-first --ti-min 6 --ti-max 16 --per-cell 40 --optimal
    python run_tournament.py --balanced --ti-min 6 --ti-max 16 --per-cell 40
    python run_tournament.py --ti-min 6 --ti-max 16 --stratify 500          # generator (archetype_pool)
    python run_tournament.py --csv loadouts_hf_6_16_pc40.csv --optimal       # reuse a saved pool

Budget: TI = Holdings in the build. The Mastery Chain makes every Holding bring its line, so the Holding count
is the investment; the Wards a build occupies (military_pursuit_count / MPC) are reported, not budgeted.

Output (written to --out):
    matchups.parquet, summary.csv, tactic_matrix.csv                   (Random)
    matchups_optimal.parquet, summary_optimal.csv, ...                 (--optimal)
    matchups_playstyle.parquet, summary_playstyle.csv, ...             (unless --no-playstyle)
    loadouts_<pool>_<ti_min>_<ti_max>_<cap>.parquet/.csv               (the pool, reusable with --csv)
    build_explorer.html, build_explorer_optimal.html, ...              (unless --no-explorer)
"""
import os, sys, time, argparse, random, json
from collections import Counter, defaultdict

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
    return os.path.abspath(basename + ".csv")


def ti_of(l):
    return len(l.pursuits) if l.pursuits else 0


def stratify(pool, per_ti, seed=2026):
    """Cap each TI bucket at per_ti builds, spread across Retinues."""
    rng = random.Random(seed)
    by_ti = defaultdict(list)
    for l in pool:
        by_ti[ti_of(l)].append(l)
    out = []
    for ti, builds in sorted(by_ti.items()):
        by_ret = defaultdict(list)
        for b in builds:
            by_ret[b.retinue].append(b)
        q = per_ti // max(1, len(by_ret))
        pick = []
        for r in by_ret:
            rng.shuffle(by_ret[r]); pick += by_ret[r][:q]
        rng.shuffle(builds)
        for b in builds:
            if len(pick) >= per_ti:
                break
            if b not in pick:
                pick.append(b)
        out += pick[:per_ti]
    return out


def write_explorers(out, ran):
    """build_explorer{suffix}.html for each tournament in `ran` (mode, suffix); open it in any browser.
    Returns {mode: path}."""
    import build_rank as BR
    paths = {}
    for mode, suf in ran:
        sp = os.path.join(out, f"summary{suf}.csv")
        mp = os.path.join(out, f"matchups{suf}.parquet")
        if not os.path.exists(mp):
            mp = os.path.join(out, f"matchups{suf}.csv")
        if not (os.path.exists(sp) and os.path.exists(mp)):
            print(f"  explorer: {mode} files missing, skipped")
            continue
        try:
            cols = ["a_name", "b_name", "a_wins", "b_wins"]
            M = pd.read_parquet(mp, columns=cols) if mp.endswith(".parquet") else pd.read_csv(mp, usecols=cols)
            R, H = BR.rank(pd.read_csv(sp), M)
            arche = BR.archetypes(R, H, k=min(8, max(2, len(R) // 25)), show=False)
            paths[mode] = BR.export_explorer(R, H, os.path.join(out, f"build_explorer{suf}.html"), arche=arche,
                                             title=f"Build Explorer — {os.path.basename(os.path.normpath(out))} {mode}")
        except MemoryError:
            print(f"  explorer ({mode}): pool too large for the head-to-head matrix in RAM — build it from the notebook")
    return paths


def _per_cell(v):
    v = str(v).strip().lower()
    return None if v in ("none", "0", "all", "") else int(v)


def main():
    ap = argparse.ArgumentParser(description="Run the Renown tournament outside the notebook.")
    ap.add_argument("--out", default=os.path.join(HERE, "lab_out"), help="output dir")
    ap.add_argument("--csv", default=None, help="load a saved pool CSV instead of generating")
    ap.add_argument("--holding-first", action="store_true",
                    help="pool = loadouts.holding_first_pool: Holdings first, gear from their text, "
                         "balanced per (Retinue x TI)")
    ap.add_argument("--balanced", action="store_true",
                    help="pool = balanced_validation_pool: gear first, full legal gear cross, balanced per (Retinue x TI)")
    ap.add_argument("--ti-min", type=int, default=6, help="min TI (Holdings per build)")
    ap.add_argument("--ti-max", type=int, default=16, help="max TI")
    ap.add_argument("--mpc-min", type=int, default=None, help=argparse.SUPPRESS)   # retired: read as --ti-min
    ap.add_argument("--mpc-max", type=int, default=None, help=argparse.SUPPRESS)   # retired: read as --ti-max
    ap.add_argument("--per-cell", default="40",
                    help="holding-first / balanced: builds per (Retinue x TI) cell, or 'none' for all. Default 40.")
    ap.add_argument("--balance", default="none", choices=("none", "weapon"),
                    help="holding-first: how each (Retinue x TI) cell is sampled. 'none' = uniform; "
                         "'weapon' = slots dealt evenly across the weapons the cell can field.")
    ap.add_argument("--stratify", default="all",
                    help="generator pool: builds per TI bucket (an integer like 500), or 'all' for the full pool.")
    ap.add_argument("--drop-shield-tier", action="store_true",
                    help="balanced pool only: drop the shield-tier>=weapon-tier rule.")
    ap.add_argument("--runs", type=int, default=100, help="n_runs for all tournaments")
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 4) - 2))
    ap.add_argument("--slot-budget", default="auto",
                    help="batch block memory budget (slots/block). 'auto' = size from free RAM; "
                         "or an integer (e.g. 500000). Bigger = faster but more memory.")
    ap.add_argument("--no-random", action="store_true", help="skip the Random tournament")
    ap.add_argument("--optimal", action="store_true",
                    help="also run the Optimal tournament (both sides play the per-pairing equilibrium mix; "
                         "writes *_optimal files)")
    ap.add_argument("--no-playstyle", action="store_true", help="skip the playstyle tournament")
    ap.add_argument("--no-save-pool", action="store_true", help="don't write the generated pool CSV")
    ap.add_argument("--no-explorer", action="store_true",
                    help="don't write build_explorer*.html (one per tournament run)")
    args = ap.parse_args()
    if args.mpc_min is not None or args.mpc_max is not None:
        print("note: --mpc-min / --mpc-max are retired; read as --ti-min / --ti-max (Holdings per build)")
        args.ti_min = args.mpc_min if args.mpc_min is not None else args.ti_min
        args.ti_max = args.mpc_max if args.mpc_max is not None else args.ti_max

    os.makedirs(args.out, exist_ok=True)
    vectorized_combat.invalidate_tactic_tables()
    random.seed(2026); np.random.seed(2026)
    per_cell = _per_cell(args.per_cell)
    cap = f"_pc{per_cell}" if per_cell else "_full"
    pool_csv, pool_kind = None, None

    # ── Build or load the pool ──
    if args.csv and os.path.exists(args.csv):
        pool = loadouts.archetype_pool(csv_path=args.csv)
        pool_csv, pool_kind = os.path.abspath(args.csv), "csv"
        print(f"Loaded {len(pool)} loadouts from {args.csv}")
    elif args.holding_first:
        pool_kind = "holding_first"
        _bal = None if args.balance == "none" else args.balance
        pool = loadouts.holding_first_pool(ti_min=args.ti_min, ti_max=args.ti_max, per_cell=per_cell, balance=_bal)
        if not args.no_save_pool:
            pool_csv = save_pool(pool, os.path.join(
                args.out, f"loadouts_hf_{args.ti_min}_{args.ti_max}{cap}" + (f"_bal{_bal[0]}" if _bal else "")))
    elif args.balanced:
        pool_kind = "balanced"
        pool = loadouts.balanced_validation_pool(
            ti_min=args.ti_min, ti_max=args.ti_max, per_cell=per_cell,
            keep_shield_tier_rule=not args.drop_shield_tier, verbose=True)
        print(f"Balanced validation pool: {len(pool)} builds (TI {args.ti_min}-{args.ti_max}, per_cell={per_cell})")
        if not args.no_save_pool:
            pool_csv = save_pool(pool, os.path.join(args.out, f"loadouts_bal_{args.ti_min}_{args.ti_max}{cap}"))
    else:
        pool_kind = "generator"
        if args.csv:
            print(f"  ({args.csv} not found — generating instead)")
        pool = loadouts.archetype_pool(min_pursuit_cost=args.ti_min, max_pursuit_cost=args.ti_max)
        print(f"Generated {len(pool)} loadouts (TI {args.ti_min}-{args.ti_max})")
        strat_n = _per_cell(args.stratify)
        if strat_n:
            pool = stratify(pool, strat_n)
            print(f"Stratified to {len(pool)} builds ({strat_n} per TI)")
        if not args.no_save_pool:
            pool_csv = save_pool(pool, os.path.join(
                args.out, f"loadouts_gen_{args.ti_min}_{args.ti_max}" + (f"_st{strat_n}" if strat_n else "_full")))

    print("By retinue:", dict(Counter(l.retinue for l in pool).most_common()))
    print("By TI:", dict(sorted(Counter(ti_of(l) for l in pool).items())))

    n_pairs_est = len(pool) * (len(pool) - 1)
    print(f"\nPool: {len(pool)} builds  (~{n_pairs_est:,} raw pairs before monument filter)")
    print(f"Workers: {args.workers}  |  n_runs: {args.runs}\n")

    _sb = str(args.slot_budget).strip().lower()
    slot_budget = None if _sb in ("auto", "none", "") else int(_sb)

    ran = []                                                   # (mode, suffix) actually run
    if not args.no_random:
        t0 = time.time()
        batch_engine.run_mode_batched(
            pool, mode="random", n_runs=args.runs,
            output_dir=args.out, suffix="", base_seed=2026,
            verbose=True, n_workers=args.workers, slot_budget=slot_budget)
        print(f"Random tournament complete in {time.time()-t0:.0f}s")
        ran.append(("random", ""))

    if args.optimal:
        t0 = time.time()
        batch_engine.run_mode_batched(
            pool, mode="optimal", n_runs=args.runs,
            output_dir=args.out, suffix="_optimal", base_seed=2026,
            verbose=True, n_workers=args.workers, slot_budget=slot_budget)
        print(f"Optimal tournament complete in {time.time()-t0:.0f}s")
        ran.append(("optimal", "_optimal"))

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
        ran.append(("playstyle", "_playstyle"))

    # The notebook reads this to find the pool and the modes this run holds.
    with open(os.path.join(args.out, "run.json"), "w", encoding="utf-8") as fh:
        json.dump({"pool_csv": pool_csv, "pool_kind": pool_kind, "per_cell": per_cell, "balance": args.balance,
                   "ti_min": args.ti_min, "ti_max": args.ti_max, "runs": args.runs,
                   "modes": [m for m, _ in ran]}, fh, indent=2)

    explorers = {} if args.no_explorer else write_explorers(args.out, ran)
    print_pointers(args, os.path.abspath(args.out), pool_csv, pool_kind, per_cell, ran, explorers)


def print_pointers(args, out, pool_csv, pool_kind, per_cell, ran, explorers):
    """What to set in v11Renown_Combat_Lab.ipynb to analyse this run, and where the pages are."""
    bar = "=" * 78
    modes = [m for m, _ in ran]
    print(f"\n{bar}\nDONE. Notebook (Combatv4/v11Renown_Combat_Lab.ipynb), cell 2:\n{bar}")
    print(f'    OUT_DIR        = None      # latest run = {out}')
    print(f'    SUMMARY_SOURCE = "{"optimal" if "optimal" in modes else "random"}"'
          f"      (this run holds: {', '.join(modes) or 'nothing'})")
    print(f"    pool: {pool_csv or 'not saved; the notebook matches it by build name'}")
    print("  Then run the notebook top to bottom.")
    if explorers:
        print("\n  Build explorer (double-click to open in your browser):")
        for mode, p in explorers.items():
            print(f"    {mode:9s} {os.path.abspath(p)}")
    print(f"\n  All files: {out}\n{bar}")


if __name__ == "__main__":
    main()
