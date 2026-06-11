#!/usr/bin/env python3
"""economy.py — per-turn gold model for Renown builds, derived from renown_data.

Model (per the designer's spec):
  * Purchase cost (one-time): by node type — Monument 300, Power 200, everything
    else 100. Retinue purchase = RETINUES[r]['cost'].
  * Upkeep (per turn) = retinue purchase cost - upkeep_effects reductions, summed
    over the army. (There is no separate base upkeep; the retinue cost IS the base.)
  * Trade income (per turn, only while trading): Craft +N  ->  100 * N * partners.
  * Other "+N" effects are per-turn FLAT GOLD only when the parser is confident it
    is gold (see _flat_gold); ambiguous +N (Influence/Trade Spec/Speed/etc.) are
    EXCLUDED and surfaced in the derivation table for manual confirmation.

Nothing here is written back into renown_data — it's derived live, so editing the
rules text or upkeep_effects updates the economy automatically. Use
`income_table()` to review every node's parsed income and override as needed.
"""
import re
import renown_data as rd

DEFAULT_PARTNERS = 2
SEASON_FRACTION = 0.25       # a seasonal/Winter effect fires 1 turn in 4
ARMY_SIZE = 25               # combat-sim army size; upkeep is FLAT (size-independent)

TAX_PER_TIER_PER_SETTLEMENT = 2000   # collected in Winter (every 4th turn)
# Canonical settlement data from renown_data.SETTLEMENTS (tax = Winter collection).
SETTLEMENT_TIER = {n: v["tier"] for n, v in rd.SETTLEMENTS.items()}
SETTLEMENT_TAX  = {n: v["tax_income"] for n, v in rd.SETTLEMENTS.items()}
TRADE_PER_CRAFT = rd.TRADE_RULES["income_per_craft"]
TRADE_SEASONS   = 0.75   # no trade income in Spring (1 of 4 turns)
# Canonical empire arc: everyone starts here and grows to here.
EMPIRE_START = ["Village", "Village", "Town"]      # 2 villages + 1 town
EMPIRE_END   = ["City", "City", "Town"]            # 2 cities + 1 town

def empire_slots(settlements):
    """Pursuit build capacity = sum of settlement tiers. Each tier allows 1
    pursuit; Efficient-X pursuits are the exception (they don't consume a slot,
    which is exactly the MPC discount the combat pool already applies)."""
    return sum(SETTLEMENT_TIER.get(s, 1) for s in settlements)

def empire_tax(settlements):
    """Per-turn tax, averaged (collected only in Winter = 1 turn in 4).
    Uses the canonical per-settlement Winter values from renown_data.SETTLEMENTS
    (Village 2000 / Town 4000 / City 6000 / Metropolis 10000; Hamlet 0)."""
    winter = sum(SETTLEMENT_TAX.get(s, 0) for s in settlements)
    return winter * SEASON_FRACTION

def tax_income(settlements=1, avg_tier=1):
    """Legacy scalar form: 2000 per settlement-tier, 1 turn in 4."""
    return TAX_PER_TIER_PER_SETTLEMENT * avg_tier * settlements * SEASON_FRACTION

PURCHASE_BY_TYPE = {"Monument": 300, "Power": 200}      # else 100
def purchase_cost(node):
    return PURCHASE_BY_TYPE.get(rd.NODES.get(node, {}).get("type", ""), 100)

# tokens after a "+N" that mean it is NOT gold
_NOT_GOLD = re.compile(
    r"(influence|trade\s*spec|craft|siege|speed|recover|endurance|maximum|reach|"
    r"build\s*timer|domain|i\b|i;|i\.|initiative)", re.I)
_CRAFT = re.compile(r"Craft\s*\+(\d+)", re.I)

def _craft_plus(text):
    return sum(int(m) for m in _CRAFT.findall(text or ""))

SPEC_COUNT      = 4        # assumed active specs for "+N per spec" (Manor House)
PLAYERS_WO      = 2        # assumed players lacking a building for Extort-style income

