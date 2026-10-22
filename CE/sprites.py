"""
sprites.py — pixel sprites for the settlement board scene (skins: farmstead, blackletter, scene).

Art only. No mechanics. Which sprite a thing gets is decided by the data file:
    Holding        -> its own sprite, else its group     (24x24, "holding:<name>" / "group:<g_key>")
    Raw Material   -> also a terrain strip at the feet    (30x5, "feet:<name>") of the ward's frontmost holding
    Monument       -> its own sprite, else its group     (36x36, "monument:<name>")
    Wonder         -> its own sprite                     (36x36, "wonder:<name>")
    Settlement     -> a skyline behind its holdings: "sky:core:<tier>" centred, "sky:fill:<tier>" tiled
                      across the lot (fallback 24x24 "tier:<tier>")
    Infrastructure -> skyline pieces "inf:<name>", placed per SKYLINE; INFRA_SUPERSEDES hides the replaced one
    Status / marks -> "st:<state>" per STATUS_ICONS (12x12), "mk:battle" / "mk:siege" (24x24): Inspect panel, Army plate, map
    Equipment      -> "eq:<item>" per WEAPONS / RANGED / SHIELDS / ARMORS (18x18, no ground row): loadout icons
    Map pieces     -> "army:<Retinue>" per RETINUES, "map:<tier>" per SETTLEMENTS, "map:camp" / "map:bandit_army"
                      (24x24). Key 'p' is the owner's colour, swapped in per player on the map.
    Map terrain    -> small "prop:<name>" sprites (free size) scattered per hex by SCATTER[<kind>] for every
                      kind in MAP_TERRAIN: deterministic per map seed + hex, kept inside the hex, clear of the
                      resource badge and of each other (layer "g" = min gap in px; negative = may overlap).
                      Drawn in the hex's own colour: H / S / D are relief tones the board derives from each
                      hex fill (climate-safe); SCATTER[<kind>]["tone"] overrides the mix (tundra is muted).

Format: each sprite is a list of equal-length strings, one char per pixel.
'.' is transparent; every other char is a palette key (KEYS). The last row is ground ('g'),
which the scene renderer skips so every building stands on one ground line.
Art is built with the small canvas kit below (cv / put / box / gable / house …, then fin() or art() add the ground
row and stand the art on it). Nothing is truncated silently: oversize art fails --check.

    python sprites.py --data ../renown_data_d10.py --check
    python sprites.py --data ../renown_data_d10.py --sheet sprites_sheet.html
"""
import argparse, json, os, sys

SPRITE_VERSION = "0.9.5"

KEYS = {
    "k": "outline", "w": "plaster wall", "t": "stone", "u": "dark stone", "r": "roof",
    "d": "door / shadow", "y": "lit window / gold", "f": "fire", "s": "pale (smoke, canvas, bone)",
    "m": "metal", "b": "wood", "l": "leaf (seasonal)", "n": "evergreen needles", "c": "red cloth", "a": "royal cloth", "e": "water",
    "h": "skin", "p": "owner colour (map pieces; replaced per player)",
    "P": "owner colour shade (heraldry; derived per player)", "q": "owner colour hilite (heraldry; derived per player)",
    "x": "heraldic charge shade (darkened on pale player colours)",
    "H": "terrain hilite", "S": "terrain shade", "D": "terrain deep (map terrain; derived per hex fill)",
    "g": "ground (skipped in scene)",
}

PALETTES = {
    "farmstead":   {"k": "#3b2414", "w": "#f0d8a8", "t": "#b8b0a0", "u": "#7a7068", "r": "#b8432f", "d": "#4a2a16",
                    "y": "#ffd84a", "f": "#ff8a2a", "s": "#ece6da", "m": "#8a8f9a", "b": "#9a6a32", "l": "#5a9a32",
                    "c": "#c8302a", "a": "#4a5ab8", "e": "#4a8ad8", "n": "#2f6a2a", "g": "#5a8a2e",
                    "h": "#f0c090", "p": "#9aa0a8", "P": "#686e7c", "q": "#c4c8d2", "x": "#c8c0b4", "H": "#a8c878", "S": "#5a7a3a", "D": "#34481f"},
    "blackletter": {"k": "#0a0807", "w": "#9a8e7c", "t": "#8a8070", "u": "#4a423a", "r": "#6b2a2a", "d": "#1a1410",
                    "y": "#d8b45a", "f": "#e0602a", "s": "#c8bca8", "m": "#a0a0a8", "b": "#6b4a2a", "l": "#4a6a2a",
                    "c": "#9a2020", "a": "#3a3a7a", "e": "#3a5a7a", "n": "#2a4428", "g": "#2c2521",
                    "h": "#c8a07a", "p": "#8a8a90", "P": "#686e7c", "q": "#c4c8d2", "x": "#c8c0b4", "H": "#a8c878", "S": "#5a7a3a", "D": "#34481f"},
    "scene":       {"k": "#0e1220", "w": "#e8d8b0", "t": "#a8a0a0", "u": "#605a68", "r": "#a03a3a", "d": "#2a1f30",
                    "y": "#ffd27a", "f": "#ff9a3a", "s": "#e8e4dc", "m": "#8a96b0", "b": "#8a5a3a", "l": "#3a7a2a",
                    "c": "#c83a3a", "a": "#5a4ab0", "e": "#3a7ac8", "n": "#24563a", "g": "#2f4a2a",
                    "h": "#e0b088", "p": "#9aa0b0", "P": "#686e7c", "q": "#c4c8d2", "x": "#c8c0b4", "H": "#a8c878", "S": "#5a7a3a", "D": "#34481f"},
}


def _s(rows, size, mirror=False):
    """Pad art to size x size, bottom-anchored, with a ground row. mirror=True: rows are left halves."""
    if mirror:
        half = size // 2
        rows = [r.ljust(half, ".") for r in rows]
        rows = [r + r[::-1] for r in rows]
    rows = [r.ljust(size, ".") for r in rows]
    return ["." * size] * max(0, size - 1 - len(rows)) + rows + ["g" * size]


