#!/usr/bin/env python3
"""
Input x Output sensitivity sweep for Renown combat.

For each INPUT parameter (retinue stats, global AP, shake/front caps), perturb it by +/-1,
re-run a tournament, and measure the change in EVERY output metric vs a baseline run. Produces:
  - sensitivity_matrix.csv : one row per (input, direction); columns = delta of each output metric
  - sensitivity_baseline.csv : the baseline output metrics (absolute values)
  - sensitivity_heatmap.png : inputs (rows) x outputs (cols), color = delta

This is the CAUSAL version: each cell answers "if I nudge input X by +1, how much does output Y move?"

Runs unattended; ~2 * n_inputs tournaments. Keep STRATIFY small (30-40) and RUNS modest (40-60)
unless you want it to take hours. Run from bash:
    python sensitivity_sweep.py --stratify 30 --runs 50 --mpc-min 1 --mpc-max 9
"""
import os, sys, time, argparse, random, copy
from collections import defaultdict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import numpy as np
import pandas as pd
import renown_combat, vectorized_combat as vc, loadouts, playstyles, batch_engine as be, analysis


# ── Output metric extraction: turn one tournament's matchups frame into a flat dict of metrics ──
def extract_metrics(df):
    m = {}
    tot = (df["a_wins"] + df["b_wins"] + df["mut_wipe"] + df["indecisive"]).sum()
    tot = max(tot, 1)
    m["decisive_rate"] = (df["a_wins"] + df["b_wins"]).sum() / tot
    m["mutual_rate"]   = df["mut_wipe"].sum() / tot
    m["indec_rate"]    = df["indecisive"].sum() / tot
    m["avg_skirm"]     = df["avg_skirm"].mean()
    # death mix by troops (both sides)
    ck = df["avg_a_killed_combat"].sum() + df["avg_b_killed_combat"].sum()
    sk = df["avg_a_killed_shake"].sum()  + df["avg_b_killed_shake"].sum()
    rk = df["avg_a_killed_rout"].sum()   + df["avg_b_killed_rout"].sum()
    T = max(ck + sk + rk, 1)
    m["death_combat_pct"] = ck / T
    m["death_shake_pct"]  = sk / T
    m["death_rout_pct"]   = rk / T
    m["shield_destroyed_rate"] = pd.concat([df["a_shield_destroyed_rate"], df["b_shield_destroyed_rate"]]).mean()
    m["avg_survivors"]    = pd.concat([df["avg_a_rem"], df["avg_b_rem"]]).mean()
    m["avg_spoils"]       = pd.concat([df["a_spoils_per_battle"], df["b_spoils_per_battle"]]).mean()
    # per-retinue win rate (decisive) + per-retinue casualty mix
    for ret, tag in [("Levy","levy"),("Man-at-Arms","maa"),("Sergeant","sgt"),("Knight Templar","kt")]:
        sub = df[df["a_retinue"] == ret]
        aw = sub["a_wins"].sum(); bw = sub["b_wins"].sum(); dec = aw + bw
        m[f"wr_{tag}"] = aw / dec if dec else np.nan
        c = sub["avg_a_killed_combat"].sum(); s = sub["avg_a_killed_shake"].sum(); r = sub["avg_a_killed_rout"].sum()
        t = max(c + s + r, 1)
        m[f"{tag}_combat_pct"] = c / t
        m[f"{tag}_shake_pct"]  = s / t
        m[f"{tag}_rout_pct"]   = r / t
    return m


def run_once(pool, runs, workers, seed=2026):
    import tempfile
    d = tempfile.mkdtemp()
    be.run_mode_batched(pool, mode="random", n_runs=runs, output_dir=d, suffix="",
                        base_seed=seed, verbose=False, n_workers=workers)
    df = analysis.load_tournament(os.path.join(d, "matchups.csv"))
    return extract_metrics(df)


