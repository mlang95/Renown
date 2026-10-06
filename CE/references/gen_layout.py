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
CATCH_ALL = "Other Pursuits (feed no Monument)"   # display layer renames Pursuits under SIMPLE
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
    if getattr(rd, "SIMPLE", False):   # Monuments listed as a parent (Secret Cellar) would loop the chart back on itself
        return [p for p in rd.node_parents(n) if p != n and not (N[p].get("monument") and not N[n].get("monument"))]
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


def track_layout(nodes, sinks):
    """SIMPLE: columns = depth from the roots; rows = tracks. Walking back from each sink, a Holding's
    deepest parent continues its row and every other unplaced parent starts a new row, so alternative
    lines into the same Holding (e.g. a market track and a merchant track) read as separate rows."""
    nodes = list(nodes)
    par = {n: [q for q in reqs(n) if q in nodes] for n in nodes}
    depth = {}
    def d(n, stack=()):
        if n in depth: return depth[n]
        if n in stack: return 0
        depth[n] = 0 if not par[n] else 1 + max(d(p, stack + (n,)) for p in par[n])
        return depth[n]
    for n in nodes: d(n)
    row, nxt = {}, [0]
    def place(n, r):
        row[n] = r
        first = True
        for q in sorted(par[n], key=lambda q: (-depth[q], q)):
            if q in row or depth[q] >= depth[n]:
                continue
            if first:
                first = False; place(q, r)
            else:
                nxt[0] += 1; place(q, nxt[0])
    for snk in sinks:
        if snk in row: continue
        if row: nxt[0] += 1
        place(snk, nxt[0])
    for n in sorted(nodes, key=lambda n: -depth[n]):          # anything a cycle left unplaced
        if n not in row:
            nxt[0] += 1; place(n, nxt[0])
    pos = {n: [depth[n], row[n]] for n in sorted(nodes, key=lambda n: (depth[n], row[n]))}
    return pos, [[p, n] for n in nodes for p in par[n]]


def _domain(unlock):
    for dname in ("Industry", "Prowess", "Piety", "Cunning"):
        if dname in str(unlock): return dname
    return "Other"


def main_simple(out):
    """SIMPLE: one chart per Monument (its full Mastery Chain), then one chart for Holdings that feed none."""
    mons = [k for k, v in N.items() if v.get("monument")]
    order = {"Industry": 0, "Prowess": 1, "Piety": 2, "Cunning": 3, "Other": 4}
    mons.sort(key=lambda m: (order[_domain(N[m].get("unlock"))], m))
    charts = []
    groups = []                                   # Monuments whose Mastery Chains are identical share a chart
    for m in mons:
        base = frozenset(ancestry([m]) - {m})
        for g in groups:
            if g[0] == base: g[1].append(m); break
        else:
            groups.append((base, [m]))
    for base, ms in groups:
        nodes = set(base) | set(ms)
        pos, edges = track_layout(nodes, ms)
        title = " × ".join(rd.display(m) if hasattr(rd, "display") else m for m in ms)
        charts.append({"title": title, "anchor": ms if len(ms) > 1 else ms[0], "mode": "chain",
                       "nodes": pos, "edges": edges})
        print(f"{title}: {len(pos)} holdings, {max(v[1] for v in pos.values()) + 1} track(s)")
    shown = set().union(*[set(c["nodes"]) for c in charts]) if charts else set()
    loose = [n for n in N if n not in shown]
    # Holdings that feed no Monument: one chart per connected family (with the ancestors it builds from)
    seen = set()
    for start in loose:
        if start in seen: continue
        comp, stack = set(), [start]
        while stack:
            x = stack.pop()
            if x in comp: continue
            comp.add(x)
            stack += [q for q in reqs(x) if q in loose] + [k for k in loose if x in reqs(k)]
        seen |= comp
        nodes = ancestry(sorted(comp))
        kids = {n: [k for k in nodes if n in reqs(k)] for n in nodes}
        sinks = sorted([n for n in comp if not kids[n]])
        pos, edges = track_layout(nodes, sinks)
        title = CATCH_ALL + " — " + ", ".join(rd.display(x) if hasattr(rd, "display") else x for x in sinks[:3]) \
            + (" …" if len(sinks) > 3 else "")
        charts.append({"title": title, "anchor": None, "mode": "group", "nodes": pos, "edges": edges})
        print(f"{title}: {len(comp)} holdings (+{len(nodes) - len(comp)} ancestors)")
    json.dump(charts, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("wrote", out)


def main(path, out=None):
    """Read chart titles/anchors/modes from `path`; write the rebuilt layout to `out` (default: in place)."""
    out = out or path
    if getattr(rd, "SIMPLE", False):
        return main_simple(out)
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
