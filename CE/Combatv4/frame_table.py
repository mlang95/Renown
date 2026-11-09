"""Frame analysis: groups builds by fighting style (frame) instead of by item, from a finished tournament.

  python frame_table.py [run_dir]        (default: newest lab_out/d10_* with a summary_optimal.csv)

Tables:
  1. frame value at equal spend  - ctrl_prem by frame (same method as build_rank.attribute_table: win rate
     minus the pool's win rate in the same TI quartile, weighted by builds per quartile)
  2. frame ceiling               - best build per frame per TI quartile, and share of the top 10%
  3. frame vs frame              - mean win rate of the row frame against the column frame (matchups file)
Writes frame_*.csv next to the run.
"""
import os, sys, glob
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
CE = os.path.dirname(HERE)
sys.path.insert(0, CE); sys.path.insert(0, HERE)
import ce_paths; ce_paths.install(verbose=False)
import build_rank as BR

# Frames (user, Nov 9 2026). Florentine = actually Dual Wielding (the Florentine keyword alone only allows it);
# builds with no melee weapon = "Ranged Only".
FRAME_OF_WEAPON = {
    "Short Sword": "Sword & Board", "Arming Sword": "Sword & Board", "Bastard Sword": "Sword & Board",
    "Estoc": "Sword & Board",
    "2HBastard": "Shock Troops", "Battle Axe": "Shock Troops",
    "Flail": "Crowd Control", "Morningstar": "Crowd Control",
    "Bill Hook": "Polearms", "Halberd": "Polearms", "Poleaxe": "Polearms",
    "War Hammer": "War Hammer",
    "Spears": "Spears & Pikes", "2HSpears": "Spears & Pikes", "Pike": "Spears & Pikes",
    "Cavalry Spear": "Cavalry", "Lance": "Cavalry",
    "Farm Tools": "Chaff", "Cudgel": "Chaff", "Pitchfork": "Chaff", "Daggers": "Chaff",
}
ORDER = ["Sword & Board", "Florentine", "Shock Troops", "Crowd Control", "Polearms", "War Hammer",
         "Spears & Pikes", "Cavalry", "Chaff", "Ranged Only"]


def _has(col):
    return ~col.astype(str).str.strip().isin(["", "nan", "None"])


def frame(weapon, tags):
    if "dual wield" in str(tags).lower():
        return "Florentine"
    if weapon is None or (isinstance(weapon, float) and np.isnan(weapon)) or str(weapon) in ("", "None", "nan"):
        return "Ranged Only"
    return FRAME_OF_WEAPON.get(str(weapon), "Other")


