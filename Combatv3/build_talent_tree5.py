#!/usr/bin/env python
# build_talent_tree.py - pursuit tech tree as a series of SEPARATE flowcharts.
# One chart per goal (monument) or theme. Charts never share edges - shared
# prerequisites are simply repeated inside each chart so every chart reads
# standalone, top of page to bottom, like a page of skill trees.
# Edges are rounded ELBOWS (flowchart style), short and followable.
# Usage: python build_talent_tree.py [out.svg]
import sys, collections
import renown_data as rd

NODES = rd.NODES
CH = {n: [b for b in (d.get("builds_into") or []) if b in NODES] for n, d in NODES.items()}
PA = collections.defaultdict(list)
for n, ch in CH.items():
    for c in ch: PA[c].append(n)

# remove unwanted implied edge
if "Quarry" in CH.get("Peat Bog", []): CH["Peat Bog"].remove("Quarry")
if "Peat Bog" in PA.get("Quarry", []): PA["Quarry"].remove("Peat Bog")
# Designer-directed edges not yet in renown_data (visual spec from playtest prep)
for _a, _b in [("Black Market", "Thieves' Guild"), ("Merchant Quarter", "Inn")]:
    if _b not in CH[_a]:
        CH[_a].append(_b); PA[_b].append(_a)

# Chart membership derives from the pure builds_into graph (snapshot now).
import copy as _copy
_PA0 = {k: list(v) for k, v in PA.items()}
def _anc0(n):
    out = set(); q = [n]
    while q:
        x = q.pop()
        for p in _PA0.get(x, []):
            if p not in out: out.add(p); q.append(p)
    return out

# Root nodes (no builds_into parents) that carry a mastery_req are chained by it,
# so they sit AFTER their requirements instead of in the first column.
# Cycle guard: skip reqs that are the node's own descendants.
def _descendants(n):
    out = set(); q = [n]
    while q:
        x = q.pop()
        for c in CH.get(x, []):
            if c not in out: out.add(c); q.append(c)
    return out
def _parse_req(r):
    if not r or str(r).strip() in ("", "-", "\u2014"): return []
    t = str(r).replace(" or ", "+")
    return [p.strip() for p in t.split("+") if p.strip() in NODES]
for _n, _d in list(NODES.items()):
    _reqs = _parse_req(_d.get("mastery_req"))
    if not _reqs: continue
    _desc = _descendants(_n)
    for _src in _reqs:
        if _src in _desc: continue          # would cycle; builds_into already orders these
        if _n in CH[_src]: continue         # already an edge
        CH[_src].append(_n)
        PA[_n].append(_src)

DOM = ["Industry", "Prowess", "Cunning", "Piety"]
DOMC = {"Common": "#6a6a72", "Industry": "#2E5A8C", "Prowess": "#9E2B25",
        "Cunning": "#1c1c20", "Piety": "#C6A024"}
GOLD = "#8a6d1a"
def domain_of(n):
    u = NODES[n].get("unlock") or ""
    for x in DOM:
        if x in u: return x
    return "Common"

def ancestors(n):
    return _anc0(n)

# ---------- chart definitions ----------
def _union(*mons):
    s = set()
    for m in mons: s |= ancestors(m) | {m}
    return sorted(s)

SECTIONS = None  # filled after ancestors() defined

SECTIONS = [
    ("ECONOMY", [
        ("Husbandry & Provisions", ["Common Land","Orchard","Vineyard","Meadery","Cidery","Winery",
                                     "Bakery","Butchery","Smokehouse","Fishmongery","Mill","Burgages",
                                     "Market Square","Manor House"], "Manor House"),
        ("Trade & Works", ["Fishmongery","Salt Works","Harbor","Shipyard","Carpentry","Storehouse",
                            "College of Engineering","Trade Guild","Masonry","Academy","Workyard",
                            "Common Land","Census Hall","Market Square","Burgages","Supply Depot",
                            "Granary","Smokehouse"], None),
        ("Advanced Blast Furnace \u00d7 Royal Pavilion",
         _union("Advanced Blast Furnace","Royal Pavilion") + ["Kiln","Charcoal Burner",
          "Jewelry Foundry","Merchant Quarter","Weavery","Artisan Workshop","Saddlery","Joinery"],
         ["Advanced Blast Furnace","Royal Pavilion"]),
    ]),
    ("RULE & COURT", [
        ("Aristocratic Court \u00d7 Thieves' Guild \u00d7 Shadow Work",
         _union("Aristocratic Court","Thieves' Guild") + ["Black Market","Toxicarium",
          "Forgotten Catacombs","Courier Network","Cipher Chamber","Outrider Intercept Post",
          "University","Toll House","Beacon Towers","Spice Merchant","Herb Garden"],
         ["Aristocratic Court","Thieves' Guild","Outrider Intercept Post"]),
        ("Senate Hall", None, "Senate Hall"),
        ("Imperial Palace", None, "Imperial Palace"),
    ]),
    ("WAR & LEARNING", [
        ("Ministry of Military Strategy \u00d7 Studium Generale",
         _union("Ministry of Military Strategy","Studium Generale") + ["Siege Works","Siege Camp"],
         ["Ministry of Military Strategy","Studium Generale"]),
    ]),
    ("FAITH & SHADOW", [
        ("Preceptory \u00d7 Inquisitorial Palace", _union("Preceptory of the Knight's Templar","Inquisitorial Palace"),
         ["Preceptory of the Knight's Templar","Inquisitorial Palace"]),
    ]),
]

