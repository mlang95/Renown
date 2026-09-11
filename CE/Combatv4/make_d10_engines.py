"""Generate *_d10.py engine files with FACES parameterised.

Sources: combat_primitives.py, combat_morale.py, combat_kernel.py, vectorized_combat.py
Every hardcoded 6 / 7 in a roll path becomes a reference to dice_config.
Assertions on each edit so a miss fails loudly.
"""
import re

CONFIG = '''"""dice_config — single source for die size across both combat engines.

Import this, never hardcode a face count. Changing FACES here changes every
threshold, RNG bound, cap clip and rout test in both the vectorized and scalar
engines simultaneously.
"""

FACES           = 10          # die size
FOCUSED_THR     = 10          # Focused fires on this natural result or higher
ROUT_THR        = FACES + 1   # modified Morale target >= this Routs
CAP_THR         = FACES       # worst printable target ("6+" ceiling on d6)
AUTO_PASS_FLOOR = 2           # target modified below this auto-passes; None deletes the rule
FATIGUE_STRIKE  = 2           # per-token Strike penalty (magnitude)
FATIGUE_MORALE  = 2           # per-token Morale penalty (magnitude)

# Derived helpers -------------------------------------------------------------
def p_success(target):
    """Probability a single die meets `target`+ (honours the auto-pass floor)."""
    if AUTO_PASS_FLOOR is not None and target < AUTO_PASS_FLOOR:
        return 1.0
    if target > FACES:
        return 0.0
    return (FACES - target + 1) / FACES


def p_fail(target):
    return 1.0 - p_success(target)
'''
open("dice_config.py", "w", encoding="utf-8").write(CONFIG)
print("wrote dice_config.py")

IMPORT = "from dice_config import FACES, FOCUSED_THR, ROUT_THR, CAP_THR, AUTO_PASS_FLOOR\n"


def patch(src, dst, edits, insert_after="import numpy as np"):
    s = open(src, encoding="utf-8").read()
    n = 0
    for old, new, cnt, label in edits:
        c = s.count(old)
        assert c == cnt, f"[{dst}:{label}] expected {cnt}, found {c}: {old[:60]!r}"
        s = s.replace(old, new)
        n += 1
    assert insert_after in s, f"{dst}: anchor {insert_after!r} not found"
    s = s.replace(insert_after, insert_after + "\n" + IMPORT, 1)
    open(dst, "w", encoding="utf-8").write(s)
    print(f"wrote {dst}  ({n} edits)")


# ── combat_primitives ────────────────────────────────────────────────────────
patch("combat_primitives.py", "combat_primitives_d10.py", [
    ("save_clipped = np.where(cap_active, np.minimum(save_clipped, 6), save_clipped)",
     "save_clipped = np.where(cap_active, np.minimum(save_clipped, CAP_THR), save_clipped)", 1, "save cap"),
    ("deadly_clipped = np.where(cap_active, np.minimum(deadly_clipped, 6), deadly_clipped)",
     "deadly_clipped = np.where(cap_active, np.minimum(deadly_clipped, CAP_THR), deadly_clipped)", 1, "deadly cap"),
    ("parry_thr = np.minimum(parry_thr, 6).astype(np.int64)",
     "parry_thr = np.minimum(parry_thr, CAP_THR).astype(np.int64)", 1, "parry cap"),
])

# ── combat_morale ────────────────────────────────────────────────────────────
patch("combat_morale.py", "combat_morale_d10.py", [
    ("Target >=7 -> panic-rout.", "Target >=ROUT_THR -> panic-rout.", 1, "doc1"),
    ("so Unshakable still ROUTS at >=7. Target >=7 -> break-rout.",
     "so Unshakable still ROUTS at >=ROUT_THR. Target >=ROUT_THR -> break-rout.", 1, "doc2"),
    ("any side whose shake target >=7 via panic-rout or break-rout",
     "any side whose shake target >=ROUT_THR via panic-rout or break-rout", 1, "doc3"),
    ("target = np.where(np.asarray(morale_cap_mask, dtype=bool), np.minimum(target, 6), target).astype(np.int64)",
     "target = np.where(np.asarray(morale_cap_mask, dtype=bool), np.minimum(target, CAP_THR), target).astype(np.int64)", 1, "morale cap"),
    ("panic_test = panic_trig & (target <= 6)", "panic_test = panic_trig & (target <= FACES)", 1, "panic test"),
    ("break_test = break_trig & (target <= 6) & (size > 0)",
     "break_test = break_trig & (target <= FACES) & (size > 0)", 1, "break test"),
])

