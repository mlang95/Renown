"""
Vectorized tournament runner — same interface as tournament.py but ~4x faster
for large run counts. Optional multiprocessing via n_workers parameter.

Usage:
    python3 tournament_vec.py [n_runs] [n_workers]
"""

import csv
import time
import sys
from pathlib import Path
import multiprocessing as mp
from functools import partial

import numpy as np

import renown_combat
from normalized_matrix import build_normalized_matrix
from loadouts import archetype_pool
from vectorized_combat import run_matchup_vec, invalidate_tactic_tables


# Unique in-game MONUMENTS (CSV Type == "Monument"): only ONE of each can be built in the entire
# game, so two loadouts that BOTH contain the same monument can never coexist as opponents. Skipping
# these matchups removes nonsensical mirror comparisons. Names are the PURSUITS_INFO keys (which differ
# from the CSV display names): ABF=Advanced Blast Furnaces, Preceptory=Preceptory of the Knight's
# Templar, Outrider Intercept Post=Outrider Station.
UNIQUE_BUILDINGS = ("ABF", "Royal Pavilion", "Preceptory",
                    "Ministry of Military Strategy", "Outrider Intercept Post", "Cipher Chamber")

def _unique_conflict(ld_a, ld_b):
    """True if A and B share any unique-only-one-in-game building (can't both exist)."""
    pa = ld_a.pursuits
    pb = ld_b.pursuits
    for b in UNIQUE_BUILDINGS:
        if b in pa and b in pb:
            return True
    return False


# The tactic matrix lives in renown_combat.TACTIC_MATRIX (single source of truth).
# No sync needed — just ensure the cached lookup tables are fresh on import.
invalidate_tactic_tables()


def _init_worker():
    """Each worker rebuilds tactic tables on init. The matrix is already defined in
    renown_combat (imported fresh per worker), so no clear/update is needed."""
    from vectorized_combat import invalidate_tactic_tables
    invalidate_tactic_tables()


def _playstyles_for_mode(ld_a, ld_b, mode):
    """Resolve the (a_playstyle, b_playstyle) pair for a given simulation mode.
      'random'    → both sides play uniformly-random tactics (skill-neutral).
      'playstyle' → each side plays its assigned default playstyle.
    """
    if mode == "random":
        return "Random", "Random"
    return (ld_a.playstyle or "Random"), (ld_b.playstyle or "Random")


def _process_row(args):
    """Process one row (one a_loadout vs all b_loadouts) across all requested modes."""
    i, ld_a, pool, n_runs, base_seed, n_loadouts, modes = args
    from vectorized_combat import run_matchup_vec
    row_results = []
    for j, ld_b in enumerate(pool):
        if i != j and _unique_conflict(ld_a, ld_b):
            continue  # both share a unique monument — can't coexist, skip
        for m_idx, mode in enumerate(modes):
            # Distinct seed per (pair, mode) so modes are independent draws.
            seed = base_seed + (i * n_loadouts + j) * len(modes) + m_idx
            a_ps, b_ps = _playstyles_for_mode(ld_a, ld_b, mode)
            r = run_matchup_vec(ld_a, ld_b, n_runs=n_runs, seed=seed,
                                a_playstyle=a_ps, b_playstyle=b_ps)
            row_results.append((j, mode, r))
    return i, row_results


def _matchup_header():
    return [
        "a_name", "b_name", "mode",
        "a_wins", "b_wins", "mut_wipe", "indecisive",
        "avg_skirm", "avg_a_rem", "avg_b_rem",
        "avg_a_killed_combat", "avg_a_killed_shake", "avg_a_killed_waver", "avg_a_killed_rout",
        "avg_b_killed_combat", "avg_b_killed_shake", "avg_b_killed_waver", "avg_b_killed_rout",
        "a_wipe_combat", "a_wipe_shake", "a_wipe_waver", "a_wipe_rout",
        "b_wipe_combat", "b_wipe_shake", "b_wipe_waver", "b_wipe_rout",
        "a_shield_destroyed_rate", "b_shield_destroyed_rate",
        "a_retinue", "a_weapon", "a_shield", "a_armor", "a_ranged", "a_tiltyard", "a_size", "a_tags", "a_playstyle",
        "b_retinue", "b_weapon", "b_shield", "b_armor", "b_ranged", "b_tiltyard", "b_size", "b_tags", "b_playstyle",
        "a_military_pursuit_count", "a_domain_count", "a_pursuits",
        "b_military_pursuit_count", "b_domain_count", "b_pursuits",
    ]


