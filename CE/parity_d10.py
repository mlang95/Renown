#!/usr/bin/env python3
"""parity_d10.py — batch_engine and vectorized_combat must agree within dice noise.

Runs the same matchups through both engines and flags any pair whose win counts differ by more
than Z standard errors (difference of two independent binomials). Run from the CE folder:
    python parity_d10.py                 # 60 random pairs, 2000 runs each
    python parity_d10.py --pairs 150 --runs 4000 --z 3.5
Exit code 1 if any pair is out of tolerance.
"""
import argparse, os, sys
ap = argparse.ArgumentParser()
ap.add_argument("--pairs", type=int, default=60)
ap.add_argument("--runs", type=int, default=2000)
ap.add_argument("--z", type=float, default=3.5)
ap.add_argument("--seed", type=int, default=7)
args = ap.parse_args()
import ce_paths
ce_paths.install(verbose=False)
import numpy as np, loadouts as L, vectorized_combat as vc, batch_engine as be

pool = L.balanced_validation_pool(mpc_min=4, mpc_max=13, per_cell=3)
rng = np.random.default_rng(args.seed)
idx = rng.integers(0, len(pool), size=(args.pairs, 2))
pairs = [(pool[i], pool[j]) for i, j in idx if i != j]
n = args.runs
bw = be.run_batch_random(pairs, n_runs=n, seed=args.seed)["a_wins"]
bad, zs = [], []
for k, (a, b) in enumerate(pairs):
    v = vc.run_matchup_vec(a, b, n_runs=n, seed=args.seed + k)["a_wins"]
    x = int(bw[k]); p = (x + v) / (2 * n)
    se = max(np.sqrt(2 * n * p * (1 - p)), 1.0)
    z = (x - v) / se; zs.append(z)
    if abs(z) > args.z:
        bad.append((z, x, v, a, b))
zs = np.array(zs)
print(f"pairs {len(pairs)}  runs {n}  mean z {zs.mean():+.2f}  sd z {zs.std():.2f}  max |z| {np.abs(zs).max():.2f}")
for z, x, v, a, b in sorted(bad, key=lambda t: -abs(t[0])):
    print(f"  z={z:+.1f}  batch {x}  vec {v}  |  {a.name}  vs  {b.name}")
print("PARITY OK" if not bad else f"PARITY FAIL ({len(bad)} pairs beyond {args.z} SE)")
sys.exit(1 if bad else 0)
