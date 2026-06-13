"""mapgen.py — procedural Renown map generator.

Pipeline: plains fill -> coastline -> rivers -> lakes -> mountain ranges ->
forests -> wetlands -> tundra -> starting regions -> resources. All tunables in
PARAMS. Produces a HexMap (the C1 territory graph). Deterministic per seed.
"""
from __future__ import annotations
import random, math
from hexmap import HexMap, neighbors, distance

# cube direction vectors (flat-top), for consistent directional walks
CUBE_DIRS = [(+1, -1, 0), (+1, 0, -1), (0, +1, -1),
             (-1, +1, 0), (-1, 0, +1), (0, -1, +1)]


def _cube(col, row):
    x = col; z = row - (col - (col & 1)) // 2; return (x, -x - z, z)


def _offset(x, y, z):
    return (x, z + (x - (x & 1)) // 2)


PARAMS = dict(
    width=32, height=26, players=6, seed=7,
    settlement_range=5,              # min hex distance between settlements
    settlement_range_max=7,          # max hex distance between settlements
    first_settle_range=4,            # first settlement within this of the corner
    coast_prob=0.18,                 # chance an edge hex is water (rare; see guarantee)
    rivers=(2, 3), river_len=(10, 18), river_branch=0.10,
    lakes=(2, 4), lake_size=(2, 4),
    ranges=(0, 1), range_len=(5, 9), range_width2=0.35,  # P(widen the band)
    forests=(7, 11), forest_size=(7, 17),
    wetlands=(2, 4), wetland_size=(12, 21),
    tundras=(2, 3), tundra_size=(12, 20),
    region_radius=4, region_core=2,  # core forced buildable
    cluster_cap=30,                  # max hexes in one same-terrain cluster
    plains_target=0.50,              # stop stamping when plains <= this
    resource_density=0.075,          # global, on top of per-region guarantees
)


# ── primitive shapers ──────────────────────────────────────────────────────
FEATURES = ("mountain", "water")        # may abut other terrain (per prob rule)
LAND_BIOMES = ("forest", "wetland", "tundra")   # kept apart by plains corridors


def _clear(m, coord, terrain, own=None):
    """Placement legality + adjacency rule.

    * Two DIFFERENT land biomes (forest/wetland/tundra) must stay one plains hex
      apart -> the plains corridors between them are the chokepoints.
    * Mountains and water (features) MAY touch other terrain. Being alone, or
      adjacent on a single side, is always allowed; adjacent on MORE than one
      side is half as likely. Same applies to a land biome touching a feature.
    Same-terrain and own-cluster neighbours are always fine; plains always fine.
    """
    own = own or set()
    rng = getattr(m, "_rng", random)
    feat_adj = 0
    for nb in m.neighbors(coord):
        if nb.terrain == "plains" or nb.terrain == terrain or nb.coord in own:
            continue
        if terrain in LAND_BIOMES and nb.terrain in LAND_BIOMES:
            return False                       # different biome -> strict buffer
        feat_adj += 1                          # a feature touch (mtn/water)
    if feat_adj <= 1:
        return True                            # alone or one side: fine
    return rng.random() < 0.5                  # more than one side: half as likely


def _blob(m, start, size, terrain, over, rng):
    h0 = m.get(start)
    filled = set()
    if not h0 or h0.terrain not in over or not _clear(m, start, terrain, filled):
        return 0
    h0.terrain = terrain
    filled.add(start)
    frontier = [n.coord for n in m.neighbors(start)]
    placed = 1
    while frontier and placed < size:
        c = frontier.pop(rng.randrange(len(frontier)))
        h = m.get(c)
        if c in filled or not h or h.terrain not in over or not _clear(m, c, terrain, filled):
            continue
        h.terrain = terrain
        filled.add(c)
        placed += 1
        frontier += [n.coord for n in m.neighbors(c) if n.coord not in filled]
    return placed


def _walk(m, start, direction, length, terrain, over, rng, width2=0.0):
    cur = _cube(*start)
    laid = set()
    n = 0
    res = getattr(m, "reserved", set())
    for _ in range(length):
        off = _offset(*cur)
        if not m.in_bounds(off):
            break
        h = m.get(off)
        if ((h.terrain in over or off in laid) and off not in res
                and _clear(m, off, terrain, laid)):
            h.terrain = terrain
            laid.add(off)
            n += 1
            if width2 and rng.random() < width2:           # widen the band
                added = 0
                for nb in m.neighbors(off):
                    if (nb.terrain in over and nb.coord not in res
                            and _clear(m, nb.coord, terrain, laid)):
                        nb.terrain = terrain; laid.add(nb.coord); added += 1
                        if added >= 2:
                            break
        d = direction
        if rng.random() < 0.35:                            # wobble +-1 dir
            d = (direction + rng.choice((-1, 1))) % 6
        dx, dy, dz = CUBE_DIRS[d]
        cur = (cur[0] + dx, cur[1] + dy, cur[2] + dz)
    return n


# ── pipeline stages ─────────────────────────────────────────────────────────
def _coastline(m, p, rng):
    for h in m.all():
        edge = h.col in (0, m.width - 1) or h.row in (0, m.height - 1)
        if edge and rng.random() < p["coast_prob"]:
            h.terrain = "water"


def _rivers(m, p, rng):
    for _ in range(rng.randint(*p["rivers"])):
        # start on a water edge, head inward across the map
        start = (rng.randint(0, m.width - 1), rng.choice([0, m.height - 1]))
        direction = 5 if start[1] == 0 else 2              # head inward (down/up)
        _walk(m, start, direction, rng.randint(*p["river_len"]),
              "water", ("plains", "forest", "wetland", "tundra"), rng)
        if rng.random() < p["river_branch"]:
            _walk(m, start, (direction + 1) % 6, rng.randint(6, 14),
                  "water", ("plains", "forest"), rng)


def _lakes(m, p, rng):
    for _ in range(rng.randint(*p["lakes"])):
        c = (rng.randint(2, m.width - 3), rng.randint(2, m.height - 3))
        _blob(m, c, rng.randint(*p["lake_size"]), "water", ("plains", "wetland"), rng)


def _dot(u, v):
    return u[0] * v[0] + u[1] * v[1] + u[2] * v[2]


def _perp_dir(a, b):
    """The CUBE_DIRS index most perpendicular to the a->b line."""
    va, vb = _cube(*a), _cube(*b)
    v = (vb[0] - va[0], vb[1] - va[1], vb[2] - va[2])
    return min(range(6), key=lambda d: abs(_dot(CUBE_DIRS[d], v)))


def _ranges(m, p, rng, anchors):
    """Mountain ranges as natural separators: a wall on the midpoint between
    each anchor and its nearest neighbour, walked roughly perpendicular to the
    line joining them (both directions), longer + thicker. Plus a couple of
    free-roaming ranges for organic relief."""
    over = ("plains",)
    pairs = set()
    for i, a in enumerate(anchors):
        order = sorted((j for j in range(len(anchors)) if j != i),
                       key=lambda j: distance(a, anchors[j]))
        for j in order[:1]:               # nearest neighbour only
            pairs.add(tuple(sorted((i, j))))
    for i, j in pairs:
        a, b = anchors[i], anchors[j]
        mid = ((a[0] + b[0]) // 2, (a[1] + b[1]) // 2)
        d = _perp_dir(a, b)
        L = rng.randint(*p["range_len"])
        _walk(m, mid, d, L, "mountain", over, rng, width2=p["range_width2"])
        _walk(m, mid, (d + 3) % 6, L, "mountain", over, rng, width2=p["range_width2"])
    for _ in range(rng.randint(*p["ranges"])):
        c = (rng.randint(3, m.width - 4), rng.randint(3, m.height - 4))
        _walk(m, c, rng.randrange(6), rng.randint(*p["range_len"]),
              "mountain", over, rng, width2=p["range_width2"])


def _scatter_blobs(m, p, key_n, key_sz, terrain, over, rng, bias=None):
    for _ in range(rng.randint(*p[key_n])):
        if bias == "water":                                # start adjacent to water
            cands = [h for h in m.all() if h.terrain == "plains"
                     and any(n.terrain == "water" for n in m.neighbors(h.coord))]
        elif bias == "cold":                               # top/bottom strips
            cands = [h for h in m.all() if h.terrain == "plains"
                     and (h.row < m.height * 0.22 or h.row > m.height * 0.78)]
        else:
            cands = [h for h in m.all() if h.terrain == "plains"]
        if not cands:
            continue
        c = rng.choice(cands).coord
        _blob(m, c, rng.randint(*p[key_sz]), terrain, over, rng)


# ── center zones (wetland fingers / tundra circles, outside regions) ─────────
def _free_plain(h):
    return h.terrain == "plains" and h.region is None


def _blob_compact(m, seed, size, terrain, ok=_free_plain):
    """Circular zone: always annex the frontier hex nearest the seed."""
    if not ok(m.get(seed)) or not _clear(m, seed, terrain, set()):
        return 0
    m.get(seed).terrain = terrain
    filled = {seed}
    placed = 1
    while placed < size:
        frontier = set()
        for c in filled:
            for nb in m.neighbors(c):
                if nb.coord not in filled and ok(nb) and _clear(m, nb.coord, terrain, filled):
                    frontier.add(nb.coord)
        if not frontier:
            break
        nxt = min(frontier, key=lambda c: distance(seed, c))
        m.get(nxt).terrain = terrain
        filled.add(nxt); placed += 1
    return placed


def _blob_fingers(m, seed, size, terrain, rng, ok=_free_plain):
    """Tendrilled zone: several directional fingers that wander and branch."""
    if not ok(m.get(seed)) or not _clear(m, seed, terrain, set()):
        return 0
    m.get(seed).terrain = terrain
    filled = {seed}
    placed = 1
    heads = [(seed, rng.randrange(6)) for _ in range(rng.randint(3, 5))]
    while placed < size and heads:
        nxt_heads = []
        for cur, dirn in heads:
            if placed >= size:
                break
            d = dirn if rng.random() < 0.7 else (dirn + rng.choice((-1, 1))) % 6
            x, y, z = _cube(*cur)
            dx, dy, dz = CUBE_DIRS[d]
            nc = _offset(x + dx, y + dy, z + dz)
            if (m.in_bounds(nc) and nc not in filled and ok(m.get(nc))
                    and _clear(m, nc, terrain, filled)):
                m.get(nc).terrain = terrain
                filled.add(nc); placed += 1
                nxt_heads.append((nc, d))
                if rng.random() < 0.22:                      # branch a new finger
                    nxt_heads.append((nc, (d + rng.choice((-1, 1))) % 6))
        heads = nxt_heads
    return placed


def _center_zones(m, p, rng):
    """Add variety to the central plains: tundra circles, wetland fingers, and
    forest copses. Converts a fraction of ALL central plains (region plains
    included — forest/wetland/tundra stay buildable so starts remain playable).
    Plains remain the majority."""
    lo, hi = 0.18, 0.82

    def is_central_plain(h):
        return (h is not None and h.terrain == "plains"
                and lo * m.width < h.col < hi * m.width
                and lo * m.height < h.row < hi * m.height)

    central = [h for h in m.all() if is_central_plain(h)]
    cn = len(central)
    if cn < 6:
        return

    # Pre-space cluster seeds across the central band (farthest-point spread)
    # so each biome gets its own territory and none starves competing for
    # leftovers. Seeds are assigned to terrains round-robin.
    pool = [h.coord for h in central]
    k = max(4, cn // 10)
    seeds = [rng.choice(pool)]
    while len(seeds) < k:
        nxt = max(pool, key=lambda c: min(distance(c, s) for s in seeds))
        if min(distance(nxt, s) for s in seeds) < 2:
            break
        seeds.append(nxt)

    order = ("wetland", "forest", "tundra")
    for i, sd in enumerate(seeds):
        terrain = order[i % len(order)]
        if not is_central_plain(m.get(sd)):
            valid = [h.coord for h in m.all() if is_central_plain(h)]
            if not valid:
                break
            sd = min(valid, key=lambda c: distance(c, sd))
        want = rng.randint(12, 20)
        _blob_compact(m, sd, want, terrain, ok=is_central_plain)


# ── starting regions ─────────────────────────────────────────────────────────
def _place_regions(m, p, rng):
    n = p["players"]
    # balanced anchor layouts per player count (fractions of width/height)
    layouts = {
        1: [(0.5, 0.5)],
        2: [(0.18, 0.5), (0.82, 0.5)],
        3: [(0.18, 0.2), (0.82, 0.2), (0.5, 0.82)],
        4: [(0.16, 0.18), (0.84, 0.18), (0.16, 0.82), (0.84, 0.82)],
        5: [(0.16, 0.18), (0.84, 0.18), (0.16, 0.82), (0.84, 0.82), (0.5, 0.5)],
        6: [(0.16, 0.2), (0.5, 0.16), (0.84, 0.2),
            (0.16, 0.8), (0.5, 0.84), (0.84, 0.8)],
        7: [(0.16, 0.2), (0.5, 0.16), (0.84, 0.2),
            (0.16, 0.8), (0.5, 0.84), (0.84, 0.8), (0.5, 0.5)],
    }
    fracs = layouts.get(n, layouts[6])[:n]
    slots = [(int(m.width * fc), int(m.height * fr)) for (fc, fr) in fracs]
    anchors = []
    for (c, r) in slots:
        c = min(m.width - 3, max(2, c + rng.randint(-1, 1)))
        r = min(m.height - 3, max(2, r + rng.randint(-1, 1)))
        anchors.append((c, r))

    SEP = p["settlement_range"]           # min distance between settlements (5)
    SMAX = p["settlement_range_max"]      # max distance between settlements (7)
    FIRST = p["first_settle_range"]       # capital within this of the board corner (4)
    buildable = lambda c: (m.in_bounds(c)
                           and m.get(c).terrain not in ("water", "mountain"))
    m.settlements, m.centers = [], []

    for rid, (a, (fx, fy)) in enumerate(zip(anchors, fracs)):
        # corner target: the board-corner hex for this region's quadrant.
        # middle-edge regions (e.g. 6p top-centre) have no corner -> use anchor.
        if abs(fx - 0.5) < 0.12 or abs(fy - 0.5) < 0.12:
            corner = a
        else:
            corner = (0 if fx < 0.5 else m.width - 1,
                      0 if fy < 0.5 else m.height - 1)

        # capital: nearest fully-interior hex to the corner (all 6 neighbours
        # in-bounds), so a complete ring can surround it; force that ring plains.
        interior = [h.coord for h in m.within(corner, FIRST + 1)
                    if len(m.neighbors(h.coord)) == 6]
        cap = min(interior, key=lambda c: distance(c, corner)) if interior else corner
        for c in [cap] + [n.coord for n in m.neighbors(cap)]:
            m.get(c).terrain = "plains"

        def pick(existing):
            # buildable hex within [SEP, SMAX] of every existing settlement,
            # nearest the corner so the cluster stays cornered.
            cells = [h.coord for h in m.within(corner, FIRST + SMAX)
                     if buildable(h.coord)
                     and all(SEP <= distance(h.coord, o) <= SMAX for o in existing)]
            return min(cells, key=lambda c: distance(c, corner) + rng.random()) if cells else None

        s2 = pick([cap])
        s3 = pick([cap, s2]) if s2 else None
        if s2 is None:
            s2 = cap
        if s3 is None:
            s3 = s2
        settles = [cap, s2, s3]

        for s in settles:                 # settlements must sit on buildable land
            h = m.get(s)
            if h.terrain in ("water", "mountain"):
                h.terrain = "plains"
            h.region = rid

        center = (round(sum(s[0] for s in settles) / 3),
                  round(sum(s[1] for s in settles) / 3))
        m.settlements.append(settles)
        m.centers.append(center)

        # keep each settlement spot open (1-hex ring) so it isn't buried
        for s in settles:
            for h in m.within(s, 1):
                m.reserved.add(h.coord)
        # region membership tag around the triangle
        for s in settles:
            for h in m.within(s, p["region_core"]):
                if h.region is None and h.terrain != "water":
                    h.region = rid
    return anchors


# ── resources ────────────────────────────────────────────────────────────────
def _near(m, h, terrain):
    return any(n.terrain == terrain for n in m.neighbors(h.coord))


def _component(m, start, terrain, visited):
    """Connected component of one terrain type (flood fill)."""
    comp, stack = [], [start.coord]
    while stack:
        c = stack.pop()
        if c in visited:
            continue
        h = m.get(c)
        if not h or h.terrain != terrain:
            continue
        visited.add(c); comp.append(c)
        for nb in m.neighbors(c):
            if nb.coord not in visited:
                stack.append(nb.coord)
    return comp


MIN_NODE = 5    # no terrain cluster smaller than this (culled to plains)
BIG_NODE = 16   # large clusters drop BOTH their raw materials
# size a cluster must reach to DROP a raw material (separate from the cull min);
# forest/wetland set high so forestry stays scarce despite many woods
MARK_MIN = {"forest": 12, "wetland": 12, "tundra": 5, "plains": 5}

# raw materials a terrain can drop (primary, secondary), per renown_data.TERRAIN
RESOURCE_BY_TERRAIN = {
    "plains":   ("arable", "apiary"),
    "forest":   ("forestry", "apiary"),
    "wetland":  ("forestry",),            # peat unused (no marker type)
    "tundra":   ("quarry", "salt"),
    "mountain": ("mine", "quarry"),
}
RESOURCE_MIN = {"mine": 3, "quarry": 3, "arable": 3, "forestry": 3,
                "apiary": 2, "salt": 2}

# canonical render attributes per resource (border colour + icon asset)
RESOURCE_COLOR = {"mine": "#161616", "quarry": "#8a3b2e", "arable": "#7a4f2a",
                  "forestry": "#2f5d2f", "apiary": "#e8c020", "salt": "#ece6d6"}
RESOURCE_ICON = {"mine": "ore", "quarry": "stone", "arable": "grain",
                 "forestry": "wood", "apiary": "apiary", "salt": "salt"}
# where a shortfall can be topped up
TOPUP_TERRAINS = {"arable": ("plains",), "apiary": ("plains", "forest"),
                  "forestry": ("forest", "wetland"), "salt": ("tundra",),
                  "quarry": ("tundra",), "mine": ()}


def _cap_components(m, cap, terrains=("forest", "wetland", "tundra")):
    """No single connected same-terrain cluster exceeds `cap` hexes. Excess is
    eroded from the cluster edge back to plains (widening the chokepoints).
    Water is exempt (sea border / river network)."""
    for terrain in terrains:
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



def _seed_score(m, coord, terrain):
    """Bias seed placement: wetland near water, tundra to cold strips."""
    h = m.get(coord)
    s = 0.0
    if terrain == "wetland" and any(n.terrain == "water" for n in m.neighbors(coord)):
        s += 3.0
    if terrain == "tundra" and (h.row < m.height * 0.25 or h.row > m.height * 0.75):
        s += 2.0
    return s


def _fill_to_target(m, p, rng):
    """Additive fill: from a (mostly) plains board, keep stamping land-biome
    clusters that satisfy the cross-family plains buffer and the size cap,
    cycling terrains and spreading each from its own kind, until plains drops
    into the target band. Bigger clusters => fewer stamps => reaches target."""
    tot = m.width * m.height
    target = p["plains_target"]
    cap = p["cluster_cap"]
    types = ["forest", "wetland", "tundra"]
    ti = 0
    misses = 0
    guard = 0
    is_plain = lambda h: (h is not None and h.terrain == "plains"
                          and h.coord not in m.reserved)
    while guard < 1500 and misses < len(types):
        guard += 1
        if m.count("plains") / tot <= target:
            break
        terrain = types[ti % len(types)]; ti += 1
        cands = [h.coord for h in m.all()
                 if h.terrain == "plains" and h.coord not in m.reserved
                 and _clear(m, h.coord, terrain)]
        if not cands:
            misses += 1
            continue
        misses = 0
        existing = [h.coord for h in m.all() if h.terrain == terrain]
        sample = rng.sample(cands, min(len(cands), 60))
        if existing:                      # spread from same-terrain, plus bias
            seed = max(sample, key=lambda c: min(distance(c, e) for e in existing)
                       + _seed_score(m, c, terrain))
        else:
            seed = max(sample, key=lambda c: _seed_score(m, c, terrain) + rng.random())
        want = rng.randint(cap - 8, cap)
        _blob_compact(m, seed, want, terrain, ok=is_plain)


def _ensure_biomes(m, rng, terrains=("forest", "wetland", "tundra"), size=7):
    """Safety net: if a biome was wiped (small clusters culled), force one
    compact patch on the most open plains so every terrain type appears."""
    for terrain in terrains:
        if m.count(terrain) > 0:
            continue
        plains = [h.coord for h in m.all()
                  if h.terrain == "plains" and h.coord not in m.reserved]
        if not plains:
            return
        # prefer the most buffer-clear spot
        plains.sort(key=lambda c: (not _clear(m, c, terrain),
                                   -sum(1 for n in m.neighbors(c) if n.terrain == "plains")))
        seed = plains[0]
        got = _blob_compact(m, seed, size, terrain,
                            ok=lambda h: (h is not None and h.terrain == "plains"
                                          and h.coord not in m.reserved))
        if got == 0:                      # buffer blocked everywhere; place raw
            m.get(seed).terrain = terrain
            for nb in m.neighbors(seed)[:max(0, size - 1)]:
                if nb.terrain == "plains" and nb.coord not in m.reserved:
                    nb.terrain = terrain


MATERIAL_TERRAINS = ("forest", "mountain", "tundra", "wetland", "water")


def _ensure_region_material(m, p):
    """Every starting region needs a raw-material source within range 2 of its
    settlements. If none (only bare plains nearby), open a water board-edge hex
    so the player can take the water/fishing route."""
    for settles in m.settlements:
        cap = settles[0]
        ring = {cap} | {n.coord for n in m.neighbors(cap)}
        reach = set()
        for s in settles:
            for h in m.within(s, 2):
                reach.add(h.coord)
        if any(m.get(c).terrain in MATERIAL_TERRAINS for c in reach):
            continue
        # don't disturb the capital's plains ring; prefer a board edge
        pool0 = [c for c in reach if c not in ring]
        edge = [c for c in pool0
                if c[0] in (0, m.width - 1) or c[1] in (0, m.height - 1)]
        pool = edge or pool0 or list(reach)
        target = min(pool, key=lambda c: min(distance(c, s) for s in settles))
        m.get(target).terrain = "water"


def _carve_region_exits(m, p):
    """Guarantee at least one grassland chokepoint OUT of each region: if a
    region's plains aren't connected to the main plains body, carve a 1-wide
    plains corridor from its capital toward it via an in-bounds greedy walk."""
    seen, comps = set(), []
    for h in m.all():
        if h.terrain == "plains" and h.coord not in seen:
            comps.append(_component(m, h, "plains", seen))
    if not comps:
        return
    big = set(max(comps, key=len))
    for settles in m.settlements:
        cap = settles[0]
        touch = any(c in big
                    for s in settles
                    for c in [s] + [n.coord for n in m.neighbors(s)])
        if touch:
            continue
        target = min(big, key=lambda c: distance(cap, c))
        cur, guard = cap, 0
        while cur not in big and guard < 200:
            guard += 1
            m.get(cur).terrain = "plains"
            nbrs = [n.coord for n in m.neighbors(cur)]   # in-bounds only
            if not nbrs:
                break
            cur = min(nbrs, key=lambda c: distance(c, target))


def _cull_small(m):
    """No forest/wetland/tundra cluster smaller than MIN_NODE — revert to plains."""
    for terrain in ("forest", "wetland", "tundra"):
        seen = set()
        for h in list(m.all()):
            if h.terrain == terrain and h.coord not in seen:
                comp = _component(m, h, terrain, seen)
                if len(comp) < MIN_NODE:
                    for c in comp:
                        m.get(c).terrain = "plains"


def _spread_picks(comp, k):
    picks = [min(comp, key=lambda c: sum(distance(c, x) for x in comp))]
    while len(picks) < k and len(picks) < len(comp):
        picks.append(max(comp, key=lambda c: min(distance(c, q) for q in picks)))
    return picks


def _resources(m, p, rng):
    """1 raw material per major cluster; BOTH if large. Mountains (>=3) give
    mine (+quarry if large) on adjacent buildable hexes. Then top up to the
    global minimums (>=3 each; salt/apiary >=2)."""
    for h in m.all():
        h.resource = None
    # land clusters
    for terrain in ("forest", "wetland", "tundra", "plains"):
        prim, *rest = RESOURCE_BY_TERRAIN[terrain]
        seen = set()
        for h in m.all():
            if h.terrain == terrain and h.coord not in seen:
                comp = _component(m, h, terrain, seen)
                if len(comp) < MARK_MIN[terrain]:
                    continue
                types = [prim] + (rest if (len(comp) >= BIG_NODE and rest) else [])
                for c, t in zip(_spread_picks(comp, len(types)), types):
                    m.get(c).resource = t
    # mountain ranges (>=3): mine on the mountain hex itself; +quarry if large
    seen = set()
    for h in m.all():
        if h.terrain == "mountain" and h.coord not in seen:
            comp = _component(m, h, "mountain", seen)
            if len(comp) < 3:
                continue
            types = ["mine"] + (["quarry"] if len(comp) >= BIG_NODE else [])
            for c, t in zip(_spread_picks(comp, len(types)), types):
                m.get(c).resource = t
    # global minimums
    for res, need in RESOURCE_MIN.items():
        have = sum(1 for h in m.all() if h.resource == res)
        if have >= need:
            continue
        terrains = TOPUP_TERRAINS[res]
        if res == "mine":                       # mines sit on mountain hexes
            cands = [h.coord for h in m.all() if h.terrain == "mountain" and not h.resource]
        elif res == "quarry":                    # quarry from tundra or mountain
            cands = [h.coord for h in m.all()
                     if h.terrain in ("tundra", "mountain") and not h.resource]
        else:
            cands = [h.coord for h in m.all() if h.terrain in terrains and not h.resource]
        existing = [h.coord for h in m.all() if h.resource == res]
        cands.sort(key=lambda c: -min([distance(c, e) for e in existing], default=999))
        for c in cands:
            if have >= need:
                break
            m.get(c).resource = res; have += 1


# ── top level ─────────────────────────────────────────────────────────────────
def generate(**over):
    p = {**PARAMS, **over}
    # scale feature counts to map area (baseline 720 hexes = 30x24); lengths by linear dim
    ratio = (p["width"] * p["height"]) / 720.0
    lin = math.sqrt(ratio)
    def _sc(t): return (max(1, round(t[0] * ratio)), max(1, round(t[1] * ratio)))
    def _scl(t): return (max(1, round(t[0] * lin)), max(1, round(t[1] * lin)))
    for k in ("rivers", "lakes", "ranges", "forests", "wetlands", "tundras"):
        if k not in over:
            p[k] = _sc(p[k])
    for k in ("river_len", "range_len"):
        if k not in over:
            p[k] = _scl(p[k])
    rng = random.Random(p["seed"])
    random.seed(p["seed"])
    m = HexMap.blank(p["width"], p["height"], "plains")
    m._rng = rng
    m.reserved = set()
    _coastline(m, p, rng)
    _rivers(m, p, rng)
    _lakes(m, p, rng)
    anchors = _place_regions(m, p, rng)
    _ranges(m, p, rng, anchors)
    _fill_to_target(m, p, rng)
    _cull_small(m)
    _ensure_biomes(m, rng)
    _cap_components(m, p["cluster_cap"])
    _ensure_region_material(m, p)
    _carve_region_exits(m, p)
    _resources(m, p, rng)
    m.anchors = anchors
    m.settlement_range = p["settlement_range"]
    return m


def stats(m):
    from collections import Counter
    terr = Counter(h.terrain for h in m.all())
    res = Counter(h.resource for h in m.all() if h.resource)
    regions = Counter(h.region for h in m.all() if h.region is not None)
    return terr, res, regions


if __name__ == "__main__":
    m = generate()
    terr, res, regions = stats(m)
    tot = m.width * m.height
    print(f"map {m.width}x{m.height} = {tot} hexes")
    print("terrain:", dict(terr))
    print("  pct:", {k: f"{v*100//tot}%" for k, v in terr.items()})
    print("resources:", dict(res))
    print("region sizes:", dict(sorted(regions.items())))
