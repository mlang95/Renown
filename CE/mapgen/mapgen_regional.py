"""mapgen_regional.py — preset-driven map generation for Renown.

Sibling to mapgen.generate(), not a replacement. Where the default generator is
additive (blank plains -> stamp biomes -> stop at a plains target) and keeps
terrain out of the way, this one is preset-driven and lets terrain matter:
a preset may fill the board with a SUBSTRATE and carve plains out of it.

Order of operations is deliberate. Settlements are placed on a blank plains
board FIRST, before any substrate exists, so settlement legality never fights
the matrix. The substrate is then poured around them and the connective tissue
is carved back out.

    blank plains
      -> water border
      -> place regions (mapgen._place_regions, unchanged)
      -> pour substrate around reserved hexes        [matrix presets only]
      -> carve settlement clearings                  [matrix presets only]
      -> carve route network between clearings       [matrix presets only]
      -> stamp accent terrain (blob / band / scatter / fringe)
      -> cull + cap (substrate exempt)
      -> resources (palette-filtered)
      -> hills (preset-toggleable)
      -> validate; reseed on failure

Deterministic per seed.
"""
from __future__ import annotations
import math, random
from collections import Counter

from hexmap import HexMap, distance
import mapgen
from mapgen import _cube, _offset, CUBE_DIRS, _component, _spread_picks
import region_presets


# ── buffer rule ──────────────────────────────────────────────────────────────
def _clear_pw(m, coord, terrain, own, buffers, substrate):
    """Pairwise buffer. A hex may become `terrain` unless one of its neighbours
    holds a terrain that is listed as needing a plains gap from `terrain`.

    mapgen._clear applies a blanket buffer between ALL land biomes; here the
    preset names the specific pairs. An empty `buffers` list means terrain may
    abut freely, which is what a matrix preset wants. The substrate is always
    permitted to touch anything — it is the background, not a feature.
    """
    for nb in m.neighbors(coord):
        t = nb.terrain
        if t in ("plains", terrain, substrate) or nb.coord in own:
            continue
        if frozenset((terrain, t)) in buffers:
            return False
    return True


# ── primitives ───────────────────────────────────────────────────────────────
def _roll_borders(spec, players, rng, mirror="ns"):
    """Resolve a border spec into per-edge coastline segments.

    Each edge resolves to (width, lo, hi): a water rim `width` hexes deep
    running CONTINUOUSLY from `lo` to `hi` along that edge, and dry elsewhere.
    A coast is one unbroken run that starts and stops — never a scatter of
    disconnected puddles along the border.

    A per-edge spec is one of:
        0                      dry edge (the default)
        2                      full-length rim, 2 hexes deep
        {"width": (1, 2),      depth, rolled
         "span":  (.4, .8)}    fraction of the edge covered, rolled

    BALANCE CONSTRAINT: edges that player start regions front onto must match
    each other — same depth, same span, same offset — or one side of the table
    gets a sea flank its opposite number does not. With 6-7 players the starts
    run along the top and bottom, so north and south are rolled once and
    mirrored while east and west roll free. At 2 players the starts are left
    and right, so the live axis flips (mirror="ew"). At 4-5 the starts sit in
    the corners and every edge fronts one, so all four match (mirror="all").
    Passing mirror="auto" derives this from the player count.
    """
    def one(v, length):
        if isinstance(v, dict):
            w = v.get("width", 1)
            w = rng.randint(*w) if isinstance(w, (tuple, list)) else w
            sp = v.get("span", 1.0)
            sp = rng.uniform(*sp) if isinstance(sp, (tuple, list)) else sp
        else:
            w = rng.randint(*v) if isinstance(v, (tuple, list)) else v
            sp = 1.0
        if w <= 0:
            return (0, 0, -1)
        run = max(1, int(round(sp * length)))
        lo = rng.randint(0, max(0, length - run))
        return (w, lo, lo + run - 1)

    if isinstance(spec, int):
        spec = {e: spec for e in "nsew"}
    spec = dict(spec)
    if mirror == "auto":
        mirror = "ew" if players <= 2 else ("all" if players in (4, 5) else "ns")

    out = {}
    if mirror == "all":
        v = one(spec.get("n", 0), 0)
        return {e: v for e in "nsew"}
    pair = ("n", "s") if mirror == "ns" else ("e", "w") if mirror == "ew" else ()
    return out, spec, pair, one


def _resolve_borders(spec, players, rng, w, h, mirror="ns"):
    packed = _roll_borders(spec, players, rng, mirror)
    if isinstance(packed, dict):
        return packed
    out, spec, pair, one = packed
    if pair:
        length = w if pair[0] in "ns" else h
        v = one(spec.get(pair[0], 0), length)
        out[pair[0]] = out[pair[1]] = v          # identical depth, span, offset
    for e in "nsew":
        if e not in out:
            out[e] = one(spec.get(e, 0), w if e in "ns" else h)
    return out


def _border_water(m, edges):
    """Apply per-edge coastline segments.

    Each edge of the frame is its own thing: the Lost Woods opens west to
    water and is landlocked on the other three, Lenaveron meets the Sea of Ash
    only on its east. Land is the DEFAULT — a map is not automatically an
    island.
    """
    if isinstance(edges, int):
        edges = {e: (edges, 0, (m.width if e in "ns" else m.height) - 1)
                 for e in "nsew"}
    for h in m.all():
        wn, ln, hn = edges.get("n", (0, 0, -1))
        ws, ls, hs = edges.get("s", (0, 0, -1))
        ww, lw, hw = edges.get("w", (0, 0, -1))
        we, le, he = edges.get("e", (0, 0, -1))
        if ((h.row < wn and ln <= h.col <= hn)
                or (m.height - 1 - h.row < ws and ls <= h.col <= hs)
                or (h.col < ww and lw <= h.row <= hw)
                or (m.width - 1 - h.col < we and le <= h.row <= he)):
            h.terrain = "water"


def _thin_water(m, protect):
    """Flatten confluences back to one hex.

    Rivers are drawn as independent layers, so where two of them cross or run
    alongside each other the union is two or three hexes wide. Any interior
    water hex is removed if the water around it stays connected without it —
    the junction survives, the bulge does not. Border rim hexes are protected.
    """
    changed = True
    while changed:
        changed = False
        for h in list(m.all()):
            if h.terrain != "water" or h.coord in protect:
                continue
            wn = [n.coord for n in m.neighbors(h.coord) if n.terrain == "water"]
            if len(wn) < 3:
                continue
            seen, stack = set(), [wn[0]]        # is the rest still joined?
            while stack:
                c = stack.pop()
                if c in seen or c == h.coord:
                    continue
                if m.get(c).terrain != "water":
                    continue
                seen.add(c)
                for nb in m.neighbors(c):
                    if nb.coord not in seen and nb.coord != h.coord:
                        stack.append(nb.coord)
            if all(w in seen for w in wn):
                h.terrain = "plains"
                changed = True


def _pour_substrate(m, terrain, skip):
    """Fill every land hex not in `skip` with the substrate."""
    for h in m.all():
        if h.terrain == "water" or h.coord in skip:
            continue
        h.terrain = terrain