def _b(rows, w=32, h=20, mirror=False):
    """Backdrop: like _s but w x h (default 32x20). mirror=True: rows are left halves (w/2)."""
    if mirror:
        rows = [r.ljust(w // 2, ".") for r in rows]
        rows = [r + r[::-1] for r in rows]
    rows = [r.ljust(w, ".") for r in rows]
    return ["." * w] * max(0, h - 1 - len(rows)) + rows + ["g" * w]


S12, S18, S24, S36, S48 = 12, 18, 24, 36, 48
EQ_TILE = "#3a404c"      # fixed backing square behind every eq: icon (board + sheet)
SPRITES = {}

# ---------------------------------------------------------------- kit
def cv(w=24, h=23):
    """Blank canvas, w wide, h art rows (ground row added by fin)."""
    return [list("." * w) for _ in range(h)]


def put(c, rows, x, y):
    """Paste rows at (x, y); '.' is transparent."""
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            if ch != "." and 0 <= y + j < len(c) and 0 <= x + i < len(c[0]):
                c[y + j][x + i] = ch


def box(c, x, y, w, h, fill, edge="k"):
    for j in range(h):
        for i in range(w):
            on_edge = edge and (i in (0, w - 1) or j in (0, h - 1))
            c[y + j][x + i] = edge if on_edge else fill


def hline(c, x0, x1, y, ch):
    for x in range(x0, x1 + 1):
        c[y][x] = ch


def vline(c, x, y0, y1, ch):
    for y in range(y0, y1 + 1):
        c[y][x] = ch


def gable(c, cx, y, half, fill="r", eave=True):
    """Gable roof: apex at (cx, y), widening one px per row to half; outlined."""
    for i in range(half + 1):
        for x in range(cx - i, cx + i + 1):
            edge = x in (cx - i, cx + i) or (eave and i == half)
            c[y + i][x] = "k" if edge else fill


def gable2(c, x, y, half, fill="r"):
    """Even-width gable: two-px apex at x, x+1."""
    for i in range(half + 1):
        for xx in range(x - i, x + 2 + i):
            edge = xx in (x - i, x + 1 + i) or i == half
            c[y + i][xx] = "k" if edge else fill


def fin(c):
    """Rows + ground row; art is dropped so its lowest pixel stands on the ground."""
    rows = ["".join(r) for r in c]
    while rows and set(rows[-1]) == {"."}:
        rows = [rows[-1]] + rows[:-1]
    return rows + ["g" * len(c[0])]


def art(rows, w=24, h=24):
    """Hand rows -> padded sprite (like sprites._s)."""
    rows = [r.ljust(w, ".") for r in rows]
    return ["." * w] * max(0, h - 1 - len(rows)) + rows + ["g" * w]


WHEEL = ["..kkk..",
         ".kbbbk.",
         "kbkbkbk",
         "kbbkbbk",
         "kbkbkbk",
         ".kbbbk.",
         "..kkk.."]
WHEEL5 = [".kkk.",
          "kbkbk",
          "kbkbk",
          "kbkbk",
          ".kkk."]
WIN = ["kkk", "kyk", "kkk"]
WIN2 = ["kkkk", "kyyk", "kyyk", "kkkk"]
WINT = ["kkk", "kyk", "kyk", "kkk"]
SLIT = ["k", "d", "d", "k"]


# ================================================================ BATCH 1: logistics
def _wagon(c, x, y, cloth="s"):
    """Covered wagon, 18 wide, 13 tall, top-left at (x, y)."""
    put(c, ["...kkkkkkkkkk.....",
            "..k" + cloth * 10 + "k....",
            ".k" + cloth * 3 + "k" + cloth * 4 + "k" + cloth * 3 + "k...",
            ".k" + cloth * 3 + "k" + cloth * 4 + "k" + cloth * 3 + "k...",
            ".k" + cloth * 3 + "k" + cloth * 4 + "k" + cloth * 3 + "k...",
            "kbbbbbbbbbbbbbbk..",
            "kbkbbbbkbbbbkbbkkk",
            "kbbbbbbbbbbbbbbk.k",
            ".kkkkkkkkkkkkkk..."], x, y)
    put(c, WHEEL, x + 1, y + 7)
    put(c, WHEEL, x + 9, y + 7)


c = cv()
_wagon(c, 2, 9)
SPRITES["group:g_logistics"] = fin(c)

# Butchery: half-timbered shop, shutter counter, carcass rack with hanging joints
c = cv()
gable(c, 7, 6, 7)
box(c, 0, 13, 15, 10, "w")
for x in (4, 10):
    vline(c, x, 14, 21, "b")
hline(c, 1, 13, 17, "b")
put(c, ["kkk", "kyk", "kkk"], 1, 14)
put(c, ["kkk", "kyk", "kkk"], 11, 14)
put(c, ["kkkk", "kddk", "kddk", "kddk", "kddk"], 5, 18)
put(c, ["kkkkk", "kcbck"], 9, 18)                     # counter with cuts
put(c, ["bbbbbbbbb",
        "bk.k.k.kb",
        "bm.m.m.mb",
        "bc.c.c.cb",
        "bc.ccc.cb",
        "b..cc...b",
        "b...c...b",
        "b.......b",
        "b.......b",
        "b.......b",
        "b.......b"], 15, 12)
SPRITES["holding:Butchery"] = fin(c)

# Smokehouse: low hut, smoking roof louver, drying rack of fish
c = cv()
put(c, [".s.......",
        "..s..s...",
        ".s..s....",
        "..s......",
        "...kk....",
        "..kddk..."], 3, 3)
gable(c, 6, 9, 6)
box(c, 0, 15, 13, 8, "b")
for x in (3, 6, 9):
    vline(c, x, 16, 21, "k")
put(c, ["kkkk", "kddk", "kddk", "kddk", "kddk", "kddk"], 7, 16)
put(c, ["bbbbbbbbbbb",
        "b.m..m..m.b",
        "b.e..e..e.b",
        "bsee.ee.eeb",
        "b.e..e..e.b",
        "b..s......b",
        "bbbbbbbbbbb",
        "b.........b",
        "b.........b"], 13, 14)
SPRITES["holding:Smokehouse"] = fin(c)

# Caravanery: walled courtyard, crenellated, arched gate, wagon cover over the wall
c = cv()
put(c, ["k.k.k.k.k.k.k.k.",
        "kkkkkkkkkkkkkkkk"], 0, 9)
box(c, 0, 10, 16, 13, "w")
for x in (5, 10):
    vline(c, x, 11, 13, "b")
hline(c, 1, 14, 13, "b")
put(c, ["...kkkk...",
        "..kddddk..",
        ".kddddddk.",
        ".kddddddk.",
        ".kddsdddk.",
        ".kddsdddk.",
        ".kddddddk.",
        ".kddddddk.",
        ".kddddddk."], 3, 13)
put(c, WIN, 1, 11)
put(c, WIN, 12, 11)
put(c, ["..kkkkkk",
        ".kssksssk",
        "ksssksssk",
        "ksssksssk",
        "kbbbbbbbbk",
        "kbkbbbkbbk",
        "kkkkkkkkkk"], 14, 10)
put(c, WHEEL5, 15, 17)
put(c, ["kk", "kbk"], 21, 21)
SPRITES["holding:Caravanery"] = fin(c)

# Castle Yard (key: Coliseum): keep tower, curtain wall with arcade, yard with a pell and banner
c = cv()
put(c, ["k.k.k.", "kkkkkk"], 0, 0)
box(c, 0, 2, 6, 21, "t")
put(c, SLIT, 2, 4)
put(c, SLIT, 2, 11)
put(c, ["kkk", "kdk", "kdk"], 1, 19)
put(c, ["..c.", ".kcc", ".kc.", ".k.."], 5, 0)
put(c, ["k.k.k.k.k.k.k.k.k.",
        "kkkkkkkkkkkkkkkkkk"], 6, 8)
box(c, 6, 10, 18, 13, "t")
for x in (8, 12, 16, 20):
    put(c, ["kk", "dd", "dd", "dd"], x, 12)
hline(c, 7, 22, 16, "u")
for x in range(7, 23, 3):
    c[18][x] = "u"
put(c, ["kbk", ".b.", "kbk", ".b."], 18, 18)
SPRITES["holding:Coliseum"] = fin(c)

# Conditioning Field: beam on two posts with two straw pells hanging through it, stool and bucket (original layout)
c = cv()
for x0 in (4, 13):
    put(c, ["bbb"], x0, 6)
    for y in range(7, 16):
        put(c, ["yyy"], x0, y)
    put(c, ["bbb"], x0, 12)
    vline(c, x0 + 1, 16, 22, "b")
hline(c, 1, 19, 10, "b")
put(c, ["bbbbb", "..b..", "..b..", "..b.."], 18, 15)
put(c, ["kkkk", "ktuk", "kuuk", "kkkk"], 19, 19)
SPRITES["holding:Conditioning Field"] = fin(c)

# Grand Tournament: two striped pavilions with pennants, tilt barrier and lance between
def _pav(c, x, y, a, b):
    rows = [".....k.....",
            ".....k" + a + a + "...",
            ".....k" + a + a + "...",
            ".....k.....",
            "....kkk....",
            "...k" + b + a + b + "k...",
            "..k" + b + a + b + a + b + "k..",
            ".k" + b + a + b + a + b + a + b + "k.",
            "k" + b + a + b + a + b + a + b + a + b + "k",
            "kkkkkkkkkkk",
            "k" + a + "k" + a + "k" + a + "k" + a + "k" + a + "k"]
    for j in range(11):
        mid = "ddd" if j >= 3 else b + a + b
        rows.append("k" + a + b + a + mid + a + b + a + "k")
    put(c, rows, x, y)


c = cv()
_pav(c, 0, 1, "c", "s")
_pav(c, 13, 1, "a", "s")
SPRITES["holding:Grand Tournament"] = fin(c)

# Charcoal Burner: turf clamp smoking, vent glow, log stack, axe in a stump
c = cv()
put(c, ["....s.....",
        ".....s....",
        "....s.....",
        "...s..s...",
        "....s.....",
        ".....s...."], 4, 6)
put(c, ["......kuuuk......",
        "....kkuuuuukk....",
        "...kuuuuuuuuuk...",
        "..kuuuduuuuduuk..",
        ".kuuuuuuuuuuuuuk.",
        ".kuuuuuuduuuuuuk.",
        "kuufuuuuuuuuufuuk",
        "kuyfuuuuuuuuufyuk",
        "kkkkkkkkkkkkkkkkk"], 0, 14)
put(c, [".kk.kk.",
        "kbbkbbk",
        "kbkkkbk",
        ".kk.kk.",
        "kbbkbbk",
        "kbkkkbk",
        "kkkkkkk"], 17, 16)
put(c, ["m", "b"], 19, 14)
SPRITES["holding:Charcoal Burner"] = fin(c)

# Kiln: bottle kiln, banded, fire mouth, stacked pots
c = cv()
put(c, [".....s.....",
        "......s....",
        ".....s.....",
        "....kkk....",
        "....krk....",
        "....krk....",
        "...krrrk...",
        "...krrrk...",
        "..krrrrrk..",
        ".krrrrrrrk.",
        ".kkkkkkkkk.",
        "krrrrrrrrrk",
        "krrrrrrrrrk",
        "krrrrrrrrrk",
        "kkkkkkkkkkk",
        "krrrkkkrrrk",
        "krrkfffkrrk",
        "krrkfyfkrrk",
        "krrkfyfkrrk",
        "kkkkkkkkkkk"], 1, 3)
put(c, ["...kk....",
        "..kcck...",
        "..kcck..k",
        ".kkkkk.kc",
        "kcckcck.k",
        "kcckcckkc",
        "kkkkkkkkk"], 14, 16)
SPRITES["holding:Kiln"] = fin(c)

# Levy Hall: timber muster hall, lit windows, red banner at the eave, spear rack with shields (original: wooden walls)
c = cv()
gable(c, 7, 4, 7)
box(c, 0, 11, 15, 12, "b")
put(c, WIN, 2, 13)
put(c, WIN, 10, 13)
put(c, ["kkkkk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk"], 5, 16)
put(c, ["cc", "cc", "cc", "c."], 15, 11)
put(c, ["m.m.m.m",
        "b.b.b.b",
        "b.b.b.b",
        "bbbbbbb",
        "b.b.b.b",
        "b.b.b.b",
        "bkcbkab",
        "kcckaak",
        "bkcbkab",
        "b.b.b.b",
        "b.b.b.b",
        "bbbbbbb"], 17, 11)
SPRITES["holding:Levy Hall"] = fin(c)

# Siege Camp: palisade, two tents with pennants, campfire
SPRITES["holding:Siege Camp"] = art([
    "....k...........k.......",
    "...kck.........kak......",
    "...k...........k........",
    "...k...........k........",
    "..kskk........kskk......",
    ".ksssdk......ksssdk.....",
    "ksssssdk....ksssssdk....",
    "ksssssdk..f.ksssssdk..s.",
    "ksssdddk.fyfksssdddk.s..",
    "kkkkkkkk.kbk.kkkkkkk....",
    "k.k.k.k.k.k.k.k.k.k.k.k.",
    "kbkbkbkbkbkbkbkbkbkbkbkb",
    "kbbbbbbbbbbbbbbbbbbbbbbk",
    "kbkbkbkbkbkbkbkbkbkbkbkk",
    "kbbbbbbbbbbbbbbbbbbbbbbk",
    "kbbbbbbbbbbbbbbbbbbbbbbk",
    "kkkkkkkkkkkkkkkkkkkkkkkk",
])

# Siege Works: covered battering ram — plank-roofed shed on a wheeled bed, iron-capped log slung on chains, head out front
SPRITES["holding:Siege Works"] = [
    "........................",
    "........................",
    "........................",
    ".............kk.........",
    "...........kkbbkk.......",
    ".........kkddddddkk.....",
    ".......kkbbbbbbbbbbkk...",
    ".....kkddddddddddddddkk.",
    "....kbbbbbbbbbbbbbbbbbbk",
    "....kddddddddddddddddddd",
    "....kbbbbbbbbbbbbbbbbbbb",
    "....kddddddddddddddddddd",
    "..kk.kkbkkkmkkkkkmkkkbkk",
    ".kmmkkkbkkkmkkkkkmkkkbk.",
    "kmmsmbbbbbbbbbbbbbbbbbbk",
    "kmmmmbbbbdbbbdbbbdbbbdbk",
    ".kmmkkkbkkkkkkkkkkkkkbk.",
    "..kk..kbk...........kbk.",
    ".....kkkkkkkkkkkkkkkkbkk",
    "....kbkbkbkbbbbbbkbkbkbb",
    ".....kkkmkkkkkkkkkkmkkkk",
    "......kbkbk......kbkbk..",
    ".......kkk........kkk...",
    "gggggggggggggggggggggggg",
]

# Battery Park: trebuchet, cocked — A-frame, long arm down with sling and stone, iron-banded counterweight up on the short end
SPRITES["holding:Battery Park"] = [
    "........kk..............",
    ".......kbbk.............",
    "......kmkbbk............",
    ".....kkmkkbbk...........",
    "....kbbbbbkbbk..........",
    "....kmmmmmkkmbk.........",
    "....kbbbbbk.kbbk........",
    "....kbbbbbkk.kbbk.......",
    "....kmmmmmkbkkbbbk......",
    ".....kkkkkkbkkbkbbk.....",
    ".........kbk..kbkbbk....",
    ".........kbkkkkbkkbbk...",
    "........kbbbbbbbbkkbbk..",
    "........kbkkkkkkbk.kbbk.",
    ".......kbk......kbk.kbbk",
    ".......kbk......kbk..ksk",
    "......kbk......kttbkkksk",
    "...kkkkbkkkkkkkktsssssk.",
    "..kbbkkkbbbbbbbbkkkbbbk.",
    "...kkbkbkkkkkkkkbkbkkk..",
    "....kkmkk......kkmkk....",
    "....kbkbk......kbkbk....",
    ".....kkk........kkk.....",
    "gggggggggggggggggggggggg",
]

# War College: hall with crossed-swords shield, watchtower, banner
c = cv()
gable(c, 7, 6, 7)
box(c, 0, 13, 15, 10, "t")
put(c, ["m.....m",
        ".m...m.",
        "..kmk..",
        "..mcm..",
        ".m.c.m.",
        "m..b..m"], 4, 14)
put(c, ["kkk", "kdk", "kdk"], 6, 20)
put(c, ["k.k.k.k", "kkkkkkk"], 16, 2)
box(c, 16, 4, 7, 19, "t")
put(c, SLIT, 19, 6)
put(c, ["kkk", "kyk", "kkk"], 18, 12)
put(c, ["kkk", "kdk", "kdk", "kdk"], 18, 18)
put(c, ["k.", "kaa", "kaa", "k.", "k."], 22, 0)
SPRITES["holding:War College"] = fin(c)


# ---------------------------------------------------------------- logistics monuments (36)
# Baggage Train: two covered carts hitched in line behind a draught horse
def _cart(c, x, y, cloth="s"):
    """Covered cart, 13 wide, 13 tall."""
    put(c, ["...kkkkkk....",
            "..k" + cloth * 6 + "k...",
            ".k" + cloth * 2 + "k" + cloth * 2 + "k" + cloth * 2 + "k..",
            "k" + cloth * 3 + "k" + cloth * 2 + "k" + cloth * 3 + "k.",
            "k" + cloth * 3 + "k" + cloth * 2 + "k" + cloth * 3 + "k.",
            "k" + cloth * 3 + "k" + cloth * 2 + "k" + cloth * 3 + "k.",
            "kbbbbbbbbbbk.",
            "kbkbbbkbbbbkk",
            "kkkkkkkkkkkk.k"[:13]], x, y)
    put(c, WHEEL5, x, y + 8)
    put(c, WHEEL5, x + 7, y + 8)


# Baggage Train (Prowess red): supply column — draught horse in a red collar, red-canopied command wagon flying the war banner, cargo barrels behind
SPRITES["monument:Baggage Train"] = [
    "....................................",
    "....................................",
    "....................................",
    "............kkkkkkk.................",
    "............kcccccck................",
    "............kcyyyyck................",
    "............kccyycck................",
    "............kcccccck................",
    "............kcccccck................",
    "............kcckkcck................",
    "............kkk..kk.................",
    "............k.......................",
    "............k...kkkkkkkkkk..........",
    "............k.kkcrccccrccckk........",
    "............kkcccrccccrccccrk.......",
    "............kccccrccccrccccrck......",
    "...........kkccccrccccrccccrcck.....",
    "...........kkccccrccccrccccrcck.....",
    "...........kkccccrccccrccccrcck.....",
    "..kk.......kkccccrccccrccccrcck.....",
    ".kbbk......kkccccrccccrccccrcck.....",
    "kbbbbk.....kkccccrccccrccccrcck.....",
    "bkbbbdk....kkccccrccccrccccrcck.....",
    "bbbbbddk...kksssssssssssssssssk.....",
    "kkbbbbcdkkkkkkkkkkkkkkkkkkkkkkbk..kk",
    "..kbbbcybbbbkbbbbbbbbbbbbbbbbbbkkkbb",
    "..kbbbcbbbbbddbbbdbbbdbbbdbbbdbkbbbb",
    "..kbbbcbbbbbkbbkkkbbbbbbkkkbbbbkbbbb",
    "..kbbbbbbbbbkbkbbbkbbbbkbbbkbbbkmmmb",
    "..kbbkkkkbbkkkbkbkbkkkkbkbkbkkkbbbbk",
    "..kbbk..kbbk.kbbmbbk..kbbmbbk.kbbbbk",
    "..kbbk..kbbk.kbkbkbk..kbkbkbk.kmmmmk",
    "..kbbk..kbbk..kbbbk....kbbbk..kbbbbk",
    "..kddk..kddk...kkk......kkk...kbbbbk",
    "...kk....kk....................kkkk.",
    "gggggggggggggggggggggggggggggggggggg",
]

# Royal Pavilion (Prowess red): great red-and-white striped pavilion, gold crown finial, gold valance, open flap with the throne inside, striped side tents
SPRITES["monument:Royal Pavilion"] = [
    "...............kyyyk................",
    "...............kykyk................",
    "................kkkccc..............",
    ".................kkcc...............",
    "................ksck................",
    "...............ksscck...............",
    "..............kcssccsk..............",
    ".............kccssccssk.............",
    "............ksccssccssck............",
    "...........kssccssccsscck...........",
    "..........kcssccssccssccsk..........",
    ".........kccssccssccssccssk.........",
    "........ksccssccssccssccssck........",
    ".......kssccssccssccssccsscck.......",
    "......kcssccssccssccssccssccsk......",
    ".....kccssccssccssccssccssccssk.....",
    "....kkkkkkkkkkkkkkkkkkkkkkkkkkkk....",
    "....kycycycycycycycycycycycycyckcc..",
    "....kkkykykykykykykykykykykykykk....",
    "....k.kcssccssccssccssccssccsk.k....",
    "...kskkcssccssccssccssccssccskkck...",
    "..kcsskcssccssccssccssccssccskccsk..",
    ".kccsskcssccssccssccssccssccskccssk.",
    "ksccsskcssccssccssccssccssccskccssck",
    "ssccsskcssccssccsdscssccssccskccsscc",
    "ssccsskcssccssccsdscssccssccskccsscc",
    "ssccsskcssccsscsdddsssccssccskccsscc",
    "ssccsskcssccsscsdddsssccssccskccsscc",
    "ssccsskcssccsssdddddssccssccskccsscc",
    "sscdddkcssccsssdddddssccssccskdddscc",
    "sscdddkcssccssdddddddsccssccskdddscc",
    "sscdddkcssccssdddyyddsccssccskdddscc",
    "sscdddkcssccsddddccdddscssccskdddscc",
    "sscdddkcssccsdddddddddscssccskdddscc",
    "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk",
    "gggggggggggggggggggggggggggggggggggg",
]

# Ordnance Yard (key: Artillery Park): great bombard facing left, muzzle raised — hooped iron barrel on a timber bed over a planked box, dark bore in the muzzle face, pegged elevation posts at the muzzle end, curved chocks at the breech
SPRITES["monument:Artillery Park"] = [
    "....................................",
    "....................................",
    "....................................",
    "....................................",
    "..............k.....................",
    "..kk.........kbk....................",
    ".kmmkkk..k...kbk....................",
    ".kuummmkkbk..kbk....................",
    ".kuuuuukkbk..kdk....................",
    ".kudduukkbk..kbk....................",
    ".kukduummdmk.kbk....................",
    ".kukduussmumkkbk....................",
    ".kukduuuususmkdkk...................",
    ".kukduuuuuuuskbkmkk.k...............",
    ".kudduuuuduuukbksmmkmk..............",
    ".kuuuuuuuuuuukbkussmumkk.k..........",
    "..kkuuudduuuukdkuuususmmkmk.....k...",
    "....kkkkkdudukbkuuuuuussmumk...kbk..",
    ".......kbdukdkbkuuuuuukususkk.kbbk.k",
    "........kbkbkkbkduuuukbkuuummkbbk.kb",
    "........kkkkbkdkkddukbkuuuuuukbk.kbb",
    "........kbk.kkbkbkkkbkuuuuuuukbkkbbk",
    "........kdk..kbkkbkbkkdduuuuukbbbbk.",
    "........kbk..kbk.kbkkbkkdudddkbbbbkk",
    "........kbk..kdkkbkkkkbbkukkkdkkkbbb",
    "........kbk..kbkbk...kddbkbbbkkkkbbb",
    "....kkkkkbkkkkbbkkkkkkbbdddbbbbbkkkk",
    "...kdbbbbkbbbbkkbbbbbbkkkkkkkbbbbk..",
    "...kdbbbbbbbbbbbbbbbbbbbbbbbbkkkbk..",
    "...kddddddddddddddddddddddddddddkk..",
    "...kdbbbbbbbbbbbbbbbbbbbbbbbbbbbdk..",
    "...kdddddddddddddddddddddddddddddk..",
    "...kdbbbbbbbbbbbbbbbbbbbbbbbbbbbdk..",
    "...kdbbbbbbbbbbbbbbbbbbbbbbbbbbbdk..",
    "....kkkkkkkkkkkkkkkkkkkkkkkkkkkkk...",
    "gggggggggggggggggggggggggggggggggggg",
]

# Ministry of Military Strategy (Prowess red): war office — map-room hall with the campaign map in its window, keep under a red roof with the war banner, signal tower flying red pennants
SPRITES["monument:Ministry of Military Strategy"] = [
    "..........................kccc......",
    ".................kk.......kcc.......",
    "................krrk......k....kcc..",
    "...............krrrrk.....k....kc...",
    "..............kcccccck....k....k....",
    ".............krrrrrrrrk...k....k....",
    "............krrrrrrrrrrkk.k.k.kkk...",
    "...........kcccccccccccktktktktktk..",
    "..........krrrrrrrrrrrrkttttttttttk.",
    ".........krrrrrrrrrrrrrkttttttttttk.",
    "......kk..kkkkkkkkkkkkkkttttttttttk.",
    ".....kcck...kttttttttttkttttddttttk.",
    "....krrrrk..kttkkkkkkktkttttddttttk.",
    "...krrrrrrk.ktkccccccckkttttttttttk.",
    "..kcccccccckktkcccyccckkttttttttttk.",
    ".krrrrrrrrrrktkccckccckkttttttttttk.",
    "krrrrrrrrrrrktkccckccckkttttttttttk.",
    "ccccccccccccktkcyykyyckkttttddttttk.",
    "kkkkkkkkkkkkktkccckccckkttttddttttk.",
    "ttttttttttttktkccckccckkttttttttttk.",
    "ttkkkkkkkkkkktkccckccckkttttttttttk.",
    "tkeeeeeceeeektkccckccckkttttttttttk.",
    "tkelleleeeyektkccccccckkttttttttttk.",
    "tkeeceeeeeeektkcckkkcckkttttddttttk.",
    "tkeeeeeelleekttkktttkktkttttddttttk.",
    "tkeeeyeeeceekttttttttttktkkkttkkktk.",
    "tkeeeeeeeeeektttkkkkkttkkccckkccckk.",
    "ttkkkkkkkkkkkttkddkddktkkccckkccckk.",
    "ttttkddddkttkttkddkddktkkccckkccckk.",
    "ttttkddddkttkttkddkddktkkccckkccckk.",
    "ttttkddddkttkttkddkddktkkccckkccckk.",
    "ttttkddddkttkttkddkddktkkccckkccckk.",
    "ttttkddddkttkttkddkddktkkccckkccckk.",
    "ttttkddddkttkttkddkddktktkkkttkkktk.",
    "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk..",
    "gggggggggggggggggggggggggggggggggggg",
]


# ---------------------------------------------------------------- kit: buildings
def house(c, x, y, w, h, wall="w", roof="r", timber=True, door=None, wins=(), chimney=None):
    """Gabled building: walls w x h with top-left (x, y); roof sits above y. w odd.
    door = column offset of a 3-wide door; wins = column offsets of 3x3 windows (row y+1);
    chimney = column offset of a 2-wide chimney with smoke."""
    half = (w - 1) // 2
    if chimney is not None:
        put(c, [".s.", "s..", ".s.", "kk.", "uk.", "uk.", "uk."], x + chimney, y - half - 2)
    gable(c, x + half, y - half, half, roof)
    box(c, x, y, w, h, wall)
    if timber and wall == "w":
        for xx in range(x + 3, x + w - 2, 4):
            vline(c, xx, y + 1, y + h - 2, "b")
        hline(c, x + 1, x + w - 2, y + 4, "b")
    for o in wins:
        put(c, WIN, x + o, y + 1)
    if door is not None:
        put(c, ["kkk"] + ["kdk"] * 4, x + door, y + h - 6)


ANVIL = ["kkkkkk.", "kmmmmmk", ".kkmk..", "..kmk..", ".kkkkk."]


# ================================================================ BATCH 2: arms
# group: smithy — plaster house, chimney smoke, steel shield on the wall, glowing forge door, anvil in front (original layout)
c = cv()
house(c, 3, 12, 19, 11, timber=False, chimney=14)
put(c, [".kkk.", "kmmmk", "kmumk", "kmmmk", ".kmk.", "..k.."], 6, 14)
put(c, ["kkkk", "kffk", "kfyk", "kfyk", "kffk", "kffk"], 15, 17)
put(c, ANVIL, 0, 18)
SPRITES["group:g_arms"] = fin(c)

# Carpentry: timber workshop, sawhorse with a log and saw, plank stack
c = cv()
house(c, 0, 12, 13, 11, wall="b", timber=False, door=8)
for xx in (3, 6):
    vline(c, xx, 13, 21, "k")
put(c, WIN, 1, 14)
put(c, ["..kkkkkkkk",
        ".kbbbbbbbbk",
        "kbkbbbbbbkbk",
        ".kkkkkkkkkk.",
        "..k.k...k.k.",
        ".k...k.k...k",
        "k.....k.....k"[:11]], 13, 16)
put(c, ["m.", "mm", "mm", "m."], 18, 13)
SPRITES["holding:Carpentry"] = fin(c)

# Fletchery: timber hut, lit window, archery target on a tripod with an arrow in the gold (original layout)
c = cv()
house(c, 0, 13, 11, 10, wall="b", timber=False, door=6, wins=(1,))
put(c, ["..kkkkk..",
        ".kccccck.",
        "kcsssssck",
        "kcscccsck",
        "kcscycsck",
        "kcscccsck",
        "kcsssssck",
        ".kccccck.",
        "..kkkkk.."], 14, 7)
put(c, ["cbbbbbb"], 11, 11)
put(c, ["...kbk...", "...kbk...", "..kb.bk..", "..kb.bk..", ".kb...bk.", ".kb...bk.", "kb.....bk"], 14, 16)
SPRITES["holding:Fletchery"] = fin(c)

# Tannery: workshop, hide stretched on a frame, steaming vat
c = cv()
house(c, 0, 12, 13, 11, door=8, wins=(1,))
put(c, ["bbbbbbb",
        "bk.k.kb",
        "b.sss.b",
        "bksssk" + "b",
        "b.sss.b",
        "bk.k.kb",
        "bbbbbbb",
        "b.....b",
        "b.....b",
        "b.....b"], 13, 9)
put(c, [".s.", "s..", "kkkk", "kuek"[:4], "kuuk", "kkkk"], 20, 17)
SPRITES["holding:Tannery"] = fin(c)

# Joinery: workshop, bench with clamp and a finished chair
c = cv()
house(c, 0, 12, 13, 11, door=8, wins=(1,))
put(c, ["..mm.....",
        "kkkkkkkk.",
        "kbbbbbbk.",
        "kkkkkkkk.",
        "kb....kb.",
        "kb....kb.",
        "kb....kb."], 13, 16)
put(c, ["k..", "b..", "b..", "bbb", "b.b", "b.b"][::1], 21, 16)
SPRITES["holding:Joinery"] = fin(c)

# Furnace: stone furnace house, tall chimney with smoke, glowing mouth, ore heap
c = cv()
put(c, [".s.", "..s", ".s.", "s.."], 13, 0)
box(c, 12, 4, 4, 10, "u")
box(c, 0, 10, 16, 13, "t")
for y0 in (12, 15, 18):
    for x0 in range(1, 15, 3):
        c[y0][x0 + (y0 // 3) % 2] = "u"
put(c, [".kkkkk.", "kkfffkk", "kfyyyfk", "kfyyyfk", "kfffffk"], 5, 17)
put(c, ["..kk..", ".kuuk.", "kuumuk", "kumuuuk"[:6], "kkkkkk"], 17, 18)
SPRITES["holding:Furnace"] = fin(c)

# Blacksmith: open-fronted smithy, hearth glow, hood and chimney, anvil with hammer
c = cv()
house(c, 0, 12, 15, 11, wall="t", timber=False, chimney=9)
put(c, ["kkkkkkkkkkk",
        "kdddddddddk",
        "kdkkkkkkddk",
        "kdkfffkdddk",
        "kdkfyfkdmdk",
        "kdkkkkkdmdk",
        "kdddddddddk"], 2, 15)
put(c, ANVIL, 16, 18)
put(c, ["mm", ".b", ".b"], 18, 15)
SPRITES["holding:Blacksmith"] = fin(c)

# Armory: stone store, shield blazon over the door, weapon rack
c = cv()
house(c, 0, 12, 15, 11, wall="t", timber=False, door=6)
put(c, ["kkkkk", "kcack", "kcack", ".kck.", "..k.."], 5, 13)
put(c, ["m.m.m.m",
        "m.m.m.m",
        "b.b.b.b",
        "bbbbbbb",
        "b.b.b.b",
        "b.bkkkk"[:7],
        "b.kmmmk",
        "bbkmmmk",
        "b.kmmmk",
        "b.b.b.b"], 16, 13)
SPRITES["holding:Armory"] = fin(c)

# Master Workshop: forge wing with chimney, gabled hall with a great gear
c = cv()
put(c, [".y.", "y..", ".y."], 1, 2)
box(c, 1, 5, 3, 9, "u")
box(c, 0, 12, 12, 11, "u")
put(c, ["kkkk", "kffk", "kfyk", "kfyk", "kffk"], 3, 17)
house(c, 11, 11, 13, 12, door=16)
put(c, [".k.k.", "kmmmk", ".mkm.", "kmmmk", ".k.k."], 12, 12)
put(c, WIN, 19, 12)
SPRITES["holding:Master Workshop"] = fin(c)

# Gilded Foundry: thatch-gold roof workshop, crucible pouring gold into a mould, ingot stack
c = cv()
house(c, 0, 12, 13, 11, roof="y", wall="t", timber=False, door=8, wins=(1,))
put(c, ["kkkkk..",
        "kmmmk..",
        ".kmmyk.",
        "..kkky.",
        ".....y.",
        "....kyk",
        "....kyk",
        "...kkkkk"], 14, 12)
put(c, [".kkk.", "kyyyk", "kkkkkk", "kyykyyk"[:6]], 18, 19)
SPRITES["holding:Gilded Foundry"] = fin(c)

# Stable: long timber stable, three stall doors with horse heads, hay bale
c = cv()
gable(c, 10, 3, 10)
box(c, 0, 13, 21, 10, "b")
for x0 in (1, 8, 15):
    put(c, ["kkkkk", "kdddk", "kdbbk", "kdbhk", "kkkkk", "kbkbk", "kkbkk", "kbkbk", "kkkkk"][:9], x0, 13)
put(c, ["kkkk", "kyyk", "kyyk"], 20, 20)
SPRITES["holding:Stable"] = fin(c)

# Forge: twin chimneys with sparks, great hearth, quench trough
c = cv()
put(c, ["y......y.", ".y....y..", "y.....y.y"], 3, 0)
box(c, 3, 3, 3, 9, "u")
box(c, 12, 3, 3, 9, "u")
put(c, ["..kkkkkkkkkkkkk..",
        ".kuuuuuuuuuuuuuk.",
        "kuuuuuuuuuuuuuuuk"], 0, 9)
box(c, 0, 12, 18, 11, "u")
put(c, ["..kkkkkkk..",
        ".kkfffffkk.",
        "kkfffyfffkk",
        "kfffyyyfffk",
        "kffyyyyyffk",
        "kfffyyyfffk"], 3, 16)
put(c, ["kkkkkk", "keeeek", "kkkkkk"], 18, 20)
SPRITES["holding:Forge"] = fin(c)

# Tiltyard: tilt barrier with list posts, pennants, viewing stand
c = cv()
put(c, ["kcc.......kaa."] * 2 + ["k.........k..."] * 9, 0, 6)
put(c, ["kkkkkkkkkkkkkkkkkkkkkkkk",
        "kscscscscscscscscscscsck",
        "kkkkkkkkkkkkkkkkkkkkkkkk",
        ".kb...kb...kb...kb...kb.",
        ".kb...kb...kb...kb...kb.",
        ".kb...kb...kb...kb...kb."], 0, 17)
put(c, ["kkkkkkkk", "kaayyaak", "kbbbbbbk", "khhhhhhk", "kbbbbbbk"], 14, 7)
put(c, ["k......k", "k......k", "k......k", "k......k", "k......k"], 14, 12)
SPRITES["holding:Tiltyard"] = fin(c)

# Court Armoury: stone hall, royal hangings, crest with crossed blades over the door, tall windows
c = cv()
house(c, 0, 10, 23, 13, wall="t", timber=False, door=10)
put(c, ["aa", "aa", "aa", "aa", "a."], 2, 12)
put(c, ["aa", "aa", "aa", "aa", "a."], 19, 12)
for o in (5, 10, 15):
    put(c, WINT, o, 11)
put(c, ["m...m", ".kak.", ".kak.", "m.k.m"], 9, 4)
SPRITES["holding:Court Armoury"] = fin(c)

# Advanced Blast Furnace (Industry blue): dark iron furnace with a tall smoking stack and roaring tapping door, bellows driven by a waterwheel fed from a blue flume, ingots stacked beside it
SPRITES["monument:Advanced Blast Furnace"] = [
    ".....s..............................",
    "....................................",
    "......s.............................",
    "....s...............................",
    ".......s............................",
    "...kkkkkk...............kkkkkkkkkkkk",
    "..kuuuuuuk.............keeeeeeeeeeee",
    "..kuuuuuuk.............kbbbbbbbbbbbb",
    "..kuuuuuuk..............ekkkkkkkkkkk",
    "..kuuuuuuk..............e...........",
    "..kuuuuuuk..............e...........",
    "..kuuuuuuk..............e...........",
    "..kuuuuuuk..............ekkkkk......",
    "..kuuuuuukkkkkkkkk.....kkbbbbbkk....",
    "..kuuuuukkuuuuuuuukk..kbbbbbbbbbk...",
    "..kuuukkuuuuuuuuuuuukkbbbkkbkkbbbk..",
    "..kuukuuuuuuuuuuuuuuukbbk.kbk.kbbbk.",
    "..kukuuduuuduuuduuuduukdbkkbkkbkbbk.",
    "..kkuuuuuuuuuuuuuuuuuuukkbkbkbk.kbbk",
    "..kkuuuuuuuuuuuuuuuuuuukkkbbbkkkkbbk",
    "..kkuduuuduuuduuuduuudukbbbbbbbbbbbk",
    "...kuuuuuuuuuuuuuuubbbbbbkbbbkkkkbbk",
    "...kuuuuuukkkkkkkuueeeeeebkbkbk.kbbk",
    "...kuuudukfffffffkuduuudbkkbkkbkbbk.",
    "...kuuuukfffffffffkuuuukk.kbk.kbbbk.",
    "...kuuuukffffyffffkuuuukbkkbkkbbbk..",
    "...kuduukffyyyyyffkuudukbbbbbbbbk...",
    "...kuuuukffyyyyyffkuuuukkbbbbbkk....",
    "...kuuuukffyyyyyffkuuuuk.kkkkk......",
    "...kuuudkffyyyyyffkduuud............",
    "...kuuuukffyyyyyffkuuuuk............",
    ".kkkkkuukffyyyyyffkuuuuk............",
    "ksmksmkukffyyyyyffkuudukkkkkkkkkkkkk",
    "mmmmmmkukfffffffffkuuuukeeeeeeeeeeee",
    "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk",
    "gggggggggggggggggggggggggggggggggggg",
]


# ================================================================ BATCH 3: commerce
def stall(c, x, y, w, a="c", b="s", goods="yfl", h=9):
    """Market stall w wide: striped awning, counter of goods, posts. h tall (>= 9)."""
    put(c, ["k" * w], x, y)
    put(c, ["k" + "".join(a if (i // 2) % 2 == 0 else b for i in range(w - 2)) + "k"], x, y + 1)
    put(c, ["k" + "".join(a if (i // 2) % 2 == 0 else b for i in range(w - 2)) + "k"], x, y + 2)
    put(c, ["".join("k" if i % 2 == 0 else a if (i // 2) % 2 == 0 else b for i in range(w))], x, y + 3)
    for j in range(4, h):
        c[y + j][x + 1] = "b"
        c[y + j][x + w - 2] = "b"
    g = y + h - 6
    gd = "".join(goods[(i // 3) % len(goods)] if i % 3 else "k" for i in range(w - 4))
    put(c, ["." + "".join("k" if ch != "k" else "." for ch in gd)], x + 1, g)
    put(c, ["k" + gd + "k"], x + 1, g + 1)
    put(c, ["k" * (w - 2)], x + 1, g + 2)
    put(c, ["k" + "b" * (w - 4) + "k"], x + 1, g + 3)
    put(c, ["k" + "".join("k" if i % 5 == 4 else "b" for i in range(w - 4)) + "k"], x + 1, g + 4)
    put(c, ["k" * (w - 2)], x + 1, g + 5)


def water(c, y, x0=0, x1=None):
    x1 = len(c[0]) - 1 if x1 is None else x1
    for j in range(y, len(c)):
        for x in range(x0, x1 + 1):
            c[j][x] = "s" if (j == y and x % 5 == 1) else "e"


# group: market stall with striped awning and goods
c = cv()
stall(c, 1, 9, 22, h=14)
put(c, ["kkkk", "kbbk", "kbbk"], 5, 20)
put(c, [".kk.", "kssk", "kyyk"], 15, 20)
SPRITES["group:g_commerce"] = fin(c)

# Alchemy: purple-roofed stone workshop; shelf of blue, red and purple flasks with herbs; cauldron over a fire (original layout)
c = cv()
house(c, 0, 11, 11, 12, roof="a", wall="t", timber=False, door=6, wins=(1,))
put(c, [".s...", "s.s..", ".s..."], 11, 8)
put(c, ["..k..", ".kek.", ".kek.", "keeek", "keeek", "kkkkk"], 11, 12)
put(c, ["l.l.", ".l..", ".kk.", "kcck", "kcck", "kkkk"], 16, 11)
put(c, [".k.", "kak", "kak", "kak", "kkk"], 20, 12)
put(c, ["kkkkkkkkkkkkk", "kbbbbbbbbbbbk", "kkkkkkkkkkkkk"], 11, 17)
put(c, ["kkkkkkkk", "kuuuuuuk", ".kuuuuk.", "..fyf..."], 13, 19)
SPRITES["holding:Alchemy"] = fin(c)

# Weavery: workshop, loom with warp threads, bolts of dyed cloth hanging
c = cv()
house(c, 0, 12, 11, 11, door=6, wins=(1,))
put(c, ["bbbbbbbbbbbbb",
        "b.k.k.k.k.k.b",
        "bccakkyyaccab",
        "bccakkyyaccab",
        "bccakkyyaccab",
        "bccakkyyaccab",
        "bc.a..y..c.ab",
        "b...........b",
        "bbbbbbbbbbbbb",
        "b...........b",
        "b...........b"], 11, 12)
SPRITES["holding:Weavery"] = fin(c)

# Jewelry Foundry: gilded-roof shop, gem sign, crucible furnace with chimney
c = cv()
house(c, 0, 12, 13, 11, roof="y", wall="t", timber=False, door=8)
put(c, [".kak.", "kaaak", ".kak.", "..k.."], 1, 14)
put(c, [".s.", "s..", "kk.", "uk.", "uk.", "uk."], 17, 9)
put(c, ["..kkkkk..", ".kuuuuuk.", "kuuuuuuuk", "kuukkkuuk", "kukfyfkuk", "kukfffkuk", "kuuuuuuuk", "kkkkkkkkk"], 14, 15)
SPRITES["holding:Jewelry Foundry"] = fin(c)

# Market Square: two stalls flanking a stone market cross
c = cv()
stall(c, 0, 13, 10, "c", "s", "yfl")
stall(c, 14, 13, 10, "a", "s", "ysf")
put(c, ["..k..", ".kmk.", "..k..", "..k..", "..t..", "..t..", ".ktk.", ".ktk.", "kkkkk", "kttttk"[:5]], 9, 12)
SPRITES["holding:Market Square"] = fin(c)

# Spice Merchant: great orange tent, open front, sacks of spice
c = cv()
put(c, ["..........k.........", ".........kck........"], 2, 4)
for i in range(10):
    for x in range(11 - i - 1, 11 + i + 2):
        edge = x in (11 - i - 1, 11 + i + 1)
        c[6 + i][x] = "k" if edge else ("f" if (x + i) % 4 else "c")
hline(c, 0, 22, 16, "k")
box(c, 1, 16, 21, 7, "f")
put(c, ["kkkkkkk", "kdddddk", "kdddddk", "kdddddk", "kdddddk", "kdddddk"], 8, 17)
for x0, col in ((1, "y"), (16, "c"), (19, "f")):
    put(c, [".kk.", "kssk", "k" + col + col + "k", "kssk", "kkkk"], x0, 18)
SPRITES["holding:Spice Merchant"] = fin(c)

# Harbor: stone quay, bollard, moored cog with furled sail, water
c = cv()
water(c, 19)
put(c, ["kkkkkkkkkk", "kttttttttk", "ktuttuttuk", "kttttttttk"], 0, 15)
put(c, [".kk.", "kmmk", "kkkk"], 2, 12)
put(c, ["......k......",
        "......kcc....",
        "......k......",
        "...kkkkkkk...",
        "...kssssssk..",
        "...kssssssk..",
        "....kkkkkk...",
        "......k......",
        "kk....k....kk",
        "kbkkkkkkkkkbk",
        ".kbbbbbbbbbk.",
        "..kbbbbbbbk..",
        "...kkkkkkk..."], 11, 7)
SPRITES["holding:Harbor"] = fin(c)

# Merchant Quarter: three tall townhouses, stepped gables, shop windows
c = cv()
for x0, h0, col in ((0, 7, "w"), (8, 3, "w"), (16, 6, "w")):
    put(c, ["..kkk...", ".kkrkk..", ".krrrk..", "kkrrrkk.", "krrrrrk."], x0, h0)
    box(c, x0, h0 + 5, 7, 18 - h0, col)
    for yy in range(h0 + 6, 19, 4):
        put(c, WIN, x0 + 2, yy)
    put(c, ["kkkk", "kydk", "kydk", "kydk"][:4], x0 + 1, 19)
SPRITES["holding:Merchant Quarter"] = fin(c)

# Money Lending: pillared counting house, stone pediment with a coin, steps
c = cv()
put(c, ["..........kk..........",
        "........kkttkk........",
        "......kktttttt kk......"[:22],
        "....kkttttkyktttkk....",
        "..kkttttttkyykttttkk..",
        "kkttttttttkkkttttttttkk"[:22],
        "kkkkkkkkkkkkkkkkkkkkkk"], 1, 4)
c[6][1 + 14] = "t"
box(c, 1, 11, 22, 9, "w")
for x0 in (3, 7, 15, 19):
    put(c, ["kk", "tt", "tt", "tt", "tt", "tt", "tt"], x0, 12)
put(c, ["kkkk", "kyyk", "kyyk", "kyyk", "kyyk", "kyyk", "kyyk"], 10, 12)
put(c, ["kkkkkkkkkkkkkkkkkkkkkkkk", "kuuuuuuuuuuuuuuuuuuuuuuk", "kkkkkkkkkkkkkkkkkkkkkkkk"], 0, 20)
SPRITES["holding:Money Lending"] = fin(c)

# Shipyard: hull ribs on a slipway, scaffold crane with hoisted plank
c = cv()
put(c, ["kkkkkkkkkk", "........kb", "........kb", "........m.", ".......kbbk", "........m.", ".........."], 13, 3)
for y0 in range(4, 22):
    c[y0][22] = "b"
c[3][22] = "k"
put(c, ["k.k.k.k.k.k.k.k.k",
        "kbkbkbkbkbkbkbkbk",
        "kbkbkbkbkbkbkbkbk",
        ".kbkbkbkbkbkbkbk.",
        ".kbbbbbbbbbbbbbk.",
        "..kbbbbbbbbbbbk..",
        "...kkkkkkkkkkk..."], 1, 12)
put(c, ["kkkkkkkkkkkkkkkkkkkkkkkk", "kbbbbbbbbbbbbbbbbbbbbbbk", "kbkbbbbkbbbbkbbbbkbbbbkk"[:24], "kkkkkkkkkkkkkkkkkkkkkkkk"], 0, 19)
SPRITES["holding:Shipyard"] = fin(c)

# Courtyard: arcaded range with a red tiled cornice, over a diagonal-tiled paved court with a few dropped goods (original layout)
c = cv()
hline(c, 0, 23, 5, "k")
for x in range(24):
    c[6][x] = "w" if x % 4 == 2 else "r"
    c[7][x] = "r"
    c[8][x] = "w"
    c[9][x] = c[10][x] = c[12][x] = c[13][x] = "w" if x % 3 == 0 else "d"
    c[11][x] = "t"
    for y in range(14, 23):
        c[y][x] = "t" if (x + y) % 4 == 0 else "s"
for (x, y, ch) in ((8, 17, "c"), (17, 19, "a"), (4, 21, "y"), (20, 15, "w")):
    c[y][x] = ch
SPRITES["holding:Courtyard"] = fin(c)

# Artisan Workshop: workshop with hanging sign, potter's wheel and glazed vases
c = cv()
house(c, 0, 12, 13, 11, door=8, wins=(1,))
put(c, ["kkkk", ".kbk", ".kak"], 12, 13)
put(c, [".kk.", "kcck", "kcck", ".kk."], 14, 19)
put(c, [".k.", "kak", "kak", "kak", ".k."], 18, 18)
put(c, [".kk..", "kyyk.", ".kyyk", ".kkk."], 19, 19)
SPRITES["holding:Artisan Workshop"] = fin(c)

# Court Artists: purple-roofed studio, easel with a painted canvas, marble bust on a plinth
c = cv()
house(c, 0, 12, 13, 11, roof="a", door=8, wins=(1,))
put(c, ["..k..",
        ".kkkkk",
        ".klyek",
        ".kycak",
        ".klllk",
        ".kkkkk",
        ".k.k.k",
        "k..k..k",
        "k..k..k"], 13, 13)
put(c, [".kk.", "kssk", "kssk", ".kk.", "kssk", "ktttk"[:4], "kttk", "kttk"], 20, 14)
SPRITES["holding:Court Artists"] = fin(c)

# Emporium: tall warehouse with loading doors, hoist beam with a bale over the quay
c = cv()
water(c, 21)
put(c, ["...kk.....", "..krrk....", ".krrrrk...", "krrrrrrk.."], 3, 2)
gable(c, 7, 2, 7)
box(c, 0, 9, 15, 12, "w")
for xx in (3, 11):
    vline(c, xx, 10, 19, "b")
put(c, ["kkkk", "kbbk", "kbbk", "kkkk"], 6, 10)
put(c, ["kkkkk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk"], 5, 15)
put(c, WIN, 1, 11)
put(c, WIN, 12, 11)
put(c, ["kkkkkkkkk", "bbbbbbbbb", "........m", "........m", ".......kk", ".......kbk", ".......kkk"], 13, 6)
put(c, ["kkkkkkkkkk", "kbbbbbbbbk"], 14, 19)
SPRITES["holding:Emporium"] = fin(c)


# ---------------------------------------------------------------- commerce monuments (36)
# Aristocratic Court (Industry blue): palace under blue roofs with blue pennants, gold cornice and balcony, central pavilion, rows of lit windows, gold coffers at the doors
SPRITES["monument:Aristocratic Court"] = [
    ".................k..................",
    "...kee..........kyk.............kee.",
    "...ke...........kyyk............ke..",
    "...k............kyyk............k...",
    "...k............kkkk............k...",
    "..kak..........keeeak..........kek..",
    ".kaeek........keeeaeek........keeek.",
    "kaeeeak......keeeaeeeak......keeeaek",
    "aeeeaeek....keeeaeeeaeek....keeeaeee",
    "eeeaeeeak..keeeaeeeaeeeak..keeeaeeea",
    "eeaeeeaeekkeeeaeeeaeeeaeekkeeeaeeeae",
    "eaeeeaeeekeeeaeeeaeeeaeeeakeeaeeeaee",
    "kkkkkkkkkeeeaeeeaeeeaeeeaeekkkkkkkkk",
    "wwwwwkkkeeeaeeeaeeeaeeeaeeeakkkwwwww",
    "wwwwkyyykkkkkkkkkkkkkkkkkkkkyyykwwww",
    "wwyykykykykykkkykykykykkkykykykyywww",
    "wwyywkwkwkwkeekkwkwkwkeekkwkwkkyywww",
    "wwwwwkwwwwwkeekwwwwwwkeekwwwwwkwwwww",
    "wwwwwkwwyywkeekwyywwykeekywwwwkwwwww",
    "wwwwwkwwyywkeekwyywwykeekywwwwkwwwww",
    "wwwwwkwwyywkeekkykwkykeekywwwwkwwwww",
    "wwyywkwwwwwkeekykykykkeekwwwwwkyywww",
    "wwyywkwwwwwwkkyyyyyyyykkwwwwwwkyywww",
    "wwwwwkwwwwwwwkkkkkkkkkkwwwwwwwkwwwww",
    "wwwwwkwwwwwwwwwwwwwwwwwwwwwwwwkwwwww",
    "wwwwwkwwyywwyywkkkkkkwwwyywwwwkwwwww",
    "wwwwwkwwyywwyykddddddkwwyywwwwkwwwww",
    "wwyywkwwyywwyykddddddkwwyywwwwkyywww",
    "wwyywkwwwwwwwwkddyyddkwwwwwwwwkyywww",
    "wwwwwkwwwwwwwwkddyyddkwwwwwwwwkwwwww",
    "wwwwwkwwwkkkwwkddyyddkwwkkkwwwkwwwww",
    "wwwwwkwwkbybkwkddddddkwkbybkwwkwwwww",
    "wwwwwkwwkybykwkddddddkwkybykwwkwwwww",
    "wwwwwkwwkbbbkwkddddddkwkbbbkwwkwwwww",
    "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk",
    "gggggggggggggggggggggggggggggggggggg",
]

# Port Authority (Industry blue): customs tower under a blue roof flying the harbour flag, customs hall, quay with taxed crates, laden cog with a blue-striped sail, blue water
SPRITES["monument:Port Authority"] = [
    "....keee............................",
    "....kee.............................",
    "...kek..............................",
    "..keeak.............................",
    ".keeaeek.....................eee....",
    "keeaeeaek...................be......",
    "eeaeeaeeak.............kkkkkkkkkkk..",
    "eaeeaeeaeek...........ksssssssssssk.",
    "aeeaeeaeeaek..........ksssssssssssk.",
    "kkkkkkkkkkk...kk......keeeeeeeeeeek.",
    "kttttttttk...keak.....keeeeeeeeeeek.",
    "ktttyytttk..keaeek....ksssssssssssk.",
    "ktttyytttk.keaeeaek...ksssssssssssk.",
    "kttttttttkkeaeeaeeak..keeeeeeeeeeek.",
    "kttttttttkeaeeaeeaeek.keeeeeeeeeeek.",
    "ktttttttkeaeeaeeaeeaekksssssssssssk.",
    "ktttyytkeaeeaeeaeeaeeaksssssssssssk.",
    "ktttyyttkkkkkkkkkkkkkkkeeeeeeeeeeek.",
    "ktttttttkwwyywwwwyywwkksssssssssssk.",
    "ktttttttkwwwwwwwwwwwwkksssssssssssk.",
    "ktttttttkwwwwkkkkwwwwkkkkkkkkkkkkk..",
    "ktttyyttkwwwkddddkkkkkbbbbk.b..kkk..",
    "ktttyyttkwwwkdddkbbbbkbbbbk.b.kbbbk.",
    "ktttttttkwwwkdddkbbbbkbbbbk.b.kbbbk.",
    "ktttttttkwwwkdddkkkkkkbbbbkkbkkbbbkk",
    "ktttttttkwwwkdddkbbbkkkkkkbbbbbkkkbb",
    "ktttttttkwwwkdddkbbkbbbbbbbbbbbbbbbb",
    "bkkkkkkkkkkkkkkkkkkkkbbbbbbbbbbbbbbk",
    "bbbbbbbbbbbbbbbbbbbbbkbbbbbbbbbbbbkk",
    "kkbkkkkkbkkkkkbkkkkkbkkkkkkkkkkkkkee",
    "esbeeeesbeeeesbeeeesbeeeeseeeeeseeee",
    "eebeeeeebeeeeebeeeeebeeeeeeeeeeeeeee",
    "eebeseeebeeseebeeesebeeeeseeeeeeseee",
    "eebeeeeebeeeeebeeeeebeeeeeeeeeeeeeee",
    "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
    "gggggggggggggggggggggggggggggggggggg",
]


# ================================================================ BATCH 4: court
# group: hall between two banner turrets
c = cv()
for x0 in (0, 18):
    put(c, ["k...", "kaa.", "kaa.", "k...", "k..."], x0 + 2, 1)
    put(c, ["k.k.k.", "kkkkkk"], x0, 6)
    box(c, x0, 8, 6, 15, "t")
    put(c, SLIT, x0 + 2, 10)
    put(c, WIN, x0 + 1, 16)
gable(c, 11, 6, 6)
box(c, 5, 12, 14, 11, "t")
for o in (7, 14):
    put(c, WINT, o, 13)
put(c, ["kkkk", "kddk", "kddk", "kddk", "kddk", "kddk"], 10, 17)
put(c, ["kak", "kak", ".k."], 10, 13)
SPRITES["group:g_court"] = fin(c)

# Inn: two-storey half-timber with jettied upper floor, hanging sign, lantern, barrels
c = cv()
gable(c, 8, 2, 8)
box(c, 0, 10, 17, 6, "w")
for xx in (4, 8, 12):
    vline(c, xx, 11, 14, "b")
for o in (1, 5, 13):
    put(c, WIN, o, 11)
hline(c, 0, 16, 15, "k")
box(c, 1, 16, 15, 7, "w")
put(c, ["kkkk", "kddk", "kddk", "kddk", "kddk", "kddk"], 7, 16)
put(c, WIN2[:3], 2, 17)
put(c, WIN, 12, 17)
put(c, ["kkkkk", "....k", "..kkkk", "..kyyk", "..kbbk", "..kkkk"][:6], 16, 9)
put(c, ["k.", "y."], 6, 18)
put(c, [".kkk.", "kbbbk", "kmmmk", "kbbbk", ".kkk."], 18, 18)
SPRITES["holding:Inn"] = fin(c)

# Jester's Court: purple-roofed hall, harlequin facade, belled pennant pole
c = cv()
gable(c, 8, 1, 8, "a")
put(c, [".y."], 7, 0)
box(c, 0, 9, 17, 14, "a")
for j in range(10, 22):
    for x in range(1, 16):
        q = ((x // 2) + (j // 2)) % 3
        c[j][x] = "cay"[q]
put(c, ["kkkkk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk"], 6, 16)
put(c, ["kc..", "kccy", "kc..", "kyy.", "ka..", "kaay", "k...", "kcc.", "k..y", "k...", "k...", "k...", "k...", "k...", "k...", "k...", "k...", "k...", "k...", "kk.."], 19, 3)
SPRITES["holding:Jester's Court"] = fin(c)

# Bell Tower: stone campanile, open belfry with the bell, spire, clock face
c = cv()
put(c, ["....k.....", "....kk....", "...krrk...", "...krrk...", "..krrrrk..", "..krrrrk..", ".krrrrrrk.", "krrrrrrrrk", "kkkkkkkkkk"], 7, 0)
box(c, 7, 9, 10, 14, "t")
put(c, ["kkkkkk", "kddddk", "kdkkdk", "kdyydk", "kyyyyk", "kyyyyk", "kkkkkk"], 9, 9)
put(c, ["kk", "kk"], 11, 16)
put(c, ["kkkk", "kddk", "kddk", "kddk"], 10, 19)
for y0 in (11, 14, 17, 20):
    c[y0][8] = "u"
    c[y0 + 1][15] = "u"
SPRITES["holding:Bell Tower"] = fin(c)

# Embassy: colonnaded residence, flags of many houses along the cornice
c = cv()
for x0, col in ((1, "c"), (6, "a"), (11, "l"), (16, "e"), (20, "y")):
    put(c, ["k" + col + col, "k" + col + col, "k..", "k..", "k.."], x0, 3)
hline(c, 0, 23, 8, "k")
hline(c, 0, 23, 9, "t")
hline(c, 0, 23, 10, "k")
box(c, 1, 11, 22, 12, "w")
for x0 in (3, 7, 15, 19):
    put(c, ["kk"] + ["tt"] * 9, x0, 11)
put(c, ["kkkk", "kddk", "kddk", "kddk", "kddk", "kddk", "kddk"], 10, 16)
put(c, WIN, 10, 12)
SPRITES["holding:Embassy"] = fin(c)

# Academy: lecture hall under a gilded lantern dome, open-book roundel
c = cv()
put(c, ["..k..", ".kyk.", "..k..", ".kyk.", "kyyyk"], 9, 0)
put(c, ["...kkkkkkk...", "..kyyyyyyyk..", ".kyyyyyyyyyk.", "kkkkkkkkkkkkk"], 5, 5)
box(c, 2, 9, 20, 14, "t")
hline(c, 2, 21, 11, "k")
put(c, ["kkkkk", "kswsk", "kswsk", "kkkkk"][:4], 9, 12)
c[13][11] = "k"; c[14][11] = "k"
for o in (4, 16):
    put(c, WINT, o, 13)
put(c, ["kkkkk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk"], 9, 17)
hline(c, 0, 23, 22, "u")
SPRITES["holding:Academy"] = fin(c)

# University: tall central gate tower, two wings with purple roofs, rows of lit windows
c = cv()
put(c, ["..kk..", ".kaak.", "kaaaak", "kkkkkk"], 9, 0)
box(c, 9, 4, 6, 19, "t")
put(c, ["kkkk", "kyyk", "kkkk"], 10, 6)
put(c, WINT, 10, 10)
put(c, ["kkkk", "kddk", "kddk", "kddk", "kddk", "kddk", "kddk"], 10, 16)
for x0 in (0, 15):
    gable(c, x0 + 4, 7, 4, "a")
    box(c, x0, 11, 9, 12, "t")
    for o in (1, 5):
        put(c, WINT, x0 + o, 12)
        put(c, WIN, x0 + o, 17)
SPRITES["holding:University"] = fin(c)

# Courier Network: dovecote tower with birds, post stable with a saddled horse at the door
c = cv()
put(c, ["s...s..", ".s.s...", "......s"], 1, 0)
put(c, ["..kk..", ".kaak.", "kaaaak", "kkkkkk"], 1, 3)
box(c, 1, 7, 6, 16, "w")
for y0 in (8, 11, 14):
    put(c, ["kdk", "kkk"][:1], 2, y0)
    put(c, ["d.d"], 2, y0 + 1)
put(c, ["kkkk", "kddk", "kddk", "kddk", "kddk"], 2, 18)
house(c, 7, 13, 11, 10, door=None, wins=(1,))
put(c, ["kkkkk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk"], 11, 17)
put(c, ["..kk..", ".kbbk.", "kbbk..", "kbbbbbk"[:6], ".kbbbbk", ".kb..kb", ".kb..kb"][:7], 17, 16)
SPRITES["holding:Courier Network"] = fin(c)


# ---------------------------------------------------------------- court monuments (36)
# Senate Hall: temple front, pediment with a laurel boss, eight columns, broad steps
c = cv(36, 35)
for i in range(7):
    for x in range(17 - 2 * i - 1, 19 + 2 * i + 1):
        edge = x in (17 - 2 * i - 1, 19 + 2 * i) or i == 6
        c[6 + i][x] = "k" if edge else "t"
put(c, [".kk.", "kyyk", ".kk."], 16, 9)
hline(c, 1, 34, 13, "k")
hline(c, 1, 34, 14, "y")
hline(c, 1, 34, 15, "k")
box(c, 2, 16, 32, 13, "d")
for x0 in range(3, 33, 4):
    put(c, ["kkk"] + ["sts"] * 11 + ["kkk"], x0, 16)
put(c, ["kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk", "ktttttttttttttttttttttttttttttttk", "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk"[:33]], 1, 29)
put(c, ["kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk", "kuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuk"], 0, 32)
c[34] = list("kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk")
SPRITES["monument:Senate Hall"] = fin(c)

# Studium Generale (four Established standings): grand university — clock-and-bell gate tower under a slate spire, two long college ranges with dormered slate roofs, lit study windows, cloister arcade, the four domain banners (red, gold, black, blue), open-book gate
SPRITES["monument:Studium Generale"] = [
    "................kyyk................",
    "................kkak................",
    ".............k.kkaakk.k.............",
    "............kakkaakakkak............",
    "............kakaakaakkak............",
    "............kkaakaakaak.............",
    "....k....k..ktkkkkkkkktk.k....k.....",
    "...kak..kak.kttkkkkkkttkkak..kak....",
    "..kaaakkaaakktkkkkkkkktkaaakkaaak...",
    "..kkykkkkykkktkssksssktkkykkkkykk...",
    "..kkkkakkkkkktkssksssktkkkkkakkkak..",
    ".kkaaakaaakaktksskkksktkaakaaakaaak.",
    "kkaaakaaakaaktkssssssktkakaaakaaakak",
    "kaaakaaakaaaktkksssskktkkaaakaaakaaa",
    "aaakaaakaaakktukkkkkkttkaaakaaakaaak",
    "kkkkkkkkkkkkkttkddddkttkkkkkkkkkkkkk",
    "ttttttttttttkttkdyydkttktttttttttttt",
    "ttyttyttyttykttkdyydkutkttyttyttyttt",
    "ttyttyttyttykttkddddkttkttyttyttyttt",
    "ttkkkktkkkktkttkddddkttkkkkktkkkkttt",
    "tkcccckyyyykktutkkkkuttkddddkeeeektt",
    "tkcccckyyyykktttkkkktttkddddkeeeektt",
    "tkcyyckyccykkttkyssykttkdssdkeyyektt",
    "tkcyyckyccykkttkskkskutkdssdkeyyektt",
    "tkcccckyyyykktttkkkktttkddddkeeeektt",
    "tkcccckyyyykkttyyyyyyttkddddkeeeektt",
    "tkcccckyyyykktkddddddktkddddkeeeektt",
    "tkcccckyyyykktkddddddktkddddkeeeektt",
    "tkckkckykkykktkddddddktkdkkdkekkektt",
    "uukuukukuukuktkddddddktkkuukukuukuuu",
    "tddtddtddtddktkddddddktktddtddtddtdd",
    "tddtddtddtddktkddddddktktddtddtddtdd",
    "tddtddtddtddktkddddddktktddtddtddtdd",
    "tddtddtddtddktkddddddktktddtddtddtdd",
    "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk",
    "gggggggggggggggggggggggggggggggggggg",
]


# ================================================================ BATCH 5: devotion
CROSS = [".k.", "kkk", ".k.", ".k."]


def steeple(c, x, y, h=6, roof="r"):
    """Narrow spire 5 wide topped by a cross, apex cross at (x+2, y); h rows of roof."""
    put(c, CROSS, x + 1, y)
    for i in range(h):
        hw = i // 2
        for xx in range(x + 2 - hw, x + 3 + hw):
            c[y + 4 + i][xx] = "k" if xx in (x + 2 - hw, x + 2 + hw) else roof


# group: chapel, steeple and cross, lit lancets, arched door
c = cv()
steeple(c, 9, 0, 6)
box(c, 9, 10, 5, 4, "t")
gable(c, 11, 8, 6)
box(c, 4, 14, 15, 9, "w")
put(c, WINT, 6, 15)
put(c, WINT, 14, 15)
put(c, [".kkk.", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk"][:7], 9, 16)
SPRITES["group:g_devotion"] = fin(c)

# Chandlery: shop with dipped-candle racks, great candle sign
c = cv()
house(c, 0, 12, 13, 11, door=8, wins=(1,))
put(c, ["k.k.k", "s.s.s", "s.s.s"], 2, 16)
put(c, ["..y..", "..f..", ".kkk.", ".kwk.", ".kwk.", ".kwk.", ".kwk.", ".kwk.", ".kwk.", ".kwk.", "kkkkk", "kbbbk", "kbbbk", "kkkkk"][::1], 14, 9)
put(c, [".y.y.", ".s.s.", ".s.s.", "kkkkk", "kbbbk"], 19, 18)
SPRITES["holding:Chandlery"] = fin(c)

# Interrogation Chambers: squat dark keep, barred windows, iron-studded door, red lantern
c = cv()
put(c, ["k.k.k.k.k.k.k.k.k.", "kkkkkkkkkkkkkkkkkk"], 1, 7)
box(c, 1, 9, 18, 14, "u")
for x0 in (3, 13):
    put(c, ["kkkk", "kmdm"[:4], "kdmd"[:4], "kkkk"], x0, 11)
put(c, ["kkkkkk", "kmdmdk", "kdmdmk", "kmdmdk", "kdmdmk", "kmdmdk"], 7, 17)
put(c, ["kkk", "..k", "..k", ".kck", ".kck", "..k"], 19, 9)
SPRITES["holding:Interrogation Chambers"] = fin(c)

# Priory: bellcote chapel with cross, cloister arcade range
c = cv()
put(c, ["...k....................",
        "..kkk...................",
        "...k....................",
        "..kkk...................",
        "..kyk...................",
        "..kkk...................",
        ".krrrk..................",
        ".krrrk..................",
        "krrrrrk.................",
        "krrrrrrk.kkkkkkkkkkkkkkk",
        "krrrrrrrkrrrrrrrrrrrrrrk",
        "krrrrrrrrkrrrrrrrrrrrrrk",
        "kkkkkkkkkkkkkkkkkkkkkkkk",
        "kwwwwwwwkttttttttttttttk",
        "kwwkykwwktkdktkdktkdkttk",
        "kwwkykwwkkdddkdddkdddktk",
        "kwwwwwwwkkdddkdddkdddktk",
        "kwwwwwwwkkdddkdddkdddktk",
        "kwwwkdwwkkdddkdddkdddktk",
        "kwwkddkwktttttttttttttk.",
        "kwwkddkwkuuuuuuuuuuuuuk.",
        "kkkkkkkkkkkkkkkkkkkkkkk."], 0, 1)
SPRITES["holding:Priory"] = fin(c)

# Abbey: long nave with rose window, west tower with belfry and cross
c = cv()
gable(c, 7, 6, 7)
box(c, 0, 13, 15, 10, "t")
put(c, [".kkk.", "kaycak"[:5], "kyyyk", "kcyak", ".kkk."], 5, 7)
for o in (1, 11):
    put(c, WINT, o, 15)
put(c, [".kkk.", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk"], 5, 17)
put(c, CROSS, 17, 0)
put(c, ["..k..", ".krk.", "krrrk"], 16, 4)
box(c, 15, 7, 7, 16, "t")
put(c, ["kkk", "kyk", "kkk"], 17, 9)
put(c, SLIT, 18, 14)
put(c, ["kkk", "kdk", "kdk"], 17, 19)
SPRITES["holding:Abbey"] = fin(c)

# Reliquary Sanctum (key: Reliquary): gilded shrine-house, open door showing a glowing casket, candles
c = cv()
put(c, CROSS, 10, 0)
gable(c, 11, 4, 9, "y")
box(c, 3, 13, 17, 10, "t")
put(c, ["kkkkkkk", "kdddddk", "kdyyydk", "kykkkyk", "kyyyyyk", "kdddddk", "kdddddk", "kdddddk", "kdddddk"], 8, 14)
for x0 in (4, 16):
    put(c, ["y", "s", "s", "k"], x0, 18)
SPRITES["holding:Reliquary"] = fin(c)

# Monastery: dormitory range, chapel with bellcote, garden wall with herb beds
c = cv()
house(c, 0, 12, 13, 11, wall="t", timber=False, door=5)
for o in (1, 9):
    put(c, WIN, o, 13)
put(c, ["..k...", ".kyk..", "kkkkk.", ".kak..", ".k.k.."][:3], 15, 0)
gable(c, 17, 3, 6, "r")
box(c, 12, 9, 11, 14, "w")
put(c, WINT, 16, 11)
put(c, [".kkk.", "kdddk", "kdddk", "kdddk", "kdddk"], 15, 18)
put(c, ["ktkt"], 19, 21)
SPRITES["holding:Monastery"] = fin(c)

# Execution Dock: gallows with a hooded noose on a dark stone quay (Interrogation -> Inquisitorial run), water below, gibbet cage
c = cv()
water(c, 20)
put(c, ["kkkkkkkkkkkkkk",
        "bbbbbbbbbbbbbk",
        "bk.........m..",
        "b..........m..",
        "b..........m..",
        "b.........kck.",
        "b.........kck.",
        "b.........kck.",
        "b..........k..",
        "b.............",
        "b.............",
        "b............."], 4, 3)
put(c, ["k.", "bk", "b.", "b."], 5, 4)
box(c, 0, 15, 24, 5, "u")
for x in range(2, 23, 4):
    c[17][x] = "t"
put(c, [".kkk.", "kmkmk", "kmkmk", ".kkk.", "..k.."], 18, 10)
SPRITES["holding:Execution Dock"] = fin(c)

# Hospitaller: hall with tall windows, black banner with a white cross
c = cv()
house(c, 0, 12, 15, 11, wall="t", timber=False, door=6)
for o in (2, 10):
    put(c, WINT, o, 13)
put(c, ["kkkkkkk", "bdddddd", "bddsddd", "bdssssd", "bddsddd", "bddsddd", "bdddddd", "b.ddd..", "b......", "b......", "b......", "b......", "b......", "b......", "b......", "b......", "b......", "kk....."], 16, 5)
SPRITES["holding:Hospitaller"] = fin(c)

# Episcopal Court: purple-roofed hall, mitre finial, tall windows, banners of the see
c = cv()
put(c, [".k.", "kyk", "kyk", "kak"], 10, 0)
gable(c, 11, 3, 10, "a")
box(c, 1, 13, 21, 10, "t")
put(c, ["aa", "aa", "ay", "aa", "a."], 2, 14)
put(c, ["aa", "aa", "ay", "aa", "a."], 19, 14)
for o in (5, 15):
    put(c, WINT, o, 14)
put(c, ["kkkkk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk"], 9, 17)
put(c, [".kkk.", "kyyyk", ".kkk."], 9, 8)
SPRITES["holding:Episcopal Court"] = fin(c)

# Apothecary: shop with drying herbs under the eaves, jars in the window, mortar-and-pestle sign
c = cv()
house(c, 0, 12, 13, 11, door=8)
put(c, ["l.n.l.", "l.n.l.", "..n..."][:2], 2, 12)
put(c, ["kkkkk", "kekak", "kkkkk", "kclyk", "kkkkk"], 1, 15)
put(c, ["kkkkk", "....k", "..kkkk"[:6], ".kmmk.", ".kmmmk"[:6], "..kk.."], 12, 10)
put(c, ["l.l..", "lllll", ".kkk.", "kbbbk", "kbbbk", "kkkkk"], 18, 17)
SPRITES["holding:Apothecary"] = fin(c)

# Infirmary: long ward with red cross over the door, row of lit windows, bench
c = cv()
gable(c, 11, 4, 11)
box(c, 0, 15, 23, 8, "w")
for o in (1, 5, 15, 19):
    put(c, WIN, o, 16)
put(c, ["..k..", ".kck.", "kcccck"[:5], ".kck.", "..k.."], 9, 8)
put(c, ["kkkkk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk"], 9, 17)
SPRITES["holding:Infirmary"] = fin(c)

# Pilgrimage Site: stone cross on a grassy mound, worn path, candles, a pilgrim with a staff (original layout)
c = cv()
put(c, ["..........kkkk..........",
        "..........kttk..........",
        "..........kttk..........",
        "......kkkkkttkkkkk......",
        "......kttttttttttk......",
        "......kttttttttttk......",
        "......kkkkkttkkkkk......",
        "..........kttk..........",
        "..........kttk..........",
        "..........kttk..........",
        "..........kttk..........",
        "..........kttk..........",
        ".........kkuukk........."], 0, 1)
for y, x0, x1 in ((14, 7, 16), (15, 5, 18), (16, 3, 20), (17, 2, 21), (18, 1, 22), (19, 0, 23), (20, 0, 23), (21, 0, 23), (22, 0, 23)):
    for x in range(x0, x1 + 1):
        c[y][x] = "n" if (x * 7 + y * 3) % 11 == 0 else "l"
    if y < 19:
        c[y][x0] = c[y][x1] = "k"
hline(c, 8, 15, 13, "k")
for (x, y) in ((11, 14), (12, 15), (12, 16), (11, 17), (10, 18), (10, 19), (11, 20), (11, 21), (12, 22)):
    c[y][x] = "s"
for x in (5, 17):
    c[15][x] = "y"; c[16][x] = "s"
put(c, ["..h..", ".kak.", "kaaak", "kaaak", ".a.a."], 18, 12)
vline(c, 22, 11, 17, "b")
SPRITES["holding:Pilgrimage Site"] = fin(c)

# Unforgotten Shrine: wayside shrine on a plinth, lit niche, candles, offerings
c = cv()
put(c, ["........k...............",
        ".......krk..............",
        "......krrrk.............",
        ".....krrrrrk............",
        "....krrrrrrrk...........",
        "....kkkkkkkkk...........",
        ".....kdddddk............",
        ".....kdyyydk............",
        ".....kykkkyk............",
        ".....kdyyydk............",
        ".....kkkkkkk............",
        ".......ktk..............",
        ".......ktk......y.......",
        "..y....ktk......s...y...",
        "..s....ktk......s...s...",
        "..s....ktk...c..s...s...",
        "..s..cktttkc.cc.s...s...",
        "kkkkkkkkkkkkkkkkkkkkkkk.",
        "kuuuuuuuuuuuuuuuuuuuuuk.",
        "kkkkkkkkkkkkkkkkkkkkkkk."], 0, 3)
SPRITES["holding:Unforgotten Shrine"] = fin(c)


# ---------------------------------------------------------------- devotion monuments (36)
# Papal Palace (Piety gold): white basilica-palace under a great gold dome with the triple-crowned tiara, gold-capped bell towers, columned front, gold banners, tithe coffers at the steps
SPRITES["monument:Papal Palace"] = [
    "................kyk.................",
    "...............kyyyk................",
    "..............kysysyk...............",
    "...k...........kyyykk...........k...",
    "..yky........kkycycykkk........yky..",
    "...k........kyykkkkkyffk........k...",
    "..kyk......kyysyyyyyyyffk......kyk..",
    ".kyyyk....kyysyyyyyyyyyffk....kyyyk.",
    "kyyyyyk...kyysyyyyyyyyyffk...kyyyyyk",
    "yyyyyyyk.kyyyyyyyyyyyyyyffk.kyyyyyyy",
    "yyyyyyyykkyyyyyyyyyyyyyyffkkyyyyyyyy",
    "yyyyyyyyykyyyyyyyyyyyyyyffkyyyyyyyyy",
    "kkkkkkkkk.kkkkkkkkkkkkkkkk.kkkkkkkkk",
    "wwwwwwwk..kwwddwwddwwddwwk..kwwwwwww",
    "wwwwwwwk..kwwddwwddwwddwwk..kwwwwwww",
    "wwwdwwwk..kwwwwwwwwwwwwwwk..kwwwdwww",
    "wwwdwwkkkkkwwwwwwwwwwwwwwkkkkkwwdwww",
    "wwwwwkyyyyykkkkkkkkkkkkkkyyyyykwwwww",
    "wwwwwwkkkkkkkkkkkkkkkkkkkkkkkkwwwwww",
    "wwwwwwkwwkkkstwstwstwstwkkkstkwwwwww",
    "wwwwwwkwkyyyktwstwstwstkyyyktkwwwwww",
    "wwwwwwkwkyyyktwstwstwstkyyyktkwwwwww",
    "wwwdwwkwkysyktwstwstwstkysyktkwwdwww",
    "wwwdwwkwksssktwstwstwstksssktkwwdwww",
    "wwwwwwkwkysyktwstwstwstkysyktkwwwwww",
    "wwwwwwkwkyyyktwyyyyyystkyyyktkwwwwww",
    "wwwwwwkwkyyyktkddddddktkyyyktkwwwwww",
    "wyyyyykwkyyyktkddddddktkyyyktkyyyyyw",
    "wwwwwwkwkykyktkddyyddktkykyktkwwwwww",
    "wwwwwwkwwktkstkddyyddktwktkstkwwwwww",
    "wwwwwwkwwstkkkkddyyddkkkktwstkwwwwww",
    "wwwwwwkwwskbybkddddddkbybkwstkwwwwww",
    "wwwwwwkwwskybykddddddkybykwstkwwwwww",
    "wwwwwwkwwwkbbbkddddddkbbbkwwwkwwwwww",
    "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk",
    "gggggggggggggggggggggggggggggggggggg",
]

# Inquisitorial Palace (Piety gold on black): black gothic hall, pinnacled spires tipped in gold, the gold all-seeing eye over an iron portcullis, black-and-gold banners, candlelit slits
SPRITES["monument:Inquisitorial Palace"] = [
    "................kyyk................",
    "................kuuk................",
    ".........kk.....kuuk.....kk.........",
    "........kyyk...kuuuuk...kyyk........",
    "........kuuk...kuuuuk...kuuk........",
    "...kk...kuuk...kuuuuk...kuuk...kk...",
    "..kyyk.kuuuuk.kuuuuuuk.kuuuuk.kyyk..",
    "..kuuk.kuuuuk.kuuuuuuk.kuuuuk.kuuk..",
    "..kuuk.kuuuuk.kuuuuuuk.kuuuuk.kuuk..",
    ".kuuuukuuuuuukkuuuuuukkuuuuuukuuuuk.",
    ".kuuuukuuuuuukkuuuuuukkuuuuuukuuuuk.",
    ".kuuuukuuuuuukkuuuuuukkuuuuuukuuuuk.",
    "kuuuuukuuuuuukkuuuuuukkuuuuukuuuuuuk",
    "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk",
    "kuuuuuuuuuuuuuuuuyuuuuuuuuuuuuuuuuuk",
    "kuuuuuuuuuuuuuykkkkkyuuuuuuuuuuuuuuk",
    "kudukkkkuuduuukyyyyykuduuudukkkkuuuk",
    "kuukddddkuuuukyykkkyykuuuuukddddkuuk",
    "kuukddddkuuuykykdsdkykyuuuukddddkuuk",
    "kuukddddkuuudkyykkkyykuuduukddddkuuk",
    "kuukdyydkfuuuukyyyyykuuuufukdyydkuuk",
    "kuukdyydkfuuuuykkkkkyuuuufukdyydkuuk",
    "kudkyddykfduuuduuyduuuduufdkyddykuuk",
    "kuukdyydkuuuuuuuuuuuuuuuuuukdyydkuuk",
    "kuukddddkuuuukkkkkkkkkkuuuukddddkuuk",
    "kuukddddkuuukkkkkkkkkkkkduukddddkuuk",
    "kuukddddkuuukkmmkmmkmmkkuuukddddkuuk",
    "kuukddddkuuukkmmkmmkmmkkuuukddddkuuk",
    "kudkdkkdkudukkkkkkkkkkkkuudkdkkdkuuk",
    "kuuukuukuuuukkmmkmmkmmkkuuuukuukuuuk",
    "kuuuuuuuuuuukkmmkmmkmmkkuuuuuuuuuuuk",
    "kuuuduuuduuukkkkkkkkkkkkduuuduuuduuk",
    "kuuuuuuuuuuukkmmkmmkmmkkuuuuuuuuuuuk",
    "kuuuuuuuuuuukkmmkmmkmmkkuuuuuuuuuuuk",
    ".kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk.",
    "gggggggggggggggggggggggggggggggggggg",
]

# Sacred Preceptory (Piety gold + Prowess red): fortress-house of the Oathsworn — pale stone gatehouse and wall towers, crenellated curtain, white standard with the red oath-sword, gold banners bearing the red oath-sword
SPRITES["monument:Preceptory of the Knight's Templar"] = [
    ".................ksscssk............",
    ".................kscccsk............",
    ".................ksscssk............",
    ".................ksscssk............",
    ".................kkkkkk.............",
    "............k.k.kkk.k.k.............",
    "...........ksksksksksksk............",
    "...........kssssssssssssk...........",
    "...........kssssssssssssk...........",
    "...........ksddsstsssddsk...........",
    "k.k.k.k....ksddssssssddsk...k.k.k.k.",
    "tktktktk...kssskkkkkksssk..ktktktktk",
    "ttttttttk..ksskyyyyyykssk..ktttttttt",
    "ttttttttk..ksskyyccyykstk..ktttttttt",
    "ttttttttk..ksskyyccyykssk..ktttttttt",
    "tttddtttk..ksskyccccykssk..ktttddttt",
    "ttkkkkttk..ksskyyccyykssk..kttkkkktt",
    "tkyyyyktk.kkstkyyccyykssk.kktkyyyykt",
    "tkyccykktktksskyyccyyksskktktkyccykt",
    "tkcccckktttksskyyccyykssktttkkcccckt",
    "tkyccykktttksskyyyyyykssktttkkyccykt",
    "tkyccykktttksskykkkkykstktttkkyccykt",
    "tkyccykktttkssskssssksssktttkkyccykt",
    "tkyccykktttksddssssssddsktttkkyccykt",
    "tkyccykktttksddssssssddsktttkkyccykt",
    "tkyccykktttkstsyyyyyytssktttkkyccykt",
    "tkyyyykktttksskddddddkssktttkkyyyykt",
    "ttkkkktktttksskddddddkssktttktkkkktt",
    "tttttttktttksskddddddkssktttkttttttt",
    "tttttttktttksskddddddkstktttkttttttt",
    "tttttttktttksskddddddkssktttkttttttt",
    "tttttttktttksskddddddkssktttkttttttt",
    "tttttttktttksskddddddkssktttkttttttt",
    "tttttttktttksskddddddkssktttkttttttt",
    "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk",
    "gggggggggggggggggggggggggggggggggggg",
]

# Eternal Sepulchre (key: Exalted Basilica; Piety gold): white tomb-shrine on the pilgrims' mound under a stone cross, gold-ridged roof, gold light pouring from the open tomb down a path of candles
SPRITES["monument:Exalted Basilica"] = [
    "................kttk................",
    "...............kkttkk...............",
    "..............kttyyttk..............",
    "..............kttyyttk..............",
    "...............kkttkk...............",
    "................kttk................",
    "...............ktkktk...............",
    "..............kttuttuk..............",
    ".............kttuttuttk.............",
    "............kttuttuttutk............",
    "...........kttuttuttuttuk...........",
    "..........kttuttuttuttuttk..........",
    ".........kttuttuttuttuttutk.........",
    "........kttuttuttuttuttuttuk........",
    "........kkkkkkkkkkkkkkkkkkkk........",
    "........ksstsssssssssssstssk........",
    "........ksstsssskkkksssstssk........",
    "........ksstssskffffkssstssk........",
    "........ksstssskffffkssstssk........",
    "........ksstsskfyyyyfksstssk........",
    "........ksstsskfyyyyfksstssk........",
    "........ksstsskfyyyyfksstssk........",
    "........ksstsskfyyyyfksstssk........",
    ".......kksstsskfyyyyfksstsskk.......",
    ".....kklksstsskfyyyyfksstssklkk.....",
    "...kklllksssyskfyyyyfksysssknllkk...",
    ".kklnllllkkkskkkkyykkkkskkklllnllkk.",
    "klllllnllllllllllyynllllllllllllnllk",
    "llllllllnlylllllyyyylnlllyllllllllnl",
    "llllllllllsllllllyyllllnlsllllllllll",
    "lllllllyllllnlllyyyylllllnllylllllll",
    "lnlllllsllllllnllllllllllllnslllllll",
    "lllnllllllllllllnllllllllllllnllllll",
    "lllllnllllllllllllnllllllllllllnllll",
    "lllllllnllllllllllllnllllllllllllnll",
    "gggggggggggggggggggggggggggggggggggg",
]


# ================================================================ BATCH 6: husbandry
BARREL = [".kkk.", "kbbbk", "kmmmk", "kbbbk", "kmmmk", "kbbbk", ".kkk."]
HAY = [".kkkk.", "kyyyyk", "kybyyk", "kyyyyk", "kkkkkk"]
SKEP = [".kk.", "kyyk", "kkkk", "kyyk", "kydk"]


def tree(c, x, y, fruit=None):
    """Round deciduous tree 11 wide, 15 tall, top-left (x, y); fruit key dots the canopy."""
    put(c, ["...kkkkk...",
            ".kklllllkk.",
            "klllllllllk",
            "klllllllllk",
            "klllllllllk",
            "klllllllllk",
            ".klllllllk.",
            "..kkkbkkk..",
            ".....b.....",
            ".....b.....",
            ".....b.....",
            ".....b.....",
            ".....b.....",
            "....kbk....",
            "....kbk...."], x, y)
    if fruit:
        for dx, dy in ((2, 2), (6, 1), (8, 3), (4, 4), (1, 4), (7, 5)):
            c[y + dy][x + dx] = fruit


def fence(c, x0, x1, y):
    """Post-and-rail fence, 4 tall, from x0 to x1, top at y."""
    for x in range(x0, x1 + 1):
        c[y + 1][x] = "b"
        c[y + 3][x] = "b" if c[y + 3][x] == "." else c[y + 3][x]
    for x in range(x0, x1 + 1, 4):
        for j in range(4):
            c[y + j][x] = "k"


# group: plaster barn, braced double doors, loft hatch, hay bale (original: plaster walls)
c = cv()
gable(c, 10, 2, 10)
box(c, 1, 12, 19, 11, "w")
put(c, ["kkk", "kdk", "kkk"], 9, 8)
put(c, ["kkkkkkkkk",
        "kbbbkbbbk",
        "kbkbkbkbk",
        "kbbkkkbbk",
        "kbkbkbkbk",
        "kbbbkbbbk",
        "kbbbkbbbk",
        "kbbbkbbbk",
        "kbbbkbbbk"], 6, 14)
put(c, ["kkkkk", "kyyyk", "kybyk", "kyyyk", "kkkkk"], 19, 18)
SPRITES["group:g_husbandry"] = fin(c)

# Herb Garden: cottage, raised beds of herbs and flowers, wattle fence
c = cv()
house(c, 0, 13, 9, 10, door=5)
put(c, WIN, 1, 14)
for x0, flw in ((10, "a"), (17, "y")):
    put(c, ["l" + flw + "l" + flw + "l" + flw,
            "llllll",
            "l" + flw + "l" + "l" + flw + "l",
            "kkkkkk",
            "kbbbbk"], x0, 16)
fence(c, 9, 23, 19)
SPRITES["holding:Herb Garden"] = fin(c)

# Animal Husbandry: byre with a hayloft, cow in the paddock, fence
c = cv()
house(c, 11, 12, 13, 11, wall="b", timber=False)
put(c, ["kkkk", "kyyk", "kkkk"], 15, 13)
put(c, ["kkkkk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk"], 15, 17)
put(c, ["kk..........",
        "ksk.kkkkkk..",
        "kssksskssk..",
        ".kssssskssk.",
        "..kskssssskk",
        "..kssssssk..",
        "..ks.k.ks...",
        "..kk.k.kk...",
        "..kk...kk..."][:9], 0, 14)
fence(c, 0, 10, 19)
SPRITES["holding:Animal Husbandry"] = fin(c)

# Saddlery: half-timber shop, saddle on a trestle, bridle hanging from the sign
c = cv()
house(c, 0, 12, 13, 11, door=8, wins=(1,))
put(c, ["kkkk", "...k", "..kbk", "..kbk", "...m"], 12, 10)
put(c, ["..kkk...",
        ".kbbbkk.",
        "kcbbbbck",
        "kcccccck",
        ".kkkkkk.",
        ".kb..bk.",
        ".kb..bk.",
        ".kb..bk."], 15, 15)
SPRITES["holding:Saddlery"] = fin(c)

# Vineyard: trellised vines in three tiers, grape bunches, end posts
c = cv()
for x in (0, 8, 15, 23):
    vline(c, x, 7, 22, "b")
    c[6][x] = "k"
for y0 in (7, 12, 17):
    hline(c, 0, 23, y0, "b")
    for x in range(1, 23):
        if x in (8, 15):
            continue
        c[y0 + 1][x] = "l"
        c[y0 + 2][x] = "l" if x % 3 else "n"
    for x0 in (2, 10, 17, 20):
        put(c, ["aa", "aa", ".a"], x0 + (y0 // 5) % 2, y0 + 2)
hline(c, 0, 23, 22, "k")
SPRITES["holding:Vineyard"] = fin(c)

# Orchard: two apple trees, ladder, basket of apples
c = cv()
tree(c, 0, 8, "c")
tree(c, 11, 8, "c")
put(c, ["k.k", "kkk", "k.k", "kkk", "k.k", "kkk", "k.k"], 9, 16)
put(c, [".c.c.", "kckck", "kbbbk", "kbbbk", ".kkk."], 19, 18)
SPRITES["holding:Orchard"] = fin(c)

# Bakery: house with a domed bread oven glowing, smoke, loaves on the sill
c = cv()
house(c, 0, 12, 13, 11, door=8, chimney=9)
put(c, ["kkkkk", "kyyyk", "kkkkk"], 1, 14)
put(c, ["...s....",
        "..s.....",
        "..kk....",
        "..ku.kk.",
        ".kkkkuuk",
        "kuuuuuuuk"[:8] + "k",
        "kuukkkuuk",
        "kukfffkuk",
        "kukfyfkuk",
        "kkkkkkkkk"], 14, 13)
SPRITES["holding:Bakery"] = fin(c)

# Meadery: cottage, row of straw skeps on a bench, mead barrel
c = cv()
house(c, 0, 12, 13, 11, door=8, wins=(1,))
for x0 in (13, 17):
    put(c, SKEP, x0, 13)
put(c, ["kkkkkkkk", "b......b", "b......b", "b......b", "b......b"], 13, 18)
put(c, BARREL, 21, 16)
SPRITES["holding:Meadery"] = fin(c)

# Winery: cellar house with arched door, barrels stacked on racks, grapes on the eave
c = cv()
house(c, 0, 12, 15, 11, wall="t", timber=False, door=6)
put(c, ["lalal", "laall", ".lal."], 1, 12)
put(c, WIN, 11, 13)
put(c, BARREL, 15, 9)
put(c, BARREL, 15, 16)
put(c, BARREL, 19, 16)
put(c, ["kkkkkkkkk"], 15, 15)
SPRITES["holding:Winery"] = fin(c)

# Cidery: cottage, twin-screw cider press, basket of apples, barrel
c = cv()
house(c, 0, 12, 13, 11, door=8, wins=(1,))
put(c, ["kkkkkkkkk",
        "kbbbbbbbk",
        "kkkmkmkkk",
        "..km.mk..",
        ".kkkkkkk.",
        ".kbbbbbk.",
        ".kccyckk."[:9],
        "kkkkkkkkk",
        "kb.....bk",
        "kb.....bk"], 14, 13)
put(c, [".c.", "kck", "kbk"], 21, 20)
SPRITES["holding:Cidery"] = fin(c)

# Mill: stone tower windmill, cap, four lattice sails, door and window
c = cv()
box(c, 7, 9, 9, 14, "t")
put(c, WIN, 10, 12)
put(c, ["kkk", "kdk", "kdk", "kdk", "kdk"], 10, 18)
for y0 in (11, 14, 17, 20):
    c[y0][8] = "u"
    c[y0 + 1][14] = "u"
put(c, ["..kkkkk..", ".krrrrrk.", "krrrrrrrk", "kkkkkkkkk"], 7, 5)
SAIL = ["kk.......", "ksk......", "kssk.....", ".kssk....", "..kssk...", "...ksbk..", "....kbbk."]
for flipx in (False, True):
    for flipy in (False, True):
        rows = SAIL[::-1] if flipy else SAIL
        rows = [r[::-1] for r in rows] if flipx else rows
        put(c, rows, 12 if flipx else 3, 7 if flipy else 0)
put(c, [".kk.", "kbbk", "kbbk", ".kk."], 10, 5)
SPRITES["holding:Mill"] = fin(c)


# ---------------------------------------------------------------- husbandry monument (36)
# Manor House (Industry blue): half-timbered manor under blue slate roofs, twin chimneys, gabled wings, lit windows, its wheat fields in front
SPRITES["monument:Manor House"] = [
    "...........s............s...........",
    "...........ks...........ks..........",
    "..........kuuk.........kuuk.........",
    "..........kuuk.........kuuk.........",
    "..........kuuk.........kuuk.........",
    "..........kuukkkkkkkkkkkuuk.........",
    "..........kuukeeaeeeaeekuuk.........",
    "..........kuukeaeeeaeeekuuk.........",
    ".....k....kkkeaeeeaeeeaekk....k.....",
    "....kek..keeeaeeeaeeeaeeeak..kek....",
    "...keeakkeeeaeeeaeeeaeeeaeekkeaek...",
    "..keeaekeeeaeeeaeeeaeeeaeeeakaeeek..",
    ".keeaeeekkkkkkkkkkkkkkkkkkkkaeeeaek.",
    "keeaeeeakwwwbwwwbwwwbwwwbwwkeeeaeeek",
    "eeaeeeaekwyybwyybwyybwyybwwkeeaeeeae",
    "eaeeeaeekwyybwyybwyybwyybwwkeaeeeaee",
    "kkkkkkkkkwwwbwwwbwwwbwwwbwwkkkkkkkkk",
    "wyybwyybkwwwbwwwbwwwbwwwbwwkbwyybwww",
    "wyybwyybkwwwbwwwbwwwbwwwbwwkbwyybwww",
    "wwwbwwwbkwbbbbbbbbbbbbbbbbwkbwwwbwww",
    "wwwbwwwbkwwwbwwwbwwwbwwwbwwkbwwwbwww",
    "wbbbbbbbkwwwbwwwkkkkbwwwbwwkbbbbbbbw",
    "wwwbwwwbkwwwbwwkddddkwwwbwwkbwwwbwww",
    "wwwbwwwbkwwwbwwkddddkwwwbwwkbwwwbwww",
    "wwwbwwwbkwwwbwwkddddkwwwbwwkbwwwbwww",
    "wwwbwwwbkwwwbwwkddddkwwwbwwkbwwwbwww",
    "wwwbwwwbkwwwbwwkddddkwwwbwwkbwwwbwww",
    "wwwbwwwbkwwwbwwkddddkwwwbwwkbwwwbwww",
    "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk",
    "llyyllyyllyyllyyllyyllyyllyyllyyllyy",
    "yybbyybbyybbyybbyybbyybbyybbyybbyybb",
    "llyyllyyllyyllyyllyyllyyllyyllyyllyy",
    "yybbyybbyybbyybbyybbyybbyybbyybbyybb",
    "llyyllyyllyyllyyllyyllyyllyyllyyllyy",
    "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk",
    "gggggggggggggggggggggggggggggggggggg",
]


# ================================================================ BATCH 7: secrecy
LAMPPOST = [".kkk.", "kyyyk", ".kkk.", "..k..", "..k..", "..k..", "..k..", "..k..", "..k..", ".kkk."]
SKULL = [".kkk.", "ksssk", "kdsdk", ".sss.", ".kdk."]


# group: shuttered dark house, lantern post
c = cv()
gable(c, 7, 4, 7, "u")
box(c, 0, 11, 15, 12, "u")
for o in (2, 10):
    put(c, ["kkk", "kdk", "kbk", "kkk"], o, 12)
put(c, ["kkk", "kdk", "kkk"], 6, 7)
put(c, ["kkkkk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk"], 5, 17)
c[19][8] = "y"
put(c, LAMPPOST, 17, 13)
SPRITES["group:g_secrecy"] = fin(c)

# Toll House: tower-house over the road, striped toll boom, strongbox
c = cv()
gable(c, 4, 0, 4)
box(c, 0, 4, 9, 19, "t")
put(c, WIN, 3, 6)
put(c, WIN, 3, 11)
put(c, ["kkk", "kdk", "kdk", "kdk", "kdk"], 3, 18)
put(c, ["kkkkkkkkkkkkkkk", "kcsscssccsscssk"[:15], "kkkkkkkkkkkkkkk"], 9, 13)
put(c, ["k", "b", "b", "b", "b", "b", "b", "k"][:7], 9, 16)
put(c, ["kk", "kb", "kb", "kb", "kb", "kb", "kk"], 22, 16)
put(c, ["kkkkk", "kbybk", "kmmmk", "kbbbk", "kkkkk"], 13, 18)
SPRITES["holding:Toll House"] = fin(c)

# Secret Cellar: cottage, cellar bulkhead doors open on steps going down, lantern
c = cv()
house(c, 0, 12, 13, 11, door=8, wins=(1,))
put(c, [".kk.......",
        "kbbk......",
        "kbbbk.....",
        "kbbbbk....",
        ".kbbbbk...",
        "..kdddddk.",
        "..kdkkkdk.",
        "..kddkkdk.",
        "..kdddkkkk",
        "kkkkkkkkkk"], 13, 13)
put(c, ["k", "y"], 22, 17)
SPRITES["holding:Secret Cellar"] = fin(c)

# Smuggler's Nook: sea cave under a cliff, lantern in the mouth, rowboat with contraband
c = cv()
water(c, 20)
put(c, ["......kkkkkk............",
        "....kkuuuuuukk..........",
        "...kuuuuuuuuuukk........",
        "..kuuuuuuuuuuuuuk.......",
        ".kuuuukkkkkuuuuuuk......",
        ".kuuukdddddkuuuuuuk.....",
        "kuuukdddddddkuuuuuuk....",
        "kuukddddydddkuuuuuuuk...",
        "kuukddkkkdddkuuuuuuuuk..",
        "kuukdkbbbkddkuuuuuuuuuk.",
        "kuukdddddddddkuuuuuuuuuk",
        "kuukdddddddddkuuuuuuuuuk"], 0, 8)
put(c, ["kkk.....", "kbbk....", "kkkkkkkkk"[:0] + ".kbkbkbk", "kkkkkkkk"][1:], 14, 18)
put(c, ["k.......k", "kbkbbkbbk", ".kbbbbbk."], 14, 19)
SPRITES["holding:Smuggler's Nook"] = fin(c)

# Syndicate Hub: huddle of tall narrow dark houses, single lit windows, connecting bridge
c = cv()
for x0, top, w in ((0, 2, 7), (8, 7, 7), (16, 0, 8)):
    gable(c, x0 + (w - 1) // 2, top, (w - 1) // 2, "u")
    box(c, x0, top + (w - 1) // 2, w, 23 - top - (w - 1) // 2, "u")
for x0, y0 in ((2, 9), (10, 13), (19, 7), (19, 13)):
    put(c, ["kkk", "kyk", "kkk"], x0, y0)
for x0, y0 in ((2, 14), (10, 18)):
    put(c, ["kkk", "kdk", "kkk"], x0, y0)
hline(c, 7, 16, 11, "k")
hline(c, 7, 16, 12, "b")
put(c, ["kkk", "kdk", "kdk", "kdk"], 19, 19)
put(c, ["kkk", "kdk", "kdk", "kdk"], 2, 19)
SPRITES["holding:Syndicate Hub"] = fin(c)

# Black Market: dark-curtained canopy, hooded dealer, contraband on the board, lantern
c = cv()
put(c, ["kkkkkkkkkkkkkkkkkkkkkkkk",
        "kaaaaaaaaaaaaaaaaaaaaaak",
        "kakakakakakakakakakakaka",
        ".b....................b."], 0, 8)
for y in range(12, 22):
    c[y][1] = "b"; c[y][22] = "b"
put(c, ["k", "y"], 19, 11)
put(c, ["..kkk..", ".kdddk.", ".kdhdk.", "kdddddk", "kdddddk", "kdddddk"], 8, 12)
put(c, ["kkkkkkkkkkkkkkkkkkkk", "kycmkyakcmykaymkcayk", "kkkkkkkkkkkkkkkkkkkk", ".kd................."[:0] + "kdddddddddddddddddk", "kkkkkkkkkkkkkkkkkkkk"[:0] + "kdddddddddddddddddk"], 2, 18)
put(c, ["kkkkkkkkkkkkkkkkkkkk"], 2, 22)
SPRITES["holding:Black Market"] = fin(c)

# Forgery Workshop: stone scriptorium (between Academy and Cipher Chamber), screw press with sheets, wax seal
c = cv()
house(c, 0, 12, 13, 11, wall="t", timber=False, door=8, wins=(1,))
put(c, ["kkkk", "kssk", "kssk", "kkkk"], 4, 13)
put(c, ["kkkkkkk",
        "kbbbbbk",
        "kk.m.kk",
        "kb.m.bk",
        "kbkkkbk",
        "kbsssbk",
        "kbkkkbk",
        "kb...bk",
        "kb...bk",
        "kk...kk"], 13, 13)
put(c, [".cc.", "cyyc", ".cc."], 20, 19)
put(c, ["kkkk"], 20, 22)
SPRITES["holding:Forgery Workshop"] = fin(c)

# Toxicarium: blue-glazed poison house on a dark stone base (sits in the Catacombs -> Charnel House run), poison plants, skull sign
c = cv()
gable(c, 11, 4, 9, "e")
for i in range(2, 9, 2):
    for x in range(11 - i + 1, 11 + i):
        if (x - 11) % 3 == 0:
            c[4 + i][x] = "k"
box(c, 2, 13, 19, 6, "d")
for x in (5, 8, 11, 14, 17):
    vline(c, x, 14, 17, "k")
for x0, a in ((3, "c"), (6, "a"), (9, "l"), (12, "c"), (15, "a"), (18, "l")):
    put(c, [a + ".", "ll", ".l"], x0, 14)
box(c, 1, 18, 21, 5, "u")
for x in range(3, 20, 4):
    c[20][x] = "t"
put(c, ["kkkk", "kddk", "kddk"], 9, 20)
put(c, SKULL, 19, 13)
SPRITES["holding:Toxicarium"] = fin(c)

# Charnel House: stone bone-house, skull over the door, bone stack against the wall
c = cv()
house(c, 0, 12, 15, 11, wall="t", timber=False)
put(c, SKULL, 5, 12)
put(c, ["kkkkk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk"][:6], 5, 17)
put(c, ["..k.k..", ".ksksk.", "kskskskk"[:7], "ksssssk", "kskskskk"[:7], "ksssssk", "kkkkkkk"], 15, 16)
put(c, [".kkk.", "ksssk", "kdsdk", ".kkk."], 16, 12)
SPRITES["holding:Charnel House"] = fin(c)

# Plague Pit (Holding; was a Monument): open lime pit of bones, warning post with red cloth, body cart, crows
c = cv()
put(c, ["k.k", ".k."], 9, 6)
put(c, ["kkkkkk", "kcccck", "kcccck", "kkkkkk", "..b...", "..b...", "..b...", "..b...", "..b...", ".kbk.."], 1, 9)
put(c, ["...kkkkkkkkkkkk...",
        ".kkssksdsskssdskk.",
        "ksskssssdssksssssk",
        "kuuuuuuuuuuuuuuuuk",
        "kkkkkkkkkkkkkkkkkk"], 2, 18)
put(c, ["kk.......",
        "bbk......",
        ".kkkkkkkk",
        ".kssdsssk",
        ".kbbbbbbk",
        ".kkkkkkkk",
        "...kkk...",
        "..kbkbk..",
        "..kkbkk..",
        "..kbkbk..",
        "...kkk..."], 15, 11)
SPRITES["holding:Plague Pit"] = fin(c)

# Beacon Towers: tall beacon tower with a fire basket, smaller relay tower, signal smoke
c = cv()
put(c, ["..s....", ".s.s...", "..f....", ".fyf...", "kfyyfk.", "kmmmmk.", ".kmmk.."], 4, 0)
box(c, 3, 7, 9, 16, "t")
put(c, ["k.k.k.k.k", "kkkkkkkkk"], 3, 6)
put(c, SLIT, 7, 9)
put(c, WIN, 6, 14)
put(c, ["kkk", "kdk", "kdk", "kdk"], 6, 19)
put(c, [".f.", "kyk", "kmk"], 16, 7)
put(c, ["k.k.k", "kkkkk"], 15, 10)
box(c, 15, 12, 5, 11, "t")
put(c, SLIT, 17, 14)
SPRITES["holding:Beacon Towers"] = fin(c)

# Forgotten Catacombs: stone arch over a dark stair going down, moss on the right, rubble either side (original: stone, not turf)
c = cv()
cx, cy = 11.5, 12
for y in range(5, 23):
    for x in range(24):
        dx, dy = x - cx, y - cy
        outer = (dy >= 0 and 3 <= x <= 20) or (dy < 0 and dx * dx + dy * dy <= 8.6 ** 2)
        inner = (dy >= 0 and 7 <= x <= 16) or (dy < 0 and dx * dx + dy * dy <= 4.6 ** 2)
        if inner: c[y][x] = "d"
        elif outer: c[y][x] = "u" if (x * 5 + y * 3) % 9 == 0 else "t"
for y in range(5, 23):
    for x in range(24):
        if c[y][x] == "." and any(0 <= x + a < 24 and 0 <= y + b < 23 and c[y + b][x + a] in "tud"
                                  for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            c[y][x] = "k"
    for x in range(24):
        if c[y][x] == "d" and any(0 <= x + a < 24 and c[y + b][x + a] in "tu" for a, b in ((1, 0), (-1, 0), (0, -1))):
            c[y][x] = "k"
for y, x0, x1 in ((18, 9, 14), (20, 8, 15), (22, 7, 16)):
    hline(c, x0, x1, y, "u")
for (x, y) in ((20, 8), (21, 9), (21, 10), (21, 11), (22, 12), (20, 9), (19, 7)):
    c[y][x] = "l"
put(c, ["kk..", "tuk.", "ttuk"], 0, 20)
put(c, ["..kk", ".kuu", "kutu"], 20, 20)
SPRITES["holding:Forgotten Catacombs"] = fin(c)

# Cipher Chamber: narrow stone tower, cipher wheel blazon, lit study, scroll rack
c = cv()
put(c, ["k.k.k.k.k", "kkkkkkkkk"], 6, 1)
box(c, 6, 3, 9, 20, "t")
put(c, ["..kkkkk..", ".kyykyyk.", "kykkykkyk", "kyykyyyyk"[:9], "kykkykkyk", ".kyykyyk.", "..kkkkk.."][::1], 6, 4)
put(c, WIN, 9, 12)
put(c, ["kkk", "kdk", "kdk", "kdk", "kdk"], 9, 18)
put(c, ["kkkkkkk", "kskskok"[:5] + "sk", "kkkkkkk", "kskskok"[:5] + "sk", "kkkkkkk", "kb...bk", "kb...bk"], 16, 16)
SPRITES["holding:Cipher Chamber"] = fin(c)


# ---------------------------------------------------------------- secrecy monuments (36)
# Ossuary Crypt: half-sunk stone crypt, bone-ringed arch, skull niches, charnel grate, black crows
c = cv(36, 35)
put(c, ["k.k", ".k."], 4, 2)
put(c, ["k.k", ".k."], 29, 5)
put(c, CROSS, 16, 1)
for i in range(9):
    for x in range(17 - i - 1, 18 + i + 1):
        c[5 + i][x] = "k" if x in (17 - i - 1, 17 + i + 1) or i == 8 else ("u" if (x + i) % 3 else "t")
box(c, 7, 14, 22, 15, "t")
for y0 in range(16, 28, 3):
    for x0 in range(8, 28, 4):
        c[y0][x0 + (y0 % 2) * 2] = "u"
put(c, ["...kkkkkkk...",
        "..kskskskssk.",
        ".kskkkkkkksk.",
        ".ksk.....ksk.",
        ".kkkdddddkkk.",
        ".ksk.ddd.ksk.",
        ".kskdddddksk.",
        ".kskdddddksk.",
        ".kskdddddksk.",
        ".kskdddddksk.",
        ".kskdddddksk."], 11, 17)
for x0 in (8, 24):
    put(c, ["kkkkk", "kdddk"] + ["k" + "".join("s" if q % 2 else "d" for q in range(3)) + "k"] + ["kkkkk"], x0, 16)
    put(c, SKULL, x0, 21)
put(c, ["kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk",
        "kuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuk",
        "kumkmkmkmuuuuuuuuuuuuuuuuuukmkmkmkmk"[:35] + "k",
        "kukskskskuuuuuuuuuuuuuuuuukskskskuuk"[:35] + "k",
        "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk"], 0, 29)
SPRITES["monument:Ossuary Crypt"] = fin(c)


# Thieves' Guild: crooked dark guildhall, leaning tower, purse sign, lantern, hidden back door
c = cv(36, 35)
put(c, ["....k....", "...kuk...", "..kuuuk..", ".kuuuuuk.", "kuuuuuuuk", "kkkkkkkkk"], 9, 0)
box(c, 9, 6, 9, 28, "u")
for y0 in (8, 14, 20):
    put(c, ["kkk", "kyk", "kkk"], 12, y0)
gable(c, 7, 11, 7, "u")
box(c, 0, 18, 15, 16, "u")
for o in (2, 10):
    put(c, ["kkk", "kdk", "kbk", "kkk"], o, 20)
put(c, ["kkkkk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk"], 5, 27)
gable(c, 25, 14, 7, "u")
box(c, 18, 21, 15, 13, "u")
put(c, ["kkkkkkk", "......k", "....kkk", "...kyyk", "...kymk", "....kk."], 26, 18)
put(c, ["kkk", "kyk", "kkk"], 21, 23)
put(c, ["kkkk", "kddk", "kddk", "kddk", "kddk"], 22, 29)
put(c, LAMPPOST, 32, 24)
SPRITES["monument:Thieves' Guild"] = fin(c)

# Outlaw Rookery (Cunning black): bandit hideout in the dark pines — blackened stilt huts joined by rope bridges, skull banner, campfire
SPRITES["monument:Outlaw Rookery"] = [
    "..................kdddddk...........",
    "..................kdsssdk.......k...",
    "..................kdsdsdk......knk..",
    "..k..............kkdddddk......knk..",
    ".knk............kbukkkkk......knndk.",
    ".knk...........kbubbk........knndnnk",
    "knndk.........kbubbubk.......kndnnnk",
    "nndnnk.......kbubbubbuk......kdnnnnk",
    "ndnnnk......kbubbubbubbk....kdnnnndn",
    "dnnnnk.....kbubbubbubbubk..kdnnnndnn",
    "nnnndnk.....kkkkkkkkkkkk...knknndnnn",
    "nnndnkuk....kddddffddddk...kkbkdnnnn",
    "nndnkubbk...kddddddddddk..kkbubknnnd",
    "ndnkubbubk..kddddddddddk.kkbubbukndn",
    "dnkubbubbuk.kddddddddddk.kbubbubbknn",
    "nkubbubbubbkbbbbbbbbbbbbkbubbubbubkn",
    "nnkkkkkkkkk.kkkkbbbkkkkkkkkkkkkkkknn",
    "nnkddffdddk..kbk....kbkknkddffdddknd",
    "ndkdddddddk..kbkbbb.kbkkdkdddddddkdn",
    "dnkdddddddkk.kbk....kbkknkdddddddknn",
    "nkbbbbbbbbssskbsbbb.kssnkssbbbbbbbkn",
    "nnkkkkkkkkkk.ssk....kbksskkkkkkkkknn",
    "nndkbknkbknnkkbkbbb.kbknndkbknkbknnd",
    "ndnkbkdkbkndnkbk....kbkndnkbkdkbkndn",
    "dnnkbknkbkdnnkbkbbb.kbkdnnkbknkbkdnn",
    "nnnkbknkbknnnkbk...kkbknnnkbknkbknnn",
    "nnnkbknkbknnnkbkbbbkkbknnnkbknkbknnn",
    "nndkbknkbknndkbk...kkbknndkbknkbknnd",
    "ndnkbkdkbkndnkbkbbbdkbkndnkbkdkbkndn",
    "dnkkbknkbkdnnkbk.kdnkbkdnnkbknkbkdnn",
    "kkdkbkkkbkkkkkbkbbbkkbkkkkkbkkkbkkkk",
    ".kdkbk.kbkkfkkbk....kbk...kbk.kbkk..",
    ".kdkbk.kbkfyfkbkbbb.kbk...kbk.kbkk..",
    ".kdkbk.kbkbbbkbk....kbk...kbk.kbkk..",
    "..k.k...k.kkk.k......k.....k...kk...",
    "gggggggggggggggggggggggggggggggggggg",
]

# Whispering Undercroft: small dark gabled house on a broad dark platform, stair arches stepping down into it (original layout)
c = cv(36, 35)
gable(c, 18, 10, 6, "u")
hline(c, 9, 27, 16, "k")
box(c, 11, 17, 15, 7, "u")
for x0 in (13, 20):
    put(c, ["kdk", "kdk"], x0, 19)
hline(c, 0, 35, 24, "k")
for y in range(25, 34):
    hline(c, 1, 34, y, "u"); c[y][0] = c[y][35] = "k"
for i in range(4):
    y = 26 + 2 * i
    x0, x1 = 8 - 2 * i, 27 + 2 * i
    hline(c, x0, x1, y, "d"); c[y][x0 - 1] = c[y][x1 + 1] = "k"
    hline(c, x0, x1, y + 1, "k"); c[y + 1][x0] = c[y + 1][x1] = "d"
hline(c, 0, 35, 34, "k")
SPRITES["monument:Whispering Undercroft"] = fin(c)

# Outrider Intercept Post (Cunning black): dark-timbered watchtower with a hooded signal lantern and black pennant; a black-cloaked outrider on a dark horse at its foot
SPRITES["monument:Outrider Intercept Post"] = [
    ".........kkdddk.....................",
    "........kdkddk......................",
    ".......kduukk.......................",
    "......kduuduuk......................",
    "....kkduuduudukk....................",
    "...kkduuduuduudkk...................",
    "...kdkkkkkkkkkkdk...................",
    "...kdddddyydddddk...................",
    "...kdddddffdddddk...................",
    "...kddddddddddddk............m......",
    "..kkddddddddddddkk...........b......",
    ".kbbkkkkkkkkkkkkbbk..........b......",
    ".kbbbbbbbbbbbbbbbbk..........b......",
    ".kbbbbbbbbbbbbbbbbk..........b......",
    "..kkkkkkkkkkkkkkkk...........b......",
    "....kbk..bb..kbk.............b......",
    "....kbk......kbk.............b......",
    "....kbk..bb..kbk.........kk..b......",
    "....kbk......kbk........kddk.b......",
    "...kbk...bb...kbk......kddddkb......",
    "...kbk........kbk......kdhddkb.kk...",
    "...kbk...bb...kbk.......kddk.bkbbk..",
    "...kbbbbbbbbbbbbk......kddddkbbbbbk.",
    "...kbk...bb...kbk.....kddddddbbbbbk.",
    "..kbk..........kbk...kkddddddbbbkk..",
    "..kbk....bb....kbk..kbccccccccbk....",
    "..kbk..........kbk..kbbbkkbkkbbk....",
    "..kbk....bb....kbk..kbbbbbbbbbbk....",
    "..kbk..........kbk..kbbbbbbbbbbk....",
    ".kbk.....bb.....kbk..kbbkkkkbbk.....",
    ".kbbbbbbbbbbbbbbbbk..kbbk..kbbk.....",
    ".kbk.....bb.....kbk..kbbk..kbbk.....",
    ".kbk............kbk..kbbk..kbbk.....",
    ".kbk.....bb.....kbk..kddk..kddk.....",
    "..k..............k....kk....kk......",
    "gggggggggggggggggggggggggggggggggggg",
]


# ================================================================ BATCH 8: works
CRATE = ["kkkkk", "kbkbk", "kkbkk", "kbkbk", "kkkkk"]
SACK = [".kk.", "kssk", "kssk", "kkkk"]


def treadwheel(c, x, y):
    """Treadwheel crane: jib over a wheel, 12 wide, top-left (x, y), 22 tall."""
    put(c, ["kkkkkkkkkkkk", "kbbbbbbbbbbk", ".kb......m..", ".kb......m..", ".kb.....kuk.", ".kb.....kuk."], x, y)
    for yy in range(y + 6, y + 22):
        c[yy][x + 2] = "b"
        c[yy][x + 1] = "k"
    put(c, ["..kkkkk..", ".kbkbkbk.", "kbkbbbkbk", "kkbbkbbkk", "kbkbbbkbk", ".kbkbkbk.", "..kkkkk.."], x, y + 14)


# group: crane over a workshop
c = cv()
treadwheel(c, 0, 1)
house(c, 9, 13, 15, 10, door=10, wins=(1, 5))
SPRITES["group:g_works"] = fin(c)

# Masonry: masons' lodge, half-built wall in a scaffold, dressed blocks and mallet
c = cv()
house(c, 0, 12, 11, 11, wall="t", timber=False, door=6)
put(c, WIN, 2, 13)
put(c, ["b.......b...",
        "bbbbbbbbbb..",
        "b.......b...",
        "b.kkkkkkbk..",
        "b.kttuttbk..",
        "bbkkkkkkbk..",
        "b.kutttubk..",
        "b.kkkkkkbkkk",
        "b.kttuttbktk",
        "b.kkkkkkbkkk"], 11, 13)
put(c, ["kkkk", "kttk", "kkkk"], 20, 20)
SPRITES["holding:Masonry"] = fin(c)

# Workyard: tall A-frame crane with a steel mast on the right, stacked timber on the left (original layout)
c = cv()
put(c, ["kkk"], 17, 0)
vline(c, 18, 1, 10, "m")
for y in range(6, 11):
    c[y][17] = c[y][19] = "b"
put(c, ["kbbbbbk"], 15, 11)
for y in range(12, 19):
    c[y][16] = c[y][20] = "b"
for y in (19, 20):
    c[y][15] = c[y][21] = "b"
for y in (21, 22):
    c[y][14] = c[y][22] = "b"
put(c, [".kkkkkkkkkk...",
        ".kdbbbbbbbbk..",
        "kkkkkkkkkkkk..",
        "kdbbbbbbbbbbk.",
        "kkkkkkkkkkkkk.",
        "kdbbbbbbbbbbbk",
        "kkkkkkkkkkkkkk"], 0, 16)
SPRITES["holding:Workyard"] = fin(c)

# Storehouse: big gabled warehouse, loft door with hoist, braced doors, sacks and crates
c = cv()
gable(c, 11, 1, 11)
put(c, ["kkkk", "kddk", "kkkk"], 10, 6)
box(c, 0, 12, 23, 11, "b")
put(c, ["kkkkkkkkk", "kbkbbbkbk", "kkbkbkbkk", "kbbkbkbbk", "kbbbkbbbk", "kbbkbkbbk", "kkbkbkbkk", "kbkbbbkbk", "kbkbbbkbk"], 7, 14)
put(c, SACK, 1, 19)
put(c, CRATE, 17, 18)
SPRITES["holding:Storehouse"] = fin(c)

# Census Hall: civic hall, ledger board over the door, clerk's lit window, scroll rolls
c = cv()
house(c, 0, 10, 19, 13, wall="t", timber=False, door=8)
put(c, ["kkkkkkkkk", "kswswswsk"[:9], "kssssssk"[:0] + "kswswswsk", "kkkkkkkkk"], 5, 12)
put(c, WIN2, 1, 15)
put(c, WIN2, 14, 15)
put(c, [".kk..", "kssk.", "kssk.", "kkkkk", "kskssk"[:5], "kkkkk"], 19, 17)
SPRITES["holding:Census Hall"] = fin(c)

# Granary: thatched granary raised on staddle stones, ladder, grain sacks
c = cv()
gable(c, 10, 2, 9, "y")
for i in range(2, 9, 2):
    for x in range(10 - i + 1, 10 + i):
        if (x + i) % 3 == 0:
            c[2 + i][x] = "b"
box(c, 2, 11, 17, 7, "b")
for x in (6, 10, 14):
    vline(c, x, 12, 16, "k")
put(c, ["kkkk", "kddk", "kddk", "kkkk"], 9, 12)
hline(c, 1, 19, 18, "k")
for x0 in (2, 9, 16):
    put(c, ["kttk", ".kk.", ".tt.", ".kk."], x0, 19)
put(c, ["k.k", "kkk", "k.k", "kkk", "k.k"], 19, 18)
SPRITES["holding:Granary"] = fin(c)

# Supply Depot: canvas store tent, stacked crates, barrels, sacks
c = cv()
put(c, ["......k.......",
        ".....kskk.....",
        "....ksssdk....",
        "...ksssssdk...",
        "..ksssssssdk..",
        ".ksssskksssdk.",
        "ksssskddksssdk",
        "kssskddddksssk",
        "kssskddddkssdk",
        "kkkkkkkkkkkkkk"], 0, 13)
put(c, CRATE, 14, 13)
put(c, CRATE, 14, 18)
put(c, CRATE, 19, 18)
put(c, [".kkk.", "kbbbk", "kmmmk", "kbbbk", ".kkk."], 19, 13)
SPRITES["holding:Supply Depot"] = fin(c)

# Trade Guild: guildhall over an open arcade, jettied timbered upper floor, guild banner
c = cv()
gable(c, 10, 0, 10)
box(c, 0, 10, 21, 6, "w")
for xx in (4, 8, 12, 16):
    vline(c, xx, 11, 14, "b")
for o in (1, 5, 13, 17):
    put(c, WIN, o, 11)
put(c, ["kkk", "kyk", "kkk"], 9, 11)
box(c, 1, 16, 19, 7, "t")
for x0 in (2, 7, 12, 16):
    put(c, ["kkk", "ddd", "ddd", "ddd", "ddd"], x0, 17)
put(c, ["k...", "kaa.", "kya.", "kaa.", "k...", "k..."], 21, 8)
SPRITES["holding:Trade Guild"] = fin(c)

# College of Engineering: hall with a great gear blazon in the gable, arch model on a trestle
c = cv()
gable(c, 8, 1, 8)
put(c, [".k.k.", "kmmmk", ".mkm.", "kmmmk", ".k.k."], 6, 4)
box(c, 0, 9, 17, 14, "t")
for o in (1, 13):
    put(c, WINT, o, 11)
put(c, ["kkkkk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk"], 6, 16)
put(c, [".kkkk.", "kttttk", "kt..tk", "kt..tk", "kkkkkkk"[:6], "kb..bk", "kb..bk", "kb..bk"], 17, 15)
SPRITES["holding:College of Engineering"] = fin(c)

# Masons' Guild: stone guildhall, slate roof, upper hall windows, hanging hammer sign
c = cv()
put(c, [".kk", ".ks"], 5, 0)
gable(c, 8, 2, 8, "u")
box(c, 0, 10, 17, 13, "t")
hline(c, 1, 15, 15, "k")
for o in (1, 7, 13):
    put(c, WIN, o, 11)
put(c, WIN, 2, 17)
put(c, WIN, 12, 17)
put(c, ["kkkkk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk"][:6], 6, 17)
put(c, ["kkkkk", "....k", "...kbk", "..kbmbk"[:7], "..kbmbk"[:7], "...kbk", "....m."], 17, 10)
SPRITES["holding:Masons' Guild"] = fin(c)

# Burgages: two narrow half-timbered plot houses, paired windows over a centred door, each with its garden strip (original layout)
c = cv()
for x0 in (0, 12):
    house(c, x0, 12, 9, 11, timber=True, door=3)
    put(c, WIN, x0 + 1, 13)
    put(c, WIN, x0 + 5, 13)
    put(c, ["l.l", "lll", "nln", "lll"], x0 + 9, 19)
SPRITES["holding:Burgages"] = fin(c)

# Citadel: white stepped keep in four tiers, red flag, dark windows and gate (original layout and colours)
c = cv()
put(c, ["kcc", "kcc", "k.."], 12, 0)
hline(c, 9, 14, 3, "k")
for y in range(4, 8): hline(c, 9, 14, y, "s")
put(c, ["d", "d"], 11, 5)
hline(c, 6, 17, 8, "k")
for y in range(9, 12): hline(c, 6, 17, y, "s")
put(c, ["d", "d"], 8, 9); put(c, ["d", "d"], 15, 9)
hline(c, 3, 20, 12, "k")
for y in range(13, 16):
    hline(c, 3, 20, y, "s"); c[y][3] = c[y][20] = "t"
put(c, ["d", "d"], 6, 13); put(c, ["d", "d"], 17, 13)
hline(c, 0, 23, 16, "k")
for y in range(17, 23): hline(c, 0, 23, y, "s")
for x in (2, 5, 18, 21):
    put(c, ["u", "u"], x, 18)
put(c, ["dddd", "dddd", "dddd", "dddd"], 10, 19)
SPRITES["holding:Citadel"] = fin(c)

# Castle Hall: white stone great hall and stair tower under red roofs, banner (Citadel -> Imperial Palace: white and red)
c = cv()
gable(c, 7, 6, 7)
box(c, 0, 13, 15, 10, "s")
for o in (2, 10):
    put(c, WINT, o, 14)
put(c, ["kkkkk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk"], 5, 17)
put(c, ["k...", "kcc.", "kcc.", "k..."], 19, 0)
put(c, ["..kkkk..", ".krrrrk.", "krrrrrrk", "kkkkkkkk"], 15, 3)
box(c, 15, 7, 8, 16, "s")
for y0 in (9, 14):
    put(c, SLIT, 18, y0)
put(c, ["kkk", "kdk", "kdk", "kdk"], 17, 19)
SPRITES["holding:Castle Hall"] = fin(c)


# ---------------------------------------------------------------- works monuments (36)
# Office of Works (Industry blue): master builders' tower rising in scaffolding — fresh stone courses, treadwheel crane lifting a block, blue guild banner with a gold cog, stacked blocks, blue awning
SPRITES["monument:Office of Works"] = [
    "....................................",
    ".......k..................kkkkkkkkkk",
    "......kbk................kbbbbbbbbbb",
    "......kbk................kkkkkkkkmkk",
    "......kbk................kbk.....m..",
    "......kbkk.k.k.k.k.......kbk.....m..",
    "......kbktktktktktkkkkkkkkbk.....m..",
    "......kbkttttttttttttttttkbk.....m..",
    "......kbkutttutttutttutttkbk.....m..",
    "......kbktttttkkkkkktttttkbk.....m..",
    "......kbkkkkkkkkkkkkkkkkkkbk...kkkkk",
    ".....kbbbbbbbbbbbbbbbbbbbbbbk.kttttt",
    "......kbkkkkkkkkkkkkkkkkkkbk..kttttt",
    "......kbkttttkeeyyeekttttkbk..kttttt",
    "......kbkttutkeyeeyekttutkbk..kttttt",
    "......kbkttttkeeyyeekttttkbk...kkkkk",
    "......kbkutttkeeeeeekutttkbk........",
    "......kbkttttkeeeeeekttttkbk........",
    "......kbkkkkkkkkkkkkkkkkkkbk........",
    ".kkkkkbbbbbbbbbbbbbbbbbbbbbbk.......",
    "keeeeekbkkkkkkkkkkkkkkkkkkbk........",
    "keeeeekbkttttttttttttttttkbk.kkk....",
    ".kkbkkkbkttutttutttutttutkbkkbbbkk..",
    "..kbk.kbkttttttttttttttttkkbbbbbbbk.",
    "..kbk.kbkutttutttutttutttkbbkkbkkbbk",
    "..kbk.kbkttttttttttttttttkbkbkbkbkbk",
    "..kbk.kbkkkkkkkkkkkkkkkkkbbkkbbbkkbb",
    "kkkbkkbbbbbbbbbbbbbbbbbbkbbbbbbbbbbb",
    "ttkkttkbkkkkkkkkkkkkkkkkkbbkkbbbkkbb",
    "ttktttkbktttttkddddktttttkbkbkbkbkbk",
    "kkkkkkkbkttuttkddddktttutkbbkkbkkbbk",
    "ttttktkbktttttkddddktttttkkbbbbbbbk.",
    "ttttktkbkutttukddddktutttkbkkbbbkk..",
    "ttttktkbktttttkddddktttttkbk.kkk....",
    "kkkkkk.k.kkkkkkkkkkkkkkkk.k.........",
    "gggggggggggggggggggggggggggggggggggg",
]

# Imperial Palace: a grander Citadel (Prowess) — white stepped keep in four tiers, each under a red tiled roof band, red pyramid roof with a gold crown, white flanking towers with red conical roofs and pennants, red war banners with a gold crown device, red studded gate
SPRITES["monument:Imperial Palace"] = [
    "..............kykyykyk..............",
    "..............kyyyyyyk..............",
    "..............kkkkkkkk..............",
    "..kcc........krrrrrrrrk.........kcc.",
    "..kc........kcccccccccck........kc..",
    "..kk.......krrrrrrrrrrrrk.......kk..",
    ".krrk.......kkkkkkkkkkkk.......krrk.",
    ".krrk........kkkkkkkkkk........krrk.",
    "krrrrk.......ksssddsstk.......krrrrk",
    "kcccck.......ksssddsstk.......kcccck",
    "krrrrk....kkkkkkkkkkkkkkkk....krrrrk",
    "rrrrrrk..krrrrrrrrrrrrrrrrk..krrrrrr",
    "cccccck.kcrrcrrcrrcrrcrrcrrk.kcccccc",
    "rrrrrrk..kkkkkkkkkkkkkkkkkk..krrrrrr",
    "rrrrrrrk.kssdsssdssdsssdstk.krrrrrrr",
    "kkkkkkk..kssdsssdssdsssdstk..kkkkkkk",
    "ssssstkkkkkkkkkkkkkkkkkkkkkkkktsssss",
    "ssssskrrrrrrrrrrrrrrrrrrrrrrrrksssss",
    "ssddkrcrrcrrcrrcrrcrrcrrcrrcrrckddss",
    "ssddskkkccckkkkkkkkkkkkkkccckkksddss",
    "sssssksscccsdssssssssssdscccstksssss",
    "sssssksscycsdssssssssssdscycstksssss",
    "sssskkkkyyykkkkkkkkkkkkkkyyykkkkssss",
    "ssskrrrrcccrrrrrrrrrrrrrrcccrrrrksss",
    "sskcrrcrcccrcrrcrrcrrcrrccccrrcrrkss",
    "ssdkkkkkccckkkkkkkkkkkkkkccckkkkkdss",
    "sssksssscccssskkkkkkkkssscccssstksss",
    "sssksssscccsskkcccccckksscccssstksss",
    "sssksssscccsskccckkcccksscccssstksss",
    "sssksssscscsskcyckkcycksscscssstksss",
    "ssskssssssssskccckkcccksssssssstksss",
    "ssskssssssssskccckkcccksssssssstksss",
    "ssskssssssssskcyckkcycksssssssstksss",
    "ssskssssssssskccckkcccksssssssstksss",
    "kkkkkkkttttttttttttttttttttttkkkkkkk",
    "gggggggggggggggggggggggggggggggggggg",
]


# ================================================================ BATCH 9: raw materials, feet strips, scenery
def mound(c, x, y, w, h, fill="t", spot="u"):
    """Rounded rock / earth mound w wide, h tall, base on row y+h-1."""
    for j in range(h):
        inset = max(0, (h - 1 - j) * (w // 2) // max(1, h) - 0)
        inset = int(round((1 - ((j + 1) / h) ** 0.5) * (w / 2)))
        x0, x1 = x + inset, x + w - 1 - inset
        for xx in range(x0, x1 + 1):
            c[y + j][xx] = "k" if xx in (x0, x1) or j == 0 else (spot if (xx * 7 + j * 3) % 11 == 0 else fill)


def pine(c, x, y, h=12):
    """Tiered evergreen, 11 wide, h tall (>= 8), tip at (x+5, y); trunk 2 rows."""
    c[y][x + 5] = "k"
    for j in range(1, h - 2):
        p = (j - 1) % 4
        hw = 1 + int(4 * j / (h - 3)) - (1 if p == 0 and j > 1 else 0)
        hw = max(1, min(5, hw))
        for xx in range(x + 5 - hw, x + 6 + hw):
            if 0 <= xx < len(c[0]):
                c[y + j][xx] = "k" if xx in (x + 5 - hw, x + 5 + hw) or p == 3 and abs(xx - x - 5) > hw - 2 else "n"
    for j in range(h - 2, h):
        c[y + j][x + 5] = "b"


# group: timbered adit in a rock mound
c = cv()
mound(c, 1, 9, 22, 14)
put(c, ["kkkkkkkk", "kbbbbbbk", "kbkkkkbk", "kbkddkbk", "kbkddkbk", "kbkddkbk", "kbkddkbk", "kkkddkkk"], 8, 15)
SPRITES["group:g_raw"] = fin(c)

# Quarry: terraced rock face, dressed blocks, shear-legs hoisting a stone
c = cv()
put(c, ["kkkkkkkkkk..............",
        "kttuttttuk..............",
        "kttttuttttkkkkk.........",
        "ktuttttkkktttuk.........",
        "kttttutkttttttkkkk......",
        "ktttttkkttuttttttk......",
        "kttuttkttttkkkkkkkk.....",
        "ktttttktttkttuttttk.....",
        "kttttkktttkttttuttk.....",
        "kkkkkkkkkkkkkkkkkkk....."], 0, 10)
put(c, ["kkkk.kkkk", "kttk.ktuk", "kkkkkkkkk", "kttkkttuk", "kkkkkkkkk"][:5], 0, 18)
put(c, ["kkk", "ktk", "kkk"], 10, 20)
put(c, ["...k...", "..k.k..", "..km.k.", ".k.m.k.", ".kkkkk.", ".kttuk.", ".kkkkk.", "k.....k", "k.....k"][:9], 15, 14)
SPRITES["holding:Quarry"] = fin(c)

# Salt Works: boiling house with smoke, shallow pans of brine, white salt heaps
c = cv()
put(c, [".s.", "s..", ".s."], 15, 2)
put(c, ["kk", "uk", "uk"], 15, 5)
house(c, 9, 13, 11, 6, wall="w", door=None)
put(c, WIN, 10, 14)
put(c, ["kkk", "kfk"], 15, 16)
put(c, ["..k.....", ".ksk....", "kssskk..", "ksssssk."], 0, 15)
put(c, ["kkkkkkkkkkkkkkkkkkkkkkkk",
        "keesekeeeeskeeeseekesek"[:23] + "k",
        "kkkkkkkkkkkkkkkkkkkkkkkk",
        "kuuuuuuuuuuuuuuuuuuuuuuk"], 0, 19)
put(c, [".k.", "ksk", "kkk"][:2], 20, 17)
SPRITES["holding:Salt Works"] = fin(c)

# Apiary: three box hives on a stand, bees, flowering meadow
c = cv()
put(c, ["y.....y......y....", "...y......y.....y."], 3, 6)
for x0 in (1, 9, 17):
    put(c, [".kkkkk.", "krrrrrk", "kkkkkkk", "kbbbbbk", "kbkkkbk", "kbbbbbk", "kbbdbbk", "kkkkkkk"], x0, 11)
put(c, ["kkkkkkkkkkkkkkkkkkkkkkkk", ".kb...kb.......kb...kb.", ".kb...kb.......kb...kb.", ]  , 0, 19)
for x in range(24):
    c[22][x] = "l" if x % 3 else ("a" if x % 2 else "y")
SPRITES["holding:Apiary"] = fin(c)

# Peat Bog: reeds, stacked cut peat, bog water, spade
c = cv()
for x0 in (0, 3, 19, 22):
    put(c, ["l.", "l.", "ll", ".l", ".l", "ll", ".l"], x0, 13)
put(c, ["..kkkk..", ".kbbbbk.", "kkkkkkkk", "kbbkbbbk", "kkkkkkkk", "kbbbkbbk", "kkkkkkkk"], 7, 13)
put(c, ["k", "b", "b", "b", "m", "m"], 16, 14)
put(c, ["kkkkkkkkkkkkkkkkkkkkkkkk", "kddeddeddddeddddeddeddek", "deeddeeddeeddeeddeeddeed"], 0, 20)
SPRITES["holding:Peat Bog"] = fin(c)

# Forestry: two firs, forester's log pile, axe in a stump
c = cv()
pine(c, 0, 3, 20)
pine(c, 13, 1, 22)
put(c, [".kk.kk.", "kbbkbbk", "kbkkbkk", ".kkbkk.", "kbbkbbk", "kbkkbkk", "kkkkkkk"], 8, 16)
SPRITES["holding:Forestry"] = fin(c)

# Fishmongery: quayside shop, fish strung under the eave, creel, water
c = cv()
water(c, 21)
house(c, 1, 11, 13, 9, door=8, wins=(1,))
put(c, ["kkkkkkkk", "k.k.k.k.", "e.e.e.e.", "eee.eee."[:0] + "e.e.e.e.", "s.s.s.s."], 14, 11)
put(c, ["kkkkkkkkkkkkkkkkkkkkkkkk", "kbbbbbbbbbbbbbbbbbbbbbbk"], 0, 19)
put(c, [".kkkk.", "kbebek", "kbbbbk", "kkkkkk"], 16, 15)
SPRITES["holding:Fishmongery"] = fin(c)

# Mine: hill with a timbered entrance, rails, ore cart, pick
c = cv()
mound(c, 0, 7, 20, 16, "u", "t")
put(c, ["kkkkkkkkk", "kbbbbbbbk", "kbkkkkkbk", "kbkdddkbk", "kbkdddkbk", "kbkdddkbk", "kbkdddkbk", "kkkdddkkk"], 3, 15)
put(c, ["kkkkkkk", "kumyumk", "kkkkkkk", ".kmk.kmk"[:7]], 14, 18)
put(c, ["kkkkkkkkkkkkkkkkkkkkkkkk"], 0, 22)
put(c, ["m.", "mm", ".b", ".b"], 22, 18)
SPRITES["holding:Mine"] = fin(c)

# Arable Land: ploughed strips with three wheat stooks
c = cv()
for x0 in (1, 9, 17):
    put(c, ["...y...", "..yyy..", "..yyy..", ".yykyy.", ".yyyyy.", "yykyyky", "yyyyyyy", "ybykyby"], x0, 11)
for x in range(24):
    c[19][x] = "b"
    c[20][x] = "y" if x % 2 else "b"
    c[21][x] = "b"
    c[22][x] = "k" if x % 3 == 0 else "b"
SPRITES["holding:Arable Land"] = fin(c)

# Common Land: grazing sheep, shepherd's hurdle fence, rough grass
c = cv()
for x0, y0 in ((0, 14), (10, 16)):
    put(c, ["kk......",
            "ksk.kkkk.",
            "kssksssskk"[:9],
            ".ksssssssk",
            ".kssssssk.",
            "..kk..kk..",
            "..kk..kk.."], x0, y0)
fence(c, 18, 23, 18)
for x in range(0, 24, 3):
    c[22][x] = "l" if c[22][x] == "." else c[22][x]
SPRITES["holding:Common Land"] = fin(c)


# ---------------------------------------------------------------- feet strips (30 wide; ground row skipped)
def strip(rows):
    w = 30
    rows = [r.ljust(w, ".")[:w] for r in rows]
    return rows + ["g" * w]


SPRITES["feet:Quarry"] = strip(["..kk..............kkk.........",
                           ".kttk..kk........kttuk...kk.k.",
                           "kttutkkttk.....kktttttk.kttktk",
                           "kttttkkttuk...kttuttttkkttkttk"])
SPRITES["feet:Salt Works"] = strip(["..k.......................k...",
                               ".ksk.......k.............ksk..",
                               "ksssk.eeeeskeeeseeeeesee.ksssk",
                               "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkk"])
SPRITES["feet:Apiary"] = strip(["..y.......y.........y.....y...",
                           ".l.a..l.y....a..l.....a..l...l",
                           "lllallllallllllallllyllllallll",
                           "llllllllllllllllllllllllllllll"])
SPRITES["feet:Peat Bog"] = strip([".l.l..................l..l.l..",
                             ".l.l...kkk........kkk.l..l.l..",
                             "dllddeekbbkddeeddkbbkdeelddeed",
                             "deeddeeddeeddeeddeeddeeddeedde"])
SPRITES["feet:Forestry"] = strip(["..kkkk..................kkkk..",
                             ".kbbbbk...l.......l....kbbbbk.",
                             "kbkbbkbk.lll.....lll..kbkbbkbk",
                             "kkkkkkkk..b.......b...kkkkkkkk"])
SPRITES["feet:Fishmongery"] = strip([".kk.......................kk..",
                                "kmbk.....................kbmk.",
                                "kbbkeeeeeeseeeeeeeeseeeeekbbk.",
                                "kkkkeeeeeeeeeeeeeeeeeeeeekkkk."])
SPRITES["feet:Mine"] = strip(["..tt.........ttt.........tt...",
                         ".tuut..m.m..tuyut.......tuut..",
                         "tuuutkkkkkktuuuuut.m.m.tuuuut.",
                         "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkk"])
SPRITES["feet:Arable Land"] = strip(["y.y.y...................y.y.y.",
                                "yyyyy...................yyyyy.",
                                "bybyb.bbbbbbbbbbbbbbbbb.bybyb.",
                                "bbbbbbybybybybybybybybybbbbbbb"])
SPRITES["feet:Common Land"] = strip([".kkk...................kkk....",
                                "ksssk.....l..l..l.....ksssk...",
                                "kssssk..l..l..l..l...kssssk...",
                                ".k.k.....................k.k.."])

# ---------------------------------------------------------------- scenery
c = cv()
pine(c, 0, 3, 20)
pine(c, 11, 8, 15)
SPRITES["scenery:tree"] = fin(c)

c = cv()
put(c, ["kkkkkkkkkk", "kbbbbbbbbk", "kbsssssbbk"[:10], "kkkkkkkkkk", "....kbk...", "....kbk...", "....kbk...", "....kbk...", "....kbk..."], 7, 14)
put(c, ["k", "b", "b"], 1, 20)
put(c, ["k", "b", "b"], 22, 20)
SPRITES["scenery:plot"] = fin(c)


# ================================================================ BATCH 10: settlement tiers (fallback), wonders
# tier:<name> — 24x24 fallback when a skyline piece is missing
c = cv()
gable(c, 7, 9, 6, "b")
box(c, 1, 15, 13, 8, "w")
put(c, WIN, 3, 16)
put(c, ["kkk", "kdk", "kdk", "kdk", "kdk"], 8, 17)
fence(c, 15, 23, 19)
SPRITES["tier:Hamlet"] = fin(c)

c = cv()
gable(c, 5, 10, 5)
box(c, 0, 15, 11, 8, "w")
put(c, WIN, 1, 16)
put(c, ["kkk", "kdk", "kdk", "kdk", "kdk"], 6, 17)
gable(c, 17, 6, 6)
box(c, 11, 12, 13, 11, "w")
put(c, WIN, 13, 13)
put(c, WIN, 19, 13)
put(c, ["kkk", "kdk", "kdk", "kdk", "kdk"], 16, 17)
SPRITES["tier:Village"] = fin(c)

c = cv()
for x0 in (1, 18):
    put(c, ["k.k.k", "kkkkk"], x0, 2)
    box(c, x0, 4, 5, 19, "t")
    put(c, SLIT, x0 + 2, 6)
put(c, ["k.k.k.k.k.k.k.k", "kkkkkkkkkkkkkkk"], 5, 9)
box(c, 5, 11, 14, 12, "t")
for o in (7, 15):
    put(c, WIN, o, 12)
put(c, ["kkkk", "kddk", "kddk", "kddk", "kddk", "kddk"], 10, 17)
SPRITES["tier:Town"] = fin(c)

c = cv()
for x0 in (0, 20):
    put(c, ["k.k.", "kkkk"], x0, 1)
    box(c, x0, 3, 4, 20, "t")
gable(c, 11, 3, 5)
put(c, ["kcc", "kcc", "k.."], 11, 0)
box(c, 4, 8, 16, 15, "t")
hline(c, 4, 19, 8, "k")
for o in (6, 15):
    put(c, WINT, o, 10)
put(c, ["kkkkkk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk"], 9, 16)
put(c, ["kkkk", "kyyk", "kkkk"], 10, 10)
SPRITES["tier:City"] = fin(c)

c = cv()
put(c, CROSS, 10, 0)
put(c, [".kkk.", "kyyyk", "kkkkk"], 9, 4)
gable(c, 11, 7, 6)
for x0 in (0, 20):
    put(c, ["k.k.", "kkkk"], x0, 4)
    box(c, x0, 6, 4, 17, "t")
box(c, 4, 13, 16, 10, "w")
for o in (5, 9, 13, 16):
    put(c, WIN, o, 14)
put(c, ["kkkk", "kddk", "kddk", "kddk", "kddk"], 10, 18)
SPRITES["tier:Metropolis"] = fin(c)


# ---------------------------------------------------------------- wonders (36)
# Colossus: crowned bronze figure, torch raised, spear grounded, stone plinth
c = cv(36, 35)
put(c, [".y.", "fyf", ".f.", "kmk", "kmk", "kmk", "kmk", "kmk"], 8, 0)
put(c, ["...y.y.y...",
        "...yyyyy...",
        "...kmmmk...",
        "..kmmkmmk..",
        "..kmmmmmk..",
        "...kmmmk...",
        "..kkkmkkk..",
        ".kmmmmmmmk.",
        "kmkmmmmmmmkk",
        "km.kmmmmmk.km",
        "kk.kmmmmmk..km",
        "...kmmmmmk...km"[:14],
        "...kmmmmmk....k",
        "...kmmmmmk....m"[:15],
        "...kmmkmmk....m",
        "...kmmkmmk....m",
        "..kmmk.kmmk...m",
        "..kmmk.kmmk...m",
        "..kmmk.kmmk...m",
        ".kmmmk.kmmmk..m",
        ".kkkkk.kkkkk..m"], 10, 3)
for y in range(8, 24):
    c[y][8] = "k" if c[y][8] == "." else c[y][8]
put(c, ["kmk"], 9, 8)
put(c, ["kkkkkkkkkkkkkkkkkk", "kttttttttttttttttk", "ktuttttttttttuttk"[:17] + "k", "kttttkkkkkkkttttk"[:17] + "k",
        "ktttkyyyyyykttttk"[:17] + "k", "kttttkkkkkkkttttk"[:17] + "k", "kttttttttttttttttk", "kkkkkkkkkkkkkkkkkk"], 6, 24)
put(c, ["kkkkkkkkkkkkkkkkkkkkkk", "kuuuuuuuuuuuuuuuuuuuuk", "kkkkkkkkkkkkkkkkkkkkkk"], 4, 32)
SPRITES["wonder:Colossus"] = fin(c)

# The Grand Exchange: gilded dome on a drum, colonnaded trading hall, broad steps
c = cv(36, 35)
put(c, ["..k..", ".kyk.", "..k.."], 15, 0)
put(c, ["......kkkkk......",
        "....kkyyyyykk....",
        "...kyyyyyyyyyk...",
        "..kyyyyyyyyyyyk..",
        ".kyyyyyyyyyyyyyk.",
        "kkkkkkkkkkkkkkkkk"], 9, 3)
box(c, 10, 9, 15, 5, "w")
for o in (12, 16, 20):
    put(c, ["kkk", "kyk", "kkk"], o, 10)
for i in range(4):
    for x in range(17 - 5 * i - 4, 18 + 5 * i + 4):
        if 0 <= x < 36:
            c[13 + i][x] = "k" if x in (17 - 5 * i - 4, 17 + 5 * i + 4) or i == 3 else "t"
hline(c, 1, 34, 17, "y")
hline(c, 1, 34, 18, "k")
box(c, 2, 19, 32, 11, "d")
for x0 in range(3, 33, 4):
    put(c, ["kkk"] + ["sws"] * 9 + ["kkk"], x0, 19)
put(c, ["kkkkkk", "kyyyyk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk"], 15, 23)
put(c, ["kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk", "kttttttttttttttttttttttttttttttttttk", "kuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuk", "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk"], 0, 30)
SPRITES["wonder:The Grand Exchange"] = fin(c)

# The Exalted Archbasilica (key: The Eternal Sepulchre): twin spired bell towers, nave gable, rose window, great door
c = cv(36, 35)
for x0 in (1, 25):
    put(c, ["....k.....", "...kkk....", "....k.....", "....k.....", "...krk....", "...krk....", "..krrrk...", "..krrrk...", ".krrrrrk..", "krrrrrrrk.", "kkkkkkkkk."], x0, 0)
    box(c, x0, 11, 9, 23, "t")
    put(c, ["kkkkk", "kdyyk"[:4] + "k", "kyyyk", "kkkkk"], x0 + 2, 13)
    put(c, WINT, x0 + 3, 19)
    put(c, SLIT, x0 + 4, 26)
put(c, CROSS, 16, 1)
gable(c, 17, 5, 8)
box(c, 10, 13, 15, 21, "w")
put(c, ["..kkkkk..",
        ".kcayack.",
        "kaykkkyak",
        "kcykyykck",
        "kaykkkyak",
        ".kcayack.",
        "..kkkkk.."], 13, 14)
put(c, ["...kkk...", "..kdddk..", ".kdddddk.", ".kdddddk.", ".kdddddk.", ".kdddddk.", ".kdddydk."[:9], ".kdddddk.", ".kdddddk.", ".kdddddk."], 13, 24)
SPRITES["wonder:The Eternal Sepulchre"] = fin(c)

# High Chancery: clock tower with gilt face and spire, long chancery wings, many lit windows
c = cv(36, 35)
put(c, ["..y..", "..k..", ".krk.", ".krk.", "krrrk", "krrrk"], 15, 0)
put(c, ["kkkkkkkkk"], 13, 6)
box(c, 13, 7, 9, 27, "t")
put(c, ["..kkkkk..", ".kyyyyyk.", "kyyykyyyk", "kyyykkkyk", "kyyyyyyyk", ".kyyyyyk.", "..kkkkk.."], 13, 8)
put(c, WINT, 16, 17)
put(c, ["kkkkk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk"], 15, 26)
for x0, x1 in ((0, 13), (22, 36)):
    w = x1 - x0
    put(c, ["k" * w, "k" + "r" * (w - 2) + "k", "k" + "r" * (w - 2) + "k", "k" * w], x0, 14)
    box(c, x0, 18, w, 16, "w")
    for o in range(2, w - 3, 4):
        put(c, WIN, x0 + o, 20)
        put(c, WIN, x0 + o, 25)
    hline(c, x0 + 1, x1 - 2, 29, "b")
    for x in (x0 + 2, x1 - 3):
        put(c, ["k", "u", "u"], x, 11)
SPRITES["wonder:High Chancery"] = fin(c)


# ================================================================ BATCH 11: skylines + infrastructure (x1.5)
def sky(w, h):
    """Canvas for a free-size skyline / infrastructure piece: w wide, h total rows incl. ground."""
    return cv(w, h - 1)


def cypress(c, x, y, h):
    """Tall narrow seasonal tree, 3 wide, top at y, trunk 2 rows."""
    put(c, [".l."], x, y)
    for j in range(1, h - 2):
        put(c, ["lll"], x, y + j)
    put(c, [".b.", ".b."], x, y + h - 2)


# Hamlet core: thatched longhouse on a knoll, cypress, haystack
c = sky(39, 34)
cypress(c, 0, 3, 30)
put(c, [".s", "s.", "kk", "kb"], 18, 0)
gable(c, 18, 4, 12, "b")
for i in range(3, 12, 2):
    for x in range(18 - i + 1, 18 + i):
        if (x + i) % 4 == 0:
            c[4 + i][x] = "y"
box(c, 9, 16, 19, 10, "w")
for o in (11, 23):
    put(c, WIN, o, 17)
put(c, ["kkk", "kdk", "kdk", "kdk", "kdk", "kdk"], 16, 20)
put(c, ["....kk....", "...kyyk...", "..kyyyyk..", ".kyyyyyyk.", ".kyyyyyyk.", "kyyyyyyyyk", "kyyyyyyyyk", "kyyyyyyyyk", "kyyyyyyyyk", "kyyyyyyyyk", "kyyyyyyyyk", "kkkkkkkkkk"], 29, 15)
for y in range(26, 33):
    for x in range(3, 39):
        if c[y][x] == ".":
            inset = (32 - y) * 0
            c[y][x] = "l"
for y in range(26, 33):
    c[y][3] = "k" if y == 26 else c[y][3]
put(c, [".b.", ".b."], 1, 31)
SPRITES["sky:core:Hamlet"] = fin(c)

c = sky(15, 28)
cypress(c, 6, 0, 22)
fence(c, 0, 14, 22)
c[22][7] = "l"
for y in range(23, 27):
    c[y][7] = "b"
SPRITES["sky:fill:Hamlet"] = fin(c)

# Village core: church with a tall tower between two cottages
c = sky(39, 40)
put(c, ["kk", "kk"], 18, 0)
box(c, 17, 2, 4, 2, "t")
box(c, 16, 4, 6, 14, "t")
put(c, ["kkkk", "kyyk", "kyyk", "kkkk"], 17, 7)
put(c, SLIT, 18, 13)
gable(c, 19, 17, 9)
box(c, 11, 26, 17, 13, "t")
for o in (13, 23):
    put(c, WINT, o, 28)
put(c, ["kkkk", "kddk", "kddk", "kddk", "kddk", "kddk"], 17, 33)
for x0, half in ((0, 5), (28, 5)):
    gable(c, x0 + half, 19, half)
    box(c, x0, 25, 2 * half + 1, 14, "w")
    put(c, WIN, x0 + 2, 27)
    put(c, ["kkk", "kdk", "kdk", "kdk", "kdk", "kdk"], x0 + 5, 33)
SPRITES["sky:core:Village"] = fin(c)

c = sky(15, 28)
gable(c, 7, 0, 7)
box(c, 1, 7, 13, 20, "w")
put(c, WIN, 3, 10)
put(c, WIN, 9, 10)
put(c, WIN, 3, 16)
put(c, ["kkk", "kdk", "kdk", "kdk", "kdk", "kdk"], 7, 21)
SPRITES["sky:fill:Village"] = fin(c)

# Town core: crenellated stone hall between gabled houses
c = sky(36, 30)
put(c, ["k.k.k.k.k.k.k.k.k", "kkkkkkkkkkkkkkkkk"], 9, 0)
box(c, 9, 2, 17, 27, "t")
for o in (11, 21):
    put(c, WINT, o, 7)
    put(c, WINT, o, 15)
put(c, ["kkkkk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk"], 15, 21)
for x0 in (0, 26):
    gable(c, x0 + 4, 7, 4)
    box(c, x0, 12, 9, 17, "w")
    put(c, WIN, x0 + 3, 14)
    put(c, ["kkk", "kdk", "kdk", "kdk", "kdk"], x0 + 3, 24)
SPRITES["sky:core:Town"] = fin(c)

c = sky(15, 21)
gable(c, 7, 0, 6)
box(c, 1, 6, 13, 14, "w")
put(c, WIN, 3, 8)
put(c, WIN, 9, 8)
put(c, ["kkk", "kdk", "kdk", "kdk", "kdk"], 6, 15)
SPRITES["sky:fill:Town"] = fin(c)

# City core: tall red-roofed hall between twin crenellated towers
c = sky(45, 39)
for x0 in (3, 34):
    put(c, ["k.k.k.k.", "kkkkkkkk"], x0, 0)
    box(c, x0, 2, 8, 36, "t")
    for y0 in (6, 15, 24):
        put(c, SLIT, x0 + 3, y0)
gable(c, 22, 1, 10)
put(c, ["kk"], 22, 0)
box(c, 11, 11, 23, 27, "t")
hline(c, 11, 33, 12, "k")
for o in (14, 28):
    put(c, WINT, o, 15)
    put(c, WINT, o, 24)
put(c, ["kkkkkk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk"], 20, 29)
put(c, ["kkkk", "kyyk", "kkkk"], 21, 15)
SPRITES["sky:core:City"] = fin(c)

c = sky(12, 26)
put(c, ["....kk....", "...krrk...", "..krrrrk.."], 1, 0)
box(c, 1, 3, 10, 22, "w")
for y0 in (5, 12):
    put(c, WIN, 4, y0)
put(c, ["kkk", "kdk", "kdk", "kdk", "kdk"], 4, 19)
SPRITES["sky:fill:City"] = fin(c)

# Metropolis core: spired central tower with gilt finial, domed side halls, bastion
c = sky(51, 46)
put(c, ["ky", "kk", "kk", "kk", "kk"], 24, 0)
gable2(c, 24, 4, 5)
put(c, ["kkkkkkkkkkkkkk"], 18, 10)
box(c, 19, 11, 12, 34, "t")
for y0 in (14, 22):
    put(c, ["kkk", "kyk", "kyk", "kkk"], 21, y0)
    put(c, ["kkk", "kyk", "kyk", "kkk"], 26, y0)
put(c, ["kkkkkk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk"], 22, 37)
for x0 in (4, 36):
    put(c, ["...kkk...", "..kyyyk..", ".kyyyyyk.", "kyyyyyyyk", "kkkkkkkkk"], x0, 15)
    box(c, x0, 20, 9, 25, "w")
    for y0 in (22, 30):
        put(c, WIN, x0 + 3, y0)
    put(c, ["kkk", "kdk", "kdk", "kdk", "kdk"], x0 + 3, 40)
box(c, 0, 30, 5, 15, "t")
put(c, ["k.k.k"], 0, 29)
box(c, 45, 27, 6, 18, "t")
put(c, ["k.k.kk"], 45, 26)
SPRITES["sky:core:Metropolis"] = fin(c)

c = sky(12, 30)
put(c, ["......k.....", "......k.....", ".....kkk....", "....krrk....", "...krrrrk..."], 0, 0)
box(c, 2, 5, 9, 24, "w")
for y0 in (8, 16):
    put(c, WIN, 4, y0)
put(c, ["kkk", "kdk", "kdk", "kdk", "kdk"], 4, 23)
SPRITES["sky:fill:Metropolis"] = fin(c)


# ---------------------------------------------------------------- infrastructure pieces
c = sky(18, 25)
put(c, ["kk", "ky"], 8, 0)
gable2(c, 8, 1, 7)
put(c, ["kkkk", "kyyk", "kkkk"], 7, 4)
box(c, 1, 9, 16, 15, "w")
hline(c, 2, 15, 13, "b")
for o in (2, 13):
    put(c, WIN, o, 10)
put(c, ["kkkk", "kddk", "kddk", "kddk", "kddk", "kddk"], 7, 18)
SPRITES["inf:Town Hall"] = fin(c)

c = sky(18, 46)
put(c, CROSS, 7, 0)
put(c, ["kk", "kk", "kk", "kk", "kk"], 8, 4)
put(c, ["kttk", "kttk", "kttk", "kkkk"], 7, 9)
put(c, ["kk", "kk"], 8, 13)
put(c, ["kttk", "kttk", "kttk", "kkkk"], 7, 15)
gable2(c, 8, 18, 4)
box(c, 3, 23, 12, 22, "t")
put(c, ["kkkk", "kyyk", "kyyk", "kyyk", "kkkk"], 7, 26)
for x0 in (1, 15):
    box(c, x0, 31, 2, 14, "t")
put(c, ["kkkk", "kddk", "kddk", "kddk", "kddk", "kddk", "kddk"], 7, 38)
SPRITES["inf:Cathedral"] = fin(c)

c = sky(18, 27)
put(c, ["..y..", ".yyy.", "..y..", "..k..", ".kkk."], 6, 0)
gable2(c, 8, 4, 7)
box(c, 1, 12, 16, 14, "t")
for o in (4, 12):
    put(c, WINT, o, 14)
put(c, ["kkkk", "kddk", "kddk", "kddk", "kddk", "kddk"], 7, 20)
SPRITES["inf:Chapel"] = fin(c)

c = sky(21, 28)
put(c, ["kk", "yy", "kk"], 10, 0)
gable(c, 10, 2, 9)
put(c, ["kkk", "kyk", "kkk"], 9, 6)
hline(c, 0, 20, 11, "k")
box(c, 1, 12, 19, 7, "w")
for x in range(2, 19, 3):
    vline(c, x, 13, 17, "k")
hline(c, 0, 20, 18, "k")
box(c, 1, 19, 19, 8, "w")
for o in (3, 15):
    put(c, WIN, o, 20)
put(c, ["kkkk", "kyyk", "kddk", "kddk", "kddk", "kddk"], 8, 21)
SPRITES["inf:Magistrate's Hall"] = fin(c)

c = sky(18, 25)
put(c, ["..kkkkk..", ".keeeeek.", "keeeeeeek", "kkkkkkkkk"], 4, 0)
box(c, 4, 4, 9, 20, "t")
for y0 in (6, 12):
    put(c, ["kkkkk", "kyyyk", "kyyyk", "kkkkk"][:4], 6, y0)
    for x in (7, 9):
        c[y0 + 1][x] = "k"; c[y0 + 2][x] = "k"
put(c, ["kkk", "kdk", "kdk", "kdk", "kdk"], 7, 19)
SPRITES["inf:Library"] = fin(c)

c = sky(9, 37)
put(c, ["...kcc..", "...kc...", "...k....", "k.k.k.k.k"[:9]], 0, 0)
put(c, ["kkkkkkkkk"], 0, 4)
box(c, 0, 5, 9, 31, "t")
for y0 in (8, 17, 26):
    put(c, SLIT, 4, y0)
put(c, ["kkk", "kdk", "kdk"], 3, 33)
SPRITES["inf:Garrison"] = fin(c)

c = sky(15, 37)
put(c, ["......kccc", "......kcc.", "......k..."], 0, 0)
put(c, ["k.kk.kk.kk.kk.k", "kkkkkkkkkkkkkkk"], 0, 3)
box(c, 0, 5, 15, 31, "t")
put(c, ["kkkk", "kddk", "kddk", "kkkk"], 6, 8)
for o in (2, 10):
    put(c, WINT, o, 16)
put(c, SLIT, 7, 22)
put(c, ["kkkkk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk"], 5, 30)
SPRITES["inf:Keep"] = fin(c)

c = sky(6, 34)
put(c, ["kcccc", "kcccc", "kccc.", "kcc..", "kc..."], 0, 0)
for y in range(5, 33):
    c[y][0] = "k"
SPRITES["inf:Muster Field"] = fin(c)

SPRITES["inf:Wooden Walls"] = art(["k..k..", "kb.kb.", "bbbbbb", "bbbbbb", "kkkkkk", "bbbbbb", "bkbbkb", "bbbbbb", "bbbbbb", "kkkkkk", "bbbbbb"], 6, 12)
SPRITES["inf:Stone Walls"] = art(["kk..kk", "kk..kk", "kkkkkk", "tttttt", "tutttt", "kkkkkk", "tttutt", "tttttt", "kkkkkk", "tuttt t".replace(" ", "t")[:6], "tttttt", "tttttt"], 6, 13)
SPRITES["inf:Stone Walls:tower"] = art(["k.kk.kk.k",
                                    "kkkkkkkkk",
                                    "ktttttttk",
                                    "kttkdkttk",
                                    "kttkdkttk",
                                    "ktttttttk",
                                    "ktuttttuk",
                                    "ktttttttk",
                                    "ktttdtttk",
                                    "ktttdtttk",
                                    "ktttttttk",
                                    "kttuttttk",
                                    "ktttttttk",
                                    "ktttttutk",
                                    "ktttttttk",
                                    "kkkkkkkkk"], 9, 17)
SPRITES["inf:Hitching Post"] = art(["kkkkkkkk", "bbbbbbbb", "b..m...b", "b..m...b", "b.kmk..b", "b......b", "b......b", "b......b"], 8, 9)

# Road Wardens: wardens' lodge, two mounts at the rail
c = sky(35, 16)
gable(c, 4, 0, 4)
box(c, 0, 4, 9, 11, "w")
put(c, WIN, 3, 5)
put(c, ["kkk", "kdk", "kdk", "kdk"], 3, 11)
put(c, ["..........kk..",
        ".........kbbk.",
        "........kbbbbk",
        "........kbkbbk",
        ".......kbbk.kk",
        ".kkkkkkbbk....",
        "kbbbbbbbbk....",
        "kbbbbbbbbk....",
        "kbbcccbbbk....",
        ".kbkkkkbk.....",
        ".kb....kb.....",
        ".kb....kb.....",
        ".kk....kk....."], 10, 2)
put(c, ["..........kk..",
        ".........kuuk.",
        "........kuuuuk",
        "........kukuuk",
        ".......kuuk.kk",
        ".kkkkkkuuk....",
        "kuuuuuuuuk....",
        "kuuuuuuuuk....",
        "kuuaaauuuk....",
        ".kukkkkuk.....",
        ".ku....ku.....",
        ".ku....ku.....",
        ".kk....kk....."], 21, 2)
SPRITES["inf:Road Wardens"] = fin(c)

SPRITES["inf:Bridges"] = art(["kkkkkkkkkkkkkkkkkkkkk",
                         "ktttttttttttttttttttk",
                         "ktuttttttttttttttuttk",
                         "ktttkkkkkkkkkkkkktttk",
                         "kttk.............kttk",
                         "ktk...............ktk",
                         "kk.................kk",
                         "k...................k"], 21, 9)
SPRITES["inf:Aqueducts"] = art(["kkkkkkkkkkkk",
                           "eeeeeeeeeeee",
                           "kkkkkkkkkkkk",
                           "tttttttttttt",
                           "tuttttttuttt",
                           "tttttttt.ttt"[:0] + "ttttttttttt.",
                           "tttkkkk..ttt"[:0] + "tttt.....ttt"[:12],
                           "ttt.......tt",
                           "ttt........t",
                           "tt.........t",
                           "tt..........",
                           "tt..........",
                           "tt..........",
                           "tt..........",
                           "tt..........",
                           "tt..........",
                           "tt..........",
                           "tt..........",
                           "tt..........",
                           "tt..........",
                           "tt.........."], 12, 22)


# ================================================================ BATCH 12: map pieces, retinues, markers (24)
# 'p' = owner colour, swapped per player
SPRITES["army:Levy"] = art([
    "..............m.........",
    ".............kmk........",
    ".............kmk........",
    "......kkkk....b.........",
    ".....kbbbbk...b.........",
    "....kbbbbbbk..b.........",
    "....kkhhhhkk..b.........",
    ".....khkhkk...b.........",
    ".....khhhhk...b.........",
    "......khhk....b.........",
    "....kkppppkk..b.........",
    "...kppppppppk.b.........",
    "..kpppppppppkkh.........",
    "..khkppppppkhkb.........",
    "..khkppppppk..b.........",
    "...kkbbbbbbk..b.........",
    "....kppppppk..b.........",
    "....kpppkppk..b.........",
    "....kppk.kppk.b.........",
    "....kddk.kddk.b.........",
    "....kddk.kddk.b.........",
    "...kkddk.kddkkb.........",
    "...kkkk...kkkkk.........",
])
# Man-at-Arms: brimmed kettle helm with the face showing, mail coat, kite shield in the owner's colour with a gold pale, flanged mace (original layout)
SPRITES["army:Man-at-Arms"] = art([
    "........................",
    "......kkkkkkk...........",
    ".....kmmmmmmmk..........",
    "....kmmmmmmmmmk.........",
    "...kkkkkkkkkkkkk........",
    ".....khhhhhhhk.....kmk..",
    ".....khkhhhkhk....kmmmk.",
    ".....khhhhhhhk.....kmk..",
    "......khhhhhk......kbk..",
    "...kkkkmmmmmmmk...kbk...",
    ".kkpppkmmmmmmmmk.kbk....",
    "kpppyppkmmmmmmmkkbk.....",
    "kpppyppkmmmmmmmhhk......",
    "kppyyyykmmmmmmmkk.......",
    "kpppyppkmmmmmmmk........",
    "kpppyppkmbbbbbmk........",
    ".kppypkkmmmmmmmk........",
    "..kppk.kmmmmmmmk........",
    "...kk..kmmkkkmmk........",
    ".......kddk.kddk........",
    ".......kddk.kddk........",
    ".......kkkk.kkkk........",
])
SPRITES["army:Sergeant"] = art([
    ".................kmmk...",
    "................kmmmk...",
    ".................kmk....",
    ".....kkkkk.......kbk....",
    "....kmmmmmk.......b.....",
    "...kmmmmmmmk......b.....",
    "..kkkkkkkkkkk.....b.....",
    "....khhhhhk.......b.....",
    "....khkhkhk.......b.....",
    "....khhhhhk.......b.....",
    "...kkmmmmmkk......b.....",
    "..kmmkpppkmmk....kb.....",
    "..kmmkpppkmmkkkkkhb.....",
    "..khkkpppkk.......b.....",
    "..khk.pppk........b.....",
    "...k.kbbbbk.......b.....",
    ".....kppppk.......b.....",
    ".....kpkkpk.......b.....",
    ".....kpk.kpk......b.....",
    ".....kmk.kmk......b.....",
    ".....kdk.kdk......b.....",
    "....kkdk.kdkk....kbk....",
    "....kkkk.kkkk....kkk....",
])
# Oathsworn (key: Knight Templar): great helm, pale surcoat with the oath-sword device, lance with owner pennon
SPRITES["army:Knight Templar"] = art([
    ".................kpppk..",
    ".................kppk...",
    ".................kpk....",
    ".....kkkkkk......kb.....",
    "....kmmmmmmk......b.....",
    "....kmmmmmmk......b.....",
    "....kkkkkkkk......b.....",
    "....kmmmmmmk......b.....",
    "....kmmkmmmk......b.....",
    ".....kkkkkk.......b.....",
    "...kkssssssk......b.....",
    "..kssssmsssskkk..kb.....",
    ".ksssskmksssskhkkhb.....",
    ".kssssmmmssssk..kkb.....",
    ".ksmkssmssssk.....b.....",
    "..kmkssmsssk......b.....",
    "...k.ssmsssk......b.....",
    "....kssssssk......b.....",
    "....kmmkkmmk......b.....",
    "....kmmk.kmmk.....b.....",
    "....kmmk.kmmk.....b.....",
    "...kkddk.kddkk...kbk....",
    "...kkkk...kkkk...kkk....",
])
# bandit army: skull banner on a pole, hooded figure, studded club (original layout)
SPRITES["map:bandit_army"] = art([
    "...b....................",
    "...bkkkkkkkkk...........",
    "...bksssssssk...........",
    "...bkssdssdsk...........",
    "...bksssssssk...........",
    "...bkssdddssk...........",
    "...bkkkkkkkkk.....kk....",
    "...b....kkkkk....kbbk...",
    "...b...kdddddk...kbbk...",
    "...b..kdddddddk...kbk...",
    "...b..kddhhhddk..kbk....",
    "...b..kdhkhkhdk.kbk.....",
    "...b..kddhhhddkkbk......",
    "...bkkdddddddddhhk......",
    "..khkddddddddddkk.......",
    "...b.kddddddddk.........",
    "...b.kdddbdbddk.........",
    "...b.kddddddddk.........",
    "...b..kddddddk..........",
    "...b..kddk.kddk.........",
    "...b..kddk.kddk.........",
    "...b..kkkk.kkkk.........",
])
SPRITES["map:camp"] = art([
    ".........k..............",
    "........kbk.............",
    ".......ksbsk............",
    "......kssbssk...........",
    ".....ksssbsssk..........",
    "....kssssbssssk.........",
    "...ksssbsbsbsssk........",
    "..ksssbssdssbsssk.......",
    ".ksssbsssdddsssbsk......",
    "kssssbssdddddsssbsk.....",
    "ksssbsssdddddssssbsk..y.",
    "kssbssssdddddsssssbk.yfy",
    "kkkkkkkkkkkkkkkkkkkkkfyf",
    "..................kbkfbk",
    "..................kkkkkk",
])
SPRITES["map:Hamlet"] = art([
    "................kpppp...",
    "................kpppk...",
    "................kpp.....",
    "................k.......",
    ".......kkkkk....k.......",
    "......kbbbbbk...k.......",
    ".....kbbbbbbbk..k.......",
    "....kbbbbbbbbbk.k.......",
    "...kbbbbbbbbbbbkk.......",
    "..kkkkkkkkkkkkkkk.......",
    "...kwwwwwwkdddk.........",
    "...kwwyywwkdddk.........",
    "...kwwyywwkdddk.........",
    "...kwwwwwwkdddk.........",
    "...kkkkkkkkkkkk.........",
])
SPRITES["map:Village"] = art([
    "...............kpppp....",
    "...............kpppk....",
    "...............kpp......",
    "...............k........",
    "..............kyk.......",
    ".............krrrk......",
    "............krrrrrk.....",
    "...kkkk....krrrrrrrk....",
    "..krrrrk..krrrrrrrrrk...",
    ".krrrrrrk.kkkkkkkkkkk...",
    "krrrrrrrrk.kwwwywwwk....",
    "kkkkkkkkkk.kwwwwwwwk....",
    ".kwwykddk..kwwwdwwwk....",
    ".kwwwkddk..kwwwdwwwk....",
    ".kkkkkkkk..kkkkkkkkk....",
])
# Town: tall crenellated keep with the owner's flag and a lit window, behind a crenellated curtain wall with a gate (original layout)
SPRITES["map:Town"] = art([
    "...........kpp..........",
    "...........kpp..........",
    "...........k............",
    "...........k............",
    "........k.k.k.k.k.......",
    "........kkkkkkkkk.......",
    "........kttttttk........"[:24],
    "........ktttttttk.......",
    "........kttyyttk........"[:24],
    "........kttyytttk.......",
    "........ktttttttk.......",
    ".k.k.k.kktttttttkk.k.k.k",
    ".kkkkkkkktttttttkkkkkkkk",
    ".kttttttttttttttttttttk.",
    ".kttkttttttttttttttkttk.",
    ".kttttttttttttttttttttk.",
    ".kttttttttkddkttttttttk.",
    ".kttttttttkdddktttttttk."[:24],
    ".kttttttttkddkttttttttk.",
    ".kttttttttkddkttttttttk.",
    ".kkkkkkkkkkkkkkkkkkkkkk.",
])
# City: two flagged towers, red-roofed hall with lit windows, crenellated wall and gate (original layout)
SPRITES["map:City"] = art([
    "..kpp..............kpp..",
    "..kpp..............kpp..",
    "..k................k....",
    "..k.......kk.......k....",
    ".k.k.k...krrk.....k.k.k.",
    ".kkkkk..krrrrk....kkkkk.",
    ".ktttk.krrrrrrk...ktttk.",
    ".ktktkkrrrrrrrrk..ktktk.",
    ".ktttkkkkkkkkkkkkkktttk.",
    ".ktttkttyyttyyttkkktttk.",
    "kkkkkkkkkkkkkkkkkkkkkkkk",
    "kttttttttttttttttttttttk",
    "ktkttttttttttttttttttktk",
    "kttttttttttttttttttttttk",
    "ktttttttttkddkttttttttttk"[:23] + "k",
    "ktttttttttkddktttttttttk",
    "ktttttttttkddktttttttttk",
    "ktttttttttkddktttttttttk",
    "kkkkkkkkkkkkkkkkkkkkkkkk",
])
# Metropolis: gilded dome with the owner's flag between two flagged towers, palace front with lit windows, wall and gate (original layout)
SPRITES["map:Metropolis"] = art([
    "...........kk...........",
    "...........kpp..........",
    "...........kpp..........",
    "...........k............",
    "..kpp.....kyyk.....kpp..",
    "..k......kyyyyk....k....",
    "..k.....kyyyyyyk...k....",
    ".k.k.k..kyyyyyyk..k.k.k.",
    ".kkkkk..kkkkkkkk..kkkkk.",
    ".ktttk.kwwwwwwwwk.ktttk.",
    ".ktktkkwywwywwywk.ktktk.",
    ".ktttkkwywwywwywkkktttk.",
    ".ktttkkwwwwwwwwwkkktttk.",
    "kkkkkkkkkkkkkkkkkkkkkkkk",
    "kttttttttttttttttttttttk",
    "ktkttttttttttttttttttktk",
    "kttttttttttttttttttttttk",
    "ktttttttttkddktttttttttk",
    "ktttttttttkddktttttttttk",
    "ktttttttttkddktttttttttk",
    "kkkkkkkkkkkkkkkkkkkkkkkk",
])
# markers (no ground row)
SPRITES["mk:battle"] = [
    ".kk..................kk.",
    "kmsk................ksmk",
    ".kmsk..............ksmk.",
    "..kmsk............ksmk..",
    "...kmsk..........ksmk...",
    "....kmsk........ksmk....",
    ".....kmsk......ksmk.....",
    "......kmsk....ksmk......",
    ".......kmsk..ksmk.......",
    "........kmskksmk........",
    ".........kmssmk.........",
    "..........ksmk..........",
    ".........ksmmsk.........",
    "........ksmkkmsk........",
    ".......ksmk..kmsk.......",
    "...kk.ksmk....kmsk.kk...",
    "...kykkmk......kmkkyk...",
    "....kyyk........kyyk....",
    "....kkyk........kykk....",
    "...kbkkyk......kykkbk...",
    "..kbk..kk......kk..kbk..",
    ".kbk................kbk.",
    "kbk..................kbk",
    ".k....................k.",
]
SPRITES["mk:siege"] = [
    "................kkk.....",
    "...............kssk.....",
    "..............ksbsk.....",
    ".............kbbkk......",
    "............kbbk........",
    "...........kbbk.........",
    "..........kbbk..........",
    "..kkkkk..kbbk...........",
    ".kuuuuuk.kbk............",
    ".kutuuukkbk.............",
    ".kuuuuubbk..............",
    "..kkkkbbk...............",
    "....kbbyk...............",
    "...kbkkbk...............",
    "..kbk..kbk..............",
    ".kbk....kbk.............",
    "kbkkkkkkkkbk............",
    "kbbbbbbbbbbbk...........",
    "kkkkkkkkkkkkk...........",
    ".kbk....kbk.............",
    "kbkbk..kbkbk............",
    ".kbk....kbk.............",
    "........................",
    "........................",
]


# ================================================================ BATCH 13: equipment icons (18x18, no ground row; drawn on EQ_TILE)
def ic():
    return [list("." * 18) for _ in range(18)]


def icon(c):
    return ["".join(r) for r in c]


def diag(c, x, y, n, mid="m", lo="k", hi="k"):
    """Outlined 1-px diagonal stroke running down-left from (x, y), n steps."""
    for i in range(n):
        xx, yy = x - i, y + i
        if 0 <= yy < 18:
            for dx, ch in ((-1, lo), (0, mid), (1, hi)):
                if 0 <= xx + dx < 18 and (c[yy][xx + dx] == "." or dx == 0):
                    c[yy][xx + dx] = ch


def sword(c, tip_x, blade, grip, guard="m", pommel="u", hi="s", edge="m", grip_ch="b"):
    """Diagonal sword, tip at (tip_x, 0): 2-px blade with edge highlight, cross-guard, grip, pommel."""
    for i in range(blade):
        x, y = tip_x - i, i
        put(c, ["k" + hi + edge + "k"], x - 2, y) if i else put(c, ["k" + "k"], x - 1, y)
    gx, gy = tip_x - blade, blade
    for d in range(-3, 4):                      # cross-guard: perpendicular bar, 2 px thick, outlined
        for t in (0, 1):
            x, y = gx - 1 + d + t, gy + d
            if 0 <= x < 18 and 0 <= y < 18:
                c[y][x] = guard
    for d in (-4, 4):
        for t in (0, 1):
            x, y = gx - 1 + d + t, gy + d
            if 0 <= x < 18 and 0 <= y < 18 and c[y][x] == ".":
                c[y][x] = "k"
    for i in range(grip):
        x, y = gx - 2 - i, gy + 1 + i
        if 0 <= y < 18 and 0 <= x < 18:
            c[y][x] = grip_ch
            if x + 1 < 18 and c[y][x + 1] == ".":
                c[y][x + 1] = "k"
            if x - 1 >= 0 and c[y][x - 1] == ".":
                c[y][x - 1] = "k"
    x, y = gx - 2 - grip, gy + 1 + grip
    if 0 <= y < 18 and 0 <= x < 18:
        c[y][x] = pommel


def shaft(c, x, y, n, ch="b"):
    diag(c, x, y, n, ch)


def torso(fill_fn, belt="b"):
    rows = ["..................",
            "....kkkk..kkkk....",
            "..kkFFFFkkFFFFkk..",
            ".kFFFFFFFFFFFFFFk.",
            "kFFFFFFFFFFFFFFFFk",
            "kFFFFFFFFFFFFFFFFk",
            "kFFkFFFFFFFFFFkFFk",
            "kFFkFFFFFFFFFFkFFk",
            "kFFkFFFFFFFFFFkFFk",
            "kkkkFFFFFFFFFFkkkk",
            "...kFFFFFFFFFFk...",
            "...kFFFFFFFFFFk...",
            "...kBBBBBBBBBBk...",
            "...kFFFFFFFFFFk...",
            "...kFFFFFFFFFFk...",
            "...kFFFFFFFFFFk...",
            "....kkkkkkkkkk....",
            ".................."]
    out = []
    for y, r in enumerate(rows):
        out.append("".join(fill_fn(x, y) if ch == "F" else (belt if ch == "B" else ch) for x, ch in enumerate(r)))
    return out


# ---- weapons: the 12 px originals redrawn at 18 px (same composition and colours, 1-px outline)
SPRITES["eq:Farm Tools"] = [   # billhook
    "..................",
    "..................",
    ".........kkkk.....",
    "........kmmmmk....",
    ".......kmmkkkmk...",
    "......kmkk...kmk..",
    "......kmsk....k...",
    "......kmsk........",
    "......kmsk........",
    "......kmk.........",
    ".....kbk..........",
    "....kbk...........",
    "...kbk............",
    "..kbk.............",
    ".kbk..............",
    "kbk...............",
    ".k................",
    "..................",
]
SPRITES["eq:Cudgel"] = [   # knotted club
    "...........kkk....",
    "..........kbddk...",
    ".........kbddbbk..",
    "........kbdbbdbk..",
    "........kbbbbbbk..",
    "........kdbbdbbk..",
    "........kbbdbbk...",
    "........kdbbbk....",
    ".......kbkkkk.....",
    "......kbk.........",
    ".....kbk..........",
    "....kbk...........",
    "...kbk............",
    "..kbk.............",
    ".kbk..............",
    "kbk...............",
    ".k................",
    "..................",
]
SPRITES["eq:Pitchfork"] = [   # three tines
    "..................",
    "..........k.......",
    ".........ksk......",
    "........kmk...k...",
    ".......kmk...ksk..",
    "......kmk...kmk...",
    ".......kmk.kmk....",
    "........kmkmk...k.",
    ".........kmk...ksk",
    "........kbkmk.kmk.",
    ".......kbk.kmkmk..",
    "......kbk...kmk...",
    ".....kbk.....k....",
    "....kbk...........",
    "...kbk............",
    "..kbk.............",
    ".kbk..............",
    "kbk...............",
]
SPRITES["eq:Daggers"] = [   # two daggers, original layout
    "........k.........",
    ".......ksk........",
    "..k...kmk.........",
    ".ktk.kmk..........",
    "..ktkmk...........",
    "...ktk............",
    "..kbktk.........k.",
    ".kbk.ktk.......ksk",
    "ktk...k...k...kmk.",
    ".k.......ktk.kmk..",
    "..........ktkmk...",
    "...........ktk....",
    "..........kbktk...",
    ".........kbk.ktk..",
    "........ktk...k...",
    ".........k........",
    "..................",
    "..................",
]
SPRITES["eq:Short Sword"] = [   #
    "..................",
    "..............k...",
    ".............kmk..",
    "............kmsk..",
    "...........kmsk...",
    "..........kmsk....",
    ".....k...kmsk.....",
    "....ktk.kmsk......",
    ".....ktkmsk.......",
    "......ktkk........",
    ".....kbktk........",
    "....kbk.ktk.......",
    "...ktk...k........",
    "....k.............",
    "..................",
    "..................",
    "..................",
    "..................",
]
SPRITES["eq:Spears"] = [   # leaf head
    "................k.",
    "..............kksk",
    ".............ksmk.",
    "............ksmmk.",
    "...........ksmmk..",
    "...........kmmk...",
    "..........kmkk....",
    ".........kbk......",
    "........kbk.......",
    ".......kbk........",
    "......kbk.........",
    ".....kbk..........",
    "....kbk...........",
    "...kbk............",
    "..kbk.............",
    ".kbk..............",
    "kbk...............",
    ".k................",
]
SPRITES["eq:Arming Sword"] = [   #
    "................k.",
    "...............kmk",
    "..............kmsk",
    ".............kmsk.",
    "............kmsk..",
    "...........kmsk...",
    "....k.....kmsk....",
    "...kmk...kmsk.....",
    "....kmk.kmsk......",
    ".....kmkmsk.......",
    "......kmkk........",
    ".....kbkmk........",
    "....kbk.kmk.......",
    "...kbk...kmk......",
    "..kuk.....k.......",
    "...k..............",
    "..................",
    "..................",
]
SPRITES["eq:Pike"] = [   #
    "................k.",
    "...............ksk",
    "..............kmk.",
    ".............kbk..",
    "............kbk...",
    "...........kbk....",
    "..........kbk.....",
    ".........kbk......",
    "........kbk.......",
    ".......kbk........",
    "......kbk.........",
    ".....kbk..........",
    "....kbk...........",
    "...kbk............",
    "..kbk.............",
    ".kbk..............",
    "kbk...............",
    "bk................",
]
SPRITES["eq:Flail"] = [   # original style: no outline
    "..................",
    "..................",
    "..................",
    "..................",
    ".........tt.......",
    "........t..t......",
    ".......t....t.....",
    "......b......t....",
    ".....b........m...",
    "....b........mum..",
    "...b........muuum.",
    "..b.........musum.",
    ".b..........muuum.",
    "d............mum..",
    "..............m...",
    "..................",
    "..................",
    "..................",
]
SPRITES["eq:Halberd"] = [   #
    "........kmk.......",
    "........kmk.......",
    ".....k..kmkkk.....",
    "....kmk.kmkmmkk...",
    ".....kmkkummmmsk..",
    "......kmkummmmmsk.",
    ".......kmummmmmsk.",
    "........kummmmmsk.",
    "........kukmmmsk..",
    "........kbkkksk...",
    "........kbk..k....",
    "........kbk.......",
    "........kbk.......",
    "........kbk.......",
    "........kbk.......",
    "........kbk.......",
    "........kbk.......",
    "........kdk.......",
]
SPRITES["eq:Battle Axe"] = [   # double bit
    ".k.....kmk.....k..",
    "kskk...kmk...kksk.",
    "ksmmk..kuk..kmmsk.",
    "ksmmmkkkukkkmmmsk.",
    "ksmmmmmmummmmmmsk.",
    "ksmmmkkkukkkmmmsk.",
    "ksmmk..kuk..kmmsk.",
    "kskk...kbk...kksk.",
    ".k.....kbk.....k..",
    ".......kbk........",
    ".......kbk........",
    ".......kbk........",
    ".......kbk........",
    ".......kbk........",
    ".......kbk........",
    ".......kbk........",
    ".......kdk........",
    "........k.........",
]
SPRITES["eq:Cavalry Spear"] = [   # red pennon
    "......kk.......k..",
    ".....kcck.....ksk.",
    "....kcccsk...kmsk.",
    ".....kkccsk.kmmk..",
    ".......kccckbmk...",
    "........kccbkk....",
    ".........kbk......",
    "........kbk.......",
    ".......kbk........",
    "......kbk.........",
    ".....kbk..........",
    "....kbk...........",
    "...kbk............",
    "..kbk.............",
    ".kbk..............",
    "kbk...............",
    ".k................",
    "..................",
]
SPRITES["eq:Morningstar"] = [   #
    "..................",
    "...........k......",
    "..........kmk.....",
    "..........kmk.....",
    ".........kuuuk....",
    ".......kkussuukk..",
    "......kmmusuuummk.",
    ".......kkuummukk..",
    "........kbuuuk....",
    ".......kbkkmk.....",
    "......kbk.kmk.....",
    ".....kbk...k......",
    "....kbk...........",
    "...kbk............",
    "..kbk.............",
    ".kbk..............",
    "kbk...............",
    ".k................",
]
SPRITES["eq:Bastard Sword"] = [   # one profile with 2HBastard
    "................k.",
    "...............kmk",
    "..............kmsk",
    ".............kmsk.",
    "............kmsk..",
    "...........kmsk...",
    "....k.....kmsk....",
    "...kyk...kmsk.....",
    "....kyk.kmsk......",
    ".....kykmsk.......",
    "......kykk........",
    ".....kbkyk........",
    "....kbk.kyk.......",
    "...kbk...kyk......",
    "..kbk.....k.......",
    ".kyk..............",
    "..k...............",
    "..................",
]
SPRITES["eq:War Hammer"] = [   #
    ".......kmk........",
    ".......kmk........",
    ".kkkkk.kmk........",
    "ksuuuukkuk........",
    "ksuuuukkukkkk.....",
    "ksuuuuuuummmmk....",
    "ksuuuukkukkkmmk...",
    "ksuuuukkuk..kmmk..",
    ".kkkkk.kbk...kmk..",
    ".......kbk....k...",
    ".......kbk........",
    ".......kbk........",
    ".......kbk........",
    ".......kbk........",
    ".......kbk........",
    ".......kbk........",
    ".......kdk........",
    "........k.........",
]
SPRITES["eq:Lance"] = [   #
    "...............kck",
    "..............kcck",
    ".............kcsck",
    "............kccck.",
    "...........kccck..",
    "..........kcsck...",
    ".........kccck....",
    "........kccck.....",
    "...kkkkkcsck......",
    "..kmmmmmmkk.......",
    "...kmmmmk.........",
    "...kmmmmk.........",
    "..kbkkmmk.........",
    ".kbk..kk..........",
    "kbk...............",
    "bk................",
    "k.................",
    "..................",
]
SPRITES["eq:Estoc"] = [   # swept guard
    "................k.",
    "...............ksk",
    "..............kmk.",
    ".............kmk..",
    "............kmk...",
    "...........kmk....",
    ".....k....kmk.....",
    "....kyk..kmk......",
    "....kyykkmk.......",
    ".....kyymk........",
    "......kbkyk.......",
    ".....kbkkyyk......",
    "....kbk..kyk......",
    "...kak....k.......",
    "..kyk.............",
    "...k..............",
    "..................",
    "..................",
]
SPRITES["eq:Poleaxe"] = [   # original layout: gold langets, back fluke, crescent head
    "..ksk......k......",
    "..kuk.....ksk.....",
    "..kuk.....kusk....",
    "..kuk.....kudsk...",
    "..kyk.....kudsk...",
    "k.kyk.....kuddsk..",
    "ykkyk..kkkkuddsk..",
    "ykkykkkddddudddsk.",
    "uyyydddddddudddsk.",
    "ykkykkkddddudddsk.",
    "ykkyk..kkkkuddsk..",
    "k.kyk.....kuddsk..",
    "..kbk.....kudsk...",
    "..kbk.....kusk....",
    "..kyk.....ksk.....",
    "..kbk......k......",
    "..kbk.............",
    "..kdk.............",
]
SPRITES["eq:Hunting Bow"] = [   # original style: no outline
    "..................",
    "..................",
    "......bb..........",
    ".....b..b.........",
    ".....s...b........",
    ".....s....b.......",
    ".....s.....b......",
    ".....s.....b......",
    ".....s.....b......",
    ".....s.....b......",
    ".....s....b.......",
    ".....s...b........",
    ".....b..b.........",
    "......bb..........",
    "..................",
    "..................",
    "..................",
    "..................",
]
SPRITES["eq:Longbow"] = [   # original style: no outline
    ".....b............",
    ".....sb...........",
    ".....s.b..........",
    ".....s..b.........",
    ".....s...b........",
    ".....s...b........",
    ".....s...b........",
    ".....s...c........",
    ".....s...c........",
    ".....s...c........",
    ".....s...b........",
    ".....s...b........",
    ".....s...b........",
    ".....s..b.........",
    ".....s.b..........",
    ".....sb...........",
    ".....b............",
    "..................",
]
SPRITES["eq:Javelin"] = [   # reads Throwing Axe
    ".....kkkkk........",
    "....kbmmmskk......",
    "....kbmmmmmsk.....",
    "....kbmmmmmmsk....",
    "....kbmmmmmmmsk...",
    "....kbmmmmmmmsk...",
    "....kbdkmmmmmsk...",
    "....kbk.kkmmmsk...",
    "....kbk...kmsk....",
    "....kbk....ksk....",
    "....kbk.....k.....",
    "....kbk...........",
    "....kbk...........",
    "....kbk...........",
    "....kbk...........",
    "....kbk...........",
    "....kdk...........",
    ".....k............",
]
SPRITES["eq:Crossbow"] = [   #
    ".......kmk........",
    ".......kbk........",
    ".kkkkkkkbkkkkkkk..",
    "kmmmmmmmmmmmmmmmk.",
    "kmkkkkkkbkkkkkkmk.",
    ".kssssssbssssssk..",
    "..kkkkkkbkkkkkk...",
    ".......kbk........",
    ".......kbk........",
    ".......kbk........",
    ".......kbuk.......",
    ".......kbk........",
    "......kbbbk.......",
    "......kbbbk.......",
    "......kbbbk.......",
    "......kbbbk.......",
    ".......kkk........",
    "..................",
]
SPRITES["eq:Pilum"] = [   # reads Throwing Spear: two crossed
    ".kk............kk.",
    "kssk..........kssk",
    "ksmmk........kmmsk",
    ".kmmmk......kmmmk.",
    "..kmmk......kmmk..",
    "...kkdk....kdkk...",
    ".....kbk..kbk.....",
    "......kbkkbk......",
    ".......kbbk.......",
    ".......kbbk.......",
    "......kbkkbk......",
    ".....kck..kck.....",
    "....kbk....kbk....",
    "...kbk......kbk...",
    "..kbk........kbk..",
    ".kdk..........kdk.",
    "..k............k..",
    "..................",
]
SPRITES["eq:2HBastard"] = list(SPRITES["eq:Bastard Sword"])   # bastard swords: one profile

c = ic()                                   # Arquebus: barrel, smouldering match, stock
put(c, ["......f...........",
        ".....kyk..........",
        "....kkkkkkkkkkkkkk",
        "...kmmmmmmmmmmmmdk",
        "..kbuuuuuuuuuuuuuk",
        ".kbbbbbbbbbbbbbbk.",
        "kbbbbkkkbbkkkkkk..",
        "kbbbk..kyk........",
        "kbbk....k.........",
        "kbbk..............",
        "kkk..............."], 0, 4)
SPRITES["eq:Arquebus"] = icon(c)

# ---- shields
c = ic()                                   # Buckler
put(c, ["....kkkkk....",
        "..kksmmmmkk..",
        ".ksmmmmmmmmk.",
        ".kmmmkkkmmmk.",
        "kmmmkuuukmmmk",
        "kmmmkusukmmmk",
        "kmmmkuuukmmmk",
        ".kmmmkkkmmmk.",
        ".kmmmmmmmmuk.",
        "..kkmmmmukk..",
        "....kkkkk...."], 2, 3)
SPRITES["eq:Buckler Shield"] = icon(c)

c = ic()                                   # Targe: round wooden, studded, boss
put(c, [".....kkkkkk.....",
        "...kkbbbbbbkk...",
        "..kbbybbbbybbk..",
        ".kbbbbbbbbbbbbk.",
        ".kbybbbkkbbbybk.",
        "kbbbbbkmmkbbbbbk",
        "kbbbbkmssmkbbbbk",
        "kbbbbkmmmmkbbbbk",
        "kbbbbbkmmkbbbbbk",
        ".kbybbbkkbbbybk.",
        ".kbbbbbbbbbbbbk.",
        "..kbbybbbbybbk..",
        "...kkbbbbbbkk...",
        ".....kkkkkk....."], 1, 2)
SPRITES["eq:Targe Shield"] = icon(c)

c = ic()                                   # Kite
put(c, ["kkkkkkkkkkkk",
        "kaaaaayyaaaak",
        "kaaaaayyaaaak",
        "kaaaaayyaaaak",
        "kyyyyyyyyyyyk",
        "kaaaaayyaaaak",
        ".kaaaayyaaak.",
        ".kaaaayyaaak.",
        "..kaaayyaak..",
        "..kaaayyaak..",
        "...kaayyak...",
        "...kaayyak...",
        "....kayak....",
        "....kayak....",
        ".....kyk.....",
        "......k......"], 2, 1)
for y in range(1, 17):
    c[y] = c[y][:15] + c[y][15:]
SPRITES["eq:Kite Shield"] = icon(c)

c = ic()                                   # Tower (pavise): boarded, iron-banded, central ridge
put(c, ["kkkkkkkkkkkkkk",
        "kbbbbbmmbbbbbk",
        "kbcccbmmbcccbk",
        "kbcccbmmbcccbk",
        "kbcccbmmbcccbk",
        "kbcccbmmbcccbk",
        "kmmmmmssmmmmmk",
        "kbcccbmmbcccbk",
        "kbcccbmmbcccbk",
        "kbcccbmmbcccbk",
        "kbcccbmmbcccbk",
        "kmmmmmssmmmmmk",
        "kbcccbmmbcccbk",
        "kbcccbmmbcccbk",
        "kbbbbbmmbbbbbk",
        ".kkkkkkkkkkkk."], 2, 1)
SPRITES["eq:Tower Shield"] = icon(c)

c = ic()                                   # Heater: quartered
put(c, ["kkkkkkkkkkkkkk",
        "kaaaaaakyyyyyyk"[:14],
        "kaaaaaakyyyyyk",
        "kaaaaaakyyyyyk",
        "kaaaaaakyyyyyk",
        "kaaaaaakyyyyyk",
        "kkkkkkkkkkkkkk",
        "kyyyyyykaaaaak",
        "kyyyyyykaaaaak",
        ".kyyyyykaaaak.",
        ".kyyyyykaaaak.",
        "..kyyyykaaak..",
        "...kyyykaak...",
        "....kkykak....",
        "......kk......"], 2, 1)
SPRITES["eq:Heater Shield"] = icon(c)

# ---- armour (torsos)
SPRITES["eq:Cloth"] = torso(lambda x, y: "d" if y == 15 or (y == 2 and x in (5, 6, 11, 12)) else "c")
SPRITES["eq:Gambeson"] = torso(lambda x, y: "d" if x == 9 else ("s" if y % 3 == 0 else "w"))
SPRITES["eq:Leather"] = torso(lambda x, y: "d" if (x in (5, 12) and y < 9) else "b", belt="y")
SPRITES["eq:Chainmail"] = torso(lambda x, y: "m" if (x + y) % 2 else "u")
SPRITES["eq:Full Plate"] = torso(lambda x, y: "s" if x in (8, 9) else ("u" if y in (10, 13) else ("s" if x < 5 and y < 6 else "m")), belt="u")
SPRITES["eq:Gothic Plate"] = torso(lambda x, y: "y" if y in (3, 15) else ("u" if x % 3 == 0 else "d"), belt="y")


# ================================================================ BATCH 14: status icons (12x12), map terrain props (x1.5)
SPRITES["st:endurance"] = [      # lightning bolt
    "......kkkk..",
    ".....kyyyk..",
    "....kyyyk...",
    "...kyyyk....",
    "..kyyyykkkk.",
    ".kyyyyyyyyk.",
    ".kkkkyyyyk..",
    "....kyyyk...",
    "...kyyyk....",
    "..kyyk......",
    "..kyk.......",
    "..kk........"]
SPRITES["st:strained"] = [       # cracked stone, red strain line
    "c.....kuuk..",
    ".c...kuuk...",
    "..c.kuuk....",
    "...cuuk.....",
    ".kuucuuuuk..",
    "kuuuucuuuk..",
    ".kkkkuckk...",
    "....kuuc....",
    "...kuuk.c...",
    "..kuuk...c..",
    ".kuuk.....c.",
    ".kk........c"]
SPRITES["st:blocked"] = [        # no-entry ring
    "...kkkkkk...",
    "..kcccccck..",
    ".kcckkkkcck.",
    "kcck....kcck",
    "kck....kccck",
    "kck...kcckck",
    "kckckcck.kck",
    "kckccck..kck",
    "kccck...kcck",
    ".kcckkkkcck.",
    "..kcccccck..",
    "...kkkkkk..."]
SPRITES["st:fatigue"] = [        # sweat drop
    ".....kk.....",
    ".....ke.....",
    "....keek....",
    "....keek....",
    "...keeeek...",
    "..keseeeek..",
    "..kesseeek..",
    ".keeseeeeek.",
    ".keeeeeeeek.",
    "..keeeeeek..",
    "...keeeek...",
    "....kkkk...."]
SPRITES["st:routed"] = [         # white flag
    ".kkkkkkk....",
    ".kbssssskk..",
    ".kbsssssssk.",
    ".kbssssssk..",
    ".kbsssssk...",
    ".kbkkkkk....",
    ".kbk........",
    ".kbk........",
    ".kbk........",
    ".kbk........",
    "kkbkk.......",
    "kbbbk......."]
SPRITES["st:muster"] = [         # green plus
    "....kkkk....",
    "....kllk....",
    "....kllk....",
    "....kllk....",
    "kkkkkllkkkkk",
    "kllllllllllk",
    "kllllllllllk",
    "kkkkkllkkkkk",
    "....kllk....",
    "....kllk....",
    "....kllk....",
    "....kkkk...."]
SPRITES["st:sieging"] = [        # siege ladder
    ".kbk...kbk..",
    ".kbkkkkkbk..",
    ".kbbbbbbbk..",
    ".kbkkkkkbk..",
    ".kbk...kbk..",
    ".kbkkkkkbk..",
    ".kbbbbbbbk..",
    ".kbkkkkkbk..",
    ".kbk...kbk..",
    ".kbkkkkkbk..",
    ".kbbbbbbbk..",
    ".kkk...kkk.."]
SPRITES["st:besieged"] = [       # burning tower
    "k.kk.kk.k...",
    "kkkkkkkkk...",
    "kttttuttk...",
    "ktuttttk"[:0] + "kttkdkttk...",
    "kttkdkttk...",
    "ktttttftk...",
    "kttttfyfk...",
    "kttfffyfk...",
    "ktfyyfyfk...",
    "ktfyyyffk...",
    "kkfyyfkkk...",
    "..kffk......"]
SPRITES["st:battle"] = [         # crossed swords
    "km........mk",
    ".kms....smk.",
    "..kms..smk..",
    "...kmssmk...",
    "....kssk....",
    "....kssk....",
    "...kmkkmk...",
    "..kyk..kyk..",
    ".kyk....kyk.",
    "kbk......kbk",
    "kuk......kuk",
    ".k........k."]
SPRITES["st:pillage"] = [        # torch flame
    ".....f......",
    "....ff..f...",
    "...fff..ff..",
    "...ffff.ff..",
    "..ffyfffff..",
    "..fyyyfff...",
    ".ffyyyyff...",
    ".ffyyyyff...",
    "..fyyyff....",
    "...kbbk.....",
    "...kbbk.....",
    "....kk......"]
SPRITES["st:destabilize"] = [    # cracked coin
    "...kkkkkk...",
    "..kyyyyyyk..",
    ".kyykyyyyyk.",
    "kyyyykyyyyyk",
    "kyyyykkyyyyk",
    "kcccccckcccк"[:11] + "k",
    "kyyyyykkyyyk",
    "kyyyyyykyyyk",
    "kyyyyyyyyyyk",
    ".kyyyyyyyyk.",
    "..kyyyyyyk..",
    "...kkkkkk..."]
SPRITES["st:tension"] = [        # warning triangle
    ".....kk.....",
    "....kffk....",
    "....kffk....",
    "...kffffk...",
    "...kfkkfk...",
    "..kffkkffk..",
    "..kffkkffk..",
    ".kfffkkfffk.",
    ".kffffffffk.",
    "kffffkkffffk",
    "kffffffffffk",
    "kkkkkkkkkkkk"]
SPRITES["st:invasion"] = [       # red arrow
    "......kk....",
    "......kck...",
    "......kcck..",
    "kkkkkkkccck.",
    "kccccccccccк"[:11] + "k",
    "kccccccccccc"[:0] + "kcccccccccck",
    "kccccccccck.",
    "kkkkkkkccck.",
    "......kcck..",
    "......kck...",
    "......kk....",
    "............"]
SPRITES["st:unrest"] = [         # skull
    "...kkkkkk...",
    "..kssssssk..",
    ".kssssssssk.",
    "kssssssssssk",
    "ksddsssddssk"[:0] + "ksddssssddsk",
    "ksddssssddsk",
    "ksssskksssk"[:0] + "kssssddssssk",
    ".kssssssssk.",
    "..kskskssk.."[:0] + "..ksksksk...",
    "..ksksksk...",
    "...kkkkk....",
    "............"]
SPRITES["st:damaged"] = [        # cracked masonry
    "...k........",
    "tttktttutttt",
    "tutkttuttutt",
    "tttkkttttttt",
    "uttttkututtu",
    "tttutkkttttt",
    "ttttttkttutt",
    "tutttttkkttt",
    "tttuttttkutt",
    "uuuuuuuukuuu",
    "uuuuuuuuuuuu",
    "kkkkkkkkkkkk"]
SPRITES["st:intercept"] = [      # barrier with warning light
    ".....kk.....",
    "....kyyk....",
    "....kyyk....",
    "kkkkkkkkkkkk",
    "kbbcbbcbbcbk",
    "kbbcbbcbbcbk",
    "kkkkkkkkkkkk",
    ".kbk....kbk.",
    ".kbk....kbk.",
    ".kbk....kbk.",
    "kkbkk..kkbkk",
    "kbbbk..kbbbk"]


# ---------------------------------------------------------------- map terrain props (original 0.7 art; the x1.5 redraw was reverted)
_P = {}
_P["tuft_a"] = [".H.", "HSH"]
_P["tuft_b"] = ["H.H", "SHS"]
_P["tuft_c"] = ["H..H", ".HH."]
_P["wave_a"] = ["HHH..", "...HH"]
_P["wave_b"] = ["HH.", "..H"]
_P["pine"] = ["...D...", "..DHD..", ".DHHSD.", "..DHD..", ".DHHSD.", "DHHHSSD", "DDDDDDD", "...D..."]
_P["pine_s"] = ["..D..", ".DHD.", "DHHSD", ".DHD.", "DHHSD", "DDDDD", "..D.."]
_P["peak"] = [".....D......", "....DHD.....", "...DHHSD....", "...DHHSSD...", "..DHHHSDSD..",
             "..DHHHSSSD..", ".DHHHSSSDSD.", ".DHHSSSSSSD.", "DHHSSSSDSSSD", "DDDDDDDDDDDD"]
_P["peak_s"] = ["...D...", "..DHD..", ".DHHSD.", "DHHSSSD", "DDDDDDD"]
_P["hump"] = ["..DDDD..", ".DHHHSD.", "DHHHHSDD", "DDDDDDDD"]
_P["pool"] = [".DDDDDD.", "DHHHDDDD", ".DDDDDD."]
_P["pool_s"] = [".DDDD.", "DHHDDD", ".DDDD."]
_P["reeds"] = ["H..H", "H.H.", "HH.H", ".HH."]
_P["cattail"] = ["D..D", "D..D", "H.H.", "HHH."]
_P["boulder"] = [".DDDD.", "DHHSSD", "DHSSSD", ".DDDD."]     # tundra: quarry stone
_P["blocks"] = ["..DDDDD..", "..DHHSD..", "..DHSSD..", "DDDDDDDDD", "DHHSDHHSD", "DHSSDHSSD", "DDDDDDDDD"]   # tundra: stacked cut stone (quarry)
_P["blocks_b"] = ["DDDDD....", "DHHSD....", "DHSSDDDDD", "DDDDDHHSD", "....DHSSD", "....DDDDD"]                # tundra: staggered cut stone (quarry)
_P["saltpan"] = ["..DDDDD..", ".DHHHHHD.", "DHHHDHHHD", ".DDDDDDD."]   # tundra: salt crust (salt works)
_P["crack_l"] = ["D......", ".DD....", "...D.DD", "....D.."]   # tundra: frost crack (Strained)
_P["flower"] = ["y", "S"]                                       # plains: rare wildflower
for _n, _r in _P.items():
    SPRITES["prop:" + _n] = _r + ["g" * len(_r[0])]


# ================================================================ BATCH 15: heraldry (48x48 shield, 30x30 charges)
S48 = 48


def _her_shield48():
    """Heater shield mask 48x48: flat top, straight sides to row 22, curving to a point at row 45."""
    rows = []
    for y in range(S48):
        if y <= 1 or y > 45:
            rows.append("." * S48); continue
        t = max(0.0, (y - 21) / 24.75)
        hw = 20.4 * (1 - t ** 2.1) ** 0.55
        rows.append("".join("p" if abs(x + 0.5 - 24) <= hw else "." for x in range(S48)))
    m = [list(r) for r in rows]
    inside = lambda x, y: 0 <= x < S48 and 0 <= y < S48 and rows[y][x] == "p"
    for y in range(S48):
        for x in range(S48):
            if inside(x, y) and not all(inside(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                m[y][x] = "k"
    out = [r[:] for r in m]
    for y in range(S48):
        for x in range(S48):
            if m[y][x] != "p":
                continue
            if m[y][x - 1] == "k" or m[y - 1][x] == "k" or m[y][x - 2] == "k" or m[y - 2][x] == "k":
                out[y][x] = "q"                                   # lit rim: top and left, 2 px
            elif any(m[y + dy][x + dx] == "k" for dx, dy in ((1, 0), (0, 1), (2, 0), (1, 1), (0, 2), (2, 1), (3, 0))):
                out[y][x] = "P"                                   # shaded rim: right and lower curve
    return ["".join(r) for r in out]


HER_SHIELD48 = _her_shield48()
HER_AT48 = (9, 8)    # charges are 30x30


def _her48(charge):
    rows = [list(r) for r in HER_SHIELD48]
    cx, cy = HER_AT48
    ch = {}
    for y, r in enumerate(charge):
        for x, c in enumerate(r.ljust(30, ".")):
            if c != ".":
                ch[(x, y)] = c
    on = lambda x, y: (x, y) in ch and ch[(x, y)] in "#x"
    for (x, y), c in ch.items():
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if q not in ch and rows[cy + q[1]][cx + q[0]] in "pqP":
                rows[cy + q[1]][cx + q[0]] = "P"
    for (x, y), c in ch.items():
        if c == "#" and on(x, y - 1) and not on(x, y + 1):
            c = "x"
        rows[cy + y][cx + x] = {"#": "s", "x": "x", "o": "k", "y": "y", "c": "c"}[c]
    return ["".join(r) for r in rows]


HER_CHARGES30 = {
    "Pelican": [
        "..............................",
        ".............####.............",
        "............######............",
        "...........########...........",
        "..........####o#####yyyy......",
        "...........##oo####yyyyyyy....",
        "............#######yyyyyyyyyy.",
        ".............######yyyyyyyyy..",
        ".............#####..yyyyyyy...",
        ".............#####.....yyyy...",
        ".............#####.......y....",
        "............######............",
        "...........#######............",
        "..........##########..........",
        ".........#############........",
        "........####xx####xx####......",
        ".......####xx####xx#######....",
        "......####xx####xx#########...",
        "......###xx####xx###########..",
        "......###xxx###xxx###########.",
        "......####xx####xx###########.",
        ".......#####################..",
        "........###################...",
        ".........################.....",
        "...........###########........",
        ".............#y###y#..........",
        ".............yy...yy..........",
        ".............yy...yy..........",
        "............yyy..yyy..........",
        "............yy..yyy...........",
    ],
    "Lion": [
        "..............................",
        ".......#####..................",
        "......########................",
        ".....##########...............",
        "....##o##x######..............",
        "...###oo#xx######.............",
        ".#########xx######............",
        "..#######xxx######............",
        "....#####xx#######............",
        ".....###.#########............",
        "yy........#########...........",
        "yy##......##########..........",
        "..#####...###########....####.",
        "..####################..######",
        "...########.##########..##..##",
        "yy#.......#############.##....",
        "y#######..#############.##....",
        "..#######.#############.##....",
        "....###################.##....",
        "......#################.##....",
        "...........############.##....",
        "............###########.##....",
        "...........############.#.....",
        "..........#####..#######......",
        ".........#####....######......",
        "........#####......#####......",
        ".......#####.......######.....",
        "......#####........######.....",
        ".....y###..........y###y##....",
        "....yy##............y#yy#.....",
    ],
    "Fox": [
        "..............................",
        "...#.......#..................",
        "...##.....##..................",
        "...###...###..................",
        "...#########..................",
        "..##########..................",
        "..##oo###oo#..................",
        ".####o###o###.................",
        ".#############................",
        "#############.................",
        "############..................",
        "......#######.................",
        "......#######.................",
        ".....#########................",
        ".....##########...............",
        "....############..........##..",
        "....#############........####.",
        "....##############......#####.",
        "....###############....######.",
        "....################.########.",
        "....################.########.",
        "....#################.######..",
        "....##################.#####..",
        "....###################.###...",
        "....####################.##...",
        "....########################..",
        "....######..#################.",
        "....######...##############...",
        "...y#####...y#############....",
        "...yy###....yy####............",
    ],
    "Beaver": [
        "..............................",
        "..............................",
        "..............................",
        "...........########...........",
        ".........############.........",
        ".......################.......",
        ".....####################.....",
        "....#o####################....",
        "...#oo#####################...",
        "..##########################..",
        "y############################.",
        "yy###########################.",
        ".yy#########################..",
        "...#########################..",
        "...########################...",
        "....#####xx##########xx#####..",
        "....#####xx##########x##x##x#.",
        "....####....####.....##xxx#xx#",
        ".....yy.....yyy.......xx#xx#xx",
        ".............y........xxxxxxxx",
        ".......................#xx#xx.",
        "........................xx#x..",
        ".........................x#...",
        "..............................",
        "..............................",
        "..............................",
        "..............................",
        "..............................",
        "..............................",
        "..............................",
    ],
    "Tree": [
        ".........############.........",
        ".......####x######x####.......",
        "......####xx######xx####......",
        ".....##xx############xx##.....",
        "....####x############x####....",
        "...########################...",
        "..####xx#####xx####xx######...",
        ".#####x#######x#####x#######..",
        ".############################.",
        "######xx####xx#####xx#########",
        "######x#####x#######x#########",
        ".############################.",
        "..####xx#######xx#######xx##..",
        "..####x########x########x###..",
        "...########################...",
        ".....#########.###########....",
        ".......#################......",
        ".........##.#####.###.........",
        "............#####.............",
        "............#####.............",
        "............#####.............",
        "............#####.............",
        "............#####.............",
        "...........#######............",
        "...........#######............",
        "..........#########...........",
        "........############..........",
        "......######.##.######........",
        ".....######...#...######......",
        "....###..............###......",
    ],
    "Raven": [
        "..............................",
        "..................###.........",
        "................#######.......",
        "...............#########......",
        "...............###o#####yyyy..",
        "..............####oo####yyyyy.",
        "..............##########yyy...",
        ".............###########yy....",
        "............##########........",
        "...........###########........",
        ".........############.........",
        ".......##############.........",
        "......###xx#xx#xx####.........",
        ".....###xxxxxxxx#####.........",
        "....###xx#xx#xx######.........",
        "...###xx#xx#xx#######.........",
        "..###xxxxxxxx########.........",
        ".###xx#xx#xx#########.........",
        "####xx#xx###########..........",
        "####xx##x##########...........",
        "###...############............",
        "##.....##########.............",
        "#.......########..............",
        ".........##..##...............",
        ".........##..##...............",
        ".........##..##...............",
        ".......yy#..yy................",
        "......yyy.yyy.................",
        "......yy...y..................",
        "..............................",
    ],
    "Ox": [
        ".#..........................#.",
        "###........................###",
        "####......................####",
        ".###......................###.",
        ".####....................####.",
        "..#####................#####..",
        "...######............######...",
        "....######################....",
        "....######################....",
        "....######################....",
        "...y######################y...",
        "...yy####################yy...",
        ".....####################.....",
        "......##o############o##......",
        "......#oo############oo#......",
        "......##################......",
        ".......################.......",
        ".......################.......",
        ".......################.......",
        ".......################.......",
        "........##############........",
        "........##############........",
        ".........############.........",
        ".........############.........",
        ".........##oooooooo##.........",
        ".........#oooooooooo#.........",
        ".........#oo######oo#.........",
        "..........##########..........",
        "...........########...........",
        "............######............",
    ],
    "Octopus": [
        "...........########...........",
        "..........##########..........",
        ".........############.........",
        "........##############........",
        ".......################.......",
        ".......################.......",
        ".......################.......",
        ".......################.......",
        "......##################......",
        "......#oo############oo#......",
        "......#ooo##########ooo#......",
        "......##ooo########ooo##......",
        ".......################.......",
        "......##################......",
        "....######################....",
        "...###.##.##########.##.###...",
        "..###..##.##########.##..###..",
        "..##..###.###....###.###..##..",
        ".###..##..###....###..##..###.",
        ".##...##..##......##..##...##.",
        ".###..##..###....###..##..###.",
        "..##..###..##....##..###..##..",
        "..###..##..###..###..##..###..",
        "...##..##...##..##...##..##...",
        "...##..##...##..##...##..##...",
        "..###..##...##..##...##..###..",
        "..##..###...##..##...###..##..",
        ".##...##....##..##....##...##.",
        "..#...#.....#....#.....#...#..",
        "..............................",
    ],
    "Mantis": [
        "..............................",
        "..#.....#.....................",
        ".##....##.....................",
        "..###.##......................",
        "...#####......................",
        "..######......................",
        ".##ooo###.....................",
        "..#ooo###.....................",
        "...######.....................",
        "....####......................",
        "....####......................",
        "....#####.....................",
        "...##.###.....................",
        "..###..###....................",
        "..###..####...................",
        ".##.##..####..................",
        "..#.###.#####.................",
        ".....###.#####................",
        ".........######...............",
        ".........#######..............",
        "........#.#######.............",
        ".......###..##########........",
        "......###..#.#############....",
        "......##..##.###############..",
        "....##...##..##.##############",
        "...###...##..##...############",
        "...##...###..##.....########..",
        ".......##....##........####...",
        "......###....##..........#....",
        "......##.....##...............",
    ],
    "Stag": [
        ".##...##..............##...##.",
        ".##...##...#......#...##...##.",
        ".###..##..##......##..##..###.",
        "..##..##..##......##..##..##..",
        "..###.##.###......###.##.###..",
        "...##.##.##........##.##.##...",
        "...#####.##........##.#####...",
        "....#######........#######....",
        ".....######........######.....",
        ".......####........####.......",
        "........###........###........",
        ".........##........##.........",
        ".###.....############.....###.",
        "..####...############...####..",
        "...#####.############.#####...",
        "....######################....",
        "......##################......",
        ".......################.......",
        "......#oo############oo#......",
        "......##o############o##......",
        "........##############........",
        "........##############........",
        ".........############.........",
        ".........############.........",
        ".........############.........",
        "..........##########..........",
        "..........##########..........",
        "...........#oooooo#...........",
        "...........#oooooo#...........",
        "............######............",
    ],
    "Rooster": [
        ".....yy..yy...................",
        "....yyyyyyy...................",
        "....yyyyyyyy..................",
        "....#########.................",
        "....##o#######................",
        "...###oo######................",
        "yyy###########................",
        "yyyy##########................",
        "..yy##########................",
        ".....ccc######.........##.....",
        ".....cccc#####........####....",
        "......ccc######......######...",
        ".........#######....####.###..",
        ".........########..####..####.",
        "........#########.####...###..",
        "......###############....###..",
        ".....#################...##...",
        "....##################..###...",
        "...###xx#xx#xx#########.##....",
        "...##xxxxxxxx##########.#.....",
        "...#xx#xx#xx##########........",
        "....###xx#xx#########.........",
        ".....###x##x########..........",
        "......#############...........",
        "........##########............",
        "..........#######.............",
        "..........##...##.............",
        "..........##...##.............",
        ".........yyy..yyyy............",
        ".........yy..yyyyy............",
    ],
    "Wolf": [
        "...###........................",
        "...#####....#.................",
        ".....####..###................",
        "......###oo####...............",
        ".......##o######..............",
        "........#########.............",
        "........##########............",
        ".........##########...........",
        ".........###########..........",
        "..........###########.........",
        "..........############........",
        "..........#############.......",
        ".........###############......",
        ".........################.....",
        "........##################....",
        "........###################...",
        ".......#####################..",
        ".......######################.",
        ".......#########xx#xx#########",
        ".......##########x##x#########",
        ".......####################...",
        ".......#################.###..",
        ".......################..####.",
        "......#######..#######...####.",
        "......######...######...####..",
        "......#####....#####...#####..",
        ".....######...######..#####...",
        ".....#####....#####..#####....",
        "...y######..y######..###......",
        "...yy####...yy####............",
    ],
    "Spider": [
        ".##........................##.",
        "..##......................##..",
        "...##....................##...",
        "...##.....##......##.....##...",
        "...###....##......##....###...",
        "....##....##......##....##....",
        "....##...##........##...##....",
        ".....##..##..####..##..##.....",
        "......##.##.######.##.##......",
        ".......################.......",
        "...#...##o##########o##...#...",
        "...##..##oo########oo##..##...",
        ".##.######################.##.",
        "###..####################..###",
        "##.....################.....##",
        "......##################......",
        ".....####################.....",
        "....##.################.##....",
        "...##..################..##...",
        "..##...################...##..",
        ".##...##################...##.",
        ".##...##################...##.",
        ".##..#.################.#..##.",
        ".##.##..##############..##.##.",
        "..###....############....###..",
        "...##.....##########.....##...",
        "...##......########......##...",
        "....##..................##....",
        ".....#..................#.....",
        "..............................",
    ],
    "Sea Eagle": [
        "..............................",
        ".............#................",
        "............###...............",
        "...........#oo##..............",
        "..........y#o####.............",
        ".........yyy#####.............",
        ".........yy.#####.............",
        "#........y..#####............#",
        "##.........######...........##",
        "###........#######.........###",
        "####......#########.......####",
        "#####....###########.....#####",
        "######..#############...######",
        "##############################",
        "##############################",
        ".#####xx#xx#######xx#xx######.",
        "..####xx#xx#######xx#xx#####..",
        "...###xx#xx#######xx#xx####...",
        "....####..########.....###....",
        "..........########............",
        "...........#######............",
        "............#####.............",
        "...........######.............",
        "..........########............",
        ".........###.##.###...........",
        "........###..##..###..........",
        "........##...##...###.........",
        ".......yy....##....yy.........",
        "........y.....#.....y.........",
        "..............................",
    ],
    "Owl": [
        "...##....................##...",
        "...##....................##...",
        "...###..................###...",
        "...####................####...",
        "...########################...",
        "..##########################..",
        "..##########################..",
        ".#####yy##############yy#####.",
        ".###yyyyy############yyyyy###.",
        ".##yyyooyy##########yyooyyy##.",
        ".##yyooooyy########yyooooyy##.",
        ".##yoooooyy########yyoooooy##.",
        ".##yyyooyy####yy####yyooyyy##.",
        ".###yyoyyy###yyyy###yyyoyy###.",
        "..###yyyy####yyyy####yyyy###..",
        "..############..############..",
        "...########################...",
        "...########################...",
        "...###xx#xx#xx##xx#xx#xx###...",
        "...##xxxxxxxx####xxxxxxxx##...",
        "...#xx#xx#xx######xx#xx#xx#...",
        "...###xx#xx#xx##xx#xx#xx###...",
        "....##x##x##x####x##x##x##....",
        "....######################....",
        ".....####################.....",
        ".....####################.....",
        "......##################......",
        ".........yy.yy..yy.yy.........",
        "........yyy.yyyyyy.yyy........",
        ".......yyy...yyyy...yyy.......",
    ],
}
for _n, _c in HER_CHARGES30.items():
    SPRITES["her:" + _n] = _her48(_c)


# ---------------------------------------------------------------- status icon order (st:<state>)
STATUS_ICONS = ["endurance", "strained", "blocked", "fatigue", "routed", "muster", "sieging", "besieged", "battle", "pillage", "destabilize", "tension", "invasion", "unrest", "damaged", "intercept"]


# ---------------------------------------------------------------- map terrain: scattered props in the hex's own tones (prop: art is above)
MAP_TERRAIN = ("plains", "hill", "forest", "wetland", "tundra", "mountain", "water")   # hexstyle kinds + hill; "tundra" = Barrens
SCATTER = {
    "plains":   {"layers": [{"p": [["tuft_a", 2], ["tuft_b", 2], ["tuft_c", 1]], "n": [3, 5], "r": 0.72}, {"p": [["flower", 1]], "n": [0, 1], "r": 0.7}]},
    "water":    {"layers": [{"p": [["wave_a", 1], ["wave_b", 2]], "n": [1, 3], "r": 0.68}]},
    "forest":   {"layers": [{"p": [["pine", 1], ["pine_s", 2]], "n": [4, 6], "r": 0.6, "g": -3}]},
    "mountain": {"layers": [{"p": [["peak", 1]], "n": [1, 1], "r": 0.12}, {"p": [["peak_s", 1]], "n": [1, 2], "r": 0.68, "g": -4}]},
    "hill":     {"layers": [{"p": [["hump", 1]], "n": [2, 2], "r": 0.42}, {"p": [["tuft_a", 1], ["tuft_b", 1]], "n": [1, 2], "r": 0.72}]},
    "tundra":   {"tone": [0.16, 0.10, 0.42],   # muted fill tones, firm outlines: angular stone vs plains' soft tufts
                 "layers": [{"p": [["boulder", 2], ["blocks", 1], ["blocks_b", 1]], "n": [1, 2], "r": 0.6},
                            {"p": [["saltpan", 1]], "n": [0, 1], "r": 0.55},
                            {"p": [["crack_l", 1]], "n": [1, 2], "r": 0.62}]},
    "wetland":  {"layers": [{"p": [["pool", 2], ["pool_s", 2]], "n": [2, 3], "r": 0.6},
                            {"p": [["reeds", 2], ["cattail", 2]], "n": [2, 3], "r": 0.66}]},
}


# ---------------------------------------------------------------- lookup
def load_data(path):
    ns = {}
    with open(path, encoding="utf-8") as fh:
        exec(fh.read(), ns)
    return ns


def sprite_key(name, ns):
    """Sprite key for a Settlement tier, Wonder, Infrastructure, Monument or Holding name. None if unknown."""
    if name in ns.get("SETTLEMENTS", {}):
        return "sky:core:" + name if "sky:core:" + name in SPRITES else "tier:" + name
    if name in ns.get("WONDERS", {}):
        return "wonder:" + name
    if name in ns.get("INFRASTRUCTURE", {}):
        return "inf:" + name if "inf:" + name in SPRITES else None
    node = ns.get("NODES", {}).get(name)
    if node:
        if node.get("type") == "Monument" and "monument:" + name in SPRITES:
            return "monument:" + name
        if "holding:" + name in SPRITES:
            return "holding:" + name
        return "group:" + node.get("group", "")
    return None


# Where each Infrastructure goes in the scene (display only, no mechanics):
#   slot   - skyline building beside/behind the tier core (left / center / right of the core)
#   edge   - skyline piece at the left or right end of the lot
#   band   - wall tile repeated across the lot, behind the holdings ("<name>:tower" at each end if present)
#   ground - one road surface in the ground strip, running from the first settlement to the last (no sprite)
#   gap    - a single stream + bridge, in the middle gap between settlements, carrying the road
#   span   - one arcade, the farthest layer (only the sky behind it), joining the cores of the first and last
#            settlement that carries infrastructure (ends hidden behind them); with only one, it runs off the right edge
#   front  - small foreground piece at the lot's left edge
SKYLINE = {
    "Library": ("slot", "left"), "Town Hall": ("slot", "right"), "Cathedral": ("slot", "center"),
    "Muster Field": ("edge", "left"), "Garrison": ("edge", "right"),
    "Wooden Walls": ("band", ""), "Stone Walls": ("band", ""),
    "Dirt Roads": ("ground", "dirt"), "Stone Roads": ("ground", "stone"),
    "Bridges": ("gap", ""), "Aqueducts": ("span", ""), "Hitching Post": ("front", "left"),
    "Chapel": ("slot", "center"), "Magistrate's Hall": ("slot", "right"), "Keep": ("edge", "right"),
    "Road Wardens": ("front", "right"),
}
# display only: when both are built, draw the upgrade in the same spot (frees skyline room)
INFRA_SUPERSEDES = {"Stone Roads": "Dirt Roads", "Stone Walls": "Wooden Walls", "Cathedral": "Chapel",
                    "Keep": "Garrison", "Magistrate's Hall": "Town Hall"}
# display only: these tiers are drawn bare (no slot / edge / band / front pieces);
# ground, gap and link pieces are shared between settlements and still pass by them
PLATE_NO_INFRA = ["Hamlet", "Village"]

# display only: how the skyline separates from the holdings in front of it
#   fade - blend of skyline colours toward the sky (0..1)
#   sil  - flatten the skyline toward two sky-derived tones (0 = full colour, 1 = silhouette)
#   halo - 1 = dark 1px edge around each holding
SCENE_STYLE = {"fade": 0.15, "sil": 0.6, "halo": 1}


def feet_key(raw_name):
    """Terrain strip for a ward whose chain is rooted in this Raw Material. None if it has none."""
    k = "feet:" + raw_name
    return k if k in SPRITES else None


def _dims(key):
    if key.startswith(("sky:", "inf:", "feet:", "prop:")):
        return None          # free size: checked for consistency only
    if key.startswith(("monument:", "wonder:")):
        return S36, S36
    if key.startswith("eq:"):
        return S18, S18
    if key.startswith("st:"):
        return S12, S12
    if key.startswith("her:"):
        return S48, S48
    if key.startswith("mk:"):
        return S24, S24
    return S24, S24


AIRBORNE = set("sy")   # smoke, sparks, bees, stars may float


def floating(rows, small=3):
    """Pixel groups not connected (8-way) to the row above the ground line.
    Allowed to float: groups made only of AIRBORNE keys, or of <= `small` pixels (birds)."""
    h, w = len(rows), len(rows[0])
    solid = {(x, y) for y in range(h - 1) for x in range(w) if rows[y][x] not in ".g"}
    seen, out = set(), []
    stack = [(x, h - 2) for x in range(w) if (x, h - 2) in solid]
    seen.update(stack)
    while stack:
        x, y = stack.pop()
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                q = (x + dx, y + dy)
                if q in solid and q not in seen:
                    seen.add(q); stack.append(q)
    rest = solid - seen
    while rest:
        comp, st = set(), [rest.pop()]
        comp.add(st[0])
        while st:
            x, y = st.pop()
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    q = (x + dx, y + dy)
                    if q in rest:
                        rest.discard(q); comp.add(q); st.append(q)
        keys = {rows[y][x] for x, y in comp}
        if len(comp) > small and not keys <= AIRBORNE:
            top = min(y for _, y in comp)
            out.append(f"{len(comp)}px from row {top} ({''.join(sorted(keys))})")
    return out


def check(ns):
    """Shape, palette and coverage problems. Empty list = clean."""
    out = []
    for key, rows in SPRITES.items():
        w, h = _dims(key) or (len(rows[0]), len(rows))
        if len(rows) != h:
            out.append(f"{key}: {len(rows)} rows, expected {h}")
        for i, r in enumerate(rows):
            if len(r) != w:
                out.append(f"{key}: row {i} is {len(r)} wide, expected {w}")
            bad = set(r) - set(KEYS) - {"."}
            if bad:
                out.append(f"{key}: row {i} unknown keys {''.join(sorted(bad))}")
        if key.startswith(("eq:", "st:", "mk:", "her:")):
            continue                                   # icons / markers: no ground row, may float
        if any(c != "g" for c in rows[-1]):
            out.append(f"{key}: last row is not ground")
        elif all(len(r) == w for r in rows) and not key.startswith("prop:"):   # props are tiny scattered marks by design
            for f in floating(rows):
                out.append(f"{key}: floating {f}")
    for pal, cols in PALETTES.items():
        miss = set(KEYS) - set(cols)
        if miss:
            out.append(f"palette {pal}: missing {''.join(sorted(miss))}")
    for g in ns.get("HOLDING_GROUPS", {}):
        if "group:" + g not in SPRITES:
            out.append(f"no sprite for group {g}")
    for n in ns.get("SETTLEMENTS", {}):
        if "tier:" + n not in SPRITES:
            out.append(f"no sprite for settlement {n}")
        if "sky:core:" + n not in SPRITES or "sky:fill:" + n not in SPRITES:
            out.append(f"settlement {n}: needs sky:core and sky:fill")
    infra = set(ns.get("INFRASTRUCTURE", {}))
    for n in infra - set(SKYLINE) - set(ns.get("WONDERS", {})):   # Wonders (Wondrous tier) draw as wonder: sprites, not skyline slots
        out.append(f"infrastructure {n} missing from SKYLINE")
    for n, (kind, _) in SKYLINE.items():
        if n not in infra:
            out.append(f"SKYLINE entry {n} not in INFRASTRUCTURE")
        elif kind != "ground" and "inf:" + n not in SPRITES:
            out.append(f"infrastructure {n}: no inf: sprite")
    for n in PLATE_NO_INFRA:
        if n not in ns.get("SETTLEMENTS", {}):
            out.append(f"PLATE_NO_INFRA entry {n} not in SETTLEMENTS")
    for a, b in INFRA_SUPERSEDES.items():
        if a not in infra or b not in infra:
            out.append(f"INFRA_SUPERSEDES {a} -> {b}: name not in INFRASTRUCTURE")
    for n in ns.get("WONDERS", {}):
        if "wonder:" + n not in SPRITES:
            out.append(f"no sprite for wonder {n}")
    for n, v in ns.get("NODES", {}).items():
        if v.get("type") == "Monument" and "monument:" + n not in SPRITES:
            out.append(f"no sprite for monument {n} (falls back to {v.get('group')})")
    raw = [n for n, v in ns.get("NODES", {}).items() if v.get("type") == "Raw Materials"]
    for n in raw:
        if "holding:" + n not in SPRITES:
            out.append(f"raw material {n}: no holding sprite")
        if "feet:" + n not in SPRITES:
            out.append(f"raw material {n}: no feet strip")
    for n in ns.get("RETINUES", {}):
        if "army:" + n not in SPRITES:
            out.append(f"no map sprite for retinue {n}")
    for n in ns.get("SETTLEMENTS", {}):
        if "map:" + n not in SPRITES:
            out.append(f"no map sprite for settlement {n}")
    used = set()
    for n in MAP_TERRAIN:
        if n not in SCATTER:
            out.append(f"no SCATTER entry for map terrain {n}")
    for n, sc in SCATTER.items():
        if n not in MAP_TERRAIN:
            out.append(f"SCATTER {n}: not in MAP_TERRAIN")
        for L in sc.get("layers", []):
            for a, _w in L.get("p", []):
                used.add(a)
                if "prop:" + a not in SPRITES:
                    out.append(f"SCATTER {n}: no sprite prop:{a}")
    for n in STATUS_ICONS:
        if "st:" + n not in SPRITES:
            out.append(f"no status icon st:{n}")
    for key in SPRITES:
        if key.startswith("st:") and key[3:] not in STATUS_ICONS:
            out.append(f"{key}: not in STATUS_ICONS")
    for k in ("mk:battle", "mk:siege"):
        if k not in SPRITES:
            out.append(f"no map marker {k}")
    gear = set()
    for t in ("WEAPONS", "RANGED", "SHIELDS", "ARMORS"):
        gear |= {n for n in ns.get(t, {}) if n not in (None, "None", "null")}
    for n in sorted(gear):
        if "eq:" + n not in SPRITES:
            out.append(f"no equipment icon for {n}")
    for key in SPRITES:
        if key.startswith("eq:") and key[3:] not in gear:
            out.append(f"{key}: not in WEAPONS / RANGED / SHIELDS / ARMORS")
    for k in ("map:camp", "map:bandit_army"):
        if k not in SPRITES:
            out.append(f"no map sprite {k}")
    for key in SPRITES:
        kind, _, name = key.partition(":")
        if kind == "prop" and name not in used:
            out.append(f"{key}: not used by SCATTER")
        if kind == "army" and name not in ns.get("RETINUES", {}):
            out.append(f"{key}: not in RETINUES")
        if kind == "map" and name not in ns.get("SETTLEMENTS", {}) and name not in ("camp", "bandit_army"):
            out.append(f"{key}: not a settlement tier / camp / bandit_army")
    known = set(ns.get("NODES", {})) | set(ns.get("WONDERS", {})) | set(ns.get("SETTLEMENTS", {}))
    for key in SPRITES:
        kind, _, name = key.partition(":")
        if kind in ("monument", "wonder", "tier", "holding") and name not in known:
            out.append(f"{key}: name not in data")
        if kind == "feet" and name not in raw:
            out.append(f"{key}: not a Raw Material")
    return out


def sheet_html(path, ns, palette="scene", only=None):
    """Preview sheet (no dependencies): sprites in one palette, then a skyline per tier (bare, and with every
    skyline infrastructure piece), then each raw feet strip under its first builds_into holding."""
    keys = [k for k in SPRITES if not only or k.startswith(tuple(only))]
    comps = []
    for n, v in ns.get("NODES", {}).items():
        if v.get("type") == "Raw Materials" and feet_key(n):
            kids = [c for c in (v.get("builds_into") or []) if c in ns.get("NODES", {})]
            comps.append({"ft": feet_key(n), "front": sprite_key(kids[0] if kids else n, ns), "label": n + " \u2192 " + (kids[0] if kids else n)})
    data = json.dumps({"S": SPRITES, "K": keys, "P": PALETTES[palette], "C": comps, "pal": palette,
                       "T": [t for t in ns.get("SETTLEMENTS", {}) if "sky:core:" + t in SPRITES],
                       "SK": SKYLINE, "NI": PLATE_NO_INFRA, "SUP": INFRA_SUPERSEDES})
    html = """<!doctype html><meta charset="utf-8"><title>Sprite Sheet</title>
<style>body{margin:0;padding:16px;background:#14161a;color:#c8ccd2;font:12px ui-monospace,monospace}
h2{font-size:14px;margin:18px 0 8px}.g{display:flex;flex-wrap:wrap;gap:12px;align-items:flex-end}
.c{display:flex;flex-direction:column;align-items:center;gap:4px;min-width:96px;text-align:center}
canvas{image-rendering:pixelated;background:#2a2e36}</style><div id="r"></div><script>
const D=__DATA__,r=document.getElementById("r"),Z=4,SKY="#5aa2ea",GR="#7fa452";
function mix(a,b,t){const p=x=>[1,3,5].map(i=>parseInt(x.slice(i,i+2),16));const A=p(a),B=p(b);return "rgb("+A.map((v,i)=>Math.round(v+(B[i]-v)*t)).join(",")+")";}
function paint(c,rows,ox,oy,tint,skipG){rows.forEach((row,y)=>[...row].forEach((ch,x)=>{if(ch==="."||(skipG&&ch==="g"))return;
  const col=D.P[ch]||"#f0f";c.fillStyle=tint?mix(col,SKY,tint):col;c.fillRect(ox+x,oy+y,1,1)}));}
function feetOn(c,rows,ox,G){paint(c,rows,ox,G-(rows.length-1),0,true);}
function cell(g,w,h,label,fn,bg){const cv=document.createElement("canvas");cv.width=w;cv.height=h;cv.style.width=w*Z+"px";cv.style.height=h*Z+"px";
  if(bg)cv.style.background=bg;fn(cv.getContext("2d"));const d=document.createElement("div");d.className="c";d.appendChild(cv);
  const l=document.createElement("span");l.textContent=label;d.appendChild(l);g.appendChild(d);}
function sec(t){const h=document.createElement("h2");h.textContent=t;r.appendChild(h);const g=document.createElement("div");g.className="g";r.appendChild(g);return g;}
let g=sec("sprites \u00b7 "+D.pal);
D.K.forEach(k=>{const rows=D.S[k];cell(g,rows[0].length,rows.length,k,c=>paint(c,rows,0,0));});
function skyline(c,t,W,G,all){const at=(k,x)=>{const s=D.S[k];if(s)paint(c,s,x,G-(s.length-1),.2,true);},w=k=>(D.S[k]||[""])[0].length;
  const hide=new Set(Object.keys(D.SUP).map(k=>D.SUP[k]));const on=n=>all==="chapel"?n==="Chapel":all&&!hide.has(n);
  for(let x=0;x<W;x+=w("sky:fill:"+t)+1)at("sky:fill:"+t,x);
  const cw=w("sky:core:"+t),cx=Math.floor((W-cw)/2);
  if(on("Library"))at("inf:Library",Math.max(0,cx-w("inf:Library")+3));
  if(on("Town Hall"))at("inf:Town Hall",Math.min(W-w("inf:Town Hall"),cx+cw-3));
  at("sky:core:"+t,cx);
  ["Chapel","Cathedral"].filter(on).forEach(n=>at("inf:"+n,Math.floor((W-w("inf:"+n))/2)));   // centre slot in front of the core
  if(on("Muster Field"))at("inf:Muster Field",0);if(on("Garrison"))at("inf:Garrison",W-w("inf:Garrison"));
  ["Stone Walls","Wooden Walls"].filter(on).forEach(n=>{for(let x=0;x<W;x+=w("inf:"+n))at("inf:"+n,x);
    if(D.S["inf:"+n+":tower"]){at("inf:"+n+":tower",0);at("inf:"+n+":tower",W-w("inf:"+n+":tower"));}});}
if(D.T.length){g=sec("settlement skylines (faded 20% toward the sky); Town+ also shown with every skyline infrastructure piece");
 D.T.forEach(t=>{const W=72,H=40,G=H-6;[false,true,"chapel"].forEach(all=>{if(all&&D.NI.includes(t))return;
  cell(g,W,H,t+(all==="chapel"?" + Chapel":all?" + infra":""),c=>{c.fillStyle=SKY;c.fillRect(0,0,W,G+1);c.fillStyle=GR;c.fillRect(0,G+1,W,H-G-1);skyline(c,t,W,G,all);});});});}
if(D.C.length){g=sec("raw feet strip in front of its first builds_into holding");
 D.C.forEach(o=>{const ft=D.S[o.ft],fr=D.S[o.front];cell(g,24,22,o.label,c=>{c.fillStyle=SKY;c.fillRect(0,0,24,20);
  c.fillStyle=GR;c.fillRect(0,20,24,2);paint(c,fr,4,20-(fr.length-1),0,true);feetOn(c,ft,2,20);});});}
</script>"""
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(html.replace("__DATA__", data))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "renown_data_d10.py"))
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--sheet")
    ap.add_argument("--only", nargs="*", help="key prefixes for the sheet, e.g. holding: backdrop:")
    a = ap.parse_args()
    ns = load_data(a.data)
    if a.check:
        probs = check(ns)
        for p in probs:
            print("  " + p)
        hold = [n for n, v in ns.get("NODES", {}).items() if v.get("type") != "Monument"]
        own = sum(1 for n in hold if "holding:" + n in SPRITES)
        print(f"sprites {len(SPRITES)} | holdings with own sprite {own}/{len(hold)} | problems {len(probs)}")
        if probs:
            sys.exit(1)
    if a.sheet:
        sheet_html(a.sheet, ns, only=a.only)
        print("wrote", a.sheet)