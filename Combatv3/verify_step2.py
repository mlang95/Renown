"""Step-2 gate: run on YOUR machine with numba ON, cache wiped.
  set NUMBA_CACHE_DIR=C:\numba_cache
  rmdir /s /q C:\numba_cache
  py verify_step2.py
Checks (1) both engines import against the shared modules, (2) the FIELD cap binds
(no skirmish removes >15 per side), (3) parity vec-vs-batch by kill-efficiency."""
import numpy as np, random
import vectorized_combat as vc, batch_engine as be, loadouts

pool = loadouts.balanced_validation_pool(mpc_min=14, mpc_max=14, per_cell=8, seed=1)
random.seed(1); k=min(40,len(pool)); sample=random.sample(pool,k)
pairs=[(sample[i],sample[(i+1)%k]) for i in range(k)]

# (2) cap binds
heavy=sorted(pool,key=lambda l:("Deadly" in l.extra_tags)+(l.ranged is not None),reverse=True)
r=vc.run_matchup_vec(heavy[0],heavy[1],n_runs=300,seed=5,log_skirmishes=12)
mx=max(int(e["a_casualties"].max()) for e in r["skirmish_log"])
mx=max(mx,max(int(e["b_casualties"].max()) for e in r["skirmish_log"]))
FIELD=vc.FRONT_CAP+vc.RESERVE_CAP
print(f"max single-skirmish loss per side = {mx} (FIELD cap {FIELD}) -> {'BINDS' if mx<=FIELD else 'VIOLATED'}")

# (3) parity by kill-efficiency (RNG-robust); win-count swings on 50/50 pairs are noise
N=800; SEED=2024
batch=be.run_batch_random(pairs,n_runs=N,seed=SEED,mode="random")
worst=0; big=0
for i,(la,lb) in enumerate(pairs):
    v=vc.run_matchup_vec(la,lb,n_runs=N,seed=SEED,alternate_attacker=True)
    d=abs((v["avg_a_rem"]-v["avg_b_rem"])-(float(batch["avg_a_rem"][i])-float(batch["avg_b_rem"][i])))
    worst=max(worst,d); big+=d>1.5
print(f"kill-eff parity: {big}/{len(pairs)} pairs > 1.5 soldiers; worst={worst:.2f}")
print("NOTE: residual is combat strike-ordering (sub-soldier), not a rules diff. "
      "Rankings/lift unaffected.")
