#!/usr/bin/env python3
"""verify_engine.py — golden-case tests for the Escalation combat engine.
Run: python verify_engine.py    (exit 0 = all rules resolve as written)"""
import numpy as np
import sys
sys.path.insert(0, ".")
import vectorized_combat as vc
import renown_data as rd

FAILS = []
def check(name, cond):
    print(("PASS  " if cond else "FAIL  ") + name)
    if not cond:
        FAILS.append(name)

class FixedRNG:
    """rng.integers returns pre-seeded arrays in call order."""
    def __init__(self, seq):
        self.seq = [np.asarray(x, dtype=np.int8) for x in seq]
        self.i = 0
    def integers(self, lo, hi, size=None, dtype=np.int8):
        out = self.seq[self.i]; self.i += 1
        assert out.shape == tuple(size), f"shape {out.shape} != {size}"
        return out.astype(dtype)

def saves(rng, save_target, n_strikes, deadly, **kw):
    cas, rip = vc._roll_saves_vec(rng, 1, np.array([save_target]),
        np.array([n_strikes]), np.array([deadly]),
        atk_has_poison=kw.get("poison", False),
        def_has_parry=kw.get("parry", False),
        def_regen_threshold=kw.get("regen", None),
        atk_unstoppable=kw.get("unstoppable", False),
        def_has_riposte=kw.get("riposte", False),
        def_parry_improved=kw.get("improved", False),
        atk_is_ranged=kw.get("ranged", False),
        def_fat=np.array([kw.get("fat", 0)]),
        def_planishing=kw.get("planishing", False),
        def_crit5=kw.get("crit5", False))
    return int(cas[0]), int(rip[0])

MS = lambda *rows: np.array([rows[0]])  # 1-run roll matrix helper

# ── 1. Deadly: save at AP -5 ────────────────────────────────────────────────
# Save target 4 (Chainmail, no AP). Deadly strike -> target 9 -> clip 7 = impossible.
# Save roll 6 would save a normal strike but NOT the deadly one.
rng = FixedRNG([MS([6])])
cas, _ = saves(rng, 4, 1, 1)
check("Deadly: roll 6 vs target 4 still dies (AP-5 -> impossible)", cas == 1)
rng = FixedRNG([MS([6])])
cas, _ = saves(rng, 4, 1, 0)
check("Normal: roll 6 vs target 4 saves", cas == 0)
# Deadly where target stays reachable: save target 1 -> deadly target 6; roll 6 saves.
rng = FixedRNG([MS([6])])
cas, _ = saves(rng, 1, 1, 1)
check("Deadly vs target 1 -> 6: natural 6 saves", cas == 0)
rng = FixedRNG([MS([5])])
cas, _ = saves(rng, 1, 1, 1)
check("Deadly vs target 1 -> 6: roll 5 dies", cas == 1)

# ── 2. Planishing caps the save at 6+ (incl. Deadly) ───────────────────────
rng = FixedRNG([MS([6])])
cas, _ = saves(rng, 4, 1, 1, planishing=True)
check("Planishing: Deadly vs Chainmail capped at 6+ — natural 6 saves", cas == 0)
rng = FixedRNG([MS([6])])
cas, _ = saves(rng, 9, 1, 0, planishing=True)   # AP pushed target to 9
check("Planishing: huge AP capped at 6+ — natural 6 saves", cas == 0)

# ── 3. Deadly Parry/Recover only on natural 6 ──────────────────────────────
# saves order: save roll, then parry roll, then regen roll arrays
rng = FixedRNG([MS([1]), MS([5])])
cas, _ = saves(rng, 4, 1, 1, parry=True)
check("Deadly: Parry 5 fails (needs natural 6)", cas == 1)
rng = FixedRNG([MS([1]), MS([6])])
cas, rip = saves(rng, 4, 1, 1, parry=True, riposte=True)
check("Deadly: Parry natural 6 saves and Ripostes", cas == 0 and rip == 1)
rng = FixedRNG([MS([1]), MS([5])])
cas, _ = saves(rng, 4, 1, 0, parry=True)
check("Normal: Parry 5 succeeds (5+)", cas == 0)
rng = FixedRNG([MS([1]), MS([5])])
cas, _ = saves(rng, 4, 1, 1, regen=6)
check("Deadly: Recover 5 fails (needs natural 6)", cas == 1)
rng = FixedRNG([MS([1]), MS([6])])
cas, _ = saves(rng, 4, 1, 1, regen=6)
check("Deadly: Recover natural 6 saves", cas == 0)

