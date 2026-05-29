"""
Cross-loadout tactic sweep.

For every (loadout_A, loadout_B) pair, run every (tactic_A, tactic_B) matchup.
Produces:
- Per-tactic-pair win rates averaged across ALL loadout combos (true tactic-only matrix)
- Per-tactic-pair win rates for same-tier vs cross-tier matchups
- Variance decomposition: how much does tactic matter vs loadout?
- Hard-counter robustness: do tactic counters hold across resource gaps?
"""

import numpy as np
import pandas as pd
from itertools import product

TACTICS = ['Scout', 'Ambush', 'Flank', 'Charge',
           'Fighting Formation', 'Defensive Formation', 'Fall Back']


def _build_pure_tactic_resolver(playstyles_module):
    """Patch playstyles to support 'Pure:Scout' style pure-tactic playstyles."""
    TACTIC_IDX = {t: i for i, t in enumerate(TACTICS)}
    original_resolve = playstyles_module.resolve_playstyle_weights

    def patched_resolve(playstyle_name, state, n_runs):
        if playstyle_name and playstyle_name.startswith('Pure:'):
            idx = TACTIC_IDX[playstyle_name[5:]]
            w = np.zeros(7); w[idx] = 1.0
            return np.tile(w, (n_runs, 1))
        return original_resolve(playstyle_name, state, n_runs)
    playstyles_module.resolve_playstyle_weights = patched_resolve
    return original_resolve


def run_cross_loadout_sweep(loadouts, n_runs=500, seed_base=42, verbose=True):
    """
    Run every loadout-pair × tactic-pair matchup.

    Returns a long-format DataFrame with one row per (loadout_a, loadout_b, tactic_a, tactic_b)
    combination, containing win rates and outcome distributions.

    Args:
        loadouts: list of (name, Loadout) tuples
        n_runs: number of runs per matchup (default 500 — 2401 matchups × 500 = 1.2M runs)
        seed_base: base seed for reproducibility
        verbose: print progress

    Returns:
        DataFrame with columns:
            loadout_a, loadout_b, tactic_a, tactic_b,
            a_wins_pct, b_wins_pct, mut_wipe_pct, indecisive_pct, avg_skirm
    """
    # Lazy imports so this module is loadable standalone
    from vectorized_combat import run_matchup_vec, invalidate_tactic_tables
    import playstyles
    _build_pure_tactic_resolver(playstyles)
    invalidate_tactic_tables()

    n_loadouts = len(loadouts)
    n_tactics = len(TACTICS)
    total = n_loadouts * n_loadouts * n_tactics * n_tactics
    if verbose:
        print(f"Running {n_loadouts}×{n_loadouts} loadouts × "
              f"{n_tactics}×{n_tactics} tactics = {total} matchups @ {n_runs} runs each")

    rows = []
    done = 0
    for la_idx, (la_name, la) in enumerate(loadouts):
        for lb_idx, (lb_name, lb) in enumerate(loadouts):
            for ti, ta in enumerate(TACTICS):
                for tj, tb in enumerate(TACTICS):
                    seed = seed_base + done  # unique per matchup
                    r = run_matchup_vec(
                        la, lb,
                        n_runs=n_runs, seed=seed,
                        a_playstyle=f'Pure:{ta}',
                        b_playstyle=f'Pure:{tb}',
                        attacker_mode='balanced',
                    )
                    rows.append({
                        'loadout_a': la_name,
                        'loadout_b': lb_name,
                        'tactic_a': ta,
                        'tactic_b': tb,
                        'a_wins_pct': 100 * r['a_wins'] / n_runs,
                        'b_wins_pct': 100 * r['b_wins'] / n_runs,
                        'mut_wipe_pct': 100 * r['mut_wipe'] / n_runs,
                        'indecisive_pct': 100 * r['indecisive'] / n_runs,
                        'avg_skirm': r['avg_skirm'],
                    })
                    done += 1
            if verbose:
                progress = done / total * 100
                print(f"  {la_name} vs {lb_name}: done ({progress:.1f}%)")
    return pd.DataFrame(rows)


def tactic_only_matrix(df):
    """Collapse loadout dimension: average win rates per tactic pair across ALL loadout combos."""
    grouped = df.groupby(['tactic_a', 'tactic_b']).agg({
        'a_wins_pct': 'mean',
        'b_wins_pct': 'mean',
        'mut_wipe_pct': 'mean',
        'indecisive_pct': 'mean',
        'avg_skirm': 'mean',
    }).reset_index()
    # Pivot to 7x7 matrix
    return grouped.pivot(index='tactic_a', columns='tactic_b', values='a_wins_pct').reindex(
        index=TACTICS, columns=TACTICS)


def tactic_matrix_same_tier(df, tier_groups):
    """
    Win-rate matrix restricted to same-tier matchups.

    tier_groups: dict mapping tier name to list of loadout names.
    """
    same_tier_pairs = set()
    for tier, lds in tier_groups.items():
        for a in lds:
            for b in lds:
                same_tier_pairs.add((a, b))
    sub = df[df.apply(lambda r: (r['loadout_a'], r['loadout_b']) in same_tier_pairs, axis=1)]
    return sub.groupby(['tactic_a', 'tactic_b'])['a_wins_pct'].mean().unstack().reindex(
        index=TACTICS, columns=TACTICS)


