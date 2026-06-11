#!/usr/bin/env python3
"""
Tactic matrix evaluator — per-statline 6x6 (Fall Back excluded).

The tournament samples tactics randomly, which averages OVER the tactic layer and tells you nothing
about whether Charge beats Defensive Formation. This forces every (a_tactic, b_tactic) pair in the
6x6 non-Fall-Back grid and measures the engagement, for several representative statlines — so you can
see whether the best tactic depends on the build (good design = it does) or one tactic dominates
regardless (a solved, shallow layer).

Per (statline, a_tactic, b_tactic) cell it reports:
  EMPIRICAL (simulated):
    a_win_rate     - A's decisive win share
    cas_diff       - (B troops lost - A troops lost); >0 = A favored
    decisive_rate  - fraction of runs with a decisive result
    a_survivors    - A troops remaining
  MECHANICAL (deterministic, read from TACTIC_MATRIX — what the tactic DOES):
    a_I, b_I       - initiative mods; init_adv = (a_base+a_I) - (b_base+b_I); >0 = A strikes first
    a_TH, b_TH     - to-hit mods (negative target = better; we report as "A hits harder" sign)
    a_TS, b_TS     - target-save mods (better save for that side)
And per column (defender tactic) it flags A's BEST RESPONSE (row maximizing a_win_rate).

Fall Back is excluded: its cells are mostly end=True (a disengage mechanic, not combat resolution);
forcing it just ends battles indecisively. Analyze it separately.

Run:
    python tactic_eval.py --runs 400
"""
import os, sys, argparse, itertools
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import numpy as np
import pandas as pd
import renown_combat as rc, vectorized_combat as vc, loadouts, batch_engine as be

TAC6 = ["Scout", "Ambush", "Flank", "Charge", "Fighting Formation", "Defensive Formation"]  # no Fall Back
TAC7 = TAC6 + ["Fall Back"]  # full grid incl. Fall Back (mostly end=True — disengage mechanic)


def statlines():
    """Representative builds spanning the stat space. Same gear axis so the TACTIC effect is isolated;
    the retinue stat differences (to_hit/shaking/endurance/unshakable) are what vary."""
    LD = loadouts.Loadout
    def mk(name, ret, weapon="Arming Sword", shield="Kite Shield", armor="Chainmail"):
        return LD(name=name, retinue=ret, weapon=weapon, shield=shield, armor=armor, ranged=None,
                  has_tiltyard=False, size=loadouts.DEFAULT_ARMY_SIZE, extra_tags=frozenset(),
                  upkeep_per_retinue=0, playstyle=None, tiltyard_mastery=False,
                  pursuits=frozenset(), military_pursuit_count=0, domain_count=0)
    return [
        mk("Levy (fragile)",     "Levy"),
        mk("Man-at-Arms (mid)",  "Man-at-Arms"),
        mk("Sergeant (elite)",   "Sergeant"),
        mk("Knight Templar (tank)", "Knight Templar"),
    ]


def mech_mods(a_tac, b_tac, a_base_init, b_base_init):
    """Deterministic mechanical effects of the tactic cell, read straight from TACTIC_MATRIX."""
    a_cell, b_cell = rc.TACTIC_MATRIX[(a_tac, b_tac)]
    a_I, a_TH, a_TS = a_cell["I"], a_cell["TH"], a_cell["TS"]
    b_I, b_TH, b_TS = b_cell["I"], b_cell["TH"], b_cell["TS"]
    init_adv = (a_base_init + a_I) - (b_base_init + b_I)   # >0 => A strikes first
    return dict(a_I=a_I, b_I=b_I, a_TH=a_TH, b_TH=b_TH, a_TS=a_TS, b_TS=b_TS,
                init_adv=init_adv,
                a_th_better=-a_TH, b_th_better=-b_TH,   # report so +1 = "hits harder" (lower target)
                a_save_better=a_TS, b_save_better=b_TS)