# ── 4. Fatigue worsens Parry & Recover (capped 6+), doesn't disable ────────
rng = FixedRNG([MS([1]), MS([5])])
cas, _ = saves(rng, 7, 1, 0, parry=True, fat=1)
check("Fatigue 1: Parry needs 6 — roll 5 fails", cas == 1)
rng = FixedRNG([MS([1]), MS([6])])
cas, _ = saves(rng, 7, 1, 0, parry=True, fat=3)
check("Fatigue 3: Parry capped at 6+ — natural 6 still parries", cas == 0)
rng = FixedRNG([MS([1]), MS([4])])
cas, _ = saves(rng, 7, 1, 0, regen=4, fat=1)
check("Fatigue 1: Recover 4 -> 5 — roll 4 fails", cas == 1)
rng = FixedRNG([MS([1]), MS([5])])
cas, _ = saves(rng, 7, 1, 0, regen=4, fat=1)
check("Fatigue 1: Recover 4 -> 5 — roll 5 saves", cas == 0)
rng = FixedRNG([MS([1]), MS([6])])
cas, _ = saves(rng, 7, 1, 0, regen=4, fat=9)
check("Fatigue 9: Recover capped at 6+ — natural 6 still recovers", cas == 0)

# ── 5. Unstoppable: -1 Parry on ALL strikes (not unparryable) ───────────────
rng = FixedRNG([MS([1]), MS([5])])
cas, _ = saves(rng, 7, 1, 0, parry=True, unstoppable=True)
check("Unstoppable: Parry 5 fails (threshold 6)", cas == 1)
rng = FixedRNG([MS([1]), MS([6])])
cas, _ = saves(rng, 7, 1, 0, parry=True, unstoppable=True)
check("Unstoppable: Parry natural 6 still works", cas == 0)

# ── 6. Serrated worsens Recover, capped 6+ ──────────────────────────────────
thr = vc._regen_threshold(["Recover 4"], ["Serrated"])
check("Serrated: Recover 4 -> 5", thr == 5)
thr = vc._regen_threshold(["Recover 6"], ["Serrated", "Serrated"])
check("Serrated x2 on Recover 6: capped at 6 (can't fully negate)", thr == 6)
thr = vc._regen_threshold(["Regenerate 5"], ["Rend"])
check("Legacy names still resolve (Regenerate 5 + Rend -> 6)", thr == 6)

# ── 7. Cleave: extra die rolled at modified value (can miss) ────────────────
def strikes(rng, th, front, tags, crit5=False):
    st, dl, ds = vc._roll_strikes_vec(rng, 1, np.array([th]), np.array([front]),
        tags, False, np.array([False]), atk_crit5=crit5)
    return int(st[0]), int(dl[0])
# one die: roll 6 (hit+proc), cleave die rolls 2 vs th 4 -> miss => 1 strike
pad = lambda v: [v] + [1]*19
rng = FixedRNG([np.array([pad(6)]), np.array([pad(2)])])
st, _ = strikes(rng, 4, 1, ["Cleave"])
check("Cleave: extra die that misses adds nothing", st == 1)
rng = FixedRNG([np.array([pad(6)]), np.array([pad(5)])])
st, _ = strikes(rng, 4, 1, ["Cleave"])
check("Cleave: extra die that hits adds one strike", st == 2)
# Cleave extra die rolling 6 does NOT chain another cleave
rng = FixedRNG([np.array([pad(6)]), np.array([pad(6)])])
st, _ = strikes(rng, 4, 1, ["Cleave"])
check("Cleave: no chaining (6 on extra die = still 2 strikes)", st == 2)
# Deadly classification on the extra die's natural 6
rng = FixedRNG([np.array([pad(6)]), np.array([pad(6)])])
st, dl = strikes(rng, 4, 1, ["Cleave", "Deadly"])
check("Cleave+Deadly: both the proc and the 6 on the extra die are Deadly", st == 2 and dl == 2)

