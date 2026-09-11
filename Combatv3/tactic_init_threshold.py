#!/usr/bin/env python3
"""
Threshold-conditioned tactic eval — where the gear->init coupling ACTUALLY decides games.

Insight (Gage): tactic init mods are two-sided (A gains, B loses) and gear cancels them directionally
(Unwieldy zeros your +I, Steady zeros your -I). Initiative only changes the OUTCOME when it flips who
strikes first (a_init > b_init). A field-average buries this: in most matchups the init gap doesn't sit
on the flip boundary, so the coupling does nothing and washes the signal to ~0.

This partitions every (archetype, tactic, opponent) matchup by whether it is INIT-DECISIVE — i.e. the
strike order would flip if A's init moved by 1 (which is exactly what Unwieldy/Steady do). It then
measures each tactic's win rate INTO THE FIELD split by decisive vs irrelevant, and the Unwieldy
toggle effect WITHIN the decisive partition (where it should be large).

Run:  python tactic_init_threshold.py --runs 200 --panel 60
"""
import os, sys, argparse, random
from collections import defaultdict, Counter
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import numpy as np, pandas as pd
import renown_combat as rc, vectorized_combat as vc, loadouts, playstyles, batch_engine as be

TAC6 = ["Scout", "Ambush", "Flank", "Charge", "Fighting Formation", "Defensive Formation"]

def Ld(name, ret, weapon, shield, armor, ranged=None, tags=(), tiltyard=False):
    return loadouts.Loadout(name=name, retinue=ret, weapon=weapon, shield=shield, armor=armor,
        ranged=ranged, has_tiltyard=tiltyard, size=loadouts.DEFAULT_ARMY_SIZE,
        extra_tags=frozenset(tags), upkeep_per_retinue=0, playstyle=None, tiltyard_mastery=False,
        pursuits=frozenset(), military_pursuit_count=0, domain_count=0)

def eff_init(build, is_attacker):
    """Effective normal-skirmish base initiative (gear + tags), via the engine's StaticArmy."""
    sa = vc.StaticArmy(build, is_attacker)
    return sa.base_init(first=False)

def tactic_I(build_tags, raw_I, immune_unwieldy=False):
    """Apply the directional gear rule to a tactic's I mod for one side."""
    if raw_I < 0 and "Steady" in build_tags:
        return 0
    if raw_I > 0 and "Unwieldy" in build_tags and not immune_unwieldy:
        return 0
    return raw_I

def strike_first(a_build, b_build, a_tac, b_tac):
    """Does A strike first, given gear + tactic init mods (post directional-cancellation)?"""
    a_cell, b_cell = rc.TACTIC_MATRIX[(a_tac, b_tac)]
    at = set(a_build.extra_tags) | set(rc.WEAPONS.get(a_build.weapon, {}).get("tags", [])) \
         | set(rc.ARMORS.get(a_build.armor, {}).get("tags", [])) | set(rc.SHIELDS.get(a_build.shield, {}).get("tags", []))
    bt = set(b_build.extra_tags) | set(rc.WEAPONS.get(b_build.weapon, {}).get("tags", [])) \
         | set(rc.ARMORS.get(b_build.armor, {}).get("tags", [])) | set(rc.SHIELDS.get(b_build.shield, {}).get("tags", []))
    a_iu = "Immune Unwieldy" in a_build.extra_tags
    b_iu = "Immune Unwieldy" in b_build.extra_tags
    a_init = eff_init(a_build, True) + tactic_I(at, a_cell["I"], a_iu)
    b_init = eff_init(b_build, False) + tactic_I(bt, b_cell["I"], b_iu)
    return a_init, b_init

def is_init_decisive(a_build, b_build, a_tac, b_tac):
    """True if a +/-1 swing in A's init would FLIP the strike order (the coupling can decide here)."""
    ai, bi = strike_first(a_build, b_build, a_tac, b_tac)
    now = np.sign(ai - bi)
    up = np.sign((ai + 1) - bi)
    dn = np.sign((ai - 1) - bi)
    return (up != now) or (dn != now)

def hand_archetypes():
    return [
        ("Unwieldy +init (Cav Spear)",  Ld("a_cs", "Sergeant", "Cavalry Spear", "Kite Shield", "Chainmail")),
        ("High-init (Daggers)",         Ld("a_dg", "Sergeant", "Daggers", None, "Cloth")),
        ("High-init Steady (Spears)",   Ld("a_sp", "Sergeant", "Spears", "Kite Shield", "Leather")),
        ("Neutral 1H (Arming Sword)",   Ld("a_as", "Sergeant", "Arming Sword", "Kite Shield", "Chainmail")),
        ("Unwieldy heavy (War Hammer)", Ld("a_wh", "Sergeant", "War Hammer", None, "Full Plate")),
    ]

