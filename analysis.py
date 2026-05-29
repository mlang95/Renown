"""
Analysis module for tournament results.

Reads matchups.csv and computes:
- Modified upkeep (assumes player has all upkeep-reducing specs along the pathway)
- Spoils of War per cost
- Punch-above-weight rate
- Mirror matchups (same retinue, same equipment, etc.)
- Durability, kill power, battle efficiency, crush rate, stalemate rate, robustness
- Counters

All upkeep-based metrics use MODIFIED upkeep by default. Base upkeep is preserved
as a_upkeep_base / b_upkeep_base for comparison.
"""

import pandas as pd
import numpy as np
from renown_combat import RETINUES


# ==============================================================================
# UPKEEP REDUCTIONS FROM SPECIALIZATIONS
# ==============================================================================
# Assumes player has built every upkeep-reducing spec along the pathway.
# Generic reductions apply to all retinues (per-retinue). Equipment reductions
# apply only if the relevant equipment is in the loadout.

# Generic Upkeep -5 specializations (stack additively).
# Levy Hall innate (in-province) and mastery (out-of-province) don't stack —
# they apply in different contexts. Default assumes in-province (innate).
GENERIC_UPKEEP_REDUCTIONS = [
    ("Butchery (mastery)",            5),
    ("Tannery (mastery)",             5),
    ("Armory (mastery)",              5),
    ("Master Workshop (innate)",      5),
    ("Gilded Foundry (innate)",       5),
    ("Smokehouse (mastery)",          5),
    ("Levy Hall (innate)",            5),  # in-province; swap to mastery for out-of-province
    ("Advanced Blast Furnaces (innate)", 5),
]
GENERIC_UPKEEP_TOTAL = sum(r for _, r in GENERIC_UPKEEP_REDUCTIONS)  # 40

# Equipment-conditional (Maintain X -5):
LANCE_REDUCTION       = 5    # Saddlery mastery — if weapon == Lance
SHIELD_REDUCTION      = 5    # Joinery mastery — if any shield
LIGHT_ARMOR_REDUCTION = 5    # Tannery innate — Cloth, Leather
HEAVY_ARMOR_REDUCTION = 5    # Armory innate — Chainmail, Full Plate, Gothic Plate
RANGED_REDUCTION      = 5    # Fletchery mastery — if ranged equipped (incl. Tiltyard dual-equip)

LIGHT_ARMORS = {"Cloth", "Leather"}
HEAVY_ARMORS = {"Chainmail", "Full Plate", "Gothic Plate"}


def _is_set(val):
    """Robust check for non-empty equipment field (handles None, '', 'nan')."""
    if val is None:
        return False
    s = str(val).strip()
    return s not in ("", "nan", "None")


def compute_per_retinue_upkeep(retinue, weapon, shield, armor, ranged):
    """Modified upkeep per retinue, applying all relevant spec reductions.
    Clamped at 0 (a retinue cannot have negative upkeep)."""
    base = RETINUES[retinue]["cost"]
    reduction = GENERIC_UPKEEP_TOTAL

    if weapon == "Lance":
        reduction += LANCE_REDUCTION
    if _is_set(shield):
        reduction += SHIELD_REDUCTION
    if armor in LIGHT_ARMORS:
        reduction += LIGHT_ARMOR_REDUCTION
    if armor in HEAVY_ARMORS:
        reduction += HEAVY_ARMOR_REDUCTION
    if _is_set(ranged):
        reduction += RANGED_REDUCTION

    return max(0, base - reduction)


def upkeep_sources(retinue, weapon, shield, armor, ranged):
    """Return a list of (source, amount) tuples describing all upkeep reductions for a loadout.
    Useful for surfacing 'where' the per-retinue savings come from in a structured way.
    """
    sources = []
    for name, val in GENERIC_UPKEEP_REDUCTIONS:
        sources.append((name, val))
    if weapon == "Lance":
        sources.append(("Saddlery (mastery, Lance)", LANCE_REDUCTION))
    if _is_set(shield):
        sources.append((f"Joinery (mastery, {shield})", SHIELD_REDUCTION))
    if armor in LIGHT_ARMORS:
        sources.append((f"Tannery (innate, {armor})", LIGHT_ARMOR_REDUCTION))
    if armor in HEAVY_ARMORS:
        sources.append((f"Armory (innate, {armor})", HEAVY_ARMOR_REDUCTION))
    if _is_set(ranged):
        sources.append((f"Fletchery (mastery, {ranged})", RANGED_REDUCTION))
    return sources


def upkeep_breakdown(retinue, weapon, shield, armor, ranged):
    """Show how a loadout's modified upkeep is computed. Useful for sanity checks."""
    base = RETINUES[retinue]["cost"]
    lines = [f"Base ({retinue}): {base}"]
    total = 0
    for source, val in upkeep_sources(retinue, weapon, shield, armor, ranged):
        lines.append(f"  -{val}  {source}")
        total += val
    modified = max(0, base - total)
    lines.append(f"Total reduction: -{total}")
    lines.append(f"Modified per-retinue upkeep: {modified}  (base was {base})")
    return "\n".join(lines)


# ==============================================================================
# LOAD TOURNAMENT
# ==============================================================================

def load_tournament(matchups_path="matchups.csv", encoding="utf-8"):
    """Load matchups CSV with derived columns:
      - a_ret_cost / b_ret_cost: base per-retinue cost
      - a_ret_cost_modified / b_ret_cost_modified: after spec reductions
      - a_upkeep_base / b_upkeep_base: size × base
      - a_upkeep / b_upkeep: size × MODIFIED (this is what analyses use)
      - casualties, spoils, win rates

    Tries the given encoding first, falls back to cp1252 (Excel-saved CSVs)."""
    try:
        df = pd.read_csv(matchups_path, encoding=encoding)
    except UnicodeDecodeError:
        df = pd.read_csv(matchups_path, encoding="cp1252")

    df["a_tags"] = df["a_tags"].fillna("")
    df["b_tags"] = df["b_tags"].fillna("")
    df["a_shield"] = df["a_shield"].fillna("")
    df["b_shield"] = df["b_shield"].fillna("")
    df["a_ranged"] = df["a_ranged"].fillna("")
    df["b_ranged"] = df["b_ranged"].fillna("")
    # Playstyle column is new; older CSVs won't have it
    if "a_playstyle" not in df.columns:
        df["a_playstyle"] = "Random"
    else:
        df["a_playstyle"] = df["a_playstyle"].fillna("Random")
    if "b_playstyle" not in df.columns:
        df["b_playstyle"] = "Random"
    else:
        df["b_playstyle"] = df["b_playstyle"].fillna("Random")

    # Shield destruction columns are new; older CSVs won't have them
    if "a_shield_destroyed_rate" not in df.columns:
        df["a_shield_destroyed_rate"] = 0.0
    if "b_shield_destroyed_rate" not in df.columns:
        df["b_shield_destroyed_rate"] = 0.0

    df["a_ret_cost"] = df["a_retinue"].map(lambda r: RETINUES[r]["cost"])
    df["b_ret_cost"] = df["b_retinue"].map(lambda r: RETINUES[r]["cost"])

    df["a_ret_cost_modified"] = df.apply(
        lambda r: compute_per_retinue_upkeep(r["a_retinue"], r["a_weapon"], r["a_shield"], r["a_armor"], r["a_ranged"]),
        axis=1,
    )
    df["b_ret_cost_modified"] = df.apply(
        lambda r: compute_per_retinue_upkeep(r["b_retinue"], r["b_weapon"], r["b_shield"], r["b_armor"], r["b_ranged"]),
        axis=1,
    )

    df["a_upkeep_base"] = df["a_size"] * df["a_ret_cost"]
    df["b_upkeep_base"] = df["b_size"] * df["b_ret_cost"]
    df["a_upkeep"] = df["a_size"] * df["a_ret_cost_modified"]   # modified by default
    df["b_upkeep"] = df["b_size"] * df["b_ret_cost_modified"]

    df["a_killed"] = df["a_size"] - df["avg_a_rem"]
    df["b_killed"] = df["b_size"] - df["avg_b_rem"]

    df["n_runs"] = df["a_wins"] + df["b_wins"] + df["mut_wipe"] + df["indecisive"]
    df["a_win_rate"] = df["a_wins"] / df["n_runs"]
    df["b_win_rate"] = df["b_wins"] / df["n_runs"]

    # Spoils of War uses BASE cost: when you destroy a retinue you extort its raw cost,
    # not what someone else paid in upkeep with their specs.
    df["a_spoils_per_battle"] = df["b_killed"] * df["b_ret_cost"]
    df["b_spoils_per_battle"] = df["a_killed"] * df["a_ret_cost"]

    return df


