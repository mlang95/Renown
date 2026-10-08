"""gen_layout_roots.py — SIMPLE: one chart per root Holding (no chain parent) with everything built from it.
Exceptions: the Manor House chart (with its Natural families) is taken whole from gen_layout's Monument
charts, and ROOT_ATTACH Holdings are moved onto the named root's chart as a side track."""
import json, os, sys, tempfile
import gen_layout as g
N, rd = g.N, g.rd
ROOT_ATTACH = {"Mine": ["Court Armoury"]}        # root -> Holdings shown only on that root's chart
KEEP = ["Manor House"]                            # Monument charts kept as-is from gen_layout

kids = {n: [k for k in N if n in g.reqs(k)] for n in N}
def desc(r):
    s, st = {r}, [r]
    while st:
        for k in kids[st.pop()]:
            if k not in s: s.add(k); st.append(k)
    return s

def center_rows(pos, edges, zag=()):
    """Reorder whole rows (each row's Holdings stay together, columns unchanged) to shorten vertical links:
    side tracks move above or below the main track instead of all dropping below it. Exhaustive up to 9 rows,
    else local search; cost = zag steps not on adjacent rows, then total row distance over links, then fewest rows moved, then least movement."""
    rows = sorted({r for _, r in pos.values()})
    if len(rows) < 3: return pos
    E = [(pos[a][1], pos[b][1]) for a, b in edges if a in pos and b in pos and pos[a][1] != pos[b][1]]
    Z = [(pos[a][1], pos[b][1]) for a, b in zag if a in pos and b in pos]
    def cost(order):
        at = {r: i for i, r in enumerate(order)}
        return (sum(abs(at[a] - at[b]) != 1 for a, b in Z),
                sum(abs(at[a] - at[b]) for a, b in E),
                sum(at[r] - at[rows[0]] != r - rows[0] for r in rows),
                sum(abs((at[r] - at[rows[0]]) - (r - rows[0])) for r in rows))
    if len(rows) <= 9:                            # small enough to try every order
        from itertools import permutations
        best = list(min(permutations(rows), key=cost))
    else:                                         # best single-row move until nothing improves
        best, bc = list(rows), cost(rows)
        while True:
            cands = [rest[:i] + [r] + rest[i:] for r in best for rest in [[x for x in best if x != r]]
                     for i in range(len(rest) + 1)]
            nb = min(cands, key=cost)
            if cost(nb) >= bc: break
            best, bc = nb, cost(nb)
    at = {r: i for i, r in enumerate(best)}
    return {n: [c, at[r]] for n, (c, r) in pos.items()}


tmp = os.path.join(tempfile.gettempdir(), "_layout_mon.json")
g.main_simple(tmp)
mon = json.load(open(tmp, encoding="utf-8"))
kept = [c for c in mon if c["anchor"] in KEEP or (isinstance(c["anchor"], list) and set(c["anchor"]) & set(KEEP))]
def natural(n): return "natural" in str(N[n].get("innate", "")).lower()
for c in kept:   # Natural-only: keep the Natural Holdings that reach the Monument through Natural Holdings alone
    ms = c["anchor"] if isinstance(c["anchor"], list) else [c["anchor"]]
    links = [l for l in c.get("links", []) if l[0] in c["nodes"]]
    ok = {n for n in c["nodes"] if natural(n)} | set(ms)
    up = {n: [q for q in g.reqs(n) if q in ok] + [a for a, b in links if b == n and a in ok] for n in ok}
    keep, st = set(ms), list(ms)
    while st:
        for q in up[st.pop()]:
            if q not in keep: keep.add(q); st.append(q)
    links = [l for l in links if l[0] in keep and l[1] in keep]
    pos, edges = g.track_layout(keep, ms, links)
    print(f"{c['title']}: Natural only, dropped {sorted(set(c['nodes']) - keep)}")
    pos = center_rows(pos, edges + links)
    c["nodes"], c["edges"], c["links"] = pos, edges + links, links
claimed = set().union(*[set(c["nodes"]) for c in kept]) if kept else set()
# a Holding leaves the root charts if every Holding it leads to is also on a kept chart
own = {n for n in claimed if desc(n) <= claimed}
moved = {x for xs in ROOT_ATTACH.values() for x in xs}

def zag_pairs(nodes):
    """(B, X) where X can be built from B or from B's own parent A: X sits in B's column on the next row,
    B steps straight into it, and X's line is one column shorter. Skipped inside cycles, and when B feeds
    nothing else on the chart (B would have no row of its own)."""
    par = {n: [q for q in g.reqs(n) if q in nodes] for n in nodes}
    ch = {n: [k for k in nodes if n in par[k]] for n in nodes}
    def up(n, s=None):
        s = set() if s is None else s
        for q in par[n]:
            if q not in s: s.add(q); up(q, s)
        return s
    out = []
    for x in sorted(nodes):
        bs = [b for b in par[x] if any(a in par[b] for a in par[x] if a != b)
              and x not in up(b) and [k for k in ch[b] if k != x]]
        if bs: out.append((max(bs, key=lambda b: (len(up(b)), b)), x))
    return out

def zag_ok(pos, zag):
    return [z for z in zag if pos[z[0]][0] != pos[z[1]][0] or abs(pos[z[0]][1] - pos[z[1]][1]) != 1]

def layout_root(nodes, sinks, side=()):
    """track_layout with zag steps (+ ROOT_ATTACH side tracks), rows centred; a zag that can't end up one
    row from its parent in the same column is dropped and the chart laid out again."""
    zag = zag_pairs(nodes)
    while True:
        pos, edges = g.track_layout(nodes, sinks, zag=set(zag))
        if side:
            pos, edges = g.attach_layout(pos, set(pos) | g.ancestry(side), side)
        pos = center_rows(pos, edges, zag)
        bad = zag_ok(pos, zag)
        if not bad: return pos, edges, zag
        print("  zag dropped:", bad)
        zag = [z for z in zag if z not in bad]

roots = [n for n in N if not g.reqs(n) and n not in own]
charts = []
for r in sorted(roots, key=lambda r: (-len(desc(r)), r)):
    nodes = desc(r) - own - moved
    sinks = sorted(x for x in nodes if not [k for k in kids[x] if k in nodes])
    side = [x for x in ROOT_ATTACH.get(r, []) if x in N]
    nodes |= {x for x in side if x in desc(r)}           # already built from this root: a normal part of the chart
    side = [x for x in side if x not in desc(r)]          # otherwise a side track with its own ancestry
    sinks = sorted(x for x in nodes if not [k for k in kids[x] if k in nodes])
    pos, edges, zag = layout_root(nodes, sinks, side)
    charts.append({"title": rd.display(r) if hasattr(rd, "display") else r, "anchor": r, "mode": "root",
                   "nodes": pos, "edges": edges})
    print(f"{r}: {len(pos)} holdings" + (f" (+ side track {side})" if side else "") + (f", zag {zag}" if zag else ""))
for c in kept:
    charts.append(c); print(f"{c['title']}: {len(c['nodes'])} holdings (kept from Monument charts)")
print("left the root charts:", sorted(own))
out = sys.argv[1] if len(sys.argv) > 1 else "layout_roots.json"
json.dump(charts, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1); print("wrote", out)