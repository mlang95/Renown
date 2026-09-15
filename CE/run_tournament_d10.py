#!/usr/bin/env python3
"""run_tournament_d10.py — run the Renown tournament against the d10 build.

Delegates entirely to Combatv3/run_tournament.py; the only difference is that
CE/Combatv4/shims sits first on sys.path, so every `import renown_data`,
`import vectorized_combat`, `import combat_kernel`, `import combat_morale` and
`import combat_primitives` resolves to the *_d10 versions instead. CE is fully self-contained: nothing here imports from Combatv3.

Output goes to CE/lab_out/<tag>/, one subfolder per dice configuration.

Usage, from the CE folder:
    python run_tournament_d10.py --mpc-min 3 --mpc-max 20 --runs 50 --workers 8
    python run_tournament_d10.py --faces 6 --tag d6base      # d6 control run
    python run_tournament_d10.py --focused 9 --tag foc9      # 9+ Focused variant

Every argument accepted by run_tournament.py is passed straight through.
"""
import argparse
import os
import sys

import ce_paths

# Paths FIRST. Nothing below may import an engine module before this runs, or the
# import lands in whatever happens to be on sys.path (or fails outright). Doing it
# at module top rather than after argparse removes the ordering hazard entirely.
OUT_ROOT = ce_paths.install(verbose=True)

# ── Pre-scan our own switches before anything imports the engines ────────────
_pre = argparse.ArgumentParser(add_help=False)
_pre.add_argument("--faces", type=int, default=None,
                  help="override dice_config.FACES for this run (6 to reproduce the d6 baseline)")
_pre.add_argument("--focused", type=int, default=None,
                  help="override dice_config.FOCUSED_THR (e.g. 9 for the top-two-faces variant)")
_pre.add_argument("--fatigue-strike", type=int, default=None, help="override FATIGUE_STRIKE magnitude")
_pre.add_argument("--fatigue-morale", type=int, default=None, help="override FATIGUE_MORALE magnitude")
_pre.add_argument("--no-auto-pass", action="store_true",
                  help="delete the auto-pass rule (AUTO_PASS_FLOOR = None)")
_pre.add_argument("--tag", default=None,
                  help="subfolder under lab_out for this run (default: derived from the dice settings)")
_pre.add_argument("--parry-base", type=int, default=None, help="override PARRY_BASE (base Parry target)")
_pre.add_argument("--recover-base", type=int, default=None, help="override RECOVER_BASE (worst Recover rung)")
_pre.add_argument("--deadly-ap", type=int, default=None, help="override DEADLY_AP (additional AP on a Focused Deadly strike)")
_pre.add_argument("--deadly-mode", choices=["additional", "set"], default=None, help="override DEADLY_MODE")
_pre.add_argument("--unstoppable", type=int, default=None, help="override UNSTOPPABLE_MOD (+N to defender Parry target)")
_pre.add_argument("--improved-parry", type=int, default=None, help="override IMPROVED_PARRY_MOD (-N to own Parry target)")
_pre.add_argument("--skip-verify", action="store_true", help="skip the d10 sanity assertions")
mine, passthrough = _pre.parse_known_args()

# ── Apply dice overrides BEFORE the engines import dice_config ───────────────
import dice_config as dc  # noqa: E402

if mine.faces is not None:
    dc.FACES = mine.faces
    dc.ROUT_THR = dc.FACES + 1
    dc.CAP_THR = dc.FACES
    if mine.focused is None:
        dc.FOCUSED_THR = dc.FACES
    if mine.faces != 10:
        print(f"\n  !! --faces {mine.faces} changes the ENGINE but renown_data_d10 still holds the\n"
              f"     d10-rescaled values (Levy to_hit 6, Cloth save 10, ...). That is NOT a d6\n"
              f"     baseline — it is d10 numbers on a d{mine.faces} die. For the real d6 control,\n"
              f"     run Combatv3\\run_tournament.bat (the separate d6 tree) instead.\n")