# ==============================================================================
# Module-level aggregators (pandas version-proof)
# ==============================================================================

def _punch_agg(g):
    return pd.Series({
        "punch_wins":       int(g["a_wins"].sum()),
        "punch_losses":     int(g["b_wins"].sum()),
        "punch_indecisive": int(g["indecisive"].sum()),
        "punch_battles":    int(g["n_runs"].sum()),
        "n_richer_opps":    len(g),
        "avg_cost_ratio":   (g["b_upkeep"] / g["a_upkeep"].replace(0, np.nan)).mean(),
        "a_upkeep":         g["a_upkeep"].iloc[0],
    })


def _crush_agg(g):
    return pd.Series({
        "total_wins":               int(g["a_wins"].sum()),
        "weighted_avg_rem_in_wins": (g["weighted_rem"].sum() / max(1, g["a_wins"].sum())),
        "a_size":                   g["a_size"].iloc[0],
    })


# ==============================================================================
# 1. Spoils of War per cost
# ==============================================================================

def spoils_efficiency(df):
    """Avg Spoils per gold of MODIFIED upkeep. Higher = better gold-engine via warfare.
    Loadouts with 0 modified upkeep get NaN (can't divide); reported separately at top."""
    df = df[df["a_name"] != df["b_name"]].copy()
    grp = df.groupby("a_name").agg(
        avg_spoils=("a_spoils_per_battle", "mean"),
        a_upkeep=("a_upkeep", "first"),
        a_upkeep_base=("a_upkeep_base", "first"),
        a_retinue=("a_retinue", "first"),
        a_weapon=("a_weapon", "first"),
        a_armor=("a_armor", "first"),
        n_opponents=("b_name", "count"),
    ).reset_index()
    grp["spoils_per_upkeep"] = grp["avg_spoils"] / grp["a_upkeep"].replace(0, np.nan)
    return grp.sort_values("spoils_per_upkeep", ascending=False, na_position="first")


# ==============================================================================
# 2. Punch above weight (uses MODIFIED upkeep)
# ==============================================================================

def punch_above_weight(df, cost_threshold_ratio=1.2):
    """Win rate vs opponents with at least cost_threshold_ratio × your modified upkeep.
    Excludes loadouts with 0 modified upkeep (can't form a meaningful ratio)."""
    df = df[df["a_name"] != df["b_name"]].copy()
    df = df[df["a_upkeep"] > 0]
    df = df[df["b_upkeep"] >= df["a_upkeep"] * cost_threshold_ratio]
    if len(df) == 0:
        return pd.DataFrame(columns=["a_name", "punch_win_rate", "n_richer_opps", "avg_cost_ratio"])
    cols = ["a_wins", "b_wins", "indecisive", "n_runs", "b_upkeep", "a_upkeep"]
    grp = df.groupby("a_name")[cols].apply(_punch_agg).reset_index()
    grp["punch_win_rate"] = grp["punch_wins"] / grp["punch_battles"]
    return grp.sort_values("punch_win_rate", ascending=False)


# ==============================================================================
# 3. Mirror matchups
# ==============================================================================

def mirror_matchups(df, key_cols):
    mask = pd.Series(True, index=df.index)
    for col in key_cols:
        mask &= (df[f"a_{col}"] == df[f"b_{col}"])
    return df[mask & (df["a_name"] != df["b_name"])].copy()


def mirror_winners(df, key_cols, top_n=15):
    sub = mirror_matchups(df, key_cols)
    if len(sub) == 0:
        return pd.DataFrame()
    grp = sub.groupby("a_name").agg(
        wins=("a_wins", "sum"),
        losses=("b_wins", "sum"),
        indec=("indecisive", "sum"),
        battles=("n_runs", "sum"),
        n_matchups=("b_name", "count"),
    ).reset_index()
    grp["win_rate"] = grp["wins"] / grp["battles"]
    grp["decisive_win_rate"] = grp["wins"] / (grp["wins"] + grp["losses"] + 1)
    return grp.sort_values("win_rate", ascending=False).head(top_n)


# ==============================================================================
# 4. Durability
# ==============================================================================

def durability(df):
    df = df[df["a_name"] != df["b_name"]].copy()
    df["a_survival_rate"] = df["avg_a_rem"] / df["a_size"]
    grp = df.groupby("a_name").agg(
        avg_survival_rate=("a_survival_rate", "mean"),
        avg_self_survivors=("avg_a_rem", "mean"),
        a_size=("a_size", "first"),
        a_retinue=("a_retinue", "first"),
        a_armor=("a_armor", "first"),
        a_weapon=("a_weapon", "first"),
    ).reset_index()
    return grp.sort_values("avg_survival_rate", ascending=False)


# ==============================================================================
# 5. Kill power
# ==============================================================================

def kill_power(df):
    df = df[df["a_name"] != df["b_name"]].copy()
    df["kill_rate"] = df["b_killed"] / df["b_size"]
    grp = df.groupby("a_name").agg(
        avg_kills=("b_killed", "mean"),
        avg_kill_rate=("kill_rate", "mean"),
        a_retinue=("a_retinue", "first"),
        a_weapon=("a_weapon", "first"),
    ).reset_index()
    return grp.sort_values("avg_kills", ascending=False)


# ==============================================================================
# 6. Battle efficiency (per-1k uses MODIFIED upkeep)
# ==============================================================================

def battle_efficiency(df):
    df = df[df["a_name"] != df["b_name"]].copy()
    df["kill_diff"] = df["b_killed"] - df["a_killed"]
    grp = df.groupby("a_name").agg(
        avg_kill_diff=("kill_diff", "mean"),
        avg_kills=("b_killed", "mean"),
        avg_losses=("a_killed", "mean"),
        a_retinue=("a_retinue", "first"),
        a_upkeep=("a_upkeep", "first"),
        a_upkeep_base=("a_upkeep_base", "first"),
    ).reset_index()
    grp["kill_diff_per_1k_upkeep"] = grp["avg_kill_diff"] / (grp["a_upkeep"].replace(0, np.nan) / 1000)
    return grp.sort_values("avg_kill_diff", ascending=False)


# ==============================================================================
# 7. Crush rate
# ==============================================================================

def crush_rate(df):
    df = df[df["a_name"] != df["b_name"]].copy()
    df = df[df["a_wins"] > 0]
    if len(df) == 0:
        return pd.DataFrame()
    df["weighted_rem"] = df["avg_a_rem"] * df["a_wins"]
    cols = ["a_wins", "weighted_rem", "a_size"]
    grp = df.groupby("a_name")[cols].apply(_crush_agg).reset_index()
    grp["crush_score"] = grp["weighted_avg_rem_in_wins"] / grp["a_size"]
    return grp.sort_values("crush_score", ascending=False)