def base_init(build):
    """Approximate base initiative for the build (weapon+shield+armor init), for the strikes-first calc."""
    w = rc.WEAPONS.get(build.weapon, {}).get("init", 0)
    sh = rc.SHIELDS.get(build.shield, {}).get("init", 0)
    return w + sh


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "lab_out"))
    ap.add_argument("--runs", type=int, default=400)
    ap.add_argument("--include-fallback", action="store_true",
                    help="use the full 7x7 grid including Fall Back (shows the disengage bleed).")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    vc.invalidate_tactic_tables()

    GRID = TAC7 if args.include_fallback else TAC6

    rows = []
    for sl in statlines():
        bi = base_init(sl)
        for ai, a_tac in enumerate(GRID):
            for bi_, b_tac in enumerate(GRID):
                r = be.run_batch_random([(sl, sl)], n_runs=args.runs, seed=2026,
                                        mode="forced", force_a=ai, force_b=bi_)
                aw = int(r["a_wins"][0]); bw = int(r["b_wins"][0])
                mut = int(r["mut_wipe"][0]); ind = int(r["indecisive"][0])
                tot = max(1, aw + bw + mut + ind); dec = aw + bw
                a_killed = float(r["avg_a_killed_combat"][0] + r["avg_a_killed_shake"][0] + r["avg_a_killed_rout"][0])
                b_killed = float(r["avg_b_killed_combat"][0] + r["avg_b_killed_shake"][0] + r["avg_b_killed_rout"][0])
                m = mech_mods(a_tac, b_tac, bi, bi)
                rows.append({
                    "statline": sl.name, "a_tactic": a_tac, "b_tactic": b_tac,
                    "a_win_rate": aw / dec if dec else np.nan,
                    "win_rate_all": aw / tot,                  # counts mutual/indecisive as non-wins
                    "cas_diff": b_killed - a_killed,           # >0 = A favored
                    "decisive_rate": dec / tot,
                    "indecisive_rate": ind / tot,
                    "mutual_rate": mut / tot,
                    "a_survivors": float(r["avg_a_rem"][0]),
                    "avg_skirm": float(r["avg_skirm"][0]),
                    **m,
                })
    df = pd.DataFrame(rows)

    # Best-response flag: per (statline, b_tactic), which a_tactic maximizes a_win_rate.
    df["is_best_response"] = False
    for (sl, bt), grp in df.groupby(["statline", "b_tactic"]):
        idx = grp["a_win_rate"].idxmax()
        df.loc[idx, "is_best_response"] = True

    suffix = "_7x7" if args.include_fallback else ""
    df.to_csv(os.path.join(args.out, f"tactic_eval{suffix}.csv"), index=False)
    print(f"Wrote tactic_eval{suffix}.csv ({len(df)} cells = {df['statline'].nunique()} statlines "
          f"x {len(GRID)**2})\n")

    for sl in df["statline"].unique():
        sub = df[df["statline"] == sl]
        piv = sub.pivot(index="a_tactic", columns="b_tactic", values="a_win_rate").reindex(index=GRID, columns=GRID)
        print(f"=== {sl}: A win-rate by (row=A tactic, col=B tactic) ===")
        print(piv.round(2).to_string())
        rowmean = piv.mean(axis=1).round(3)
        best = rowmean.idxmax(); worst = rowmean.idxmin()
        print(f"  avg as A: {dict(rowmean)}")
        print(f"  strongest: {best} ({rowmean[best]:.2f}) | weakest: {worst} ({rowmean[worst]:.2f}) "
              f"| spread: {rowmean.max()-rowmean.min():.2f}\n")

    if args.include_fallback:
        print("=== Indecisive rate (Levy) — shows Fall Back ending battles ===")
        sub = df[df["statline"] == df["statline"].iloc[0]]
        piv = sub.pivot(index="a_tactic", columns="b_tactic", values="indecisive_rate").reindex(index=GRID, columns=GRID)
        print(piv.round(2).to_string(), "\n")

    print("Per-column best responses (does the right answer shift by statline?):")
    br = df[df["is_best_response"]].pivot(index="statline", columns="b_tactic", values="a_tactic").reindex(columns=GRID)
    print(br.to_string())

    # Mechanical breakdown: WHY the Defensive Formation column is punishing.
    print("\n=== Why the Defensive Formation column hurts attackers (mechanical mods, Levy) ===")
    sub = df[(df["statline"] == df["statline"].iloc[0]) & (df["b_tactic"] == "Defensive Formation")]
    cols = ["a_tactic", "a_win_rate", "init_adv", "a_th_better", "b_save_better", "cas_diff"]
    print("  (init_adv>0 = A strikes first; a_th_better>0 = A hits harder; b_save_better>0 = B saves better)")
    print(sub[cols].round(2).to_string(index=False))


if __name__ == "__main__":
    main()
