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


def per_build_metrics(df):
    """Collapse a matchups frame (one row per pair) to ONE row per attacker build (a_name),
    with aggregated output metrics. Cheap base for feature_bucket_matrix: the giant frame is
    grouped once (observed=True) into ~thousands of rows; all bucketing then runs on that.
    Metrics: win_rate, decisive, mutual, death mix (combat/shake/rout), shield_destroyed,
    survivors, spoils, avg_skirm."""
    n = df["n_runs"].clip(lower=1) if "n_runs" in df.columns else (
        df["a_wins"] + df["b_wins"] + df["mut_wipe"] + df["indecisive"]).clip(lower=1)
    tmp = df.assign(_wr=df["a_wins"] / n,
                    _dec=(df["a_wins"] + df["b_wins"]) / n,
                    _mut=df["mut_wipe"] / n)
    has_dc = "a_domain_count" in df.columns
    has_pur = "a_pursuits" in df.columns
    has_tags = "a_tags" in df.columns
    agg = dict(
        retinue=("a_retinue", "first"),
        weapon=("a_weapon", "first"), shield=("a_shield", "first"),
        armor=("a_armor", "first"), ranged=("a_ranged", "first"),
        mpc=("a_military_pursuit_count", "first"),
        win_rate=("_wr", "mean"), decisive=("_dec", "mean"), mutual=("_mut", "mean"),
        kc=("avg_a_killed_combat", "sum"), ks=("avg_a_killed_shake", "sum"), kr=("avg_a_killed_rout", "sum"),
        shield_destroyed=("a_shield_destroyed_rate", "mean"),
        survivors=("avg_a_rem", "mean"), spoils=("a_spoils_per_battle", "mean"),
        avg_skirm=("avg_skirm", "mean"),
    )
    if has_dc:  agg["domain_count"] = ("a_domain_count", "first")
    if has_pur: agg["pursuits"]     = ("a_pursuits", "first")
    if has_tags: agg["tags"]        = ("a_tags", "first")
    g = tmp.groupby("a_name", observed=True).agg(**agg).reset_index()
    t = (g["kc"] + g["ks"] + g["kr"]).clip(lower=1e-9)
    g["death_combat"] = g["kc"] / t
    g["death_shake"]  = g["ks"] / t
    g["death_rout"]   = g["kr"] / t
    g = g.drop(columns=["kc", "ks", "kr"])
    # TOTAL INVESTMENT COUNT: every pursuit counts as 1 (no efficiency discount). MPC charges 0
    # for line-extensions (Blacksmith->Forge->ABF = 1 MPC), which lets top-tier gear appear at a
    # low MPC and flattens the MPC<->winrate correlation. Counting the raw pursuit set instead
    # reflects the real number of buildings stood up. Derived from the "|"-joined pursuits string.
    if "pursuits" in g.columns:
        g["total_investment"] = g["pursuits"].fillna("").map(
            lambda s: len([x for x in str(s).split("|") if x]))
    for c in ("pursuits", "tags", "weapon", "shield", "armor", "ranged", "retinue"):
        if c in g.columns and isinstance(g[c].dtype, pd.CategoricalDtype):
            g[c] = g[c].astype("object")
    return g


_BUCKET_METRICS = ["win_rate", "decisive", "mutual", "death_combat", "death_shake", "death_rout",
                   "shield_destroyed", "survivors", "spoils", "avg_skirm"]


def investment_vs_winrate(df):
    """Compare how well MPC vs TOTAL INVESTMENT COUNT predicts win rate.

    MPC counts military pursuit SLOTS but gives a 0-cost discount for extending an efficiency line
    (Blacksmith->Forge->ABF = 1 MPC), so a Crafted-tier weapon can appear at MPC 4 while actually
    sitting on 6 stood-up pursuits. That decouples MPC from real investment and flattens the
    MPC<->winrate correlation. total_investment counts every pursuit as 1.

    Returns a dict of Pearson + Spearman r for each predictor, plus the per-(count) mean win-rate
    tables for both, so you can see which is the cleaner indicator of invested power.
    """
    from scipy.stats import pearsonr, spearmanr
    g = per_build_metrics(df)
    if "total_investment" not in g.columns:
        raise ValueError("no pursuits column — can't compute total_investment")
    out = {}
    for label, col in [("MPC", "mpc"), ("total_investment", "total_investment")]:
        sub = g[[col, "win_rate"]].dropna()
        pr = pearsonr(sub[col], sub["win_rate"])
        sr = spearmanr(sub[col], sub["win_rate"])
        means = sub.groupby(col)["win_rate"].agg(["mean", "std", "count"]).round(3)
        out[label] = {"pearson_r": round(float(pr[0]), 3), "pearson_p": float(pr[1]),
                      "spearman_r": round(float(sr[0]), 3), "spearman_p": float(sr[1]),
                      "by_count": means}
    return out


def _ctrl_delta(g, mask, metric, strata):
    """Mean(metric|has) - mean(metric|not) WITHIN each stratum, weighted-averaged across strata
    (weight = smaller bucket in the stratum). Controls for the retinue+MPC confound."""
    sub = pd.DataFrame({"m": g[metric].values, "_has": mask.values, "_s": strata.values})
    grp = sub.groupby(["_s", "_has"], observed=True)["m"].agg(["mean", "count"]).reset_index()
    mean_piv = grp.pivot(index="_s", columns="_has", values="mean")
    cnt_piv  = grp.pivot(index="_s", columns="_has", values="count")
    if True not in mean_piv.columns or False not in mean_piv.columns:
        return np.nan
    delta = mean_piv[True] - mean_piv[False]
    w = cnt_piv.reindex(columns=[True, False]).min(axis=1)
    valid = delta.notna() & w.notna() & (w > 0)
    if not valid.any() or w[valid].sum() == 0:
        return np.nan
    return float((delta[valid] * w[valid]).sum() / w[valid].sum())