# ==============================================================================
# 8. Stalemate rate
# ==============================================================================

def stalemate_rate(df):
    df = df[df["a_name"] != df["b_name"]].copy()
    grp = df.groupby("a_name").agg(
        indec=("indecisive", "sum"),
        total=("n_runs", "sum"),
        a_retinue=("a_retinue", "first"),
        a_armor=("a_armor", "first"),
        a_weapon=("a_weapon", "first"),
    ).reset_index()
    grp["stalemate_rate"] = grp["indec"] / grp["total"]
    return grp.sort_values("stalemate_rate", ascending=False)


# ==============================================================================
# 9. Robustness
# ==============================================================================

def robustness(df):
    df = df[df["a_name"] != df["b_name"]].copy()
    grp = df.groupby("a_name").agg(
        mean_win_rate=("a_win_rate", "mean"),
        std_win_rate=("a_win_rate", "std"),
        min_win_rate=("a_win_rate", "min"),
        max_win_rate=("a_win_rate", "max"),
        n_opps=("b_name", "count"),
    ).reset_index()
    grp["robustness_score"] = grp["mean_win_rate"] - grp["std_win_rate"]
    return grp.sort_values("robustness_score", ascending=False)


# ==============================================================================
# 10. Counters
# ==============================================================================

def counters_for(df, target_name, top_n=10):
    sub = df[df["b_name"] == target_name].copy()
    sub = sub[sub["a_name"] != sub["b_name"]]
    sub = sub.sort_values("a_win_rate", ascending=False).head(top_n)
    return sub[["a_name", "a_wins", "b_wins", "indecisive", "a_win_rate",
                "avg_skirm", "avg_a_rem", "avg_b_rem"]]


# ==============================================================================
# 11. Composite dashboard
# ==============================================================================

def composite_dashboard(df, top_n=20):
    spoils = spoils_efficiency(df).set_index("a_name")[["spoils_per_upkeep", "a_upkeep", "a_upkeep_base"]]
    dur = durability(df).set_index("a_name")[["avg_survival_rate"]]
    kill = kill_power(df).set_index("a_name")[["avg_kills"]]
    eff = battle_efficiency(df).set_index("a_name")[["avg_kill_diff", "kill_diff_per_1k_upkeep"]]
    robust = robustness(df).set_index("a_name")[["mean_win_rate", "std_win_rate"]]
    stale = stalemate_rate(df).set_index("a_name")[["stalemate_rate"]]
    out = robust.join([spoils, dur, kill, eff, stale])
    out["punch_score"] = out["mean_win_rate"] * out["spoils_per_upkeep"] * 10
    return out.sort_values("mean_win_rate", ascending=False).head(top_n)


# ==============================================================================
# 12. Upkeep comparison table
# ==============================================================================

def upkeep_comparison(df, include_sources=True):
    """Per loadout: base vs modified upkeep, savings, % reduction.
    If include_sources=True, adds a 'sources' column listing where each reduction comes from
    and an 'n_sources' column for the count.
    """
    df = df[df["a_name"] != df["b_name"]].copy()
    grp = df.groupby("a_name").agg(
        a_retinue=("a_retinue", "first"),
        a_weapon=("a_weapon", "first"),
        a_shield=("a_shield", "first"),
        a_armor=("a_armor", "first"),
        a_ranged=("a_ranged", "first"),
        a_size=("a_size", "first"),
        a_ret_cost=("a_ret_cost", "first"),
        a_ret_cost_modified=("a_ret_cost_modified", "first"),
        a_upkeep_base=("a_upkeep_base", "first"),
        a_upkeep_modified=("a_upkeep", "first"),
    ).reset_index()
    grp["upkeep_savings"] = grp["a_upkeep_base"] - grp["a_upkeep_modified"]
    grp["upkeep_pct_reduction"] = grp["upkeep_savings"] / grp["a_upkeep_base"]

    if include_sources:
        def _sources_str(row):
            srcs = upkeep_sources(row["a_retinue"], row["a_weapon"], row["a_shield"],
                                  row["a_armor"], row["a_ranged"])
            return "; ".join(f"{name} −{val}" for name, val in srcs)
        def _n_sources(row):
            return len(upkeep_sources(row["a_retinue"], row["a_weapon"], row["a_shield"],
                                       row["a_armor"], row["a_ranged"]))
        grp["sources"] = grp.apply(_sources_str, axis=1)
        grp["n_sources"] = grp.apply(_n_sources, axis=1)

    return grp.sort_values("upkeep_pct_reduction", ascending=False)


# ==============================================================================
# Print helper
# ==============================================================================

def print_summary(df, n=10):
    print("=" * 80)
    print("TOURNAMENT ANALYSIS SUMMARY  (modified upkeep)")
    print("=" * 80)

    print("\n[1] SPOILS OF WAR PER MODIFIED UPKEEP")
    s = spoils_efficiency(df).head(n)
    for _, row in s.iterrows():
        spu = f"{row['spoils_per_upkeep']:>6.3f}" if pd.notna(row['spoils_per_upkeep']) else "   inf"
        print(f"  {row['a_name']:<48} {spu}  "
              f"(spoils {row['avg_spoils']:>6.0f} | upkeep mod {row['a_upkeep']:>4.0f} / base {row['a_upkeep_base']:>4.0f})")

    print("\n[2] PUNCH ABOVE WEIGHT (vs 20%+ more expensive, MODIFIED)")
    pw = punch_above_weight(df).head(n)
    for _, row in pw.iterrows():
        print(f"  {row['a_name']:<48} {row['punch_win_rate']:>5.1%}  "
              f"(vs avg {row['avg_cost_ratio']:.2f}x cost, {int(row['n_richer_opps']):>3} opps)")

    print("\n[3] DURABILITY")
    d = durability(df).head(n)
    for _, row in d.iterrows():
        print(f"  {row['a_name']:<48} {row['avg_survival_rate']:>5.1%}  "
              f"(avg {row['avg_self_survivors']:>5.1f}/{int(row['a_size'])})")

    print("\n[4] KILL POWER")
    k = kill_power(df).head(n)
    for _, row in k.iterrows():
        print(f"  {row['a_name']:<48} {row['avg_kills']:>5.1f}")

    print("\n[5] BATTLE EFFICIENCY (per-1k uses MODIFIED upkeep)")
    eff = battle_efficiency(df).head(n)
    for _, row in eff.iterrows():
        ratio = f"{row['kill_diff_per_1k_upkeep']:>+5.1f}" if pd.notna(row['kill_diff_per_1k_upkeep']) else "   inf"
        print(f"  {row['a_name']:<48} {row['avg_kill_diff']:>+5.1f}  "
              f"(kills {row['avg_kills']:>5.1f} - losses {row['avg_losses']:>5.1f}; "
              f"{ratio}/1k upkeep)")

    print("\n[6] MIRROR (same retinue)")
    m = mirror_winners(df, ["retinue"], top_n=n)
    for _, row in m.iterrows():
        print(f"  {row['a_name']:<48} {row['win_rate']:>5.1%}  "
              f"(wins {int(row['wins'])} / battles {int(row['battles'])})")

    print("\n[7] MIRROR (same armor)")
    m = mirror_winners(df, ["armor"], top_n=n)
    for _, row in m.iterrows():
        print(f"  {row['a_name']:<48} {row['win_rate']:>5.1%}")

    print("\n[8] MIRROR (same weapon)")
    m = mirror_winners(df, ["weapon"], top_n=n)
    for _, row in m.iterrows():
        print(f"  {row['a_name']:<48} {row['win_rate']:>5.1%}")

    print("\n[9] STALEMATE RATE")
    s = stalemate_rate(df).head(n)
    for _, row in s.iterrows():
        print(f"  {row['a_name']:<48} {row['stalemate_rate']:>5.1%}")

    print("\n[10] ROBUSTNESS")
    r = robustness(df).head(n)
    for _, row in r.iterrows():
        print(f"  {row['a_name']:<48} score {row['robustness_score']:>+.3f}  "
              f"(mean {row['mean_win_rate']:.1%} +- {row['std_win_rate']:.1%})")

    print("\n[11] UPKEEP SAVINGS (largest % reductions from spec maintenance)")
    u = upkeep_comparison(df).head(n)
    for _, row in u.iterrows():
        print(f"  {row['a_name']:<48} base {int(row['a_upkeep_base']):>5} -> mod {int(row['a_upkeep_modified']):>5} "
              f"(-{int(row['upkeep_savings']):>4}, {row['upkeep_pct_reduction']:>5.1%})")


