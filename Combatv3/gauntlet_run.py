#!/usr/bin/env python3
"""
Fixed-gauntlet power-level runner.

Question this answers: "is each build over/underpowered?" — NOT the full pairwise matrix.

Instead of round-robin (every build vs every build, which scales QUADRATICALLY and blew the detiered
pool to ~408M pairs), this tests EVERY build against one FIXED reference panel of opponents. That
scales LINEARLY: 20,210 builds x 80 gauntlet = ~1.6M matchups, runs in minutes, loads trivially.

Each build gets a single comparable "win rate vs the field" number, because every build faces the
SAME yardstick. The gauntlet is sampled balanced across (retinue x MPC) so no archetype dominates it.

Output (to OUT_DIR):
    gauntlet_power.csv  : one row per build — win_rate, decisive, death mix, survivors, spoils, MPC, gear
    gauntlet_panel.csv  : the fixed opponent panel used (for reproducibility)

Run from bash:
    python gauntlet_run.py --balanced --per-cell none --gauntlet 80 --runs 60
    python gauntlet_run.py --csv loadouts_bal_4_13_full.csv --gauntlet 80
"""
import os, sys, time, argparse, random
from collections import defaultdict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import numpy as np
import pandas as pd
import renown_combat, vectorized_combat as vc, loadouts, playstyles, batch_engine as be