def build_panel(n, seed=2026):
    pool = loadouts.balanced_validation_pool(4, 13, per_cell=20, seed=seed)
    rng = random.Random(seed); by = defaultdict(list)
    for l in pool: by[(l.retinue, l.military_pursuit_count)].append(l)
    keys = sorted(by.keys()); panel = []; i = 0
    while len(panel) < n and keys:
        b = by[keys[i % len(keys)]]
        if b: panel.append(b[rng.randrange(len(b))])
        i += 1
        if i > n*20: break
    seen=set(); uniq=[]
    for p in panel:
        if p.name not in seen: seen.add(p.name); uniq.append(p)
    return [p._replace(playstyle=playstyles.assign_default_playstyle(p)) for p in uniq]

def win_rate_partitioned(arch, panel, tac_idx, runs, block=20000):
    """Win rate vs the field, split into init-DECISIVE and init-IRRELEVANT opponent subsets.
    Decisive membership uses A's tactic vs B playing its likely engaging tactics (avg over TAC6)."""
    a_tac = TAC6[tac_idx]
    dec_opps, irr_opps = [], []
    for opp in panel:
        if opp.name == arch.name: continue
        # opponent considered init-decisive if A's strike order is flip-sensitive for >=half of B's tactics
        flips = sum(is_init_decisive(arch, opp, a_tac, bt) for bt in TAC6)
        (dec_opps if flips >= 3 else irr_opps).append(opp)
    out = {}
    for label, opps in [("decisive", dec_opps), ("irrelevant", irr_opps)]:
        if not opps:
            out[label] = (float("nan"), 0); continue
        pairs = [(arch, o) for o in opps]
        aw = bw = 0
        for s in range(0, len(pairs), block):
            blk = pairs[s:s+block]
            r = be.run_batch_random(blk, n_runs=runs, seed=2026+s, mode="forced", force_a=tac_idx, force_b=-1)
            aw += int(r["a_wins"].sum()); bw += int(r["b_wins"].sum())
        out[label] = (aw/(aw+bw) if (aw+bw) else float("nan"), len(opps))
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "lab_out"))
    ap.add_argument("--runs", type=int, default=200)
    ap.add_argument("--panel", type=int, default=60)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    vc.invalidate_tactic_tables()
    panel = build_panel(args.panel)
    print(f"Panel: {len(panel)} builds\n")

    rows = []
    print("="*86)
    print("SCOUT win-rate: init-DECISIVE opponents vs init-IRRELEVANT opponents, per archetype")
    print("  (Scout's +1I only helps where init is decisive AND not cancelled by Unwieldy)")
    print("="*86)
    for name, arch in hand_archetypes():
        sc = win_rate_partitioned(arch, panel, TAC6.index("Scout"), args.runs)
        (wd, nd), (wi, ni) = sc["decisive"], sc["irrelevant"]
        print(f"\n{name}")
        print(f"  Scout vs init-DECISIVE   ({nd:2d} opp): {wd:.3f}")
        print(f"  Scout vs init-IRRELEVANT ({ni:2d} opp): {wi:.3f}")
        rows.append({"archetype": name, "scout_decisive_wr": wd, "n_decisive": nd,
                     "scout_irrelevant_wr": wi, "n_irrelevant": ni})

    print("\n" + "="*86)
    print("UNWIELDY TOGGLE within init-DECISIVE opponents (where the coupling should be LARGE)")
    print("="*86)
    for name, b in [("Cav Spear (Unwieldy,init+1)", Ld("c_cs","Sergeant","Cavalry Spear","Kite Shield","Chainmail")),
                    ("Lance (Unwieldy,init+1)",     Ld("c_ln","Sergeant","Lance","Kite Shield","Chainmail"))]:
        on  = win_rate_partitioned(b, panel, TAC6.index("Scout"), args.runs)["decisive"][0]
        off = win_rate_partitioned(b._replace(extra_tags=frozenset({"Immune Unwieldy"})), panel,
                                   TAC6.index("Scout"), args.runs)["decisive"][0]
        print(f"\n{name}")
        print(f"  Scout wr (init-decisive)  Unwieldy ON: {on:.3f}   OFF: {off:.3f}   delta: {off-on:+.3f}")
        rows.append({"archetype": name+" [toggle,decisive]", "scout_unw_on": on, "scout_unw_off": off})

    pd.DataFrame(rows).to_csv(os.path.join(args.out, "tactic_init_threshold.csv"), index=False)
    print("\nWrote tactic_init_threshold.csv")

if __name__ == "__main__":
    main()