def skirmish_length(df):
    """Per-loadout average skirmish count across all battles.
    Short skirmish counts = high lethality (wipe fast). Long = attrition / defensive armies.
    """
    df = df[df["a_name"] != df["b_name"]].copy()
    grp = df.groupby("a_name").agg(
        avg_skirmishes=("avg_skirm", "mean"),
        min_skirmishes=("avg_skirm", "min"),
        max_skirmishes=("avg_skirm", "max"),
        a_retinue=("a_retinue", "first"),
        a_weapon=("a_weapon", "first"),
        a_armor=("a_armor", "first"),
    ).reset_index()
    return grp.sort_values("avg_skirmishes", ascending=False)


def _rout_col(df, side, kind):
    """Return the right column name for rout casualties — 'rout' (new) or 'flee' (legacy)."""
    new = f"avg_{side}_killed_rout"
    old = f"avg_{side}_killed_flee"
    return new if new in df.columns else old


def _wipe_rout_col(df, side):
    new = f"{side}_wipe_rout"
    old = f"{side}_wipe_flee"
    return new if new in df.columns else old


def casualty_sources(df):
    """Per-loadout: where do their casualties come from?
    Each row: avg combat / shake / rout casualties per battle as A, with %.
    Useful to identify loadouts that are rout-prone (and thus benefit massively from Steadfast).
    """
    df = df[df["a_name"] != df["b_name"]].copy()
    rout_col = _rout_col(df, "a", "killed")
    grp = df.groupby("a_name").agg(
        avg_combat_cas=("avg_a_killed_combat", "mean"),
        avg_shake_cas=("avg_a_killed_shake", "mean"),
        avg_rout_cas=(rout_col, "mean"),
        a_retinue=("a_retinue", "first"),
        a_armor=("a_armor", "first"),
        a_weapon=("a_weapon", "first"),
        a_tags=("a_tags", "first"),
    )
    grp["total_cas"] = grp["avg_combat_cas"] + grp["avg_shake_cas"] + grp["avg_rout_cas"]
    grp["pct_combat"] = (grp["avg_combat_cas"] / grp["total_cas"].replace(0, 1) * 100)
    grp["pct_shake"]  = (grp["avg_shake_cas"]  / grp["total_cas"].replace(0, 1) * 100)
    grp["pct_rout"]   = (grp["avg_rout_cas"]   / grp["total_cas"].replace(0, 1) * 100)
    return grp.sort_values("pct_rout", ascending=False)


def wipe_causes(df):
    """Per-loadout: when this loadout's armies get wiped, what's the cause?
    Helps identify which builds die to fatigue (rout) vs which die to combat.
    A high rout% means Steadfast would substantially improve survival.
    """
    df = df[df["a_name"] != df["b_name"]].copy()
    rout_col = _wipe_rout_col(df, "a")
    grp = df.groupby("a_name").agg(
        wipes_combat=("a_wipe_combat", "sum"),
        wipes_shake=("a_wipe_shake", "sum"),
        wipes_rout=(rout_col, "sum"),
        a_retinue=("a_retinue", "first"),
        a_armor=("a_armor", "first"),
        a_weapon=("a_weapon", "first"),
        a_tags=("a_tags", "first"),
    )
    grp["total_wipes"] = grp["wipes_combat"] + grp["wipes_shake"] + grp["wipes_rout"]
    grp["pct_combat"] = (grp["wipes_combat"] / grp["total_wipes"].replace(0, 1) * 100)
    grp["pct_shake"]  = (grp["wipes_shake"]  / grp["total_wipes"].replace(0, 1) * 100)
    grp["pct_rout"]   = (grp["wipes_rout"]   / grp["total_wipes"].replace(0, 1) * 100)
    return grp.sort_values("pct_rout", ascending=False)


def shaking_impact(df):
    """Quantify when shaking actually matters.
    For each loadout: what's the typical shake damage when it triggers, and what % of battles
    does shake fire at all? Most interesting for armies with high shaking values (Levy/MaA).

    Returns per-loadout:
      pct_battles_with_shake: % of matchups where shake casualties > 0
      avg_shake_when_triggered: avg shake damage in those matchups
      avg_shake_overall: avg across ALL matchups (counts 0s)
      steadfast_value: average shake casualties = the per-battle gain from adding Steadfast
                       (since Steadfast prevents shaking entirely)
    """
    df = df[df["a_name"] != df["b_name"]].copy()
    rows = []
    for name, group in df.groupby("a_name"):
        with_shake = group[group["avg_a_killed_shake"] > 0]
        rows.append({
            "a_name": name,
            "a_retinue": group["a_retinue"].iloc[0],
            "a_weapon": group["a_weapon"].iloc[0],
            "a_armor": group["a_armor"].iloc[0],
            "a_tags": group["a_tags"].iloc[0],
            "pct_battles_with_shake": (group["avg_a_killed_shake"] > 0).sum() / len(group) * 100,
            "avg_shake_when_triggered": float(with_shake["avg_a_killed_shake"].mean()) if len(with_shake) else 0.0,
            "avg_shake_overall": float(group["avg_a_killed_shake"].mean()),
            "max_shake_per_battle": float(group["avg_a_killed_shake"].max()),
            "steadfast_retinue_savings": float(group["avg_a_killed_shake"].mean()),  # implied per-battle save
        })
    import pandas as pd
    return pd.DataFrame(rows).sort_values("steadfast_retinue_savings", ascending=False)


def shaking_by_retinue(df):
    """Aggregate shake impact by retinue tier.
    Shows how much per-battle damage each retinue tier takes from shaking on average.
    Translates directly into 'what does Steadfast save you?'.
    """
    df = df[df["a_name"] != df["b_name"]].copy()
    import pandas as pd
    grp = df.groupby("a_retinue").agg(
        n_matchups=("avg_a_killed_shake", "count"),
        avg_shake_per_battle=("avg_a_killed_shake", "mean"),
        max_shake=("avg_a_killed_shake", "max"),
        pct_with_shake=("avg_a_killed_shake", lambda x: (x > 0).sum() / len(x) * 100),
        total_shake_cas=("avg_a_killed_shake", "sum"),
    )
    # Look up retinue stats
    grp["base_size"] = 50  # standard pool size
    grp["shake_cas_pct_of_army"] = grp["avg_shake_per_battle"] / grp["base_size"] * 100
    return grp.sort_values("avg_shake_per_battle", ascending=False)


# ==============================================================================
# Playstyle analysis — for tournaments run with multiple playstyles per loadout
# ==============================================================================

