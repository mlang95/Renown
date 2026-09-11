#!/usr/bin/env python3
"""monument_viability.py — for every Monument, test the two viability constraints:
  (1) WARD FOOTPRINT: does the monument's required pursuit chain (after Efficient
      collapse) fit a 2-City + 1-Metropolis + 1-Hamlet empire?
        general wards = 3+3+4 = 10 ; husbandry-only wards (Hamlet) = 4
  (2) CASH FLOW: with remaining wards filled by the best income pursuits, is the
      build net positive (tax + pursuit income - upkeep >= 0)?
Efficient pursuits stack into a shared ward (cost 0 extra) — ward cost of a set =
number of distinct Efficient stack-groups it spans.
"""
import sys
sys.path.insert(0, ".")
import renown_data as rd
import economy as ec

GEN_WARDS, HUSB_WARDS = 10, 4
SETTLE = ["City", "City", "Metropolis"]   # hamlet tax 0, husbandry-only
TAX = ec.empire_tax(SETTLE + ["Hamlet"])  # avg per turn

N = rd.NODES

# ---- Efficient stack-group (ward) resolution ----
# Single source of truth: renown_data.EFFICIENT (parsed from "**Efficient X**" text).
_parent = rd.EFFICIENT

def ward_root(n):
    seen = set()
    while n in _parent and n not in seen:
        seen.add(n); n = _parent[n]
    return n

def _reqs(name):
    """All prerequisite node names: engine.prereqs + parsed text mastery_req."""
    v = N.get(name, {})
    reqs = list(v.get("engine", {}).get("prereqs", []) or [])
    txt = v.get("mastery_req", "") or ""
    for part in txt.split("+"):
        p = part.strip()
        if p in N and p not in reqs:
            reqs.append(p)
    return reqs

def closure(name, seen=None):
    seen = seen or set()
    if name in seen or name not in N: return seen
    seen.add(name)
    for p in _reqs(name):
        closure(p, seen)
    return seen

def is_husb(n): return N[n].get("type") == "Husbandry"

def footprint(nodes):
    """(general_wards, husbandry_wards) consumed by a set of nodes.
    A ward's type follows its ANCHOR (where the stack physically sits): a stack
    rooted on a Husbandry node is a Hamlet ward even if general nodes stack onto
    it (e.g. Tannery -> Animal Husbandry). Classify each distinct root once, by
    the root's own type — never double-count a root in both buckets."""
    roots = {ward_root(n) for n in nodes}
    gen = {r for r in roots if not is_husb(r)}
    husb = {r for r in roots if is_husb(r)}
    return len(gen), len(husb)

def node_net(n):
    inc = ec.node_income(n)["income"]
    up = ec.purchase_cost  # not used per-turn; upkeep:
    return inc

def node_upkeep(n):
    v = N[n]
    base = {"Monument": 300, "Power": 200}.get(v.get("type"), 100)
    red = ec._upkeep_reduction(v.get("innate", "") or "")
    return max(0, base - red)

# best income pursuits to fill spare wards (by net income per ward), split by type
def income_candidates():
    husb, gen = [], []
    for n, v in N.items():
        inc = ec.node_income(n)["income"]
        net = inc - node_upkeep(n)
        (husb if is_husb(n) else gen).append((net, n))
    husb.sort(reverse=True); gen.sort(reverse=True)
    return gen, husb

GEN_FILL, HUSB_FILL = income_candidates()

def analyze(mon):
    chain = closure(mon)
    g, h = footprint(chain)
    chain_income = sum(ec.node_income(n)["income"] for n in chain)
    chain_upkeep = sum(node_upkeep(n) for n in chain)
    gen_free, husb_free = GEN_WARDS - g, HUSB_WARDS - h
    fits = gen_free >= 0 and husb_free >= 0
    # fill spare wards with best net-income pursuits not already in chain
    add_inc = add_up = 0
    used = set(chain)
    for net, n in GEN_FILL:
        if gen_free <= 0: break
        if n in used or net <= 0: continue
        used.add(n); gen_free -= 1
        add_inc += ec.node_income(n)["income"]; add_up += node_upkeep(n)
    for net, n in HUSB_FILL:
        if husb_free <= 0: break
        if n in used or net <= 0: continue
        used.add(n); husb_free -= 1
        add_inc += ec.node_income(n)["income"]; add_up += node_upkeep(n)
    income = TAX + chain_income + add_inc
    upkeep = chain_upkeep + add_up
    net = income - upkeep
    return dict(mon=mon, gen=g, husb=h, fits=fits, chain_net=chain_income - chain_upkeep,
                net=net, income=income, upkeep=upkeep,
                gen_free=GEN_WARDS - g, husb_free=HUSB_WARDS - h)

if __name__ == "__main__":
    mons = [n for n, v in N.items() if v.get("type") == "Monument"]
    print(f"Empire: 2 City + 1 Metropolis + 1 Hamlet | general wards {GEN_WARDS}, husbandry {HUSB_WARDS} | tax/turn {TAX:.0f}\n")
    print(f"{'Monument':<34}{'genW':>5}{'husW':>5}{'fits':>6}{'net/turn':>10}")
    print("-"*60)
    for m in sorted(mons, key=lambda x: analyze(x)["net"], reverse=True):
        a = analyze(m)
        flag = "OK" if a["fits"] else "OVER"
        print(f"{m:<34}{a['gen']:>5}{a['husb']:>5}{flag:>6}{a['net']:>+10.0f}")