# ── Input perturbations: each returns a (apply_fn, restore_fn) that mutates the live modules ──
def make_perturbations():
    """Yield (input_name, delta, apply, restore) tuples. apply() mutates; restore() undoes."""
    perts = []

    # Retinue stats: to_hit, shaking, endurance, each retinue, +/-1
    for ret in ["Levy", "Man-at-Arms", "Sergeant", "Knight Templar"]:
        for stat in ["to_hit", "shaking", "endurance"]:
            for delta in (+1, -1):
                def mk(ret=ret, stat=stat, delta=delta):
                    orig = {}
                    def apply():
                        orig[(ret, stat)] = renown_combat.RETINUES[ret][stat]
                        renown_combat.RETINUES[ret][stat] = orig[(ret, stat)] + delta
                    def restore():
                        renown_combat.RETINUES[ret][stat] = orig[(ret, stat)]
                    return apply, restore
                a, r = mk()
                perts.append((f"{ret}.{stat}", delta, a, r))

    # Global AP shift (all weapons), +/-1  (more negative AP = deadlier; we add `delta` to ap)
    for delta in (+1, -1):
        def mk(delta=delta):
            orig = {}
            def apply():
                for k, v in renown_combat.WEAPONS.items():
                    orig[k] = v["ap"]; v["ap"] = orig[k] - delta   # +delta = deadlier (more negative)
            def restore():
                for k, v in renown_combat.WEAPONS.items():
                    v["ap"] = orig[k]
            return apply, restore
        a, r = mk()
        perts.append(("global_AP", delta, a, r))

    # SHAKE_CAP +/-1
    for delta in (+1, -1):
        def mk(delta=delta):
            orig = {}
            def apply():
                orig["v"] = vc.SHAKE_CAP; vc.SHAKE_CAP = orig["v"] + delta
            def restore():
                vc.SHAKE_CAP = orig["v"]
            return apply, restore
        a, r = mk()
        perts.append(("SHAKE_CAP", delta, a, r))

    # FRONT_CAP +/-1
    for delta in (+1, -1):
        def mk(delta=delta):
            orig = {}
            def apply():
                orig["v"] = vc.FRONT_CAP; vc.FRONT_CAP = orig["v"] + delta
            def restore():
                vc.FRONT_CAP = orig["v"]
            return apply, restore
        a, r = mk()
        perts.append(("FRONT_CAP", delta, a, r))

    return perts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "lab_out"))
    ap.add_argument("--csv", default=None, help="use a saved pool CSV instead of generating")
    ap.add_argument("--mpc-min", type=int, default=1)
    ap.add_argument("--mpc-max", type=int, default=9)
    ap.add_argument("--stratify", type=int, default=30, help="builds per MPC bucket (keep small!)")
    ap.add_argument("--runs", type=int, default=50)
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 4) - 2))
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    # Build pool
    if args.csv and os.path.exists(args.csv):
        pool = loadouts.archetype_pool(csv_path=args.csv)
    else:
        pool = loadouts.archetype_pool(min_pursuit_cost=args.mpc_min, max_pursuit_cost=args.mpc_max)
    # stratify (rows scale quadratically — keep this pool SMALL since we run it ~40 times)
    if args.stratify:
        rng = random.Random(2026); by = defaultdict(list)
        for l in pool: by[getattr(l, "military_pursuit_count", 0)].append(l)
        out = []
        for mpc, b in sorted(by.items()):
            rng.shuffle(b); out += b[:args.stratify]
        pool = out
    print(f"Pool: {len(pool)} builds | runs={args.runs} | workers={args.workers}")

    perts = make_perturbations()
    print(f"Perturbations: {len(perts)}  (=> {len(perts)+1} tournaments total)\n")

    # Baseline
    vc.invalidate_tactic_tables()
    t0 = time.time()
    base = run_once(pool, args.runs, args.workers)
    print(f"[baseline] {time.time()-t0:.0f}s")
    pd.DataFrame([base]).to_csv(os.path.join(args.out, "sensitivity_baseline.csv"), index=False)

    out_keys = list(base.keys())
    rows = []
    for i, (name, delta, apply, restore) in enumerate(perts, 1):
        t0 = time.time()
        apply()
        vc.invalidate_tactic_tables()
        importlib_reload_engines()
        try:
            metrics = run_once(pool, args.runs, args.workers)
        finally:
            restore()
            vc.invalidate_tactic_tables()
            importlib_reload_engines()
        row = {"input": name, "delta": delta}
        for k in out_keys:
            v = metrics.get(k, np.nan); b = base.get(k, np.nan)
            row[k] = (v - b) if (v == v and b == b) else np.nan   # delta from baseline
        rows.append(row)
        print(f"[{i}/{len(perts)}] {name:>22} {delta:+d}  ({time.time()-t0:.0f}s)")

    res = pd.DataFrame(rows)
    res.to_csv(os.path.join(args.out, "sensitivity_matrix.csv"), index=False)
    print(f"\nWrote sensitivity_matrix.csv ({res.shape[0]} input-perturbations x {len(out_keys)} outputs)")

    # Heatmap
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        label = res["input"] + " " + res["delta"].map(lambda d: f"{d:+d}")
        M = res[out_keys].values.astype(float)
        # normalize each OUTPUT column by its max abs so colors are comparable across metrics
        scale = np.nanmax(np.abs(M), axis=0); scale[scale == 0] = 1
        Mn = M / scale
        fig, axx = plt.subplots(figsize=(max(12, 0.5*len(out_keys)), max(8, 0.32*len(res))))
        im = axx.imshow(Mn, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
        axx.set_xticks(range(len(out_keys))); axx.set_xticklabels(out_keys, rotation=90, fontsize=7)
        axx.set_yticks(range(len(res)));      axx.set_yticklabels(label, fontsize=7)
        axx.set_title("Sensitivity: input perturbation (row) x output delta (col)\n"
                      "color = delta normalized per output column; raw deltas in sensitivity_matrix.csv")
        plt.colorbar(im, ax=axx, shrink=0.6, label="normalized delta")
        plt.tight_layout()
        plt.savefig(os.path.join(args.out, "sensitivity_heatmap.png"), dpi=110, bbox_inches="tight")
        print("Wrote sensitivity_heatmap.png")
    except Exception as e:
        print("heatmap skipped:", e)


def importlib_reload_engines():
    """Re-sync the batch engine's view of RETINUES after a mutation (StaticArmy reads live dict,
    so no reload needed for stats; caps are read live via vc.*; AP is read at StaticArmy build).
    This is a no-op hook kept for clarity / future-proofing."""
    pass


if __name__ == "__main__":
    main()