TIER_RANK = {"": 0, "Rising": 1, "Established": 2, "Sovereign": 3}
def tier_rank(n):
    u = NODES[n].get("unlock") or ""
    for t in ("Sovereign", "Established", "Rising"):
        if t in u: return TIER_RANK[t]
    return 0

NW, NH = 118, 24
COLGAP, ROWGAP = 54, 12
CHART_GAP_X, CHART_GAP_Y = 70, 56
PAGE_W = 1560

def chart_layout(members, anchor):
    anchors = anchor if isinstance(anchor, (list, tuple)) else ([anchor] if anchor else [])
    mem = set(members)
    ch = {n: [c for c in CH[n] if c in mem] for n in mem}
    pa = {n: [p for p in PA[n] if p in mem] for n in mem}
    depth = {}
    def dep(n, stack=()):
        if n in depth: return depth[n]
        if n in stack: return 0
        d = 0
        for p in pa[n]: d = max(d, dep(p, stack + (n,)) + 1)
        depth[n] = d; return d
    for n in mem: dep(n)
    if "Caravanery" in mem and "Merchant Quarter" in mem and "Inn" in mem:
        depth["Caravanery"] = depth["Merchant Quarter"]
        if depth["Inn"] <= depth["Caravanery"]:
            depth["Inn"] = depth["Caravanery"] + 1
    if "Siege Works" in mem and "Coliseum" in mem and not [p for p in pa["Siege Works"] if p in mem]:
        depth["Siege Works"] = depth["Coliseum"]
        if "Siege Camp" in mem: depth["Siege Camp"] = depth["Coliseum"] + 1
    ncols = max(depth.values()) + 1

    # lane score = mean index of anchors fed; none-feeders tuck behind nearest lane
    band = {n: 0.0 for n in mem}
    if len(anchors) >= 2:
        ansets = [((ancestors(a) & mem) | {a}) for a in anchors]
        mid = (len(anchors) - 1) / 2.0
        pend = []
        for n in mem:
            f = [i for i, As in enumerate(ansets) if n in As]
            band[n] = sum(f) / len(f) if f else None
            if band[n] is None: pend.append(n)
        for _ in range(4):
            for n in pend:
                pb = [band[p] for p in pa[n] if band.get(p) is not None]
                if pb: band[n] = sum(pb) / len(pb)
        import math as _m
        feeders = set().union(*ansets) if ansets else set()
        for n in mem:
            if band[n] is None: band[n] = mid
            band[n] = (round(band[n] * 2) / 2.0) if n in feeders else float(_m.floor(band[n] + 0.5))
        # a capstone alone in its lane joins its deepest parent's lane and
        # continues that ribbon instead of dangling past the boundary
        for a in anchors:
            if a in band and sum(1 for n in mem if band[n] == band[a]) == 1:
                ps = [p for p in pa[a] if p in band]
                if ps:
                    band[a] = band[max(ps, key=lambda p: depth[p])]

    # ---- GLOBAL chain decomposition: a chain keeps its row across lanes ----
    pitch = NH + ROWGAP
    visited = set()
    def chain_len(n, seen=()):
        best = 0
        for c in ch[n]:
            if c not in visited and c not in seen:
                best = max(best, chain_len(c, seen + (n,)))
        return best + 1
    chains = []
    while len(visited) < len(mem):
        starts = [n for n in mem - visited
                  if not any(p not in visited for p in pa[n])]
        if not starts: starts = sorted(mem - visited)
        s0 = max(starts, key=lambda n: (chain_len(n), -depth[n]))
        chain = [s0]; visited.add(s0)
        cur = s0
        while True:
            nxt = [c for c in ch[cur] if c not in visited]
            if not nxt: break
            cur = max(nxt, key=chain_len)
            chain.append(cur); visited.add(cur)
        chains.append(chain)
    # a chain's group = band of its tail (which monument it drives toward)
    def cband(chain): return band[chain[-1]] if band else 0.0
    groups = sorted({cband(c) for c in chains})
    chains.sort(key=lambda c: (cband(c), depth[c[0]], c[0]))
    pos = {}
    rowy = 0
    prev_g = None
    for g in groups:
        gchains = [c for c in chains if cband(c) == g]
        lane_rows = []      # (colset, rowy) first-fit within group
        for chain in gchains:
            colset = {depth[n] for n in chain}
            placed = None
            for i, (cs, ry) in enumerate(lane_rows):
                if not (cs & colset):
                    placed = i; break
            if prev_g is not None and not lane_rows:
                rowy += 14   # single breath between monument groups
            if placed is None:
                lane_rows.append((set(colset), rowy)); ry = rowy; rowy += pitch
            else:
                cs, ry = lane_rows[placed]
                lane_rows[placed] = (cs | colset, ry)
            for n in chain:
                pos[n] = (depth[n] * (NW + COLGAP), ry)
        prev_g = g

    # singleton chains snap adjacent to their deepest in-chart parent
    occ = {}
    for n,(x,y) in pos.items(): occ.setdefault(round(y),set()).add(x)
    for chain in chains:
        if len(chain) != 1: continue
        n = chain[0]
        ps = [p for p in pa[n] if p in pos]
        if not ps: continue
        px, py = pos[max(ps, key=lambda p: depth[p])]
        x = depth[n] * (NW + COLGAP)
        oldy = round(pos[n][1])
        for cand in (py + pitch, py - pitch, py):
            cy = round(cand)
            if cy < 0: continue
            if x not in occ.get(cy, set()):
                occ[oldy].discard(x)
                pos[n] = (x, cy); occ.setdefault(cy,set()).add(x)
                break

    # final row normalization: uniform pitch, no holes, no off-grid overlaps
    occ2 = sorted({round(y) for _, y in pos.values()})
    remap2 = {yv: i * pitch for i, yv in enumerate(occ2)}
    pos = {n: (x, remap2[round(y)]) for n, (x, y) in pos.items()}

    # collision fix: same (col,row) can only happen across lanes (never within);
    # nudge any duplicate down within its lane block
    seen = {}
    for n in sorted(pos, key=lambda n: (pos[n][1], pos[n][0])):
        x, y = pos[n]
        while (x, y) in seen:
            y += pitch
        pos[n] = (x, y); seen[(x, y)] = n
    w = ncols * NW + (ncols - 1) * COLGAP

    h = max(y for _, y in pos.values()) + pitch
    return pos, ch, w, h

