# parity_harness.py
import numpy as np, random
from loadouts import balanced_validation_pool
from vectorized_combat import run_matchup_vec
from batch_engine import run_batch_random

pool = balanced_validation_pool(mpc_min=14, mpc_max=14, per_cell=8, seed=1)
print(f"pool size: {len(pool)}")
random.seed(1)
k = min(40, len(pool))
sample = random.sample(pool, k)
pairs = [(sample[i], sample[(i + 1) % len(sample)]) for i in range(len(sample))]

N_RUNS, SEED = 200, 12345
batch = run_batch_random(pairs, n_runs=N_RUNS, seed=SEED, mode="random")

mism = 0
for k, (la, lb) in enumerate(pairs):
    v = run_matchup_vec(la, lb, n_runs=N_RUNS, seed=SEED, alternate_attacker=True)
    bw_a, bw_b = int(batch["a_wins"][k]), int(batch["b_wins"][k])
    da, db = abs(v["a_wins"] - bw_a), abs(v["b_wins"] - bw_b)
    if da > 0.05 * N_RUNS or db > 0.05 * N_RUNS:
        mism += 1
        print(f"MISMATCH {la.name[:28]} vs {lb.name[:28]}: "
              f"vec=({v['a_wins']},{v['b_wins']}) batch=({bw_a},{bw_b})")
print(f"\n{mism}/{len(pairs)} mismatched beyond 5% tolerance")
print("PARITY OK" if mism == 0 else "PARITY FAIL — engines disagree")