def main():
    run = sys.argv[1] if len(sys.argv) > 1 else max(
        (d for d in glob.glob(os.path.join(CE, "lab_out", "d10_*")) if os.path.exists(os.path.join(d, "summary_optimal.csv"))),
        key=lambda d: os.path.getmtime(os.path.join(d, "summary_optimal.csv")))
    pd.set_option("display.width", 250)
    S = pd.read_csv(os.path.join(run, "summary_optimal.csv"))
    T = BR.builds(S)
    WR = BR.WR
    T["frame"] = [frame(w, t) for w, t in zip(S["weapon"], S["tags"])]
    T["_band"] = pd.qcut(T["ti"], 4, duplicates="drop")
    band_wr = T.groupby("_band", observed=True)[WR].mean()
    top_cut = T[WR].quantile(0.9)
    print(f"run: {os.path.basename(run)}  ({len(T)} builds)\n")

    rows = []
    for f in ORDER + ["Other"]:
        sub = T[T.frame == f]
        if sub.empty:
            continue
        num = den = 0.0
        for b, s in sub.groupby("_band", observed=True):
            num += len(s) * (s[WR].mean() - band_wr[b]); den += len(s)
        rows.append(dict(frame=f, n=len(sub), wr=sub[WR].mean(), ctrl_prem=num / den,
                         d_inv=sub["ti"].mean() - T["ti"].mean(),
                         top10_share=(sub[WR] >= top_cut).sum() / max(1, (T[WR] >= top_cut).sum()),
                         pool_share=len(sub) / len(T),
                         ranged_share=_has(sub["ranged"]).mean(), shield_share=_has(sub["shield"]).mean(),
                         weapons=", ".join(f"{w} {c}" for w, c in sub["weapon"].value_counts().items())))
    V = pd.DataFrame(rows)
    print("== 1. frame value at equal spend ==")
    print(V.round(3).to_string(index=False))

    C = T.pivot_table(index="frame", columns="_band", values=WR, aggfunc="max", observed=True)
    C = C.reindex([f for f in ORDER + ["Other"] if f in C.index])
    C.columns = [f"TI {c.left:.0f}-{c.right:.0f}" for c in C.columns]
    best = T.loc[T.groupby("frame")[WR].idxmax(), ["frame", "name", WR, "ti"]].set_index("frame").reindex(C.index)
    print("\n== 2. frame ceiling: best build win rate per TI quartile ==")
    print(C.round(3).to_string())
    print("\nbest build per frame:")
    print(best.round(3).to_string())

    M = pd.read_parquet(os.path.join(run, "matchups_optimal.parquet"),
                        columns=["a_weapon", "b_weapon", "a_tags", "b_tags", "a_wins", "b_wins", "mut_wipe", "indecisive"])
    n = (M.a_wins + M.b_wins + M.mut_wipe + M.indecisive).clip(lower=1)
    fa = [frame(w, t) for w, t in zip(M.a_weapon, M.a_tags)]
    fb = [frame(w, t) for w, t in zip(M.b_weapon, M.b_tags)]
    dec = (M.a_wins + M.b_wins).clip(lower=1)        # decisive share: draws left out, so a vs b + b vs a = 1
    D = pd.concat([pd.DataFrame({"me": fa, "op": fb, "wr": M.a_wins / n, "dw": M.a_wins / dec, "w": M.a_wins + M.b_wins}),
                   pd.DataFrame({"me": fb, "op": fa, "wr": M.b_wins / n, "dw": M.b_wins / dec, "w": M.a_wins + M.b_wins})], ignore_index=True)
    X = D.pivot_table(index="me", columns="op", values="wr", aggfunc="mean")
    keep = [f for f in ORDER + ["Other"] if f in X.index]
    X = X.reindex(index=keep, columns=keep)
    print("\n== 3. frame vs frame: win rate of row against column ==")
    print(X.round(2).to_string())

    # 4. rock-paper-scissors: strip out each frame's overall strength (logit win rate = a_row - a_col + r),
    #    what's left (r) is the matchup itself. + = row counters column beyond what strength explains.
    D["dww"] = D.dw * D.w
    G = D.groupby(["me", "op"])[["dww", "w"]].sum()
    XD = (G.dww / G.w).unstack().reindex(index=keep, columns=keep)
    L = np.log(XD.clip(0.01, 0.99) / (1 - XD.clip(0.01, 0.99)))
    strength = (L.mean(axis=1) - L.mean(axis=0)) / 2
    R = L.sub(strength, axis=0).add(strength, axis=1)
    R = (1 / (1 + np.exp(-R)) - 0.5)                 # back to win-rate points around an even match
    print("\n== 4. rock-paper-scissors: matchup edge left after overall strength (win-rate points) ==")
    print((R * 100).round(0).astype("Int64").to_string())
    pairs = [(a, b, R.loc[a, b]) for i, a in enumerate(keep) for b in keep[i + 1:] if pd.notna(R.loc[a, b])]
    pairs.sort(key=lambda t: -abs(t[2]))
    print("\nstrongest counters (row beats column more than strength says):")
    for a, b, v in pairs[:10]:
        w, l = (a, b) if v > 0 else (b, a)
        print(f"  {w:15s} > {l:15s} {abs(v) * 100:4.1f} pts")
    loops = []
    for i, a in enumerate(keep):
        for j, b in enumerate(keep):
            for c in keep:
                if len({a, b, c}) == 3 and i < j and R.loc[a, b] > 0.02 and R.loc[b, c] > 0.02 and R.loc[c, a] > 0.02:
                    loops.append((a, b, c, min(R.loc[a, b], R.loc[b, c], R.loc[c, a])))
    loops = sorted({tuple(sorted(l[:3])): l for l in loops}.values(), key=lambda l: -l[3])
    print("\ncounter loops (each beats the next by > 2 pts beyond strength):", "none" if not loops else "")
    for a, b, c, m in loops[:10]:
        print(f"  {a} > {b} > {c} > {a}   (weakest link {m * 100:.1f} pts)")
    R.to_csv(os.path.join(run, "frame_rps.csv"))

    V.to_csv(os.path.join(run, "frame_value.csv"), index=False)
    C.join(best).to_csv(os.path.join(run, "frame_ceiling.csv"))
    X.to_csv(os.path.join(run, "frame_matrix.csv"))
    print(f"\n-> {run}\\frame_*.csv")


if __name__ == "__main__":
    main()