def _carve_clearing(m, centre, radius, terrain="plains"):
    """Open a pocket. Used to guarantee a settlement is not buried by its own
    substrate. Never touches water (the rim stays intact).

    Every hex opened is recorded in m.carved. The validator resolves carved
    hexes back to the substrate when counting raw-material terrains: the
    material WAS in range before the swap, and it is the clearing that made
    the site legal at all. Without this, clearing radius and the material
    invariant are the same knob and fight each other.
    """
    carved = getattr(m, "carved", None)
    if carved is None:
        carved = m.carved = set()
    n = 0
    for h in m.within(centre, radius):
        if h.terrain != "water" and h.terrain != terrain:
            carved.add(h.coord)
            h.terrain = terrain
            n += 1
    return n


def _carve_route(m, a, b, width=1, terrain="plains", temp=0.8, rng=None):
    """Corridor from a to b as a DRIFT-BIASED RANDOM WALK.

    At each step every non-water neighbour is scored by how much it changes the
    distance to the target (-1 closer, 0 level, +1 further) and chosen with
    weight exp(-delta/temp). Low temp is a near-straight road; high temp
    wanders badly before arriving. Backward steps are legal, which is what
    separates this from a greedy line — it is the backtracking that produces
    switchbacks, dead-end stubs and canyon bends rather than a drawn diagram.

    Step budget scales with distance so a hot walk still terminates.
    """
    rng = rng or getattr(m, "_rng", random)
    carved = getattr(m, "carved", None)
    if carved is None:
        carved = m.carved = set()
    cur, laid = a, 0
    budget = 8 * distance(a, b) + 30
    for _ in range(budget):
        h = m.get(cur)
        if h and h.terrain not in ("water", terrain):
            carved.add(cur)
            h.terrain = terrain
            laid += 1
        if width > 1:
            for nb in m.neighbors(cur):
                if nb.terrain not in ("water", terrain):
                    carved.add(nb.coord)
                    nb.terrain = terrain
                    laid += 1
        if cur == b:
            break
        nbrs = [n.coord for n in m.neighbors(cur)
                if m.get(n.coord).terrain != "water"]
        if not nbrs:
            break
        d0 = distance(cur, b)
        ws = [math.exp(-(distance(c, b) - d0) / max(temp, 1e-3)) for c in nbrs]
        cur = rng.choices(nbrs, weights=ws, k=1)[0]
    return laid


def _route_network(m, points, extra, width, temp=0.8):
    """Spanning tree over `points` (nearest-neighbour greedy), plus `extra`
    chords. The spanning tree is the playability guarantee; the chords are what
    make the network a network instead of a corridor."""
    if len(points) < 2:
        return
    linked = [points[0]]
    rest = list(points[1:])
    while rest:
        a, b = min(((a, b) for a in linked for b in rest),
                   key=lambda p: distance(*p))
        _carve_route(m, a, b, width, temp=temp)
        linked.append(b)
        rest.remove(b)
    pairs = sorted(((a, b) for i, a in enumerate(points) for b in points[i + 1:]),
                   key=lambda p: distance(*p))
    for a, b in pairs[:max(0, extra)]:
        _carve_route(m, a, b, width, temp=temp)


