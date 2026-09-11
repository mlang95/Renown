#!/usr/bin/env python3
"""two_monument_builds.py — for the monument cap of 2, generate every viable
2-monument build in a 2-City + 1-Metropolis + 1-Hamlet empire (10 general + 4
husbandry wards), measure how efficiently the pair's required chains pack, and
fill leftover wards with the deepest spare efficient chains (best income).

Reports per pair: required wards (after Efficient collapse + shared overlap),
spare wards, what fills them, and the build's total pursuit count.
"""
import sys, itertools
sys.path.insert(0, ".")
import renown_data as rd
import monument_viability as mv
import economy as ec
from collections import defaultdict

N = rd.NODES
GEN, HUSB = mv.GEN_WARDS, mv.HUSB_WARDS

def is_husb(n): return N[n].get("type") == "Husbandry"

# ---- ward bookkeeping ----
def ward_roots(nodeset):
    """{root: [members]} grouping a set of nodes by efficient anchor."""
    g = defaultdict(list)
    for n in nodeset:
        g[mv.ward_root(n)].append(n)
    return g

def split_wards(roots):
    gen = [r for r in roots if not is_husb(r)]
    husb = [r for r in roots if is_husb(r)]
    return gen, husb

# spare efficient chains to fill leftover wards (deepest first, disjoint)
_children = defaultdict(list)
for n, e in rd.EFFICIENT.items():
    _children[e].append(n)
def deepest_chain(anchor, used):
    if anchor in used: return [anchor]
    best = []
    for c in _children.get(anchor, []):
        sub = deepest_chain(c, used | {anchor})
        if len(sub) > len(best): best = sub
    return [anchor] + best

def _chain_net(chain):
    return sum(ec.node_income(n)["income"] - mv.node_upkeep(n) for n in chain)

def fill_spare(used_nodes, gen_free, husb_free, by="income"):
    """Fill leftover wards with disjoint efficient chains. by='income' ranks each
    candidate chain by net income per ward (realistic — players fill spare wards
    with the most profitable development); by='depth' maximises raw pursuit count."""
    used = set(used_nodes); fills = []; added = 0
    while gen_free > 0 or husb_free > 0:
        best = None
        for r in N:
            if rd.EFFICIENT.get(r) or r in used:
                continue
            chain = [c for c in deepest_chain(r, used) if c not in used]
            if not chain:
                continue
            if is_husb(r) and husb_free <= 0: continue
            if not is_husb(r) and gen_free <= 0: continue
            score = _chain_net(chain) if by == "income" else len(chain)
            if best is None or score > best[0]:
                best = (score, r, chain)
        if best is None:
            break
        _, r, chain = best
        if is_husb(r): husb_free -= 1
        else: gen_free -= 1
        used |= set(chain); added += len(chain); fills.append((r, chain))
    return added, fills

def analyze_pair(a, b):
    chain = mv.closure(a) | mv.closure(b)            # union (shared nodes once)
    roots = ward_roots(chain)
    gen, husb = split_wards(roots)
    fits = len(gen) <= GEN and len(husb) <= HUSB
    req_pursuits = len(chain)
    gen_free, husb_free = GEN - len(gen), HUSB - len(husb)
    added, fills = (0, [])
    all_nodes = set(chain)
    if fits:
        added, fills = fill_spare(chain, gen_free, husb_free)
        for _, fchain in fills:
            all_nodes |= set(fchain)
    # combined cash flow: tax + every pursuit's income - every pursuit's upkeep
    income = mv.TAX + sum(ec.node_income(n)["income"] for n in all_nodes)
    upkeep = sum(mv.node_upkeep(n) for n in all_nodes)
    net = income - upkeep
    return dict(a=a, b=b, gen=len(gen), husb=len(husb), fits=fits,
                req_pursuits=req_pursuits, spare_gen=gen_free, spare_husb=husb_free,
                filled=added, total_pursuits=req_pursuits + added, fills=fills,
                net=net, income=income, upkeep=upkeep,
                solvent=(fits and net >= 0))

if __name__ == "__main__":
    mons = [n for n, v in N.items() if v.get("type") == "Monument"]
    pairs = [analyze_pair(a, b) for a, b in itertools.combinations(mons, 2)]
    fit = [p for p in pairs if p["fits"]]
    solvent = [p for p in fit if p["solvent"]]
    fit.sort(key=lambda p: -p["total_pursuits"])
    print(f"{len(fit)}/{len(pairs)} pairs fit wards | {len(solvent)}/{len(fit)} of those are also cash-flow positive\n")
    print(f"{'Monument pair':<48}{'wards':>6}{'total':>6}{'net/turn':>10}{'solvent':>9}")
    print("-"*80)
    for p in fit[:18]:
        name = f"{p['a'][:21]} + {p['b'][:21]}"
        wards = f"{p['gen']}+{p['husb']}h"
        flag = "OK" if p["solvent"] else "NEG"
        print(f"{name:<48}{wards:>7}{p['total_pursuits']:>6}{p['net']:>+10.0f}{flag:>9}")
    neg = [p for p in fit if not p["solvent"]]
    if neg:
        print(f"\nWard-fitting but CASH-NEGATIVE pairs: {len(neg)}")
        for p in sorted(neg, key=lambda x: x['net'])[:6]:
            print(f"  {p['a']} + {p['b']}: net {p['net']:+.0f}")
