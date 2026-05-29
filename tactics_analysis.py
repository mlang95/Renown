"""
Tactics analysis — empirically find which tactic each loadout/equipment combo prefers.

Approach: simulate the loadout playing each tactic 100% of the time against a reference field
(or against random-tactic opponents). Compare win rates. The "preferred tactic" is the one
that gives the highest win rate; the "anti-tactic" is the worst.

This produces, for every loadout:
  - preferred_tactic: best single tactic
  - second_best: runner-up
  - worst_tactic: avoid this
  - tactic_sensitivity: max_win_rate - min_win_rate (how much does the choice matter?)
  - profile: full 7-way win rate distribution across tactics (including Fall Back)
"""

import numpy as np
import pandas as pd
from renown_combat import TACTICS
from vectorized_combat import run_matchup_vec
from playstyles import _weights_from_primaries


# Build "pure tactic" playstyles dynamically by registering single-tactic primaries.
# Engine accepts a playstyle name; we'll handle these specially with custom weight inject.

def _make_pure_tactic_playstyle(tactic_idx, primary_weight=0.95):
    """Returns a tactic-weight vector that picks the given tactic ~95% of the time."""
    return _weights_from_primaries([tactic_idx], primary_weight=primary_weight)


PURE_TACTIC_WEIGHTS = {t: _make_pure_tactic_playstyle(i) for i, t in enumerate(TACTICS)}


def run_pure_tactic_matchup(ld_a, ld_b, a_tactic_idx, n_runs=300, seed=42):
    """Run a matchup where A always plays a specific tactic, B plays randomly.
    Hack: we monkeypatch resolve_playstyle_weights for this call.
    
    Cleaner: just pass a playstyle whose primaries = [tactic_idx]. We'll create a temp
    playstyle name in the engine.
    """
    # Easier: use the engine directly with a custom playstyle name by registering it
    # at module-import time. We'll do this in tactics_profile_for_loadout instead.
    raise NotImplementedError("Use tactics_profile_for_loadout instead.")


def tactics_profile_for_loadout(loadout, opponents, n_runs=200, seed=42):
    """For a single loadout, run it under each of the 7 pure-tactic playstyles
    against the given list of opponents. Returns per-tactic mean win rate.

    To inject a pure tactic, we register a temporary playstyle in playstyles.STATIC_PLAYSTYLES.
    """
    import playstyles
    results = {}
    for tac_idx, tac_name in enumerate(TACTICS):
        ps_name = f"_Pure_{tac_name.replace(' ', '_')}"
        playstyles.STATIC_PLAYSTYLES[ps_name] = {
            "primaries": [tac_idx],
            "description": f"Pure {tac_name} (95% weight)",
            "good_for": "internal tactics analysis",
        }
        wins = 0
        total_battles = 0
        for j, opp in enumerate(opponents):
            r = run_matchup_vec(loadout, opp, n_runs=n_runs, seed=seed + j * 13,
                               a_playstyle=ps_name)
            wins += r["a_wins"]
            total_battles += n_runs
        results[tac_name] = wins / total_battles if total_battles else 0.0
        # Clean up the temp playstyle
        del playstyles.STATIC_PLAYSTYLES[ps_name]
    return results


def tactics_matrix_analysis(loadouts, opponents=None, n_runs=200, seed=42, verbose=False):
    """For each loadout in `loadouts`, compute its tactics profile against `opponents`
    (defaults to the same loadouts list - field test).
    Returns a DataFrame: one row per loadout, columns = win rate per tactic + summary cols.
    """
    if opponents is None:
        opponents = loadouts
    rows = []
    for i, ld in enumerate(loadouts):
        if verbose:
            print(f"[{i+1}/{len(loadouts)}] {ld.name}")
        profile = tactics_profile_for_loadout(ld, opponents, n_runs=n_runs, seed=seed + i * 1009)
        # Summary
        sorted_tactics = sorted(profile.items(), key=lambda kv: -kv[1])
        best, second = sorted_tactics[0], sorted_tactics[1]
        worst = sorted_tactics[-1]
        sensitivity = best[1] - worst[1]
        row = {"name": ld.name, "retinue": ld.retinue, "weapon": ld.weapon,
               "armor": ld.armor, "shield": ld.shield or "", "ranged": ld.ranged or "",
               "tags": ",".join(ld.extra_tags),
               "preferred_tactic": best[0], "best_win_rate": best[1],
               "second_best_tactic": second[0], "second_best_win_rate": second[1],
               "worst_tactic": worst[0], "worst_win_rate": worst[1],
               "tactic_sensitivity": sensitivity}
        for t in TACTICS:
            row[f"wr_{t.replace(' ', '_')}"] = profile[t]
        rows.append(row)
    return pd.DataFrame(rows)


