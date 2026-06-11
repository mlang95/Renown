#!/usr/bin/env python3
"""
Tactic-pruning eval (marginal-edge version) — does EQUIPMENT shape which tactics are worth picking?

The earlier field-AVERAGE ranking washed out the gear coupling. This uses a MARGINAL-EDGE metric:
for each archetype, edge(tactic) = win_into_field(tactic) - (that archetype's mean across tactics).
Subtracting the archetype's own mean removes its base power level, isolating the RELATIVE tactic
preference FOR that build.

Plus a direct INITIATIVE-COUPLING diagnostic: take init-positive builds, toggle Unwieldy on/off (via
Immune Unwieldy injection), and show how Scout's edge moves. Verifies "Unwieldy zeros a tactic's +I".

Method: force A's tactic, B plays the random mix, vs a (retinue x MPC)-balanced panel.
Run:  python tactic_pruning.py --runs 200 --panel 50
"""
import os, sys, argparse, random
from collections import defaultdict, Counter
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import numpy as np
import pandas as pd
import renown_combat as rc, vectorized_combat as vc, loadouts, playstyles, batch_engine as be

TAC7 = ["Scout", "Ambush", "Flank", "Charge", "Fighting Formation", "Defensive Formation", "Fall Back"]

def init_positive_tactics():
    out = []
    for t in TAC7[:6]:
        mods = [rc.TACTIC_MATRIX[(t, o)][0]["I"] for o in TAC7[:6]]
        if np.mean(mods) > 0.15:
            out.append(t)
    return out

def Ld(name, ret, weapon, shield, armor, ranged=None, tags=(), tiltyard=False):
    return loadouts.Loadout(
        name=name, retinue=ret, weapon=weapon, shield=shield, armor=armor, ranged=ranged,
        has_tiltyard=tiltyard, size=loadouts.DEFAULT_ARMY_SIZE, extra_tags=frozenset(tags),
        upkeep_per_retinue=0, playstyle=None, tiltyard_mastery=False,
        pursuits=frozenset(), military_pursuit_count=0, domain_count=0)

def hand_archetypes():
    return [
        ("Unwieldy +init (Cav Spear)",  Ld("a_cs", "Sergeant", "Cavalry Spear", "Kite Shield", "Chainmail")),
        ("Unwieldy heavy (War Hammer)", Ld("a_wh", "Sergeant", "War Hammer", None, "Full Plate")),
        ("Unwieldy heavy (Battle Axe)", Ld("a_ba", "Sergeant", "Battle Axe", None, "Chainmail")),
        ("High-init Steady (Spears)",   Ld("a_sp", "Sergeant", "Spears", "Kite Shield", "Leather")),
        ("High-init (Daggers)",         Ld("a_dg", "Sergeant", "Daggers", None, "Cloth")),
        ("Neutral 1H (Arming Sword)",   Ld("a_as", "Sergeant", "Arming Sword", "Kite Shield", "Chainmail")),
        ("Shieldwall / high-save",      Ld("a_wall", "Sergeant", "Arming Sword", "Tower Shield", "Full Plate")),
        ("Glass cannon (Cloth)",        Ld("a_gc", "Sergeant", "Bastard Sword", "Heater Shield", "Cloth")),
        ("One-Shot ranged (Pilum)",     Ld("a_os", "Sergeant", "Farm Tools", None, "Chainmail", ranged="Pilum", tiltyard=True)),
    ]

def build_panel(n, seed=2026):
    pool = loadouts.balanced_validation_pool(4, 13, per_cell=20, seed=seed)
    rng = random.Random(seed)
    by = defaultdict(list)
    for l in pool:
        by[(l.retinue, l.military_pursuit_count)].append(l)
    keys = sorted(by.keys()); panel = []; i = 0
    while len(panel) < n and keys:
        b = by[keys[i % len(keys)]]
        if b: panel.append(b[rng.randrange(len(b))])
        i += 1
        if i > n * 20: break
    seen = set(); uniq = []
    for p in panel:
        if p.name not in seen: seen.add(p.name); uniq.append(p)
    return [p._replace(playstyle=playstyles.assign_default_playstyle(p)) for p in uniq]

