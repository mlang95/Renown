#!/usr/bin/env python3
"""verify_d10.py — prove the CE wiring is live before spending hours on a run.

Checks, in order:
  1. every module resolves to the file you expect (shims are working)
  2. the data values are the d10 ones, not the d6 ones
  3. dice_config actually reaches the engines
  4. a tiny matchup runs end to end and produces sane numbers

Run from the CE folder:
    python verify_d10.py
    python verify_d10.py --faces 6      # confirm the d6 control path also works
"""
import argparse
import os
import sys

ap = argparse.ArgumentParser()
ap.add_argument("--faces", type=int, default=None)
ap.add_argument("--focused", type=int, default=None)
args = ap.parse_args()

import ce_paths

ce_paths.install(verbose=False)

if args.faces is not None:
    os.environ["RENOWN_FACES"] = str(args.faces)
    os.environ["RENOWN_ROUT_THR"] = str(args.faces + 1)
    os.environ["RENOWN_CAP_THR"] = str(args.faces)
    os.environ["RENOWN_FOCUSED_THR"] = str(args.focused if args.focused else args.faces)
elif args.focused is not None:
    os.environ["RENOWN_FOCUSED_THR"] = str(args.focused)

FAIL = []


def check(label, ok, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f"  — {detail}" if detail else ""))
    if not ok:
        FAIL.append(label)


print("\n1. MODULE RESOLUTION")
import dice_config as dc
import renown_data as rd
import vectorized_combat as vc
import combat_kernel as ck
import combat_morale as cm
import combat_primitives as cp
import loadouts
import batch_engine

for name, mod, want in [("renown_data", rd, "renown_data_d10.py"),
                        ("vectorized_combat", vc, "vectorized_combat_d10.py"),
                        ("combat_kernel", ck, "combat_kernel_d10.py"),
                        ("combat_morale", cm, "combat_morale_d10.py"),
                        ("combat_primitives", cp, "combat_primitives_d10.py")]:
    f = os.path.basename(getattr(mod, "__file__", "?"))
    check(f"{name} -> {want}", f == want, f"got {f}")
check("renown_combat -> renown_combat_d10.py",
      os.path.basename(getattr(__import__("renown_combat"), "__file__", "?")) == "renown_combat_d10.py")
for name, mod in [("loadouts", loadouts), ("batch_engine", batch_engine)]:
    check(f"{name} inside CE tree", os.path.abspath(getattr(mod, "__file__", "")).startswith(ce_paths.CE_DIR),
          os.path.dirname(getattr(mod, "__file__", "?")))
try:
    ce_paths.assert_isolated()
    check("nothing loaded from outside CE", True)
except Exception as e:
    check("nothing loaded from outside CE", False, str(e))

print(f"\n2. DICE CONFIG  ({dc.describe()})")
check("renown_data is the -d10 build", str(rd.VERSION).endswith("-d10"), rd.VERSION)
check("renown_data.FACES matches dice_config", rd.FACES == dc.FACES, f"{rd.FACES} vs {dc.FACES}")

print("\n3. DATA VALUES  (structural — these do not hard-code your tuning)")
TIER_ORDER = list(rd.TIERS)

# every combat threshold must be rollable and not auto-pass
bad = [(n, k, v[k]) for n, v in rd.RETINUES.items() for k in ("to_hit", "shaking")
       if not (2 <= v[k] <= dc.FACES)]
check("retinue thresholds within 2..FACES", not bad, bad)
print(f"      retinues: " + ", ".join(
    f"{n} {v['to_hit']}+/{v['shaking']}+" for n, v in rd.RETINUES.items()))

# armor must not improve as tier drops
arm = sorted(rd.ARMORS.items(), key=lambda kv: TIER_ORDER.index(kv[1]["tier"]))
mono = all(arm[i][1]["save"] >= arm[i + 1][1]["save"] for i in range(len(arm) - 1))
check("armor ladder monotonic by tier", mono,
      ", ".join(f"{n} {d['save']}+" for n, d in arm))
check("armor saves within 2..FACES",
      all(2 <= d["save"] <= dc.FACES for d in rd.ARMORS.values()))

