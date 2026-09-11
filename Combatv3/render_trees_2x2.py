#!/usr/bin/env python3
"""render_trees_2x2.py — render the Escalation talent tree as FOUR per-domain
subtrees (Industry / Prowess / Cunning / Piety), each its own Graphviz graph,
composited into a single 2x2 landscape page (PDF + PNG).

Each quadrant keeps its own Untested->Sovereign tier rail and prereq edges.

Usage:  python render_trees_2x2.py [nodes_escalation.csv] [out_basename]
Requires: graphviz (dot) + pypdf for the composite, or falls back to a
montage via reportlab if available.
"""
import csv, subprocess, sys, os
from collections import OrderedDict

CSV = sys.argv[1] if len(sys.argv) > 1 else "nodes_escalation.csv"
OUT = sys.argv[2] if len(sys.argv) > 2 else "talent_tree_2x2"

DOMAIN_COL = {
    "Industry": ("#1F4E8C", "#1F4E8C"),
    "Prowess":  ("#9E1B1B", "#9E1B1B"),
    "Piety":    ("#B8941F", "#9E7A00"),
    "Cunning":  ("#1A1A1A", "#1A1A1A"),
}
MON = ("#5B2A86", "#5B2A86")
TIERS = ["Untested", "Rising", "Established", "Sovereign"]
QUAD_ORDER = ["Industry", "Prowess", "Cunning", "Piety"]   # 2x2 reading order

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

def emit_domain_dot(domain):
    """Build a dot graph for one domain's subtree."""
    dnodes = {nm: n for nm, n in nodes.items() if n["domain"] == domain}
    fill0, _ = DOMAIN_COL[domain]
    L = ['digraph T {', 'rankdir=TB; bgcolor=white;',
         f'labelloc="t"; label=<<b>{domain.upper()}</b>>; fontname="Arial Bold"; fontsize=20; fontcolor="{fill0}";',
         'graph [fontname="Arial", nodesep=0.22, ranksep=0.28, splines=true];',
         'node [shape=box, style="rounded,filled", fontname="Arial Bold", fontsize=18, penwidth=0, margin="0.18,0.11", fontcolor=white];',
         'edge [color="#9a9a9a", arrowsize=0.6, penwidth=1.1];']
    # tier rail (left column of grey labels)
    L += ['node [shape=plaintext, style="", fontcolor="#777777", fontsize=15];']
    L += [f'{t[0].upper()}_rail[label="{t.upper()}"];' for t in TIERS]
    L.append(" -> ".join(f'{t[0].upper()}_rail' for t in TIERS) + " [style=invis];")
    # nodes
    for name, n in dnodes.items():
        fill, border = MON if n["mon"] else DOMAIN_COL[domain]
        fc = "white"
        maxr = max(n["ranks"])
        head = (name.upper() + " " + ("*" * maxr)) if n["mon"] else name
        if len(n["ranks"]) > 1:
            body = "\\n".join(f"{k}: {n['ranks'][k]}" for k in sorted(n["ranks"]))
        else:
            body = n["ranks"][1]
        extra = f"\\n(+ {n['extra']})" if n["extra"] else ""
        if not body:
            fill, border, fc = "#ECECEC", "#999999", "#555555"
            body = "(no battle effect)"
            style = 'style="rounded,filled,dashed", penwidth=1'
        else:
            style = 'style="rounded,filled", penwidth=0'
        L.append(f'{nid(name)}[label="{head}\\n{body}{extra}", shape=box, {style}, '
                 f'fillcolor="{fill}", color="{border}", fontcolor="{fc}"];')
    # edges (only within this domain; cross-domain prereqs drawn as a faint note-less edge if target in-domain)
    for name, n in dnodes.items():
        for pre in [p.strip() for p in n["all"].split(",") if p.strip()]:
            if pre in dnodes:
                L.append(f'{nid(pre)} -> {nid(name)};')
            # cross-domain prereqs are NOT drawn — only real in-domain talent nodes appear
        anys = [p.strip() for p in n["any"].split(",") if p.strip()]
        for i, pre in enumerate(anys):
            if pre in dnodes:
                lbl = ' label="or", fontsize=8, fontcolor="#999999"' if i else ""
                L.append(f'{nid(pre)} -> {nid(name)} [style=dashed{lbl}];')
    # tier ranks
    for t in TIERS:
        same = [f'{t[0].upper()}_rail'] + [nid(nm) for nm, n in dnodes.items() if n["standing"] == t]
        L.append("{ rank=same; " + "; ".join(same) + "; }")
    L.append("}")
    return "\n".join(L)

