"""region_presets.py — regional map-generation presets for Renown.

A preset describes HOW a region of the world generates, not what is on it.
The default generator (mapgen.generate) is additive: blank plains, stamp
biomes, stop at a plains target. A preset may instead be a MATRIX: the board
fills with a substrate terrain and plains are CARVED out of it.

Schema
------
substrate    terrain the board fills with before anything else.
             "plains" -> additive preset (default behaviour).
             anything else -> matrix preset (carve routes/clearings).
palette      set of terrains permitted to appear AT ALL. Anything outside the
             palette is never stamped and is stripped from resource logic.
             Closing the palette is what makes a region read as itself.
shares       {terrain: fraction-of-board} targets for non-substrate terrain.
morphology   {terrain: "blob"|"band"|"scatter"|"fringe"} shaper per terrain.
buffers      list of terrain PAIRS that must stay one plains hex apart.
             Replaces mapgen's global all-biomes-buffer rule.
band         {terrain: (edge, thickness_frac, jitter)} for "band" morphology.
             edge in ("n","s","e","w").
scatter      {terrain: (count, size_lo, size_hi, min_sep)} for "scatter".
border       width in hexes of the water rim. 0 = landlocked.
carve        matrix presets only:
               routes           number of corridors linking clearings
               width            corridor width in hexes
               clearing_radius  radius of the pocket cleared per settlement
               connect          "spanning" (MST-ish) or "ring"
require_hill whether the >=1 Hill invariant is enforced (see the TERRAIN /
             RULES chartering drift; left toggleable on purpose).
resource_min per-preset overrides to mapgen.RESOURCE_MIN. A closed palette can
             make a raw material genuinely unavailable — that is intended.
art          {terrain: tile_name} render override, e.g. Draggath tundra
             painted as badlands. Consumed by build_board, not by mapgen.
"""
from __future__ import annotations

# terrain keys used by the generator (mapgen vocabulary, not renown_data's)
ALL = ("plains", "forest", "wetland", "tundra", "mountain", "water")


def preset(**kw):
    base = dict(
        name="", substrate="plains", palette=set(ALL), shares={},
        morphology={}, buffers=[], band={}, scatter={}, border=0,
        carve=None, require_hill=True, resource_min={}, art={}, notes="",
    )
    base.update(kw)
    return base