def shaking_deep_dive(df):
    """When is shaking most potent? Per-matchup analysis showing the conditions
    under which shake casualties are highest.

    Outputs three groupings:
    1. By a_retinue + b_retinue: how does shake depend on opponent tier?
    2. By a_weapon (own weapon): does the weapon you're holding affect your shake exposure?
       (Yes — slow weapons fatigue you faster because they take more skirmishes to win.)
    3. By a_armor: armor doesn't prevent shake directly but extends battle length.
    """
    import pandas as pd
    sub = df[df["a_name"] != df["b_name"]].copy()

    by_pair = sub.groupby(["a_retinue", "b_retinue"]).agg(
        n=("avg_a_killed_shake", "count"),
        avg_shake=("avg_a_killed_shake", "mean"),
        avg_skirm=("avg_skirm", "mean"),
    ).sort_values("avg_shake", ascending=False)

    by_weapon = sub.groupby(["a_retinue", "a_weapon"]).agg(
        n=("avg_a_killed_shake", "count"),
        avg_shake=("avg_a_killed_shake", "mean"),
        avg_skirm=("avg_a_killed_shake", "mean"),
    ).sort_values("avg_shake", ascending=False)

    return {"by_pair": by_pair, "by_weapon": by_weapon}


def shaking_threshold_analysis(df):
    """Identify the threshold conditions where shaking shifts from negligible to severe.
    Bins battles by length (avg_skirm) and shows shake casualties at each bin.
    """
    import pandas as pd
    sub = df[df["a_name"] != df["b_name"]].copy()
    sub["skirm_bin"] = pd.cut(sub["avg_skirm"], bins=[0, 2, 3, 4, 5, 6, 7, 10, 20],
                              labels=["<2", "2-3", "3-4", "4-5", "5-6", "6-7", "7-10", "10+"])
    rout_col = _rout_col(df, "a", "killed")
    grp = sub.groupby(["a_retinue", "skirm_bin"], observed=True).agg(
        n=("avg_a_killed_shake", "count"),
        avg_shake=("avg_a_killed_shake", "mean"),
        avg_rout=(rout_col, "mean"),
        avg_combat=("avg_a_killed_combat", "mean"),
    )
    return grp.sort_values(["a_retinue", "skirm_bin"])


def steadfast_gold_value(df, retinue_size=50):
    """Estimate the gold value of Steadfast per battle for each retinue.
    Steadfast prevents Army Rout (to-hit modified to 7+). It does NOT prevent shake —
    only Unshakable does. So Steadfast's value = avg Rout casualties saved × retinue cost.
    """
    import pandas as pd
    sub = df[df["a_name"] != df["b_name"]].copy()
    # Exclude loadouts that already have Steadfast
    sub["a_tags"] = sub["a_tags"].fillna("").astype(str)
    sub = sub[~sub["a_tags"].str.contains("Steadfast", na=False, regex=False)]
    sub = sub[sub["a_retinue"] != "Knight Templar"]  # KT is Unshakable

    rout_col = _rout_col(df, "a", "killed")
    grp = sub.groupby("a_retinue").agg(
        avg_rout=(rout_col, "mean"),
        avg_shake=("avg_a_killed_shake", "mean"),
        n=(rout_col, "count"),
    )
    grp["ret_cost"] = grp.index.map(lambda r: RETINUES[r]["cost"])
    # Steadfast value = rout casualties saved × retinue cost
    grp["steadfast_value_per_battle"] = grp["avg_rout"] * grp["ret_cost"]
    grp["steadfast_value_pct_of_army"] = grp["avg_rout"] / retinue_size * 100
    return grp


def playstyle_win_rates(df, n_runs_per_matchup=None):
    """For each (equipment-loadout, playstyle) pair, compute the average win rate.
    Returns DataFrame indexed by (equipment_key, playstyle).
    """
    if n_runs_per_matchup is None:
        from_df = df[df["a_name"] != df["b_name"]] if "a_name" in df.columns else df
        per_row = from_df["a_wins"] + from_df["b_wins"] + from_df["mut_wipe"] + from_df["indecisive"]
        n_runs_per_matchup = int(per_row.mode().iloc[0]) if len(per_row) else 100
    sub = df[df["a_name"] != df["b_name"]].copy()
    # Equipment key = everything except playstyle
    sub["a_equip"] = (sub["a_retinue"] + "|" + sub["a_weapon"] + "|" +
                     sub["a_shield"].fillna("") + "|" + sub["a_armor"] + "|" +
                     sub["a_ranged"].fillna("") + "|" + sub["a_tags"].fillna(""))
    grp = sub.groupby(["a_equip", "a_playstyle"]).agg(
        wins=("a_wins", "sum"),
        losses=("b_wins", "sum"),
        mut_wipe=("mut_wipe", "sum"),
        indecisive=("indecisive", "sum"),
        n_matchups=("a_wins", "count"),
        survival=("avg_a_rem", "mean"),
        avg_skirm=("avg_skirm", "mean"),
        rout_wipes=(_wipe_rout_col(df, "a"), "sum"),
        combat_wipes=("a_wipe_combat", "sum"),
    )
    grp["total_battles"] = grp["n_matchups"] * n_runs_per_matchup
    grp["win_rate"] = grp["wins"] / grp["total_battles"]
    return grp.sort_values("win_rate", ascending=False)


def best_playstyle_per_loadout(df, n_runs_per_matchup=None):
    """For each equipment loadout, find the playstyle that maximizes win rate."""
    if n_runs_per_matchup is None:
        from_df = df[df["a_name"] != df["b_name"]] if "a_name" in df.columns else df
        per_row = from_df["a_wins"] + from_df["b_wins"] + from_df["mut_wipe"] + from_df["indecisive"]
        n_runs_per_matchup = int(per_row.mode().iloc[0]) if len(per_row) else 100
    ps_wr = playstyle_win_rates(df, n_runs_per_matchup).reset_index()
    # For each a_equip, pick the playstyle with max win_rate
    idx = ps_wr.groupby("a_equip")["win_rate"].idxmax()
    best = ps_wr.loc[idx].reset_index(drop=True)
    return best.sort_values("win_rate", ascending=False)


def playstyle_effect_summary(df, n_runs_per_matchup=None):
    """For each playstyle, compute its average win rate across all loadouts it was applied to.
    Tells you which playstyles are generally strong vs niche.
    """
    if n_runs_per_matchup is None:
        from_df = df[df["a_name"] != df["b_name"]] if "a_name" in df.columns else df
        per_row = from_df["a_wins"] + from_df["b_wins"] + from_df["mut_wipe"] + from_df["indecisive"]
        n_runs_per_matchup = int(per_row.mode().iloc[0]) if len(per_row) else 100
    sub = df[df["a_name"] != df["b_name"]].copy()
    grp = sub.groupby("a_playstyle").agg(
        wins=("a_wins", "sum"),
        losses=("b_wins", "sum"),
        mut_wipe=("mut_wipe", "sum"),
        indecisive=("indecisive", "sum"),
        n_matchups=("a_wins", "count"),
        survival=("avg_a_rem", "mean"),
        avg_skirm=("avg_skirm", "mean"),
        rout_wipes=(_wipe_rout_col(df, "a"), "sum"),
        combat_wipes=("a_wipe_combat", "sum"),
    )
    grp["total_battles"] = grp["n_matchups"] * n_runs_per_matchup
    grp["win_rate"] = grp["wins"] / grp["total_battles"]
    return grp.sort_values("win_rate", ascending=False)