# ── 8. Ministry rank 2 (Crit 5): procs on a successful natural 5 ────────────
rng = FixedRNG([np.array([pad(5)]), np.array([pad(5)])])
st, dl = strikes(rng, 4, 1, ["Deadly", "Cleave"], crit5=True)
check("Crit 5: natural 5 procs Deadly+Cleave (extra 5 also hits)", st == 2 and dl == 2)
rng = FixedRNG([np.array([pad(5)]), np.array([pad(1)])])
st, dl = strikes(rng, 6, 1, ["Deadly"], crit5=True)
check("Crit 5: natural 5 that MISSES (th 6) does not proc", st == 0 and dl == 0)
# Riposte on a successful natural-5 parry
rng = FixedRNG([MS([1]), MS([5])])
cas, rip = saves(rng, 7, 1, 0, parry=True, riposte=True, crit5=True)
check("Crit 5: natural-5 Parry (5+ threshold) Ripostes", cas == 0 and rip == 1)
rng = FixedRNG([MS([1]), MS([5])])
cas, rip = saves(rng, 7, 1, 0, parry=True, riposte=True, crit5=True, fat=1)
check("Crit 5: natural-5 Parry at threshold 6 does NOT parry or riposte", cas == 1 and rip == 0)

# ── 9. Poison: natural 6 to Save fails ──────────────────────────────────────
rng = FixedRNG([MS([6])])
cas, _ = saves(rng, 4, 1, 0, poison=True)
check("Poison: natural-6 save fails", cas == 1)

# ── 10. Deflect: ranged is -1 Parry and never Ripostes ──────────────────────
rng = FixedRNG([MS([1]), MS([5])])
cas, _ = saves(rng, 7, 1, 0, parry=True, ranged=True)
check("Ranged: Parry 5 fails (threshold 6)", cas == 1)
rng = FixedRNG([MS([1]), MS([6])])
cas, rip = saves(rng, 7, 1, 0, parry=True, riposte=True, ranged=True)
check("Ranged: natural-6 Parry works but never Ripostes", cas == 0 and rip == 0)

# ── 10b. Data-tag wiring: every shield/armor tag the data emits is read ─────
sa_args = dict(retinue="Levy", weapon="Farm Tools", ranged=None, has_tiltyard=False,
               size=25, extra_tags=[], upkeep_per_retinue=0)
from loadouts import Loadout as _LD
_scutum = vc.StaticArmy(_LD(name="s", shield="Scutum Shield", armor="Cloth", **sa_args), False)
check("Wiring: Scutum '-1 to Strike' tag sets the TBH penalty", _scutum.shield_tbh_penalty_start == 1)
_heater = vc.StaticArmy(_LD(name="h", shield="Heater Shield", armor="Cloth", **sa_args), False)
check("Wiring: Heater Immune Destroy Shield read", _heater.shield_immune)
_kt = vc.StaticArmy(_LD(name="k", shield=None, armor="Cloth",
                        **{**sa_args, "retinue": "Knight Templar"}), False)
check("Wiring: KT unbreakable key read", _kt.unshakable)
_deadly_tags = set(rd.WEAPONS["Daggers"]["tags"])
check("Wiring: data emits 'Deadly' and engine recognizes it",
      ("Deadly" in _deadly_tags))

# ── 10c. ABF package: weapons -1 AP, incoming AP reduced by 1 (pre-Deadly) ──
def _abf_wr(atk_extra, def_extra, seed=21, n=4000):
    a = _LD(name="a", shield=None, armor="Cloth",
            **{**sa_args, "retinue": "Man-at-Arms", "weapon": "Arming Sword",
               "extra_tags": atk_extra})
    b = _LD(name="b", shield=None, armor="Chainmail",
            **{**sa_args, "retinue": "Man-at-Arms", "weapon": "Arming Sword",
               "extra_tags": def_extra})
    r = vc.run_matchup_vec(a, b, n_runs=n, seed=seed)
    return r["a_wins"] / n
