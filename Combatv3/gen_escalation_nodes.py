#!/usr/bin/env python3
"""gen_escalation_nodes.py — regenerate nodes_escalation.csv from renown_data.NODES
(the escalation node graph), so render_trees.py always draws current data.

Usage:  python gen_escalation_nodes.py [nodes_escalation.csv]
"""
import csv, sys
sys.path.insert(0, ".")
import renown_data as rd

OUT = sys.argv[1] if len(sys.argv) > 1 else "nodes_escalation.csv"
TIER_ORDER = {"Untested": 0, "Rising": 1, "Established": 2, "Sovereign": 3}

rows = []
for name, nd in rd.NODES.items():
    e = nd.get("escalation")
    if not e:
        continue
    standing = (e.get("standing") or "").strip()          # e.g. "Sovereign Industry"
    parts = standing.split()
    tier = parts[0] if parts else ""                       # "Sovereign"
    domain = parts[1] if len(parts) > 1 else ""            # "Industry"
    ranks = e.get("ranks") or {1: ""}
    is_mon = "yes" if nd.get("monument") else "no"
    all_req = ", ".join(e.get("requires_all") or [])
    any_req = ", ".join(e.get("requires_any") or [])
    extra = e.get("extra_req") or ""
    # one row per rank (render_trees collapses them)
    for rk in sorted(ranks):
        rows.append([name, domain, tier, rk, str(ranks[rk]).strip(),
                     all_req if rk == 1 else "",
                     any_req if rk == 1 else "",
                     extra if rk == 1 else "",
                     is_mon])

# stable order: by tier then name, so the dot layout is deterministic
rows.sort(key=lambda r: (TIER_ORDER.get(r[2], 9), r[0], r[3]))

with open(OUT, "w", newline="", encoding="utf-8") as f:
    cw = csv.writer(f)
    cw.writerow(["Name","Domain","Standing","Rank","Effect",
                 "Requires_All","Requires_Any","Extra_Req","Monument"])
    cw.writerows(rows)
print(f"wrote {len(rows)} rows ({len(set(r[0] for r in rows))} nodes) -> {OUT}")