def _write_matchup_row(writer, ld_a, ld_b, r, mode="random"):
    a_mpc = getattr(ld_a, "military_pursuit_count", 0)
    a_dc  = getattr(ld_a, "domain_count", 0)
    a_pu  = getattr(ld_a, "pursuits", frozenset())
    b_mpc = getattr(ld_b, "military_pursuit_count", 0)
    b_dc  = getattr(ld_b, "domain_count", 0)
    b_pu  = getattr(ld_b, "pursuits", frozenset())
    writer.writerow([
        ld_a.name, ld_b.name, mode,
        r["a_wins"], r["b_wins"], r["mut_wipe"], r["indecisive"],
        f"{r['avg_skirm']:.2f}", f"{r['avg_a_rem']:.2f}", f"{r['avg_b_rem']:.2f}",
        f"{r['avg_a_killed_combat']:.2f}", f"{r['avg_a_killed_shake']:.2f}", f"{r.get('avg_a_killed_waver',0.0):.2f}", f"{r['avg_a_killed_rout']:.2f}",
        f"{r['avg_b_killed_combat']:.2f}", f"{r['avg_b_killed_shake']:.2f}", f"{r.get('avg_b_killed_waver',0.0):.2f}", f"{r['avg_b_killed_rout']:.2f}",
        r['a_wipe_combat'], r['a_wipe_shake'], r.get('a_wipe_waver',0), r['a_wipe_rout'],
        r['b_wipe_combat'], r['b_wipe_shake'], r.get('b_wipe_waver',0), r['b_wipe_rout'],
        f"{r.get('a_shield_destroyed_rate', 0.0):.4f}", f"{r.get('b_shield_destroyed_rate', 0.0):.4f}",
        ld_a.retinue, ld_a.weapon, ld_a.shield or "", ld_a.armor, ld_a.ranged or "", ld_a.has_tiltyard, ld_a.size, ",".join(ld_a.extra_tags), ld_a.playstyle or "Random",
        ld_b.retinue, ld_b.weapon, ld_b.shield or "", ld_b.armor, ld_b.ranged or "", ld_b.has_tiltyard, ld_b.size, ",".join(ld_b.extra_tags), ld_b.playstyle or "Random",
        a_mpc, a_dc, "|".join(sorted(a_pu)),
        b_mpc, b_dc, "|".join(sorted(b_pu)),
    ])


def _update_summary(summary, ld_a_name, r, n_runs, mirror):
    if mirror:
        return
    s = summary[ld_a_name]
    s["wins"] += r["a_wins"]
    s["losses"] += r["b_wins"]
    s["mut_wipe"] += r["mut_wipe"]
    s["indecisive"] += r["indecisive"]
    s["rem_self"] += r["avg_a_rem"]
    s["rem_opp"] += r["avg_b_rem"]
    s["n_battles"] += n_runs