def _esc(t): return str(t).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

def elbow(x1, y1, x2, y2):
    """Rounded elbow: out horizontally, turn once, into the child."""
    if abs(y1 - y2) < 2:
        return f'M{x1:.0f},{y1:.0f} L{x2-7:.0f},{y2:.0f}'
    midx = x1 + (x2 - x1) * 0.45
    r = min(9, abs(y2 - y1) / 2)
    sgn = 1 if y2 > y1 else -1
    return (f'M{x1:.0f},{y1:.0f} L{midx-r:.0f},{y1:.0f} '
            f'Q{midx:.0f},{y1:.0f} {midx:.0f},{y1+sgn*r:.0f} '
            f'L{midx:.0f},{y2-sgn*r:.0f} '
            f'Q{midx:.0f},{y2:.0f} {midx+r:.0f},{y2:.0f} '
            f'L{x2-7:.0f},{y2:.0f}')

def render_chart(svg, ox, oy, title, members, anchor, accent):
    anchors = anchor if isinstance(anchor, (list, tuple)) else ([anchor] if anchor else [])
    pos, ch, w, h = chart_layout(members, anchor)
    svg.append(f'<text x="{ox}" y="{oy-8}" font-size="12.5" font-weight="bold" fill="{accent}">{_esc(title)}</text>')
    svg.append(f'<line x1="{ox}" y1="{oy-2}" x2="{ox+w}" y2="{oy-2}" stroke="{accent}" stroke-width="1" opacity="0.5"/>')
    for n in members:
        ax, ay = pos[n]
        kids = [c for c in ch[n] if c in pos]
        if not kids: continue
        x1, y1 = ox + ax + NW, oy + ay + NH/2
        if len(kids) == 1:
            bx, by = pos[kids[0]]
            svg.append(f'<path d="{elbow(x1, y1, ox+bx, oy+by+NH/2)}" fill="none" stroke="#8f8672" stroke-width="1.2" opacity="0.85" marker-end="url(#arw)"/>')
        else:
            fx = x1 + COLGAP * 0.45
            cys = [oy + pos[c][1] + NH/2 for c in kids]
            lo, hi = min(cys + [y1]), max(cys + [y1])
            svg.append(f'<path d="M{x1:.0f},{y1:.0f} L{fx:.0f},{y1:.0f}" fill="none" stroke="#8f8672" stroke-width="1.4" opacity="0.85"/>')
            if hi - lo > 1:
                svg.append(f'<path d="M{fx:.0f},{lo:.0f} L{fx:.0f},{hi:.0f}" fill="none" stroke="#8f8672" stroke-width="1.4" opacity="0.85"/>')
            for c, cy in zip(kids, cys):
                bx = ox + pos[c][0]
                svg.append(f'<path d="M{fx:.0f},{cy:.0f} L{bx-6:.0f},{cy:.0f}" fill="none" stroke="#8f8672" stroke-width="1.2" opacity="0.85" marker-end="url(#arw)"/>')
    for n in members:
        x, y = pos[n]; col = DOMC[domain_of(n)]
        mon = NODES[n].get("monument")
        fill = "#fdf3d0" if mon else "#ffffff"
        sw = 2.2 if mon else 1.4
        svg.append(f'<rect x="{ox+x:.0f}" y="{oy+y:.0f}" width="{NW}" height="{NH}" rx="4" fill="{fill}" stroke="{col}" stroke-width="{sw}"/>')
        svg.append(f'<rect x="{ox+x:.0f}" y="{oy+y:.0f}" width="4" height="{NH}" fill="{col}"/>')
        label = n if len(n) <= 21 else n[:20] + "\u2026"
        dia = " \u25c6" if mon else ""
        svg.append(f'<text x="{ox+x+8:.0f}" y="{oy+y+15.5:.0f}" font-size="8.2" fill="#2b2620">{_esc(label)}{dia}</text>')
    return w, h