def playstyle_by_retinue(df, n_runs_per_matchup=None):
    """For each (retinue, playstyle) combo, average win rate.
    Shows which playstyles work best for which retinue tiers.
    """
    if n_runs_per_matchup is None:
        from_df = df[df["a_name"] != df["b_name"]] if "a_name" in df.columns else df
        per_row = from_df["a_wins"] + from_df["b_wins"] + from_df["mut_wipe"] + from_df["indecisive"]
        n_runs_per_matchup = int(per_row.mode().iloc[0]) if len(per_row) else 100
    sub = df[df["a_name"] != df["b_name"]].copy()
    grp = sub.groupby(["a_retinue", "a_playstyle"]).agg(
        wins=("a_wins", "sum"),
        n_matchups=("a_wins", "count"),
    )
    grp["total_battles"] = grp["n_matchups"] * n_runs_per_matchup
    grp["win_rate"] = grp["wins"] / grp["total_battles"]
    return grp.sort_values(["a_retinue", "win_rate"], ascending=[True, False])


# ==============================================================================
# Tier-filtered analysis — focus on realistic competitive band
# ==============================================================================
# Only ONE player gets KT in any given game (Preceptory is a Monument: Sovereign Piety +
# Established Prowess, single instance per realm). Most ongoing combat is MaA / Sgt.
# These helpers let you restrict analysis to specific tier combinations.

def filter_tiers(df, a_tiers=None, b_tiers=None, exclude_mirror=True):
    """Subset to matchups where retinues are within the given tier sets.
    a_tiers / b_tiers: iterable of retinue names. None = no filter on that side.
    exclude_mirror: drop self-matchups (a_name == b_name).
    """
    out = df.copy()
    if a_tiers is not None:
        out = out[out["a_retinue"].isin(a_tiers)]
    if b_tiers is not None:
        out = out[out["b_retinue"].isin(b_tiers)]
    if exclude_mirror:
        out = out[out["a_name"] != out["b_name"]]
    return out


def tier_landscape(df, tiers=("Man-at-Arms", "Sergeant"), n_runs_per_matchup=None):
    """Per-loadout win rate, survival, and wipe-cause within a tier-restricted field.
    Use this to ask 'what wins in the realistic competitive band?'
    Defaults to MaA/Sgt (the most common gameplay tier).
    """
    if n_runs_per_matchup is None:
        from_df = df[df["a_name"] != df["b_name"]] if "a_name" in df.columns else df
        per_row = from_df["a_wins"] + from_df["b_wins"] + from_df["mut_wipe"] + from_df["indecisive"]
        n_runs_per_matchup = int(per_row.mode().iloc[0]) if len(per_row) else 100
    sub = filter_tiers(df, a_tiers=tiers, b_tiers=tiers, exclude_mirror=True)
    import pandas as pd
    grp = sub.groupby("a_name").agg(
        a_retinue=("a_retinue", "first"),
        a_weapon=("a_weapon", "first"),
        a_shield=("a_shield", "first"),
        a_armor=("a_armor", "first"),
        a_tags=("a_tags", "first"),
        wins=("a_wins", "sum"),
        losses=("b_wins", "sum"),
        mut_wipe=("mut_wipe", "sum"),
        indecisive=("indecisive", "sum"),
        n_matchups=("a_wins", "count"),
        survival=("avg_a_rem", "mean"),
        skirm=("avg_skirm", "mean"),
        rout_wipes=(_wipe_rout_col(df, "a"), "sum"),
        combat_wipes=("a_wipe_combat", "sum"),
        shake_wipes=("a_wipe_shake", "sum"),
    )
    grp["total_battles"] = grp["n_matchups"] * n_runs_per_matchup
    grp["win_rate"] = grp["wins"] / grp["total_battles"]
    total_wipes = grp["rout_wipes"] + grp["combat_wipes"] + grp["shake_wipes"]
    grp["pct_rout_of_wipes"] = grp["rout_wipes"] / total_wipes.replace(0, 1) * 100
    return grp.sort_values("win_rate", ascending=False)


def cross_tier_matrix(df, n_runs_per_matchup=None):
    """Aggregate win/loss rates by retinue-tier pairing.
    Answers: what % of MaA-vs-Sgt matchups does MaA win? What % does Sgt win? Etc.

    n_runs_per_matchup: if None (default), auto-detected from the dataframe
                       (a_wins + b_wins + mut_wipe + indecisive per row).
                       Pass an explicit value only to override.
    """
    sub = df[df["a_name"] != df["b_name"]].copy()
    # Auto-detect n_runs per matchup if not provided
    if n_runs_per_matchup is None:
        # Each row's events sum to n_runs; use modal value across rows for robustness
        per_row_runs = sub["a_wins"] + sub["b_wins"] + sub["mut_wipe"] + sub["indecisive"]
        n_runs_per_matchup = int(per_row_runs.mode().iloc[0]) if len(per_row_runs) else 100
    import pandas as pd
    grp = sub.groupby(["a_retinue", "b_retinue"]).agg(
        n_matchups=("a_wins", "count"),
        wins=("a_wins", "sum"),
        losses=("b_wins", "sum"),
        mut_wipe=("mut_wipe", "sum"),
        indec=("indecisive", "sum"),
    )
    grp["total_battles"] = grp["n_matchups"] * n_runs_per_matchup
    grp["a_win_rate"] = grp["wins"] / grp["total_battles"]
    grp["b_win_rate"] = grp["losses"] / grp["total_battles"]
    grp["indec_rate"] = grp["indec"] / grp["total_battles"]
    grp["mut_rate"] = grp["mut_wipe"] / grp["total_battles"]
    return grp[["n_matchups", "a_win_rate", "b_win_rate", "mut_rate", "indec_rate"]]


# ==============================================================================
# 13. Spec impact — what does each spec/kit actually add?
# ==============================================================================

def _per_loadout_stats(df):
    """Aggregate per-loadout (as A) stats. Returns DataFrame indexed by a_name."""
    df = df[df["a_name"] != df["b_name"]].copy()
    df["a_survival_rate"] = df["avg_a_rem"] / df["a_size"]
    grp = df.groupby("a_name").agg(
        win_rate=("a_win_rate", "mean"),
        survival_rate=("a_survival_rate", "mean"),
        avg_kills=("b_killed", "mean"),
        avg_losses=("a_killed", "mean"),
        avg_spoils=("a_spoils_per_battle", "mean"),
        avg_skirm=("avg_skirm", "mean"),
        upkeep=("a_upkeep", "first"),
        upkeep_base=("a_upkeep_base", "first"),
        a_retinue=("a_retinue", "first"),
        a_weapon=("a_weapon", "first"),
        a_shield=("a_shield", "first"),
        a_armor=("a_armor", "first"),
        a_ranged=("a_ranged", "first"),
        a_tiltyard=("a_tiltyard", "first"),
        a_tags=("a_tags", "first"),
    )
    grp["kill_diff"] = grp["avg_kills"] - grp["avg_losses"]
    return grp


def compare_kits(df, retinue, weapon, armor, shield="", ranged="", tiltyard=False):
    """For a given base equipment, return all kit variants found in the pool
    along with their stats and deltas relative to the vanilla version.

    Use empty string "" for missing shield/ranged (matches CSV NaN-filled values).
    """
    stats = _per_loadout_stats(df)
    eq_filter = (
        (stats["a_retinue"] == retinue) &
        (stats["a_weapon"] == weapon) &
        (stats["a_armor"] == armor) &
        (stats["a_shield"] == shield) &
        (stats["a_ranged"] == ranged) &
        (stats["a_tiltyard"] == tiltyard)
    )
    variants = stats[eq_filter].copy()
    if len(variants) == 0:
        return pd.DataFrame()

    # Find baseline: the row with empty tags
    baseline_mask = (variants["a_tags"] == "") | variants["a_tags"].isna()
    if baseline_mask.any():
        baseline = variants[baseline_mask].iloc[0]
    else:
        # No vanilla in pool; use min-win-rate row as baseline
        baseline = variants.loc[variants["win_rate"].idxmin()]

    variants["delta_win_rate"]    = variants["win_rate"]    - baseline["win_rate"]
    variants["delta_survival"]    = variants["survival_rate"] - baseline["survival_rate"]
    variants["delta_kills"]       = variants["avg_kills"]    - baseline["avg_kills"]
    variants["delta_losses"]      = variants["avg_losses"]   - baseline["avg_losses"]
    variants["delta_kill_diff"]   = variants["kill_diff"]    - baseline["kill_diff"]
    variants["delta_spoils"]      = variants["avg_spoils"]   - baseline["avg_spoils"]

    return variants.sort_values("delta_win_rate", ascending=False)[
        ["a_tags", "win_rate", "delta_win_rate",
         "survival_rate", "delta_survival",
         "avg_kills", "delta_kills",
         "kill_diff", "delta_kill_diff",
         "avg_spoils", "delta_spoils",
         "upkeep"]
    ]