def _csv_to_parquet(csv_path, parquet_path, verbose=False):
    """Read the matchup CSV and write a compact Parquet copy. Downcasts numeric columns
    (small ints for counts, float32 for rates) so the file is ~20x smaller than the CSV
    and loads ~9x faster. Reads in chunks to bound memory on very large tournaments."""
    import pandas as pd
    t0 = time.time()
    # Read in chunks and concat (chunked read bounds peak memory vs one giant read_csv).
    chunks = []
    for chunk in pd.read_csv(csv_path, chunksize=500_000):
        # Downcast: integer count columns → smallest int; float columns → float32; keep
        # string/object columns (names, retinue, weapon, etc.) as-is.
        for col in chunk.columns:
            cd = chunk[col].dtype
            if cd.kind in ("i", "u"):
                chunk[col] = pd.to_numeric(chunk[col], downcast="integer")
            elif cd.kind == "f":
                chunk[col] = chunk[col].astype("float32")
        chunks.append(chunk)
    df = pd.concat(chunks, ignore_index=True)
    df.to_parquet(parquet_path, index=False, compression="snappy")
    if verbose:
        import os
        csv_mb = os.path.getsize(csv_path) / 1e6
        pq_mb = os.path.getsize(parquet_path) / 1e6
        print(f"  Parquet written: {parquet_path.name} "
              f"({csv_mb:.0f}MB CSV → {pq_mb:.0f}MB Parquet, {csv_mb/max(pq_mb,1e-9):.0f}x smaller) "
              f"in {time.time()-t0:.1f}s", flush=True)