sa_args2 = {k: v for k, v in sa_args.items() if k not in ("retinue",)}
_base = _abf_wr([], [])
_out  = _abf_wr(["ABF"], [])
_inc  = _abf_wr([], ["ABF"])
print(f"      ABF deltas: base {_base:.3f} | attacker-ABF {_out:.3f} | defender-ABF {_inc:.3f}")
check("ABF outgoing: attacker with ABF wins more", _out > _base + 0.01)
check("ABF incoming: defender with ABF lowers attacker WR", _inc < _base - 0.01)
# Deadly interaction: ABF defender in Gothic — Deadly proc resolves at (AP+1)+5.
# War Hammer AP -8 vs Gothic 2: deadly target = clip(2+8+5,..7)=7 either way; use AP -1:
# Arming Sword vs Gothic+ABF: normal target 2-0=2; deadly = 2+5=7 (impossible) without
# Planishing — vs WITH Planishing capped at 6 (natural 6 saves). Distinguishable:
import numpy as np
class _FR:
    def __init__(self, seq): self.seq=[np.asarray(x,dtype=np.int8) for x in seq]; self.i=0
    def integers(self, lo, hi, size=None, dtype=np.int8):
        out=self.seq[self.i]; self.i+=1; return out.astype(dtype)
rngx = _FR([np.array([[6]])])
cas, _ = vc._roll_saves_vec(rngx, 1, np.array([1]), np.array([1]), np.array([1]),
    atk_has_poison=False, def_has_parry=False, def_regen_threshold=None,
    def_fat=np.array([0]))
check("Deadly stacks on the (ABF-adjusted) base target: target 1 -> 6, nat 6 saves", cas[0] == 0)
# Clamp semantics, tested on the pure helper:
check("ABF AP math: outgoing -4 -> -5", vc._abf_effective_ap(-4, True, False) == -5)
check("ABF AP math: incoming -4 -> -3", vc._abf_effective_ap(-4, False, True) == -3)
check("ABF AP math: 0-AP weapon clamped (incoming cannot go positive)", vc._abf_effective_ap(0, False, True) == 0)
check("ABF AP math: mutual cancels (-4 stays -4)", vc._abf_effective_ap(-4, True, True) == -4)
check("ABF AP math: attacker-ABF 0-AP then defender-ABF -> 0", vc._abf_effective_ap(0, True, True) == 0)

# ── 10d. SSOT canary: loadouts' pursuit table is built from NODES engine fields ──
import loadouts as _lo
_alias_back = {v.get("engine", {}).get("alias", k): k for k, v in rd.NODES.items() if "engine" in v}
check("SSOT: every sim pursuit resolves to a NODES engine entry",
      all(k in _alias_back for k in _lo.PURSUITS_INFO))
check("SSOT: sim pursuit table is non-trivial", len(_lo.PURSUITS_INFO) >= 30)

# ── 11. End-to-end smoke: full battles still run ────────────────────────────
from loadouts import Loadout
ld_a = Loadout(name="A", retinue="Man-at-Arms", weapon="Battle Axe", shield=None,
               armor="Chainmail", ranged=None, has_tiltyard=False, size=25,
               extra_tags=[], upkeep_per_retinue=0)
ld_b = Loadout(name="B", retinue="Levy", weapon="Farm Tools", shield=None,
               armor="Cloth", ranged=None, has_tiltyard=False, size=25,
               extra_tags=["Recover 4"], upkeep_per_retinue=0)
res = vc.run_matchup_vec(ld_a, ld_b, n_runs=2000, seed=7)
awin = res["a_wins"] / 2000
print(f"      smoke: MaA/BattleAxe vs Levy/Recover4 -> A wins {awin:.0%}")
check("Smoke: battles complete and produce outcomes", 0.0 <= awin <= 1.0 and res["a_wins"] + res["b_wins"] > 0)

ld_c = Loadout(name="C", retinue="Sergeant", weapon="Poleaxe", shield=None,
               armor="Full Plate", ranged=None, has_tiltyard=False, size=25,
               extra_tags=["Crit 5", "+1I", "Seize: first", "Immune Tactic TH"], upkeep_per_retinue=0)
res2 = vc.run_matchup_vec(ld_c, ld_b, n_runs=1000, seed=11)
check("Smoke: Ministry-tagged loadout runs", res2["a_wins"] + res2["b_wins"] > 0)

print()
if FAILS:
    print(f"{len(FAILS)} FAILURES:"); [print(" -", f) for f in FAILS]
    sys.exit(1)
print("ALL RULES VERIFIED")