def spec_impact_summary(df, retinue, weapon, armor, shield="", ranged="", tiltyard=False, sort_by="delta_win_rate"):
    """Pretty-print spec/kit impact on a given base loadout.
    
    Shows what each spec or spec combo adds in absolute terms (win rate, durability, kills).
    """
    result = compare_kits(df, retinue, weapon, armor, shield=shield, ranged=ranged, tiltyard=tiltyard)
    if len(result) == 0:
        print(f"No variants found for {retinue}/{weapon}/{armor}.")
        return result

    eq_label = f"{retinue}/{weapon}"
    if shield:
        eq_label += f"/{shield}"
    eq_label += f"/{armor}"
    if ranged:
        eq_label += f" + {ranged}"
    if tiltyard:
        eq_label += " (TY)"

    print(f"=" * 90)
    print(f"SPEC IMPACT on base: {eq_label}")
    print(f"=" * 90)
    print(f"{'Tags / Kit':<55} {'Win%':>6} {'Δ Win':>7} {'Surv%':>6} {'Δ Surv':>7} {'Kills':>5} {'Δ Kill':>7}")
    print("-" * 90)
    for tags, row in result.iterrows():
        tag_label = (row["a_tags"] if row["a_tags"] else "(vanilla)")[:52]
        print(f"  {tag_label:<53} "
              f"{row['win_rate']*100:>5.1f}% "
              f"{row['delta_win_rate']*100:>+6.1f}% "
              f"{row['survival_rate']*100:>5.1f}% "
              f"{row['delta_survival']*100:>+6.1f}% "
              f"{row['avg_kills']:>5.1f} "
              f"{row['delta_kills']:>+6.1f}")
    return result


def tag_impact(df, tag):
    """For a single tag, find all loadouts that have it and all sibling loadouts
    (same equipment) that don't, and compute the average delta from adding it.
    
    Returns: dict with mean win rate delta, survival delta, kills delta, n_pairs.
    """
    stats = _per_loadout_stats(df)
    
    # Parse tags into sets for comparison
    def tag_set(s):
        if not s or pd.isna(s):
            return set()
        return set(t.strip() for t in str(s).split(",") if t.strip())
    
    stats["tag_set"] = stats["a_tags"].apply(tag_set)
    stats["has_tag"] = stats["tag_set"].apply(lambda s: tag in s)

    # Equipment signature for sibling matching
    stats["eq_sig"] = (
        stats["a_retinue"] + "|" +
        stats["a_weapon"] + "|" +
        stats["a_armor"] + "|" +
        stats["a_shield"].fillna("") + "|" +
        stats["a_ranged"].fillna("") + "|" +
        stats["a_tiltyard"].astype(str)
    )

    with_tag = stats[stats["has_tag"]].copy()
    without_tag = stats[~stats["has_tag"]].copy()

    pairs = []
    for _, w_row in with_tag.iterrows():
        # Sibling: same equipment, same other tags (minus the one we're testing)
        target_other_tags = w_row["tag_set"] - {tag}
        candidates = without_tag[without_tag["eq_sig"] == w_row["eq_sig"]]
        for _, c_row in candidates.iterrows():
            if c_row["tag_set"] == target_other_tags:
                pairs.append({
                    "with": w_row.name,
                    "without": c_row.name,
                    "delta_win_rate": w_row["win_rate"] - c_row["win_rate"],
                    "delta_survival": w_row["survival_rate"] - c_row["survival_rate"],
                    "delta_kills": w_row["avg_kills"] - c_row["avg_kills"],
                    "delta_losses": w_row["avg_losses"] - c_row["avg_losses"],
                    "delta_spoils": w_row["avg_spoils"] - c_row["avg_spoils"],
                })
    if not pairs:
        return None
    pairs_df = pd.DataFrame(pairs)
    return {
        "tag": tag,
        "n_pairs": len(pairs_df),
        "mean_delta_win_rate": pairs_df["delta_win_rate"].mean(),
        "mean_delta_survival": pairs_df["delta_survival"].mean(),
        "mean_delta_kills": pairs_df["delta_kills"].mean(),
        "mean_delta_losses": pairs_df["delta_losses"].mean(),
        "mean_delta_spoils": pairs_df["delta_spoils"].mean(),
        "pairs": pairs_df,
    }


def all_tag_impacts(df, tags=None):
    """Compute tag_impact for every interesting tag found in the pool.
    Returns DataFrame summarizing each tag's average effect on win rate, survival, kills, etc.
    """
    if tags is None:
        tags = [
            "Drilled", "Nimble", "Steady", "Steadfast", "Parry",
            "Cond Field", "MW Weapons", "GF Armor",
            "Immune Poison", "Poison", "Immune Unwieldy",
            "Yew Heart", "Unwieldy",
            "Regenerate", "Regenerate 5", "Regenerate 4", "Regenerate Reroll",
        ]
    rows = []
    for tag in tags:
        result = tag_impact(df, tag)
        if result is None:
            continue
        rows.append({
            "tag": tag,
            "n_pairs": result["n_pairs"],
            "mean_delta_win_rate": result["mean_delta_win_rate"],
            "mean_delta_survival": result["mean_delta_survival"],
            "mean_delta_kills": result["mean_delta_kills"],
            "mean_delta_losses": result["mean_delta_losses"],
            "mean_delta_spoils": result["mean_delta_spoils"],
        })
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).sort_values("mean_delta_win_rate", ascending=False)


# ==============================================================================
# PURSUIT COUNT ANALYSIS
# ==============================================================================
# Each loadout has a Military Pursuit Count (sum of building costs) and a Domain
# Count (sum of Rising=3, Established=6, Sovereign=10 across all four domains).
# These metrics let us see how concentrated military investment trades off
# against win rate, and whether some pursuit counts under/over-perform peers.


def _pursuit_summary_from_df(df, n_runs_per_matchup=None):
    """Aggregate per-loadout win rates and join with pursuit metadata.

    Returns a DataFrame indexed by `a_name` with columns:
      retinue, military_pursuit_count, domain_count, pursuits,
      battles, wins, losses, win_rate, kill_efficiency
    """
    if n_runs_per_matchup is None:
        # Auto-detect: mode of (a_wins+b_wins+mut_wipe+indecisive) per row
        totals = df["a_wins"] + df["b_wins"] + df["mut_wipe"] + df["indecisive"]
        n_runs_per_matchup = int(totals.mode().iloc[0])

    # Group by attacker name; drop mirror matches to avoid double-counting
    non_mirror = df[df["a_name"] != df["b_name"]]
    grp = non_mirror.groupby("a_name").agg(
        retinue=("a_retinue", "first"),
        military_pursuit_count=("a_military_pursuit_count", "first"),
        domain_count=("a_domain_count", "first"),
        pursuits=("a_pursuits", "first"),
        wins=("a_wins", "sum"),
        losses=("b_wins", "sum"),
        mut_wipe=("mut_wipe", "sum"),
        indecisive=("indecisive", "sum"),
        avg_a_rem=("avg_a_rem", "mean"),
        avg_b_rem=("avg_b_rem", "mean"),
    )
    grp["battles"] = grp[["wins", "losses", "mut_wipe", "indecisive"]].sum(axis=1)
    grp["win_rate"] = grp["wins"] / grp["battles"].clip(lower=1)
    grp["loss_rate"] = grp["losses"] / grp["battles"].clip(lower=1)
    grp["kill_efficiency"] = grp["avg_a_rem"] - grp["avg_b_rem"]
    return grp


