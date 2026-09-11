#!/usr/bin/env python3
"""income_profile.py — classify a build's economy by SOURCE, tag its inflation
character and exposure, and describe its risk shape. Descriptive layer (no
risk-adjusted EV yet — that needs attack magnitudes/inflation model to be set).

Five sources, read from renown_data node text:
  TAX        — settlement base (Winter); exposed to Destabilise (removes one
               settlement's tax for 4 turns; each settlement target-once per cycle).
  PURSUIT    — Craft/Natural income; MINTS new gold (inflationary); exposed to
               Foster Rebellion (Execution Dock defends).
  TRADE      — 100 x Craft x partners; MINTS gold; partner-coupled (high variance);
               exposed to Intercept Caravan (Caravanery defends).
  EXTORTION  — TRANSFER of opponents' gold (NON-inflationary); adversarial,
               retaliation-exposed (Black Market counter-extorts); scales with
               opponents' wealth.
  UPKEEP_RED — not income; a HEDGE that lowers the floor you must cover.

Defense is a build choice: Influence (from Domain standings) + the four defender
nodes (Caravanery/Execution Dock/Chandlery/Monastery) reduce envoy success, so a
source is "exposed" only if the build lacks its defender.
"""
import sys, re
sys.path.insert(0, ".")
import renown_data as rd
import economy as ec

N = rd.NODES

DEFENDERS = {            # node -> the attack action it blunts (Influence -1 to it)
    "Caravanery": "Intercept Caravan",   # defends TRADE
    "Execution Dock": "Foster Rebellion", # defends PURSUIT/settlement
    "Monastery": "Cunning (Piety envoys)",
    "Chandlery": "Cunning",
}
# which source each attack hits
ATTACKS = {
    "Destabilise": "TAX",
    "Intercept Caravan": "TRADE",
    "Foster Rebellion": "PURSUIT",
    "Counter-Extort (Black Market)": "EXTORTION",
}

def _txt(n): return (N[n].get("innate","") or "") + " | " + (N[n].get("mastery","") or "")

def source_tags(n):
    t = _txt(n); tags = set()
    if re.search(r"Extort", t): tags.add("EXTORTION")
    if re.search(r"Craft \+|\+\d+, \*\*Natural\*\*", t): tags.add("PURSUIT")
    if re.search(r"Trade Partner|Trade Specialization|\bTrade\b", t): tags.add("TRADE")
    if re.search(r"Upkeep [-−]\d+", t): tags.add("UPKEEP_RED")
    return tags

INFLATION = {"PURSUIT": "mint", "TRADE": "mint", "EXTORTION": "transfer",
             "TAX": "mint", "UPKEEP_RED": "—"}  # tax is minted by the crown too
VARIANCE = {"TAX": "low (catastrophic tail: lose a city)",
            "PURSUIT": "moderate (per-settlement, Foster Rebellion)",
            "TRADE": "HIGH (x partners; Intercept; alliance-coupled)",
            "EXTORTION": "HIGH (adversarial; counter-extort; opponent-wealth-coupled)",
            "UPKEEP_RED": "none (hedge)"}

def profile(pursuits, settlements=("City","City","Metropolis","Hamlet")):
    """pursuits: iterable of node names. Returns the build's income profile."""
    pursuits = set(pursuits)
    tax = ec.empire_tax(list(settlements))
    by_source = {"TAX": tax, "PURSUIT": 0, "TRADE": 0, "EXTORTION": 0, "UPKEEP_RED": 0}
    members = {"PURSUIT": [], "TRADE": [], "EXTORTION": [], "UPKEEP_RED": []}
    opponents = max(1, len([x for x in settlements]) and 3)  # assume ~3 opponents for "per player" extort
    for n in pursuits:
        if n not in N: continue
        for s in source_tags(n):
            members[s].append(n)
            if s == "UPKEEP_RED":
                by_source[s] += ec._upkeep_reduction(N[n].get("mastery","") or "") or 200
            elif s == "EXTORTION":
                t = _txt(n)
                amt = 0
                for m in re.finditer(r"Extort\s+(\d+)", t):
                    base = int(m.group(1))
                    # "per player / every player" scales by opponent count
                    amt += base * (opponents if re.search(r"(per|every)\s+\**player", t, re.I) else 1)
                by_source[s] += amt
            else:
                by_source[s] += ec.node_income(n)["income"]
    # exposure: which sources lack their defender in this build
    have_def = {d for d in DEFENDERS if d in pursuits}
    exposed = {}
    for atk, src in ATTACKS.items():
        defender = next((d for d, a in DEFENDERS.items() if a == atk), None)
        exposed[src] = (defender not in have_def) if defender else True  # Destabilise/Tax: no node defender (Influence only)
    return dict(by_source=by_source, members=members, exposed=exposed,
                inflationary=sum(by_source[s] for s in ("PURSUIT","TRADE","TAX")),
                transfer=by_source["EXTORTION"], have_defenders=sorted(have_def))

def describe(pursuits, settlements=("City","City","Metropolis","Hamlet")):
    p = profile(pursuits, settlements)
    bs = p["by_source"]
    gross = sum(v for k,v in bs.items() if k != "UPKEEP_RED")
    lines = ["INCOME PROFILE", f"  gross income/turn-equiv: {gross:.0f}  (upkeep hedge: -{bs['UPKEEP_RED']:.0f})", ""]
    for s in ("TAX","PURSUIT","TRADE","EXTORTION"):
        v = bs[s]; pct = (v/gross*100) if gross else 0
        exp = "EXPOSED" if p["exposed"].get(s) else "defended"
        lines.append(f"  {s:<10} {v:>7.0f} ({pct:4.0f}%)  {INFLATION[s]:<8} | {exp:<8} | var: {VARIANCE[s]}")
    infl_pct = p["inflationary"]/gross*100 if gross else 0
    lines += ["",
              f"  inflation: {infl_pct:.0f}% of income MINTS new gold; {100-infl_pct:.0f}% is TRANSFER (extortion)",
              f"  defenders held: {', '.join(p['have_defenders']) or 'none — all attack vectors open'}"]
    return "\n".join(lines)

if __name__ == "__main__":
    # demo: a trade-heavy vs an extortion-heavy build
    trade_build = ["Quarry","Masonry","Market Square","Merchant Quarter","Shipyard","Harbor","Fishmongery","Caravanery"]
    extort_build = ["Money Lending","Court Artists","Black Market","Thieves' Guild","Pilgrimage Site","Toll House","Secret Cellar"]
    print("=== TRADE-HEAVY BUILD ===")
    print(describe(trade_build))
    print("\n=== EXTORTION-HEAVY BUILD ===")
    print(describe(extort_build))