def _carve_river(m, count, rng, temp=1.0, turn_p=0.38):
    """Meandering one-hex rivers, edge of board to edge of board.

    Built as LAYERS rather than painted in place. Each river is first walked
    out as an ordered path, then cleaned, then stamped:

      1. Walk with HEADING MOMENTUM — keep a direction and turn at most one
         face at a time. Re-sampling every step from distance weights (what
         the corridor carver does) produces jittery zig-zags; a river wants
         gentle sweeping bends.
      2. Cut loops. If the walk re-enters a hex it already occupies, the whole
         intervening excursion is discarded rather than drawn — that is where
         doubled-up width came from.
      3. Thin. Any hex whose removal still leaves its neighbours in the path
         adjacent is redundant width and is dropped.

    Both endpoints sit on the board edge, so every river runs off the map at
    both ends instead of beginning or ending in the middle of the wood.
    """
    bw = getattr(m, "borders", {})
    wet = {e for e in "nsew" if bw.get(e, (0,))[0] > 0}
    def side(c):
        if c[1] == 0: return "n"
        if c[1] == m.height - 1: return "s"
        if c[0] == 0: return "w"
        if c[0] == m.width - 1: return "e"
        return None
    edges = [h.coord for h in m.all()
             if h.col in (0, m.width - 1) or h.row in (0, m.height - 1)]
    # EVERY edge is a legal mouth — a river may enter over a land border and
    # run off the far side just as readily as it can run down to a coast.
    # A water border only WEIGHTS that edge more heavily (it appears twice in
    # the pool); it never excludes the dry ones, which is what wrongly pinned
    # Lenaveron's rivers away from its western edge.
    mouths = edges + [c for c in edges if side(c) in wet]
    if len(edges) < 2:
        return 0
    depth = lambda c: min(c[0], m.width - 1 - c[0], c[1], m.height - 1 - c[1])
    inland = max(2, min(m.width, m.height) // 4)
    laid = 0
    for _ in range(count):
        a = rng.choice(mouths)
        # The exit must be placed so the line between the two ends actually
        # CROSSES the map. Any two edge hexes can be joined by walking along
        # the border, and with a water rim that path is already water — which
        # is why most rivers were carving nothing at all.
        # only the MOUTH is biased to a wet edge; the far end may leave by any
        # edge, or the pair collapses onto one side and no river is legal
        far = [c for c in edges
               if distance(c, a) >= max(m.width, m.height) // 2
               and depth(((c[0] + a[0]) // 2, (c[1] + a[1]) // 2)) >= inland]
        if not far:
            continue
        b = rng.choice(far)

        # 1. walk with momentum, starting INWARD rather than straight at b,
        # so the river commits to the interior before it starts steering.
        path, cur, went_inland = [a], a, False
        heading = max(range(6), key=lambda d: depth(
            _offset(*(x + y for x, y in zip(_cube(*a), CUBE_DIRS[d])))))
        for _ in range(8 * distance(a, b) + 30):
            if rng.random() < turn_p:
                heading = (heading + rng.choice((-1, 1))) % 6
            elif rng.random() < 1.0 / max(temp, 0.2) * 0.10:
                heading = min(                       # gentle pull toward b
                    ((heading + k) % 6 for k in (-1, 0, 1)),
                    key=lambda d: distance(_offset(*(
                        x + y for x, y in zip(_cube(*cur), CUBE_DIRS[d]))), b))
            nxt = _offset(*(x + y for x, y in
                            zip(_cube(*cur), CUBE_DIRS[heading])))
            if not m.in_bounds(nxt):
                # A momentum walk launched from the rim re-hits the rim within
                # a few steps, so breaking on the first out-of-bounds killed
                # most rivers before they entered the wood. Deflect along the
                # boundary until the river has actually gone inland; only then
                # is leaving the map a legitimate ending.
                if went_inland:
                    break
                for k in (1, -1, 2, -2, 3):
                    h2 = (heading + k) % 6
                    cand = _offset(*(x + y for x, y in
                                     zip(_cube(*cur), CUBE_DIRS[h2])))
                    if m.in_bounds(cand) and cand not in path:
                        heading, nxt = h2, cand
                        break
                else:
                    break
                if not m.in_bounds(nxt):
                    break
            if nxt in path:                          # 2. cut the loop
                path = path[:path.index(nxt) + 1]
                cur = nxt
                continue
            path.append(nxt)
            cur = nxt
            if depth(cur) >= inland:
                went_inland = True
            if cur == b and went_inland:
                break

        # 3. thin redundant width
        i = 1
        while i < len(path) - 1:
            if distance(path[i - 1], path[i + 1]) <= 1:
                path.pop(i)
            else:
                i += 1

        for c in path:
            h = m.get(c)
            if h and h.terrain != "water":
                h.terrain = "water"
                laid += 1
    return laid


def _lift_islands(m, groups, size_rng, rng, islets=(0, 0),
                  land_target=0.55, gap=(2, 4)):
    """Raise land out of a water substrate.

    Each group is a set of settlement coords that must share one island; the
    island grows outward from those settlements until it reaches its target
    size. Extra uninhabited islets are scattered afterwards as expansion
    targets — the small starter isle that makes a Shipyard worth building.
    """
    # Hard ceiling on total land. Per-island budgets scale with how many
    # settlements share an island, and with few large islands that product
    # can exceed the whole board — Twelfth Reach drank the entire ocean at
    # 2 islands x 9 settlements. The ceiling is what keeps it a sea.
    budget = int(land_target * m.width * m.height) - m.count("plains")
    total = 0
    for grp in groups:
        # Size scales with how many settlements share the island. With 6
        # regions and islands=(5,6) one island carries two regions and needs
        # roughly double the land, or its settlements end up on separate
        # sandbars and fail their own reachability check.
        want = int(rng.randint(*size_rng) * max(1.0, len(grp) / 3.0))
        want = max(len(grp) * 8, min(want, budget // max(1, len(groups))))
        filled = set(grp)
        for c in grp:
            h = m.get(c)
            if h and h.terrain == "water":
                h.terrain = "plains"
        # Bridge the settlements to each other FIRST. Growing outward from
        # scattered seeds and hoping the blobs merge leaves settlements on
        # separate sandbars whenever the size budget runs out early.
        anchor = next(iter(grp))
        for c in grp:
            cur = c
            while cur != anchor:
                nxt = min((n.coord for n in m.neighbors(cur)),
                          key=lambda q: distance(q, anchor))
                if distance(nxt, anchor) >= distance(cur, anchor):
                    break
                h = m.get(nxt)
                if h.terrain == "water":
                    h.terrain = "plains"
                filled.add(nxt)
                cur = nxt
        while len(filled) < want:
            frontier = set()
            for c in filled:
                for nb in m.neighbors(c):
                    if nb.coord not in filled and nb.terrain == "water":
                        frontier.add(nb.coord)
            if not frontier:
                break
            nxt = min(frontier,
                      key=lambda c: min(distance(c, g) for g in grp) + rng.random() * 2)
            m.get(nxt).terrain = "plains"
            filled.add(nxt)
        total += len(filled)
    n_islet, sz = islets
    for _ in range(n_islet):
        # Seed islets at a controlled GAP from existing land rather than
        # wherever open water happens to be. A two-hex gap is the interesting
        # one: still impassable at base movement, but crossable with Bridges
        # once a player's Reach covers the water between.
        land = [h.coord for h in m.all() if h.terrain != "water"]
        cands = [h.coord for h in m.all()
                 if h.terrain == "water"
                 and all(n.terrain == "water" for n in m.neighbors(h.coord))
                 and gap[0] <= min((distance(h.coord, l) for l in land),
                                   default=99) <= gap[1]]
        if not cands:
            cands = [h.coord for h in m.all()
                     if h.terrain == "water"
                     and all(n.terrain == "water" for n in m.neighbors(h.coord))]
        if not cands:
            break
        seed = rng.choice(cands)
        filled = {seed}
        m.get(seed).terrain = "plains"
        while len(filled) < sz:
            frontier = {nb.coord for c in filled for nb in m.neighbors(c)
                        if nb.terrain == "water"}
            if not frontier:
                break
            nxt = min(frontier, key=lambda c: distance(c, seed) + rng.random())
            m.get(nxt).terrain = "plains"
            filled.add(nxt)
        total += len(filled)
    return total


def _group_regions(m, k):
    """Split the region centres into k island groups by nearest-centre
    clustering, then return the settlement coords per group."""
    ctrs = list(m.centers)
    if k >= len(ctrs):
        return [set(st) for st in m.settlements]
    picks = [ctrs[0]]
    while len(picks) < k:
        picks.append(max(ctrs, key=lambda c: min(distance(c, q) for q in picks)))
    groups = [set() for _ in picks]
    for st, ctr in zip(m.settlements, m.centers):
        i = min(range(k), key=lambda j: distance(ctr, picks[j]))
        groups[i] |= set(st)
    return [g for g in groups if g]


def _carve_maze(m, count, rng, temp=1.7, junction_p=0.5, terrain="plains"):
    """Extra single-hex passages threaded through the matrix, independent of
    the settlement network.

    Each passage runs rim-to-rim across the board at high walk temperature, so
    it wanders rather than crossing. With probability `junction_p` every
    passage is instead routed through ONE shared hex near the board centre,
    which turns that hex into a single-tile chokepoint every passage must pass
    through — the whole middle of the map funnelled into one Territory.

    These are width 1 by definition. Widening them would defeat the point.
    """
    if count <= 0:
        return 0
    rim = [h.coord for h in m.all()
           if h.terrain != "water"
           and (any(n.terrain == "water" for n in m.neighbors(h.coord))
                or h.col in (0, m.width - 1) or h.row in (0, m.height - 1))]
    if len(rim) < 2:
        return 0
    junction = None
    if rng.random() < junction_p:
        # The junction must sit in UNBROKEN SUBSTRATE, not merely at the board
        # centre. Centre is usually already open ground from the settlement
        # network, and a junction in a field is not a chokepoint at all — the
        # passages just merge into the existing plains. Score candidates by
        # distance from any existing plains, tie-broken toward the middle.
        mid = (m.width // 2, m.height // 2)
        plains = [h.coord for h in m.all() if h.terrain == terrain]
        inner = [h.coord for h in m.all()
                 if h.terrain not in ("water", terrain)
                 and distance(h.coord, mid) <= max(m.width, m.height) // 3]
        if inner:
            junction = max(inner, key=lambda c: (
                min((distance(c, q) for q in plains), default=99)
                - 0.15 * distance(c, mid)))
    laid = 0
    used = []
    for _ in range(count):
        pool = [c for c in rim if all(distance(c, u) >= 6 for u in used)] or rim
        a = rng.choice(pool)
        b = max(rim, key=lambda c: distance(c, a) - 3 * sum(
            1 for u in used if distance(c, u) < 6))
        used += [a, b]
        if junction:
            laid += _carve_route(m, a, junction, 1, terrain, temp=temp, rng=rng)
            laid += _carve_route(m, junction, b, 1, terrain, temp=temp, rng=rng)
        else:
            laid += _carve_route(m, a, b, 1, terrain, temp=temp, rng=rng)
    return laid


def _blob(m, seed, size, terrain, ok, buffers, substrate):
    """Compact blob: always annex the frontier hex nearest the seed."""
    if not ok(m.get(seed)) or not _clear_pw(m, seed, terrain, set(), buffers, substrate):
        return 0
    m.get(seed).terrain = terrain
    filled = {seed}
    placed = 1
    while placed < size:
        frontier = set()
        for c in filled:
            for nb in m.neighbors(c):
                if (nb.coord not in filled and ok(nb)
                        and _clear_pw(m, nb.coord, terrain, filled, buffers, substrate)):
                    frontier.add(nb.coord)
        if not frontier:
            break
        nxt = min(frontier, key=lambda c: distance(seed, c))
        m.get(nxt).terrain = terrain
        filled.add(nxt)
        placed += 1
    return placed


def _stamp_blobs(m, terrain, target, ok, buffers, substrate, rng, size=(9, 16)):
    """Stamp compact blobs until `target` hexes of `terrain` exist, spreading
    each new seed away from the terrain already placed."""
    guard = 0
    while m.count(terrain) < target and guard < 400:
        guard += 1
        cands = [h.coord for h in m.all()
                 if ok(h) and _clear_pw(m, h.coord, terrain, set(), buffers, substrate)]
        if not cands:
            break
        existing = [h.coord for h in m.all() if h.terrain == terrain]
        sample = rng.sample(cands, min(len(cands), 80))
        if existing:
            seed = max(sample, key=lambda c: min(distance(c, e) for e in existing))
        else:
            seed = rng.choice(sample)
        want = min(rng.randint(*size), target - m.count(terrain))
        if _blob(m, seed, max(1, want), terrain, ok, buffers, substrate) == 0:
            # seed was blocked; drop it from consideration by nudging the rng
            continue


def _stamp_band(m, terrain, target, edge, thickness_frac, jitter, ok, rng,
                span=1.0):
    """Parallel bands running across the board, perpendicular to `edge`.

    edge "e"/"w" -> vertical bands (a wall you go around or through).
    edge "n"/"s" -> horizontal bands.
    Repeats at spaced offsets until the share target is met, which is how
    Hermit's Row gets its *pair* of ranges out of one declaration.

    `span` is the fraction of the cross axis a band covers, placed at a random
    offset. At 1.0 a band reaches edge to edge and is a genuine wall — right
    for Hermit's Row, whose ranges exist to be held at a narrows. Below 1.0 it
    is a ridge with open ground at one or both ends, which is what most regions
    actually want: relief that shapes a march without sealing an axis.
    `span` may be a (lo, hi) range to roll per band.
    """
    vertical = edge in ("e", "w")
    across = m.width if vertical else m.height
    cross = m.height if vertical else m.width
    thick = max(1, int(round(thickness_frac * across)))
    used = []
    guard = 0
    while m.count(terrain) < target and guard < 30:
        guard += 1
        sp = rng.uniform(*span) if isinstance(span, (tuple, list)) else span
        run = max(1, int(round(min(1.0, sp) * cross)))
        start = rng.randint(0, max(0, cross - run))
        # Two ridges may share an across-position provided they occupy
        # different stretches of the cross axis — otherwise partial spans can
        # only ever fill a fraction of the share target, since the spacing rule
        # caps how many positions exist. Echeloned ridges are also the more
        # natural shape.
        cands = [p for p in range(2, across - 2)
                 if all(abs(p - u) >= thick + 2
                        or start > ue or start + run < us
                        for (u, us, ue) in used)]
        if not cands:
            break
        pos = rng.choice(cands)
        used.append((pos, start, start + run))
        centre = pos
        for k in range(start, start + run):
            if rng.random() < jitter:
                centre += rng.choice((-1, 1))
            centre = max(1, min(across - 2, centre))
            for d in range(thick):
                p = centre + d - thick // 2
                coord = (p, k) if vertical else (k, p)
                h = m.get(coord)
                if h is not None and ok(h):
                    h.terrain = terrain


def _stamp_scatter(m, terrain, count, size_lo, size_hi, min_sep, ok, rng,
                   chain=0.0, chain_range=5, widen=0.0):
    """Isolated clusters, spaced at least `min_sep` apart. This is the Bleak
    Highlands primitive: peaks as local obstacles rather than as a wall.

    `chain` is the fraction of seeds that get joined to a nearby neighbour by
    a one-hex spur, turning some of the dots into short ridges. Pure scatter
    reads as decoration — every peak is walked around at no cost. A ridge two
    or three hexes long is the smallest thing an army has to actually plan
    against, and it is what stops the terrain being merely aesthetic.

    Chaining also changes the economy: mapgen._resources grants a mine only to
    a mountain component of >= 3 hexes, so joining singletons converts dead
    peaks into mine sites.
    """
    seeds = []
    guard = 0
    while len(seeds) < count and guard < 3000:
        guard += 1
        cands = [h.coord for h in m.all() if ok(h)]
        if not cands:
            break
        c = rng.choice(cands)
        if any(distance(c, s) < min_sep for s in seeds):
            continue
        seeds.append(c)
        _blob(m, c, rng.randint(size_lo, size_hi), terrain, ok, [], terrain)

    if chain > 0 and len(seeds) > 1:
        # Each peak may be joined ONCE. Without that cap the spurs cascade
        # transitively — a links to b, b links to c — and a scatter meant to
        # read as broken country grows a 20-hex ridge, which is the wall the
        # preset is specifically not supposed to have. Pairs and the occasional
        # triple are the target.
        linked = set()
        for a in seeds:
            if a in linked or rng.random() >= chain:
                continue
            near = [b for b in seeds
                    if b != a and b not in linked
                    and distance(a, b) <= chain_range]
            if not near:
                continue
            linked.add(a)
            linked.add(min(near, key=lambda q: distance(a, q)))
            b = min(near, key=lambda q: distance(a, q))
            cur, guard2 = a, 0
            while cur != b and guard2 < 12:      # straight spur, no meander
                guard2 += 1
                step = min((n.coord for n in m.neighbors(cur)),
                           key=lambda q: distance(q, b))
                if distance(step, b) >= distance(cur, b):
                    break
                h = m.get(step)
                if h is not None and ok(h):
                    h.terrain = terrain
                if widen and rng.random() < widen:
                    # occasional double-width in a ridge. A one-hex spur is
                    # sidestepped for free; a two-hex shoulder has to be walked
                    # around, which is the whole difference between decorative
                    # relief and terrain that costs an army tempo.
                    for nb in m.neighbors(step):
                        if ok(nb):
                            nb.terrain = terrain
                            break
                cur = step
    return len(seeds)


def _stamp_massif(m, terrain, count, size_lo, size_hi, min_sep, bbox,
                  keepout, ok, rng):
    """A few chunky, bounded massifs — Blighthold's shape.

    Compact blobs grown nearest-first, but refused any hex that would push the
    cluster's bounding box past `bbox` on either axis, so a massif stays a
    block of high ground rather than sprawling into a range. `keepout` is a
    radius around the board centre they may not seed in: mountains dumped in
    the middle cut the map in half and make the centre unplayable, whereas
    high ground toward the edges frames the ground people fight over.
    """
    mid = (m.width // 2, m.height // 2)
    seeds, guard = [], 0
    while len(seeds) < count and guard < 2000:
        guard += 1
        cands = [h.coord for h in m.all()
                 if ok(h) and distance(h.coord, mid) >= keepout]
        if not cands:
            break
        c = rng.choice(cands)
        if any(distance(c, s) < min_sep for s in seeds):
            continue
        seeds.append(c)

        want = rng.randint(size_lo, size_hi)
        if not ok(m.get(c)):
            continue
        m.get(c).terrain = terrain
        filled = {c}
        while len(filled) < want:
            lo_c = min(x[0] for x in filled); hi_c = max(x[0] for x in filled)
            lo_r = min(x[1] for x in filled); hi_r = max(x[1] for x in filled)
            frontier = set()
            for f in filled:
                for nb in m.neighbors(f):
                    if nb.coord in filled or not ok(nb):
                        continue
                    if (max(hi_c, nb.col) - min(lo_c, nb.col) >= bbox
                            or max(hi_r, nb.row) - min(lo_r, nb.row) >= bbox):
                        continue
                    frontier.add(nb.coord)
            if not frontier:
                break
            nxt = min(frontier, key=lambda q: distance(c, q))
            m.get(nxt).terrain = terrain
            filled.add(nxt)
    return len(seeds)


def _stamp_perimeter(m, terrain, count, length, width, depth, ok, rng,
                     jitter=0.30):
    """Long, thin ranges running PARALLEL to the board edge, set back from it.

    This is the map7 reading of Lenaveron: ranges that frame a region along its
    margins rather than crossing it. Each range starts inside a depth band from
    the nearest edge and walks tangentially — along the edge, not toward it —
    so it stays a rim feature instead of becoming a wall across the middle.
    """
    laid = 0
    for _ in range(count):
        band = [h.coord for h in m.all() if ok(h)
                and depth[0] <= min(h.col, m.width - 1 - h.col,
                                    h.row, m.height - 1 - h.row) <= depth[1]]
        if not band:
            break
        start = rng.choice(band)
        # nearest edge decides the axis; walk along it, never into the middle
        dists = {"w": start[0], "e": m.width - 1 - start[0],
                 "n": start[1], "s": m.height - 1 - start[1]}
        near = min(dists, key=dists.get)
        vertical = near in ("w", "e")
        step = rng.choice((-1, 1))
        cur = list(start)
        run = rng.randint(*length)
        for _ in range(run):
            for k in range(rng.randint(*width)):
                c = (cur[0], cur[1] + k) if vertical else (cur[0] + k, cur[1])
                h = m.get(c)
                if h is not None and ok(h):
                    h.terrain = terrain
                    laid += 1
            if vertical:
                cur[1] += step
                if rng.random() < jitter:
                    cur[0] += rng.choice((-1, 1))
            else:
                cur[0] += step
                if rng.random() < jitter:
                    cur[1] += rng.choice((-1, 1))
            if not m.in_bounds(tuple(cur)):
                break
    return laid


def _stamp_fringe(m, terrain, target, ok, rng, depth=3):
    """Push terrain to the board rim: the Glen of Pravak ring."""
    cands = [h for h in m.all() if ok(h)]
    cands.sort(key=lambda h: min(h.col, m.width - 1 - h.col,
                                 h.row, m.height - 1 - h.row))
    n = 0
    for h in cands:
        if n >= target:
            break
        d = min(h.col, m.width - 1 - h.col, h.row, m.height - 1 - h.row)
        if d > depth and n >= target * 0.6:
            break
        h.terrain = terrain
        n += 1
    return n


# ── housekeeping (substrate-aware) ───────────────────────────────────────────
def _cull_small(m, substrate, palette, exempt=(), min_node=mapgen.MIN_NODE):
    """Revert undersized clusters to plains.

    Two exemptions. The substrate is the background — eroding it would dissolve
    the matrix. And any terrain placed by SCATTER morphology is deliberately
    1-3 hexes, so culling below MIN_NODE would delete it as fast as it is
    placed; scatter and the cull are the same rule pointed in opposite
    directions, and scatter wins where a preset asked for it.
    """
    for terrain in ("forest", "wetland", "tundra"):
        if terrain == substrate or terrain not in palette or terrain in exempt:
            continue
        seen = set()
        for h in list(m.all()):
            if h.terrain == terrain and h.coord not in seen:
                comp = _component(m, h, terrain, seen)
                if len(comp) < min_node:
                    for c in comp:
                        m.get(c).terrain = "plains"


def _cap_components(m, cap, substrate, palette, exempt=()):
    """Erode oversized clusters from the edge. Substrate and scatter exempt."""
    for terrain in ("forest", "wetland", "tundra"):
        if terrain == substrate or terrain not in palette or terrain in exempt:
            continue
        seen = set()
        for h in list(m.all()):
            if h.terrain == terrain and h.coord not in seen:
                comp = set(_component(m, h, terrain, seen))
                while len(comp) > cap:
                    peri = [c for c in comp
                            if any(n.terrain == "plains" for n in m.neighbors(c))]
                    if not peri:
                        break
                    worst = max(peri, key=lambda c: sum(
                        1 for n in m.neighbors(c) if n.terrain == "plains"))
                    m.get(worst).terrain = "plains"
                    comp.discard(worst)


def _ensure_connectivity(m):
    """Every settlement must be reachable from every other over passable
    terrain. Where a band or fringe has sealed a region off, carve ONE
    single-hex corridor through it rather than dissolving the wall — the wall
    is the point, the narrows is the counterplay. Returns hexes carved.
    """
    pts = [s for settles in getattr(m, "settlements", []) for s in settles]
    if not pts:
        return 0
    carved, guard = 0, 0
    while guard < 20:
        guard += 1
        reach = _reachable(m, pts[0])
        orphan = next((s for s in pts if s not in reach), None)
        if orphan is None:
            break
        target = min(reach, key=lambda c: distance(orphan, c)) if reach else pts[0]
        carved += _carve_route(m, orphan, target, width=1)
    return carved


def _ensure_region_material(m, p, rng):
    """Every region must see >=2 distinct raw-material terrains within range 2
    of one of its settlements. Where a preset's own stamping did not deliver
    that, convert a nearby plains hex to whichever material terrain the
    PALETTE allows — unlike mapgen's version, which always reaches for water
    and would punch a hole in a landlocked preset.
    """
    # forest/wetland/tundra grow as small patches; mountain is the LAST resort
    # and is placed as a single hex. Adding a terrain to a preset's palette to
    # dodge this case would put it on every map of that region, whereas the
    # shortfall usually hits one region on one seed.
    order = [t for t in ("forest", "wetland", "tundra", "mountain")
             if t in p["palette"] and t != p["substrate"]]
    carved = getattr(m, "carved", set())
    sub = p["substrate"]
    look = lambda c: (sub if c in carved else m.get(c).terrain)
    for settles in getattr(m, "settlements", []):
        ring = {c for s in settles for c in
                [s] + [n.coord for n in m.neighbors(s)]}
        for _ in range(6):
            best = max(settles, key=lambda st: len(
                {look(h.coord) for h in m.within(st, 2)
                 if look(h.coord) in mapgen.MATERIAL_TERRAINS}))
            have = {look(h.coord) for h in m.within(best, 2)
                    if look(h.coord) in mapgen.MATERIAL_TERRAINS}
            if len(have) >= 2:
                break
            pick = next((t for t in order if t not in have), None)
            if not pick:
                break
            spots = [h.coord for h in m.within(best, 2)
                     if h.coord not in ring and h.terrain == "plains"]
            if not spots:
                break
            seed = max(spots, key=lambda c: distance(c, best))
            targets = ([seed] if pick == "mountain"
                       else [seed] + [n.coord for n in m.neighbors(seed)][:2])
            for c in targets:
                h = m.get(c)
                if h and h.terrain == "plains" and c not in ring:
                    h.terrain = pick


HILL_SEP = 4


def _mark_hills(m, min_sep=HILL_SEP):
    """Hills, thinned so no two sit within `min_sep` of each other.

    The raw rule — a plains hex ringed entirely by plains — measures how open
    the map is, not where the high ground is. It yields 9% of plains on Lost
    Woods and 44% on Hermit's Row, because any wide field is wall-to-wall
    "hill". Those are plateaus, not hills.

    So candidates are scored by how deep inside their own open ground they sit
    (distance to the nearest non-plains hex), the deepest is taken as that
    plateau's summit, and everything within `min_sep` of it is dropped. Repeat.
    A sparse map keeps nearly all its hills because they were already far
    apart; an open map collapses from a plateau to a handful of summits.
    """
    for h in m.all():
        h.tactical = None
    cand = [h.coord for h in m.all()
            if h.terrain == "plains" and len(m.neighbors(h.coord)) == 6
            and all(n.terrain == "plains" for n in m.neighbors(h.coord))]
    if not cand:
        return
    if min_sep <= 1:
        for c in cand:
            m.get(c).tactical = "hill"
        return

    # multi-source BFS from every non-plains hex gives each candidate's depth
    # in one pass; scoring each candidate against every obstruction instead is
    # O(candidates x obstructions) and dominated the whole generator.
    from collections import deque
    depth = {}
    dq = deque()
    for h in m.all():
        if h.terrain != "plains":
            depth[h.coord] = 0
            dq.append(h.coord)
    if not dq:
        for h in m.all():
            depth[h.coord] = 99
    while dq:
        c = dq.popleft()
        for nb in m.neighbors(c):
            if nb.coord not in depth:
                depth[nb.coord] = depth[c] + 1
                dq.append(nb.coord)

    ranked = sorted(cand, key=lambda c: (-depth.get(c, 99), c))
    kept = []
    for c in ranked:
        if all(distance(c, k) >= min_sep for k in kept):
            kept.append(c)
            m.get(c).tactical = "hill"


# ── resources ────────────────────────────────────────────────────────────────
def _resources(m, palette, res_min):
    """As mapgen._resources, but palette-aware. A terrain absent from the
    palette contributes nothing, and a raw material with no legal source is
    simply unavailable on this map — that is the point of a closed palette."""
    for h in m.all():
        h.resource = None

    for terrain in ("forest", "wetland", "tundra", "plains"):
        if terrain not in palette:
            continue
        prim, *rest = mapgen.RESOURCE_BY_TERRAIN[terrain]
        seen = set()
        for h in m.all():
            if h.terrain == terrain and h.coord not in seen:
                comp = _component(m, h, terrain, seen)
                if len(comp) < mapgen.MARK_MIN[terrain]:
                    continue
                types = [prim] + (rest if (len(comp) >= mapgen.BIG_NODE and rest) else [])
                for c, t in zip(_spread_picks(comp, len(types)), types):
                    m.get(c).resource = t

    if "mountain" in palette:
        seen = set()
        for h in m.all():
            if h.terrain == "mountain" and h.coord not in seen:
                comp = _component(m, h, "mountain", seen)
                if len(comp) < 3:
                    continue
                types = ["mine"] + (["quarry"] if len(comp) >= mapgen.BIG_NODE else [])
                for c, t in zip(_spread_picks(comp, len(types)), types):
                    m.get(c).resource = t

    for res, need in res_min.items():
        if need <= 0:
            continue
        have = sum(1 for h in m.all() if h.resource == res)
        if have >= need:
            continue
        if res == "mine":
            cands = [h.coord for h in m.all()
                     if h.terrain == "mountain" and not h.resource]
        elif res == "quarry":
            cands = [h.coord for h in m.all()
                     if h.terrain in ("tundra", "mountain") and not h.resource]
        else:
            terrains = tuple(t for t in mapgen.TOPUP_TERRAINS[res] if t in palette)
            cands = [h.coord for h in m.all()
                     if h.terrain in terrains and not h.resource]
        existing = [h.coord for h in m.all() if h.resource == res]
        cands.sort(key=lambda c: -min([distance(c, e) for e in existing], default=999))
        for c in cands:
            if have >= need:
                break
            m.get(c).resource = res
            have += 1


# ── validation ───────────────────────────────────────────────────────────────
PASSABLE = ("plains", "forest", "wetland", "tundra")


def _reachable(m, start, sea_hop=True):
    """Land hexes reachable under BASE movement.

    TERRAIN["Water"]: "Must end move after moving over 1 Water Territory (must
    end on land)." So a ONE-hex strait is crossable by any army with no
    infrastructure at all, and a two-hex gap is a hard wall until someone
    masters a Shipyard ("Water Territory treated as Grassland for movement").
    Bridges do NOT help here — they only apply "within Province".

    Hence: hop land -> water -> land, but never water -> water. Set
    sea_hop=False to measure strictly-contiguous landmass instead.
    """
    seen, stack = set(), [start]
    while stack:
        c = stack.pop()
        if c in seen:
            continue
        h = m.get(c)
        if not h or h.terrain not in PASSABLE:
            continue
        seen.add(c)
        for nb in m.neighbors(c):
            if nb.coord in seen:
                continue
            if nb.terrain in PASSABLE:
                stack.append(nb.coord)
            elif sea_hop and nb.terrain == "water":
                # a single water hex may be crossed only onto land
                for far in m.neighbors(nb.coord):
                    if far.terrain in PASSABLE and far.coord not in seen:
                        stack.append(far.coord)
    return seen


def validate(m, p):
    """Hard playability contract. Anything here that fails is a reseed, not a
    fixup — a preset that cannot satisfy these is mis-specified, and silently
    patching it is how you get a map that looks right and plays wrong."""
    v = []
    palette = p["palette"]
    res_min = {**mapgen.RESOURCE_MIN, **p.get("resource_min", {})}

    # 1. three distinct settlement sites per region
    for i, settles in enumerate(getattr(m, "settlements", [])):
        if len(set(settles)) < 3:
            v.append(f"region {i}: only {len(set(settles))} distinct settlements")
        for s in settles:
            if m.get(s).terrain in ("water", "mountain"):
                v.append(f"region {i}: settlement {s} on unchartable terrain")

    # 2. >=2 distinct raw-material terrains within range 2 of some settlement
    for i, settles in enumerate(getattr(m, "settlements", [])):
        carved = getattr(m, "carved", set())
        sub = p["substrate"]
        look = lambda c: (sub if c in carved else m.get(c).terrain)
        best = max((len({look(h.coord) for h in m.within(st, 2)
                         if look(h.coord) in mapgen.MATERIAL_TERRAINS})
                    for st in settles), default=0)
        if best < 2:
            v.append(f"region {i}: only {best} material terrain(s) within range 2")

    # 3. every settlement mutually reachable over passable terrain
    if p.get("sea_crossing", "base") == "shipyard":
        # Islands are separated on purpose. Each player must still be able to
        # walk between their OWN three settlements without a Shipyard;
        # reaching anyone else is what the Shipyard is for.
        for i, settles in enumerate(getattr(m, "settlements", [])):
            reach = _reachable(m, settles[0])
            if any(s not in reach for s in settles):
                v.append(f"region {i}: own settlements not mutually reachable")
    else:
        allset = [s for settles in getattr(m, "settlements", []) for s in settles]
        if allset:
            reach = _reachable(m, allset[0])
            orphans = [s for s in allset if s not in reach]
            if orphans:
                v.append(f"{len(orphans)} settlement(s) unreachable from region 0")

    # 3b. no water run wider than one hex where it isolates land. Water is
    # allowed to be a wall on purpose (Drakenheart), but the preset has to say
    # so via sea_crossing="shipyard"; otherwise a wide channel is a bug.
    if p.get("sea_crossing", "base") == "base":
        for h in m.all():
            if h.terrain != "water":
                continue
            runs = sum(1 for n in m.neighbors(h.coord) if n.terrain == "water")
            if runs >= 5 and 1 < h.col < m.width - 2 and 1 < h.row < m.height - 2:
                v.append("interior open water wider than a one-hex strait")
                break

    # 4. Hill (preset-toggleable; see the TERRAIN/RULES chartering drift)
    if p.get("require_hill") and not any(h.tactical == "hill" for h in m.all()):
        v.append("no Hill on the board")

    # 5. resource floors, after preset overrides
    have = Counter(h.resource for h in m.all() if h.resource)
    for res, need in res_min.items():
        if need > 0 and have[res] < need:
            v.append(f"resource {res}: {have[res]}/{need}")

    return v


# ── export / import ──────────────────────────────────────────────────────────
FORMAT_VERSION = 1
GENERATOR_VERSION = "0.1.0"

_T2C = {"plains": "p", "forest": "f", "wetland": "w", "tundra": "t",
        "mountain": "m", "water": "~"}
_C2T = {v: k for k, v in _T2C.items()}


def export_map(m, p, seed, violations=()):
    """Serialise a generated board to a plain dict.

    The GRID is the durable artifact, not the seed. A seed only reproduces a
    board against the exact generator that made it — retune a share or a walk
    temperature and the same seed yields something else. A stored grid still
    prints correctly a year later, which is what matters when a playtest needs
    to refer to *this* board.

    Terrain is one character per hex, packed row-major into one string per
    column. Hills are NOT stored: they are a pure function of terrain and are
    recomputed on import, so they can never disagree with the map.
    """
    return {
        "format": FORMAT_VERSION,
        "generator": GENERATOR_VERSION,
        "preset": p.get("name", "?"),
        "seed": seed,
        "width": m.width,
        "height": m.height,
        "players": p.get("players"),
        "substrate": p.get("substrate"),
        "borders": {k: list(v) for k, v in getattr(m, "borders", {}).items()},
        "terrain": ["".join(_T2C[m.get((c, r)).terrain] for r in range(m.height))
                    for c in range(m.width)],
        "resources": {f"{h.col},{h.row}": h.resource
                      for h in m.all() if h.resource},
        "regions": {f"{h.col},{h.row}": h.region
                    for h in m.all() if h.region is not None},
        "settlements": [[list(s) for s in reg]
                        for reg in getattr(m, "settlements", [])],
        "centers": [list(c) for c in getattr(m, "centers", [])],
        "settlement_range": getattr(m, "settlement_range", None),
        "art": p.get("art", {}),
        "violations": list(violations),
    }


def import_map(data):
    """Rebuild a HexMap from an exported dict. Round-trips exactly."""
    if data.get("format") != FORMAT_VERSION:
        raise ValueError(f"unsupported map format {data.get('format')!r}")
    m = HexMap.blank(data["width"], data["height"])
    for c, colstr in enumerate(data["terrain"]):
        for r, ch in enumerate(colstr):
            m.get((c, r)).terrain = _C2T[ch]
    for k, v in data.get("resources", {}).items():
        c, r = (int(x) for x in k.split(","))
        m.get((c, r)).resource = v
    for k, v in data.get("regions", {}).items():
        c, r = (int(x) for x in k.split(","))
        m.get((c, r)).region = v
    m.settlements = [[tuple(s) for s in reg]
                     for reg in data.get("settlements", [])]
    m.centers = [tuple(c) for c in data.get("centers", [])]
    m.settlement_range = data.get("settlement_range")
    m.borders = {k: tuple(v) for k, v in data.get("borders", {}).items()}
    _mark_hills(m)                       # derived, never stored
    return m


# ── pipeline ─────────────────────────────────────────────────────────────────
def _build(p, seed):
    rng = random.Random(seed)
    random.seed(seed)
    m = HexMap.blank(p["width"], p["height"], "plains")
    m._rng = rng
    m.reserved = set()
    palette = p["palette"]
    substrate = p["substrate"]
    buffers = {frozenset(b) for b in p.get("buffers", [])}
    tot = p["width"] * p["height"]

    bw = _resolve_borders(p.get("border", 0), p["players"], rng,
                          p["width"], p["height"],
                          mirror=p.get("border_mirror", "ns"))
    _border_water(m, bw)
    m.borders = bw
    m.rim = {h.coord for h in m.all() if h.terrain == "water"}

    # settlements first, on open ground — legality never fights the matrix
    anchors = mapgen._place_regions(m, p, rng)
    m.anchors = anchors
    m.settlement_range = p["settlement_range"]

    carve = p.get("carve")
    m.carved = set()
    if substrate == "water":
        # Sea substrate: pour ocean, then LIFT the land back out around the
        # settlements. Islands may be genuinely separated by deep water — the
        # preset says sea_crossing="shipyard" and the validator relaxes
        # mutual reachability accordingly.
        _pour_substrate(m, "water", m.reserved)
        c = carve or {}
        groups = _group_regions(m, rng.randint(*c.get("islands", (3, 3))))
        _lift_islands(m, groups, c.get("island_size", (60, 90)), rng,
                      islets=c.get("islets", (0, 0)),
                      land_target=c.get("land_target", 0.55),
                      gap=c.get("gap", (2, 4)))
    elif substrate != "plains":
        _pour_substrate(m, substrate, m.reserved)
        cr = (carve or {}).get("clearing_radius", 2)
        w = (carve or {}).get("width", 1)
        for settles in m.settlements:
            for s in settles:
                _carve_clearing(m, s, cr)
        # Long-haul network spans REGION CENTRES, not every settlement.
        # Spanning 18 settlements individually carves ~100 hexes of corridor
        # and drowns the substrate; the three settlements of a region are
        # 5-7 apart and only need a short local link to their own centre.
        _route_network(m, list(m.centers), (carve or {}).get("routes", 0), w,
                       temp=(carve or {}).get("temp", 0.8))
        for settles, ctr in zip(m.settlements, m.centers):
            for st in settles:
                _carve_route(m, st, ctr, 1, temp=0.5, rng=rng)
        mz = (carve or {}).get("mazes")
        if mz:
            _carve_maze(m, rng.randint(*mz), rng,
                        temp=(carve or {}).get("maze_temp", 1.7),
                        junction_p=(carve or {}).get("junction_p", 0.5))

    # accent terrain overwrites the substrate only (never carved routes,
    # never the settlement rings), so the connective network survives
    # Rivers are substrate-agnostic: any preset may declare them, matrix or
    # not. Keeping this inside the matrix branch silently denied rivers to
    # every plains preset, which is why Lenaveron was faking them with
    # straight channel bands.
    rv = (carve or {}).get("rivers")
    if rv and substrate != "water":
        _carve_river(m, rng.randint(*rv), rng,
                     temp=(carve or {}).get("river_temp", 1.9))
        _thin_water(m, getattr(m, "rim", set()))

    accent_over = "plains" if substrate == "water" else substrate

    def free(h):
        return (h is not None and h.terrain == accent_over
                and h.coord not in m.reserved)

    for terrain, share in sorted(p.get("shares", {}).items(),
                                 key=lambda kv: -kv[1]):
        if terrain not in palette or terrain == substrate:
            continue
        target = int(round(share * tot))
        morph = p.get("morphology", {}).get(terrain, "blob")
        if morph == "band":
            bd = list(p.get("band", {}).get(terrain, ("e", 0.10, 0.35)))
            sp = bd[3] if len(bd) > 3 else 1.0
            _stamp_band(m, terrain, target, bd[0], bd[1], bd[2], free, rng,
                        span=sp)
        elif morph == "scatter":
            sc = list(p.get("scatter", {}).get(terrain, (12, 1, 3, 3)))
            n, lo, hi, sep = sc[:4]
            ch = sc[4] if len(sc) > 4 else 0.0
            crange = sc[5] if len(sc) > 5 else 5
            wd = sc[6] if len(sc) > 6 else 0.0
            _stamp_scatter(m, terrain, n, lo, hi, sep, free, rng,
                           chain=ch, chain_range=crange, widen=wd)
        elif morph == "channels":
            # Water bands one hex thick. Thicker than one would be an
            # uncrossable wall at base movement, so the thickness is pinned
            # regardless of what the preset asks for.
            bd = list(p.get("band", {}).get(terrain, ("e", 0.0, 0.5)))
            _stamp_band(m, terrain, target, bd[0], 1.0 / max(m.width, m.height),
                        bd[2], free, rng,
                        span=(bd[3] if len(bd) > 3 else 1.0))
        elif morph == "massif":
            ms = p.get("massif", {}).get(terrain, (5, 8, 14, 7, 4, 6))
            _stamp_massif(m, terrain, ms[0], ms[1], ms[2], ms[3], ms[4], ms[5],
                          free, rng)
        elif morph == "perimeter":
            pm = p.get("perimeter", {}).get(terrain, (4, (8, 16), (1, 2), (1, 6)))
            _stamp_perimeter(m, terrain, pm[0], tuple(pm[1]), tuple(pm[2]),
                             tuple(pm[3]), free, rng)
        elif morph == "fringe":
            _stamp_fringe(m, terrain, target, free, rng)
        else:
            _stamp_blobs(m, terrain, target, free, buffers, substrate, rng)

    scattered = tuple(t for t, mo in p.get("morphology", {}).items()
                      if mo == "scatter")
    _cull_small(m, substrate, palette, exempt=scattered)
    _cap_components(m, p["cluster_cap"], substrate, palette, exempt=scattered)

    # settlements must survive every stamp
    for settles in m.settlements:
        for s in settles:
            h = m.get(s)
            if h.terrain in ("water", "mountain"):
                h.terrain = "plains"

    if p.get("sea_crossing", "base") != "shipyard":
        _ensure_connectivity(m)
    else:
        for settles in m.settlements:            # link each island internally
            for st in settles[1:]:
                if st not in _reachable(m, settles[0]):
                    _carve_route(m, st, settles[0], 1, temp=0.6, rng=rng)
    _ensure_region_material(m, p, rng)
    _mark_hills(m, p.get("hill_sep", HILL_SEP))
    _resources(m, palette, {**mapgen.RESOURCE_MIN, **p.get("resource_min", {})})
    return m


def generate_region(region, *, attempts=12, **over):
    """Generate a map in the style of `region`. Reseeds on validation failure.

    Returns (map, preset, violations). A non-empty violations list means every
    attempt failed and the best-scoring board is returned anyway, so the caller
    can see what the preset cannot satisfy rather than shipping a quiet lie.
    """
    p = {**mapgen.PARAMS, **region_presets.get(region), **over}
    best, best_v = None, None
    for k in range(attempts):
        m = _build(p, p["seed"] + k * 1009)
        v = validate(m, p)
        if not v:
            return m, p, []
        if best_v is None or len(v) < len(best_v):
            best, best_v = m, v
    return best, p, best_v


def report(m, p, v):
    tot = m.width * m.height
    terr = Counter(h.terrain for h in m.all())
    res = Counter(h.resource for h in m.all() if h.resource)
    lines = [f"{p['name']}  {m.width}x{m.height} = {tot} hexes  "
             f"substrate={p['substrate']}  players={p['players']}"]
    lines.append("  terrain: " + ", ".join(
        f"{k} {vv} ({vv*100//tot}%)" for k, vv in terr.most_common()))
    hills = sum(1 for h in m.all() if h.tactical == "hill")
    lines.append(f"  hills: {hills}   (require_hill={p['require_hill']})")
    lines.append("  resources: " + (", ".join(
        f"{k} {vv}" for k, vv in sorted(res.items())) or "none"))
    absent = sorted(set(mapgen.RESOURCE_MIN) - set(res))
    if absent:
        lines.append("  UNAVAILABLE: " + ", ".join(absent))
    lines.append("  violations: " + (", ".join(v) if v else "none"))
    return "\n".join(lines)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("region", nargs="?", default=None)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--players", type=int, default=6)
    ap.add_argument("--width", type=int, default=32)
    ap.add_argument("--height", type=int, default=26)
    ap.add_argument("--export", metavar="FILE.json",
                    help="write the generated board to JSON")
    a = ap.parse_args()
    todo = [a.region] if a.region else region_presets.names()
    for name in todo:
        m, p, v = generate_region(name, seed=a.seed, players=a.players,
                                  width=a.width, height=a.height)
        print(report(m, p, v))
        if a.export:
            import json
            with open(a.export, "w") as fh:
                json.dump(export_map(m, p, a.seed, v), fh, separators=(",", ":"))
            print(f"  exported -> {a.export}")
        print()
