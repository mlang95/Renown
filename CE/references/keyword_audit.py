#!/usr/bin/env python3
# keyword_audit.py [renown_data_d10.py] > audit.tsv  — what each offensive weapon keyword changes, per strike die (rules as written).
"""Exact per-strike-die model of the Renown CE strike chain (rules text as written),
used to measure what each offensive keyword actually changes on each weapon.

Strike: natural d10 + mods >= to-Strike; Shielded (shield, unless attacker Negate Shielded) = -1, capped 10+.
Focused = natural 10. Cleave: a Focused Strike rolls one extra Strike die (not chained).
Per hit: Parry (if defender has Parry): PARRY_BASE - improved; Unstoppable +2; capped 10+.
         Deadly-focused: Parry only on natural 10. Riposte: natural-10 Parry vs a melee Strike, unless Negate Riposte.
Save: need = armor - AP - shield bonus (Deadly-focused: AP-5); need > 10 -> fails, unless Planishing
      (and attacker lacks Negate Planishing) -> succeeds on natural 10.
Recover (if defender has it): d10 >= R after a failed Save; Deadly-focused: natural 10 only.
"""
import sys, itertools, importlib.util
from fractions import Fraction as F

spec = importlib.util.spec_from_file_location("renown_data", sys.argv[1] if len(sys.argv) > 1 else "../renown_data_d10.py")
rd = importlib.util.module_from_spec(spec); sys.modules["renown_data"] = rd; spec.loader.exec_module(rd)

PB, CAP, UM, DAP = rd.PARRY_BASE, rd.CAP_THR, rd.UNSTOPPABLE_MOD, rd.DEADLY_AP
U, D, NS, NR, NP, CL, DS = (rd.UNSTOPPABLE, rd.SHATTER_ARMOR, rd.NEGATE_SHIELDED, rd.NEGATE_RIPOSTE,
                            rd.NEGATE_TEMPERED, rd.CLEAVE, rd.DESTROY_SHIELD)
STRIKE_KW = [U, D, NS, NR, NP, CL]
TOHIT = sorted({r["to_hit"] for r in rd.RETINUES.values()})
ARMOR = sorted({a["save"] for a in rd.ARMORS.values()})
SHIELD = sorted({(s["save_bonus"], rd.MINUS_1_TBH in s["tags"]) for s in rd.SHIELDS.values()})
PARRY = [None, PB, PB - 1, PB - 2]          # none / base / Improved Parry x1 / x2
RECOV = [None, 8, 7, 6]
CONFIGS = [c for c in itertools.product(ARMOR, SHIELD, PARRY, [False, True], RECOV, [False, True])
           if not (c[2] is None and c[3])]   # Riposte needs Parry

def p_ge(need):                  # P(natural d10 >= need), need clipped to 1..11
    need = max(1, need)
    return F(0) if need > 10 else F(11 - need, 10)

def hit_cas(tags, ap, ranged, cfg, focused):
    S, (b, sh), P, rip, R, plan = cfg
    dead = focused and D in tags
    if P is None: pp = F(0)
    elif dead: pp = F(1, 10)
    else: pp = p_ge(min(P + (UM if U in tags else 0), CAP))
    ripo = F(1, 10) if (P is not None and rip and not ranged and NR not in tags) else F(0)
    a = ap - (DAP if dead else 0)
    need = S - a - b
    s = p_ge(need) if need <= 10 else (F(1, 10) if plan and NP not in tags else F(0))
    rec = F(0) if R is None else (F(1, 10) if dead else p_ge(R))
    return (1 - pp) * (1 - s) * (1 - rec), ripo

def die(tags, ap, ranged, cfg, T, cleave=True):
    S, (b, sh), *_ = cfg
    need = min(T + (1 if sh and NS not in tags else 0), CAP)
    p_nf = max(F(0), F(10 - need, 10))
    c_nf, r_nf = hit_cas(tags, ap, ranged, cfg, False)
    c_f, r_f = hit_cas(tags, ap, ranged, cfg, True)
    cas, rip = p_nf * c_nf + F(1, 10) * c_f, p_nf * r_nf + F(1, 10) * r_f
    if cleave and CL in tags:
        c2, r2 = die(tags, ap, ranged, cfg, T, cleave=False)
        cas, rip = cas + F(1, 10) * c2, rip + F(1, 10) * r2
    return cas, rip

def needs(cfg):
    S, (b, sh), P, rip, R, plan = cfg
    return {"parry": P is not None, "riposte": rip, "recover": R is not None, "planishing": plan, "shield": b > 0}

rows = []
items = [(n, w, False) for n, w in rd.WEAPONS.items()] + [(n, w, True) for n, w in rd.RANGED.items()]
for name, w, ranged in items:
    tags = set(w["tags"]); ap = w["ap"]
    for kw in [k for k in STRIKE_KW if k in tags]:
        without = tags - {kw}
        dmax, rmax, n_eff, n_all, dsum = F(0), F(0), 0, 0, F(0)
        for cfg in CONFIGS:
            for T in TOHIT:
                a, ra = die(tags, ap, ranged, cfg, T); b, rb = die(without, ap, ranged, cfg, T)
                d = a - b; r = rb - ra       # casualties added; ripostes prevented
                n_all += 1; dsum += d
                if d != 0 or r != 0: n_eff += 1
                dmax, rmax = max(dmax, d), max(rmax, r)
        rows.append((name, kw, n_eff / n_all, float(dmax), float(rmax), float(dsum / n_all)))
    if DS in tags:   # Destroy Shield: casualty gain per later die if the target's shield were gone
        gain, n_eff, n_sh = F(0), 0, 0
        for cfg in CONFIGS:
            if cfg[1][0] == 0: continue
            n_sh += 1
            for T in TOHIT:
                a, _ = die(tags, ap, ranged, cfg, T)
                bare = (cfg[0], (0, False)) + cfg[2:]
                c, _ = die(tags, ap, ranged, bare, T)
                gain = max(gain, c - a); n_eff += (c != a)
        rows.append((name, DS, n_eff / (n_sh * len(TOHIT)), float(gain), 0.0, None))

print("weapon\tkeyword\tshare_of_matchups_where_it_changes_anything\tmax_extra_casualties_per_die\tmax_ripostes_prevented_per_die\tmean_extra_casualties_per_die")
for r in rows:
    print("\t".join([r[0], r[1], f"{r[2]:.0%}", f"{r[3]:.3f}", f"{r[4]:.3f}", "" if r[5] is None else f"{r[5]:.4f}"]))
print(f"\nconfigs={len(CONFIGS)} x to-Strike {TOHIT}")
