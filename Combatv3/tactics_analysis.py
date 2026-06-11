"""Tactics analysis helpers for the Renown Combat Lab.

empirical_tactic_matrix: forced-tactics sweep. For each (a_tactic, b_tactic) pair, run every
ordered matchup in the sample with BOTH sides forced to that tactic for the whole battle, and
aggregate win rate / survival / avg skirmishes / indecisive rate into 7x7 DataFrames. Uses the
batched engine (mode="forced") so it stays fast on a stratified sample.
"""
import numpy as np
import pandas as pd

from renown_combat import TACTICS
import tournament_vec as _tv
import batch_engine as _be


def empirical_tactic_matrix(sample, n_runs=100, verbose=False, n_workers=1, base_seed=2026):
    """Return {"win_rate","survival","skirm","indecisive"} as 7x7 DataFrames indexed by TACTICS.

    n_workers is accepted for API compatibility with the old per-matchup implementation but is
    unused (the batched engine resolves each forced tactic-pair block in one vectorized pass).
    """
    nT = len(TACTICS)
    # Ordered, conflict-filtered pairs from the sample (same filtering as the tournament).
    pairs = [(a, b) for a in sample for b in sample
             if a is not b and not _tv._unique_conflict(a, b)]
    if verbose:
        print(f"empirical_tactic_matrix: {len(sample)} loadouts → {len(pairs):,} pairs, "
              f"{nT*nT} tactic cells × {n_runs} runs")

    wr = np.zeros((nT, nT)); surv = np.zeros((nT, nT))
    sk = np.zeros((nT, nT)); indec = np.zeros((nT, nT))
    npair = max(1, len(pairs))
    for i in range(nT):
        for j in range(nT):
            res = _be.run_batch_random(pairs, n_runs=n_runs, seed=base_seed + i * 131 + j * 17,
                                       mode="forced", force_a=i, force_b=j)
            tot = float(res["a_wins"].sum() + res["b_wins"].sum()
                        + res["mut_wipe"].sum() + res["indecisive"].sum())
            tot = tot or 1.0
            wr[i, j] = res["a_wins"].sum() / tot
            indec[i, j] = res["indecisive"].sum() / tot
            surv[i, j] = float(res["avg_a_rem"].sum()) / npair
            sk[i, j] = float(res["avg_skirm"].sum()) / npair
        if verbose:
            print(f"  row {i+1}/{nT} ({TACTICS[i]}) done")

    cols = list(TACTICS)
    return {
        "win_rate":   pd.DataFrame(wr,   index=cols, columns=cols),
        "survival":   pd.DataFrame(surv, index=cols, columns=cols),
        "skirm":      pd.DataFrame(sk,   index=cols, columns=cols),
        "indecisive": pd.DataFrame(indec, index=cols, columns=cols),
    }
