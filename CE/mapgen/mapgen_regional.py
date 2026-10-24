"""mapgen_regional.py — preset-driven map generation for Renown, through gen.js.

gen.js is the one regional generator: the map app, the settlement board and this module all run
it, so a seed code (Region/seed/players/WxH) gives the same board everywhere. generate_region()
runs gen.js under Node (gen_cli.js) with presets built fresh from region_presets.py, then reads the
exported grid back into a HexMap. This module keeps what Python needs around that grid: import /
export, Hills (derived from terrain on import, as gen.js importMap does) and the text report.
"""
from __future__ import annotations
import json, os, subprocess
from collections import Counter

from hexmap import HexMap, distance
import mapgen

HERE = os.path.dirname(os.path.abspath(__file__))
GEN_CLI = os.path.join(HERE, "gen_cli.js")


# ── hills (mirror of gen.js markHills; derived on import) ───────────────────
HILL_SEP = 4


def _mark_hills(m, min_sep=HILL_SEP, pinned=(), blocked=frozenset()):
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
    # pinned: start-zone Town hills, kept first. blocked: start-zone hexes, where
    # no other hill may form (every seat gets the same Town spots).
    for h in m.all():
        h.tactical = None

    def ring_hill(c):
        h = m.get(c)
        return (h.terrain == "plains" and len(m.neighbors(c)) == 6
                and all(n.terrain == "plains" for n in m.neighbors(c)))
    pinned = [tuple(c) for c in pinned]
    kept = []
    for c in pinned:
        if m.get(c) is not None and ring_hill(c):
            m.get(c).tactical = "hill"
            kept.append(c)
    cand = [h.coord for h in m.all()
            if ring_hill(h.coord) and h.coord not in blocked and h.coord not in pinned]
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
    for c in ranked:
        if all(distance(c, k) >= min_sep for k in kept):
            kept.append(c)
            m.get(c).tactical = "hill"


def _zone_pins(zones):
    return [tuple(t) for z in zones or [] for t in z["towns"]]


def _hill_pins(m):
    return _zone_pins(m.start_zones) + [tuple(c) for c in getattr(m, "carved_hills", [])]


def _zone_block(zones):
    return {tuple(c) for z in zones or [] for c in z["hexes"]}


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
        "climate": p.get("climate", "temperate"),
        "start_zones": [{"seat": z["seat"], "anchor": list(z["anchor"]),
                         "slide": z.get("slide", 0), "range": z["range"],
                         "hexes": [list(c) for c in z["hexes"]],
                         "towns": [list(c) for c in z["towns"]]}
                        for z in getattr(m, "start_zones", [])],
        "hills": [list(c) for c in getattr(m, "carved_hills", [])],
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
    m.start_zones = [{"seat": z["seat"], "anchor": tuple(z["anchor"]),
                      "slide": z.get("slide", 0), "range": z["range"],
                      "hexes": [tuple(c) for c in z["hexes"]],
                      "towns": [tuple(c) for c in z["towns"]]}
                     for z in data.get("start_zones", [])]
    m.carved_hills = [tuple(c) for c in data.get("hills", [])]
    # derived, never stored (start-zone Town hills and carved Hills pinned, zones barred)
    _mark_hills(m, data.get("hill_sep", HILL_SEP),
                _hill_pins(m), _zone_block(m.start_zones))
    return m


# ── pipeline ─────────────────────────────────────────────────────────────────
def _presets_js():
    """presets.js source, built from region_presets.py and the live renown_data rules - the same
    text build_mapapp writes for the map app, so Node never reads a stale presets.js."""
    import build_mapapp
    js, _ = build_mapapp.presets_js(build_mapapp.rules_of(build_mapapp.find_data()))
    return js


def generate_region(region, *, attempts=12, **over):
    """Generate a map in the style of `region` with gen.js. Reseeds on validation failure.

    Returns (map, preset params, violations). A non-empty violations list means every attempt
    failed and the best-scoring board is returned anyway, so the caller can see what the preset
    cannot satisfy rather than shipping a quiet lie.
    """
    payload = {"presets_js": _presets_js(), "region": region, "over": over, "attempts": attempts}
    run = subprocess.run(["node", GEN_CLI], input=json.dumps(payload), capture_output=True,
                         text=True, encoding="utf-8")
    if run.returncode:
        raise RuntimeError(f"gen.js failed for {region!r}: {run.stderr.strip()}")
    res = json.loads(run.stdout)
    m = import_map(res["map"])
    m.export = res["map"]
    return m, res["params"], res["violations"]


def report(m, p, v):
    tot = m.width * m.height
    terr = Counter(h.terrain for h in m.all())
    res = Counter(h.resource for h in m.all() if h.resource)
    lines = [f"{p['name']}  {m.width}x{m.height} = {tot} hexes  "
             f"substrate={p['substrate']}  players={p['players']}"]
    lines.append("  terrain: " + ", ".join(
        f"{k} {vv} ({vv*100//tot}%)" for k, vv in terr.most_common()))
    hills = sum(1 for h in m.all() if h.tactical == "hill")
    lines.append(f"  hills: {hills}   (require_hill={p.get('require_hill')})")
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
    import region_presets
    todo = [a.region] if a.region else region_presets.names()
    for name in todo:
        m, p, v = generate_region(name, seed=a.seed, players=a.players,
                                  width=a.width, height=a.height)
        print(report(m, p, v))
        if a.export:
            import json
            with open(a.export, "w") as fh:
                json.dump(m.export, fh, separators=(",", ":"))
            print(f"  exported -> {a.export}")
        print()