def feature_bucket_matrix(df, metrics=None, min_support=20, max_tokens=50,
                          control_cols=("retinue", "mpc")):
    """Sensitivity-via-partition. For every per-build FEATURE (each weapon/shield/armor/ranged
    value, has_shield/has_ranged, each pursuit/tag token) split builds into has / hasn't and report
    the delta on every output metric BOTH raw (pooled) and controlled (within retinue+MPC). The
    raw-vs-ctrl gap = how much of the effect is confound (the tier/retinue X travels with).

    Accepts a matchups frame OR a pre-aggregated per_build_metrics frame. Returns a wide DataFrame:
    one row per feature; columns n_has/n_not and, per metric, {metric}_raw and {metric}_ctrl."""
    import re
    from collections import Counter
    g = df if ("win_rate" in df.columns and "a_name" not in df.columns) else per_build_metrics(df)
    metrics = metrics or [m for m in _BUCKET_METRICS if m in g.columns]
    c0 = control_cols[0] if control_cols[0] in g.columns else "retinue"
    c1 = control_cols[1] if control_cols[1] in g.columns else "mpc"
    strata = g[c0].astype(str) + "|" + g[c1].astype(str)

    feats = {}
    for col in ("weapon", "shield", "armor", "ranged"):
        if col in g.columns:
            s = g[col].astype("object")
            for val in [v for v in s.dropna().unique() if v not in ("", None)]:
                feats[f"{col}={val}"] = (s == val)
    if "shield" in g.columns:
        sh = g["shield"].astype("object"); feats["has_shield"] = sh.notna() & (sh != "")
    if "ranged" in g.columns:
        rg = g["ranged"].astype("object"); feats["has_ranged"] = rg.notna() & (rg != "")
    for col, sep in (("pursuits", "|"), ("tags", ",")):
        if col in g.columns:
            s = g[col].astype("object").fillna("")
            cnt = Counter()
            for v in s.unique():
                for tok in str(v).split(sep):
                    tok = tok.strip()
                    if tok:
                        cnt[tok] += 1
            for tok, _ in cnt.most_common(max_tokens):
                pat = rf"(?:^|{re.escape(sep)}){re.escape(tok)}(?:{re.escape(sep)}|$)"
                feats[f"{col}:{tok}"] = s.str.contains(pat, regex=True)

    rows = []
    for name, mask in feats.items():
        n_has = int(mask.sum()); n_not = int((~mask).sum())
        if n_has < min_support or n_not < min_support:
            continue
        row = {"feature": name, "n_has": n_has, "n_not": n_not}
        for m in metrics:
            row[f"{m}_raw"]  = g.loc[mask, m].mean() - g.loc[~mask, m].mean()
            row[f"{m}_ctrl"] = _ctrl_delta(g, mask, m, strata)
        rows.append(row)
    res = pd.DataFrame(rows)
    if len(res) and "win_rate_raw" in res.columns:
        res = res.reindex(res["win_rate_raw"].abs().sort_values(ascending=False).index)
    return res.reset_index(drop=True)


# ==============================================================================
# UPKEEP REDUCTIONS FROM SPECIALIZATIONS
# ==============================================================================
# Assumes player has built every upkeep-reducing spec along the pathway.
# Generic reductions apply to all retinues (per-retinue). Equipment reductions
# apply only if the relevant equipment is in the loadout.

# Generic Upkeep specializations (stack additively). Rescaled for the FLAT total-cost model
# (cost is the whole army's cost, not per-soldier): each generic modifier is -100, and Levy Hall
# (the would-be larger slot) is -200.
# Levy Hall innate (in-province) and mastery (out-of-province) don't stack — different contexts.
GENERIC_UPKEEP_REDUCTIONS = [
    ("Butchery (mastery)",            100),
    ("Tannery (mastery)",             100),
    ("Armory (mastery)",              100),
    ("Master Workshop (innate)",      100),
    ("Gilded Foundry (innate)",       100),
    ("Smokehouse (mastery)",          100),
    ("Levy Hall (innate)",            200),  # in-province; swap to mastery for out-of-province
    ("Advanced Blast Furnaces (innate)", 100),
]
GENERIC_UPKEEP_TOTAL = sum(r for _, r in GENERIC_UPKEEP_REDUCTIONS)