PRESETS = {

    # ── additive: the existing generator, expressed as a preset ─────────────
    "Default": preset(
        name="Default",
        substrate="plains",
        shares={"forest": 0.18, "wetland": 0.18, "tundra": 0.08, "mountain": 0.08},
        morphology={"forest": "blob", "wetland": "blob", "tundra": "blob",
                    "mountain": "band"},
        buffers=[("forest", "wetland"), ("forest", "tundra"),
                 ("wetland", "tundra")],
        border={"n": 0, "s": 0, "e": {"width": (0, 1), "span": (.3, .7)}, "w": {"width": (0, 1), "span": (.3, .7)}},
        notes="Terrain stays out of the way. Baseline.",
    ),

    # ── matrix: forest substrate, plains carved as narrow passages ──────────
    "Dreadwood": preset(
        name="Dreadwood",
        substrate="forest",
        palette={"forest", "plains", "wetland", "water"},
        shares={"wetland": 0.10},
        morphology={"wetland": "blob"},
        buffers=[],                      # forest touches everything here
        border={"n": 0, "s": 0, "w": {"width": 1, "span": (.3, .6)}, "e": 0},
        carve=dict(routes=1, width=1, clearing_radius=1, temp=0.9,
                   mazes=(2, 3), maze_temp=1.1, junction_p=0.5,
                   connect="spanning"),
        require_hill=False,
        resource_min={"quarry": 0, "salt": 0, "mine": 0, "arable": 1},
        notes=("Ithiss heartland. Woodland matrix; settlements sit in clearings "
               "linked by narrow grass passages. No tundra, no mountain: "
               "quarry/salt/mine are unavailable by design."),
    ),

    # ── matrix: mountain substrate, slot-canyon corridors ───────────────────
    "Crag Pass": preset(
        name="Crag Pass",
        substrate="mountain",
        palette={"mountain", "plains", "forest", "water"},
        shares={"forest": 0.14},
        morphology={"forest": "blob"},
        buffers=[],
        border=0,
        carve=dict(routes=0, width=1, clearing_radius=1, temp=1.3,
                   mazes=(2, 3), maze_temp=1.3, junction_p=0.6,
                   connect="spanning"),
        require_hill=False,
        resource_min={"salt": 0, "arable": 1, "forestry": 1, "apiary": 0,
                      "quarry": 1, "mine": 2},
        notes=("Labyrinth. Everything is impassable except the carved network. "
               "Chokepoint warfare; movement is the whole game."),
    ),

    # ── matrix: wetland substrate ───────────────────────────────────────────
    "Shallow Mire": preset(
        name="Shallow Mire",
        substrate="wetland",
        palette={"wetland", "plains", "forest", "water"},
        shares={"forest": 0.12},
        morphology={"forest": "blob"},
        buffers=[],
        border={"n": {"width": (1, 2), "span": (.4, .8)}, "s": {"width": (1, 2), "span": (.4, .8)}, "w": {"width": (0, 2), "span": (.3, .7)}, "e": {"width": (0, 2), "span": (.3, .7)}},
        carve=dict(routes=3, width=1, clearing_radius=1, temp=0.7, connect="spanning"),
        require_hill=False,
        resource_min={"quarry": 0, "salt": 0, "mine": 0, "arable": 1},
        notes=("Shassolin territory. Mire everywhere: Unwieldy, Immune Steady, "
               "-1 Save is the default battle condition. No tundra."),
    ),

    # ── interleaved cold: tundra bulk, forest bands, mountain wall ──────────
    "Fair Whitewood": preset(
        name="Fair Whitewood",
        substrate="tundra",
        palette={"tundra", "forest", "mountain", "plains", "water"},
        shares={"forest": 0.24, "mountain": 0.16},
        morphology={"forest": "blob", "mountain": "band"},
        band={"mountain": ("w", 0.16, 0.4, (0.35, 0.6))},
        buffers=[],                      # tundra and forest interleave freely
        border={"n": {"width": (0, 1), "span": (.3, .6)}, "s": {"width": (0, 1), "span": (.3, .6)}, "w": 0, "e": 0},
        carve=dict(routes=2, width=1, clearing_radius=1, temp=0.8, connect="spanning"),
        require_hill=False,
        resource_min={"arable": 1, "apiary": 0, "quarry": 3, "salt": 2},
        notes=("Madekite. Wintery forested mountain pass. Ridges run part-way "
               "down the map rather than sealing it, so the passes are between "
               "the ranges instead of through them. Strained is the default "
               "condition; quarry-rich, arable-poor."),
    ),

    # ── scatter: open ground broken by isolated peaks ───────────────────────
    "Bleak Highlands": preset(
        name="Bleak Highlands",
        substrate="plains",
        palette={"plains", "mountain", "tundra", "water"},
        shares={"mountain": 0.30, "tundra": 0.10},
        morphology={"mountain": "scatter", "tundra": "blob"},
        scatter={"mountain": (110, 1, 3, 3, 0.7, 5, 0.3)},
        # n, size_lo, size_hi, min_sep, chain, chain_range, widen
        buffers=[],
        border={"n": 0, "s": 0, "e": {"width": (0, 1), "span": (.2, .5)}, "w": 0},
        require_hill=True,
        resource_min={"forestry": 0, "apiary": 0, "mine": 1},
        art={"plains": "wastes", "tundra": "badlands"},
        notes=("Herding clans under a chief — the line Vogen reached in 1136 "
               "and got no further. Broken country rather than a wall: peaks "
               "stand alone or join in short ridges, occasionally two hexes "
               "thick. Every route exists and none is fast, so an army bleeds "
               "tempo everywhere instead of being stopped in one pass. No "
               "forest, so forestry is unavailable."),
    ),

    # ── two-tone arid: tundra badlands over grassland ───────────────────────
    "Draggath Wastes": preset(
        name="Draggath Wastes",
        substrate="plains",
        palette={"plains", "tundra", "mountain", "water"},
        shares={"tundra": 0.42, "mountain": 0.12},
        morphology={"tundra": "blob", "mountain": "scatter"},
        scatter={"mountain": (55, 1, 3, 3)},
        carve=dict(rivers=(1, 2), river_temp=1.0),
        buffers=[],
        border={"n": 0, "s": 0, "w": {"width": (0, 1), "span": (.2, .5)}, "e": 0},
        require_hill=True,
        resource_min={"forestry": 0, "apiary": 0},
        notes=("Badlands. Tundra painted as salted earth. Strained everywhere; "
               "arable is scarce and contested — recursive scarcity."),
        art={"plains": "wastes", "tundra": "badlands"},
    ),

    # ── near-pure grassland ────────────────────────────────────────────────
    "Wheat Fields": preset(
        name="Wheat Fields",
        substrate="plains",
        palette={"plains", "forest", "water", "wetland"},
        shares={"forest": 0.22, "wetland": 0.04},
        morphology={"forest": "scatter", "wetland": "blob"},
        scatter={"forest": (120, 1, 3, 2)},
        carve=dict(rivers=(1, 2), river_temp=1.0),
        buffers=[],
        border={"n": 0, "s": 0, "e": {"width": (0, 1), "span": (.2, .5)}, "w": {"width": (0, 1), "span": (.2, .5)}},
        require_hill=True,
        resource_min={"quarry": 0, "salt": 0, "mine": 0, "forestry": 1},
        notes=("Proving ground. Open field: ranged +1 Strike almost everywhere, "
               "Hills decide initiative. Never paved."),
    ),

    # ── forest bulk, resource-rich ─────────────────────────────────────────
    "Scarlet Forest": preset(
        name="Scarlet Forest",
        substrate="forest",
        palette={"forest", "plains", "mountain", "water", "wetland"},
        shares={"mountain": 0.08, "wetland": 0.05},
        morphology={"mountain": "band", "wetland": "blob"},
        buffers=[],
        border={"n": 0, "s": 0, "w": {"width": 1, "span": (.3, .7)}, "e": 0},
        carve=dict(routes=1, width=1, clearing_radius=1, temp=0.8,
                   mazes=(2, 3), maze_temp=1.1, junction_p=0.5,
                   rivers=(1, 2), river_temp=1.0,
                   connect="spanning"),
        require_hill=False,
        resource_min={"forestry": 6, "salt": 0, "quarry": 1, "arable": 2},
        notes=("Best wood in the world. Woodland matrix but wider passages "
               "than Dreadwood; forestry saturated."),
        art={"plains": "scarlet_plain", "forest": "scarlet_forest"},
    ),

    # ── enclosed pocket of tillable land ───────────────────────────────────
    "Glen of Pravak": preset(
        name="Glen of Pravak",
        substrate="plains",
        palette={"plains", "mountain", "tundra", "forest", "water"},
        shares={"mountain": 0.30, "tundra": 0.10, "forest": 0.14},
        morphology={"mountain": "fringe", "tundra": "blob", "forest": "scatter"},
        scatter={"forest": (60, 1, 2, 2)},
        buffers=[],
        border=0,
        require_hill=True,
        resource_min={"salt": 0, "forestry": 1},
        notes=("A glen ringed by rock. Mountains on the rim, tillable centre. "
               "Positional strategy: every approach is known ground."),
    ),

    # ── two parallel ranges with a held gap ────────────────────────────────
    "Hermit's Row": preset(
        name="Hermit's Row",
        substrate="plains",
        palette={"plains", "mountain", "tundra", "water"},
        shares={"mountain": 0.24, "tundra": 0.12},
        morphology={"mountain": "band", "tundra": "blob"},
        band={"mountain": ("w", 0.10, 0.5)},
        buffers=[],
        border={"n": 0, "s": 0, "e": {"width": (0, 1), "span": (.2, .5)}, "w": 0},
        require_hill=True,
        resource_min={"forestry": 0, "apiary": 0},
        art={"plains": "wastes", "tundra": "badlands"},
        notes=("A narrow pair of ranges. Two walls, one contested narrows "
               "between them."),
    ),
    # ── Piety heartland: settled, open, cut by a river ─────────────────────
    "Lenaveron": preset(
        name="Lenaveron",
        substrate="plains",
        palette={"plains", "tundra", "mountain", "water", "forest"},
        shares={"tundra": 0.16, "mountain": 0.10, "forest": 0.08},
        morphology={"tundra": "blob", "mountain": "perimeter",
                    "forest": "scatter"},
        # count, length, width, depth-from-edge band
        perimeter={"mountain": (9, (14, 26), (1, 2), (1, 6))},
        scatter={"forest": (40, 1, 2, 2)},
        carve=dict(rivers=(2, 3), river_temp=1.0),
        buffers=[],
        border={"n": 0, "s": 0, "e": {"width": (1, 2), "span": (.5, .9)}, "w": 0},
        require_hill=True,
        resource_min={"forestry": 1},
        notes=("Papacy heartland. Open and buildable in the middle — Piety "
               "wants Public Order, not chokepoints — with long thin ranges "
               "running along the margins and rivers crossing the interior."),
    ),

    # ── unbroken sacred forest; almost no carving ──────────────────────────
    "Lost Woods": preset(
        name="Lost Woods",
        substrate="forest",
        palette={"forest", "plains", "wetland", "water"},
        shares={"wetland": 0.06},
        morphology={"wetland": "blob"},
        buffers=[],
        border={"n": 0, "s": 0, "w": {"width": (1, 2), "span": (.5, .9)}, "e": 0},
        carve=dict(routes=0, width=1, clearing_radius=1, temp=0.6,
                   mazes=(1, 2), maze_temp=0.9, junction_p=0.7,
                   rivers=(3, 4), river_temp=1.0,
                   connect="spanning"),
        require_hill=False,
        resource_min={"quarry": 0, "salt": 0, "mine": 0, "arable": 1},
        notes=("The only land untouched by the Great Fracture. Denser than "
               "Dreadwood and barely carved: one or two passages, everything "
               "else is wood. Defender Seizes the Initiative almost always."),
    ),

    # ── smallest landmass for the size of the culture on it ────────────────
    "Drakenheart": preset(
        name="Drakenheart",
        substrate="plains",
        palette={"plains", "water", "mountain", "forest", "tundra"},
        shares={"water": 0.22, "mountain": 0.22, "forest": 0.08, "tundra": 0.06},
        morphology={"water": "channels", "mountain": "scatter",
                    "forest": "scatter", "tundra": "blob"},
        scatter={"mountain": (70, 1, 4, 3), "forest": (35, 1, 2, 2)},
        band={"water": ("e", 0.0, 0.6)},
        buffers=[],
        border={"n": {"width": (1, 2), "span": (.6, 1.)}, "s": {"width": (1, 2), "span": (.6, 1.)}, "w": {"width": (1, 2), "span": (.5, 1.)}, "e": {"width": (1, 2), "span": (.5, 1.)}},
        require_hill=True,
        resource_min={"mine": 3, "salt": 0},
        notes=("Drakteni seat. Land is the scarce resource and the engine of "
               "everything they do — heavily channelled, mine-rich. Straits "
               "stay one hex so expansion is possible without a Shipyard, "
               "but every crossing ends your Move."),
    ),

    # ── shoals: shared water, land in fragments ────────────────────────────
    "Marrow Shoals": preset(
        name="Marrow Shoals",
        substrate="water",
        palette={"water", "plains", "wetland", "forest"},
        shares={"wetland": 0.10, "forest": 0.06},
        morphology={"wetland": "blob", "forest": "scatter"},
        scatter={"forest": (25, 1, 2, 2)},
        buffers=[],
        border=0,
        sea_crossing="shipyard",
        carve=dict(islands=(6, 6), island_size=(44, 58), islets=(16, 4),
                   land_target=0.48, gap=(2, 3)),
        require_hill=False,
        resource_min={"mine": 0, "quarry": 0, "salt": 0, "arable": 2,
                      "forestry": 2},
        notes=("A true archipelago — one small isle per player plus scattered "
               "islets to expand onto. Deep water between them: you reach "
               "anyone else only once a Shipyard is mastered. Land is the "
               "scarcest thing on the board."),
    ),

    # ── the centre: balanced, wooded, one lake ─────────────────────────────
    "Vaelohk": preset(
        name="Vaelohk",
        substrate="plains",
        palette={"plains", "forest", "water", "mountain", "tundra"},
        shares={"forest": 0.22, "mountain": 0.06, "water": 0.04, "tundra": 0.05},
        morphology={"forest": "blob", "mountain": "scatter",
                    "water": "blob", "tundra": "blob"},
        scatter={"mountain": (22, 1, 2, 4)},
        carve=dict(rivers=(2, 3), river_temp=1.0),
        buffers=[("forest", "tundra")],
        border={"n": {"width": (1, 2), "span": (.7, 1.)}, "s": {"width": (1, 2), "span": (.7, 1.)}, "w": {"width": (1, 2), "span": (.7, 1.)}, "e": {"width": (1, 2), "span": (.7, 1.)}},
        require_hill=True,
        notes=("The centre island and the world's name. Deliberately the most "
               "even preset — no dominant terrain, everything available. The "
               "Sullen Lake is the one inland water body."),
    ),

    # ── castle in the mountains, heath below ───────────────────────────────
    "Blighthold": preset(
        name="Blighthold",
        substrate="plains",
        palette={"plains", "mountain", "tundra", "forest", "water"},
        shares={"mountain": 0.20, "tundra": 0.12, "forest": 0.10},
        morphology={"mountain": "massif", "tundra": "blob", "forest": "scatter"},
        # count, size_lo, size_hi, min_sep, max bbox, centre keepout
        massif={"mountain": (12, 10, 16, 6, 4, 6)},
        scatter={"forest": (35, 1, 2, 2)},
        buffers=[],
        border={"n": 0, "s": 0, "w": 0, "e": {"width": (0, 1), "span": (.2, .5)}},
        require_hill=True,
        resource_min={"mine": 4, "quarry": 3},
        notes=("The heath they grew crops through the Blight. A handful of "
               "chunky massifs set away from the centre — high ground that "
               "frames the worked land instead of cutting it in half."),
    ),

    # ── mountain bulk ──────────────────────────────────────────────────────
    "Coloured Mountains": preset(
        name="Coloured Mountains",
        substrate="mountain",
        palette={"mountain", "plains", "tundra", "forest", "water"},
        shares={"tundra": 0.16, "forest": 0.14},
        morphology={"tundra": "blob", "forest": "scatter"},
        scatter={"forest": (45, 1, 3, 2)},
        buffers=[],
        border={"n": 0, "s": 0, "w": {"width": (0, 1), "span": (.2, .5)}, "e": 0},
        carve=dict(routes=2, width=1, clearing_radius=1, temp=0.9,
                   mazes=(2, 3), maze_temp=1.1, junction_p=0.4,
                   connect="spanning"),
        require_hill=False,
        resource_min={"mine": 5, "quarry": 4, "arable": 1, "salt": 1},
        notes=("The ancient continent. Wider valleys than Crag Pass — this is "
               "where a people farmed, not a labyrinth."),
    ),

    # ── frozen south-east, abandoned institutions ──────────────────────────
    "Tombs of the Old Gods": preset(
        name="Tombs of the Old Gods",
        substrate="tundra",
        palette={"tundra", "plains", "mountain", "water", "forest"},
        shares={"mountain": 0.12, "plains": 0.0, "forest": 0.06},
        morphology={"mountain": "scatter", "forest": "scatter"},
        scatter={"mountain": (40, 1, 3, 3), "forest": (25, 1, 2, 3)},
        buffers=[],
        border={"n": 0, "s": 0, "e": {"width": (0, 1), "span": (.3, .6)}, "w": 0},
        carve=dict(routes=2, width=1, clearing_radius=1, temp=0.8,
                   mazes=(2, 3), maze_temp=1.1, junction_p=0.4,
                   connect="spanning"),
        require_hill=False,
        resource_min={"arable": 1, "forestry": 1, "quarry": 4, "salt": 3},
        notes=("Frozen tundra the Lenavorites abandoned. Strained is the "
               "default state; quarry and salt are abundant, food is not."),
    ),

    # ── twelve islands ─────────────────────────────────────────────────────
    "The Twelfth Reach": preset(
        name="The Twelfth Reach",
        substrate="water",
        palette={"water", "plains", "forest", "wetland", "tundra"},
        shares={"forest": 0.14, "wetland": 0.06, "tundra": 0.04},
        morphology={"forest": "blob", "wetland": "blob", "tundra": "blob"},
        buffers=[],
        border=0,
        sea_crossing="shipyard",
        carve=dict(islands=(3, 4), island_size=(95, 130), islets=(5, 9),
                   land_target=0.58, gap=(2, 5)),
        require_hill=True,
        resource_min={"mine": 0, "quarry": 0, "salt": 0},
        notes=("Two to four substantial islands rather than a scatter — a "
               "diaspora zone, not a reef. Players share an island with a "
               "neighbour and must cross open water to reach the rest."),
    ),
}


def get(name):
    if name not in PRESETS:
        raise KeyError(f"unknown preset {name!r}; have {sorted(PRESETS)}")
    return dict(PRESETS[name])


def names():
    return sorted(PRESETS)