if mine.focused is not None:
    dc.FOCUSED_THR = mine.focused
if mine.fatigue_strike is not None:
    dc.FATIGUE_STRIKE = mine.fatigue_strike
if mine.fatigue_morale is not None:
    dc.FATIGUE_MORALE = mine.fatigue_morale
if mine.no_auto_pass:
    dc.AUTO_PASS_FLOOR = None
if mine.parry_base is not None:     dc.PARRY_BASE = mine.parry_base
if mine.recover_base is not None:   dc.RECOVER_BASE = mine.recover_base
if mine.deadly_ap is not None:      dc.DEADLY_AP = mine.deadly_ap
if mine.deadly_mode is not None:    dc.DEADLY_MODE = mine.deadly_mode
if mine.unstoppable is not None:    dc.UNSTOPPABLE_MOD = mine.unstoppable
if mine.improved_parry is not None: dc.IMPROVED_PARRY_MOD = mine.improved_parry

# Workers get the overrides too (spawn re-imports dice_config from disk).
for _k in ("FACES", "FOCUSED_THR", "ROUT_THR", "CAP_THR", "FATIGUE_STRIKE", "FATIGUE_MORALE",
           "PARRY_BASE", "RECOVER_BASE", "DEADLY_AP", "UNSTOPPABLE_MOD", "IMPROVED_PARRY_MOD"):
    os.environ[f"RENOWN_{_k}"] = str(getattr(dc, _k))
os.environ["RENOWN_AUTO_PASS_FLOOR"] = str(dc.AUTO_PASS_FLOOR)
os.environ["RENOWN_DEADLY_MODE"] = str(dc.DEADLY_MODE)

tag = mine.tag or (
    f"d{dc.FACES}_foc{dc.FOCUSED_THR}_fat{dc.FATIGUE_STRIKE}{dc.FATIGUE_MORALE}"
    f"_par{dc.PARRY_BASE}_dea{dc.DEADLY_AP}{'s' if dc.DEADLY_MODE == 'set' else 'a'}"
    f"_uns{dc.UNSTOPPABLE_MOD}_imp{dc.IMPROVED_PARRY_MOD}"
)
out_dir = os.path.join(OUT_ROOT, tag)
os.makedirs(out_dir, exist_ok=True)
import json, datetime
_KNOBS = ("FACES", "FOCUSED_THR", "ROUT_THR", "CAP_THR", "AUTO_PASS_FLOOR",
          "FATIGUE_STRIKE", "FATIGUE_MORALE", "PARRY_BASE", "RECOVER_BASE",
          "DEADLY_AP", "UNSTOPPABLE_MOD", "IMPROVED_PARRY_MOD")
_manifest = {
    "tag": tag,
    "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    "out_dir": out_dir,
    "dice": {k: getattr(dc, k) for k in _KNOBS},
    "deadly_mode": dc.DEADLY_MODE,
}


for _p in (os.path.join(out_dir, "dice.json"),          # immutable, beside the parquet
           os.path.join(OUT_ROOT, "last_run.json")):    # mutable pointer the docs read
    with open(_p, "w", encoding="utf-8") as fh:
        json.dump(_manifest, fh, indent=2)


print(f"\n=== Renown tournament — {tag} ===")
print("  " + dc.describe())
print(f"  output -> {out_dir}\n")

if not mine.skip_verify and dc.FACES == 10:
    ce_paths.assert_d10()
    ce_paths.assert_isolated()
    print("  d10 + isolation checks passed.\n")

# ── Hand off ─────────────────────────────────────────────────────────────────
import run_tournament  # noqa: E402  (CE/Combatv4 copy, resolved through the shims)

if "--out" not in passthrough:
    passthrough += ["--out", out_dir]

sys.argv = [sys.argv[0]] + passthrough

if __name__ == "__main__":
    run_tournament.main()
