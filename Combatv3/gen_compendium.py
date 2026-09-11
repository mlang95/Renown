#!/usr/bin/env python3
"""gen_compendium.py — generate the Compendium reference as JSON tables from
renown_data (the single source of truth), then hand to a docx writer.

Emits a structured dict the JS builder consumes, so the printed Compendium can
never drift from the canonical NODES / FACTIONS / INFRASTRUCTURE / WONDERS /
RETINUES / equipment / SETTLEMENTS / ERAS / DOMAIN_BOARD data.
"""
import json, sys
sys.path.insert(0, ".")
import renown_data as rd

SECTION_ORDER = ["Raw Materials", "Husbandry", "Craft", "Civic", "Secrecy",
                 "Energy", "Power", "Monument"]

def pursuit_sections():
    secs = []
    for t in SECTION_ORDER:
        rows = []
        for n, v in rd.NODES.items():
            if v.get("type") != t:
                continue
            eff = v.get("efficient")
            innate = v.get("innate", "") or ""
            if eff:
                eff_txt = "**Efficient " + (eff if isinstance(eff, str) else ", ".join(eff)) + "**"
                innate = eff_txt + ("; " + innate if innate else "")
            rows.append([n, v.get("mastery_req", "") or "—",
                         innate or "—", v.get("mastery", "") or "—"])
        if rows:
            secs.append({"title": t, "rows": rows})
    return secs

def equipment_tables():
    out = {}
    out["Retinues"] = [[n, f"{x['cost']}", f"{x['to_hit']}+", f"{x['endurance']}",
                        f"{x['shaking']}+", "Unbreakable" if x.get("unbreakable") else "—"]
                       for n, x in rd.RETINUES.items()]
    out["Weapons"] = [[n, x["tier"], f"{x['ap']}", f"{x['init']:+d}",
                       ", ".join(x["tags"]) or "—"] for n, x in rd.WEAPONS.items()]
    out["Ranged"] = [[n, x["tier"], f"{x['ap']}", f"{x['init']:+d}",
                      ", ".join(x["tags"]) or "—"] for n, x in rd.RANGED.items()]
    out["Shields"] = [[n, x["tier"], f"+{x['save_bonus']}", f"{x['init']:+d}",
                       ", ".join(x["tags"]) or "—"] for n, x in rd.SHIELDS.items() if n]
    out["Armor"] = [[n, x["tier"], f"{x['save']}+", ", ".join(x["tags"]) or "—"]
                    for n, x in rd.ARMORS.items()]
    return out

def infra_tables():
    infra = [[n, str(e["upkeep"]), e["upkeep_frequency"], e["empire_bonus"],
              e["tier"], str(e["build_time"]), e["requirement"]]
             for n, e in rd.INFRASTRUCTURE.items()]
    wonders = [[n, e["empire_bonus"], str(e["build_time"]), e["requirement"]]
               for n, e in rd.WONDERS.items()]
    return infra, wonders

def faction_rows():
    return [[n, f.get("mechanic", "")] for n, f in rd.FACTIONS.items()]

def settlement_rows():
    return [[n, str(v["tier"]), v["sea_variant"] or "—", str(v["tax_income"]),
             str(v["muster_limit"]), str(v["build_time"]), str(v["wards"]),
             str(v["reach"]), v["notes"] or "—"] for n, v in rd.SETTLEMENTS.items()]

def era_rows():
    return [[n, str(v["renown"]), str(v["armies"]), str(v["cities"]),
             f"+{v['influence_per_turn']}", str(v["innate_diplomacy_influence"]),
             v["envoys"], v["unlocks"] or "—"] for n, v in rd.ERAS.items()]

def domain_board_rows():
    b = rd.DOMAIN_BOARD
    rows = []
    for dom in ["Industry", "Prowess", "Cunning", "Piety"]:
        d = b[dom]
        rows.append([dom, d.get("Rising", ""), d.get("Established", ""), d.get("Sovereign", "")])
    return rows

def standings_rows():
    return [[n, v.get("standing", ""), "; ".join(f"{k}: {x}" for k, x in v.get("ranks", {}).items())]
            for n, v in rd.NODES.items() if "escalation" in v]