def best_tactic_by_equipment(df_profile, group_by=("retinue", "weapon", "armor")):
    """Aggregate: for each equipment combination, what's the most-preferred tactic?
    df_profile is the output of tactics_matrix_analysis.
    """
    if isinstance(group_by, str):
        group_by = (group_by,)
    return df_profile.groupby(list(group_by))["preferred_tactic"].agg(
        lambda x: x.value_counts().index[0]).reset_index()


def tactic_choice_value(df_profile):
    """How much does picking the right tactic matter, on average?
    Returns per-loadout tactic_sensitivity (best - worst tactic win rate spread).
    """
    return df_profile[["name", "retinue", "weapon", "armor", "tags",
                       "preferred_tactic", "best_win_rate",
                       "worst_tactic", "worst_win_rate",
                       "tactic_sensitivity"]].sort_values("tactic_sensitivity", ascending=False)


def tactic_field_distribution(df_profile):
    """How often is each tactic the preferred tactic across the field?
    Tells you which tactics are 'good' in general (vs niche).
    """
    counts = df_profile["preferred_tactic"].value_counts()
    pct = counts / counts.sum() * 100
    return pd.DataFrame({"n_loadouts": counts, "pct_of_field": pct})


def tactic_winrate_by_retinue(df_profile):
    """For each retinue tier, what's the average win rate under each tactic?"""
    rows = []
    for retinue, grp in df_profile.groupby("retinue"):
        row = {"retinue": retinue}
        for t in TACTICS:
            col = f"wr_{t.replace(' ', '_')}"
            row[t] = grp[col].mean()
        rows.append(row)
    return pd.DataFrame(rows)


def _matrix_worker_init():
    """Per-worker init: install the matrix and register pure-tactic playstyles."""
    import renown_combat
    from normalized_matrix import build_normalized_matrix
    from vectorized_combat import invalidate_tactic_tables
    import playstyles
    renown_combat.TACTIC_MATRIX.clear()
    renown_combat.TACTIC_MATRIX.update(build_normalized_matrix())
    invalidate_tactic_tables()
    for i, t in enumerate(TACTICS):
        ps_name = f"_pure_{t.replace(' ', '_')}"
        playstyles.STATIC_PLAYSTYLES[ps_name] = {
            "primaries": [i],
            "description": f"Pure {t} (95% weight)",
            "good_for": "matrix analysis",
        }


def _matrix_worker(args):
    """Per-loadout worker: run the 7x7 grid for one (loadout, opponent_loadout) pair."""
    ld_idx, ld, opp, n_runs, seed_base, pure_names_dict = args
    from vectorized_combat import run_matchup_vec
    win_rate = np.zeros((7, 7), dtype=np.float64)
    survival = np.zeros((7, 7), dtype=np.float64)
    skirm = np.zeros((7, 7), dtype=np.float64)
    indec = np.zeros((7, 7), dtype=np.float64)
    for i, my_tac in enumerate(TACTICS):
        for j, opp_tac in enumerate(TACTICS):
            r = run_matchup_vec(ld, opp, n_runs=n_runs,
                                seed=seed_base + ld_idx * 49 + i * 7 + j,
                                a_playstyle=pure_names_dict[my_tac],
                                b_playstyle=pure_names_dict[opp_tac])
            win_rate[i, j] = r["a_wins"] / n_runs
            survival[i, j] = r["avg_a_rem"]
            skirm[i, j] = r["avg_skirm"]
            indec[i, j] = r["indecisive"] / n_runs
    return ld_idx, win_rate, survival, skirm, indec


