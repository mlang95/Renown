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
# SIMPLE: Holdings that feed no Monument, shown as a side track under a Monument's chart instead
# of their own chart. Monument (data name) -> end Holdings; each brings its full ancestry. The
# Monument's own layout is kept as-is; no links are added, only real requirement edges are drawn.
ATTACH = {
    "Advanced Blast Furnace": ["Court Armoury", "Jewelry Foundry"],
    "Preceptory of the Knight's Templar": ["Hospitaller"],
    "Royal Pavilion": ["Tiltyard"],
}
# SIMPLE: hand placement, applied last. Monument (data name) -> {Holding: [col, row]}. Holdings not
# listed keep their generated spot; pins naming a Holding not on the chart, or landing on an occupied
# cell, are reported and skipped.
PIN = {
    "Outrider Intercept Post": {
        "Caravanery": [3, 0], "Toll House": [4, 0], "Beacon Towers": [5, 0], "Outrider Intercept Post": [6, 0],
    },
}
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


def track_layout(nodes, sinks, links=(), zag=()):
    """SIMPLE: rows = tracks, columns = as far right as each Holding can sit.
    Walking back from each sink, a Holding's deepest parent continues its row and every other
    parent starts a new row. Columns are placed right-to-left (one left of the earliest Holding it
    feeds), so a side input sits next to what it feeds as its own block instead of being stretched
    back to the roots. `links` = extra [parent, child] pairs (e.g. Naturals into Manor House).
    `zag` = (parent, child) pairs drawn as a vertical step: the child sits in that parent's column."""
    nodes = sorted(nodes)                                   # set order varies per run; keep layouts stable
    par = {n: [q for q in reqs(n) if q in nodes] for n in nodes}
    for p_, c_ in links:
        if p_ in par and c_ in par and p_ not in par[c_]: par[c_].append(p_)
    kids = {n: [k for k in nodes if n in par[k]] for n in nodes}
    depth = {}
    def d(n, stack=()):
        if n in depth: return depth[n]
        if n in stack: return 0
        depth[n] = 0 if not par[n] else max(d(p, stack + (n,)) + (0 if (p, n) in zag else 1) for p in par[n])
        return depth[n]
    for n in nodes: d(n)
    top = max(depth.values()) if depth else 0
    col = {}
    zc = {c_ for _, c_ in zag}                              # a zag child shares its parent's depth: place it first
    for n in sorted(nodes, key=lambda n: (-depth[n], n not in zc)):
        ks = [col[k] + (1 if (n, k) in zag else 0) for k in kids[n] if k in col]
        col[n] = (min(ks) - 1) if ks else (top if n in sinks else depth[n])
    lo = min(col.values()) if col else 0
    for n in col: col[n] -= lo
    anc = {}
    def ancs(n, stack=()):
        if n in anc: return anc[n]
        out = set()
        for p in par[n]:
            if p in stack: continue
            out |= {p} | ancs(p, stack + (n,))
        anc[n] = out
        return out
    row, nxt = {}, [0]
    def place(n, r):
        row[n] = r
        first = True
        # the parent that other parents also build from (the fork) continues the row, so its link to
        # n stays clear and the branch through the other parent gets its own row; then the deepest
        ps = par[n]
        fork = lambda q: any(q in ancs(o) for o in ps if o != q)
        for q in sorted(ps, key=lambda q: (not fork(q), -depth[q], q)):
            if q in row or col[q] >= col[n]:
                continue
            if first:
                first = False; place(q, r)
            else:
                nxt[0] += 1; place(q, nxt[0])
    for snk in sinks:
        if snk in row: continue
        if row: nxt[0] += 1
        place(snk, nxt[0])
    for n in sorted(nodes, key=lambda n: -col[n]):          # anything a cycle left unplaced
        if n not in row:
            nxt[0] += 1; place(n, nxt[0])
    pos = {n: [col[n], row[n]] for n in sorted(nodes, key=lambda n: (col[n], row[n]))}
    return pos, [[p, n] for n in nodes for p in par[n]]