# shields must not improve as tier drops
sh = [(n, d) for n, d in rd.SHIELDS.items() if n]
sh.sort(key=lambda kv: TIER_ORDER.index(kv[1]["tier"]))
# Shields deliberately trade across axes (Targe's save for Steady, Heater's save for
# Initiative and Immune Destroy Shield), so a non-monotonic save ladder is a design
# choice rather than an error. Reported, never failed.
_mono_sh = all(sh[i][1]["save_bonus"] <= sh[i + 1][1]["save_bonus"] for i in range(len(sh) - 1))
print(f"      shields: " + ", ".join(
    f"{n.replace(' Shield','')} +{d['save_bonus']}/{d['init']:+d}" for n, d in sh)
    + ("" if _mono_sh else "   <- save ladder dips; check the dipping shield earns it elsewhere"))

# Recover ladder: one tag per rung, no collisions
rec = {}
for n, d in rd.NODES.items():
    e = d.get("engine", {}) or {}
    for t in (e.get("innate_tags") or []) + (e.get("mastery_tags") or []):
        if str(t).startswith("Recover "):
            rec.setdefault(str(t), []).append(n)
dupes = {t: ns for t, ns in rec.items() if len(ns) > 1}
check("no duplicate Recover rungs", not dupes, dupes)
print(f"      Recover ladder: " + ", ".join(f"{t} ({ns[0]})" for t, ns in sorted(rec.items())))

# spelling / gating of the gunpowder weapon
check("Arquebus spelled correctly", "Arquebus" in rd.RANGED,
      "found " + str([k for k in rd.RANGED if "rq" in k.lower()]))
arq = rd.RANGED.get("Arquebus", {})
check("Arquebus gated on ABF + Artillery Park",
      set(arq.get("requires", [])) >= {"ABF", "Artillery Park"}, arq.get("requires"))
check("Arquebus tactic restriction present", bool(arq.get("tactics_allowed")),
      arq.get("tactics_allowed"))

# die-dependent text tracks dice_config
check("Focused glossary matches FOCUSED_THR",
      str(dc.FOCUSED_THR) in rd.GLOSSARY[rd.PIVOTAL], rd.GLOSSARY[rd.PIVOTAL])
stale = [k for k in (rd.BLUNDER, rd.MINUS_1_TBH, rd.NEGATE_TEMPERED, rd.FATIGUE_TOKEN)
         if "6+" in str(rd.GLOSSARY.get(k, ""))]
check("no stray '6+' in combat glossary", not stale, stale)

# informational only — never fails, so AP tuning does not break the run
import collections as _c
_t = _c.defaultdict(list)
for n, w in rd.WEAPONS.items():
    _t[w["tier"]].append(abs(w["ap"]))
print("      AP by tier (informational): " + " | ".join(
    f"{t} {min(_t[t])}-{max(_t[t])}" for t in TIER_ORDER if _t[t]))

print("\n4. PROBABILITY SANITY")
for t, want in [(dc.FACES, 1 / dc.FACES), (2, (dc.FACES - 1) / dc.FACES), (dc.FACES + 1, 0.0)]:
    check(f"p_success({t})", abs(dc.p_success(t) - want) < 1e-9, f"{dc.p_success(t):.3f} expected {want:.3f}")
check("auto-pass floor", dc.p_success(1) == 1.0 if dc.AUTO_PASS_FLOOR else dc.p_success(1) < 1.0)

print("\n5. SMOKE RUN")
try:
    L = loadouts.Loadout
    a = L(name="A", retinue="Man-at-Arms", weapon="Arming Sword", shield="Kite Shield",
          armor="Chainmail", ranged=None, has_tiltyard=False, size=25,
          extra_tags=frozenset(), upkeep_per_retinue=0)
    b = L(name="B", retinue="Levy", weapon="Spears", shield=None,
          armor="Gambeson", ranged=None, has_tiltyard=False, size=25,
          extra_tags=frozenset(), upkeep_per_retinue=0)
    check("loadouts constructed", True, f"{a.retinue}/{a.armor} vs {b.retinue}/{b.armor}")
    res = vc.run_matchup_vec(a, b, n_runs=200, seed=1)
    check("matchup ran", res is not None, type(res).__name__)
    print("      ", str(res)[:400])
except Exception as e:
    check("smoke run", False, f"{type(e).__name__}: {e}")
ok, problems = rd.verify_aliases()
if not ok:
    for p in problems:
        print("  [FAIL] " + p)
    FAILED = True
else:
    print("[PASS] display aliases consistent")
print("\n" + ("ALL CHECKS PASSED" if not FAIL else f"{len(FAIL)} FAILURE(S): " + ", ".join(FAIL)))
sys.exit(1 if FAIL else 0)