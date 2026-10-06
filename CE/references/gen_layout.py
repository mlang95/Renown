#!/usr/bin/env python3
"""gen_layout.py — rebuild layout.json (the tech-tree charts) from the pursuit data.

    python gen_layout.py [layout.json]

Each chart in layout.json keeps its title / anchor / mode; this script recomputes its
NODES, POSITIONS and EDGES from NODES[*].mastery_req (the same graph builds_into mirrors):

  mode "chain" (default when the chart has anchors): the anchors plus every pursuit that
      feeds them, transitively, through Mastery requirements ("A or B" → both options shown).
  mode "group": the chart's current node list is kept (hand-curated grouping); only the
      positions and edges are recomputed.

Layout: column = longest requirement path from the chart's roots (anchors forced to the last
column); rows are ordered by the average row of each node's requirements (barycenter), so
lines run mostly straight left→right. Positions are still plain [col,row] pairs — hand-edit
the output freely; re-running this script overwrites them.

Monuments that no chart anchors are reported (add them to a chart's "anchor" list).
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
CATCH_ALL = "Other Pursuits (feed no Monument)"
sys.path.insert(0, os.path.dirname(HERE))
try:
    import ce_paths; ce_paths.install(verbose=False)
except Exception:
    pass
import renown_data as rd

N = rd.NODES
_NAMES = sorted(N, key=len, reverse=True)


def reqs(n):
    """Pursuits named in n's Mastery requirement (AND parts and every 'or' option).
    SIMPLE: n's efficient parents (the inverse of builds_into)."""
    if getattr(rd, "SIMPLE", False):
        return [p for p in rd.node_parents(n) if p != n]
    t = re.sub(r"\*", "", str(N[n].get("mastery_req") or ""))
    out, t2 = [], t
    for x in _NAMES:
        m = re.search(r"(?<![\w'])" + re.escape(x) + r"(?![\w'])", t2, re.I)
        if m:
            out.append((m.start(), x)); t2 = t2[:m.start()] + "#" * len(x) + t2[m.end():]
    return [x for _, x in sorted(out) if x != n]


def ancestry(anchors):
    seen, stack = set(anchors), list(anchors)
    while stack:
        for q in reqs(stack.pop()):
            if q not in seen:
                seen.add(q); stack.append(q)
    return seen


def layout(nodes, anchors):
    nodes = list(nodes)
    par = {n: [q for q in reqs(n) if q in nodes] for n in nodes}
    depth = {}
    def d(n, stack=()):
        if n in depth: return depth[n]
        if n in stack: return 0                              # cycle guard (e.g. mutual requirements)
        depth[n] = 0 if not par[n] else 1 + max(d(p, stack + (n,)) for p in par[n])
        return depth[n]
    for n in nodes: d(n)
    last = max(depth.values()) if depth else 0
    for a in anchors:
        if a in depth: depth[a] = max(last, depth[a])
    cols = {}
    for n in nodes: cols.setdefault(depth[n], []).append(n)
    row = {}
    for c in sorted(cols):
        def key(n):
            ps = [row[p] for p in par[n] if p in row]
            return (sum(ps) / len(ps) if ps else 1e9, n)
        for i, n in enumerate(sorted(cols[c], key=key)):
            row[n] = i
    # one right-to-left pass: pull feeders toward the average row of what they feed
    kids = {n: [k for k in nodes if n in par[k]] for n in nodes}
    for c in sorted(cols, reverse=True)[1:]:
        def key2(n):
            ks = [row[k] for k in kids[n]]
            return (sum(ks) / len(ks) if ks else row[n], n)
        for i, n in enumerate(sorted(cols[c], key=key2)):
            row[n] = i
    pos = {n: [depth[n], row[n]] for n in sorted(nodes, key=lambda n: (depth[n], row[n]))}
    edges = [[p, n] for n in nodes for p in par[n]]
    return pos, edges


def main(path, out=None):
    """Read chart titles/anchors/modes from `path`; write the rebuilt layout to `out` (default: in place)."""
    out = out or path
    charts = json.load(open(path, encoding="utf-8"))
    anchored = set()
    for c in charts:
        an = c.get("anchor")
        an = [an] if isinstance(an, str) else list(an or [])
        anchored |= set(an)
        mode = c.get("mode") or ("chain" if an else "group")
        if mode == "chain":
            nodes = ancestry([a for a in an if a in N])
        else:
            nodes = [n for n in c["nodes"] if n in N]
        old = set(c.get("nodes", {}))
        c["nodes"], c["edges"] = layout(nodes, [a for a in an if a in N])
        c["mode"] = mode
        new = set(c["nodes"])
        print(f"{c['title']}: {len(old)} -> {len(new)} pursuits"
              + (f"  - {sorted(old - new)}" if old - new else "") + (f"  + {sorted(new - old)}" if new - old else ""))
    # every pursuit should appear somewhere: anything no chart shows goes to a catch-all group chart
    shown = set().union(*[set(c["nodes"]) for c in charts if c.get("title") != CATCH_ALL])
    loose = [n for n in N if n not in shown]
    charts[:] = [c for c in charts if c.get("title") != CATCH_ALL]
    if loose:
        pos, edges = layout(loose, [])
        charts.append({"title": CATCH_ALL, "anchor": None, "mode": "group", "nodes": pos, "edges": edges})
        print(f"{CATCH_ALL}: {len(loose)} pursuits  {loose}")
    mons = [k for k, v in N.items() if v.get("type") == "Monument" or v.get("monument")]
    loose = [m for m in mons if m not in anchored]
    if loose:
        print("Monuments not anchored by any chart:", loose)
    json.dump(charts, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("wrote", out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "layout.json"),
         sys.argv[2] if len(sys.argv) > 2 else None)
