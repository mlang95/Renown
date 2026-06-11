#!/usr/bin/env python3
"""Render the Escalation talent trees from nodes_escalation.csv to a
one-page landscape PDF (+ PNG). Reads one-row-per-rank; collapses ranks
into a single node; enablers (blank Effect) would render grey but the
combat-only CSV has none."""
import csv, subprocess, sys
from collections import OrderedDict

CSV = sys.argv[1] if len(sys.argv) > 1 else "nodes_escalation.csv"
OUT = sys.argv[2] if len(sys.argv) > 2 else "talent_tree"

DOMAIN = {  # fill / border
    "Industry": ("#1F4E8C", "#1F4E8C"),
    "Prowess":  ("#9E1B1B", "#9E1B1B"),
    "Piety":    ("#B8941F", "#9E7A00"),
    "Cunning":  ("#1A1A1A", "#1A1A1A"),
}
MON = ("#5B2A86", "#5B2A86")
TIERS = ["Untested", "Rising", "Established", "Sovereign"]

def nid(name):
    return "n_" + "".join(c if c.isalnum() else "_" for c in name)

# ---- load + collapse ranks ----
nodes = OrderedDict()
for r in csv.DictReader(open(CSV, encoding="utf-8-sig")):
    name = r["Name"].strip()
    n = nodes.setdefault(name, {"domain": r["Domain"].strip(), "standing": r["Standing"].strip(),
                                "ranks": {}, "all": "", "any": "", "extra": "",
                                "mon": r.get("Monument", "no").strip().lower() == "yes"})
    rk = int(r["Rank"] or 1)
    n["ranks"][rk] = r["Effect"].strip()
    if rk == 1:
        n["all"] = r["Requires_All"].strip()
        n["any"] = r["Requires_Any"].strip()
        n["extra"] = r["Extra_Req"].strip()

# ---- emit dot ----
L = ['digraph T {', 'rankdir=TB; bgcolor=white;',
     'graph [fontname="Helvetica", nodesep=0.30, ranksep=0.60, splines=true, size="10.3,7.2"];',
     'node [shape=box, style="rounded,filled", fontname="Helvetica-Bold", fontsize=10, penwidth=0, margin="0.11,0.06", fontcolor=white];',
     'edge [color="#9a9a9a", arrowsize=0.6, penwidth=1.1];']
# tier rail
L += ['node [shape=plaintext, style="", fontcolor="#555555", fontsize=12];']
L += [f'{t[0].upper()}_rail[label="{t.upper()}"];' for t in TIERS]
L.append(" -> ".join(f'{t[0].upper()}_rail' for t in TIERS) + " [style=invis];")

for name, n in nodes.items():
    fill, border = MON if n["mon"] else DOMAIN[n["domain"]]
    fc = "white"
    maxr = max(n["ranks"])
    if n["mon"]:
        head = name.upper() + " " + ("\u25c6" * maxr)
    else:
        head = name
    if len(n["ranks"]) > 1:
        body = "\\n".join(f"{k}: {n['ranks'][k]}" for k in sorted(n["ranks"]))
    else:
        body = n["ranks"][1]
    extra = f"\\n(+ {n['extra']})" if n["extra"] else ""
    blank = (not body)  # enabler
    if blank:
        fill, border, fc = "#ECECEC", "#999999", "#555555"
        body = "(no battle effect)"
        style = 'style="rounded,filled,dashed", penwidth=1'
    else:
        style = 'style="rounded,filled", penwidth=0'
    L.append(f'{nid(name)}[label="{head}\\n{body}{extra}", shape=box, {style}, '
             f'fillcolor="{fill}", color="{border}", fontcolor="{fc}"];')

# edges
for name, n in nodes.items():
    for pre in [p.strip() for p in n["all"].split(",") if p.strip()]:
        if pre in nodes:
            L.append(f'{nid(pre)} -> {nid(name)};')
    anys = [p.strip() for p in n["any"].split(",") if p.strip()]
    for i, pre in enumerate(anys):
        if pre in nodes:
            lbl = ' label="or", fontsize=8, fontcolor="#999999"' if i else ""
            L.append(f'{nid(pre)} -> {nid(name)} [style=dashed{lbl}];')

# tier ranks
for t in TIERS:
    same = [f'{t[0].upper()}_rail'] + [nid(nm) for nm, n in nodes.items() if n["standing"] == t]
    L.append("{ rank=same; " + "; ".join(same) + "; }")
L.append("}")

open(f"{OUT}.dot", "w").write("\n".join(L))
subprocess.run(["dot", "-Tpdf", f"{OUT}.dot", "-o", f"{OUT}.pdf"], check=True)
subprocess.run(["dot", "-Tpng", "-Gdpi=130", f"{OUT}.dot", "-o", f"{OUT}.png"], check=True)
print(f"rendered {OUT}.pdf / .png from {len(nodes)} nodes")
