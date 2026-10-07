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

tmp = os.path.join(tempfile.gettempdir(), "_layout_mon.json")
g.main_simple(tmp)
mon = json.load(open(tmp, encoding="utf-8"))
kept = [c for c in mon if c["anchor"] in KEEP or (isinstance(c["anchor"], list) and set(c["anchor"]) & set(KEEP))]
claimed = set().union(*[set(c["nodes"]) for c in kept]) if kept else set()
# a Holding leaves the root charts if every Holding it leads to is also on a kept chart
own = {n for n in claimed if desc(n) <= claimed}
moved = {x for xs in ROOT_ATTACH.values() for x in xs}

roots = [n for n in N if not g.reqs(n) and n not in own]
charts = []
for r in sorted(roots, key=lambda r: (-len(desc(r)), r)):
    nodes = desc(r) - own - moved
    sinks = sorted(x for x in nodes if not [k for k in kids[x] if k in nodes])
    pos, edges = g.track_layout(nodes, sinks)
    side = [x for x in ROOT_ATTACH.get(r, []) if x in N]
    if side:
        pos, edges = g.attach_layout(pos, set(pos) | g.ancestry(side), side)
    charts.append({"title": rd.display(r) if hasattr(rd, "display") else r, "anchor": r, "mode": "root",
                   "nodes": pos, "edges": edges})
    print(f"{r}: {len(pos)} holdings" + (f" (+ side track {side})" if side else ""))
for c in kept:
    charts.append(c); print(f"{c['title']}: {len(c['nodes'])} holdings (kept from Monument charts)")
print("left the root charts:", sorted(own))
out = sys.argv[1] if len(sys.argv) > 1 else "layout_roots.json"
json.dump(charts, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1); print("wrote", out)