def _flat_gold(text):
    """Per-turn flat gold from '+N' tokens (N>=100), with the designer's
    assumptions applied: seasonal counts at 1/4, '+N per spec' at SPEC_COUNT,
    Extort-per-player at PLAYERS_WO. Returns (gold, notes)."""
    if not text:
        return 0, []
    total, notes = 0.0, []
    for m in re.finditer(r"\+(\d+)([^,;|]*)", text):
        n, tail = int(m.group(1)), m.group(2)
        if n < 100 or _NOT_GOLD.search(tail):
            continue
        if re.search(r"in (Fall|Winter|Spring|Summer)", tail, re.I):
            total += n * SEASON_FRACTION; notes.append(f"seasonal +{n}@1/4")
        elif re.search(r"for each|per .*spec", tail, re.I):
            total += n * SPEC_COUNT;      notes.append(f"+{n}x{SPEC_COUNT}specs")
        else:
            total += n
    # Extort-style "Extort N per player without X" (not a '+N' token)
    for m in re.finditer(r"Extort\s*(\d+)\s*per player", text, re.I):
        total += int(m.group(1)) * PLAYERS_WO; notes.append(f"extort {m.group(1)}x{PLAYERS_WO}")
    return total, notes

def node_income(node, partners=DEFAULT_PARTNERS, mastered=False):
    """Per-turn gold from a single node (innate always; mastery if `mastered`)."""
    v = rd.NODES.get(node, {})
    innate, mastery = v.get("innate", ""), v.get("mastery", "")
    text = innate + (" || " + mastery if mastered else "")
    craft = _craft_plus(text)
    flat, notes = _flat_gold(text)
    return {"craft": craft, "craft_gold": TRADE_PER_CRAFT * craft * partners * TRADE_SEASONS,
            "flat_gold": flat, "income": TRADE_PER_CRAFT * craft * partners * TRADE_SEASONS + flat, "notes": notes}

def _upkeep_reduction(node):
    red = 0
    for eff in rd.NODES.get(node, {}).get("engine", {}).get("upkeep_effects", []):
        red += sum(v for k, v in eff.items() if k in ("flat",))   # conditional handled at build level
    return red

def build_economy(pursuits, retinue, partners=DEFAULT_PARTNERS,
                  settlements=1, avg_tier=1, empire=None,
                  has_shield=False, has_ranged=False, mastered_all=True):
    """Net per-turn gold for a build. Upkeep is FLAT per army (the retinue cost
    is the army's upkeep, independent of size).

    Returns purchase (one-time), upkeep/turn, income/turn, net/turn, solvent.
    """
    pset = set(pursuits)
    # one-time: pursuit purchase by type + the army's purchase cost
    purchase = sum(purchase_cost(n) for n in pset) + rd.RETINUES[retinue]["cost"]
    # per-turn upkeep: army cost minus flat reductions (+ conditional if equipped)
    red = 0
    for n in pset:
        for eff in rd.NODES.get(n, {}).get("engine", {}).get("upkeep_effects", []):
            red += eff.get("flat", 0)
            if has_shield: red += eff.get("if_shield", 0)
            if has_ranged: red += eff.get("if_ranged", 0)
    upkeep = max(0, rd.RETINUES[retinue]["cost"] - red)
    # per-turn income
    pursuit_income = sum(node_income(n, partners=partners,
                                     mastered=mastered_all)["income"] for n in pset)
    tax = empire_tax(empire) if empire is not None else tax_income(settlements, avg_tier)
    income = pursuit_income + tax
    net = income - upkeep
    return {"purchase": purchase, "upkeep_per_turn": upkeep,
            "tax_per_turn": round(tax), "pursuit_income_per_turn": round(pursuit_income),
            "income_per_turn": round(income), "net_per_turn": round(net),
            "solvent": net >= 0}

def income_table(partners=DEFAULT_PARTNERS):
    """Per-node derivation for review. Only nodes with parsed income/upkeep shown."""
    import pandas as pd
    rows = []
    for n, v in rd.NODES.items():
        inn = node_income(n, partners, mastered=False)
        mas = node_income(n, partners, mastered=True)
        red = _upkeep_reduction(n)
        if inn["income"] or mas["income"] or red or inn["notes"] or mas["notes"]:
            rows.append({"node": n, "type": v.get("type", ""),
                         "purchase": purchase_cost(n),
                         "craft_innate": inn["craft"], "craft_mastered": mas["craft"],
                         "flat_gold_innate": inn["flat_gold"],
                         "income_innate": inn["income"], "income_mastered": mas["income"],
                         "upkeep_reduction": red,
                         "flags": "; ".join(sorted(set(inn["notes"] + mas["notes"])))})
    return pd.DataFrame(rows)

if __name__ == "__main__":
    import pandas as pd
    pd.set_option("display.width", 200, "display.max_rows", 100)
    t = income_table()
    print(f"=== Per-node economy (partners={DEFAULT_PARTNERS}) ===")
    print(t.to_string(index=False))
    print("\nFlags = parsed '+N' that was EXCLUDED from steady income (confirm/override).")