def empirical_tactic_matrix(loadouts, opponents=None, n_runs=100, seed=42, verbose=False, n_workers=1):
    """For each pair (my_tactic, opp_tactic), measure the empirical win rate
    averaged across all (loadout, opponent_loadout) combinations.

    For each loadout, we use the same loadout as opponent (mirror) — this isolates
    tactic value from equipment differences. Returns a 7x7 DataFrame indexed by
    'my_tactic' / 'opp_tactic'.

    Per-cell methodology:
      - For each loadout in the pool, force A to play one specific tactic (95% weight)
        and B to play another. Run n_runs battles.
      - Average the win rate across loadouts to get the cell value.

    Total work: len(loadouts) × 7 × 7 × n_runs battles.
    n_workers: 1 for sequential, mp.cpu_count() for max parallelism.
    """
    if opponents is None:
        opponents = loadouts

    import playstyles
    from vectorized_combat import run_matchup_vec

    # Register all 7 pure-tactic playstyles in main process
    pure_names = {}
    for i, t in enumerate(TACTICS):
        ps_name = f"_pure_{t.replace(' ', '_')}"
        playstyles.STATIC_PLAYSTYLES[ps_name] = {
            "primaries": [i],
            "description": f"Pure {t} (95% weight)",
            "good_for": "matrix analysis",
        }
        pure_names[t] = ps_name

    # 7x7 result accumulator
    win_rate_grid = np.zeros((7, 7), dtype=np.float64)
    survival_grid = np.zeros((7, 7), dtype=np.float64)
    skirm_grid = np.zeros((7, 7), dtype=np.float64)
    indec_grid = np.zeros((7, 7), dtype=np.float64)

    # Pair loadouts with opponents (mirror — same as ld unless opponents differs in length)
    # For the standard "mirror" mode, opponents == loadouts so opp = loadouts[ld_idx].
    # Default behavior: each loadout uses itself as opponent.
    use_mirror = opponents is loadouts or len(opponents) == len(loadouts)
    tasks = []
    for ld_idx, ld in enumerate(loadouts):
        opp = opponents[ld_idx] if use_mirror else ld
        tasks.append((ld_idx, ld, opp, n_runs, seed, pure_names))

    if n_workers <= 1:
        # Sequential path
        for ld_idx, ld in enumerate(loadouts):
            if verbose:
                print(f"  [{ld_idx+1}/{len(loadouts)}] {ld.name}")
            _, wr, sv, sk, ind = _matrix_worker(tasks[ld_idx])
            win_rate_grid += wr
            survival_grid += sv
            skirm_grid += sk
            indec_grid += ind
    else:
        import multiprocessing as mp
        import time
        t0 = time.time()
        completed = 0
        total = len(loadouts)
        with mp.Pool(n_workers, initializer=_matrix_worker_init) as workers:
            for ld_idx, wr, sv, sk, ind in workers.imap_unordered(_matrix_worker, tasks, chunksize=1):
                win_rate_grid += wr
                survival_grid += sv
                skirm_grid += sk
                indec_grid += ind
                completed += 1
                if verbose and (completed % max(1, total // 10) == 0 or completed == total):
                    elapsed = time.time() - t0
                    eta = elapsed / completed * (total - completed)
                    print(f"  [{completed}/{total}] elapsed {elapsed:.0f}s, eta {eta:.0f}s", flush=True)

    # Clean up temporary playstyles in main process
    for ps_name in pure_names.values():
        del playstyles.STATIC_PLAYSTYLES[ps_name]

    # Average
    n = max(1, len(loadouts))
    win_rate_grid /= n
    survival_grid /= n
    skirm_grid /= n
    indec_grid /= n

    win_df = pd.DataFrame(win_rate_grid, index=TACTICS, columns=TACTICS)
    win_df.index.name = "my_tactic"
    win_df.columns.name = "opp_tactic"

    return {
        "win_rate": win_df,
        "survival": pd.DataFrame(survival_grid, index=TACTICS, columns=TACTICS),
        "skirm": pd.DataFrame(skirm_grid, index=TACTICS, columns=TACTICS),
        "indecisive": pd.DataFrame(indec_grid, index=TACTICS, columns=TACTICS),
    }


def tactic_marginal_value(matrix_result):
    """From an empirical_tactic_matrix result, compute per-tactic marginal value
    (average win rate when playing this tactic, vs uniformly-distributed opponent).
    """
    wr = matrix_result["win_rate"]
    return pd.DataFrame({
        "avg_win_rate": wr.mean(axis=1),       # avg vs all opponent tactics
        "best_matchup": wr.max(axis=1),
        "best_vs": wr.idxmax(axis=1),
        "worst_matchup": wr.min(axis=1),
        "worst_vs": wr.idxmin(axis=1),
        "win_rate_spread": wr.max(axis=1) - wr.min(axis=1),
    }).sort_values("avg_win_rate", ascending=False)


def tactic_counter_value(matrix_result):
    """From the matrix, identify which tactics most strongly counter others.
    Returns a DataFrame where row tactics is the counter, col tactic is what's being countered,
    and the value is how much A wins when playing row vs col."""
    return matrix_result["win_rate"]
