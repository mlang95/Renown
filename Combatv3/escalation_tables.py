#!/usr/bin/env python3
"""escalation_tables.py — generate the Escalation Campaign's data tables from
renown_data (single source of truth). Each function returns a Markdown table so
the authored ESCALATION_CAMPAIGN.md can stay prose-first with {{TABLE:x}} markers
filled by build_escalation.py. Keeps the doc from drifting (e.g. Deadly vs the
stale 'Shatter Armor', unified Endurance, Unbreakable Knight Templar)."""
import sys
sys.path.insert(0, ".")
import renown_data as rd

def _tags(lst): return ", ".join(lst) if lst else "—"

def retinues():
    rows = ["| Retinue | to Strike | Endurance | Morale | Notes | Unlock |",
            "|---|---|---|---|---|---|"]
    unlock = {"Levy":"—","Man-at-Arms":"Coliseum","Sergeant":"War College",
              "Knight Templar":"Preceptory"}
    for name, v in rd.RETINUES.items():
        note = "Unbreakable" if v.get("unbreakable") else "—"
        rows.append(f"| {name} | {v['to_hit']}+ | {v['endurance']} | {v['shaking']} | {note} | {unlock.get(name,'—')} |")
    return "\n".join(rows)

def _weapon_table(src):
    rows = ["| Weapon | AP | Init | Tags | Tier | Note |", "|---|---|---|---|---|---|"]
    for name, v in src.items():
        if name is None: continue
        note = v.get("note") or "—"  # note now lives in renown_data
        rows.append(f"| {name} | {v['ap']} | {v['init']:+d} | {_tags(v.get('tags'))} | {v.get('tier','—')} | {note} |")
    return "\n".join(rows)

def melee():  return _weapon_table(rd.WEAPONS)
def ranged(): return _weapon_table(rd.RANGED)

def shields():
    rows = ["| Shield | Save | Init | Tags | Tier |", "|---|---|---|---|---|"]
    for name, v in rd.SHIELDS.items():
        if name is None: continue
        rows.append(f"| {name} | +{v['save_bonus']} | {v['init']:+d} | {_tags(v.get('tags'))} | {v.get('tier','—')} |")
    return "\n".join(rows)

def armor():
    rows = ["| Armor | Save | Tags | Tier |", "|---|---|---|---|"]
    for name, v in rd.ARMORS.items():
        if name is None: continue
        rows.append(f"| {name} | {v['save']}+ | {_tags(v.get('tags'))} | {v.get('tier','—')} |")
    return "\n".join(rows)

def domain_board():
    rows = ["| Domain | Rising | Established | Sovereign |", "|---|---|---|---|"]
    for dom, cells in rd.DOMAIN_BOARD.items():
        rows.append(f"| **{dom}** | {cells.get('Rising','—')} | {cells.get('Established','—')} | {cells.get('Sovereign','—')} |")
    return "\n".join(rows)

TABLES = {"retinues":retinues, "melee":melee, "ranged":ranged,
          "shields":shields, "armor":armor, "domain_board":domain_board}

if __name__ == "__main__":
    for name, fn in TABLES.items():
        print(f"\n### {name}\n{fn()}")