# render each domain to its own PNG
pngs = {}
for dom in QUAD_ORDER:
    dot = emit_domain_dot(dom)
    dfile = f"_tree_{dom}.dot"; pfile = f"_tree_{dom}.png"
    open(dfile, "w", encoding="utf-8").write(dot)
    subprocess.run(["dot", "-Tpng", "-Gdpi=150", dfile, "-o", pfile], check=True, stderr=subprocess.DEVNULL)
    # autocrop white margins so sparse trees don't carry empty tier space into the layout
    try:
        from PIL import Image, ImageChops
        im = Image.open(pfile).convert("RGB")
        bg = Image.new("RGB", im.size, (255, 255, 255))
        diff = ImageChops.difference(im, bg)
        bbox = diff.getbbox()
        if bbox:
            pad = 8
            l, t, r, b = bbox
            l = max(0, l - pad); t = max(0, t - pad)
            r = min(im.width, r + pad); bo = min(im.height, b + pad)
            im.crop((l, t, r, bo)).save(pfile)
    except Exception as _e:
        print("autocrop skipped (%s)" % _e)
    pngs[dom] = pfile

# composite onto one landscape page, PROPORTIONAL packing (not even quarters).
# Layout: two rows. Row 1 = the two widest trees (Industry, Prowess); Row 2 = the
# two compact trees (Cunning, Piety). Row heights and in-row widths scale to each
# tree's natural size so the page fills and every tree stays legible.
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

PAGE = landscape(letter)
PW, PH = PAGE
M = 0.28 * inch
GAP = 0.18 * inch
avail_w = PW - 2 * M
avail_h = PH - 2 * M

# measure each rendered png
dims = {}
for dom in QUAD_ORDER:
    iw, ih = ImageReader(pngs[dom]).getSize()
    dims[dom] = (iw, ih)

# LAYOUT: three rows. Industry (full width) | Prowess (full width) each get a big
# band so they're rendered wide and legible. Cunning + Piety share a thin bottom row.
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

PAGE = landscape(letter)
PW, PH = PAGE
M = 0.22 * inch
GAP = 0.14 * inch
avail_w = PW - 2 * M
avail_h = PH - 2 * M

dims = {d: ImageReader(pngs[d]).getSize() for d in QUAD_ORDER}
def asp(d): return dims[d][0] / dims[d][1]

# Row heights: Industry and Prowess each as tall as they get at FULL width; the
# bottom small-pair row takes whatever's left (thin).
ind_h = avail_w / asp("Industry")
pro_h = avail_w / asp("Prowess")
# small pair at the bottom, side by side, height from the taller small tree at half width
half = (avail_w - GAP) / 2
small_h = max(half / asp("Cunning"), half / asp("Piety"))

total_needed = ind_h + pro_h + small_h + 2 * GAP
if total_needed > avail_h:
    k = avail_h / total_needed          # shrink everything uniformly to fit page
    ind_h *= k; pro_h *= k; small_h *= k

def draw_full(c, d, y_bottom, h):
    w = asp(d) * h
    if w > avail_w:
        w = avail_w; h = avail_w / asp(d)
    x = M + (avail_w - w) / 2
    c.drawImage(ImageReader(pngs[d]), x, y_bottom, width=w, height=h,
                preserveAspectRatio=True, mask="auto")

def draw_small_pair(c, left, right, y_bottom, h):
    ws = [asp(left) * h, asp(right) * h]
    total = sum(ws) + GAP
    if total > avail_w:
        kk = (avail_w - GAP) / sum(ws); h *= kk; ws = [w * kk for w in ws]; total = sum(ws) + GAP
    x = M + (avail_w - total) / 2
    for d, w in zip((left, right), ws):
        c.drawImage(ImageReader(pngs[d]), x, y_bottom, width=w, height=h,
                    preserveAspectRatio=True, mask="auto")
        x += w + GAP

c = canvas.Canvas(f"{OUT}.pdf", pagesize=PAGE)
y = M + avail_h
draw_full(c, "Industry", y - ind_h, ind_h);            y -= ind_h + GAP
draw_full(c, "Prowess",  y - pro_h, pro_h);             y -= pro_h + GAP
draw_small_pair(c, "Cunning", "Piety", y - small_h, small_h)
c.showPage()
c.save()

# also a PNG of the composite (render the pdf page) if pdftoppm exists
try:
    subprocess.run(["pdftoppm", "-png", "-r", "150", "-singlefile", f"{OUT}.pdf", OUT],
                   check=True)
except Exception:
    pass

# cleanup intermediates
for dom in QUAD_ORDER:
    for ext in (".dot", ".png"):
        f = f"_tree_{dom}{ext}"
        if os.path.exists(f):
            os.remove(f)
print(f"rendered 2x2 -> {OUT}.pdf (+ .png) from {len(nodes)} nodes across {len(QUAD_ORDER)} domains")