def build_gauntlet(pool, n, seed=2026):
    """Fixed reference panel: balanced across (retinue x MPC), n opponents total."""
    rng = random.Random(seed)
    by = defaultdict(list)
    for l in pool:
        by[(l.retinue, l.military_pursuit_count)].append(l)
    keys = sorted(by.keys())
    panel = []
    # round-robin across cells until we have n
    i = 0
    while len(panel) < n and keys:
        k = keys[i % len(keys)]
        bucket = by[k]
        if bucket:
            panel.append(bucket[rng.randrange(len(bucket))])
        i += 1
        if i > n * 20:
            break
    # de-dup by name, top up if needed
    seen = set(); uniq = []
    for p in panel:
        if p.name not in seen:
            seen.add(p.name); uniq.append(p)
    return [p._replace(playstyle=playstyles.assign_default_playstyle(p)) for p in uniq]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "lab_out"))
    ap.add_argument("--csv", default=None, help="load a saved pool CSV")
    ap.add_argument("--balanced", action="store_true", help="use balanced_validation_pool")
    ap.add_argument("--per-cell", default="none", help="balanced: cap per cell, or 'none' for full")
    ap.add_argument("--mpc-min", type=int, default=4)
    ap.add_argument("--mpc-max", type=int, default=13)
    ap.add_argument("--gauntlet", type=int, default=80, help="size of the fixed opponent panel")
    ap.add_argument("--runs", type=int, default=60)
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 4) - 2))
    ap.add_argument("--block", type=int, default=20000)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    vc.invalidate_tactic_tables()
    random.seed(2026); np.random.seed(2026)

    # Pool
    if args.csv and os.path.exists(args.csv):
        pool = loadouts.archetype_pool(csv_path=args.csv)
    elif args.balanced:
        _pc = str(args.per_cell).strip().lower()
        per_cell = None if _pc in ("none", "0", "all", "") else int(_pc)
        pool = loadouts.balanced_validation_pool(args.mpc_min, args.mpc_max, per_cell=per_cell, verbose=True)
    else:
        pool = loadouts.archetype_pool(min_pursuit_cost=args.mpc_min, max_pursuit_cost=args.mpc_max)
    pool = [l._replace(playstyle=playstyles.assign_default_playstyle(l)) for l in pool]
    print(f"Pool: {len(pool)} builds")

    gauntlet = build_gauntlet(pool, args.gauntlet)
    print(f"Gauntlet panel: {len(gauntlet)} fixed opponents")
    print("  panel by retinue:", dict(Counter(g.retinue for g in gauntlet)))

    # Build pool x gauntlet pairs (skip self)
    pairs = [(b, g) for b in pool for g in gauntlet if b.name != g.name]
    print(f"Matchups: {len(pairs):,}  (linear: {len(pool)} builds x {len(gauntlet)} panel)")
    print(f"Workers: {args.workers} | runs: {args.runs}\n")

    # Run in blocks, aggregate by build (a-side index within each pair)
    agg = defaultdict(lambda: dict(wins=0, losses=0, mut=0, indec=0, n=0,
                                   kc=0.0, ks=0.0, kr=0.0, rem=0.0, spoils=0.0, skirm=0.0))
    build_meta = {b.name: b for b in pool}
    t0 = time.time()
    done = 0
    for start in range(0, len(pairs), args.block):
        block = pairs[start:start + args.block]
        res = be.run_batch_random(block, n_runs=args.runs, seed=2026 + start, mode="random")
        for k, (b, g) in enumerate(block):
            s = agg[b.name]
            s["wins"]   += int(res["a_wins"][k]);  s["losses"] += int(res["b_wins"][k])
            s["mut"]    += int(res["mut_wipe"][k]); s["indec"]  += int(res["indecisive"][k])
            s["n"]      += int(res["a_wins"][k] + res["b_wins"][k] + res["mut_wipe"][k] + res["indecisive"][k])
            s["kc"] += float(res["avg_a_killed_combat"][k]); s["ks"] += float(res["avg_a_killed_shake"][k])
            s["kr"] += float(res["avg_a_killed_rout"][k]);   s["rem"] += float(res["avg_a_rem"][k])
            s["spoils"] += float(res.get("a_spoils_per_battle", res.get("a_wins"))[k]) if "a_spoils_per_battle" in res else 0.0
            s["skirm"]  += float(res["avg_skirm"][k])
        done += len(block)
        el = time.time() - t0
        print(f"  [{done:,}/{len(pairs):,}] {el:.0f}s eta {el/done*(len(pairs)-done):.0f}s")

    rows = []
    for name, s in agg.items():
        b = build_meta[name]
        dec = s["wins"] + s["losses"]
        nblk = max(1, s["wins"] + s["losses"] + s["mut"] + s["indec"])
        tk = max(1e-9, s["kc"] + s["ks"] + s["kr"])
        rows.append({
            "name": name, "retinue": b.retinue, "weapon": b.weapon,
            "shield": b.shield or "", "armor": b.armor, "ranged": b.ranged or "",
            "mpc": b.military_pursuit_count,
            "win_rate": s["wins"] / dec if dec else np.nan,           # decisive win rate vs the panel
            "win_rate_all": s["wins"] / nblk,                          # counting mutual/indecisive as non-wins
            "decisive_rate": dec / nblk,
            "mutual_rate": s["mut"] / nblk,
            "death_combat": s["kc"] / tk, "death_shake": s["ks"] / tk, "death_rout": s["kr"] / tk,
            "avg_survivors": s["rem"] / nblk, "avg_skirm": s["skirm"] / nblk,
            "upkeep": b.upkeep_per_retinue,
        })
    df = pd.DataFrame(rows).sort_values("win_rate", ascending=False)
    df.to_csv(os.path.join(args.out, "gauntlet_power.csv"), index=False)
    pd.DataFrame([{"name": g.name, "retinue": g.retinue, "weapon": g.weapon,
                   "shield": g.shield or "", "armor": g.armor, "ranged": g.ranged or "",
                   "mpc": g.military_pursuit_count} for g in gauntlet]
                 ).to_csv(os.path.join(args.out, "gauntlet_panel.csv"), index=False)

    print(f"\nDone in {time.time()-t0:.0f}s. Wrote gauntlet_power.csv ({len(df)} builds) + gauntlet_panel.csv")
    print("\nTop 10 by win rate vs panel:")
    print(df.head(10)[["name", "retinue", "weapon", "mpc", "win_rate"]].round(3).to_string(index=False))
    print("\nBottom 10:")
    print(df.tail(10)[["name", "retinue", "weapon", "mpc", "win_rate"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