def tactic_matrix_cross_tier(df, tier_groups):
    """Win-rate matrix restricted to CROSS-tier matchups (a's tier != b's tier)."""
    loadout_tier = {}
    for tier, lds in tier_groups.items():
        for ld in lds:
            loadout_tier[ld] = tier
    sub = df[df.apply(lambda r: loadout_tier.get(r['loadout_a']) != loadout_tier.get(r['loadout_b']), axis=1)]
    return sub.groupby(['tactic_a', 'tactic_b'])['a_wins_pct'].mean().unstack().reindex(
        index=TACTICS, columns=TACTICS)


def tactic_robustness(df):
    """
    For each tactic pair, how much does the loadout combo matter?

    Returns per-tactic-pair stats:
        - mean: average win rate across loadout combos
        - std: how much the win rate varies across loadout combos
        - min, max: extremes
    Low std = tactic dominates the matchup regardless of loadout.
    High std = loadout decides the matchup more than tactic.
    """
    return df.groupby(['tactic_a', 'tactic_b'])['a_wins_pct'].agg(
        ['mean', 'std', 'min', 'max']).reset_index()


def variance_decomposition(df):
    """
    Decompose total variance in win rates into tactic-attributable vs loadout-attributable.

    Returns a dict:
        tactic_variance: variance across tactic pairs (loadouts averaged)
        loadout_variance: variance across loadout pairs (tactics averaged)
        total_variance: overall variance
        tactic_share: tactic_variance / total
        loadout_share: loadout_variance / total
    """
    total_var = df['a_wins_pct'].var()
    # Mean per tactic pair (collapse loadouts) — variance of these means is tactic-attributable
    tactic_means = df.groupby(['tactic_a', 'tactic_b'])['a_wins_pct'].mean()
    tactic_var = tactic_means.var()
    # Mean per loadout pair (collapse tactics) — variance is loadout-attributable
    loadout_means = df.groupby(['loadout_a', 'loadout_b'])['a_wins_pct'].mean()
    loadout_var = loadout_means.var()
    return {
        'total_variance': total_var,
        'tactic_variance': tactic_var,
        'loadout_variance': loadout_var,
        'tactic_share': tactic_var / total_var,
        'loadout_share': loadout_var / total_var,
    }


def hard_counter_robustness(df, threshold=70):
    """
    For each tactic pair where the tactic-only average is a hard counter (>=threshold% win rate),
    show in how many loadout combos the counter still holds.

    threshold: % win rate to count as "still working"
    """
    grouped = df.groupby(['tactic_a', 'tactic_b'])
    rows = []
    for (ta, tb), g in grouped:
        avg = g['a_wins_pct'].mean()
        if avg < threshold:
            continue
        # How many loadout combos have a_wins >= 50% (counter holds in some form)?
        hold_50 = (g['a_wins_pct'] >= 50).mean() * 100
        hold_70 = (g['a_wins_pct'] >= 70).mean() * 100
        rows.append({
            'tactic_a': ta,
            'tactic_b': tb,
            'avg_win_rate': avg,
            'hold_at_50pp': hold_50,
            'hold_at_70pp': hold_70,
            'min_win_rate': g['a_wins_pct'].min(),
        })
    return pd.DataFrame(rows).sort_values('avg_win_rate', ascending=False).reset_index(drop=True)



def add_tier_flags(df, tier_groups):
    """Add columns: a_tier, b_tier, same_tier to the DataFrame."""
    loadout_tier = {}
    for tier, lds in tier_groups.items():
        for ld in lds:
            loadout_tier[ld] = tier
    df = df.copy()
    df['a_tier'] = df['loadout_a'].map(loadout_tier)
    df['b_tier'] = df['loadout_b'].map(loadout_tier)
    df['same_tier'] = df['a_tier'] == df['b_tier']
    return df


def per_tier_tactic_matrix(df, tier_groups, tier):
    """
    Tactic-vs-tactic win rate matrix restricted to a single retinue tier.
    Includes cross-equipment within the same retinue (e.g. Sgt/Halberd vs Sgt/Poleaxe).
    """
    df = add_tier_flags(df, tier_groups)
    sub = df[(df['a_tier'] == tier) & (df['b_tier'] == tier)]
    return sub.groupby(['tactic_a', 'tactic_b'])['a_wins_pct'].mean().unstack().reindex(
        index=TACTICS, columns=TACTICS)


def variance_decomposition_subset(df):
    """Variance decomposition for a pre-filtered subset of the data."""
    total_var = df['a_wins_pct'].var()
    tactic_means = df.groupby(['tactic_a', 'tactic_b'])['a_wins_pct'].mean()
    tactic_var = tactic_means.var()
    loadout_means = df.groupby(['loadout_a', 'loadout_b'])['a_wins_pct'].mean()
    loadout_var = loadout_means.var() if len(loadout_means) > 1 else 0
    return {
        'total_variance': total_var,
        'tactic_variance': tactic_var,
        'loadout_variance': loadout_var,
        'tactic_share': tactic_var / total_var if total_var > 0 else 0,
        'loadout_share': loadout_var / total_var if total_var > 0 else 0,
    }
