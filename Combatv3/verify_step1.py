"""Step-1 gate: run on YOUR machine with numba ON, after wiping the cache.
  set NUMBA_CACHE_DIR=C:\\numba_cache
  rmdir /s /q C:\\numba_cache
  py verify_step1.py
Confirms the SHARED kernel (now imported by vectorized_combat) compiles and is correct."""
import numpy as np
import combat_kernel as ck

print("PARRY_BEFORE_SAVE (canon, want True):", ck.PARRY_BEFORE_SAVE)
print("_HAS_NUMBA (want True on your box):", ck._HAS_NUMBA)

r  = np.full((1, 20), 4, dtype=np.int8)
c  = np.full((1, 20), 4, dtype=np.int8)
fl = np.array([10], dtype=np.int64); th = np.array([2], dtype=np.int64)
af = np.array([False]); ap = np.array([False])
s4, d4, p4 = ck._strikes_kernel(r, c, fl, th, af, ap, True, False, 4, False)
s6, d6, p6 = ck._strikes_kernel(r, c, fl, th, af, ap, True, False, 6, False)
print(f"floor=4 -> strikes={s4[0]} deadly={d4[0]} procs={p4[0]}  (want 10,10,0)")
print(f"floor=6 -> strikes={s6[0]} deadly={d6[0]} procs={p6[0]}  (want 10,0,0)")

ok = (d4[0] == 10 and d6[0] == 0 and ck.PARRY_BEFORE_SAVE is True)
# Confirm the engine still imports with the shared modules.
try:
    import vectorized_combat  # noqa
    print("vectorized_combat imports against shared kernel: OK")
except Exception as e:
    ok = False
    print("IMPORT FAILED:", e)

print("STEP 1 PASS — proceed to batch port" if ok else "STEP 1 FAIL — do not proceed")
