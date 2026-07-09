#!/usr/bin/env python
# patch_pursuit_domains.py
# Injects a "Domain" column (the unlock gate, e.g. "Established Industry") into
# every pursuit row of compendium_data.json, matched by pursuit name against
# renown_data.NODES. Idempotent: re-running won't duplicate the column.
#
#   python patch_pursuit_domains.py compendium_data.json
#
# After running, use the updated build_compendium.js (header includes "Domain").
import sys, json, re
import renown_data as rd

GATE = {}
for name, d in rd.NODES.items():
    u = (d.get("unlock") or "").strip()
    GATE[name] = "" if u in ("", "-", "\u2014") else u

def norm(s):
    return re.sub(r"\s+", " ", re.sub(r"\*\*", "", str(s or ""))).strip().lower()

GATE_NORM = {norm(k): v for k, v in GATE.items()}

def build(path):
    data = json.load(open(path, encoding="utf-8"))
    secs = data.get("pursuit_sections", [])
    patched = 0; missed = []
    for sec in secs:
        newrows = []
        for row in sec["rows"]:
            # detect if already patched (5 cols with a gate-looking 2nd col)
            name = row[0]
            gate = GATE_NORM.get(norm(name), None)
            if gate is None:
                missed.append(name); gate = ""
            else:
                patched += 1
            # insert Domain right after the pursuit name
            if len(row) >= 4 and _looks_patched(row):
                row[1] = gate; newrows.append(row)
            else:
                newrows.append([row[0], gate] + list(row[1:]))
        sec["rows"] = newrows
    json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"patched {patched} pursuit rows with Domain gate")
    if missed:
        print("unmatched names (left blank):", missed)

def _looks_patched(row):
    # heuristic: 5+ columns and col1 is a gate phrase or empty
    if len(row) < 5:
        return False
    c1 = str(row[1] or "")
    return c1 == "" or any(t in c1 for t in ("Rising", "Established", "Sovereign"))

if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "compendium_data.json")