GLOSSARY_CATEGORIES = [
    ("Combat Keywords", ["Steady","Unwieldy","2H","Two-handed","Deadly","Shatter Armor","Unstoppable",
        "Cleave","Poison","Nimble","Drilled","Destroy Shield","Blunder","One-Shot","Deflect",
        "Immune Panic","Unbreakable","Parry","Riposte","Recover","Serrated","Planishing",
        "Fatigue token","Improved Parry","Blocked","Strained","Seize the Initiative","Heal X",
        "Immune [keyword]","AP"]),
    ("Battle Structure", ["Attacker / Defender","Battle","Skirmish","Casualty","Field","Endurance",
        "Fatigued","Break check","Panic check","Morale","Rout","Fall Back","Strike",
        "to-Strike number","Save","Natural roll","Initiative","Tactic","Dual-equip"]),
    ("Council & Diplomacy", ["Influence","Influence X","Envoy","Vote","Support X","Oppose X","Abstain",
        "Net Influence","Endorsed","Condemned","Council Phase","Council Envoy","Personal Envoy",
        "Diplomacy","Treaty","Alliance","Vassal","Suzerain"]),
    ("Empire & Economy", ["Faith X","Doubt X","Extort X","Recoup","Speed","Edict","Monument","Charter",
        "Muster","Pursue","Build","Repair","Move","Demand Tribute","Renown","Domain","Domain Point",
        "Standing","Public Order","Reach"]),
    ("World", ["Bandit","Outlaw Country","Siege"]),
]

def glossary_categorized():
    g = {str(k): v for k, v in rd.GLOSSARY.items()}
    used, cats = set(), []
    for title, terms in GLOSSARY_CATEGORIES:
        rows = [[t, g[t]] for t in terms if t in g]
        used.update(t for t in terms if t in g)
        if rows:
            cats.append({"title": title, "rows": rows})
    other = [[k, v] for k, v in sorted(g.items()) if k not in used]
    if other:
        cats.append({"title": "Other", "rows": other})
    return cats

def standing_effects_rows():
    by = {}
    for (dom, st), eff in rd.STANDING_EFFECTS.items():
        by.setdefault(dom, {})[st] = eff
    rows = []
    for dom in ["Industry","Prowess","Cunning","Piety"]:
        d = by.get(dom, {})
        if d:
            rows.append([dom, d.get("Rising","—"), d.get("Established","—"), d.get("Sovereign","—")])
    return rows

def po_rows():
    return [[str(k), name, eff] for k,(name,eff) in sorted(rd.PUBLIC_ORDER.items())]

def po_modifier_rows():
    rows = []
    for sign in ("faith","doubt"):
        for src, cond in rd.PO_MODIFIERS[sign].items():
            rows.append([sign.title(), src, cond])
    return rows

def season_rows():
    return [[s, v["name"], v["effect"]] for s,v in rd.SEASONS.items()]

def trade_rows():
    t = rd.TRADE_RULES
    return [["Income per Craft", str(t["income_per_craft"])],
            ["Requirements", t["requirements"]],
            ["No-trade season", t["no_trade_season"]],
            ["Tax season", t["tax_season"]]]

def tactic_matrix_grid():
    T = rd.TACTICS
    def cell(a,b):
        v = rd.TACTIC_MATRIX.get((a,b))
        if not v: return ""
        me = v[0]
        bits = []
        if me.get("I"): bits.append(f"I{me['I']:+d}")
        if me.get("TH"): bits.append(f"TH{me['TH']:+d}")
        if me.get("TS"): bits.append(f"TS{me['TS']:+d}")
        if me.get("no_combat"): bits.append("no-cbt")
        return " ".join(bits) or "—"
    header = ["vs →"] + T
    rows = [[a] + [cell(a,b) for b in T] for a in T]
    return header, rows


def build_payload():
    infra, wonders = infra_tables()
    tm_header, tm_rows = tactic_matrix_grid()
    return {
        "version": getattr(rd, "VERSION", ""),
        "glossary": rd.GLOSSARY,
        "glossary_categorized": glossary_categorized(),
        "standing_effects": standing_effects_rows(),
        "public_order": po_rows(),
        "po_modifiers": po_modifier_rows(),
        "seasons": season_rows(),
        "trade_rules": trade_rows(),
        "tactic_matrix_header": tm_header,
        "tactic_matrix_rows": tm_rows,
        "pursuit_sections": pursuit_sections(),
        "equipment": equipment_tables(),
        "infrastructure": infra,
        "wonders": wonders,
        "factions": faction_rows(),
        "settlements": settlement_rows(),
        "eras": era_rows(),
        "domain_board": domain_board_rows(),
        "tactics_matrix": {a: {b: rd.TACTIC_MATRIX.get((a, b), "") for b in rd.TACTICS}
                          for a in rd.TACTICS},
        "tactics": list(rd.TACTICS),
    }

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "compendium_data.json"
    json.dump(build_payload(), open(out, "w"), indent=1, default=str)
    p = build_payload()
    print(f"payload -> {out}")
    print(f"  pursuits: {sum(len(s['rows']) for s in p['pursuit_sections'])} across {len(p['pursuit_sections'])} sections")
    print(f"  factions {len(p['factions'])} | infra {len(p['infrastructure'])} | wonders {len(p['wonders'])}")
    print(f"  settlements {len(p['settlements'])} | eras {len(p['eras'])} | glossary {len(p['glossary'])}")