def build(out):
    # measure charts
    measured = []
    for sec, charts in SECTIONS:
        row = []
        for title, mem, anchor in charts:
            if mem is None:
                members = sorted(ancestors(anchor) | {anchor})
            else:
                members = mem
            a0 = (anchor[0] if isinstance(anchor,(list,tuple)) else anchor)
            accent = DOMC[domain_of(a0)] if a0 else "#5f5647"
            _, _, w, h = chart_layout(members, anchor)
            row.append((title, members, anchor, accent, w, h))
        measured.append((sec, row))
    # flow ALL charts in one continuous grid (no section headers)
    allcharts = [c for _, charts in measured for c in charts]
    rows, cur, curw = [], [], 0
    for cdef in allcharts:
        if curw + cdef[4] > PAGE_W and cur:
            rows.append(cur); cur, curw = [], 0
        cur.append(cdef); curw += cdef[4] + CHART_GAP_X
    if cur: rows.append(cur)
    body = [(None, rows)]
    H = 96
    for r in rows: H += max(c[5] for c in r) + CHART_GAP_Y
    W = PAGE_W + 60
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{int(H)}" viewBox="0 0 {W} {int(H)}" font-family="Georgia, serif">']
    svg.append(f'<rect width="{W}" height="{int(H)}" fill="#f4efe4"/>')
    svg.append('<defs><marker id="arw" markerWidth="7" markerHeight="7" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#8f8672"/></marker></defs>')
    svg.append(f'<text x="30" y="40" font-size="24" font-weight="bold" fill="#2b2620">Pursuit Paths</text>')
    svg.append(f'<text x="30" y="60" font-size="12" fill="#6f6f77">each chart is one goal, complete and standalone \u00b7 read left \u2192 right \u00b7 \u25c6 gold = Monument \u00b7 shared prerequisites repeat across charts \u00b7 gates not shown</text>')
    oy = 96
    for sec, rows in body:
        for r in rows:
            ox = 30
            rh = max(c[5] for c in r)
            for title, members, anchor, accent, w, h in r:
                render_chart(svg, ox, oy + (rh - h)/2 + 14, title, members, anchor, accent)
                ox += w + CHART_GAP_X
            oy += rh + CHART_GAP_Y
    svg.append("</svg>")
    open(out, "w").write("\n".join(svg))
    print(f"tree -> {out}  ({W}x{int(H)})")

if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "pursuit_tree.svg")