def win_rate_by_mpc(df, n_runs_per_matchup=None, min_loadouts=3):
    """Win rate aggregated by Military Pursuit Count.

    Returns a DataFrame indexed by mpc with columns:
      n_loadouts, mean_win_rate, median_win_rate, std_win_rate,
      min_win_rate, max_win_rate, total_battles, mean_kill_eff
    """
    g = _pursuit_summary_from_df(df, n_runs_per_matchup)
    by_mpc = g.groupby("military_pursuit_count").agg(
        n_loadouts=("win_rate", "count"),
        mean_win_rate=("win_rate", "mean"),
        median_win_rate=("win_rate", "median"),
        std_win_rate=("win_rate", "std"),
        min_win_rate=("win_rate", "min"),
        max_win_rate=("win_rate", "max"),
        total_battles=("battles", "sum"),
        mean_kill_eff=("kill_efficiency", "mean"),
    )
    return by_mpc[by_mpc["n_loadouts"] >= min_loadouts]


def win_rate_by_mpc_retinue(df, n_runs_per_matchup=None, min_loadouts=3):
    """Win rate by (Military Pursuit Count, retinue). Wide format for plotting."""
    g = _pursuit_summary_from_df(df, n_runs_per_matchup)
    by_both = g.groupby(["military_pursuit_count", "retinue"]).agg(
        n_loadouts=("win_rate", "count"),
        mean_win_rate=("win_rate", "mean"),
        median_win_rate=("win_rate", "median"),
        mean_kill_eff=("kill_efficiency", "mean"),
    )
    return by_both[by_both["n_loadouts"] >= min_loadouts]


def win_rate_by_domain_count(df, n_runs_per_matchup=None, bucket_size=4, min_loadouts=3):
    """Win rate aggregated by Domain Count, bucketed."""
    g = _pursuit_summary_from_df(df, n_runs_per_matchup)
    # Bucket the domain count
    g = g.copy()
    g["dc_bucket"] = (g["domain_count"] // bucket_size) * bucket_size
    by_dc = g.groupby("dc_bucket").agg(
        n_loadouts=("win_rate", "count"),
        mean_win_rate=("win_rate", "mean"),
        median_win_rate=("win_rate", "median"),
        std_win_rate=("win_rate", "std"),
        total_battles=("battles", "sum"),
        mean_mpc=("military_pursuit_count", "mean"),
    )
    return by_dc[by_dc["n_loadouts"] >= min_loadouts]


def mpc_outliers(df, n_runs_per_matchup=None, top_n=10):
    """Find loadouts that significantly out- or under-perform their MPC peer group.

    A loadout is an outlier if its win_rate is >1 std-dev from the mean of its
    MPC bucket. Returns top_n over-performers and top_n under-performers.
    """
    g = _pursuit_summary_from_df(df, n_runs_per_matchup)
    # Add per-bucket statistics
    bucket_stats = g.groupby("military_pursuit_count")["win_rate"].agg(["mean", "std"])
    g = g.join(bucket_stats, on="military_pursuit_count", rsuffix="_bucket")
    g["z_score"] = (g["win_rate"] - g["mean"]) / g["std"].replace(0, np.nan)
    g["delta_vs_bucket"] = g["win_rate"] - g["mean"]

    over = g.nlargest(top_n, "z_score")[
        ["retinue", "military_pursuit_count", "domain_count", "pursuits",
         "win_rate", "mean", "delta_vs_bucket", "z_score"]
    ].rename(columns={"mean": "bucket_mean_wr"})
    under = g.nsmallest(top_n, "z_score")[
        ["retinue", "military_pursuit_count", "domain_count", "pursuits",
         "win_rate", "mean", "delta_vs_bucket", "z_score"]
    ].rename(columns={"mean": "bucket_mean_wr"})
    return over, under


def mpc_vs_lower_higher(df, n_runs_per_matchup=None, min_loadouts=5):
    """For each MPC bucket, compare its mean win rate vs neighboring buckets.

    Useful for spotting cost discontinuities — e.g., does going from mpc=4 to
    mpc=5 yield a big jump in win rate (suggesting good value-per-point), or a
    small one (suggesting the extra point is wasted)?
    """
    by_mpc = win_rate_by_mpc(df, n_runs_per_matchup, min_loadouts)
    rows = []
    mpcs = sorted(by_mpc.index)
    for mpc in mpcs:
        row = by_mpc.loc[mpc]
        prev_wr = by_mpc.loc[mpc - 1, "mean_win_rate"] if (mpc - 1) in by_mpc.index else None
        next_wr = by_mpc.loc[mpc + 1, "mean_win_rate"] if (mpc + 1) in by_mpc.index else None
        rows.append({
            "mpc": mpc,
            "n_loadouts": int(row["n_loadouts"]),
            "mean_win_rate": row["mean_win_rate"],
            "delta_vs_mpc_minus_1": (row["mean_win_rate"] - prev_wr) if prev_wr is not None else None,
            "delta_vs_mpc_plus_1": (row["mean_win_rate"] - next_wr) if next_wr is not None else None,
        })
    return pd.DataFrame(rows).set_index("mpc")


def best_loadout_per_mpc(df, n_runs_per_matchup=None):
    """The highest-win-rate loadout at each Military Pursuit Count.

    Shows the "best value at each budget" — what does the optimal build look like
    if a player only spends N pursuit points on military?
    """
    g = _pursuit_summary_from_df(df, n_runs_per_matchup)
    g = g.reset_index()  # bring `a_name` back as a column
    idx = g.groupby("military_pursuit_count")["win_rate"].idxmax()
    return g.loc[idx].set_index("military_pursuit_count").sort_index()


def pursuit_presence_effect(df, n_runs_per_matchup=None):
    """For each pursuit, compare mean win rate when present vs absent.

    Helps answer: "Which pursuits actually correlate with winning?"
    Returns a DataFrame with columns:
      pursuit, n_with, n_without, wr_with, wr_without, delta_wr
    """
    g = _pursuit_summary_from_df(df, n_runs_per_matchup)
    # All distinct pursuits that appear in the pool
    all_pursuits = set()
    for s in g["pursuits"].fillna(""):
        if s:
            all_pursuits.update(s.split("|"))
    rows = []
    for p in sorted(all_pursuits):
        mask = g["pursuits"].fillna("").str.contains(rf"(?:^|\|){p}(?:\||$)", regex=True)
        with_p = g[mask]
        without_p = g[~mask]
        if len(with_p) == 0 or len(without_p) == 0:
            continue
        rows.append({
            "pursuit": p,
            "n_with": len(with_p),
            "n_without": len(without_p),
            "wr_with": with_p["win_rate"].mean(),
            "wr_without": without_p["win_rate"].mean(),
            "delta_wr": with_p["win_rate"].mean() - without_p["win_rate"].mean(),
        })
    return pd.DataFrame(rows).sort_values("delta_wr", ascending=False)


if __name__ == "__main__":
    df = load_tournament()
    print_summary(df, n=10)