# ── combat_kernel (scalar path) ──────────────────────────────────────────────
ck = open("combat_kernel.py", encoding="utf-8").read()
subs = [
    # the commented one FIRST — it contains "if rr == 6:" as a substring
    ("if rr == 6:        # Poison wounds: Recover only on a natural 6",
     "if rr >= FOCUSED_THR:        # Poison wounds: Recover only on a Focused roll", 1),
    ("if rr == 6:", "if rr >= FOCUSED_THR:", 2),
    ("if roll == 6:", "if roll >= FOCUSED_THR:", 2),
    ("if parry_before_save and pmask and pthr_eff <= 6:", "if parry_before_save and pmask and pthr_eff <= FACES:", 1),
    ("if (not parry_before_save) and pmask and pthr_eff <= 6:", "if (not parry_before_save) and pmask and pthr_eff <= FACES:", 1),
    ("if (not is_half) and rip_on and (pr == 6 or (rip5 and pr == 5 and pthr_eff <= 5)):",
     "if (not is_half) and rip_on and (pr >= FOCUSED_THR or (rip5 and pr >= FOCUSED_THR - 1 and pthr_eff <= FOCUSED_THR - 1)):", 2),
    ("if poi and roll == 6:", "if poi and roll >= FOCUSED_THR:", 1),
]
for old, new, cnt in subs:
    c = ck.count(old)
    assert c == cnt, f"[kernel] {old[:50]!r} expected {cnt}, found {c}"
    ck = ck.replace(old, new)
anchor = "import numpy as np" if "import numpy as np" in ck else ck.split("\n")[0]
ck = ck.replace(anchor, anchor + "\n" + IMPORT, 1)
open("combat_kernel_d10.py", "w", encoding="utf-8").write(ck)
print(f"wrote combat_kernel_d10.py  ({len(subs)} edit groups)")

# ── vectorized_combat ────────────────────────────────────────────────────────
vc = open("vectorized_combat.py", encoding="utf-8").read()
vsubs = [
    ("rng.integers(1, 7,", "rng.integers(1, FACES + 1,", 6, "RNG bounds"),
    ("return (7 - t) / 6.0  # rolls t..6 succeed",
     "return (FACES + 1 - t) / float(FACES)  # rolls t..FACES succeed", 1, "p_success"),
    ("return (s - 1) / 6.0  # rolls 1..s-1 fail",
     "return (s - 1) / float(FACES)  # rolls 1..s-1 fail", 1, "p_fail"),
    ("my_th = max(my_th, 6)", "my_th = max(my_th, CAP_THR)", 1, "trip cap A"),
    ("op_th = max(op_th, 6)", "op_th = max(op_th, CAP_THR)", 1, "trip cap B"),
    ("weights = np.full((n_runs, 7), (1 - counter_weight) / 6.0, dtype=np.float64)",
     "weights = np.full((n_runs, FACES + 1), (1 - counter_weight) / float(FACES), dtype=np.float64)", 1, "weights shape"),
    ("a_th_pre = np.minimum(a_static.to_hit + a_th_improve + a_fat, 6)",
     "a_th_pre = np.minimum(a_static.to_hit + a_th_improve + a_fat, CAP_THR)", 1, "a_th cap"),
    ("b_th_pre = np.minimum(b_static.to_hit + b_th_improve + b_fat, 6)",
     "b_th_pre = np.minimum(b_static.to_hit + b_th_improve + b_fat, CAP_THR)", 1, "b_th cap"),
    ("a_th_pre = np.where(a_tripped, np.maximum(a_th_pre, 6), a_th_pre)",
     "a_th_pre = np.where(a_tripped, np.maximum(a_th_pre, CAP_THR), a_th_pre)", 1, "a trip"),
    ("b_th_pre = np.where(b_tripped, np.maximum(b_th_pre, 6), b_th_pre)",
     "b_th_pre = np.where(b_tripped, np.maximum(b_th_pre, CAP_THR), b_th_pre)", 1, "b trip"),
    ("Saves roll d6; saves on roll >= save_target", "Saves roll dFACES; saves on roll >= save_target", 1, "docstring"),
]
for old, new, cnt, label in vsubs:
    c = vc.count(old)
    assert c == cnt, f"[vec:{label}] expected {cnt}, found {c}: {old[:60]!r}"
    vc = vc.replace(old, new)
vc = vc.replace("import numpy as np", "import numpy as np\n" + IMPORT, 1)
open("vectorized_combat_d10.py", "w", encoding="utf-8").write(vc)
print(f"wrote vectorized_combat_d10.py  ({len(vsubs)} edit groups)")
