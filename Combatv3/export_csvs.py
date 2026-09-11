#!/usr/bin/env python3
"""export_csvs.py — export renown_data.py to CSVs for spreadsheet VIEWING.

renown_data.py is THE master: edit it, never the CSVs. This script regenerates
the CSVs as read-only views (specs.csv, factions.csv, infrastructure.csv,
equipment.csv) so anything that wants a spreadsheet still gets one.

Usage:  python export_csvs.py [outdir]
"""
import csv, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import renown_data as rd

OUT = sys.argv[1] if len(sys.argv) > 1 else "."

def w(path, header, rows):
    with open(os.path.join(OUT, path), "w", newline="", encoding="utf-8-sig") as f:
        cw = csv.writer(f)
        cw.writerow(header)
        cw.writerows(rows)
    print(f"  wrote {path} ({len(rows)} rows)")

# specs.csv — the node graph (rules-text view)
w("specs.csv",
  ["Pursuits", "Type", "Unlock Requirement", "Mastery Requirement",
   "Innate Effects", "Mastery Effect", "Builds Into"],
  [[n, v.get("type",""), v.get("unlock",""), v.get("mastery_req",""),
    v.get("innate",""), v.get("mastery",""), ", ".join(v.get("builds_into", []))]
   for n, v in rd.NODES.items()])

# factions.csv
w("factions.csv",
  ["Inspiration", "AI Name", "Feel", "Difficulty", "Strength", "Mechanic", "Pair", "Complement"],
  [[f.get("inspiration",""), n, f.get("feel",""), f.get("difficulty",""),
    f.get("strength",""), f.get("mechanic",""), f.get("pair",""), f.get("complement","")]
   for n, f in rd.FACTIONS.items()])

# infrastructure.csv
w("infrastructure.csv",
  ["Name", "Category", "Upkeep", "Upkeep Frequency", "Empire Bonus", "Tier", "Build Time", "Requirement"],
  [[n, "Infrastructure", e["upkeep"], e["upkeep_frequency"], e["empire_bonus"],
    e["tier"], e["build_time"], e["requirement"]] for n, e in rd.INFRASTRUCTURE.items()] +
  [[n, "Wonder", e["upkeep"], e["upkeep_frequency"], e["empire_bonus"],
    e["tier"], e["build_time"], e["requirement"]] for n, e in rd.WONDERS.items()])

# equipment.csv
eq_rows = []
for n, x in rd.WEAPONS.items():
    eq_rows.append([n, "Weapon", x["tier"], x["ap"], x["init"], "", ", ".join(x["tags"]) or "None",
                    "", "", "", "", rd.TIER_UNLOCK.get(x["tier"]) or "None", ""])
for n, x in rd.RANGED.items():
    eq_rows.append([n, "Ranged", x["tier"], x["ap"], x["init"], "", ", ".join(x["tags"]) or "None",
                    "", "", "", "", rd.TIER_UNLOCK.get(x["tier"]) or "None", ""])
for n, x in rd.SHIELDS.items():
    if n is None: continue
    eq_rows.append([n, "Shield", x["tier"], "", x["init"], f"+{x['save_bonus']}",
                    ", ".join(x["tags"]) or "None", "", "", "", "",
                    rd.TIER_UNLOCK.get(x["tier"]) or "None", ""])
for n, x in rd.ARMORS.items():
    eq_rows.append([n, "Armor", x["tier"], "", "", f"{x['save']}+", ", ".join(x["tags"]) or "None",
                    "", "", "", "", rd.TIER_UNLOCK.get(x["tier"]) or "None", ""])
_runlock = {"Levy": "None", "Man-at-Arms": "Coliseum", "Sergeant": "War College",
            "Knight Templar": "Preceptory"}
for n, x in rd.RETINUES.items():
    eq_rows.append([n, "Retinue", "", "", "", "", "Unbreakable" if x.get("unbreakable") else "None",
                    x["cost"], f"{x['to_hit']}+", x["endurance"], f"{x['shaking']}+",
                    _runlock.get(n, "None"), ""])
w("equipment.csv",
  ["Name", "Category", "Tier", "AP", "Initiative", "Save", "Effects", "Cost",
   "To Hit", "Endurance", "Shaking", "Specialization Unlock", "Note"], eq_rows)

print("\nAll CSVs exported as read-only views of renown_data.py")