def win_into_field(arch, panel, tac_idx, runs, block=20000):
    pairs = [(arch, opp) for opp in panel if opp.name != arch.name]
    aw = bw = 0
    for s in range(0, len(pairs), block):
        blk = pairs[s:s + block]
        r = be.run_batch_random(blk, n_runs=runs, seed=2026 + s, mode="forced",
                                force_a=tac_idx, force_b=-1)
        aw += int(r["a_wins"].sum()); bw += int(r["b_wins"].sum())
    return aw / (aw + bw) if (aw + bw) else float("nan")

def edge_profile(arch, panel, runs):
    wr = {t: win_into_field(arch, panel, i, runs) for i, t in enumerate(TAC7)}
    vals = [v for v in wr.values() if v == v]
    mean = float(np.mean(vals))
    edge = {t: (v - mean if v == v else float("nan")) for t, v in wr.items()}
    return wr, edge, mean

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "lab_out"))
    ap.add_argument("--runs", type=int, default=200)
    ap.add_argument("--panel", type=int, default=50)
    ap.add_argument("--live-band", type=float, default=0.04)
    ap.add_argument("--dead-band", type=float, default=0.08)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    vc.invalidate_tactic_tables()

    panel = build_panel(args.panel)
    initpos = init_positive_tactics()
    print(f"Panel: {len(panel)} builds, retinues={dict(Counter(p.retinue for p in panel))}")
    print(f"Init-positive tactics (Unwieldy should suppress these): {initpos}\n")

    rows = []
    print("=" * 78)
    print("MARGINAL-EDGE PROFILE (edge = tactic win-into-field minus archetype mean)")
    print("  positive = build PREFERS the tactic; negative = pruned for this build")
    print("=" * 78)
    for name, arch in hand_archetypes():
        wr, edge, mean = edge_profile(arch, panel, args.runs)
        ranked = sorted(edge.items(), key=lambda kv: -(kv[1] if kv[1] == kv[1] else -9))
        live = [t for t, e in edge.items() if e == e and e >= -args.live_band]
        dead = [t for t, e in edge.items() if e == e and e < -args.dead_band]
        print(f"\n{name}   (mean wr {mean:.2f})")
        print("  edge:", "  ".join(f"{t[:4]}={e:+.2f}" for t, e in ranked))
        print(f"  LIVE: {live}")
        print(f"  DEAD: {dead}")
        for t in TAC7:
            rows.append({"archetype": name, "tactic": t, "win_into_field": wr[t],
                         "edge": edge[t], "is_live": t in live, "is_dead": t in dead,
                         "init_positive": t in initpos})

    print("\n" + "=" * 78)
    print("INITIATIVE COUPLING: Scout edge with Unwieldy ON vs OFF (Immune Unwieldy toggles it)")
    print("  Rule: Unwieldy zeros a tactic's +I, so Unwieldy should DROP Scout's edge.")
    print("=" * 78)
    coupling_builds = [
        ("Cav Spear (init+1, Unwieldy)", Ld("c_cs", "Sergeant", "Cavalry Spear", "Kite Shield", "Chainmail")),
        ("Lance (init+1, Unwieldy)",     Ld("c_ln", "Sergeant", "Lance", "Kite Shield", "Chainmail")),
    ]
    for name, b in coupling_builds:
        _, e_on, _ = edge_profile(b, panel, args.runs)
        _, e_off, _ = edge_profile(b._replace(extra_tags=frozenset({"Immune Unwieldy"})), panel, args.runs)
        print(f"\n{name}")
        print(f"  Scout edge  Unwieldy ON: {e_on['Scout']:+.3f}   OFF: {e_off['Scout']:+.3f}   "
              f"delta: {e_off['Scout']-e_on['Scout']:+.3f}  (positive delta = coupling works)")
        rows.append({"archetype": name + " [coupling]", "tactic": "Scout",
                     "edge_unwieldy_on": e_on["Scout"], "edge_unwieldy_off": e_off["Scout"]})

    pd.DataFrame(rows).to_csv(os.path.join(args.out, "tactic_pruning.csv"), index=False)
    print("\nWrote tactic_pruning.csv")

if __name__ == "__main__":
    main()