def _write_summary(summary, summary_path, n_runs):
    with open(summary_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "name", "retinue", "weapon", "shield", "armor", "ranged", "tiltyard", "size", "tags", "playstyle",
            "wins", "losses", "mut_wipe", "indecisive", "n_battles",
            "win_rate", "loss_rate", "decisive_rate", "decisive_win_rate",
            "avg_self_survivors", "avg_opp_survivors", "kill_efficiency",
            "upkeep_per_retinue", "army_upkeep",
            "wins_per_1000_upkeep",
            "military_pursuit_count", "domain_count", "pursuits",
        ])
        for name, s in summary.items():
            ld = s["loadout"]
            n = max(1, s["n_battles"])
            win_rate = s["wins"] / n
            loss_rate = s["losses"] / n
            decisive_rate = (s["wins"] + s["losses"] + s["mut_wipe"]) / n
            # decisive_win_rate: of battles that actually decided (one side won), what fraction
            # did THIS loadout win? Useful for tactic analysis since mutual_wipe + indecisive
            # share is dominated by combat-resolution mechanics rather than loadout/tactic quality.
            decisive_total = s["wins"] + s["losses"]
            decisive_win_rate = (s["wins"] / decisive_total) if decisive_total > 0 else 0.0
            n_opps = (n // n_runs) or 1
            avg_self_rem = s["rem_self"] / n_opps
            avg_opp_rem = s["rem_opp"] / n_opps
            kill_eff = avg_self_rem - avg_opp_rem
            army_upkeep = ld.upkeep_per_retinue * ld.size
            wins_per_1k = s["wins"] / (army_upkeep / 1000) if army_upkeep else 0
            # Pursuit columns (graceful for old Loadouts without these fields)
            mpc = getattr(ld, "military_pursuit_count", 0)
            dc = getattr(ld, "domain_count", 0)
            pursuits = getattr(ld, "pursuits", frozenset())
            writer.writerow([
                name, ld.retinue, ld.weapon, ld.shield or "", ld.armor, ld.ranged or "", ld.has_tiltyard, ld.size, ",".join(ld.extra_tags), ld.playstyle or "Random",
                s["wins"], s["losses"], s["mut_wipe"], s["indecisive"], s["n_battles"],
                f"{win_rate:.4f}", f"{loss_rate:.4f}", f"{decisive_rate:.4f}", f"{decisive_win_rate:.4f}",
                f"{avg_self_rem:.2f}", f"{avg_opp_rem:.2f}", f"{kill_eff:.2f}",
                ld.upkeep_per_retinue, army_upkeep,
                f"{wins_per_1k:.2f}",
                mpc, dc, "|".join(sorted(pursuits)),
            ])


def run_tournament_vec(pool, n_runs=100, output_dir=".", base_seed=2026,
                       filename_suffix="", n_workers=1, verbose=True, print_every=1,
                       modes=("random", "playstyle")):
    """Run a full round-robin tournament.

    n_workers: number of parallel worker processes. 1 = no multiprocessing.
               Use mp.cpu_count() for max parallelism (typically 4-16 on consumer hardware).
    verbose: print progress updates (default True).
    print_every: print only every Nth row's progress (default 1 = every row). Set to 10
                 to reduce I/O overhead in Jupyter on long tournaments.
    """
    out_dir = Path(output_dir)
    out_dir.mkdir(exist_ok=True)

    modes = list(modes)
    n_loadouts = len(pool)
    n_matchups = n_loadouts * n_loadouts
    if verbose:
        print(f"Vectorized tournament: {n_loadouts}x{n_loadouts} = {n_matchups:,} matchups × {n_runs} runs")
        print(f"Modes: {modes}  →  {n_matchups * n_runs * len(modes):,} total battles")
        if n_workers > 1:
            print(f"Multiprocessing: {n_workers} workers")

    start = time.time()

    # Single MASTER matchups file with a `mode` column distinguishing the simulations.
    matchup_path = out_dir / f"matchups{filename_suffix}.csv"
    # Per-mode summary accumulators (a build's win record differs by mode).
    summary = {m: {ld.name: {"wins": 0, "losses": 0, "mut_wipe": 0, "indecisive": 0,
                              "rem_self": 0.0, "rem_opp": 0.0, "n_battles": 0,
                              "loadout": ld} for ld in pool} for m in modes}

    f = open(matchup_path, "w", newline="")
    writer = csv.writer(f)
    writer.writerow(_matchup_header())

    # Per-mode first-skirmish tactic-pair matrices (the empirical tactic matrix).
    tactic_pair_count   = {m: np.zeros((7, 7), dtype=np.int64) for m in modes}
    tactic_pair_a_wins  = {m: np.zeros((7, 7), dtype=np.int64) for m in modes}
    tactic_pair_b_wins  = {m: np.zeros((7, 7), dtype=np.int64) for m in modes}

    if n_workers <= 1:
        for i, ld_a in enumerate(pool):
            for j, ld_b in enumerate(pool):
                if i != j and _unique_conflict(ld_a, ld_b):
                    continue  # both share a unique monument — can't coexist, skip
                for m_idx, mode in enumerate(modes):
                    seed = base_seed + (i * n_loadouts + j) * len(modes) + m_idx
                    a_ps, b_ps = _playstyles_for_mode(ld_a, ld_b, mode)
                    r = run_matchup_vec(ld_a, ld_b, n_runs=n_runs, seed=seed,
                                        a_playstyle=a_ps, b_playstyle=b_ps)
                    _write_matchup_row(writer, ld_a, ld_b, r, mode=mode)
                    _update_summary(summary[mode], ld_a.name, r, n_runs, mirror=(i == j))
                    if "first_skirm_tactic_pair" in r:
                        tactic_pair_count[mode]  += r["first_skirm_tactic_pair"]
                        tactic_pair_a_wins[mode] += r["first_skirm_tactic_a_wins"]
                        tactic_pair_b_wins[mode] += r["first_skirm_tactic_b_wins"]
            if verbose and ((i + 1) % print_every == 0 or i == n_loadouts - 1):
                elapsed = time.time() - start
                done = (i + 1) / n_loadouts
                eta = elapsed / done - elapsed if done > 0 else 0
                print(f"  [{i+1}/{n_loadouts}] {ld_a.name:<40} | elapsed {elapsed:.0f}s, eta {eta:.0f}s", flush=True)
    else:
        tasks = [(i, ld_a, pool, n_runs, base_seed, n_loadouts, modes) for i, ld_a in enumerate(pool)]
        completed = 0
        with mp.Pool(n_workers, initializer=_init_worker) as workers:
            for i, row_results in workers.imap_unordered(_process_row, tasks, chunksize=1):
                ld_a = pool[i]
                for j, mode, r in row_results:
                    ld_b = pool[j]
                    _write_matchup_row(writer, ld_a, ld_b, r, mode=mode)
                    _update_summary(summary[mode], ld_a.name, r, n_runs, mirror=(i == j))
                    if "first_skirm_tactic_pair" in r:
                        tactic_pair_count[mode]  += r["first_skirm_tactic_pair"]
                        tactic_pair_a_wins[mode] += r["first_skirm_tactic_a_wins"]
                        tactic_pair_b_wins[mode] += r["first_skirm_tactic_b_wins"]
                completed += 1
                if verbose and (completed % print_every == 0 or completed == n_loadouts):
                    elapsed = time.time() - start
                    done = completed / n_loadouts
                    eta = elapsed / done - elapsed if done > 0 else 0
                    print(f"  [{completed}/{n_loadouts}] (row i={i}) {ld_a.name:<40} | elapsed {elapsed:.0f}s, eta {eta:.0f}s", flush=True)

    f.close()

    # ── Optional Parquet post-export ──
    # The tournament writes CSV incrementally (streaming, crash-resilient). At large pool
    # sizes (e.g. MPC [5,13] → ~13M matchup rows) the matchup CSV is big (~850MB) and slow
    # to re-read in analysis. If pyarrow is available, write a compact Parquet copy ONCE here
    # (≈20x smaller, ≈9x faster to load). CSV stays the primary/authoritative file; Parquet
    # is a convenience for repeated analysis reads. Failures are non-fatal — CSV is intact.
    try:
        import pandas as pd  # noqa
        import pyarrow  # noqa: F401  (engine check)
        parquet_path = out_dir / f"matchups{filename_suffix}.parquet"
        _csv_to_parquet(matchup_path, parquet_path, verbose=verbose)
    except ImportError:
        if verbose:
            print("  (pyarrow not installed — skipping Parquet export; CSV is available. "
                  "`pip install pyarrow --break-system-packages` to enable.)", flush=True)
    except Exception as e:  # pragma: no cover
        if verbose:
            print(f"  (Parquet export failed, CSV intact: {e})", flush=True)

    summary_path = out_dir / f"summary{filename_suffix}.csv"
    # Per-mode summaries. The first mode also gets the un-suffixed name for back-compat,
    # plus each mode gets summary_{mode}.csv.
    from renown_combat import TACTICS
    primary_summary_path = None
    for m in modes:
        mode_summary_path = out_dir / f"summary{filename_suffix}_{m}.csv"
        _write_summary(summary[m], mode_summary_path, n_runs)
        if primary_summary_path is None:
            primary_summary_path = mode_summary_path
            # Back-compat alias: summary.csv == the first mode's summary.
            _write_summary(summary[m], summary_path, n_runs)

        # Per-mode empirical tactic matrix.
        tactic_matrix_path = out_dir / f"tactic_matrix{filename_suffix}_{m}.csv"
        with open(tactic_matrix_path, "w", newline="") as tf:
            tw = csv.writer(tf)
            tw.writerow(["a_tactic", "b_tactic", "n_battles", "a_wins", "b_wins",
                         "a_win_rate", "b_win_rate", "stalemate_rate"])
            for i, a_t in enumerate(TACTICS):
                for j, b_t in enumerate(TACTICS):
                    n = int(tactic_pair_count[m][i, j])
                    aw = int(tactic_pair_a_wins[m][i, j])
                    bw = int(tactic_pair_b_wins[m][i, j])
                    stale = max(0, n - aw - bw)
                    tw.writerow([a_t, b_t, n, aw, bw,
                                 f"{(aw/n if n else 0):.4f}", f"{(bw/n if n else 0):.4f}",
                                 f"{(stale/n if n else 0):.4f}"])
        # Back-compat alias for the first mode's tactic matrix.
        if m == modes[0]:
            import shutil
            shutil.copyfile(tactic_matrix_path, out_dir / f"tactic_matrix{filename_suffix}.csv")

    elapsed = time.time() - start
    if verbose:
        print(f"\nDone. {n_matchups * n_runs:,} battles in {elapsed:.0f}s ({n_matchups * n_runs / elapsed:.0f} battles/sec)")
        print(f"  Matchups CSV: {matchup_path}")
        print(f"  Summary CSV:  {summary_path}")
    return summary_path, matchup_path


if __name__ == "__main__":
    n_runs = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    n_workers = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    pool = archetype_pool()
    print(f"Pool size: {len(pool)} loadouts")
    run_tournament_vec(pool, n_runs=n_runs, n_workers=n_workers)