def attach_layout(pos0, nodes, side, links=()):
    """SIMPLE: add side tracks below an existing chart without moving its Holdings.
    New Holdings sit one column left of the earliest Holding they feed (end Holdings: one right of
    their rightmost parent). Each side end
    Holding takes a new row; a parent that is new continues that row unless an already-placed parent
    lies further left (its edge would run along the row), in which case new parents go on rows below.
    An end Holding whose parents are all placed takes the first free row at its column."""
    pos = {k: list(v) for k, v in pos0.items()}
    new = sorted(n for n in nodes if n not in pos)
    par = {n: [q for q in reqs(n) if q in nodes] for n in nodes}
    col = {k: v[0] for k, v in pos.items()}
    def c(n, stack=()):
        if n in col: return col[n]
        ps = [q for q in par[n] if q not in stack]
        col[n] = 1 + max(c(q, stack + (n,)) for q in ps) if ps else 0
        return col[n]
    for n in new: c(n)
    kids = {n: [k for k in new if n in par[k]] for n in new}
    for n in sorted(new, key=lambda n: -col[n]):    # pull new feeders right, next to what they feed
        if n in side or not kids[n]: continue
        col[n] = max(col[n], min(col[k] for k in kids[n]) - 1)
    base = max(v[1] for v in pos.values()) + 1 if pos else 0
    nxt = [base - 1]
    taken = {(v[0], v[1]) for v in pos.values()}
    def put(n, r):
        pos[n] = [col[n], r]; taken.add((col[n], r))
    def place(n, r):
        put(n, r)
        ps = sorted(par[n], key=lambda q: (-col[q], q))
        fresh = [q for q in ps if q not in pos and col[q] < col[n]]
        if not fresh: return
        left_placed = any(q in pos and col[q] < col[fresh[0]] for q in par[n])
        for i, q in enumerate(fresh):
            if q in pos: continue
            if i == 0 and not left_placed:
                place(q, r)
            else:
                nxt[0] += 1; place(q, nxt[0])
    for s_ in side:
        if s_ in pos: continue
        if not [q for q in par[s_] if q not in pos]:
            r = base
            while (col[s_], r) in taken: r += 1
            nxt[0] = max(nxt[0], r); put(s_, r)
        else:
            nxt[0] += 1; place(s_, nxt[0])
    for n in new:                                   # anything not reached from a side end
        if n not in pos:
            nxt[0] += 1; place(n, nxt[0])
    lo = min(v[0] for v in pos.values())
    pos = {n: [v[0] - lo, v[1]] for n, v in sorted(pos.items(), key=lambda kv: (kv[1][0], kv[1][1]))}
    edges = [[p, n] for n in sorted(nodes) for p in par[n]]
    return pos, edges + [list(l) for l in links if list(l) not in edges]


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

    def families(pool):
        out, seen = [], set()
        for start in pool:
            if start in seen: continue
            comp, stack = set(), [start]
            while stack:
                x = stack.pop()
                if x in comp: continue
                comp.add(x)
                stack += [q for q in reqs(x) if q in pool] + [k for k in pool if x in reqs(k)]
            seen |= comp; out.append(comp)
        return out
    def natural(n): return "natural" in str(N[n].get("innate", "")).lower()
    def chain_tokens(n):
        e = N[n].get("efficient"); return [e] if isinstance(e, str) else list(e or [])
    # A Monument chained from "Natural" (Manor House) gathers the loose families that end only in
    # Natural Holdings; each family's end Holding links into it.
    for c in charts:
        ms = c["anchor"] if isinstance(c["anchor"], list) else [c["anchor"]]
        if not any("Natural" in chain_tokens(m) for m in ms): continue
        take = []
        for comp in families(loose):
            sinks = [n for n in comp if not [k for k in comp if n in reqs(k)]]
            if sinks and all(natural(x) for x in sinks): take.append((comp, sinks))
        if not take: continue
        fam = set().union(*[t[0] for t in take])
        links = [[x, m] for _, sk in take for x in sorted(sk) for m in ms if "Natural" in chain_tokens(m)]
        nodes = set(c["nodes"]) | ancestry(sorted(fam))
        pos, edges = track_layout(nodes, ms, links)
        c["nodes"], c["edges"], c["links"] = pos, edges + links, links
        loose = [n for n in loose if n not in fam]
        print(f"{c['title']}: + {sorted(fam)} via Natural")
    # attached side tracks (ATTACH): pulled out of the catch-all onto their Monument's chart
    for c in charts:
        ms = c["anchor"] if isinstance(c["anchor"], list) else [c["anchor"]]
        side = [x for m in ms for x in ATTACH.get(m, []) if x in N]
        if not side: continue
        fam = ancestry(side)
        c["nodes"], c["edges"] = attach_layout(c["nodes"], set(c["nodes"]) | fam, side, c.get("links", ()))
        loose = [n for n in loose if n not in fam]
        print(f"{c['title']}: + side track {side}")
    for m, xs in ATTACH.items():
        miss = [x for x in [m] + xs if x not in N]
        if miss: print("ATTACH: unknown name(s)", miss)
    for c in charts:                                   # hand placement (PIN)
        ms = c["anchor"] if isinstance(c["anchor"], list) else [c["anchor"]]
        pins = {k: v for m in ms for k, v in PIN.get(m, {}).items()}
        if not pins: continue
        miss = [k for k in pins if k not in c["nodes"]]
        if miss: print(f"PIN {c['title']}: not on chart {miss}")
        new = {n: list(pins.get(n, p)) for n, p in c["nodes"].items()}
        cells = {}
        for n, p in new.items(): cells.setdefault(tuple(p), []).append(n)
        for cell, ns in cells.items():
            if len(ns) > 1:
                print(f"PIN {c['title']}: {ns} share {list(cell)}; pins on that cell skipped")
                for n in ns:
                    if n in pins: new[n] = list(c["nodes"][n])
        c["nodes"] = dict(sorted(new.items(), key=lambda kv: (kv[1][0], kv[1][1])))
        # pins are fixed; a Holding added later is placed by the generator and can end up beside or behind what it feeds
        bad = [f"{p_} -> {k_}" for p_, k_ in c["edges"] if p_ in new and k_ in new
               and new[p_][0] >= new[k_][0] and not (p_ in pins and k_ in pins)
               and [k_, p_] not in c["edges"]]                     # mutual chains (cycles) can't run one way
        if bad: print(f"PIN {c['title']}: links not left-to-right {bad}; add/adjust pins")
    # Holdings that feed no Monument: one chart per connected family (with the ancestors it builds from)
    for comp in families(loose):
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