# Equipment-conditional (Maintain X), -100 each:
LANCE_REDUCTION       = 100  # Saddlery mastery — if weapon == Lance
SHIELD_REDUCTION      = 100  # Joinery mastery — if any shield
LIGHT_ARMOR_REDUCTION = 100  # Tannery innate — Cloth, Leather
HEAVY_ARMOR_REDUCTION = 100  # Armory innate — Chainmail, Full Plate, Gothic Plate
RANGED_REDUCTION      = 100  # Fletchery mastery — if ranged equipped (incl. Tiltyard dual-equip)

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

    Tries the given encoding first, falls back to cp1252 (Excel-saved CSVs).

    Parquet fast-path: if a sibling `.parquet` file exists for the given matchups path (or
    the path itself ends in .parquet), it's loaded instead — ~9x faster than CSV. The
    tournament writes this automatically when pyarrow is installed; pass a .csv path as usual
    and the Parquet copy is used transparently if found."""
    import os
    # Resolve a Parquet fast-path.
    if str(matchups_path).endswith(".parquet"):
        return _finalize_tournament_df(pd.read_parquet(matchups_path))
    parquet_sibling = str(matchups_path)[:-4] + ".parquet" if str(matchups_path).endswith(".csv") else None
    if parquet_sibling and os.path.exists(parquet_sibling):
        try:
            return _finalize_tournament_df(pd.read_parquet(parquet_sibling))
        except Exception:
            pass  # fall back to CSV on any Parquet read error

    try:
        df = pd.read_csv(matchups_path, encoding=encoding)
    except UnicodeDecodeError:
        df = pd.read_csv(matchups_path, encoding="cp1252")
    return _finalize_tournament_df(df)


def load_tournament_pruned(matchups_path="matchups.csv", extra_columns=None):
    """Lowest-memory loader for very large matchups files (hundreds of MB).

    Reads ONLY the columns the common analyses need directly from parquet — column pruning happens
    at read time, so the heavy string columns (a_pursuits/b_pursuits, a_name/b_name, a_tags/b_tags)
    never enter RAM. No downcasting pass (that loads everything first and temporarily doubles memory,
    which is the opposite of what you want on a multi-GB frame).

    Covers: death-cause mix, retinue matrices, decisive/rout/shield-destroyed rates, MPC breakdowns,
    battle_overview. If an analysis needs a column not in the default set, pass it via extra_columns.
    Falls back to the full load_tournament if the file isn't parquet or a needed column is absent.
    """
    import os
    pq = None
    if str(matchups_path).endswith(".parquet"):
        pq = matchups_path
    elif str(matchups_path).endswith(".csv"):
        sib = str(matchups_path)[:-4] + ".parquet"
        if os.path.exists(sib):
            pq = sib
    if pq is None:
        return load_tournament(matchups_path)  # no parquet → fall back to normal path

    NEEDED = [
        "a_name","b_name","mode","a_wins","b_wins","mut_wipe","indecisive","avg_skirm",
        "avg_a_rem","avg_b_rem",
        "avg_a_killed_combat","avg_a_killed_shake","avg_a_killed_waver","avg_a_killed_rout",
        "avg_b_killed_combat","avg_b_killed_shake","avg_b_killed_waver","avg_b_killed_rout",
        "a_wipe_combat","a_wipe_shake","a_wipe_rout","b_wipe_combat","b_wipe_shake","b_wipe_rout",
        "a_shield_destroyed_rate","b_shield_destroyed_rate",
        "a_retinue","b_retinue","a_size","b_size",
        "a_military_pursuit_count","b_military_pursuit_count",
        "a_domain_count","b_domain_count",
        # equipment columns (weapon/shield/armor/ranged/tiltyard) — used by weapon-tier / AP /
        # gear-breakdown analyses. Kept because they're moderate-cardinality, not the giant
        # a_pursuits/b_pursuits/a_tags/b_tags strings (those stay pruned out).
        "a_weapon","b_weapon","a_shield","b_shield","a_armor","b_armor",
        "a_ranged","b_ranged","a_tiltyard","b_tiltyard",
    ]
    if extra_columns:
        NEEDED += [c for c in extra_columns if c not in NEEDED]
    import pyarrow.parquet as pqf
    avail = set(pqf.ParquetFile(pq).schema.names)
    cols = [c for c in NEEDED if c in avail]
    df = pd.read_parquet(pq, columns=cols)
    # category-encode just the two retinue columns (tiny, cheap, big win for groupby memory)
    for c in ("a_retinue", "b_retinue"):
        if c in df.columns:
            df[c] = df[c].astype("category")
    # derived columns the analyses reference (cheap; only the ones that don't need pruned cols)
    if "n_runs" not in df.columns:
        df["n_runs"] = df["a_wins"] + df["b_wins"] + df["mut_wipe"] + df["indecisive"]
    denom = df["n_runs"].clip(lower=1)
    if "a_win_rate" not in df.columns:
        df["a_win_rate"] = df["a_wins"] / denom
        df["b_win_rate"] = df["b_wins"] / denom
    return df


def load_tournament_lean(matchups_path="matchups.csv", columns=None, downcast=True, max_rows=None, frac=None, seed=2026):
    """Memory-lean loader that keeps EVERY column (so all analyses work) but stores them compactly.

    Row-reduction options for when the matchups file itself is too big to hold:
      - frac: load a random fraction of rows (e.g. frac=0.3 keeps 30%). A uniform random sample of
        pairs preserves every aggregate distribution (death mix, retinue/MPC win rates) — it just
        widens confidence intervals. This is the safe way to cut memory on an existing big file.
      - max_rows: hard cap (takes a random sample if the file is larger). Use frac for proportional.
    NOTE: the real fix for a huge file is regenerating the tournament with a smaller STRATIFY_PER_MPC
    (rows scale ~quadratically with build count: 80->40 per MPC = ~1/4 the rows). frac/max_rows are
    for working with a file you already have.

    The per-column memory audit shows no single column dominates — strings are ~equal-sized and the
    big win is dtype efficiency, not dropping columns. So this loads the full frame, then category-
    encodes repeated-string columns and downcasts numerics (~half the memory), in a single astype
    pass to avoid the temporary doubling of per-column reassignment.
    """
    import os
    parquet = None
    if str(matchups_path).endswith(".parquet"):
        parquet = matchups_path
    elif str(matchups_path).endswith(".csv"):
        sib = str(matchups_path)[:-4] + ".parquet"
        if os.path.exists(sib):
            parquet = sib
    if parquet:
        df = pd.read_parquet(parquet, columns=columns) if columns else pd.read_parquet(parquet)
    else:
        df = pd.read_csv(matchups_path, usecols=columns) if columns else pd.read_csv(matchups_path)
    if frac is not None and 0 < frac < 1:
        df = df.sample(frac=frac, random_state=seed).reset_index(drop=True)
    if max_rows and len(df) > max_rows:
        df = df.sample(n=max_rows, random_state=seed).reset_index(drop=True)
    df = _finalize_tournament_df(df)
    if downcast:
        # Category-encode only LOW-cardinality repeated-string columns. Deliberately NOT a_pursuits/
        # b_pursuits/a_tags/b_tags: those are long, near-unique per build, so categorizing gives no
        # memory benefit AND breaks downstream .fillna("")/.str ops (fillna with a non-category value
        # raises TypeError on a categorical). Leaving them as object strings is both lighter in
        # practice and safer.
        cat_cols = [c for c in ["a_retinue","b_retinue","a_weapon","b_weapon","a_shield","b_shield",
                                "a_armor","b_armor","a_ranged","b_ranged","a_playstyle","b_playstyle",
                                "mode"] if c in df.columns]
        if cat_cols:
            df = df.astype({c: "category" for c in cat_cols})
        for c in df.select_dtypes(include=["int64"]).columns:
            df[c] = pd.to_numeric(df[c], downcast="integer")
        for c in df.select_dtypes(include=["float64"]).columns:
            df[c] = pd.to_numeric(df[c], downcast="float")
    return df


def _finalize_tournament_df(df):
    """Apply the derived columns / fillna normalization shared by the CSV and Parquet
    load paths."""
    import pandas as pd  # local import keeps this helper self-contained
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

    # Cost is the TOTAL army cost (not per-soldier), so upkeep = cost directly — no × size.
    # Upkeep = your retinue cost minus your upkeep-reducing modifiers (a_ret_cost_modified).
    df["a_upkeep_base"] = df["a_ret_cost"]            # flat base total
    df["b_upkeep_base"] = df["b_ret_cost"]
    df["a_upkeep"] = df["a_ret_cost_modified"]        # flat, modifier-reduced (default)
    df["b_upkeep"] = df["b_ret_cost_modified"]

    df["a_killed"] = df["a_size"] - df["avg_a_rem"]
    df["b_killed"] = df["b_size"] - df["avg_b_rem"]

    df["n_runs"] = df["a_wins"] + df["b_wins"] + df["mut_wipe"] + df["indecisive"]
    df["a_win_rate"] = df["a_wins"] / df["n_runs"]
    df["b_win_rate"] = df["b_wins"] / df["n_runs"]

    # Spoils of War: destroying the enemy yields their cost minus THEIR upkeep modifiers
    # (b_ret_cost_modified), i.e. the enemy's modified total. Cost is a flat army total, so a full
    # wipe awards the whole enemy cost and a partial kill a proportional share (killed / size).
    a_frac_killed = (df["b_killed"] / df["b_size"].clip(lower=1)).clip(0, 1)
    b_frac_killed = (df["a_killed"] / df["a_size"].clip(lower=1)).clip(0, 1)
    df["a_spoils_per_battle"] = a_frac_killed * df["b_ret_cost_modified"]
    df["b_spoils_per_battle"] = b_frac_killed * df["a_ret_cost_modified"]

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

def feature_bucket_sensitivity(df, features=None, min_bucket=200, control_cols=("a_retinue", "a_military_pursuit_count")):
    """Partition the matchups frame into has-X / hasn't-X for every per-build FEATURE and report,
    for each OUTPUT metric, the raw delta (global buckets) and the controlled delta (averaged over
    within-stratum has/hasn't comparisons, strata = control_cols). Side-by-side so the gap between
    raw and controlled shows how much of X's apparent effect is confound (X traveling with tier/retinue).

    Uses ONLY the existing matchups frame - no re-running. Covers per-build inputs (weapon, shield,
    armor, ranged, retinue, MPC bucket, and every pursuit/keyword token). Global constants
    (SHAKE_CAP/FRONT_CAP/AP/stat definitions) are NOT measurable this way - they don't vary in the
    file; use sensitivity_sweep.py (re-run) for those.

    Returns a tidy DataFrame: one row per (feature, output_metric) with raw_delta, ctrl_delta, n_has,
    n_hasnt.
    """
    import numpy as np
    d = df[df["a_name"] != df["b_name"]].copy() if "a_name" in df.columns else df.copy()

    n = (d["a_wins"] + d["b_wins"] + d["mut_wipe"] + d["indecisive"]).clip(lower=1)
    d["_decisive"] = (d["a_wins"] + d["b_wins"]) / n
    d["_mutual"]   = d["mut_wipe"] / n
    d["_indec"]    = d["indecisive"] / n
    d["_wr"]       = d["a_wins"] / (d["a_wins"] + d["b_wins"]).clip(lower=1)
    ck, sk, rk = d["avg_a_killed_combat"], d["avg_a_killed_shake"], d["avg_a_killed_rout"]
    t = (ck + sk + rk).clip(lower=1)
    d["_death_combat"] = ck / t
    d["_death_shake"]  = sk / t
    d["_death_rout"]   = rk / t
    d["_shield_dest"]  = d["a_shield_destroyed_rate"]
    d["_survivors"]    = d["avg_a_rem"]
    d["_spoils"]       = d["a_spoils_per_battle"]
    OUT = ["_wr", "_decisive", "_mutual", "_indec", "_death_combat", "_death_shake", "_death_rout",
           "_shield_dest", "_survivors", "_spoils"]

    masks = {}
    for col in ["a_weapon", "a_shield", "a_armor", "a_ranged", "a_retinue"]:
        if col in d.columns:
            vals = [v for v in d[col].astype("object").dropna().unique() if v not in ("", None)]
            for v in vals:
                masks[f"{col}={v}"] = (d[col].astype("object") == v)
    if "a_military_pursuit_count" in d.columns:
        for mpc in sorted(d["a_military_pursuit_count"].dropna().unique()):
            masks[f"MPC={int(mpc)}"] = (d["a_military_pursuit_count"] == mpc)
    for col in ["a_pursuits", "a_tags"]:
        if col in d.columns:
            s = d[col].astype("object").fillna("")
            toks = set()
            for cell in s.unique():
                if cell:
                    toks.update(t2 for t2 in cell.replace(",", "|").split("|") if t2)
            for tok in sorted(toks):
                masks[f"{col[2:]}:{tok}"] = s.str.contains(rf"(?:^|[|,]){tok}(?:[|,]|$)", regex=True)

    if features:
        masks = {k: v for k, v in masks.items() if any(f in k for f in features)}

    if control_cols and all(c in d.columns for c in control_cols):
        d["_stratum"] = d[list(control_cols)].astype("object").astype(str).agg("|".join, axis=1)
    else:
        d["_stratum"] = "all"

    rows = []
    for feat, mask in masks.items():
        has = d[mask]; hasnt = d[~mask]
        if len(has) < min_bucket or len(hasnt) < min_bucket:
            continue
        for metric in OUT:
            raw = has[metric].mean() - hasnt[metric].mean()
            cdiffs, weights = [], []
            for stratum, g in d.groupby("_stratum", observed=True):
                gm = mask.loc[g.index]
                gh, gn = g[gm], g[~gm]
                if len(gh) >= 5 and len(gn) >= 5:
                    cdiffs.append(gh[metric].mean() - gn[metric].mean())
                    weights.append(min(len(gh), len(gn)))
            ctrl = (np.average(cdiffs, weights=weights) if cdiffs else np.nan)
            rows.append({"feature": feat, "metric": metric[1:], "raw_delta": raw, "ctrl_delta": ctrl,
                         "n_has": len(has), "n_hasnt": len(hasnt), "n_strata": len(cdiffs)})
    return pd.DataFrame(rows)


def crush_rate(df):
    df = df[df["a_name"] != df["b_name"]].copy()
    df = df[df["a_wins"] > 0]
    if len(df) == 0:
        return pd.DataFrame()
    df["weighted_rem"] = df["avg_a_rem"] * df["a_wins"]
    # Vectorized agg (observed=True) instead of groupby().apply(custom_func) — the latter ran one
    # Python call per a_name group (thousands), which was the bottleneck.
    grp = df.groupby("a_name", observed=True).agg(
        total_wins=("a_wins", "sum"),
        wr_sum=("weighted_rem", "sum"),
        a_size=("a_size", "first"),
    ).reset_index()
    grp["weighted_avg_rem_in_wins"] = grp["wr_sum"] / grp["total_wins"].clip(lower=1)
    grp["crush_score"] = grp["weighted_avg_rem_in_wins"] / grp["a_size"]
    grp = grp.drop(columns="wr_sum")
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
            "Cond Field", "Rend", "GF Armor",
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
    grp = non_mirror.groupby("a_name", observed=True).agg(
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
    # De-categorize string columns so downstream .fillna("")/.str ops work (the lean loader
    # category-encodes pursuits/retinue; fillna with a new category raises TypeError otherwise).
    for c in ("pursuits", "retinue"):
        if isinstance(grp[c].dtype, pd.CategoricalDtype):
            grp[c] = grp[c].astype("object")
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


# ==============================================================================
# Retinue-vs-retinue matrices, per-MPC leaderboards, and confound filtering
# ==============================================================================

RETINUE_ORDER = ["Levy", "Man-at-Arms", "Sergeant", "Knight Templar"]


def retinue_matchup_matrices(df, retinue_order=None):
    """Aggregate the matchups into a set of A-retinue x B-retinue matrices, one per metric.

    Every battle is recorded from A's perspective (A is the attacker/initiator slot). For each
    (a_retinue, b_retinue) cell we average across all builds and runs of that retinue pairing:

      a_win_rate        A's win rate vs that opponent retinue
      mut_wipe_rate     fraction of runs ending in mutual wipe
      indecisive_rate   fraction ending indecisive
      avg_skirm         mean battle length (skirmishes)
      a_kills_combat     A's combat kills on B per battle
      a_kills_shake      A's kills via B's failed shaking tests
      b_kills_combat     B's combat kills on A (i.e. A's losses) per battle
      a_rout_kills       kills A inflicts when B routs
      b_rout_kills       kills B inflicts when A routs
      a_shield_destroyed fraction of runs A's shield was destroyed

    Returns dict[str, DataFrame], each a square matrix indexed by A retinue (rows) x B retinue
    (cols). Weighted by n_runs so heavily-sampled pairings dominate appropriately.
    """
    order = retinue_order or RETINUE_ORDER
    d = df.copy()
    d["nr"] = d["n_runs"].clip(lower=1)
    # weighted helper: build a matrix of sum(metric*nr)/sum(nr) over the (a_ret,b_ret) groups
    def wmatrix(num_col, per_run=True):
        if per_run:
            d["_num"] = d[num_col] * d["nr"]
        else:
            d["_num"] = d[num_col]
        g = d.groupby(["a_retinue", "b_retinue"])
        num = g["_num"].sum()
        den = g["nr"].sum()
        m = (num / den).unstack("b_retinue")
        return m.reindex(index=order, columns=order)

    # rate metrics computed from per-battle counts
    d["_aw_rate"] = d["a_wins"] / d["nr"]
    d["_mw_rate"] = d["mut_wipe"] / d["nr"]
    d["_ind_rate"] = d["indecisive"] / d["nr"]

    out = {
        "a_win_rate":       wmatrix("_aw_rate"),
        "mut_wipe_rate":    wmatrix("_mw_rate"),
        "indecisive_rate":  wmatrix("_ind_rate"),
        "avg_skirm":        wmatrix("avg_skirm"),
        "a_kills_combat":   wmatrix("avg_a_killed_combat"),
        "a_kills_shake":    wmatrix("avg_a_killed_shake"),
        "b_kills_combat":   wmatrix("avg_b_killed_combat"),
        "a_rout_kills":     wmatrix("avg_a_killed_rout"),
        "b_rout_kills":     wmatrix("avg_b_killed_rout"),
        "a_shield_destroyed": wmatrix("a_shield_destroyed_rate"),
        "n_battles":        wmatrix("nr", per_run=False),
    }
    return out


def top_performers_by_mpc(summary_df, top_n=10, mpc_col="military_pursuit_count",
                          metric="win_rate"):
    """From a per-loadout SUMMARY dataframe (summary.csv), return the top-N builds within each
    MPC bucket, ranked by `metric` (default win_rate). Returns a single concatenated DataFrame
    with an `mpc_rank` column, sorted by (mpc, rank).

    Use summary.csv (one row per build) — NOT matchups.csv.
    """
    if mpc_col not in summary_df.columns:
        raise KeyError(f"{mpc_col} not in summary columns: {list(summary_df.columns)[:12]}...")
    rows = []
    for mpc, g in summary_df.groupby(mpc_col):
        gg = g.sort_values(metric, ascending=False).head(top_n).copy()
        gg["mpc_rank"] = range(1, len(gg) + 1)
        rows.append(gg)
    if not rows:
        return summary_df.iloc[0:0]
    out = pd.concat(rows, ignore_index=True)
    cols_front = [mpc_col, "mpc_rank", "name", "retinue", metric]
    cols = cols_front + [c for c in out.columns if c not in cols_front]
    return out[cols].sort_values([mpc_col, "mpc_rank"]).reset_index(drop=True)


def mpc_summary_table(summary_df, mpc_col="military_pursuit_count"):
    """Per-MPC rollup: count of builds, mean/median/max win rate, and the single best build name.
    Quick read on how win rate scales with military investment."""
    rows = []
    for mpc, g in summary_df.groupby(mpc_col):
        best = g.loc[g["win_rate"].idxmax()]
        rows.append({
            mpc_col: mpc,
            "n_builds": len(g),
            "mean_wr": g["win_rate"].mean(),
            "median_wr": g["win_rate"].median(),
            "max_wr": g["win_rate"].max(),
            "best_build": best["name"],
            "best_retinue": best.get("retinue", ""),
        })
    return pd.DataFrame(rows).sort_values(mpc_col).reset_index(drop=True)


def filter_confounds(df, drop_mutual_wipes=False, exclude_mirror_gear=False,
                     same_mpc=False, mpc_tolerance=0, min_decisive_rate=None,
                     decisive_only=False):
    """Return a filtered copy of the matchups dataframe that controls for the main confounds
    surfaced in tuning. All filters are optional and compose; defaults change nothing.

      drop_mutual_wipes : recompute win rates EXCLUDING mutual-wipe runs (a_win_rate becomes
                          a_wins / (a_wins + b_wins + indecisive)). Use when mutual wipes are
                          washing out a real per-side edge (the Sergeant-vs-MaA case). Adds
                          columns a_win_rate_nomw / b_win_rate_nomw; does not drop rows.
      decisive_only     : like drop_mutual_wipes but ALSO drops indecisive — win rate over
                          decided battles only (a_wins / (a_wins + b_wins)). Adds
                          a_win_rate_decisive / b_win_rate_decisive.
      exclude_mirror_gear: drop rows where A and B have identical weapon+shield+armor (mirror
                          matchups mutually annihilate and inflate the mutual-wipe bucket).
      same_mpc          : keep only rows where |a_mpc - b_mpc| <= mpc_tolerance. Controls for
                          military investment so retinue/gear effects aren't confounded by a
                          cheaper opponent field.
      min_decisive_rate : keep only rows whose decisive fraction (1 - mut - ind)/n_runs >=
                          this threshold. Filters out matchups too stalematey to be informative.
    """
    d = df.copy()
    nr = d["n_runs"].clip(lower=1)

    if exclude_mirror_gear:
        same = (d["a_weapon"] == d["b_weapon"]) & (d["a_shield"] == d["b_shield"]) & (d["a_armor"] == d["b_armor"])
        d = d[~same].copy()
        nr = d["n_runs"].clip(lower=1)

    if same_mpc and "a_military_pursuit_count" in d.columns:
        d = d[(d["a_military_pursuit_count"] - d["b_military_pursuit_count"]).abs() <= mpc_tolerance].copy()
        nr = d["n_runs"].clip(lower=1)

    if min_decisive_rate is not None:
        dec_rate = (d["a_wins"] + d["b_wins"]) / nr
        d = d[dec_rate >= min_decisive_rate].copy()
        nr = d["n_runs"].clip(lower=1)

    if drop_mutual_wipes:
        denom = (d["a_wins"] + d["b_wins"] + d["indecisive"]).clip(lower=1)
        d["a_win_rate_nomw"] = d["a_wins"] / denom
        d["b_win_rate_nomw"] = d["b_wins"] / denom

    if decisive_only:
        denom = (d["a_wins"] + d["b_wins"]).clip(lower=1)
        d["a_win_rate_decisive"] = d["a_wins"] / denom
        d["b_win_rate_decisive"] = d["b_wins"] / denom
        # rows with zero decisive battles carry NaN-safe 0; flag them
        d["_no_decisive"] = (d["a_wins"] + d["b_wins"]) == 0

    return d


# ==============================================================================
# Build combat-stat extraction + high-level battle overview
# ==============================================================================

def build_stat_table(pool):
    """Per-build combat stats pulled off StaticArmy (the values that actually drive a battle):
    to_hit target, normal-skirmish initiative, base armor save, effective save (armor + shield),
    starting endurance, weapon AP, shaking value. Returns a DataFrame keyed by build name so it
    can be joined to summary/matchups by name. These are NOT in the tournament CSV (they're army
    properties, not battle outcomes), so we reconstruct them here.

    Lower to_hit / save targets are BETTER (you hit on a lower roll). AP is negative (more
    negative = more armor-piercing). Initiative higher = strikes first.
    """
    import pandas as pd
    from vectorized_combat import StaticArmy
    rows = []
    for ld in pool:
        try:
            sa = StaticArmy(ld, is_attacker=True)
        except Exception:
            continue
        eff_save = max(2, sa.armor_save - getattr(sa, "shield_bonus_start", 0))  # shield lowers (improves) target
        rows.append({
            "name": ld.name,
            "retinue": ld.retinue,
            "to_hit": sa.to_hit,
            "init": sa.init_normal,
            "init_first": sa.init_first,
            "armor_save": sa.armor_save,
            "eff_save": eff_save,
            "endurance": sa.endurance_start,
            "weapon_ap": sa.ap_normal,
            "shaking": sa.shaking,
            "has_shield": bool(getattr(sa, "has_shield", False)),
            "unshakable": bool(getattr(sa, "unshakable", False)),
            "military_pursuit_count": getattr(ld, "military_pursuit_count", 0),
        })
    return pd.DataFrame(rows)


def battle_overview(df, n_runs=None):
    """High-level, battle-as-the-unit aggregates over the whole matchups dataframe.

    Treats each battle (one run of one matchup) as the observational unit and reports the rates
    that describe 'what a typical battle looks like': decisive win/loss split, mutual-wipe rate,
    indecisive rate, survivor counts, kill mix (combat vs shake vs rout), and battle length.
    Returns a dict of scalar stats.
    """
    nr = df["n_runs"].clip(lower=1)
    N = nr.sum()
    def wsum(col):  # weighted total across all battles
        return (df[col]).sum() if col in ("a_wins","b_wins","mut_wipe","indecisive") else None
    total_battles = int(N)
    a_w = df["a_wins"].sum(); b_w = df["b_wins"].sum()
    mw = df["mut_wipe"].sum(); ind = df["indecisive"].sum()
    # per-battle means (weight each matchup row by its battle count via the *_avg columns)
    def wmean(col):
        return float((df[col] * nr).sum() / N)
    out = {
        "total_battles": total_battles,
        "decisive_rate": (a_w + b_w) / N,
        "attacker_win_rate": a_w / N,
        "defender_win_rate": b_w / N,
        "mutual_wipe_rate": mw / N,
        "indecisive_rate": ind / N,
        "avg_skirmishes": wmean("avg_skirm"),
        "avg_attacker_survivors": wmean("avg_a_rem"),
        "avg_defender_survivors": wmean("avg_b_rem"),
        # kill mix: how the killed-by-A casualties (i.e. B's losses) break down
        "avg_kills_combat": wmean("avg_a_killed_combat"),
        "avg_kills_shake": wmean("avg_a_killed_shake"),
        "avg_kills_waver": wmean("avg_a_killed_waver") if "avg_a_killed_waver" in df.columns else 0.0,
        "avg_kills_rout": wmean("avg_a_killed_rout"),
        "avg_shield_destroyed_rate": wmean("a_shield_destroyed_rate"),
    }
    total_kills = out["avg_kills_combat"] + out["avg_kills_shake"] + out["avg_kills_waver"] + out["avg_kills_rout"]
    out["kill_mix_combat_pct"] = out["avg_kills_combat"] / total_kills if total_kills else 0.0
    out["kill_mix_shake_pct"]  = out["avg_kills_shake"]  / total_kills if total_kills else 0.0
    out["kill_mix_waver_pct"]  = out["avg_kills_waver"]  / total_kills if total_kills else 0.0
    out["kill_mix_rout_pct"]   = out["avg_kills_rout"]   / total_kills if total_kills else 0.0
    return out


def stat_winrate_correlation(summary_df, stat_df, stats=None):
    """Join per-build combat stats to per-build win rate and report Pearson correlation of each
    stat with win_rate, plus win rate bucketed by each stat value. Tells you which underlying
    combat property most moves the needle.
    """
    import pandas as pd
    stats = stats or ["to_hit", "init", "eff_save", "endurance", "weapon_ap", "shaking"]
    m = summary_df.merge(stat_df, on="name", suffixes=("", "_stat"))
    corr = {}
    for s in stats:
        if s in m.columns and m[s].std() > 0:
            corr[s] = m["win_rate"].corr(m[s])
    corr_df = pd.DataFrame({"stat": list(corr), "corr_with_win_rate": list(corr.values())})
    corr_df = corr_df.sort_values("corr_with_win_rate", key=lambda x: x.abs(), ascending=False).reset_index(drop=True)
    return m, corr_df


def dominance_frontier(df, n_runs_per_matchup=None, mpc_col="a_military_pursuit_count"):
    """Pareto/dominance analysis: which builds are STRICTLY DOMINATED (another build is cheaper-or-
    equal in MPC AND has a higher overall win rate). Dominated builds are trap picks — no reason to
    field them. A healthy meta has few dominated builds and a frontier that rises smoothly with cost.

    Returns (frontier_df, dominated_df):
      frontier_df  — the non-dominated builds (the Pareto frontier), sorted by mpc then win_rate.
                     These are the 'efficient' choices: nothing cheaper wins more.
      dominated_df — dominated builds, each with the cheaper/stronger build that dominates it and by
                     how much (win_rate_gap, mpc_saved). Sorted by win_rate_gap (worst traps first).

    Read it as: a long dominated list = lots of wasted design space (those builds need buffs or a cost
    cut). A flat frontier (win rate ~constant as MPC rises) = MPC isn't buying power. A cliff in the
    frontier = one cost breakpoint that suddenly dominates."""
    g = df.groupby("a_name").agg(
        win_rate=("a_win_rate", "mean"),
        mpc=(mpc_col, "first"),
        retinue=("a_retinue", "first"),
    ).reset_index().rename(columns={"a_name": "name"})
    g = g.dropna(subset=["mpc", "win_rate"])
    rows_front, rows_dom = [], []
    arr = g.to_dict("records")
    for b in arr:
        # b is dominated if any other build has mpc <= b.mpc AND win_rate > b.win_rate (strict on wr,
        # with a tiny epsilon so near-ties aren't called domination).
        dominators = [o for o in arr
                      if o["name"] != b["name"]
                      and o["mpc"] <= b["mpc"]
                      and o["win_rate"] > b["win_rate"] + 0.02]
        if dominators:
            best = max(dominators, key=lambda o: (o["win_rate"] - b["win_rate"]) + (b["mpc"] - o["mpc"]) * 0.001)
            rows_dom.append({
                "name": b["name"], "retinue": b["retinue"], "mpc": b["mpc"],
                "win_rate": round(b["win_rate"], 3),
                "dominated_by": best["name"], "dom_mpc": best["mpc"],
                "dom_win_rate": round(best["win_rate"], 3),
                "win_rate_gap": round(best["win_rate"] - b["win_rate"], 3),
                "mpc_saved": b["mpc"] - best["mpc"],
            })
        else:
            rows_front.append({"name": b["name"], "retinue": b["retinue"],
                               "mpc": b["mpc"], "win_rate": round(b["win_rate"], 3)})
    front = pd.DataFrame(rows_front).sort_values(["mpc", "win_rate"], ascending=[True, False]).reset_index(drop=True)
    dom = pd.DataFrame(rows_dom).sort_values("win_rate_gap", ascending=False).reset_index(drop=True) if rows_dom else pd.DataFrame()
    return front, dom


def cheapest_counter(df, win_threshold=0.55, mpc_col="a_military_pursuit_count"):
    """For each build, find the CHEAPEST opponent that beats it at >= win_threshold. A build whose
    only effective counters cost MORE than it does is oppressive — you can't answer it on-budget.

    Returns a DataFrame, one row per build (as the loser/target), with:
      target, target_mpc, target_win_rate (target's overall win rate)
      best_counter, counter_mpc, counter_win_pct (how hard the counter beats the target)
      counter_mpc_premium = counter_mpc - target_mpc  (>0 means you must overpay to answer it)
      n_counters = how many builds beat it >= threshold at all
    Sorted by counter_mpc_premium DESC then n_counters ASC, so the builds that are hardest to answer
    on-or-under budget (and have the fewest counters) sit at the top — your over-tuned suspects."""
    # B beats A means b_win_rate high; we want, for each A (target), the opponents B that beat it.
    d = df[["a_name", "b_name", "a_win_rate", "b_win_rate",
            "a_military_pursuit_count", "b_military_pursuit_count"]].copy()
    # overall win rate + mpc per build
    wr = df.groupby("a_name")["a_win_rate"].mean()
    mpc = df.groupby("a_name")[mpc_col].first()
    rows = []
    for target, sub in d.groupby("a_name"):
        # opponents B that beat this target at >= threshold (B's win rate vs A)
        beaten = sub[sub["b_win_rate"] >= win_threshold]
        t_mpc = mpc.get(target, float("nan"))
        if beaten.empty:
            rows.append({"target": target, "target_mpc": t_mpc,
                         "target_win_rate": round(wr.get(target, float("nan")), 3),
                         "best_counter": None, "counter_mpc": None, "counter_win_pct": None,
                         "counter_mpc_premium": None, "n_counters": 0})
            continue
        cheapest = beaten.loc[beaten["b_military_pursuit_count"].idxmin()]
        rows.append({
            "target": target, "target_mpc": t_mpc,
            "target_win_rate": round(wr.get(target, float("nan")), 3),
            "best_counter": cheapest["b_name"],
            "counter_mpc": int(cheapest["b_military_pursuit_count"]),
            "counter_win_pct": round(cheapest["b_win_rate"], 3),
            "counter_mpc_premium": int(cheapest["b_military_pursuit_count"] - t_mpc),
            "n_counters": int(len(beaten)),
        })
    out = pd.DataFrame(rows)
    # uncounterable (n_counters==0) first, then by mpc premium desc
    out["_sort"] = out["n_counters"].eq(0).astype(int) * 1000 + out["counter_mpc_premium"].fillna(-999)
    return out.sort_values("_sort", ascending=False).drop(columns="_sort").reset_index(drop=True)


def tag_synergy_matrix(df, tags=None, min_support=30):
    """Pairwise tag SYNERGY: for each pair of tags (i,j), the win rate of builds carrying BOTH minus
    the additive expectation (solo_i + solo_j - baseline). Positive = the combo over-performs its
    parts (a synergy power-spike to watch); negative = anti-synergy/redundancy.

    Solo effect of a tag = mean win rate of builds with it minus the global mean. Expected joint =
    global_mean + solo_i + solo_j. Synergy = actual_joint - expected_joint.

    Returns a DataFrame of pairs (tag_a, tag_b, n_both, wr_both, expected, synergy) sorted by
    |synergy| desc, keeping only pairs with >= min_support builds carrying both. tags=None auto-
    detects every tag present. Use it to catch combos like Parry+Riposte spiking above their solo sum."""
    bwr = df.groupby("a_name").agg(win_rate=("a_win_rate", "mean"),
                                   tags=("a_tags", "first")).reset_index()
    bwr["tagset"] = bwr["tags"].fillna("").apply(lambda s: set(t for t in s.split(",") if t))
    global_mean = bwr["win_rate"].mean()
    if tags is None:
        from collections import Counter
        c = Counter()
        for ts in bwr["tagset"]:
            for t in ts: c[t] += 1
        tags = [t for t, n in c.items() if n >= min_support]
    solo = {}
    for t in tags:
        has = bwr[bwr["tagset"].apply(lambda s: t in s)]
        if len(has) >= min_support:
            solo[t] = has["win_rate"].mean() - global_mean
    tags = sorted(solo.keys())
    rows = []
    for i in range(len(tags)):
        for j in range(i + 1, len(tags)):
            ta, tb = tags[i], tags[j]
            both = bwr[bwr["tagset"].apply(lambda s: ta in s and tb in s)]
            if len(both) < min_support:
                continue
            actual = both["win_rate"].mean()
            expected = global_mean + solo[ta] + solo[tb]
            rows.append({"tag_a": ta, "tag_b": tb, "n_both": len(both),
                         "wr_both": round(actual, 3), "expected": round(expected, 3),
                         "synergy": round(actual - expected, 3)})
    out = pd.DataFrame(rows)
    if len(out):
        out = out.reindex(out["synergy"].abs().sort_values(ascending=False).index).reset_index(drop=True)
    return out


def intransitivity(df, win_margin=0.55, max_builds=400, seed=2026):
    """Rock-paper-scissors health check. Counts 3-cycles (A beats B, B beats C, C beats A) in the
    win matrix. Cycles = non-transitive depth: no single build dominates, counters exist, the meta
    has real strategy. Near-zero cycles = a strict power LADDER that collapses to 'play the top build'.

    A directed edge A->B exists when A beats B at >= win_margin (A's win rate vs B). We count directed
    3-cycles and report the cycle DENSITY = cycles / all-possible-triangles-with-3-edges, plus the raw
    count. For tractability the build set is capped at max_builds (random sample if larger).

    Returns dict: n_builds, n_edges, n_3cycles, n_triads_3edge, intransitivity_ratio (cycles among
    fully-connected triads), and interpretation. Higher ratio = healthier (more RPS); ~0 = solved ladder."""
    import numpy as np
    builds = sorted(set(df["a_name"]) | set(df["b_name"]))
    rng = np.random.default_rng(seed)
    if len(builds) > max_builds:
        builds = list(rng.choice(builds, size=max_builds, replace=False))
    idx = {b: i for i, b in enumerate(builds)}
    n = len(builds)
    beats = np.zeros((n, n), dtype=bool)
    sub = df[df["a_name"].isin(idx) & df["b_name"].isin(idx)]
    for a_name, b_name, awr in zip(sub["a_name"], sub["b_name"], sub["a_win_rate"]):
        if awr >= win_margin:
            beats[idx[a_name], idx[b_name]] = True
    n_edges = int(beats.sum())
    # count directed 3-cycles i->j->k->i
    n_cyc = 0
    n_triad3 = 0  # triads with all 3 directed edges present (in some orientation)
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                e = (beats[i, j], beats[j, i], beats[j, k], beats[k, j], beats[i, k], beats[k, i])
                edge_ij = beats[i, j] or beats[j, i]
                edge_jk = beats[j, k] or beats[k, j]
                edge_ik = beats[i, k] or beats[k, i]
                if edge_ij and edge_jk and edge_ik:
                    n_triad3 += 1
                    # cycle if i->j->k->i or i->k->j->i
                    if (beats[i, j] and beats[j, k] and beats[k, i]) or \
                       (beats[i, k] and beats[k, j] and beats[j, i]):
                        n_cyc += 1
    ratio = (n_cyc / n_triad3) if n_triad3 else 0.0
    interp = ("healthy RPS depth" if ratio > 0.20 else
              "mostly transitive (mild ladder)" if ratio > 0.08 else
              "near-solved power ladder — little counterplay")
    return {"n_builds": n, "n_edges": n_edges, "n_3cycles": n_cyc,
            "n_triads_3edge": n_triad3, "intransitivity_ratio": round(ratio, 4),
            "interpretation": interp}


if __name__ == "__main__":
    df = load_tournament()
    print_summary(df, n=10)