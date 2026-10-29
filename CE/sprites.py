"""
sprites.py — pixel sprites for the settlement board scene (skins: farmstead, blackletter, scene).

Art only. No mechanics. Which sprite a thing gets is decided by the data file:
    Holding        -> its own sprite, else its group     (32x32, "holding:<name>" / "group:<g_key>")
    Raw Material   -> also a terrain strip at the feet    (38x5, "feet:<name>") of the ward's frontmost holding
    Monument       -> its own sprite, else its group     (48x48, "monument:<name>")
    Wonder         -> its own sprite                     (48x48, "wonder:<name>")
    Settlement     -> a skyline behind its holdings: "sky:core:<tier>" centred, "sky:fill:<tier>" tiled
                      across the lot (fallback 32x32 "tier:<tier>")
    Infrastructure -> skyline pieces "inf:<name>", placed per SKYLINE; INFRA_SUPERSEDES hides the replaced one
    Status / marks -> "st:<state>" per STATUS_ICONS (12x12), "mk:battle" / "mk:siege" (24x24): Inspect panel, Army plate, map
    Equipment      -> "eq:<item>" per WEAPONS / RANGED / SHIELDS / ARMORS (18x18, no ground row): loadout icons
    Map pieces     -> "army:<Retinue>" per RETINUES, "map:<tier>" per SETTLEMENTS, "map:camp" (+ "map:camp:2".."4" by
                      the camp's Authority) / "map:bandit_army"
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

SPRITE_VERSION = "0.9.6"

KEYS = {
    "k": "outline", "w": "plaster wall", "t": "stone", "u": "dark stone", "r": "roof",
    "d": "door / shadow", "y": "lit window / gold", "f": "fire", "s": "pale (smoke, canvas, bone)",
    "m": "metal", "b": "wood", "l": "leaf (seasonal)", "n": "evergreen needles", "c": "red cloth", "a": "royal cloth", "e": "water",
    "h": "skin", "p": "owner colour (map pieces; replaced per player)",
    "P": "owner colour shade (heraldry; derived per player)", "q": "owner colour hilite (heraldry; derived per player)",
    "x": "heraldic charge shade (darkened on pale player colours)",
    "H": "terrain hilite", "S": "terrain shade", "D": "terrain deep (map terrain; derived per hex fill)",
    "g": "ground (skipped in scene)",
    # 32px shading ramp: capital = shade of the lower-case key (light from the upper left); 'K' = hard line selout keeps
    "W": "plaster shade", "R": "roof shade", "B": "wood shade", "T": "stone shade", "Y": "lamplight shade", "M": "metal shade",
    "C": "red cloth shade", "L": "leaf shade (seasonal)", "E": "water shade", "Z": "pale shade", "A": "royal cloth shade",
    "F": "fire shade", "U": "dark stone shade", "N": "evergreen shade", "j": "skin shade", "K": "hard outline (kept by selout)",
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


SHADE = {"w": "W", "r": "R", "b": "B", "t": "T", "u": "U", "y": "Y", "m": "M", "c": "C", "l": "L", "e": "E", "s": "Z", "a": "A",
         "f": "F", "n": "N"}
SHADE_TOWARD = {"y": "c", "f": "c"}     # lights shade warm (toward red), everything else toward the skin's shadow 'd'


def _mix(a, b, t):
    A, B = (tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) for h in (a, b))
    return "#" + "".join(f"{round(u + (v - u) * t):02x}" for u, v in zip(A, B))


for _p in PALETTES.values():            # derived; a hand value written in PALETTES above wins
    for _b, _sh in SHADE.items():
        _p.setdefault(_sh, _mix(_p[_b], _p[SHADE_TOWARD.get(_b, "d")], .35 if _b in SHADE_TOWARD else .3))
    _p.setdefault("K", _p["k"])
    _p.setdefault("j", _mix(_p["h"], _p["d"], .3))


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


S12, S18, S24, S32, S36, S48 = 12, 18, 24, 32, 36, 48
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


# ---------------------------------------------------------------- kit: 32px holdings (2-tone ramp + selective outline)
# Draw with base keys and 'k' lines; shade with the helpers; fin32() turns interior outlines into the shade of the
# material around them (silhouette edge, door/shadow edges and frames round lamplight / fire stay black).
#
# Style ladder: each LINE_LABELS line (raw material -> holdings -> monument) should read as one escalation, so
# material and finish follow the holding's Standing unlock (display only, never a mechanic):
#   none     - the raw trade itself: plank, wattle, canvas, earth; small, working clutter
#   Rising   - half-timber and plaster, red tile, lit windows
#   Established - dressed stone with courses, tall windows, the domain's mark
#   Sovereign - monuments (48): the line's culmination
# Domain marks, from the pure-culture lore (worldbuilding/renown_worldlore.py CULTURES / DOMAINS):
#   Industry (Trusteki)    - chimneys and smoke, gears, metal trim; ordered, kept, built to outlast its makers
#   Prowess (Kraghs)       - crenels, announced banners (red), relief and trophies; the fortified hold
#   Piety (Lenavorites)    - spires and crosses, royal cloth and gold, records; austere orders
#   Cunning (Ithiss)       - concealment: shutters, few lights, dark stone, low doors, nothing announced
# Monuments gated by two Standings borrow the pair / triple culture's register (e.g. Piety + Industry = Madekite
# masons' cathedral work, Piety + Prowess = Belvareth gothic, Cunning + Industry = Prezish counting-house).
def cv32():
    return cv(S32, S32 - 1)


def shade_rect(c, x0, y0, x1, y1):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if c[y][x] in SHADE:
                c[y][x] = SHADE[c[y][x]]


def wall(c, x, y, w, h, fill="w"):
    """Outlined box, lit from the upper left: right 2 columns and the row under the top edge in shade."""
    box(c, x, y, w, h, fill)
    shade_rect(c, x + w - 3, y + 1, x + w - 2, y + h - 2)
    shade_rect(c, x + 1, y + 1, x + w - 2, y + 1)


def roof(c, cx, y, half, fill="r"):
    """Gable (draw after its wall): right slope in shade, courses every 3rd row on the lit slope, hard eave."""
    gable(c, cx, y, half, fill)
    for i in range(1, half):
        for x in range(cx + 1, cx + i):
            c[y + i][x] = SHADE[fill]
        if i % 3 == 0:
            for x in range(cx - i + 1, cx + 1, 2):
                c[y + i][x] = SHADE[fill]
    hline(c, cx - half, cx + half, y + half, "K")


def courses(c, x0, y0, x1, y1):
    """Mortar marks on a stone face (offset bond)."""
    for y in range(y0, y1 + 1, 3):
        for x in range(x0 + (y // 3) % 2 * 2, x1 + 1, 4):
            if c[y][x] == "t":
                c[y][x] = "T"


def win4(c, x, y):
    put(c, ["kkkk", "kyyk", "kyYk", "kkkk"], x, y)


def door4(c, x, y, h=7):
    put(c, [".kk.", "kddk"] + ["kddk"] * (h - 2), x, y)


def selout(c):
    """Interior 'k' -> shade of the material it sits in (8-neighbour vote). Kept black: silhouette edge, next to
    door/shadow 'd', round lamplight / fire. 'K' is never touched."""
    H, W_ = len(c), len(c[0])
    base = {v: k for k, v in SHADE.items()}
    out = [r[:] for r in c]
    for y in range(H):
        for x in range(W_):
            if c[y][x] != "k":
                continue
            n4 = [c[y + dy][x + dx] if 0 <= y + dy < H and 0 <= x + dx < W_ else "." for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
            if any(ch in ".dyYfF" for ch in n4):
                continue
            votes = {}
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if 0 <= y + dy < H and 0 <= x + dx < W_:
                        b = base.get(c[y + dy][x + dx], c[y + dy][x + dx])
                        if b in SHADE:
                            votes[b] = votes.get(b, 0) + 1
            if votes:
                out[y][x] = SHADE[max(votes, key=votes.get)]
    c[:] = out


def shade_rim(rows, ground=True):
    """2-tone pass for small finished art (icons, map pieces, figures): lit from the upper left, a material pixel
    whose right or lower neighbour is outline / empty, and whose left or upper neighbour is the same material, takes
    the material's shade. Outlines stay black — at 12-24 px they carry the read. Lamplight and fire are left alone."""
    body = [list(r) for r in (rows[:-1] if ground else rows)]
    H, W_ = len(body), len(body[0])
    at = lambda x, y: body[y][x] if 0 <= x < W_ and 0 <= y < H else "."
    out = [r[:] for r in body]
    for y in range(H):
        for x in range(W_):
            ch = body[y][x]
            if ch in SHADE and ch not in "yf" and (
                    at(x + 1, y) in "k." and at(x - 1, y) == ch or at(x, y + 1) in "k." and at(x, y - 1) == ch):
                out[y][x] = SHADE[ch]
    return ["".join(r) for r in out] + ([rows[-1]] if ground else [])


def rank2(rows, dx, dy=1):
    """A retinue as a unit: the same figure again as a second rank, dx right and dy up, behind the first and in
    shade (owner colour -> its shade 'P', skin -> 'j'). Ground row kept."""
    body = rows[:-1]
    H, W_ = len(body), len(body[0])
    out = [list(r) for r in body]
    for y in range(H):
        for x in range(W_):
            ch = body[y][x]
            ty, tx = y - dy, x + dx
            if ch != "." and 0 <= ty < H and 0 <= tx < W_ and out[ty][tx] == ".":
                out[ty][tx] = "P" if ch == "p" else ("j" if ch == "h" else SHADE.get(ch, ch))
    return ["".join(r) for r in out] + [rows[-1]]


def fin32(c):
    selout(c)
    return fin(c)


def disc(c, cx, cy, rings, edge="k"):
    """Filled circle centred on (cx, cy) (half-pixel centres allowed): rings = [(radius, key), ...] innermost first,
    outlined at the outer radius; the lower-right half of each ring is in shade."""
    R = rings[-1][0]
    for y in range(int(cy - R - 1), int(cy + R + 2)):
        for x in range(int(cx - R - 1), int(cx + R + 2)):
            if not (0 <= y < len(c) and 0 <= x < len(c[0])):
                continue
            d = ((x - cx) ** 2 + (y - cy) ** 2) ** .5
            if d > R + .5:
                continue
            if d > R - .5:
                c[y][x] = edge
                continue
            ch = next(k for r, k in rings if d <= r)
            c[y][x] = SHADE[ch] if ch in SHADE and (x - cx) + (y - cy) > R * .6 else ch


def cren(c, x, y, w):
    """Crenellated parapet w wide: merlons on row y, solid line on row y+1."""
    for i in range(w):
        if i % 3 != 2:
            c[y][x + i] = "k"
        c[y + 1][x + i] = "k"


def spire(c, cx, y, h, fill="r"):
    """Steep pointed roof, apex at (cx, y), widening one px every 2 rows; right half in shade, hard bottom line."""
    for i in range(h):
        hw = i // 2
        for x in range(cx - hw, cx + hw + 1):
            c[y + i][x] = "k" if x in (cx - hw, cx + hw) or i == h - 1 else (SHADE[fill] if x > cx else fill)
    hline(c, cx - (h - 1) // 2, cx + (h - 1) // 2, y + h - 1, "K")


def line(c, x0, y0, x1, y1, ch, w=1):
    """Straight line (w px thick, thickening to the right) from (x0, y0) to (x1, y1)."""
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(n + 1):
        x, y = round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n)
        for k in range(w):
            if 0 <= y < len(c) and 0 <= x + k < len(c[0]):
                c[y][x + k] = ch


WHEEL9 = ["..kkkkk..",
          ".kbbbbbk.",
          "kbkbkbkbk",
          "kbbkbkbBk",
          "kbkkmkkBk",
          "kbbkbkbBk",
          "kbkbkbkBk",
          ".kBBBBBk.",
          "..kkkkk.."]


def flag(c, x, y, col, h=7):
    """Pole from (x, y) down h rows, 3x2 flag to its right."""
    vline(c, x, y, y + h - 1, "k")
    put(c, [col * 3, col + SHADE.get(col, col) * 2], x + 1, y)


ANVIL8 = [".kkkkkkk", "kmmmmmMk", ".kkmMkk.", "..kmMk..", ".kkkkkk.", ".kbbbBk.", ".kbbbBk.", ".kkkkkk."]   # anvil on a stump
BARREL8 = [".kkkk.", "kbbbBk", "kmmmMk", "kbbbBk", "kbbbBk", "kmmmMk", "kbbbBk", ".kkkk."]
SKEP8 = ["..kk..", ".kyyk.", "kyyyYk", "kkkkkk", "kyyyYk", "kkkkkk", "kydyYk", "kkkkkk"]


def tree32(c, x, y, fruit=None):
    """Round deciduous tree 13 wide, 18 tall, top-left (x, y), shaded lower right; fruit dots the canopy."""
    put(c, ["....kkkkk....",
            "..kklllllkk..",
            ".klllllllllk.",
            "kllllllllllLk",
            "klllllllllLLk",
            "kllllllllLLLk",
            "klllllllLLLLk",
            ".kllllLLLLLk.",
            "..kkLLLLLkk..",
            "....kkbBkk...",
            ".....kbBk....",
            ".....kbBk....",
            ".....kbBk....",
            ".....kbBk....",
            ".....kbBk....",
            ".....kbBk....",
            "....kbbBBk...",
            "....kkkkkk..."], x, y)
    if fruit:
        for dx, dy in ((3, 2), (7, 1), (9, 4), (5, 5), (2, 6), (8, 7), (10, 2)):
            c[y + dy][x + dx] = fruit


def fence32(c, x0, x1, y):
    """Wattle fence 4 tall from x0 to x1, top at y: woven rows, a post every 5 px."""
    for x in range(x0, x1 + 1):
        c[y + 1][x] = "b" if x % 2 else "B"
        c[y + 2][x] = "B" if x % 2 else "b"
    for x in range(x0, x1 + 1, 5):
        for j in range(4):
            c[y + j][x] = "k"


# ================================================================ BATCH 1: logistics
def _wagon(c, x, y, cloth="s"):
    """Covered wagon 24 wide, 19 tall, top-left at (x, y): hooped canvas, plank bed with a tongue, two 9px wheels."""
    hline(c, x + 4, x + 19, y, "k")
    for j in range(1, 9):
        hline(c, x + 2, x + 21, y + j, cloth)
        c[y + j][x + 2] = c[y + j][x + 21] = "k"
        for hx in (x + 8, x + 14):
            c[y + j][hx] = "k"
        for xx in (x + 19, x + 20):
            c[y + j][xx] = SHADE[cloth]
    c[y + 1][x + 2] = c[y + 1][x + 21] = "."
    c[y + 1][x + 3] = c[y + 1][x + 20] = "k"
    put(c, ["k" * 22, "k" + "b" * 19 + "Bk", "k" + "B" * 20 + "k", "k" * 22], x + 1, y + 9)
    put(c, ["kkkk", "kbbb"], x - 2, y + 10)
    put(c, WHEEL9, x + 2, y + 10)
    put(c, WHEEL9, x + 13, y + 10)


# group: covered wagon
c = cv32()
_wagon(c, 4, 12)
SPRITES["group:g_logistics"] = fin32(c)

# Butchery: half-timbered shop with a shutter counter, carcass rack with hanging joints, block and cleaver
c = cv32()
wall(c, 0, 17, 17, 14, "w")
for xx in (5, 11):
    vline(c, xx, 18, 29, "b")
hline(c, 1, 15, 22, "b")
roof(c, 8, 9, 8)
win4(c, 1, 18)
win4(c, 12, 18)
door4(c, 6, 24)
put(c, ["kkkkk", "kcCsk", "kkkkk", ".kbk."], 11, 24)                                    # counter with a cut
put(c, ["k" * 14, "kbbbbbbbbbbbBk", "kk.m...m...mkk", "kb.m...m...mBk",
        "kbkck.kck.kckB", "kbkcCkkcCkkcCB", "kbkcCkkcCkkcCB", "kb.kCk.kCk.kCB", "kb..s...s...sB",
        "kb..........kB", "kb..........kB", "kb..........kB", "kb..........kB", "kb..........kB",
        "kb..........kB", "kb..........kB", "kb..........kB", "kk..........kk"], 18, 13)
put(c, [".m..", "kmkk", "kbbBk", "kkkkk"], 23, 27)                                         # block and cleaver
SPRITES["holding:Butchery"] = fin32(c)

# Smokehouse: low plank hut, smoking louver on the ridge, drying rack of fish
c = cv32()
put(c, [".s.", "..s", ".s.", "s..", ".s.", "..s"], 7, 1)
put(c, ["kkkk", "kddk", "kkkk"], 7, 8)
wall(c, 0, 19, 17, 12, "b")
for xx in (4, 8, 12):
    vline(c, xx, 21, 29, "B")
roof(c, 8, 11, 8)
put(c, ["kkkkk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk"], 9, 24)
put(c, ["k" * 14, "kbbbbbbbbbbbBk", "kk.k..k..k..kk"], 18, 15)
for x0 in (19, 22, 25, 28):
    put(c, [".m.", "eeE", "eeE", "eeE", ".E.", "e.E"], x0, 18)
for y in range(18, 31):
    c[y][18] = "k"
    c[y][31] = "k"
SPRITES["holding:Smokehouse"] = fin32(c)

# Caravanery: crenellated walled court, arched gate with a wagon inside, wagon cover over the wall
c = cv32()
cren(c, 0, 12, 22)
wall(c, 0, 14, 22, 17, "w")
hline(c, 1, 19, 18, "b")
win4(c, 1, 15)
win4(c, 16, 15)
put(c, ["...kkkk...",
        "..kddddk..",
        ".kddddddk.",
        ".kdsssddk.",
        ".kdsssddk.",
        ".kdbbbddk.",
        ".kddddddk.",
        ".kddddddk.",
        ".kddddddk.",
        ".kddddddk.",
        ".kddddddk."], 6, 20)
put(c, ["..kkkkkkk.",
        ".ksssssZk.",
        "ksssssssZk",
        "ksssssssZk",
        "kkkkkkkkkk",
        "kbbbbbbbBk",
        "kkkkkkkkkk"], 22, 15)
put(c, WHEEL, 23, 22)
put(c, ["kk", "kbk", "kbk"], 30, 26)
SPRITES["holding:Caravanery"] = fin32(c)

# soldier for the Drill Yard rank: kettle helm, red tabard, spear upright at the right hand
SOLDIER = ["....m",
           "....m",
           ".kk.b",
           "kmmkb",
           "khjkb",
           "kcCkb",
           "kcCkb",
           "kccCb",
           ".k.kb",
           ".k.kB"]

# Drill Yard (was Coliseum art): keep tower with a pennant, curtain wall with an arcade, a rank of spearmen drilling
c = cv32()
flag(c, 5, 0, "c", 4)
cren(c, 0, 3, 9)
wall(c, 0, 5, 9, 26, "t")
courses(c, 1, 7, 6, 29)
put(c, SLIT, 4, 8)
put(c, SLIT, 4, 15)
door4(c, 2, 24)
cren(c, 8, 11, 24)
wall(c, 8, 13, 24, 18, "t")
for x0 in (10, 15, 20, 25):
    put(c, [".kk.", "kddk", "kddk", "kddk", "kddk", "kddk"], x0, 16)
hline(c, 9, 29, 22, "T")
for x0 in (11, 17, 23):
    put(c, SOLDIER, x0, 21)
SPRITES["holding:Drill Yard"] = fin32(c)

# Conditioning Field: beam on two posts, two bound straw pells hanging through it, stool and bucket
c = cv32()
for x0 in (4, 15):
    put(c, ["kkkkk"] + ["kyyYk", "kbbBk", "kyyYk", "kyyYk", "kyyYk", "kbbBk", "kyyYk", "kyyYk", "kyyYk", "kyyYk", "kbbBk", "kyyYk", "kkkkk"], x0, 7)
    put(c, ["kbk"] * 9 + ["kkk"], x0 + 1, 21)
put(c, ["k" * 26, "k" + "b" * 23 + "Bk", "k" * 26], 0, 11)
put(c, [".kkkk.", "kbbbBk", "kkkkkk", "kb..kb", "kb..kb", "kk..kk"], 25, 25)               # stool
put(c, ["kkkk", "keEk", "kttk", "kTTk", "kkkk"], 27, 20)                                   # bucket on the stool
SPRITES["holding:Conditioning Field"] = fin32(c)


# Grand Tournament: two striped pavilions with pennants
def _pav(c, x, y, a, b):
    """Striped pavilion 15 wide, 27 tall, top-left (x, y): pennant, cone roof, scalloped valance, open door."""
    cx = x + 7
    vline(c, cx, y, y + 4, "k")
    put(c, [a * 3, a + SHADE[a] * 2], cx + 1, y)
    for i in range(8):
        for xx in range(cx - i, cx + i + 1):
            col = a if ((xx - cx) // 2) % 2 == 0 else b
            c[y + 5 + i][xx] = "k" if xx in (cx - i, cx + i) else (SHADE[col] if xx > cx + 1 else col)
    hline(c, x, x + 14, y + 13, "K")
    for xx in range(x + 1, x + 14):
        for j in range(y + 14, y + 27):
            col = a if ((xx - cx) // 2) % 2 == 0 else b
            c[j][xx] = SHADE[col] if xx >= x + 12 else col
        c[y + 14][xx] = (a if xx % 2 else b) if (xx - x) % 2 else "K"
    vline(c, x + 1, y + 14, y + 26, "k")
    vline(c, x + 13, y + 14, y + 26, "k")
    for j in range(8):
        for xx in range(cx - j // 3, cx + j // 3 + 1):
            c[y + 19 + j][xx] = "d"


c = cv32()
_pav(c, 0, 4, "c", "s")
_pav(c, 16, 4, "a", "s")
SPRITES["holding:Grand Tournament"] = fin32(c)

# Charcoal Burner: smoking turf clamp with glowing vents, stack of logs with an axe leaning on it
c = cv32()
put(c, ["..s....", "...s...", "..s..s.", ".s...s.", "..s.s..", "...s..."], 8, 4)
disc(c, 11, 30, [(11, "u")])
for x, y in ((6, 22), (14, 21), (10, 25), (17, 25), (4, 27)):
    c[y][x] = "d"
put(c, ["kfk", "kyk"], 2, 28)
put(c, ["kfk", "kyk"], 18, 28)
put(c, [".kk.kk.kk",
        "kbYkbYkbYk",
        "kbbkbbkbbk",
        ".kk.kk.kk.",
        "kbYkbYkbYk",
        "kbbkbbkbbk",
        ".kk.kk.kk.",
        "kbYkbYkbYk",
        "kbbkbbkbbk",
        "kkkkkkkkkk"], 22, 21)
put(c, ["kk..", "mmk.", "kmbk", "...b"], 26, 16)
for y in range(20, 23):
    c[y][29] = "b"
SPRITES["holding:Charcoal Burner"] = fin32(c)

# Finery (was Kiln art): brick finery hearth with its stack, glowing hearth mouth, leather bellows, trip-hammer on bar iron
c = cv32()
put(c, ["..s.", "...s", "..s.", ".s.."], 7, 0)
prof = [2, 2, 2, 2, 2, 3, 3, 4, 5, 6, 7, 7, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8]
for i, hw in enumerate(prof):
    y = 4 + i
    for x in range(9 - hw, 9 + hw + 1):
        c[y][x] = "k" if x in (9 - hw, 9 + hw) or i == 0 else ("R" if x > 9 + hw - 3 else "r")
for y in (13, 19):
    hline(c, 1, 17, y, "k")
put(c, ["..kkkkk..", ".kfffffk.", "kffyyyfFk", "kfyyyyyFk", "kfyyyyyFk", "kkkkkkkkk"], 5, 25)
put(c, ["kk....", "kbk...", "kbbkkk", "kbBmmm", "kbk...", "kk...."], 0, 24)                 # bellows into the hearth
put(c, ["...........kk",
        "kkkkkkkkkkkmk",
        "kbbbbbbbbbbmk",
        "kkkkkkkkkkkmk",
        "...kbk....kmk",
        "...kbk.....k.",
        "...kbk..kkkkk",
        "...kbk..kmmMk",
        "...kbk..kmmMk",
        "..kkkkk.kkkkk",
        "..kbbBk......",
        "..kkkkk......"], 19, 19)
put(c, ["kkkkkk", "kmMkmM", "kkkkkk"], 26, 28)                                              # bar iron
SPRITES["holding:Finery"] = fin32(c)

# Levy Hall: plank muster hall, lit windows, red banner at the eave, spear rack with shields
c = cv32()
wall(c, 0, 17, 19, 14, "b")
for xx in (4, 8, 12, 15):
    vline(c, xx, 19, 29, "B")
roof(c, 9, 8, 9)
win4(c, 2, 19)
win4(c, 13, 19)
put(c, [".kkkk.", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk"], 6, 23)
put(c, ["ccC", "ccC", "ccC", "ccC", "cC.", "c.."], 18, 17)
for x in (22, 25, 28):
    put(c, ["k", "m", "M"], x, 11)
    vline(c, x, 14, 26, "b")
put(c, ["kkkkkkkkkk", "kbbbbbbbBk", "kkkkkkkkkk"], 21, 16)
put(c, ["kkkkkkkkkk", "kbbbbbbbBk", "kkkkkkkkkk"], 21, 26)
disc(c, 23.5, 22, [(1, "m"), (2.6, "c")])
disc(c, 28.5, 22, [(1, "m"), (2.6, "a")])
for y in range(19, 31):
    c[y][21] = c[y][30] = "k"
SPRITES["holding:Levy Hall"] = fin32(c)

# Siege Camp: two tents with pennants, campfire, sharpened palisade in front
c = cv32()
for x0, fl in ((1, "c"), (19, "a")):
    flag(c, x0 + 5, 2, fl, 5)
    for i in range(11):
        for xx in range(x0 + 5 - i // 2 - (i > 8), x0 + 6 + i // 2 + (i > 8)):
            c[7 + i][xx] = "s" if xx <= x0 + 5 else "Z"
        c[7 + i][x0 + 5 - i // 2 - (i > 8)] = "k"
        c[7 + i][x0 + 5 + i // 2 + (i > 8)] = "k"
    put(c, ["kd", "kdd", "kddd"], x0 + 4, 15)
put(c, ["..y..", ".fyf.", "fyyyf", "kbkbk"], 13, 15)
for x in range(32):
    if x % 3 == 1:
        c[19][x] = "k"
    for y in range(20, 31):
        c[y][x] = "k" if x % 3 == 0 else ("b" if x % 3 == 1 else "B")
    c[23][x] = c[27][x] = "k"
SPRITES["holding:Siege Camp"] = fin32(c)

# Siege Works: covered battering ram — plank-roofed shed on a wheeled bed, iron-capped log slung on chains
c = cv32()
roof(c, 20, 4, 11, "b")
for x in (9, 31):
    vline(c, x, 15, 25, "k")
    vline(c, x - 1 if x == 31 else x + 1, 16, 25, "B")
for x in (15, 25):
    vline(c, x, 16, 18, "k")
put(c, [".kkk" + "k" * 25,
        "kmmmk" + "b" * 23 + "Bk",
        "kmsmk" + "b" * 23 + "Bk",
        "kmmmk" + "B" * 24 + "k",
        ".kkk" + "k" * 25], 0, 18)
put(c, ["k" * 24, "k" + "b" * 22 + "k", "k" * 24], 8, 23)
put(c, WHEEL, 10, 24)
put(c, WHEEL, 22, 24)
SPRITES["holding:Siege Works"] = fin32(c)

# Battery Park: cocked trebuchet — A-frame, long arm down to the sling and stone, banded counterweight up
c = cv32()
line(c, 15, 12, 7, 28, "b", 2)
line(c, 15, 12, 23, 28, "b", 2)
line(c, 9, 4, 28, 24, "b", 2)
box(c, 3, 2, 8, 8, "b")
hline(c, 4, 9, 4, "m")
hline(c, 4, 9, 7, "m")
shade_rect(c, 8, 3, 9, 8)
put(c, ["kk", "k.k", ".k.k", "..kssk", "..kssZk", "...kkk"], 26, 23)
put(c, ["kkk", "kmk", "kkk"], 14, 11)
put(c, ["k" * 26, "k" + "b" * 23 + "Bk", "k" * 26], 2, 27)
for x in (4, 20):
    put(c, WHEEL5, x, 26)
SPRITES["holding:Battery Park"] = fin32(c)

# War College: stone hall with a crossed-swords crest, crenellated watchtower with a banner
c = cv32()
wall(c, 0, 17, 21, 14, "t")
roof(c, 10, 7, 10)
courses(c, 1, 19, 17, 29)
put(c, ["m......m", ".m....m.", "..m..m..", "...mm...", "..mkkm..", ".m.kck.m", "m..kCk..m"], 2, 19)
put(c, ["kkkk", ".kk."], 4, 26)
door4(c, 13, 24)
flag(c, 28, 0, "a", 5)
cren(c, 21, 4, 10)
wall(c, 21, 6, 10, 25, "t")
courses(c, 22, 8, 27, 29)
put(c, SLIT, 25, 9)
win4(c, 24, 15)
door4(c, 24, 24)
SPRITES["holding:War College"] = fin32(c)


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
# group: smithy — plaster house, chimney smoke, steel shield on the wall, glowing forge door, anvil in front
c = cv32()
put(c, [".s..", "s...", ".s..", "kkkk", "kTuk", "kTuk", "kTuk", "kTuk", "kTuk", "kTuk"], 13, 3)
wall(c, 0, 17, 21, 14, "w")
roof(c, 10, 7, 10)
put(c, ["kkkkkk", "kmmmMk", "kmuuMk", "kmmmMk", ".kmMk.", "..kk.."], 3, 20)                # shield
put(c, [".kkk.", "kfffk", "kfyFk", "kfyFk", "kfyFk", "kffFk", "kffFk", "kffFk"], 13, 23)    # forge door
put(c, ANVIL8, 23, 23)
SPRITES["group:g_arms"] = fin32(c)

# Carpentry: plank workshop, log on a sawhorse with the saw in the cut
c = cv32()
wall(c, 0, 17, 17, 14, "b")
for xx in (3, 6, 9, 12):
    vline(c, xx, 19, 29, "B")
roof(c, 8, 9, 8)
win4(c, 2, 19)
door4(c, 11, 24)
put(c, ["kbbk", "kbbk", "kkkk", "kmmM", "kmmM", ".mmM", ".mM.", "..M."], 24, 13)            # saw, handle up
put(c, [".kkkkkkkkkkkkk",
        "kybbbbbbbbbbbBk",
        "kYbbbbbbbbbbBBk",
        ".kkkkkkkkkkkkk."], 17, 21)                                                    # log, end grain to the left
for x0 in (18, 26):
    put(c, ["..k..", ".kbk.", ".kbk.", "kb.bk", "kb.bk", "k...k"], x0, 25)               # A-frame legs
SPRITES["holding:Carpentry"] = fin32(c)

# Fletchery: plank hut, lit window, archery target on a tripod with an arrow in the gold
c = cv32()
wall(c, 0, 19, 13, 12, "b")
for xx in (4, 8):
    vline(c, xx, 21, 29, "B")
roof(c, 6, 13, 6)
win4(c, 1, 21)
door4(c, 8, 24)
disc(c, 23, 11, [(1.2, "y"), (2.4, "c"), (3.6, "s"), (4.8, "c")])
put(c, ["sbbbbbbbbb"], 13, 10)                                                         # arrow
put(c, ["s", "s"], 13, 9)
for y in range(17, 31):
    c[y][23] = "b"
put(c, ["..kbk..", ".kb.bk.", ".kb.bk.", "kb...bk", "kb...bk", "kb...bk", "k.....k"], 20, 24)   # tripod
SPRITES["holding:Fletchery"] = fin32(c)

# Skirmish Field: open ground with a straw butt and target, a pell with a shield on it, arrows in the turf, bow on a rack
c = cv32()
put(c, ["..kkkkkk..", ".kyyyyyYk.", "kyycccyyYk", "kyckyykcYk", "kycyfycyYk", "kyckyykcYk", "kyycccyyYk",
        ".kyyyyyYk.", "..kkkkkk..", "..kb..bk..", ".kb....bk.", "kb......bk"], 1, 19)          # butt on trestle
put(c, ["sbbbbb"], 9, 22)
put(c, ["..k..", ".kbk.", "kcccC", "kcyCC", "kcccC", ".kCk.", "..b..", "..b..", "..b..", ".kbk."], 14, 21)
for x0 in (11, 13, 19):
    put(c, ["s", "b", "b"], x0, 28)
put(c, ["k.....k", "kb...bk", "kbkkkbk", "kb.b.bk", "kb.b.bk", "kbkkkbk", "kb...bk", "kb...bk", "kb...bk", "kb...bk", "kb...bk", "kb...bk", "kk...kk"], 22, 18)
put(c, [".k", "kb", "k.", "k.", "kb", ".k"], 24, 19)                                      # bow on the rack
SPRITES["holding:Skirmish Field"] = fin32(c)

# Tannery: half-timber workshop, hide laced on a frame, steaming vat of liquor
c = cv32()
wall(c, 0, 17, 15, 14, "w")
for xx in (5, 10):
    vline(c, xx, 18, 29, "b")
hline(c, 1, 13, 22, "b")
roof(c, 7, 10, 7)
win4(c, 1, 18)
door4(c, 6, 24)
put(c, ["bbbbbbbbb",
        "bk.k.k.kb",
        "b.sssss.b",
        "bksssssZb",
        "b.ssssZ.b",
        "bksssZZkb",
        "b..sZZ..b",
        "bk.k.k.kb",
        "bbbbbbbbb",
        "b.......b",
        "b.......b",
        "B.......B",
        "B.......B",
        "B.......B"], 15, 13)                                                         # hide on its frame
put(c, ["..s....", ".s..s..", "..s.s..", "kkkkkkk", "kdddddk", "kbbbbBk", "kkkkkkk", "kbbbbBk", "kbbbbBk", "kkkkkkk"], 25, 21)
SPRITES["holding:Tannery"] = fin32(c)

# Joinery: half-timber workshop, bench with a clamp, a finished chair
c = cv32()
wall(c, 0, 17, 15, 14, "w")
for xx in (5, 10):
    vline(c, xx, 18, 29, "b")
hline(c, 1, 13, 22, "b")
roof(c, 7, 10, 7)
win4(c, 1, 18)
door4(c, 6, 24)
put(c, ["...kmk....",
        "...kmk....",
        "kkkkkkkkkk",
        "kbbbbbbbBk",
        "kkkkkkkkkk",
        "kbk....kbk",
        "kbk....kbk",
        "kbk....kbk",
        "kkk....kkk"], 15, 22)                                                        # bench + clamp
put(c, ["k.....", "kb....", "kbk...", "kb....", "kbk...", "kbbbbk", "kkkkkk", "kb..kb", "kb..kb", "kb..kb", "kk..kk"], 26, 20)   # chair
SPRITES["holding:Joinery"] = fin32(c)

# Blacksmith: stone smithy open at the front, hood over the hearth, tongs; anvil with hammer, sparks, quench tub
c = cv32()
put(c, [".s..", "s...", ".s..", "..s.", "kkkk", "kTuk", "kTuk", "kTuk", "kTuk", "kTuk", "kTuk", "kTuk", "kTuk"], 12, 1)
wall(c, 0, 16, 19, 15, "t")
roof(c, 9, 7, 9)
courses(c, 1, 18, 16, 29)
put(c, ["kkkkkkkkkkkkkkk",
        "kdddddddddddddk",
        "kddkkkkkkkddddk",
        "kddkTTTTTkddddk",
        "kdddkTTTkddmddk",
        "kddddkTkdddmddk",
        "kddddkTkddmmmdk",
        "kddkkkkkkkddddk",
        "kddkfffyfkddddk",
        "kddkfyyyfkddddk",
        "kddkFfffFkddddk",
        "kddkkkkkkkddddk",
        "kdddddddddddddk"], 2, 18)
put(c, ["..y..", "y...f", "..f.."], 21, 16)
put(c, [".....kkk", "kkkkkkmk", "kbbbBkMk", "kkkkkkkk"], 19, 19)
put(c, ANVIL8, 19, 23)
put(c, ["kkkkk", "keeEk", "kbbBk", "kkkkk", "kbbBk", "kkkkk"], 27, 25)
SPRITES["holding:Blacksmith"] = fin32(c)

# Armory: stone store, quartered shield over the door, rack of spears, round shield leaning
c = cv32()
wall(c, 0, 17, 19, 14, "t")
roof(c, 9, 8, 9)
courses(c, 1, 19, 16, 29)
put(c, ["kkkkkk", "kccaAk", "kccaAk", "kaaCCk", ".kaCk.", "..kk.."], 7, 18)
door4(c, 8, 24)
for x in (22, 25, 28):
    put(c, ["k", "m", "M"], x, 11)
    vline(c, x, 14, 26, "b")
put(c, ["kkkkkkkkkkkk", "kbbbbbbbbbBk", "kkkkkkkkkkkk"], 20, 16)
put(c, ["kkkkkkkkkkkk", "kbbbbbbbbbBk", "kkkkkkkkkkkk"], 20, 23)
for y in range(19, 31):
    c[y][20] = c[y][31] = "k"
disc(c, 26.5, 27.5, [(1, "m"), (3, "c")], edge="k")
SPRITES["holding:Armory"] = fin32(c)

# Master Workshop: stone forge wing with sparking chimney and glowing door; plaster hall with a great gear
c = cv32()
put(c, [".y.", "y..", ".y.", "..y"], 1, 2)
wall(c, 1, 6, 4, 12, "t")
wall(c, 0, 17, 13, 14, "t")
courses(c, 1, 19, 10, 29)
put(c, [".kkk.", "kfffk", "kfyFk", "kfyFk", "kfyFk", "kffFk", "kffFk", "kffFk"], 4, 23)
wall(c, 12, 15, 19, 16, "w")
roof(c, 21, 6, 9)
disc(c, 21, 19.5, [(1, "k"), (2.5, "m")])
for dx, dy in ((0, -4), (0, 4), (-4, 0), (4, 0), (-3, -3), (3, -3), (-3, 3), (3, 3)):
    c[int(19.5 + dy + .5) if dy > 0 else int(19.5 + dy)][21 + dx] = "m"
put(c, ["kkkk", "kyyk", "kyYk", "kkkk"], 13, 16)
door4(c, 24, 24)
SPRITES["holding:Master Workshop"] = fin32(c)

# Gilded Foundry: stone workshop with a gold roof; crucible on a gantry pouring into a mould; ingot stack
c = cv32()
wall(c, 0, 17, 15, 14, "t")
roof(c, 7, 10, 7, "y")
courses(c, 1, 19, 12, 29)
win4(c, 1, 19)
door4(c, 8, 24)
vline(c, 17, 9, 30, "b")
vline(c, 16, 9, 30, "k")
hline(c, 16, 28, 9, "k")
hline(c, 17, 28, 10, "b")
put(c, ["k", "k", "k"], 25, 11)
put(c, ["kkkkkk", "kmmmMk", ".kmmMkk", "..kkyyk", ".....y", ".....y", ".....y", ".....y", ".....y", ".....y"], 22, 14)
put(c, ["kkkkkkk", "kuyyYuk", "kkkkkkk"], 24, 24)                                         # mould
put(c, ["..kkkk..", ".kyyyYk.", "kkkkkkkk", "kyyYkyyYk"[:8], "kkkkkkkk"], 17, 26)          # ingots
SPRITES["holding:Gilded Foundry"] = fin32(c)

# Stable: long plank stable, three half-doors with horses looking out, hay bale
c = cv32()
wall(c, 0, 17, 27, 14, "b")
roof(c, 13, 4, 13)
for x0, hc in ((2, "s"), (10, "h"), (18, "u")):
    put(c, ["kkkkkkk",
            "kdd" + hc + "d" + hc + "k",
            "kd" + hc * 4 + "k",
            "k" + hc * 2 + "k" + hc * 2 + "k",
            "k" + hc * 4 + "dk",
            "k" + hc * 3 + "ddk",
            "kkkkkkk",
            "kbbbbBk",
            "kbkbkBk",
            "kbbkbBk",
            "kbkbkBk",
            "kbbbbBk",
            "kkkkkkk"], x0, 18)
put(c, [".kkkkkk.", "kyyyyyYk", "kybbyyYk", "kyyyyyYk", "kYYYYYYk", "kkkkkkkk"], 24, 25)
SPRITES["holding:Stable"] = fin32(c)

# Forge: big stone forge, twin stacks throwing sparks, great hearth, quench trough
c = cv32()
put(c, ["y......y..", ".y....y.y.", "y..y.....y"], 2, 0)
wall(c, 3, 3, 5, 10, "t")
wall(c, 16, 3, 5, 10, "t")
put(c, ["..kkkkkkkkkkkkkkkkkkkk..",
        ".krrrrrrrrrrrrrrrrRRRRk.",
        "KKKKKKKKKKKKKKKKKKKKKKKK"], 0, 11)
wall(c, 0, 14, 24, 17, "t")
courses(c, 1, 16, 21, 29)
put(c, ["...kkkkkkk...",
        "..kfffffffk..",
        ".kfffyyyfffk.",
        "kffyyyyyyyfFk",
        "kfyyyyyyyyyFk",
        "kfyyyyyyyyyFk",
        "kffyyyyyyyfFk",
        "kfffffffffFFk",
        "kkkkkkkkkkkkk"], 4, 22)
put(c, ["kkkkkkkk", "keeeeeEk", "kbbbbbBk", "kbbbbbBk", "kkkkkkkk"], 24, 26)
SPRITES["holding:Forge"] = fin32(c)

# List Yard: roped sparring ring on stakes, two duellists each with a pair of blades, rack of matched swords
c = cv32()
put(c, ["..k...k...k..", ".kmk.kmk.kmk.", ".kmk.kmk.kmk.", ".kmk.kmk.kmk.", ".kmk.kmk.kmk.",
        ".kmk.kmk.kmk.", "kkykkkykkkykk", ".kbk.kbk.kbk.", "kkkkkkkkkkkkk", "kb.........bk",
        "kbkkkkkkkkkbk", "kb.........bk", "kk.........kk"], 18, 14)                          # sword rack
for xx in (0, 16):
    put(c, ["kbk"] * 11, xx, 20)
hline(c, 1, 17, 20, "c")
hline(c, 1, 17, 27, "C")
DUEL = ["m.....m", "m..k..m", "k.khk.k", ".kkakk.", "..kaAk.", "..kaAk.", "..kkkk.", "..k..k.", "..k..k."]
put(c, DUEL, 2, 21)
put(c, [r.translate(str.maketrans("aA", "cC")) for r in DUEL], 9, 21)
SPRITES["holding:List Yard"] = fin32(c)

# Court Armoury: stone hall, royal hangings, crest with crossed blades over the arched door, tall windows
c = cv32()
wall(c, 3, 14, 25, 17, "t")
roof(c, 15, 2, 12)
courses(c, 4, 16, 24, 29)
for x0 in (5, 24):
    put(c, ["yy", "aA", "aA", "aA", "aA", "aA", "aA", "a."], x0, 16)
for x0 in (8, 20):
    put(c, ["kkkk", "kyyk", "kyyk", "kkkk", "kyYk", "kyYk", "kkkk"], x0, 17)
put(c, ["m......m", ".m....m.", "..m..m..", "...mm...", "..m..m.."], 12, 15)                 # crossed blades
put(c, ["kkkkkk", "kayyAk", "kaaaAk", ".kaAk.", "..kk.."], 13, 16)                         # crest
put(c, ["..kkkk..", ".kddddk.", "kddddddk", "kddddddk", "kddddddk", "kddddddk", "kddddddk", "kddddddk"], 12, 23)
SPRITES["holding:Court Armoury"] = fin32(c)

# ================================================================ BATCH 3: commerce
def stall(c, x, y, w, a="c", b="s", goods="yfl", h=13):
    """Market stall w wide, h tall, top-left (x, y): striped awning with a scalloped edge, posts, counter of goods."""
    stripe = lambda i: a if (i // 2) % 2 == 0 else b
    put(c, ["k" * w], x, y)
    for j in (1, 2):
        put(c, ["k" + "".join(stripe(i) if i < w - 4 else SHADE.get(stripe(i), stripe(i)) for i in range(w - 2)) + "k"], x, y + j)
    put(c, ["".join("k" if i % 2 == 0 else stripe(i) for i in range(w))], x, y + 3)
    for j in range(4, h):
        c[y + j][x + 1] = "b"
        c[y + j][x + w - 2] = "B"
    g = y + h - 6
    gd = "".join(goods[(i // 3) % len(goods)] if i % 3 else "k" for i in range(w - 4))
    put(c, ["." + "".join("k" if ch != "k" else "." for ch in gd)], x + 1, g)
    put(c, ["k" + gd + "k"], x + 1, g + 1)
    put(c, ["k" * (w - 2)], x + 1, g + 2)
    put(c, ["k" + "b" * (w - 5) + "Bk"], x + 1, g + 3)
    put(c, ["k" + "".join("k" if i % 5 == 4 else "b" for i in range(w - 5)) + "Bk"], x + 1, g + 4)
    put(c, ["k" * (w - 2)], x + 1, g + 5)


def water(c, y, x0=0, x1=None):
    """Water from row y down: a broken white wavelet line on top, darker rows below."""
    x1 = len(c[0]) - 1 if x1 is None else x1
    for j in range(y, len(c)):
        for x in range(x0, x1 + 1):
            c[j][x] = "s" if (j == y and x % 5 == 1) else ("E" if (j - y) % 3 == 2 and (x + j) % 4 else "e")


# group: market stall with striped awning and goods, a crate and a sack
c = cv32()
stall(c, 2, 12, 28, h=19)
put(c, ["kkkkk", "kbkbk", "kkbkk", "kbkBk", "kkkkk"], 6, 26)
put(c, [".kk.", "kssk", "kssk", "kZZk", "kkkk"], 21, 26)
SPRITES["group:g_commerce"] = fin32(c)

# Alchemy: humble plastered workshop under a purple roof; shelf of flasks and herbs; cauldron over a fire
c = cv32()
wall(c, 0, 17, 15, 14, "w")
roof(c, 7, 10, 7, "a")
win4(c, 2, 19)
door4(c, 9, 24)
put(c, [".s.s..", "s...s.", ".s....", "..s..."], 21, 7)
put(c, ["..k...l.l..k..",
        ".kek...l..kak.",
        ".kek..kk..kak.",
        "keeEk.kcCkkaAk",
        "keeEk.kcCkkaAk",
        "kkkkkkkkkkkkkk",
        "kbbbbbbbbbbbBk",
        "kkkkkkkkkkkkkk"], 15, 12)
put(c, ["kkkkkkkkk", "kuuuuuuuk", ".kuuuuuk.", "..kuuuk..", "..k...k..", ".fyfyfyf.", "kkkkkkkkk"], 19, 24)
SPRITES["holding:Alchemy"] = fin32(c)

# Jewelry Foundry: stone shop with a gilded roof, gem sign, crucible furnace with a chimney
c = cv32()
put(c, [".s.", "s..", ".s.", "kkk"] + ["kTk"] * 13, 25, 7)
wall(c, 0, 17, 17, 14, "t")
roof(c, 8, 9, 8, "y")
courses(c, 1, 19, 14, 29)
put(c, [".kkk.", "kaaAk", "kaAAk", ".kAk.", "..k.."], 2, 19)
win4(c, 2, 25)
door4(c, 11, 24)
put(c, ["...kkkkkkk...", "..kttttttTk..", ".kttttttttTk.", "kttkkkkkkkTTk", "kttkfyyyfkTTk", "kttkfyyyfkTTk", "kttkFFFFFkTTk", "kkkkkkkkkkkkk"], 18, 23)
SPRITES["holding:Jewelry Foundry"] = fin32(c)

# Market Square: two stalls flanking a stone market cross on a stepped base
c = cv32()
stall(c, 0, 14, 13, "c", "s", "yfl", h=17)
stall(c, 19, 14, 13, "a", "s", "ysf", h=17)
put(c, ["..kkk..",
        "..kmk..",
        "kkkmkkk",
        "kmmmmMk",
        "kkkmkkk",
        "..kMk..",
        "..ktk..",
        "..ktk..",
        "..ktk..",
        "..ktk..",
        "..kTk..",
        ".kktkk.",
        ".ktttk.",
        "kkkkkkk",
        "ktttTTk",
        "kkkkkkk"], 12, 15)
SPRITES["holding:Market Square"] = fin32(c)

# Spice Merchant: great striped tent, open front, sacks of spice
c = cv32()
flag(c, 15, 1, "c", 6)
for i in range(13):
    for x in range(15 - i - 1, 15 + i + 2):
        edge = x in (15 - i - 1, 15 + i + 1)
        col = "f" if (x + i) % 4 else "c"
        c[7 + i][x] = "k" if edge else (SHADE[col] if x > 15 + i - 3 else col)
hline(c, 1, 29, 20, "K")
for y in range(21, 31):
    for x in range(2, 29):
        col = "f" if (x // 3) % 2 else "c"
        c[y][x] = "k" if x in (2, 28) else (SHADE[col] if x > 25 else col)
put(c, [".kkkkkk.", "kddddddk", "kddddddk", "kddddddk", "kddddddk", "kddddddk", "kddddddk", "kddddddk", "kddddddk"], 12, 22)
for x0, col in ((0, "y"), (22, "c"), (27, "f")):
    put(c, [".kk.", "kssk", "k" + col + SHADE[col] + "k", "k" + col + SHADE[col] + "k", "kZZk", "kkkk"], x0, 25)
SPRITES["holding:Spice Merchant"] = fin32(c)

# Harbor: stone quay with a bollard and crane post, moored cog with a furled sail, water
c = cv32()
water(c, 25)
put(c, ["k" * 14, "k" + "t" * 11 + "TTk"[:2] + "k", "ktTttTttTttTTk", "k" + "t" * 11 + "TTk"[:2] + "k", "k" * 14, "kTTTTTTTTTTTTk"], 0, 20)
put(c, [".kk.", "kmmk", "kmMk", "kkkk"], 2, 16)
put(c, [".......k........",
        ".......kccC.....",
        ".......kcC......",
        ".......k........",
        "...kkkkkkkkk....",
        "...ksssssssZk...",
        "...ksssssssZk...",
        "....kkkkkkkk....",
        ".......k........",
        ".......k........",
        "kk.....k.....kk.",
        "kbkkkkkkkkkkkbk.",
        "kbbbbbbbbbbbbBk.",
        ".kbbkbbkbbkbBk..",
        "..kbbbbbbbbBk...",
        "...kkkkkkkkk...."], 15, 8)
SPRITES["holding:Harbor"] = fin32(c)

# Merchant Quarter: three tall half-timber townhouses with stepped gables and shop fronts
c = cv32()
for x0, top in ((0, 8), (11, 3), (22, 6)):
    put(c, ["...kkk...", "..krrRk..", "..krrRk..", ".krrrRRk.", ".krrrRRk.", "krrrrRRRk"], x0, top)
    wall(c, x0, top + 6, 10, 25 - top, "w")
    for yy in range(top + 8, 23, 5):
        put(c, ["kkkk", "kyyk", "kyYk", "kkkk"], x0 + 3, yy)
        hline(c, x0 + 1, x0 + 8, yy + 4, "b")
    put(c, ["kkkkkkk", "kyyydBk", "kyyydBk", "kyYYdBk", "kkkkdBk"], x0 + 1, 26)
SPRITES["holding:Merchant Quarter"] = fin32(c)

# Esteemed Bank (was Money Lending art): stone counting house, gilded pediment with the coin, pillars, strongroom door,
# stacked gold on the steps
c = cv32()
for i in range(7):
    for x in range(15 - 2 * i, 17 + 2 * i):
        c[3 + i][x] = "k" if x in (15 - 2 * i, 16 + 2 * i) or i == 6 else ("Y" if x > 16 else "y")
disc(c, 15.5, 7, [(1.6, "s")])
put(c, ["k" * 30, "k" + "y" * 26 + "YYk"[:2] + "k", "k" * 30], 1, 10)
wall(c, 2, 13, 28, 15, "w")
for x0 in (4, 9, 20, 25):
    put(c, ["kkk"] + ["ktT"] * 13 + ["kkk"], x0, 13)
put(c, [".kkkk.", "kmmmMk", "kmkkMk", "kmmmMk", "kmmmMk", "kmmmMk", "kmmmMk", "kmmmMk", "kkkkkk"], 13, 18)
put(c, ["kkkkkk", "kyyYYk", "kkkkkk"], 13, 14)
put(c, ["k" * 32, "k" + "t" * 28 + "TTk"[:2] + "k", "k" * 32], 0, 28)
for x0 in (8, 21):
    put(c, ["kkk", "yyY", "kkk", "yyY"], x0, 24)
SPRITES["holding:Esteemed Bank"] = fin32(c)

# Money Lending (new): half-timber house with the shutter let down as a counter (the banco), scales and coin stacks
c = cv32()
wall(c, 0, 13, 20, 18, "w")
for xx in (6, 13):
    vline(c, xx, 14, 29, "b")
hline(c, 1, 18, 19, "b")
roof(c, 10, 4, 10)
win4(c, 2, 14)
win4(c, 15, 14)
door4(c, 8, 23, 8)
put(c, ["kkkkkkkkkkk", "kcscscscsck", ".kkkkkkkkk."], 19, 15)                                # awning
put(c, ["..kmk..", "kk.m.kk", "m..m..m", "y..m..y", "kkkmkkk"], 21, 18)                     # scales
put(c, ["kkkkkkkkkkkk", "kbbbbbbbbbBk", "kkkkkkkkkkkk", ".kb......kb.", ".kb......kb.", ".kb......kb.",
        ".kk......kk."], 19, 23)
put(c, ["kk", "yY", "yY"], 29, 20)
put(c, ["kk", "yY"], 27, 21)
put(c, [".kkkk.", "kbmmBk", "kbbbBk", "kkkkkk"], 23, 26)                                   # strongbox under the counter
SPRITES["holding:Money Lending"] = fin32(c)

# Shipyard: ribbed hull on a slipway, timber crane hoisting a plank
c = cv32()
put(c, ["k" * 14, ".........kbBk.", "..........m...", "..........m...", "........kbbbBk", "........kkkkkk"], 17, 3)
vline(c, 28, 4, 30, "b")
vline(c, 29, 4, 30, "B")
vline(c, 27, 4, 30, "k")
vline(c, 30, 4, 30, "k")
put(c, ["k.k.k.k.k.k.k.k.k.k.k",
        "kbkbkbkbkbkbkbkbkbkbk",
        "kbkbkbkbkbkbkbkbkbkbk",
        "kbkbkbkbkbkbkbkbkbkBk",
        ".kbkbkbkbkbkbkbkbkBk.",
        ".kbbbbbbbbbbbbbbbbBk.",
        "..kbbbbbbbbbbbbbbBk..",
        "...kkkkkkkkkkkkkkk..."], 2, 15)
put(c, ["k" * 32, "k" + "b" * 29 + "Bk", "kbkbbbbkbbbbkbbbbkbbbbkbbbbkbBk"[:31] + "k", "k" * 32, ".kB" + "." * 7 + "kB" + "." * 8 + "kB" + "." * 6 + "kB."], 0, 23)
for y in range(28, 31):
    for x in (1, 11, 21, 29):
        c[y][x] = "k"
SPRITES["holding:Shipyard"] = fin32(c)

# Courtyard: seen from the front and above — a U of arcaded ranges under red tile round a paved court (joints run
# back to a point over the far range), the side ranges' front ends square the outline, a fountain in the middle so
# the open ground reads as a court
def fountain(c, cx, cy, rx=7.5, ry=3.4):
    """Round basin seen from above the front, centre (cx, cy), hard outline 'K': stone rim round the water, drum
    below, a column with a bowl spilling into it."""
    H, W_ = len(c), len(c[0])
    ins = lambda x, y: ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1
    bot = {}
    for y in range(H):
        for x in range(W_):
            if not ins(x, y):
                continue
            bot[x] = y
            if not all(ins(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                c[y][x] = "K"
            elif ((x - cx) / (rx - 1.6)) ** 2 + ((y - cy) / (ry - 1.1)) ** 2 > 1:
                c[y][x] = "T" if x > cx + 2 else "t"
            else:
                c[y][x] = "E" if x > cx + 2 else "e"
    for x, yb in bot.items():
        for j in (1, 2):
            c[yb + j][x] = "T" if x > cx + 2 else "t"
        c[yb + 3][x] = "K"
    for x in (min(bot), max(bot)):
        for j in (1, 2):
            c[bot[x] + j][x] = "K"
    x0 = int(cx - .5)
    for y in range(int(cy - 5), int(cy) + 1):
        put(c, ["KtTK"], x0 - 1, y)
    put(c, ["..KK..", "KKeeKK", "KtttTK", ".KTTK."], x0 - 2, int(cy - 7))
    for y in range(int(cy - 4), int(cy - 1)):
        c[y][x0 - 3] = c[y][x0 + 4] = "e"
    c[int(cy)][x0 - 3] = c[int(cy)][x0 + 4] = "s"


c = cv32()
BACK, L0, R0, SL = 17, 9, 22, 13 / 8          # far edge of the court, its corners, side ranges' slope (rows per px)
court_edge = lambda x: BACK + (L0 - x) * SL if x < L0 else (BACK + (x - R0) * SL if x > R0 else BACK)
for x in range(32):
    ye = court_edge(x)
    t = (ye - BACK) / 13                      # 0 at the far range, 1 at the front
    e = round(ye)
    top = e - round(6 + 3 * t)                # arcade grows toward the viewer
    r = round(4 + 2 * t)                      # and so does its roof
    side = "L" if x < L0 else ("R" if x > R0 else "B")
    for y in range(31):
        c[y][x] = "s" if y >= e else ("W" if side == "L" else "w") if y >= top else "r" if y >= top - r else "."
    for y, ch in ((top - r, "k"), (top - r + 2, "R"), (top - 1, "K")):
        if 0 <= y < 31:
            c[y][x] = ch
    d = ye - BACK                             # piers and dark arches: every 4 px on the far range, by depth on the sides
    if ((x - L0) % 4 in (2, 3) and L0 + 1 < x < R0 - 1) if side == "B" else (1.2 < d % 4.4 < 3.4 and d > 1.5):
        for y in range(top + 2, min(e, 31)):
            c[y][x] = "d"
    if 0 <= e - 1 < 31 and c[e - 1][x] != "d":
        c[e - 1][x] = "T"
for y in (19, 22, 26, 30):                    # paving: courses closer together toward the back
    for x in range(32):
        if c[y][x] == "s":
            c[y][x] = "Z"
for X in range(-12, 44, 5):                   # joints running back to a point over the far range
    for y in range(BACK, 31):
        x = round(15.5 + (X - 15.5) * (y - 3) / 27)
        if 0 <= x < 32 and c[y][x] == "s":
            c[y][x] = "Z"
for x in range(R0 + 1):                       # shadow at the foot of the far and left ranges
    e = round(court_edge(x))
    if e < 31 and c[e][x] in "sZ":
        c[e][x] = "T"
for x0 in (0, 25):                            # the side ranges' front ends, a lit window in each
    wall(c, x0, 19, 7, 12, "w")
    put(c, ["kkk", "kyk", "kYk", "kkk"], x0 + 2, 22)
fountain(c, 15.5, 24)
SPRITES["holding:Courtyard"] = fin32(c)

# Artisan Workshop: stone-footed workshop with a hanging sign; potter's wheel, glazed vases
c = cv32()
wall(c, 0, 17, 17, 14, "w")
for xx in (5, 11):
    vline(c, xx, 18, 23, "b")
hline(c, 1, 15, 23, "b")
for y in range(24, 30):
    for x in range(1, 16):
        if c[y][x] in "wW":
            c[y][x] = "t" if x < 14 else "T"
courses(c, 1, 25, 13, 29)
roof(c, 8, 9, 8)
win4(c, 1, 18)
win4(c, 12, 18)
door4(c, 6, 24)
put(c, ["kkkkk", "....k", "..kkkk", "..kaAk", "..kkkk"], 16, 17)
put(c, ["..kk..", ".kccCk", ".kccCk", "..kk..", ".kkkkk", "kbbbbBk", "kkkkkkk"], 17, 24)
put(c, [".k.", "kak", "kaA", "kaA", "kak", ".k."], 25, 25)
put(c, [".kk..", "kyyk.", ".kyYk", ".kyYk", ".kkk."], 27, 26)
SPRITES["holding:Artisan Workshop"] = fin32(c)

# Court Artists: stone studio, purple roof, tall north window; easel with a painted canvas, marble bust on a plinth
c = cv32()
wall(c, 0, 17, 17, 14, "t")
roof(c, 8, 9, 8, "a")
courses(c, 1, 19, 14, 29)
put(c, [".kkkk.", "kyyyyk", "kyyyYk", "kkkkkk", "kyyyYk", "kyyyYk", "kkkkkk"], 2, 18)
door4(c, 11, 24)
put(c, ["..kk...",
        ".kkkkkk",
        ".klyeEk",
        ".kycaAk",
        ".klllLk",
        ".kkkkkk",
        ".k.k.k.",
        "k..k..k",
        "k..k..k",
        "k..k..k",
        "k..k..k"], 17, 20)
put(c, [".kk.", "kssk", "kssZ", ".kZ.", "kssZ", "kttT", "kttT", "kttT", "kttT", "kkkk"], 26, 21)
SPRITES["holding:Court Artists"] = fin32(c)

# Emporium: tall stone-footed warehouse with loading doors, hoist beam with a bale over the quay
c = cv32()
water(c, 27)
wall(c, 0, 10, 19, 17, "w")
for xx in (4, 14):
    vline(c, xx, 11, 25, "b")
hline(c, 1, 17, 18, "b")
roof(c, 9, 1, 9)
put(c, ["kkkkk", "kbbBk", "kbkBk", "kbbBk", "kkkkk"], 7, 11)
put(c, [".kkkkk.", "kdddddk", "kdddddk", "kdddddk", "kdddddk", "kdddddk", "kdddddk", "kdddddk"], 6, 19)
win4(c, 1, 12)
win4(c, 15, 12)
put(c, ["k" * 13, "b" * 12 + "B", "...........m.", "...........m.", "..........kkk", "..........kbB", "..........kkk"], 18, 8)
put(c, ["k" * 14, "kbbbbbbbbbbbBk", "kk.kk....kk.kk"], 18, 25)
SPRITES["holding:Emporium"] = fin32(c)


# ================================================================ BATCH 4: court
# group: hall between two banner turrets
c = cv32()
for x0 in (0, 25):
    flag(c, x0 + 3, 0, "a", 7)
    wall(c, x0, 9, 7, 22, "t")
    cren(c, x0, 7, 7)
    put(c, SLIT, x0 + 3, 12)
    win4(c, x0 + 1, 19)
wall(c, 6, 17, 19, 14, "t")
roof(c, 15, 8, 9)
courses(c, 7, 19, 22, 29)
for o in (8, 19):
    put(c, ["kkkk", "kyyk", "kyyk", "kkkk", "kyYk", "kkkk"], o, 19)
put(c, ["kak", "kAk", "kak", ".k."], 14, 19)
door4(c, 13, 24)
SPRITES["group:g_court"] = fin32(c)

# Inn: two-storey half-timber with a jettied upper floor, hanging sign with a tankard, lantern, barrel
c = cv32()
wall(c, 0, 13, 23, 8, "w")
roof(c, 11, 2, 11)
for xx in (5, 11, 17):
    vline(c, xx, 15, 19, "b")
for o in (1, 7, 13, 19):
    win4(c, o, 15)
hline(c, 0, 22, 20, "K")
wall(c, 1, 21, 21, 10, "w")
for xx in (6, 16):
    vline(c, xx, 23, 29, "b")
for o in (2, 17):
    put(c, ["kkkk", "kyyk", "kyyk", "kkkk", "kyYk", "kkkk"], o, 23)
put(c, [".kkkk.", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk"], 9, 22)
put(c, ["k.", "y.", "Y."], 15, 23)                                                        # lantern
put(c, ["kkkkkkkk", ".......k", ".....kkk", ".....k.k"], 22, 12)                           # sign bracket
put(c, ["kkkkkk", "kccccC", "kcyycC", "kcyYcC", "kccccC", "kkkkkk"], 25, 16)              # sign
put(c, BARREL8, 24, 23)
SPRITES["holding:Inn"] = fin32(c)

# Jester's Court: purple-roofed hall, harlequin facade, belled pennant pole with streamers
c = cv32()
wall(c, 0, 15, 21, 16, "a")
for j in range(16, 30):
    for x in range(1, 20):
        q = ((x + j) // 3 + (x - j) // 3) % 3
        c[j][x] = "cya"[q]
shade_rect(c, 18, 16, 19, 29)
roof(c, 10, 5, 10, "a")
put(c, [".y.", "kyk"], 9, 3)
put(c, [".kkkk.", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk"], 8, 24)
vline(c, 25, 3, 30, "k")
put(c, [".y", "y.", "kc", "kcc", "kccC", "ky", "kyy", "kyyY", "ka", "kaa", "kaaA", "ky"], 25, 3)
put(c, ["kk", "kk"], 24, 29)
SPRITES["holding:Jester's Court"] = fin32(c)

# Bell Tower: stone campanile, open belfry with the bell, red spire, clock face, door
c = cv32()
spire(c, 15, 0, 12)
wall(c, 10, 11, 11, 20, "t")
courses(c, 11, 20, 18, 29)
put(c, ["kkkkkkk", "kdddddk", "kddkddk", "kdkyykk"[:7], "kdyyyYk", "kyyyyYk", "kkkkkkk"], 12, 12)
disc(c, 15, 21, [(.6, "k"), (2.4, "s")])
c[19][15] = c[20][15] = "k"
c[21][16] = "k"
door4(c, 13, 25)
SPRITES["holding:Bell Tower"] = fin32(c)

# Embassy: colonnaded residence, flags of many houses along the cornice
c = cv32()
for x0, col in ((2, "c"), (8, "a"), (14, "l"), (20, "e"), (26, "y")):
    flag(c, x0, 3, col, 7)
put(c, ["k" * 32, "t" * 30 + "TT", "k" * 32], 0, 10)
wall(c, 1, 13, 30, 18, "w")
for x0 in (4, 9, 21, 26):
    put(c, ["kkk"] + ["ktT"] * 16 + ["kkk"], x0, 13)
put(c, ["kkkk", "kyyk", "kyYk", "kkkk"], 14, 15)
put(c, [".kkkk.", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk"], 13, 22)
SPRITES["holding:Embassy"] = fin32(c)

# Academy: lecture hall under a gilded lantern dome, open-book roundel over the door, tall windows
c = cv32()
put(c, [".k.", "kyk", ".k.", "kyk", "kYk"], 14, 0)
disc(c, 15, 12, [(7, "y")])
wall(c, 2, 11, 27, 20, "t")
put(c, ["k" * 27], 2, 14)
courses(c, 3, 16, 26, 29)
disc(c, 15, 17.5, [(2.6, "s")])
vline(c, 15, 16, 19, "k")
for o in (5, 22):
    put(c, ["kkkk", "kyyk", "kyyk", "kkkk", "kyYk", "kyYk", "kkkk"], o, 17)
put(c, [".kkkk.", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk"], 12, 22)
hline(c, 1, 29, 30, "T")
SPRITES["holding:Academy"] = fin32(c)

# University: tall gate tower with a purple cap, two wings under purple roofs, rows of lit windows
c = cv32()
for x0 in (0, 19):
    wall(c, x0, 17, 13, 14, "t")
    roof(c, x0 + 6, 11, 6, "a")
    for o in (1, 8):
        put(c, ["kkkk", "kyyk", "kyYk", "kkkk"], x0 + o, 19)
        put(c, ["kkkk", "kyyk", "kyYk", "kkkk"], x0 + o, 25)
wall(c, 11, 6, 10, 25, "t")
spire(c, 15, 0, 7, "a")
put(c, ["k" * 10], 11, 6)
disc(c, 15.5, 10, [(.5, "k"), (2, "s")])
put(c, ["kkkk", "kyyk", "kyyk", "kkkk", "kyYk", "kkkk"], 14, 14)
put(c, [".kkkk.", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk"], 13, 22)
SPRITES["holding:University"] = fin32(c)

# Collegium Archives: stone archive tower with a purple roof and a lit reading room; open shed of scroll pigeonholes
c = cv32()
wall(c, 2, 9, 13, 22, "t")
courses(c, 3, 11, 12, 29)
roof(c, 8, 2, 7, "a")
put(c, ["kkkkk", "kyyyk", "kyYYk", "kkkkk"], 6, 12)
put(c, ["kkkkk", "kyyyk", "kyYYk", "kkkkk"], 6, 18)
door4(c, 6, 24)
wall(c, 15, 17, 16, 14, "w")
roof(c, 22, 11, 7, "a")
for y0 in (19, 23, 27):
    put(c, ["k" * 12] + ["".join("ks"[(x + y0) % 3 == 0] if x % 3 else "k" for x in range(12))] * 2, 17, y0)
SPRITES["holding:Collegium Archives"] = fin32(c)

# Courier Network: dovecote tower with birds, post stable, saddled horse at the door
c = cv32()
put(c, ["s...s....", ".s.s...s.", ".......s."], 0, 0)
spire(c, 5, 3, 8, "a")
wall(c, 1, 10, 9, 21, "w")
for y0 in (12, 16, 20):
    put(c, ["d.d.d"], 3, y0)
door4(c, 3, 24)
wall(c, 9, 17, 15, 14, "w")
hline(c, 10, 22, 22, "b")
roof(c, 16, 10, 7)
win4(c, 11, 18)
put(c, ["kkkkkk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk"], 16, 23)
put(c, ["..kk.......",
        ".kbbk......",
        "kbkbbk.....",
        "kbbbbk.....",
        ".kkbbkkkkk.",
        "...kbccccbk",
        "...kbcCCbBk",
        "...kbbbbbBk",
        "...kkbkkkbk",
        "....kb..kb.",
        "....kb..kb.",
        "....kk..kk."], 21, 19)
SPRITES["holding:Courier Network"] = fin32(c)


# ================================================================ BATCH 5: devotion
# Piety (Lenavorites): orders, records, austerity. Rising builds in plaster, Established in dressed stone; the
# Inquisition line (Episcopal Court -> Interrogation Chambers -> Execution Dock) darkens toward its Cunning pair.
CROSS = [".k.", "kkk", ".k.", ".k."]                      # small black cross (skylines, wonders)
CROSS5 = ["..k..", ".kyk.", "kyyyk", ".kyk.", ".kyk."]   # gold cross for 32px holdings


def steeple(c, cx, y, h=10, roof="r"):
    """Gold cross on a steep spire: cross top at (cx, y), h rows of spire under it."""
    put(c, CROSS5, cx - 2, y)
    spire(c, cx, y + 5, h, roof)


# group: plaster chapel with a stone tower and spire, lit lancets, arched door
c = cv32()
steeple(c, 16, 0, 8)
wall(c, 13, 13, 7, 8, "t")
wall(c, 4, 20, 25, 11, "w")
roof(c, 16, 14, 6)
for o in (6, 23):
    put(c, ["kkkk", "kyyk", "kyyk", "kyyk", "kyYk", "kkkk"], o, 22)
put(c, [".kkkk.", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk"], 13, 22)
SPRITES["group:g_devotion"] = fin32(c)

# Chandlery: plank shop with racks of dipped candles, a great candle sign on a post
c = cv32()
wall(c, 0, 17, 17, 14, "b")
for xx in (4, 8, 12):
    vline(c, xx, 19, 29, "B")
roof(c, 8, 9, 8)
put(c, ["kkkkkkk", "kk.k.kk", "kZ.Z.Zk", "kZ.Z.Zk", "kkkkkkk"], 2, 19)
door4(c, 11, 24)
put(c, ["..y..", "..f..", ".kkk.", ".kwk.", ".kwW.", ".kwW.", ".kwW.", ".kwW.", ".kwW.", "kkkkk", "..b..", "..b..", "..b..", "..b..", "..b..", "..b..", "..B..", ".kkk."], 18, 13)
put(c, [".y.y.y.", ".s.s.s.", ".s.s.s.", ".Z.Z.Z.", "kkkkkkk", "kbbbbBk", "kb...Bk", "kk...kk"], 24, 23)
SPRITES["holding:Chandlery"] = fin32(c)

# Interrogation Chambers: squat dark keep, barred windows, iron-studded door, red lantern
c = cv32()
cren(c, 1, 9, 24)
box(c, 1, 11, 24, 20, "u")
for y in range(13, 30, 3):
    for x in range(2 + (y // 3) % 2 * 2, 24, 4):
        c[y][x] = "d"
for x0 in (4, 18):
    put(c, ["kkkk", "kmdm", "kdmd", "kmdm", "kkkk"], x0, 14)
put(c, [".kkkkkk.", "kmdmdmdk", "kdmdmdmk", "kmdmdmdk", "kdmdmdmk", "kmdmdmdk", "kdmdmdmk", "kmdmdmdk"], 9, 23)
put(c, ["kkkk", "...k", "...k", "..kkk", "..kck", "..kCk", "..kkk"], 25, 13)
SPRITES["holding:Interrogation Chambers"] = fin32(c)

# Priory: plastered bellcote chapel with a cross, cloister arcade range
c = cv32()
put(c, CROSS5, 4, 2)
put(c, [".kkk.", "kdydk", "kkkkk"], 4, 7)
wall(c, 0, 16, 13, 15, "w")
roof(c, 6, 10, 6)
put(c, ["kkkk", "kyyk", "kyyk", "kyYk", "kkkk"], 1, 18)
put(c, [".kk.", "kddk", "kddk", "kddk", "kddk", "kddk", "kddk"], 7, 24)
roof(c, 22, 12, 9)
wall(c, 13, 21, 19, 10, "w")
for x0 in (14, 19, 24):
    put(c, [".kkk.", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk"], x0, 23)
hline(c, 14, 30, 29, "W")
SPRITES["holding:Priory"] = fin32(c)

# Abbey: long stone nave with a rose window, west tower with belfry, spire and cross
c = cv32()
wall(c, 0, 16, 21, 15, "t")
roof(c, 10, 6, 10)
courses(c, 1, 18, 18, 29)
disc(c, 10, 11, [(1, "y"), (2.4, "c"), (3.2, "a")])
for o in (2, 15):
    put(c, ["kkkk", "kyyk", "kyyk", "kyyk", "kyYk", "kkkk"], o, 18)
put(c, [".kkkk.", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk"], 7, 23)
steeple(c, 26, 0, 6)
wall(c, 21, 11, 10, 20, "t")
courses(c, 22, 13, 27, 29)
put(c, ["kkkk", "kdyk", "kyYk", "kkkk"], 24, 13)
put(c, SLIT, 25, 19)
door4(c, 24, 25)
SPRITES["holding:Abbey"] = fin32(c)

# Reliquary Sanctum (key: Reliquary): gilded shrine-house, open door showing a glowing casket, candles either side
c = cv32()
put(c, CROSS5, 13, 0)
wall(c, 4, 15, 25, 16, "w")
roof(c, 15, 5, 10, "y")
put(c, ["kkkkkkkkk",
        "kdddddddk",
        "kddyyyddk",
        "kdyyyyydk",
        "kdkkkkkdk",
        "kdkyyykdk",
        "kdkYYYkdk",
        "kdkkkkkdk",
        "kdddddddk",
        "kdddddddk",
        "kdddddddk",
        "kdddddddk",
        "kdddddddk"], 11, 18)
for x0 in (6, 23):
    put(c, ["y", "f", "s", "s", "Z", "k"], x0 + 1, 22)
    put(c, ["kkk"], x0, 28)
SPRITES["holding:Reliquary"] = fin32(c)

# Monastery: stone dormitory range, chapel with a bellcote, walled garden of herb beds
c = cv32()
wall(c, 0, 17, 15, 14, "t")
roof(c, 7, 10, 7)
courses(c, 1, 19, 12, 29)
for o in (2, 9):
    win4(c, o, 19)
door4(c, 5, 24)
put(c, CROSS5, 20, 0)
put(c, [".kkk.", "kdydk", "kkkkk"], 20, 5)
wall(c, 15, 15, 13, 16, "t")
roof(c, 21, 8, 7)
courses(c, 16, 17, 25, 29)
put(c, ["kkkk", "kyyk", "kyyk", "kyYk", "kkkk"], 20, 17)
put(c, [".kk.", "kddk", "kddk", "kddk", "kddk", "kddk"], 20, 25)
put(c, ["kkkk", "kLlk", "kllk", "ktTk", "ktTk"], 28, 26)
SPRITES["holding:Monastery"] = fin32(c)

# Execution Dock: gallows with a hooded figure on a dark stone quay, gibbet cage, water below
c = cv32()
water(c, 26)
box(c, 0, 20, 32, 6, "u")
for x in range(2, 31, 4):
    c[22][x] = "d"
put(c, ["k" * 17, "k" + "b" * 15 + "B", "kbk...........m..", "kbBk..........m..", "kbB...........m..", "kbB..........kck.", "kbB..........kcC.", "kbB..........kcC.", "kbB...........k..", "kbB..............", "kbB..............", "kbB.............."], 3, 8)
put(c, ["kkkkkkk", "kb...bk", "kb.b.bk"], 12, 20)
put(c, [".kkk.", "kmkmk", "kmkMk", "kmkMk", ".kkk.", "..k.."], 24, 11)
vline(c, 26, 17, 19, "k")
SPRITES["holding:Execution Dock"] = fin32(c)

# Hospitaller: stone hall with tall windows, black banner with a white cross on a pole
c = cv32()
wall(c, 0, 17, 21, 14, "t")
roof(c, 10, 7, 10)
courses(c, 1, 19, 18, 29)
for o in (2, 15):
    put(c, ["kkkk", "kyyk", "kyyk", "kkkk", "kyYk", "kkkk"], o, 19)
put(c, [".kkkk.", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk"], 8, 23)
vline(c, 23, 4, 30, "k")
put(c, ["kkkkkkkk", "dddsdddk", "dddsdddk", "dssssssk", "dddsdddk", "dddsdddk", "dddsdddk", "dd.ddd.k", "d...d..."], 24, 5)
SPRITES["holding:Hospitaller"] = fin32(c)

# Episcopal Court: half-timbered hall under a purple roof, mitre finial, sealed charter over the door, banners
c = cv32()
put(c, [".k.", "kyk", "kyk", "kak", "kak"], 14, 0)
wall(c, 1, 16, 29, 15, "w")
for xx in (8, 22):
    vline(c, xx, 17, 29, "b")
hline(c, 1, 28, 21, "b")
roof(c, 15, 5, 11, "a")
for x0 in (3, 26):
    put(c, ["aA", "aA", "yy", "aA", "aA", "a."], x0, 17)
for o in (10, 18):
    win4(c, o, 17)
put(c, ["kkkkkk", "kssssk", "kssZZk", "kkckkk", "...k.."], 13, 17)
put(c, [".kkkk.", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk"], 13, 23)
SPRITES["holding:Episcopal Court"] = fin32(c)

# Apothecary: humble shop with herbs drying under the eaves, jars in the window, mortar-and-pestle sign, herb tub
c = cv32()
wall(c, 0, 17, 17, 14, "w")
hline(c, 1, 15, 22, "b")
roof(c, 8, 9, 8)
put(c, ["l.n.l.n.l.n", "l.n.l.n.l.n", "..n...n...n"], 2, 17)
put(c, ["kkkkkkk", "kekakck", "kEkAkCk", "kkkkkkk", "kclylek", "kkkkkkk"], 1, 23)
door4(c, 11, 24)
put(c, ["kkkkkk", ".....k", "...kkkk", "..kmmMk", "..kmmMk", "...kkk."], 16, 16)
put(c, ["l.l.l.", "llLlLl", "LlLLlL", "kkkkkk", "kbbbBk", "kbbbBk", "kkkkkk"], 23, 24)
SPRITES["holding:Apothecary"] = fin32(c)

# Infirmary: long plastered ward, red cross on the gable, row of lit windows, door
c = cv32()
wall(c, 0, 19, 31, 12, "w")
roof(c, 15, 4, 15)
for xx in (7, 23):
    vline(c, xx, 20, 29, "b")
disc(c, 15, 12, [(3.4, "s")])
put(c, ["c", "c", "c", "c", "c"], 15, 10)
put(c, ["ccccc"], 13, 12)
for o in (1, 9, 18, 26):
    win4(c, o, 21)
put(c, [".kkkk.", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk"], 13, 25)
SPRITES["holding:Infirmary"] = fin32(c)

# Pilgrimage Site: stone cross on a grassy mound, worn path, candles, a pilgrim with a staff
c = cv32()
put(c, ["....kkkk....",
        "....kttk....",
        "....kttT....",
        "kkkkkttTkkkk",
        "kttttttTTTTk",
        "kTTTTTTTTTTk",
        "kkkkkttTkkkk",
        "....kttT....",
        "....kttT....",
        "....kttT....",
        "....kttT....",
        "....kttT....",
        "....kttT....",
        "...kkuukk..."], 9, 2)
for y, x0, x1 in ((16, 9, 20), (17, 7, 22), (18, 5, 24), (19, 4, 25), (20, 3, 26), (21, 2, 27), (22, 1, 28), (23, 0, 29), (24, 0, 30)) + tuple((y, 0, 31) for y in range(25, 31)):
    for x in range(x0, x1 + 1):
        c[y][x] = "n" if (x * 7 + y * 3) % 11 == 0 else ("L" if x > (x0 + x1) // 2 + 3 else "l")
    if y < 25:
        c[y][x0] = c[y][x1] = "k"
hline(c, 10, 19, 15, "k")
for (x, y) in ((15, 16), (16, 17), (16, 18), (15, 19), (14, 20), (14, 21), (15, 22), (15, 23), (16, 24), (17, 25), (17, 26), (16, 27), (16, 28), (17, 29), (17, 30)):
    c[y][x] = "s"
for x in (7, 23):
    c[17][x] = "y"
    c[18][x] = "s"
put(c, ["..h..", ".kak.", "kaaAk", "kaaAk", "kaaAk", ".a.A."], 23, 12)
vline(c, 28, 10, 18, "b")
SPRITES["holding:Pilgrimage Site"] = fin32(c)

# Unforgotten Shrine: roofed wayside shrine on a carved pillar, lit niche, candles and offerings on a stone plinth
c = cv32()
roof(c, 9, 2, 7)
put(c, ["kkkkkkkkkkk", "kdddddddddk", "kddyyyyyddk", "kdyykkkyydk", "kdyyyyyYYdk", "kddYYYYYddk", "kkkkkkkkkkk"], 4, 9)
put(c, ["kttTk"] * 8, 7, 16)
put(c, ["..y.......y.....y..", "..s...c...s.....s..", "..s..ccC..s..c..s..", "..Z.kkkkk.Z.cC..Z..", ".kkkktttTkkkkkkkkkk"[:19]], 4, 20)
put(c, ["k" * 30, "k" + "t" * 26 + "TTk"[:2] + "k", "k" + "T" * 28 + "k", "k" * 30, "k" + "u" * 28 + "k", "k" * 30], 1, 25)
SPRITES["holding:Unforgotten Shrine"] = fin32(c)


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


# group: plaster barn, braced double doors, loft hatch, hay bale
c = cv32()
wall(c, 1, 17, 23, 14, "w")
roof(c, 12, 6, 11)
put(c, ["kkkk", "kddk", "kddk", "kkkk"], 11, 11)                                         # loft hatch
put(c, ["kkkkkkkkkkk"] + ["k" + "".join("k" if j in (i // 2, 3 - i // 2) else ("B" if j == 3 else "b") for j in range(4))
        + "k" + "".join("k" if j in (i // 2, 3 - i // 2) else ("B" if j == 3 else "b") for j in range(4)) + "k" for i in range(8)]
    + ["kkkkkkkkkkk"], 7, 20)                                                           # X-braced double doors
put(c, [".kkkkkk.", "kyyyyyYk", "kybbyyYk", "kyyyyyYk", "kYYYYYYk", "kkkkkkkk"], 24, 25)  # hay bale
SPRITES["group:g_husbandry"] = fin32(c)

# Herb Garden: cottage, two raised beds of herbs in flower, wattle fence
c = cv32()
wall(c, 0, 19, 13, 12, "w")
hline(c, 1, 11, 23, "b")
roof(c, 6, 13, 6)
win4(c, 2, 20)
door4(c, 7, 24)
for x0, flw in ((14, "a"), (23, "y")):
    put(c, [".l..l..l",
            "l" + flw + "lLl" + flw + "lL",
            "lLl" + flw + "LlLl",
            "LlLLlLLL",
            "kkkkkkkk",
            "kbbbbbBk",
            "kkkkkkkk"], x0, 20)
fence32(c, 13, 31, 27)
SPRITES["holding:Herb Garden"] = fin32(c)

# Animal Husbandry: plank byre with a hayloft, cow in the paddock, wattle fence
c = cv32()
wall(c, 14, 17, 17, 14, "b")
for xx in range(17, 29, 3):
    vline(c, xx, 19, 29, "B")
roof(c, 22, 9, 8)
put(c, ["kkkk", "kyyk", "kyYk", "kkkk"], 20, 12)                                         # hayloft
put(c, ["kkkkkk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk"], 19, 23)
put(c, ["kk..............",
        "kskk..kkkkkkkk..",
        "ksdsk.ksssddsk..",
        "ksssskssssdddsk.",
        ".khhsssssssssskk",
        "..kkkssssssssk.k",
        "....kZZZZZZZZk..",
        "....kZk.kZkZk...",
        "....kdk..kdkdk..",
        "....kk...kkkk..."], 0, 19)                                                     # cow
fence32(c, 0, 13, 27)
SPRITES["holding:Animal Husbandry"] = fin32(c)

# Saddlery: half-timber shop, bridle on the sign bracket, saddle on a trestle
c = cv32()
wall(c, 0, 17, 17, 14, "w")
for xx in (5, 11):
    vline(c, xx, 18, 29, "b")
hline(c, 1, 15, 22, "b")
roof(c, 8, 9, 8)
win4(c, 1, 18)
win4(c, 12, 18)
door4(c, 6, 24)
put(c, ["kkkkkk", ".....k", "....kbk", "....kbk", "....kbk", "...kmkmk", "....kbk"], 16, 17)   # bracket + bridle
put(c, ["..kk.......kk",
        ".kbbk.....kbbk",
        ".kbbbkkkkkbbBk",
        "kcbbbbbbbbbbBck",
        "kcccccccccccCCk",
        ".kkkkkkkkkkkkk.",
        "..kbk.....kbk..",
        ".kbk.......kbk.",
        ".kbk.......kbk.",
        "kbk.........kbk"], 17, 21)                                                     # saddle on a trestle
SPRITES["holding:Saddlery"] = fin32(c)

# short-legged unsaddled horse for 32px holdings, facing left (the 48px HORSE is further down)
HORSE_S = ["..kk..........", ".kbbk.........", "kbkbbk........", "kbbbbk........", "kbbbbbk.......",
           ".kkkbbbkkkkkk.", "....kbbbbbbbBk", "....kbbbbbbbBk", "....kbbbbbbBBk", "....kkbkkkkbkk",
           "....kbk...kbk.", "....kbk...kbk.", "....kmk...kBk.", "....kkk...kkk."]

# Farriery: open-sided shoeing shed on posts, horseshoes on the beam, horse tied at the post, anvil and hearth
c = cv32()
roof(c, 9, 10, 9)
for xx in (1, 17):
    put(c, ["kbk"] * 11, xx - 1, 20)
hline(c, 1, 17, 20, "b")
for x0 in (4, 8, 12):
    put(c, ["kmk", "k.k", ".k."], x0, 21)                                                  # shoes hung on the beam
put(c, ["..kkk..", ".kfyfk.", "kttttTk", "kttttTk", "kkkkkkk"], 3, 26)                      # small hearth
put(c, ANVIL, 10, 26)
put(c, HORSE_S, 18, 17)                                                                      # facing the shed
put(c, ["kk", "..k"], 17, 19)                                                      # tether
SPRITES["holding:Farriery"] = fin32(c)

# Avenery: the horses' provender store — plank barn with a sack of oats in the loft door, sacks stacked at the door;
# a hay rack on the gable end where a horse feeds
c = cv32()
wall(c, 0, 15, 17, 16, "b")
for xx in (5, 11):
    vline(c, xx, 16, 29, "B")
roof(c, 8, 6, 9)
put(c, ["kkkkk", "kdkkd", "kkyYk", "kkyYk", "kkkkk"], 6, 16)                               # loft door, sack in it
door4(c, 1, 23, 8)
for x0, y0 in ((6, 26), (11, 26), (8, 22)):
    put(c, [".kkk.", "kyyYk", "kyyYk", "kkkkk"], x0, y0)                                   # oat sacks
put(c, ["kkkkkk", "kyyyYk", "kbkbkk", "kkkkkk"], 16, 17)                                   # hay rack on the gable end
put(c, HORSE_S, 18, 17)
SPRITES["holding:Avenery"] = fin32(c)

# Vineyard: trellised vines in three tiers on four posts, grape bunches
c = cv32()
for x in (0, 10, 21, 31):
    vline(c, x, 7, 30, "b")
    c[6][x] = "k"
for y0 in (7, 15, 23):
    hline(c, 0, 31, y0, "k")
    for x in range(1, 31):
        if x in (10, 21):
            continue
        c[y0 + 1][x] = "l"
        c[y0 + 2][x] = "l" if x % 3 else "L"
        c[y0 + 3][x] = "L" if x % 2 else "."
    for x0 in (2, 13, 24) if y0 != 15 else (6, 16, 26):
        put(c, ["aaA", "aAA", ".A."], x0, y0 + 3)
SPRITES["holding:Vineyard"] = fin32(c)

# Orchard: two apple trees, ladder against one, basket of apples
c = cv32()
tree32(c, 0, 13, "c")
tree32(c, 13, 11, "c")
for y in range(18, 31):
    c[y][12] = c[y][15] = "k"
    if y % 3 == 0:
        hline(c, 12, 15, y, "b")
put(c, [".c.c.c.", "kcCkcCk", "kbbbbBk", "kbBbBBk", ".kkkkk."], 25, 26)
SPRITES["holding:Orchard"] = fin32(c)

# Bakery: half-timber shop, awning over a window of loaves, domed bread oven glowing, peel
c = cv32()
put(c, [".s.", "s..", ".s.", "kkk", "kTk", "kTk", "kTk", "kTk", "kTk"], 10, 3)
wall(c, 0, 17, 17, 14, "w")
hline(c, 1, 15, 22, "b")
vline(c, 8, 18, 21, "b")
roof(c, 8, 9, 8)
win4(c, 2, 18)
win4(c, 11, 18)
put(c, ["ccccccccc", "csccsccsc"], 1, 23)                                               # awning
put(c, ["kkkkkkk", "kyyyyyk", "kbByBbk", "kkkkkkk", ".kbbBk."], 2, 25)                  # loaves in the window
door4(c, 11, 24)
put(c, ["....s.....",
        "...s......",
        "...kkk....",
        "...kTk....",
        "..kkkkkk..",
        ".kttttTTk.",
        "kttttttTTk",
        "kttkkkkTTk",
        "kttkfyfkTk",
        "kttkyyykTk",
        "kttkFFFkTk",
        "kkkkkkkkkk"], 18, 19)                                                         # domed bread oven
put(c, ["kkk", "kYk", ".b.", ".b.", ".b.", ".b.", ".b.", ".kk"], 28, 23)                  # peel
SPRITES["holding:Bakery"] = fin32(c)

# Meadery: cottage, straw skeps on a bench, mead barrel, bees
c = cv32()
wall(c, 0, 17, 15, 14, "w")
hline(c, 1, 13, 22, "b")
roof(c, 7, 10, 7)
win4(c, 2, 18)
door4(c, 9, 24)
put(c, ["y...y", "..y..y", "y...."], 17, 12)
for x0 in (16, 22):
    put(c, SKEP8, x0, 17)
put(c, ["kkkkkkkkkkkkk", "kbbbbbbbbbbBk", "kkkkkkkkkkkkk", ".kb.......kb.", ".kb.......kb.", ".kb.......kb."], 15, 25)
put(c, BARREL8, 26, 23)
SPRITES["holding:Meadery"] = fin32(c)

# Winery: stone cellar house, arched door, vine and grapes over the eave, barrels racked two-and-one
c = cv32()
wall(c, 0, 17, 17, 14, "t")
courses(c, 1, 19, 13, 29)
roof(c, 8, 9, 8)
put(c, ["lLlaAlLlLaAlL", "l.aA.Ll..aAl.", "...A.......A."], 2, 17)                        # vine on the eave
put(c, ["..kkkk..", ".kddddk.", "kddddddk", "kddddddk", "kddddddk", "kddddddk", "kddddddk", "kddddddk"], 2, 23)
win4(c, 11, 21)
put(c, BARREL8, 18, 23)
put(c, BARREL8, 25, 23)
put(c, ["kkkkkkkkkkkkk", "kbbbbbbbbbbBk", "kkkkkkkkkkkkk"], 18, 20)                          # rack
put(c, BARREL8, 21, 12)
for x in (18, 30):
    vline(c, x, 23, 30, "k")
SPRITES["holding:Winery"] = fin32(c)

# Cidery: cottage, twin-screw cider press over a tub of apples, basket, barrel
c = cv32()
wall(c, 0, 17, 15, 14, "w")
hline(c, 1, 13, 22, "b")
roof(c, 7, 10, 7)
win4(c, 2, 18)
door4(c, 9, 24)
put(c, ["kkkkkkkkkkkk",
        "kbbbbbbbbbBk",
        "kkkmkkkkmkkk",
        ".kbmb..bmbk.",
        ".kbmb..bmbk.",
        ".kbmkkkkmbk.",
        ".kbkbbbbkbk.",
        ".kbkkkkkkbk.",
        ".kbkcCcCkbk.",
        ".kbkBbBbkbk.",
        ".kbkbBbBkbk.",
        ".kbkkkkkkbk.",
        "kkkkkkkkkkkk"], 15, 18)                                                       # screw press
put(c, [".c.c.", "kcCcC", "kbBbB"[:5] + "k", ".kkk."], 27, 27)
SPRITES["holding:Cidery"] = fin32(c)

# Mill: tapering stone tower windmill, cap, four cloth sails on spars, door, flour sacks
c = cv32()
for i, y in enumerate(range(12, 31)):
    w = 9 + (i // 5) * 2
    x0 = 16 - w // 2
    for x in range(x0, x0 + w):
        c[y][x] = "k" if x in (x0, x0 + w - 1) or y == 30 else ("T" if x >= x0 + w - 3 else "t")
courses(c, 13, 14, 19, 29)
put(c, ["...kkkkkkk...", "..krrrrrrRRk.", ".krrrrrrrrRRk", "KKKKKKKKKKKKK"], 10, 8)        # cap
win4(c, 14, 15)
put(c, [".kkkk.", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk"], 13, 24)
MSAIL = ["kkk........",
         "kssk.......",
         "kssbk......",
         ".kssbk.....",
         "..kssbk....",
         "...kssbk...",
         "....kssbk..",
         ".....kssbk.",
         "......kkbBk"]
for fx in (False, True):
    for fy in (False, True):
        rows = MSAIL[::-1] if fy else MSAIL
        rows = [r[::-1] for r in rows] if fx else rows
        put(c, rows, 17 if fx else 4, 10 if fy else 0)
put(c, [".kkk.", "kbbBk", "kbmBk", "kbbBk", ".kkk."], 14, 7)                              # hub
put(c, [".kk.", "kZZk", "kssk", "ksZk", "kkkk"], 23, 26)                                  # flour sacks
put(c, [".kk.", "kZZk", "kssk", "ksZk", "kkkk"], 27, 26)
SPRITES["holding:Mill"] = fin32(c)


# ================================================================ BATCH 7: secrecy
# Cunning (Ithiss): nothing announced. Shutters over windows, one light at most, low doors, dark stone at Established;
# the Pestilence run (Cellar -> Catacombs -> Toxicarium -> Charnel House -> Plague Pit) sinks toward rot and bone.
LAMPPOST = [".kkk.", "kyyyk", ".kkk.", "..k..", "..k..", "..k..", "..k..", "..k..", "..k..", ".kkk."]
SKULL = [".kkk.", "ksssk", "kdsdk", ".sss.", ".kdk."]
SKULL7 = [".kkkkk.", "ksssssZ", "kdksdkZ", "ksssssZ", ".kZsZk.", ".ksksk.", "..kkk.."]
SHUT = ["kkkk", "kbBk", "kbBk", "kkkk"]                               # shuttered window


# group: shuttered dark house, one lit slit, lantern post
c = cv32()
wall(c, 0, 17, 19, 14, "u")
roof(c, 9, 8, 9, "u")
for o in (2, 13):
    put(c, SHUT, o, 19)
put(c, ["kkk", "kdk", "kkk"], 8, 12)
put(c, [".kkk.", "kdddk", "kdddk", "kdddk", "kdydk", "kdddk", "kdddk"], 7, 24)
put(c, LAMPPOST[:3] + ["..k.."] * 13 + [".kkk."], 23, 14)
SPRITES["group:g_secrecy"] = fin32(c)

# Toll House: plastered tower-house over the road, striped toll boom, iron-bound strongbox
c = cv32()
roof(c, 6, 1, 6)
wall(c, 0, 7, 13, 24, "w")
for y in (12, 18):
    hline(c, 1, 11, y, "b")
win4(c, 4, 8)
put(c, SHUT, 4, 14)
door4(c, 4, 24)
put(c, ["k" * 19, "k" + "".join("c" if (i // 3) % 2 else "s" for i in range(17)) + "k", "k" * 19], 13, 17)
put(c, ["kk", "kb", "kb", "kb", "kb", "kb", "kb", "kb", "kb", "kk"], 13, 20)
put(c, ["kk", "kb", "kB", "kB", "kB", "kB", "kB", "kB", "kB", "kk"], 29, 21)
put(c, ["kkkkkkk", "kbbybBk", "kmmmmMk", "kbbbbBk", "kbbbbBk", "kkkkkkk"], 18, 25)
SPRITES["holding:Toll House"] = fin32(c)

# Secret Cellar: shuttered cottage; cellar bulkhead doors flung open on steps going down; lantern on the door
c = cv32()
wall(c, 0, 17, 17, 14, "w")
hline(c, 1, 15, 22, "b")
roof(c, 8, 9, 8)
put(c, SHUT, 2, 18)
door4(c, 11, 24)
put(c, [".kk..........",
        "kbbk.........",
        "kbBbk........",
        "kbbBbk.......",
        ".kbbBbk......",
        "..kbbBbk.....",
        "..kkkkkkkkkkk",
        "..kddddddddUk",
        "..kdkkkkdddUk",
        "..kddkkkkddUk",
        "..kdddkkkkdUk",
        "..kddddkkkkkk",
        "kkkkkkkkkkkkk"], 17, 18)
put(c, ["k", "y", "Y"], 27, 21)
SPRITES["holding:Secret Cellar"] = fin32(c)

# Dark Scriptorium: low dark-stone cell with a shuttered window and one candle-lit slit; hooded scribe at a lectern
c = cv32()
wall(c, 0, 15, 19, 16, "u")
courses(c, 1, 17, 16, 29)
roof(c, 9, 7, 9, "u")
put(c, SHUT, 2, 19)
put(c, ["kk", "ky", "ky", "kk"], 9, 19)
door4(c, 13, 24, 6)
put(c, ["..kkk..", ".kdddk.", "kdhdddk", "kddddAk", "kaaaaAk", "kaaaaAk", "kaaaaAk", "kaaaaAk", "kkkkkkk"], 19, 22)
put(c, ["kkkkkk", "ksssZk", "kkkkkk", "..kb..", "..kb..", "..kb..", ".kkkk."], 25, 22)
put(c, ["y", "s", "s"], 30, 19)
put(c, [".cc.", "cyyC", ".CC."], 26, 19)
SPRITES["holding:Dark Scriptorium"] = fin32(c)

# Smuggler's Nook: sea cave under a dark cliff, one lantern in its mouth, rowboat of contraband at the landing
c = cv32()
water(c, 26)
put(c, ["........kkkkkkk.................",
        "......kkuuuuuuukk...............",
        "....kkuuuuuuuuuuukk.............",
        "...kuuuuuuuuuuuuuuuk............",
        "..kuuuuukkkkkkuuuuuUk...........",
        ".kuuuukkddddddkkuuuuUk..........",
        ".kuuukdddddddddkuuuuUUk.........",
        "kuuukdddddddddddkuuuuUUk........",
        "kuuukddddyddddddkuuuuuUUk.......",
        "kuukdddddYdddddddkuuuuuUUk......",
        "kuukddkkkkdddddddkuuuuuuUUk.....",
        "kuukdkbbbbkddddddkuuuuuuuUUk....",
        "kuukddddddddddddddkuuuuuuuUUk...",
        "kuukddddddddddddddkuuuuuuuuUUk..",
        "kuukddddddddddddddkuuuuuuuuuUUk.",
        "kuukddddddddddddddkuuuuuuuuuuUUk",
        "kuukddddddddddddddkuuuuuuuuuuuUk",
        "kuukddddddddddddddkuuuuuuuuuuuUk"], 0, 9)
put(c, ["...kkkkk.....", "...kbBcCk....", "k..kkkkkkk..k", "kbkbbbbbbbbkk", ".kbbbbbbbbBk.", "..kkkkkkkkk.."], 4, 22)
SPRITES["holding:Smuggler's Nook"] = fin32(c)

# Syndicate Hub: huddle of tall narrow dark houses, one lit window each, a covered bridge between
c = cv32()
for x0, top, w in ((0, 4, 9), (11, 10, 9), (21, 1, 11)):
    hw = (w - 1) // 2
    wall(c, x0, top + hw, w, 31 - top - hw, "u")
    roof(c, x0 + hw, top, hw, "u")
for x0, y0 in ((3, 12), (14, 17), (24, 11)):
    win4(c, x0, y0)
for x0, y0 in ((3, 19), (24, 18), (14, 23)):
    put(c, SHUT, x0, y0)
put(c, ["k" * 14, "kbBbBbBbBbBbBk", "k" * 14], 7, 14)
for x0 in (2, 24):
    door4(c, x0 + 1, 25)
SPRITES["holding:Syndicate Hub"] = fin32(c)

# Black Market: dark-curtained canopy, hooded dealer behind a board of contraband, one lantern
c = cv32()
put(c, ["k" * 32,
        "k" + "a" * 26 + "AAAA" + "k",
        "k" + "A" * 30 + "k",
        "".join("k" if i % 2 == 0 else "A" for i in range(32)),
        ".b" + "." * 28 + "B."], 0, 9)
for y in range(14, 31):
    c[y][1] = "b"
    c[y][30] = "B"
put(c, ["k", "y", "Y"], 26, 13)
put(c, ["..kkkk..", ".kddddk.", ".kdhhdk.", "kddddddk", "kddddddk", "kddddddk", "kddddddk"], 12, 14)
put(c, ["k" * 26, "kycmMkyakcmMkaymkcayYkmMyk", "k" * 26, "k" + "d" * 24 + "k", "k" + "d" * 24 + "k", "k" + "d" * 24 + "k", "k" + "d" * 24 + "k", "k" * 26], 3, 21)
put(c, [".kk.", "kssk", "kZZk", "kkkk"], 27, 27)
SPRITES["holding:Black Market"] = fin32(c)

# Forgery Workshop: shuttered stone scriptorium, screw press with fresh sheets, wax seal on the bench
c = cv32()
wall(c, 0, 17, 17, 14, "t")
roof(c, 8, 9, 8)
courses(c, 1, 19, 14, 29)
put(c, ["kkkkk", "kssZk", "kssZk", "kkkkk"], 2, 19)
put(c, SHUT, 11, 19)
door4(c, 6, 24)
put(c, ["kkkkkkkkk",
        "kbbbbbbBk",
        "kkk.m.kkk",
        "kbk.m.kBk",
        "kbkkkkkBk",
        "kbkssZkBk",
        "kbkkkkkBk",
        "kbk...kBk",
        "kbk...kBk",
        "kbk...kBk",
        "kbk...kBk",
        "kbk...kBk",
        "kkk...kkk"], 17, 18)
put(c, [".cc.", "cyyC", ".CC.", "kkkk", "kbBk", "kbBk", "kbBk", "kkkk"], 27, 23)
SPRITES["holding:Forgery Workshop"] = fin32(c)

# Toxicarium: blue-glazed poison house on a dark stone base, beds of poison plants, skull sign
c = cv32()
for i in range(10):
    for x in range(14 - i, 15 + i):
        edge = x in (14 - i, 14 + i)
        c[5 + i][x] = "k" if edge or (x - 14) % 3 == 0 and i % 2 == 0 else ("E" if x > 14 else "e")
hline(c, 4, 24, 14, "K")
wall(c, 4, 15, 21, 8, "e")
for x in (7, 11, 15, 19, 23):
    vline(c, x, 16, 21, "k")
for x0, a in ((5, "c"), (8, "a"), (12, "l"), (16, "c"), (20, "a")):
    put(c, [a + ".", "lL", ".L"], x0, 17)
wall(c, 2, 22, 25, 9, "u")
for x in range(4, 25, 4):
    c[25][x] = "U"
put(c, [".kkkk.", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk"], 12, 25)
put(c, SKULL7, 25, 12)
vline(c, 28, 19, 22, "k")
SPRITES["holding:Toxicarium"] = fin32(c)

# Charnel House: dark stone bone-house, skull over the low door, bones stacked against the wall
c = cv32()
wall(c, 0, 17, 21, 14, "u")
roof(c, 10, 7, 10, "u")
put(c, SKULL7, 7, 17)
put(c, [".kkkkk.", "kdddddk", "kdddddk", "kdddddk", "kdddddk", "kdddddk", "kdddddk"], 7, 24)
put(c, ["..k.k.k..",
        ".kskskskk",
        "kssssssZk",
        "kskskskZk",
        "kssssssZk",
        "kskskskZk",
        "kssssssZk",
        "kskskskZk",
        "kkkkkkkkk"], 21, 22)
put(c, SKULL, 23, 17)
SPRITES["holding:Charnel House"] = fin32(c)

# Plague Pit: open lime pit of bones, warning post with red cloth, body cart, crows
c = cv32()
put(c, ["k.k", ".k.", "....k.k", ".....k."], 12, 4)
put(c, ["kkkkkkk", "kccccCk", "kcccCCk", "kkkkkkk", "...b...", "...b...", "...b...", "...b...", "...b...", "...b...", "...b...", "...B...", "...B...", "..kBk.."], 0, 13)
put(c, ["....kkkkkkkkkkkkkk....",
        "..kkssksdsskssdskZkk..",
        ".kssksssdssksssssksZk.",
        "kssssksdsssskssdsssZZk",
        "kuuuuuuuuuuuuuuuuuuuUk",
        "kkkkkkkkkkkkkkkkkkkkkk"], 3, 25)
put(c, ["kk.........",
        "bbk........",
        ".kkkkkkkkkk",
        ".kssdsssZZk",
        ".kbbbbbbbBk",
        ".kkkkkkkkkk"], 19, 14)
put(c, WHEEL, 21, 19)
SPRITES["holding:Plague Pit"] = fin32(c)

# Beacon Towers: tall stone beacon tower with a fire basket, smaller relay tower, signal smoke
c = cv32()
put(c, ["..s.s...", ".s..s...", "..s.....", "..fyf...", ".fyyyf..", "kfyyyyfk", "kmmmmmMk", ".kmmmMk."], 5, 0)
cren(c, 4, 8, 11)
wall(c, 4, 10, 11, 21, "t")
courses(c, 5, 12, 11, 29)
put(c, SLIT, 9, 12)
win4(c, 7, 17)
door4(c, 7, 25)
put(c, [".f.", "fyf", "kmk", "kMk"], 22, 8)
cren(c, 19, 12, 9)
wall(c, 19, 14, 9, 17, "t")
courses(c, 20, 16, 25, 29)
put(c, SLIT, 23, 17)
SPRITES["holding:Beacon Towers"] = fin32(c)

# Forgotten Catacombs: mossy stone arch over a dark stair going down, rubble either side
c = cv32()
cx, cy = 15.5, 14
for y in range(4, 31):
    for x in range(32):
        dx, dy = x - cx, y - cy
        outer = (dy >= 0 and 4 <= x <= 27) or (dy < 0 and dx * dx + dy * dy <= 11.6 ** 2)
        inner = (dy >= 0 and 9 <= x <= 22) or (dy < 0 and dx * dx + dy * dy <= 6.6 ** 2)
        if inner:
            c[y][x] = "d"
        elif outer:
            c[y][x] = "u" if (x * 5 + y * 3) % 9 == 0 else ("T" if x > cx + 8 or (x > cx and dy < -6) else "t")
for y in range(4, 31):
    for x in range(32):
        if c[y][x] == "." and any(0 <= x + a < 32 and 0 <= y + b < 31 and c[y + b][x + a] in "tTud"
                                  for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            c[y][x] = "k"
    for x in range(32):
        if c[y][x] == "d" and any(0 <= x + a < 32 and c[y + b][x + a] in "tTu" for a, b in ((1, 0), (-1, 0), (0, -1))):
            c[y][x] = "k"
for y, x0, x1 in ((22, 12, 19), (25, 11, 20), (28, 10, 21)):
    hline(c, x0, x1, y, "U")
for (x, y) in ((25, 6), (26, 7), (27, 8), (27, 9), (28, 11), (26, 6), (24, 5), (27, 12), (28, 13)):
    c[y][x] = "l"
put(c, ["kk...", "tuk..", "tTuk."], 0, 28)
put(c, ["...kk", "..kuu", ".kuTu"], 27, 28)
SPRITES["holding:Forgotten Catacombs"] = fin32(c)

# Cipher Chamber: narrow crenellated stone tower, cipher wheel blazon, one lit study window, scroll rack
c = cv32()
cren(c, 7, 1, 13)
wall(c, 7, 3, 13, 28, "t")
courses(c, 8, 5, 16, 29)
disc(c, 13, 9, [(1, "k"), (2, "y"), (3.4, "Y")])
for dx, dy in ((0, -2), (0, 2), (-2, 0), (2, 0)):
    c[9 + dy][13 + dx] = "k"
win4(c, 11, 15)
put(c, SHUT, 11, 20)
door4(c, 11, 25)
put(c, ["kkkkkkkkk", "ksZksZksk", "kkkkkkkkk", "ksZksZksk", "kkkkkkkkk", "kbk...kBk", "kbk...kBk", "kbk...kBk", "kbk...kBk", "kkk...kkk"], 21, 21)
SPRITES["holding:Cipher Chamber"] = fin32(c)


# ================================================================ BATCH 8: works
# Industry (Trusteki): ordered, kept, built to outlast its makers. The Fortification line (Granary -> Supply Depot ->
# Citadel -> Castle Hall -> Imperial Palace) turns white stone and red roofs as it rises.
CRATE7 = ["kkkkkkk", "kbbbbBk", "kbkbkBk", "kbbkbBk", "kbkbkBk", "kBBBBBk", "kkkkkkk"]
SACK5 = [".kkk.", "kssZk", "kssZk", "kssZk", "kkkkk"]


def treadwheel(c, x, y):
    """Treadwheel crane 15 wide, top-left (x, y), 30 tall: jib with a hook and block, mast, big treadwheel."""
    put(c, ["k" * 15, "k" + "b" * 13 + "B", ".kbB.......m...", ".kbB.......m...", ".kbB......kuk..", ".kbB......kUk.."], x, y)
    for yy in range(y + 6, y + 30):
        c[yy][x + 1] = "k"
        c[yy][x + 2] = "b"
        c[yy][x + 3] = "B"
    disc(c, x + 6, y + 24, [(1, "k"), (3.5, "b"), (5.5, "B")])
    for dx, dy in ((0, -4), (0, 4), (-4, 0), (4, 0), (-3, -3), (3, -3), (-3, 3), (3, 3)):
        c[y + 24 + dy][x + 6 + dx] = "k"


# group: treadwheel crane beside a workshop
c = cv32()
treadwheel(c, 0, 1)
wall(c, 13, 17, 19, 14, "w")
for xx in (18, 26):
    vline(c, xx, 18, 29, "b")
roof(c, 22, 8, 9)
win4(c, 14, 19)
win4(c, 27, 19)
door4(c, 20, 24)
SPRITES["group:g_works"] = fin32(c)

# Masonry: rubble masons' lodge; half-built wall in a scaffold, dressed blocks and a mallet
c = cv32()
wall(c, 0, 19, 13, 12, "t")
roof(c, 6, 13, 6, "b")
for y in range(21, 30):
    for x in range(1, 11):
        if (x * 3 + y * 5) % 7 == 0:
            c[y][x] = "T"
win4(c, 2, 21)
door4(c, 7, 24)
put(c, ["b..........b...",
        "bbbbbbbbbbbbb..",
        "b..........b...",
        "b..........b...",
        "b.kkkkkkkk.b...",
        "b.kttTtttk.b...",
        "bbkkkkkkkkbb...",
        "b.ktttkttTkbk..",
        "b.kkkkkkkkkbk..",
        "b.kttTtttTkbk..",
        "b.kkkkkkkkkbkkk",
        "b.ktttkttTkbktT",
        "b.kkkkkkkkkbkkk"], 14, 18)
put(c, ["kkkkk", "ktttT", "kkkkk"], 27, 28)
put(c, [".kk", "kbbk", ".kb.", "..b."], 28, 24)
SPRITES["holding:Masonry"] = fin32(c)

# Workyard: tall A-frame crane with an iron mast, block and tackle; stacked timber
c = cv32()
put(c, ["kkkkk"], 21, 0)
vline(c, 23, 1, 14, "m")
for y in range(8, 15):
    c[y][22] = c[y][24] = "b"
put(c, ["kbbbbbbBk"], 19, 15)
for y, d in zip(range(16, 31), [3, 3, 3, 3, 4, 4, 4, 5, 5, 5, 6, 6, 6, 7, 7]):
    c[y][23 - d] = "b"
    c[y][23 + d] = "B"
put(c, [".kkkkkkkkkkkkk...",
        ".kybbbbbbbbbbBk..",
        "kkkkkkkkkkkkkkkk.",
        "kybbbbbbbbbbbbBk.",
        "kkkkkkkkkkkkkkkkk",
        "kYbbbbbbbbbbbbbBk",
        "kkkkkkkkkkkkkkkkk",
        "kybbbbbbbbbbbbbBk",
        "kkkkkkkkkkkkkkkkk"], 0, 22)
SPRITES["holding:Workyard"] = fin32(c)

# Storehouse: big warehouse, stone ground floor and timber loft, hoist over the loft door, braced doors, sacks and crates
c = cv32()
roof(c, 15, 1, 15)
put(c, ["kkkkk", "kdddk", "kdddk", "kkkkk"], 13, 7)
put(c, ["k" * 5, "....k", "....m", "....m", "...kUk"][:4], 15, 3)
wall(c, 0, 16, 31, 15, "b")
for xx in range(3, 29, 4):
    vline(c, xx, 18, 21, "B")
for y in range(22, 30):
    for x in range(1, 30):
        c[y][x] = "T" if x >= 28 else "t"
courses(c, 1, 24, 27, 29)
hline(c, 1, 29, 22, "k")
put(c, ["kkkkkkkkkkk", "kbkbbkbbkBk", "kbbkbkbkbBk", "kbbbkkbbbBk", "kbbkbkbkbBk", "kbkbbkbbkBk", "kkbbbkbbbkk", "kbbbbkbbbBk", "kkkkkkkkkkk"], 10, 22)
put(c, SACK5, 2, 26)
put(c, CRATE7, 23, 24)
SPRITES["holding:Storehouse"] = fin32(c)

# Census Hall: half-timbered civic hall, ledger board over the door, clerk's lit windows, scroll rolls
c = cv32()
wall(c, 0, 16, 25, 15, "w")
for xx in (6, 18):
    vline(c, xx, 17, 29, "b")
hline(c, 1, 23, 22, "b")
roof(c, 12, 4, 12)
put(c, ["k" * 11, "ksksksksksk", "ksZsZsZsZsk", "k" * 11], 7, 17)
for o in (1, 20):
    put(c, ["kkkk", "kyyk", "kyyk", "kyYk", "kkkk"], o, 17)
put(c, [".kkkk.", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk"], 9, 23)
put(c, [".kk..", "kssk.", "kssZk", "kkkkk", "kssZk", "kssZk", "kkkkk"], 26, 24)
SPRITES["holding:Census Hall"] = fin32(c)

# Granary: thatched granary raised on staddle stones, ladder, grain sacks
c = cv32()
roof(c, 13, 3, 12, "y")
wall(c, 2, 15, 23, 9, "b")
for x in (7, 12, 17, 21):
    vline(c, x, 17, 22, "B")
put(c, ["kkkkk", "kdddk", "kdddk", "kdddk", "kkkkk"], 11, 17)
hline(c, 1, 25, 24, "K")
for x0 in (3, 11, 19):
    put(c, ["ktTk", ".kk.", ".tT.", ".tT.", "kttT", "kkkk"], x0, 25)
for y in range(19, 31):
    c[y][26] = c[y][28] = "k"
    if y % 2 == 0:
        c[y][27] = "b"
put(c, [".kk", "ksZ", "ksZ", "kkk"], 29, 27)
SPRITES["holding:Granary"] = fin32(c)

# Supply Depot: canvas store tent, stacked crates, barrel, sacks
c = cv32()
for i in range(15):
    for x in range(9 - (i * 2) // 3, 10 + (i * 2) // 3):
        c[15 + i][x] = "s" if x <= 9 else "Z"
    c[15 + i][9 - (i * 2) // 3] = "k"
    c[15 + i][9 + (i * 2) // 3] = "k"
c[14][9] = "k"
for y in range(23, 30):
    for x in range(7, 12):
        if abs(x - 9) <= (y - 22) // 2:
            c[y][x] = "d"
hline(c, 0, 18, 30, "k")
put(c, CRATE7, 18, 17)
put(c, CRATE7, 18, 24)
put(c, CRATE7, 25, 24)
put(c, BARREL8, 25, 16)
put(c, SACK5, 13, 26)
SPRITES["holding:Supply Depot"] = fin32(c)

# Trade Guild: jettied half-timbered guildhall over a stone arcade, lit hall windows, guild banner
c = cv32()
wall(c, 0, 13, 27, 9, "w")
roof(c, 13, 0, 13)
for xx in (6, 13, 20):
    vline(c, xx, 14, 20, "b")
for o in (1, 8, 15, 22):
    win4(c, o, 15)
hline(c, 0, 26, 21, "K")
wall(c, 1, 22, 25, 9, "t")
for x0 in (3, 9, 15, 20):
    put(c, [".kk.", "kddk", "kddk", "kddk", "kddk", "kddk", "kddk"], x0, 24)
flag(c, 28, 8, "a", 23)
put(c, ["aay", "aAy", "aA."], 29, 10)
SPRITES["holding:Trade Guild"] = fin32(c)

# College of Engineering: stone hall with a great gear in the gable, model arch on a trestle
c = cv32()
wall(c, 0, 15, 21, 16, "t")
roof(c, 10, 5, 10)
courses(c, 1, 17, 18, 29)
disc(c, 10, 11.5, [(1, "k"), (2.4, "m")])
for dx, dy in ((0, -3), (0, 3), (-3, 0), (3, 0), (-2, -2), (2, -2), (-2, 2), (2, 2)):
    c[int(11.5 + dy)][10 + dx] = "m"
for o in (2, 15):
    put(c, ["kkkk", "kyyk", "kyyk", "kkkk", "kyYk", "kkkk"], o, 17)
put(c, [".kkkk.", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk"], 8, 23)
put(c, ["..kkkkkk..",
        ".kttttttTk",
        "kttkkkkkTTk"[:10],
        "ktk....kTk",
        "ktk....kTk",
        "kkkkkkkkkk",
        "kbbbbbbbBk",
        "kkkkkkkkkk",
        ".kb....kB.",
        ".kb....kB.",
        ".kb....kB.",
        ".kk....kk."], 21, 19)
SPRITES["holding:College of Engineering"] = fin32(c)

# Masons' Guild: dressed-stone guildhall under a slate roof, two floors of windows, hanging hammer sign
c = cv32()
put(c, [".s.", "s..", "kkk"] + ["kUk"] * 7, 5, 0)
wall(c, 0, 15, 23, 16, "t")
roof(c, 11, 4, 11, "u")
courses(c, 1, 17, 20, 29)
hline(c, 1, 21, 21, "T")
for o in (2, 9, 17):
    win4(c, o, 16)
for o in (2, 17):
    win4(c, o, 23)
put(c, [".kkkk.", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk"], 8, 23)
put(c, ["kkkkkk", ".....k", "....kbk", "...kkkkk", "...kmmMk", "...kkbkk", ".....b..", ".....B.."], 22, 15)
SPRITES["holding:Masons' Guild"] = fin32(c)

# Burgages: two narrow half-timbered plot houses, paired windows over a centred door, each with its garden strip
c = cv32()
for x0 in (0, 16):
    wall(c, x0, 17, 11, 14, "w")
    for xx in (x0 + 3, x0 + 7):
        vline(c, xx, 18, 22, "b")
    hline(c, x0 + 1, x0 + 9, 23, "b")
    roof(c, x0 + 5, 12, 5)
    win4(c, x0 + 1, 18)
    win4(c, x0 + 6, 18)
    door4(c, x0 + 4, 24)
    put(c, ["l.l.l", "lLlLl", "nlnLn", "lLlLL", "kkkkk"], x0 + 11, 26)
SPRITES["holding:Burgages"] = fin32(c)

# Citadel: white keep stepped in four tiers, red flag, dark windows and gate
c = cv32()
flag(c, 15, 0, "c", 4)
for (x0, x1, y0, y1) in ((11, 20, 4, 9), (7, 24, 10, 15), (3, 28, 16, 21), (0, 31, 22, 30)):
    hline(c, x0, x1, y0, "k")
    for y in range(y0 + 1, y1 + 1):
        for x in range(x0, x1 + 1):
            c[y][x] = "k" if x in (x0, x1) else ("Z" if x >= x1 - 2 or y == y0 + 1 else "s")
for (x, y) in ((14, 6), (17, 6), (10, 12), (21, 12), (6, 18), (25, 18), (3, 24), (8, 24), (23, 24), (28, 24)):
    put(c, ["k", "d", "d"], x, y)
put(c, [".kkkkkk.", "kddddddk", "kddddddk", "kddddddk", "kddddddk", "kddddddk", "kddddddk"], 12, 24)
SPRITES["holding:Citadel"] = fin32(c)

# Castle Hall: white great hall and stair tower under red roofs, red banner
c = cv32()
wall(c, 0, 17, 21, 14, "s")
roof(c, 10, 7, 10)
for o in (2, 15):
    put(c, ["kkkk", "kyyk", "kyyk", "kkkk", "kyYk", "kkkk"], o, 19)
put(c, [".kkkk.", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk"], 8, 23)
flag(c, 26, 0, "c", 6)
spire(c, 26, 3, 7, "r")
wall(c, 21, 9, 10, 22, "s")
for y0 in (12, 18):
    put(c, SLIT, 25, y0)
door4(c, 24, 24)
SPRITES["holding:Castle Hall"] = fin32(c)


# ================================================================ BATCH 9: raw materials, feet strips, scenery
# Raw materials are the bottom rung of every line: the trade itself in the open, earth and plank, no masonry.
def mound(c, x, y, w, h, fill="t", spot="u"):
    """Rounded rock / earth mound w wide, h tall, base on row y+h-1; right third in shade when fill has one."""
    for j in range(h):
        inset = int(round((1 - ((j + 1) / h) ** 0.5) * (w / 2)))
        x0, x1 = x + inset, x + w - 1 - inset
        for xx in range(x0, x1 + 1):
            ch = spot if (xx * 7 + j * 3) % 11 == 0 else fill
            if xx > x + w * 2 // 3 and ch in SHADE:
                ch = SHADE[ch]
            c[y + j][xx] = "k" if xx in (x0, x1) or j == 0 else ch


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


def pine32(c, x, y, h=24):
    """Tiered evergreen 15 wide, h tall, tip at (x+7, y), lit from the left; 3-row trunk."""
    c[y][x + 7] = "k"
    for j in range(1, h - 3):
        p = (j - 1) % 5
        hw = max(1, min(7, 1 + int(6 * j / (h - 4)) - (2 if p == 0 and j > 1 else 0)))
        for xx in range(x + 7 - hw, x + 8 + hw):
            if 0 <= xx < len(c[0]):
                edge = xx in (x + 7 - hw, x + 7 + hw) or p == 4 and abs(xx - x - 7) > hw - 2
                c[y + j][xx] = "k" if edge else ("N" if xx > x + 7 + hw // 3 else "n")
    for j in range(h - 3, h):
        put(c, ["kbBk"], x + 6, y + j)



# group: timbered adit in a rock mound
c = cv32()
mound(c, 0, 10, 32, 21)
put(c, ["kkkkkkkkkkk", "kbbbbbbbbBk", "kbkkkkkkkBk", "kbkdddddkBk", "kbkdddddkBk", "kbkdddddkBk", "kbkdddddkBk", "kbkdddddkBk", "kbkdddddkBk", "kkkdddddkkk"], 10, 21)
SPRITES["group:g_raw"] = fin32(c)

# Quarry: terraced rock face, dressed blocks, shear-legs hoisting a stone
c = cv32()
put(c, ["kkkkkkkkkkkkk...................",
        "kttuttttuttTk...................",
        "ktttttutttTTkkkkkk..............",
        "kttuttttkkkkttuttTk.............",
        "kttttutkttttttttTTk.............",
        "ktttttkktttuttttTTkkkkk.........",
        "kttuttktttttkkkkkkttTTk.........",
        "ktttttkttttktttuttttTTk.........",
        "kttttkkttttkttttuttTTTk.........",
        "ktttttkttttktttttttTTTk.........",
        "kkkkkkkkkkkkkkkkkkkkkkk........."], 0, 12)
put(c, ["kkkkk.kkkkk", "ktttT.ktutT", "kkkkkkkkkkk", "ktttTktuttT", "ktttTktttTT", "kkkkkkkkkkk"], 0, 25)
put(c, ["kkkk", "kttT", "kkkk"], 13, 28)
put(c, ["....k....", "...k.k...", "...kmk...", "..k.m.k..", "..k.m.k..", "..kkkkk..", "..ktttT..", "..kTTTT..", "..kkkkk..", ".k.....k.", ".k.....k.", "k.......k", "k.......k", "k.......k", "k.......k"], 21, 16)
SPRITES["holding:Quarry"] = fin32(c)

# Salt Works: boiling house with smoke, brine pans, white salt heaps
c = cv32()
put(c, [".s.", "s..", ".s.", "kkk", "kTk", "kTk", "kTk"], 22, 4)
wall(c, 12, 17, 17, 8, "w")
roof(c, 20, 9, 8)
win4(c, 13, 18)
put(c, [".kkkk.", "kfyyfk", "kffFFk"], 20, 19)
put(c, ["...k.......", "..ksk......", ".kssZk.....", "kssssZk....", "ksssssZk...", "ksssssZZk.."], 0, 19)
put(c, ["k" * 32,
        "keesekeeeeskeeeseeekesekeeeseeek",
        "k" * 32,
        "kuuuuuuuuuuuuuuuuuuuuuuuuuuuuUUk",
        "k" * 32], 0, 25)
SPRITES["holding:Salt Works"] = fin32(c)

# Apiary: three box hives on a stand, bees, flowering meadow
c = cv32()
put(c, ["y...y......y.....y...", "..a.....y.....y....y."], 4, 6)
for x0 in (1, 11, 21):
    put(c, ["..kkkkkk..",
            ".krrrrrRk.",
            "krrrrrrRRk",
            "KKKKKKKKKK",
            ".kbbbbbBk.",
            ".kbkkkbBk.",
            ".kbbbbbBk.",
            ".kBBBBBBk.",
            ".kbbbbbBk.",
            ".kbbkbbBk.",
            ".kkkkkkkk."], x0, 13)
put(c, ["k" * 32,
        ".kbB......kbB......kbB.....kbB.",
        ".kbB......kbB......kbB.....kbB.",
        ".kbB......kbB......kbB.....kbB."], 0, 24)
for x in range(32):
    c[28][x] = "l" if x % 4 else ("a" if x % 8 else "y")
    c[29][x] = "L" if x % 3 else "l"
    c[30][x] = "L"
for x in (2, 9, 15, 22, 29):
    c[27][x] = "c" if x % 2 else "y"
    c[28][x] = "l"
SPRITES["holding:Apiary"] = fin32(c)

# Peat Bog: reeds, stacked cut peat with a spade, bog water
c = cv32()
for x0 in (0, 4, 25, 29):
    put(c, ["l.", "l.", "lL", ".L", ".l", "lL", ".L", ".l", "lL"], x0, 15)
put(c, ["...kkkkkk...", "..kbbbbbBk..", ".kkkkkkkkkk.", "kbbbkbbbbkBk", "kkkkkkkkkkkk", "kbbbbbkbbbBk", "kbbkbbbbkbBk", "kkkkkkkkkkkk"], 9, 16)
put(c, ["k", "b", "b", "b", "b", "kk", "mM", "mM"], 21, 16)
put(c, ["k" * 32,
        "kddeddeddddeddddeddeddeddddeddek",
        "deeddeeddeeEdeeddeeddeEddeeddeed",
        "dEeddeEddeeddeEddeeddeeddEeddeed",
        "deedEeeddeeddeeddEeddeeddeeddEed"], 0, 24)
SPRITES["holding:Peat Bog"] = fin32(c)

# Forestry: two firs, forester's log pile, axe in a stump
c = cv32()
pine32(c, 0, 5, 26)
pine32(c, 16, 2, 29)
put(c, [".kk.kk.kk.", "kbYkbYkbYk", "kbbkbbkbbk", ".kk.kk.kk.", "kbYkbYkbYk", "kbbkbbkbbk", "kkkkkkkkkk"], 11, 24)
put(c, ["kk..", "mmk.", "kMbk", "..bk", "kkbbk", "kbbBk", "kkkkk"], 26, 24)
SPRITES["holding:Forestry"] = fin32(c)

# Fishmongery: quayside shop, fish strung under the eave, creel, water
c = cv32()
water(c, 27)
wall(c, 1, 14, 17, 10, "w")
hline(c, 2, 16, 18, "b")
roof(c, 9, 6, 8)
win4(c, 3, 15)
door4(c, 11, 17)
put(c, ["k" * 12, "k.k..k..k..k", "m.m..m..m..m", "e.e..e..e..e", "eEe.eEe.eEe.", "E.E..E..E..E"[:12], "s.s..s..s..s"], 18, 14)
put(c, ["k" * 32, "k" + "b" * 29 + "Bk", "k" + "B" * 30 + "k", ".kB.......kB.......kB.......kB."], 0, 24)
put(c, [".kkkkk.", "kbebeBk", "kbbbbBk", "kbkbkBk", "kkkkkkk"], 22, 19)
SPRITES["holding:Fishmongery"] = fin32(c)

# Furnace (was Mine art): ore hill with a timbered adit, rails, ore cart; a small bloomery glowing beside it
c = cv32()
mound(c, 0, 8, 21, 23, "u", "t")
put(c, ["kkkkkkkkkkk", "kbbbbbbbbBk", "kbkkkkkkkBk", "kbkdddddkBk", "kbkdddddkBk", "kbkdddddkBk",
        "kbkdddddkBk", "kbkdddddkBk", "kbkdddddkBk", "kkkdddddkkk"], 3, 20)
put(c, [".s..", "..s.", ".s..", "s...", "kkk.", "kTk.", "kTk.", "kTk."], 25, 11)
put(c, ["...kkk...", "..kttTk..", ".kttttTk.", ".kttttTk.", "kttttttTk", "kttttttTk", "kttkkkTTk", "ktkfyfkTk",
        "ktkyyykTk", "ktkyyykTk", "kkkkkkkkk"], 22, 18)
put(c, ["kkkkkkk", "kumyuUk", "kuuuuUk", "kkkkkkk", ".km.km."], 14, 24)
put(c, ["k" * 32], 0, 29)
put(c, ["".join("k" if x % 3 == 0 else "b" for x in range(32))], 0, 30)
SPRITES["holding:Furnace"] = fin32(c)

# Arable Land: ploughed strips with three wheat stooks
c = cv32()
for x0 in (1, 12, 23):
    put(c, ["....y....", "...yyY...", "...yyY...", "..yykYY..", "..yyyYY..", ".yykyYkY.", ".yyyyYYY.", "yykyyYkYY", "yyyyyYYYY", "ybykybkBY"], x0, 15)
for x in range(32):
    c[25][x] = "b"
    c[26][x] = "y" if x % 2 else "B"
    c[27][x] = "b"
    c[28][x] = "k" if x % 3 == 0 else "B"
    c[29][x] = "b"
    c[30][x] = "y" if x % 2 == 0 else "B"
SPRITES["holding:Arable Land"] = fin32(c)

# Common Land: grazing sheep, shepherd's hurdle fence, rough grass
c = cv32()
for x0, y0 in ((0, 19), (12, 22)):
    put(c, ["kk..........",
            "ksk..kkkkkk.",
            "kssksssssZk.",
            ".kssssssssZk",
            ".kssssssZZk.",
            "..kZZZZZZk..",
            "..kk...kk...",
            "..kk...kk..."], x0, y0)
fence32(c, 24, 31, 26)
for x in range(0, 32, 3):
    if c[30][x] == ".":
        c[30][x] = "l"
        c[29][x] = "l" if x % 2 else "."
SPRITES["holding:Common Land"] = fin32(c)


# ---------------------------------------------------------------- feet strips (38 wide; ground row skipped)
def strip(left, mid, right):
    """4-row terrain strip, 38 wide (overhangs a 32px holding by 3 a side): left and right clusters (up to 8 wide,
    right one right-aligned) and a middle unit repeated between them. Lit from the upper left like everything else."""
    rows = []
    for i in range(4):
        m = (mid[i] * 38)[:22]
        rows.append(left[i].ljust(8, ".")[:8] + m + right[i].rjust(8, ".")[-8:])
    return rows + ["g" * 38]


SPRITES["feet:Quarry"] = strip(["..kk....", ".kttk.kk", "kttTkktk", "kTTTkkTk"],
                               ["......", "......", "...k..", "..ktk."],
                               [".kk.....", "kttk.kk.", "kttTkttk", "kTTTkTTk"])
SPRITES["feet:Salt Works"] = strip(["..k.....", ".ksk....", "ksssk...", "kZZZk..."],
                                   [".......", ".......", "eeseeeE", "kkkkkkk"],
                                   [".....k..", "....ksk.", "...ksssk", "...kZZZk"])
SPRITES["feet:Apiary"] = strip(["", "", "", ""],
                               ["..y....", ".l.a..l", "lalLlyl", "LlLLlLL"],
                               ["", "", "", ""])
SPRITES["feet:Peat Bog"] = strip([".l.l....", ".lLl.kkk", "dlLdkbBk", "deedkkkk"],
                                 ["....", "....", "eedE", "deeE"],
                                 ["....l.l.", "kkk.lLl.", "kbBkdlLd", "kkkkdeed"])
SPRITES["feet:Forestry"] = strip(["..kkkk..", ".kbYbBk.", "kbYbYbBk", "kkkkkkkk"],
                                 ["...l.......", "..lLl......", "...b.......", "..kBk......"],
                                 ["..kkkk..", ".kbYbBk.", "kbYbYbBk", "kkkkkkkk"])
SPRITES["feet:Fishmongery"] = strip([".kk.....", "kmMk....", "kbBkeeee", "kkkkeeee"],
                                    [".........", ".........", "eeeeseeeE", "eEeeeeEee"],
                                    [".....kk.", "....kMmk", "eeeekBbk", "eeeekkkk"])
SPRITES["feet:Furnace"] = strip(["..tt....", ".tuUt...", "tuuyUt..", "kkkkkkkk"],
                                ["......", "......", "mmmmmm", "kbkbkb"],
                                ["....tt..", "...tuUt.", "..tuyuUt", "kkkkkkkk"])
SPRITES["feet:Arable Land"] = strip(["y.y.y...", "yyyYY...", "bybYB...", "BBBBBbyb"],
                                    ["..", "..", "bB", "yB"],
                                    ["...y.y.y", "...yyYYY", "...bybYB", "ybBBBBBB"])
SPRITES["feet:Common Land"] = strip([".kkk....", "ksssk...", "ksZZk...", ".k.k...."],
                                    [".....", ".....", "..l..", ".lLl."],
                                    ["....kkk.", "...ksssk", "...kZZsk", "....k.k."])

# ---------------------------------------------------------------- scenery (front row, holding scale)
# tree: two firs in the gap between settlements
c = cv32()
pine32(c, 3, 2, 29)
pine32(c, 14, 9, 22)
SPRITES["scenery:tree"] = fin32(c)

# plot: an open ward — survey stakes, a blank board on a post
c = cv32()
put(c, ["kkkkkkkkkkkk", "kbbbbbbbbbBk", "kbsssssssbBk", "kbsZZZZZsbBk", "kbbbbbbbbbBk", "kkkkkkkkkkkk", ".....kbk....", ".....kbk....", ".....kbk....", ".....kbk....", ".....kbk....", ".....kBk....", "....kkkkk..."], 10, 18)
for x in (2, 28):
    put(c, ["k", "b", "b", "B", "k"], x, 26)
hline(c, 3, 27, 27, "s")
SPRITES["scenery:plot"] = fin32(c)


# ================================================================ BATCH 10: settlement tiers (fallback), wonders
# tier:<name> — 32x32 fallback when a skyline piece is missing (same ladder: thatch -> plaster -> stone -> towers)
c = cv32()
wall(c, 1, 19, 15, 12, "w")
roof(c, 8, 11, 8, "y")
win4(c, 3, 21)
door4(c, 10, 24)
fence32(c, 17, 31, 27)
SPRITES["tier:Hamlet"] = fin32(c)

c = cv32()
wall(c, 0, 20, 13, 11, "w")
roof(c, 6, 14, 6)
win4(c, 1, 22)
door4(c, 8, 24)
wall(c, 14, 15, 17, 16, "w")
hline(c, 15, 29, 21, "b")
roof(c, 22, 7, 8)
win4(c, 16, 17)
win4(c, 25, 17)
door4(c, 20, 24)
SPRITES["tier:Village"] = fin32(c)

c = cv32()
for x0 in (0, 24):
    cren(c, x0, 3, 8)
    wall(c, x0, 5, 8, 26, "t")
    put(c, SLIT, x0 + 3, 8)
cren(c, 8, 12, 16)
wall(c, 8, 14, 16, 17, "t")
courses(c, 9, 16, 20, 29)
for o in (10, 18):
    win4(c, o, 16)
put(c, [".kkkk.", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk"], 13, 23)
SPRITES["tier:Town"] = fin32(c)

c = cv32()
flag(c, 15, 0, "c", 5)
for x0 in (0, 26):
    cren(c, x0, 3, 6)
    wall(c, x0, 5, 6, 26, "t")
wall(c, 6, 15, 20, 16, "t")
roof(c, 15, 5, 10)
courses(c, 7, 17, 22, 29)
for o in (8, 20):
    put(c, ["kkkk", "kyyk", "kyyk", "kkkk", "kyYk", "kkkk"], o, 17)
put(c, [".kkkk.", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk"], 13, 23)
SPRITES["tier:City"] = fin32(c)

c = cv32()
put(c, CROSS5, 13, 0)
spire(c, 15, 5, 9)
wall(c, 11, 13, 9, 18, "t")
put(c, ["kkkk", "kyyk", "kyYk", "kkkk"], 13, 15)
door4(c, 13, 24)
for x0 in (0, 20):
    disc(c, x0 + 6, 18, [(4.6, "y")])
    wall(c, x0, 18, 12, 13, "w")
    win4(c, x0 + 1, 20)
    win4(c, x0 + 7, 20)
    door4(c, x0 + 4, 25, 6)
SPRITES["tier:Metropolis"] = fin32(c)


# ================================================================ BATCH 10b: monuments and wonders (48)
# The top rung of each line. Flavour from the culture of the Standing combination that unlocks it
# (worldbuilding/renown_worldlore.py CULTURES): Prowess+Industry = Drakteni firepower, Piety+Industry = Madekite
# masons, Piety+Prowess = Belvareth gothic, Piety+Cunning / Cunning+Piety = Shassolin rot and the Order of Balance,
# Cunning+Industry = Prezish counting-house, Cunning+Prowess = Vorghith raiders and gallows; single-Standing
# monuments take their pure culture (Kraghs, Trusteki, Lenavorites, Ithiss).
def cv48():
    return cv(S48, S48 - 1)


HORSE = ["..kk..........",
         ".kbbk.........",
         "kbkbbk........",
         "kbbbbk........",
         "kbbbbbk.......",
         ".kkkbbbkkkkkk.",
         "....kbbbbbbbBk",
         "....kbcccbbbBk",
         "....kbbbbbbBBk",
         "....kbbbbbbBBk",
         "....kkbkkkkbkk",
         "....kbk...kbk.",
         "....kbk...kbk.",
         "....kbk...kbk.",
         "....kbk...kbk.",
         "....kBk...kBk.",
         "....kkk...kkk."]


def _pavilion(c, x, y, w, rh, wh, a, b, top="pennant"):
    """Striped pavilion w wide (odd), top-left (x, y): pennant or crown, cone roof rh rows, valance, walls wh rows, door."""
    cx = x + w // 2
    if top == "crown":
        put(c, ["y.y.y", "yyyyy", "kYYYk"], cx - 2, y + 2)
    else:
        vline(c, cx, y, y + 4, "k")
        put(c, [a * 3, a + SHADE[a] * 2], cx + 1, y)
    for i in range(rh):
        hw = round(i * (w // 2) / (rh - 1))
        for xx in range(cx - hw, cx + hw + 1):
            col = a if ((xx - cx) // 2) % 2 == 0 else b
            c[y + 5 + i][xx] = "k" if xx in (cx - hw, cx + hw) else (SHADE[col] if xx > cx + 1 else col)
    yv = y + 5 + rh
    hline(c, x, x + w - 1, yv - 1, "K")
    for xx in range(x + 1, x + w - 1):
        for j in range(yv, yv + wh):
            col = a if ((xx - cx) // 2) % 2 == 0 else b
            c[j][xx] = SHADE[col] if xx >= x + w - 3 else col
        c[yv][xx] = (a if xx % 2 else b) if (xx - x) % 2 else "K"
    vline(c, x + 1, yv, yv + wh - 1, "k")
    vline(c, x + w - 2, yv, yv + wh - 1, "k")
    dh = wh * 2 // 3
    for j in range(dh):
        for xx in range(cx - j // 3, cx + j // 3 + 1):
            c[yv + wh - dh + j][xx] = "d"


# Baggage Train (Prowess — Kraghs, the warband on the move): draught horse, covered wagon under a red war banner, barrels
c = cv48()
vline(c, 25, 3, 28, "k")
hline(c, 25, 34, 4, "k")
for j in range(5, 17):
    hline(c, 26, 33, j, "c")
    c[j][32] = c[j][33] = "C"
put(c, ["..y..", ".yyy.", "yyYyy", ".yYy."], 27, 8)
put(c, ["cc..cC", "c....C"], 26, 17)
_wagon(c, 14, 28)
put(c, HORSE, 0, 30)
put(c, BARREL8, 38, 31)
put(c, BARREL8, 37, 39)
put(c, BARREL8, 42, 39)
SPRITES["monument:Baggage Train"] = fin32(c)

# Royal Pavilion (Prowess — Kraghs, glory announced): great crowned pavilion between two striped tents, banners
c = cv48()
_pavilion(c, 0, 19, 13, 8, 15, "c", "s")
_pavilion(c, 35, 19, 13, 8, 15, "a", "s")
_pavilion(c, 12, 4, 25, 14, 24, "c", "y", top="crown")
SPRITES["monument:Royal Pavilion"] = fin32(c)

RIDER = ["...a...", "..kkk..", ".kmmMk.", ".kkkkk.", ".kmmMk.", "..kkk..", ".kccCk.", "kccyCCk", "kcyyyCk",
         "kccyCCk", ".kccCk.", "..kmk..", "..kmk.."]

# Marshal Tiltyard (was the Tiltyard art, grown into the capstone): royal stand under a striped canopy full of
# spectators, list posts with pennants, the long striped tilt barrier, and a caparisoned knight couching his lance
c = cv48()
flag(c, 2, 6, "c", 28)
flag(c, 17, 10, "a", 24)
stand = ["k" * 24,
         "k" + "ay" * 11 + "Ak",
         ".k" + "Ak" * 10 + "A.",
         "k" + "..h" * 7 + "..k",
         "k" + ".cC.aA" * 3 + ".cC.ak",
         "k" * 24,
         "k" + "cy" * 11 + "Ck",
         "k" * 24]
put(c, stand, 24, 10)
for y in range(18, 34):
    for x in (24, 31, 39, 47):
        c[y][x] = "k"
put(c, ["k" * 48,
        "".join("c" if (x // 3) % 2 else "s" for x in range(48)),
        "".join("C" if (x // 3) % 2 else "Z" for x in range(48)),
        "k" * 48] + ["".join("kb" if x % 8 == 1 else "." for x in range(48))[:48]] * 2
       + ["".join("kB" if x % 8 == 1 else "." for x in range(48))[:48]] * 3, 0, 33)
horse = [r.replace("c", "a") for r in HORSE]
for j in range(6, 10):
    horse[j] = horse[j][:5] + horse[j][5:12].replace("b", "a").replace("B", "A") + horse[j][12:]
horse[10] = horse[10][:5] + "kyyyyy" + horse[10][11:]
put(c, horse, 25, 30)
put(c, RIDER, 31, 21)
put(c, ["k" * 24 + "kk", "m" + "ycyc" * 6 + "kk", "k" * 24 + "kk"], 7, 27)                    # couched lance
SPRITES["monument:Marshal Tiltyard"] = fin32(c)

# Polish House (Sovereign Industry — Trusteki, kept and built to outlast): tall stone guildhall under a gilded roof,
# three arched display windows set with gems, gem sign on a bracket, smoking stack, polishing wheel at the door
c = cv48()
put(c, [".s..", "..s.", ".s..", "s...", ".s.."], 38, 0)
wall(c, 35, 9, 7, 38, "t")
courses(c, 36, 11, 39, 45)
cren(c, 35, 7, 7)
put(c, ["kkkk", "kyyk", "kyYk", "kkkk"], 37, 14)
put(c, ["kkkk", "kyyk", "kyYk", "kkkk"], 37, 24)
wall(c, 2, 20, 34, 27, "t")
courses(c, 3, 22, 33, 45)
roof(c, 18, 4, 16, "y")
disc(c, 18.5, 13, [(2.5, "a")])
for x0, gems in ((5, "ace"), (15, "lya"), (25, "ecl")):
    put(c, [".kkkk.", "kyyyyk", "k" + gems[0] + "yy" + gems[1] + "k", "kyyyyk", "ky" + gems[2] + "yYk", "kyyyYk", "kkkkkk"], x0 + 1, 24)
put(c, [".kkkk.", "kddddk"] + ["kddddk"] * 7, 16, 37)
disc(c, 44.5, 39.5, [(.6, "k"), (3, "m")])
put(c, [".kbk.", ".kbk.", "kbbBk", "kkkkk"], 42, 43)
put(c, ["y.s", ".y."], 44, 34)
SPRITES["monument:Polish House"] = fin32(c)

# Ordnance Yard (key: Artillery Park; Prowess + Industry — Drakteni, whose craft is conquest): hooped iron bombard
# with a flared, open muzzle on its timber bed, mortar, stacked shot, powder keg, red flag
c = cv48()
flag(c, 44, 6, "c", 41)
box(c, 1, 26, 6, 7, "m")                     # powder chamber
box(c, 6, 24, 22, 11, "m")                   # barrel
box(c, 27, 23, 5, 13, "m")                   # muzzle ring
hline(c, 7, 26, 25, "s")
for x0, x1 in ((2, 5), (7, 26), (28, 30)):
    hline(c, x0, x1, 32 if x0 == 2 else 33, "M")
    hline(c, x0, x1, 31 if x0 == 2 else 32, "M")
for x in (10, 15, 20, 25):
    vline(c, x, 23, 35, "K")                 # iron hoops, standing proud of the staves
for y in range(25, 34):
    c[y][28] = "m"
    c[y][29] = c[y][30] = "d"                # the bore
put(c, ["k" * 33, "k" + "b" * 29 + "BBk"[:2] + "k", "k" + "B" * 31 + "k", "k" * 33], 0, 35)
box(c, 3, 39, 5, 8, "b")
box(c, 22, 39, 5, 8, "b")
shade_rect(c, 6, 40, 6, 45)
shade_rect(c, 25, 40, 25, 45)
put(c, ["..kkkkk..", ".kmmmmMk.", "kmkkkkkMk", "kmmmmmMMk", ".kbbbbBk.", "kbbbbbbBk", "kkkkkkkkk"], 28, 40)
put(c, BARREL8, 35, 31)
for x0, y0 in ((37, 43), (40, 43), (43, 43), (45, 43), (38, 40), (41, 40), (44, 40), (40, 37), (43, 37)):
    put(c, [".k.", "kuU", ".k."], x0, y0)
SPRITES["monument:Artillery Park"] = fin32(c)

# Ministry of Military Strategy (Prowess — Kraghs, history as propaganda): stone hall carved with a victory frieze,
# red banners at the door, crenellated tower with a flag
c = cv48()
wall(c, 0, 22, 33, 25, "t")
roof(c, 16, 6, 16)
courses(c, 1, 31, 30, 45)
hline(c, 1, 31, 24, "k")
hline(c, 1, 31, 29, "k")
for x0 in range(2, 30, 4):
    put(c, [".T.", "TTT", ".T.", "T.T"], x0, 25)
for o in (3, 26):
    put(c, ["kkkk", "kyyk", "kyyk", "kyyk", "kkkk", "kyYk", "kyYk", "kkkk"], o, 31)
for x0 in (9, 22):
    put(c, ["kk", "cC", "cC", "cC", "yy", "cC", "cC", "cC", "c."], x0, 31)
put(c, ["..kkk..", ".kdddk.", "kdddddk", "kdddddk", "kdddddk", "kdddddk", "kdddddk", "kdddddk", "kdddddk", "kdddddk", "kdddddk", "kdddddk", "kdddddk"], 13, 34)
flag(c, 40, 0, "c", 6)
cren(c, 33, 6, 14)
wall(c, 33, 8, 14, 39, "t")
courses(c, 34, 10, 43, 45)
put(c, SLIT, 39, 11)
put(c, ["kkkk", "kyyk", "kyYk", "kkkk"], 38, 18)
put(c, SLIT, 39, 26)
door4(c, 38, 39, 8)
SPRITES["monument:Ministry of Military Strategy"] = fin32(c)

# Advanced Blast Furnace (Industry + Prowess — Drakteni, the arms of conquest): iron-banded furnace with a smoking
# stack and roaring tapping door, bellows beam driven by a waterwheel fed from a flume
c = cv48()
put(c, [".s..s", "s..s.", ".s...", "..s.."], 10, 0)
wall(c, 9, 4, 8, 11, "u")
for i, y in enumerate(range(14, 47)):
    hw = 7 + i * 4 // 32
    for x in range(13 - hw, 13 + hw + 1):
        c[y][x] = "k" if x in (13 - hw, 13 + hw) or y in (14, 46) else ("U" if x > 13 + hw - 3 else "u")
for y in (20, 30):
    hline(c, 13 - 7, 13 + 7, y, "m")
put(c, ["...kkkkk...", "..kfffffk..", ".kffyyyfFk.", "kffyyyyyfFk", "kfyyyyyyyFk", "kfyyyyyyyFk", "kfyyyyyyyFk", "kffyyyyyfFk", "kfffffffFFk", "kkkkkkkkkkk"], 8, 37)
hline(c, 28, 47, 23, "k")
hline(c, 28, 47, 24, "e")
hline(c, 28, 47, 25, "B")
hline(c, 28, 47, 26, "k")
for y in range(27, 47):
    c[y][46] = "b"
    c[y][45] = "k"
put(c, ["e", "e", "E", "e"], 30, 27)
disc(c, 36, 37, [(1.5, "m"), (5.5, "d"), (8.5, "b")])
for dx, dy in ((0, -6), (0, 6), (-6, 0), (6, 0), (-4, -4), (4, -4), (-4, 4), (4, 4), (0, -3), (0, 3), (-3, 0), (3, 0)):
    c[37 + dy][36 + dx] = "b"
line(c, 21, 27, 35, 36, "b", 2)
SPRITES["monument:Advanced Blast Furnace"] = fin32(c)

# Aristocratic Court (Industry + Cunning — Prezish, the counting-house cartel): palazzo with a gilded cornice, loggia
# arcade, balconied piano nobile, scales over the loggia; corner towers under blue roofs
c = cv48()
wall(c, 8, 15, 32, 32, "w")
hline(c, 8, 39, 15, "y")
hline(c, 8, 39, 16, "K")
for x0 in range(10, 38, 5):
    put(c, ["kkk", "kyk", "kkk"], x0, 18)
for x0 in range(10, 38, 5):
    put(c, ["kkk", "kyk", "kyk", "kYk", "kkk"], x0, 23)
hline(c, 9, 38, 28, "y")
hline(c, 9, 38, 29, "Y")
put(c, [".kkkk.", "kyyyYk", ".kYYk.", "y.kk.y", "yk..ky"], 21, 30)
hline(c, 9, 38, 35, "k")
for x0 in range(9, 37, 6):
    put(c, [".kkkk.", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk"], x0, 36)
for x0 in (0, 38):
    flag(c, x0 + 4, 0, "a", 4)
    spire(c, x0 + 4, 3, 9, "e")
    wall(c, x0, 11, 10, 36, "w")
    for y0 in (14, 22, 30):
        put(c, ["kkkk", "kyyk", "kyYk", "kkkk"], x0 + 3, y0)
    door4(c, x0 + 3, 40)
SPRITES["monument:Aristocratic Court"] = fin32(c)

# Port Authority (Industry — Trusteki, the ordered harbour): striped lighthouse, harbourmaster's hall under a blue roof
# with an anchor, stone quay with bollards, a cog alongside
c = cv48()
water(c, 41)
put(c, ["k" * 33, "k" + "t" * 29 + "TTk", "k" + "".join("T" if x % 5 == 2 else "t" for x in range(29)) + "TTk", "k" + "t" * 29 + "TTk", "k" * 33], 0, 36)
put(c, [".kk.", "kmmk", "kmMk", "kkkk"], 32, 32)
put(c, [".s.", "fyf", "kyk", "kkk"], 3, 0)
for i, y in enumerate(range(4, 36)):
    hw = 2 + i // 10
    for x in range(4 - hw, 5 + hw):
        band = "c" if (y // 5) % 2 else "w"
        c[y][x] = "k" if x in (4 - hw, 4 + hw) or y == 4 else (SHADE[band] if x > 4 + hw - 2 else band)
wall(c, 10, 21, 23, 15, "w")
roof(c, 21, 10, 11, "e")
for o in (12, 27):
    win4(c, o, 23)
put(c, ["..kk..", ".kmMk.", "..kk..", "kkmMkk", "..mM..", "k.mM.k", "kmmMMk", ".kkkk."], 18, 13)
put(c, [".kkkk.", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk"], 18, 29)
vline(c, 40, 9, 37, "k")
put(c, ["kkkkkkkk", "keeeeeEk", "ksssssZk", "keeeeeEk", "ksssssZk", "keeeeeEk", "kkkkkkkk"], 36, 13)
put(c, ["c", "cC", "c"], 41, 9)
put(c, ["kk..........kk", "kbkkkkkkkkkkbk", "kbbbbbbbbbbbBk", ".kbbkbbkbbkBk.", "..kbbbbbbbBk..", "...kkkkkkkk..."], 33, 37)
SPRITES["monument:Port Authority"] = fin32(c)

# Manor House (Industry — Trusteki, legacy and lineage): half-timbered hall and two wings under blue roofs, chimneys,
# the founder's statue on an inscribed plinth, clipped garden
c = cv48()
for x0, top in ((0, 18), (31, 18)):
    wall(c, x0, top + 7, 17, 16, "w")
    for xx in (x0 + 5, x0 + 11):
        vline(c, xx, top + 8, top + 21, "b")
    hline(c, x0 + 1, x0 + 15, top + 14, "b")
    roof(c, x0 + 8, top, 8, "e")
    win4(c, x0 + 1, top + 9)
    win4(c, x0 + 12, top + 9)
    win4(c, x0 + 6, top + 16)
put(c, [".s.", "s..", "kkk"] + ["kTk"] * 8, 8, 9)
put(c, [".s.", "..s", "kkk"] + ["kTk"] * 8, 38, 9)
wall(c, 14, 20, 21, 21, "w")
for xx in (19, 29):
    vline(c, xx, 21, 39, "b")
hline(c, 15, 33, 28, "b")
roof(c, 24, 9, 10, "e")
for o in (15, 30):
    win4(c, o, 22)
put(c, ["kkkkkk", "kyyyYk", "kyyyYk", "kkkkkk"], 21, 22)
put(c, [".kkkkk.", "kdddddk", "kdddddk", "kdddddk", "kdddddk", "kdddddk", "kdddddk", "kdddddk", "kdddddk", "kdddddk"], 21, 31)
put(c, [".ks.", "ksZk", ".sZ.", "ksZZ", ".sZ.", ".s.Z", "kkkkk", "ktttT", "kkkkk", "ktttT", "ktttT", "kkkkk"], 2, 35)
for x in range(48):
    c[41][x] = "k"
    for y in range(42, 47):
        c[y][x] = "s" if 20 <= x <= 28 else ("n" if (x // 2 + y) % 2 else "N")
SPRITES["monument:Manor House"] = fin32(c)

# Office of Works (Industry + Piety — Madekite masons, labour as devotion, chasing the lost Great Basilica): a cathedral
# front half raised — finished tower and spire, rose window, the other tower still in scaffold — with a treadwheel crane
c = cv48()
treadwheel(c, 0, 16)
put(c, ["kkkk", "kttT", "kkkk"], 4, 43)
steeple(c, 41, 0, 9)
wall(c, 36, 14, 11, 33, "t")
courses(c, 37, 16, 43, 45)
put(c, SLIT, 41, 18)
put(c, ["kkkk", "kyyk", "kyYk", "kkkk"], 40, 26)
wall(c, 18, 22, 19, 25, "t")
courses(c, 19, 24, 33, 45)
for i in range(6):
    hline(c, 27 - i * 2, 27 + i * 2, 16 + i, "t")
    c[16 + i][27 - i * 2] = c[16 + i][27 + i * 2] = "k"
put(c, ["k.k.k.."], 21, 15)
disc(c, 27, 28, [(1, "y"), (2.4, "c"), (3.6, "a")])
put(c, ["..kkkkk..", ".kdddddk.", "kdddddddk", "kdddddddk", "kdddddddk", "kdddddddk", "kdddddddk", "kdddddddk", "kdddddddk", "kdddddddk", "kdddddddk"], 23, 36)
for y in range(20, 47):
    for x in range(13, 19):
        c[y][x] = "t" if (x + y) % 5 else "T"
    c[y][13] = "k"
for y in (20, 27, 34, 41):
    hline(c, 11, 20, y, "b")
for x in (11, 20):
    vline(c, x, 18, 46, "b")
put(c, ["k.kk.k", "kttktk"], 13, 18)
SPRITES["monument:Office of Works"] = fin32(c)

# Imperial Palace (Prowess + Industry — Drakteni; the white-and-red Fortification line crowned): white palace in three
# tiers under red roofs, gold crown, red hangings, flanking towers, guns on the terrace
c = cv48()
put(c, ["y.y.y", "yyyyy", "kYYYk"], 21, 3)
for (x0, x1, ry, y1) in ((14, 33, 6, 19), (8, 39, 18, 31), (2, 45, 30, 46)):
    for i in range(3):
        hline(c, x0 - 2 + i, x1 + 2 - i, ry + 2 - i, "r")
    hline(c, x0 - 2, x1 + 2, ry + 2, "R")
    hline(c, x0, x1, ry, "k")
    for y in range(ry + 3, y1 + 1):
        for x in range(x0, x1 + 1):
            c[y][x] = "k" if x in (x0, x1) else ("Z" if x >= x1 - 2 else "s")
    c[ry + 1][x0 - 1] = c[ry + 1][x1 + 1] = "k"
for x0 in (16, 22, 28):
    put(c, ["kkkk", "kddk", "kddk", "kkkk"], x0, 12)
for x0 in (11, 33):
    put(c, ["cC", "cC", "cC", "yy", "cC", "c."], x0, 22)
for x0 in (17, 28):
    put(c, ["kkkk", "kyyk", "kyYk", "kkkk"], x0, 23)
put(c, [".kkkkkk.", "kddddddk", "kddddddk", "kddddddk", "kddddddk", "kddddddk", "kddddddk", "kddddddk", "kddddddk", "kddddddk", "kddddddk", "kddddddk", "kddddddk"], 20, 34)
for x0 in (6, 37):
    put(c, ["kkkk", "kddk", "kddk", "kkkk"], x0, 36)
put(c, ["kkkkk", "mmmMk", "kkkkk"], 3, 32)
put(c, ["kkkkk", "kmmmM", "kkkkk"], 40, 32)
SPRITES["monument:Imperial Palace"] = fin32(c)

# Senate Hall (any Sovereign Standing — the technocratic Senate that sits with the Duke; Enlightenment): marble portico,
# pediment, colonnade, steps, lead dome with a gilt lantern behind
c = cv48()
put(c, [".k.", "kyk", "kyk", "kYk", "kkk"], 23, 3)
disc(c, 24, 17, [(9, "m")])
for i in range(7):
    for x in range(24 - 3 * i - 2, 24 + 3 * i + 3):
        c[18 + i][x] = "k" if x in (24 - 3 * i - 2, 24 + 3 * i + 2) or i == 6 else ("Z" if x > 24 + 3 * i - 2 else "s")
put(c, [".kyk.", "kyyYk", ".kYk."], 22, 20)
put(c, ["k" * 42, "k" + "s" * 38 + "ZZ" + "k"[:0] + "k", "k" * 42], 3, 25)
for y in range(28, 41):
    for x in range(4, 44):
        c[y][x] = "d"
for x0 in range(4, 44, 6):
    put(c, ["kkkk"] + ["ksZk"] * 11 + ["kkkk"], x0, 28)
for i, y in enumerate(range(41, 47)):
    x0, x1 = 2 - (i > 2), 45 + (i > 2)
    hline(c, x0, x1, y, "k" if i % 2 == 0 else "s")
    if i % 2:
        c[y][x0] = c[y][x1] = "k"
        for x in range(x1 - 3, x1):
            c[y][x] = "Z"
SPRITES["monument:Senate Hall"] = fin32(c)

# Studium Generale (four Established Standings — the Astravantheliad academic halls): clock tower under a purple spire
# between two hall wings, rows of lit study windows, one banner for each Domain
c = cv48()
spire(c, 23, 0, 9, "a")
wall(c, 18, 8, 11, 39, "t")
courses(c, 19, 10, 25, 45)
disc(c, 23, 14, [(.6, "k"), (3, "s")])
c[12][23] = c[13][23] = "k"
c[14][24] = c[14][25] = "k"
for y0 in (20, 27):
    put(c, ["kkkk", "kyyk", "kyyk", "kkkk"], 22, y0)
put(c, [".kkkk.", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk"], 20, 36)
for x0 in (0, 29):
    wall(c, x0, 20, 19, 27, "t")
    courses(c, x0 + 1, 22, x0 + 15, 45)
    roof(c, x0 + 9, 11, 9, "a")
    for o in (2, 7, 12):
        for y0 in (23, 31):
            put(c, ["kkkk", "kyyk", "kyYk", "kkkk"], x0 + o + (1 if o == 12 else 0), y0)
for x0, col in ((1, "c"), (14, "a"), (31, "y"), (44, "u")):
    put(c, ["kk", col + SHADE[col], col + SHADE[col], col + SHADE[col], col + SHADE[col], col + "."], x0, 37)
SPRITES["monument:Studium Generale"] = fin32(c)

# Papal Palace (Piety + Industry — the Madekite masons' cathedral craft, seat of the Order of Saints): gilded dome and
# lantern, pale nave front with a rose window, twin bell towers, buttresses, great doors
c = cv48()
put(c, CROSS5, 22, 0)
put(c, [".kkk.", "kyyYk", "kyyYk", "kkkkk"], 22, 5)
disc(c, 24, 17, [(8, "y")])
for x in range(17, 32, 3):
    vline(c, x, 11, 16, "Y")
wall(c, 11, 18, 27, 29, "w")
disc(c, 24, 26, [(1, "y"), (2.4, "c"), (3.8, "a")])
for o in (14, 31):
    put(c, ["kkkk", "kyyk", "kyyk", "kyyk", "kyYk", "kkkk"], o, 22)
put(c, ["...kkkk...", "..kddddk..", ".kddddddk.", "kddddddddk", "kddddddddk", "kddyddyddk", "kddddddddk", "kddddddddk", "kddddddddk", "kddddddddk", "kddddddddk", "kddddddddk", "kddddddddk"], 19, 34)
for x0 in (1, 37):
    put(c, ["..k..", ".kyk.", "kyyyk"], x0 + 3, 0)
    spire(c, x0 + 5, 3, 9, "y")
    wall(c, x0, 11, 11, 36, "w")
    put(c, ["kkkkk", "kdydk", "kdyYk", "kkkkk"], x0 + 3, 14)
    put(c, ["kkkk", "kyyk", "kyyk", "kyYk", "kkkk"], x0 + 4, 24)
    door4(c, x0 + 4, 38, 9)
for x0, s in ((11, 1), (36, -1)):
    for i in range(6):
        c[30 + i][x0 + s * (i // 2)] = "T"
SPRITES["monument:Papal Palace"] = fin32(c)

# Inquisitorial Palace (Piety + Cunning — the Order of Balance; mania in dry official form): dark gothic palace of five
# spires, the watching eye over a portcullis, barred lancets, red-sealed hangings
c = cv48()
for cx, top in ((6, 6), (15, 2), (24, 0), (33, 2), (41, 6)):
    spire(c, cx, top, 13, "u")
wall(c, 2, 16, 44, 31, "u")
for y in range(18, 45, 3):
    for x in range(3 + (y // 3) % 2 * 2, 44, 4):
        c[y][x] = "U"
for x0 in (5, 13, 31, 39):
    put(c, ["kkkk", "kmdk", "kdmk", "kmdk", "kdmk", "kmdk", "kkkk"], x0, 20)
disc(c, 24, 22, [(1.2, "k"), (2.6, "y"), (4.2, "s")])
for x0 in (10, 35):
    put(c, ["kk", "cC", "cC", "yy", "cC", "cC", "c."], x0, 29)
put(c, ["..kkkkkkk..", ".kmdmdmdmk.", "kmdmdmdmdmk", "kmmmmmmmmmk", "kmdmdmdmdmk", "kmdmdmdmdmk", "kmmmmmmmmmk", "kmdmdmdmdmk", "kmdmdmdmdmk", "kmmmmmmmmmk", "kmdmdmdmdmk", "kmdmdmdmdmk", "kkkkkkkkkkk"], 19, 34)
SPRITES["monument:Inquisitorial Palace"] = fin32(c)

# Sacred Preceptory (key: Preceptory of the Knight's Templar; Piety + Prowess — Belvareth, the Lost Woods crusader
# order of Wrath, devotion curdled): crenellated chapel-keep, black gothic spire, crimson cross banners, fire-lit
# lancets, dark firs crowding in
c = cv48()
pine32(c, 0, 14, 33)
pine32(c, 33, 12, 35)
spire(c, 24, 0, 15, "u")
cren(c, 9, 12, 30)
wall(c, 9, 14, 30, 33, "t")
courses(c, 10, 16, 35, 45)
wall(c, 19, 13, 11, 34, "t")
for o in (12, 33):
    put(c, ["kkkk", "kffk", "kfFk", "kfFk", "kfFk", "kkkk"], o, 18)
put(c, [".kk.", "kffk", "kfFk", "kffk", "kfFk", "kkkk"], 22, 17)
for x0 in (13, 33):
    put(c, ["kkk", "cCC", "csC", "sss", "csC", "cCC", "cC.", "c.."], x0, 27)
put(c, ["..kkkkk..", ".kdddddk.", "kdddddddk", "kdddddddk", "kdddddddk", "kdddddddk", "kdddddddk", "kdddddddk", "kdddddddk", "kdddddddk", "kdddddddk", "kdddddddk"], 20, 35)
SPRITES["monument:Preceptory of the Knight's Templar"] = fin32(c)

# Eternal Sepulchre (key: Exalted Basilica; Piety — the Lenavorite pilgrim road's end): white domed sepulchre on a green
# hill, gilt cross, glowing doorway, candles along the worn path, pilgrims climbing
c = cv48()
put(c, CROSS5, 22, 3)
disc(c, 24, 15, [(8, "s")])
wall(c, 14, 15, 21, 18, "s")
for x0 in (17, 29):
    put(c, ["kkk", "kyk", "kyk", "kYk", "kkk"], x0, 19)
put(c, ["..kkk..", ".kyyyk.", "kyyyyYk", "kyyyyYk", "kyyyyYk", "kyyyyYk", "kyyyYYk", "kkkkkkk"], 21, 25)
for y, x0, x1 in ((32, 10, 37), (33, 7, 40), (34, 5, 42), (35, 3, 44), (36, 2, 45), (37, 1, 46)) + tuple((y, 0, 47) for y in range(38, 47)):
    for x in range(x0, x1 + 1):
        c[y][x] = "n" if (x * 7 + y * 3) % 13 == 0 else ("L" if x > (x0 + x1) // 2 + 6 else "l")
    if y < 38:
        c[y][x0] = c[y][x1] = "k"
hline(c, 14, 34, 32, "k")
for (x, y) in ((24, 33), (25, 34), (25, 35), (24, 36), (23, 37), (23, 38), (24, 39), (25, 40), (26, 41), (26, 42), (25, 43), (25, 44), (26, 45), (26, 46)):
    c[y][x] = "s"
for (x, y) in ((20, 35), (29, 36), (19, 39), (30, 40), (21, 43), (31, 44)):
    c[y - 1][x] = "y"
    c[y][x] = "s"
for x0, y0 in ((6, 31), (36, 33)):
    put(c, ["..h..", ".kak.", "kaaAk", "kaaAk", ".a.A."], x0, y0)
    vline(c, x0 + 5, y0 - 2, y0 + 4, "b")
SPRITES["monument:Exalted Basilica"] = fin32(c)

# Ossuary Crypt (Cunning + Piety — Shassolin, the Last Prophet's curse: poisoned wells, rot, plague): dark crypt chapel
# faced with bone, skull roundel, stair down into the dark; a poisoned well; a dead tree; crows
c = cv48()
put(c, ["k.k", ".k.", "", "....k.k", ".....k."], 30, 2)
roof(c, 21, 8, 12, "u")
wall(c, 9, 20, 25, 27, "u")
for y in range(22, 30, 2):
    for x in range(10, 33):
        c[y][x] = "s" if (x + y // 2) % 3 == 0 else c[y][x]
disc(c, 21, 15, [(1, "d"), (2.6, "s")])
put(c, SKULL7, 18, 30)
put(c, ["..kkkkk..", ".kdddddk.", "kdddddddk", "kdUdddUdk", "kddUdUddk", "kdddUdddk", "kddddddddk"[:9], "kdddddddk", "kdddddddk"], 17, 38)
put(c, ["..b.b...", "...bb.b.", "b..b.bb.", ".b.bb...", "..bbb...", "...bB...", "...bB...", "...bB...", "...bB...", "...bB...", "...bB...", "...bB...", "...bB...", "...bB...", "...bB...", "...bB...", "..bbBB.."], 0, 30)
put(c, ["kkkkkkkkkk", ".kb....Bk.", ".kb....Bk.", ".kb.m..Bk.", ".kb.k..Bk.", "kkkkkkkkkk", "ktllLLlTTk", "ktttttTTTk", "ktuttTtuTk", "ktttTTTTTk", "kkkkkkkkkk"], 37, 36)
SPRITES["monument:Ossuary Crypt"] = fin32(c)

# Thieves' Guild (Cunning + Industry — Prezish brokers and fences): crooked dark townhouses, a plank walk across the
# roofs, one counting-room window glinting with coin, a cellar hatch with fenced crates, a key sign
c = cv48()
for x0, top, w in ((0, 12, 13), (12, 4, 15), (26, 16, 11), (36, 8, 12)):
    hw = (w - 1) // 2
    wall(c, x0, top + hw, w, 47 - top - hw, "u")
    roof(c, x0 + hw, top, hw, "u")
for x0, y0 in ((3, 24), (15, 30), (39, 22), (29, 30)):
    put(c, SHUT, x0, y0)
put(c, ["kkkkkk", "kyYyYk", "kYyYyk", "kkkkkk"], 16, 18)
put(c, ["k" * 14, "kbBbBbBbBbBbBk", "k" * 14], 26, 20)
for x0 in (4, 17, 40):
    door4(c, x0, 38, 9)
put(c, ["kkkkkk", "....k.", "...kyk", "...kYk", "....k.", "...kk."], 6, 14)
put(c, ["kkkkkkkkk", "kdddddddk", "kdkkkkkdk", "kkkkkkkkk"], 27, 43)
put(c, CRATE7, 30, 36)
SPRITES["monument:Thieves' Guild"] = fin32(c)

# Outlaw Rookery (Cunning — Ithiss, the anarchic haven): stilt huts in a dark wood linked by rope bridges, ladders,
# a fire below, a black skull flag
c = cv48()
pine32(c, 0, 10, 37)
pine32(c, 33, 6, 41)
for x0, top in ((4, 14), (18, 4), (32, 16)):
    roof(c, x0 + 6, top, 6, "u")
    wall(c, x0, top + 6, 13, 9, "b")
    put(c, SHUT, x0 + 2, top + 8)
    put(c, ["kkkk", "kdyk", "kddk", "kkkk"], x0 + 7, top + 8)
    for x in (x0 + 2, x0 + 10):
        vline(c, x, top + 15, 46, "b")
        vline(c, x + 1, top + 15, 46, "B")
for (a, b, y0, y1) in ((16, 18, 24, 15), (30, 32, 15, 27)):
    line(c, a, y0, b, y1, "k")
    line(c, a, y0 + 1, b, y1 + 1, "b")
for y in range(25, 47):
    c[y][21] = c[y][24] = "k"
    if y % 3 == 0:
        hline(c, 22, 23, y, "b")
put(c, ["..y..", ".fyf.", "fyyyf", "kbkbk"], 27, 43)
flag(c, 24, 0, "u", 5)
c[1][26] = "s"
SPRITES["monument:Outlaw Rookery"] = fin32(c)

# Whispering Undercroft (Cunning — Ithiss; the Whispers line goes under): a broken chapel front over a wide stair
# that narrows down into the dark, candles at the edges, whispers rising
c = cv48()
put(c, ["s....s......s....s", ".s...s.....s....s.", "..s..........s...."], 15, 0)
roof(c, 24, 4, 10, "u")
wall(c, 14, 14, 21, 13, "u")
for (x, y) in ((16, 6), (17, 7), (18, 7), (32, 6)):
    c[y][x] = "."
put(c, SHUT, 17, 17)
put(c, SHUT, 28, 17)
disc(c, 24, 19, [(1, "d"), (2.4, "U")])
for i, y in enumerate(range(27, 47)):
    x0, x1 = 12 - i // 2, 36 + i // 2
    for x in range(x0, x1 + 1):
        dark = abs(x - 24) <= 3 + i // 3
        c[y][x] = "k" if x in (x0, x1) else ("d" if dark else ("T" if y % 3 == 0 else ("t" if x < 24 else "T")))
for (x, y) in ((14, 30), (34, 30), (11, 37), (37, 37), (8, 44), (40, 44)):
    c[y - 1][x] = "y"
    c[y][x] = "s"
SPRITES["monument:Whispering Undercroft"] = fin32(c)

# Outrider Intercept Post (Cunning + Prowess — Vorghith raiders; Vogen's Gallows): timber watchtower under a dark
# roof, sharpened palisade, gallows with a noose, a mounted outrider with a lance
c = cv48()
roof(c, 11, 2, 8, "u")
wall(c, 4, 10, 15, 8, "b")
put(c, SHUT, 6, 12)
put(c, ["kkkk", "kdyk", "kkkk"], 13, 12)
for x in (5, 17):
    vline(c, x, 18, 46, "b")
    vline(c, x + 1, 18, 46, "B")
line(c, 6, 20, 16, 34, "b")
line(c, 16, 20, 6, 34, "b")
put(c, ["k" * 14, "kbBbBbBbBbBbBk", "k" * 14], 4, 26)
for x in range(0, 30):
    if x % 3 == 1:
        c[34][x] = "k"
    for y in range(35, 47):
        if c[y][x] == ".":
            c[y][x] = "k" if x % 3 == 0 else ("b" if x % 3 == 1 else "B")
    c[39][x] = c[43][x] = "k"
put(c, ["k" * 12, "kbbbbbbbbbBk", "kb.......m..", "kbB......m..", "kbB.....kck.", "kbB.....kcC.", "kbB.....kcC.", "kbB......k..", "kbB.........", "kbB.........", "kbB.........", "kbB.........", "kbB.........", "kbB.........", "kbB.........", "kbB.........", "kbB........."], 20, 18)
vline(c, 44, 8, 36, "b")
put(c, ["k", "m", "M"], 44, 5)
put(c, HORSE, 33, 30)
put(c, [".kmk.", "kmmMk", ".khk.", "kcccC", "kcccC", "kccCC", ".kbk."], 38, 28)
SPRITES["monument:Outrider Intercept Post"] = fin32(c)

# ---- wonders (48): stand on the capital's skyline
# Colossus: crowned bronze warrior on a carved, stepped pedestal, spear raised, red shield
c = cv48()
vline(c, 33, 3, 30, "b")
put(c, [".k.", "kmk", "kmk"], 32, 0)
put(c, ["y.y.y", "yyyyy"], 22, 4)
disc(c, 24, 9, [(2.6, "m")])
wall(c, 20, 12, 9, 12, "m")
hline(c, 21, 27, 20, "b")
line(c, 28, 14, 32, 9, "m", 2)
disc(c, 17, 18, [(1, "y"), (4.4, "c")])
put(c, ["k" * 11, "kmmmmmmmMMk", "kmmmmmmmMMk", "k" * 11], 19, 23)
for x0 in (20, 25):
    put(c, ["kmMk"] * 9 + ["kkkk"], x0, 27)
wall(c, 14, 36, 21, 6, "t")
for x0 in range(16, 32, 4):
    put(c, [".T.", "TTT", "T.T"], x0, 37)
for i, y in enumerate(range(42, 47)):
    hline(c, 12 - i, 36 + i, y, "t")
    c[y][12 - i] = c[y][36 + i] = "k"
    for x in range(33 + i, 36 + i):
        c[y][x] = "T"
    if i % 2 == 0:
        hline(c, 12 - i, 36 + i, y, "k")
SPRITES["wonder:Colossus"] = fin32(c)

# The Grand Exchange: trading hall under a gilt dome, colonnade, the flags of many houses, broad steps
c = cv48()
put(c, [".k.", "kyk", "kYk", "kkk"], 23, 1)
disc(c, 24, 14, [(9, "y")])
for x0, col in ((3, "c"), (11, "a"), (34, "e"), (42, "l")):
    flag(c, x0, 9, col, 11)
put(c, ["k" * 46, "k" + "w" * 42 + "WWk", "k" * 46], 1, 19)
wall(c, 2, 22, 44, 20, "w")
for y in range(24, 40):
    for x in range(3, 44):
        c[y][x] = "d"
for x0 in range(3, 44, 5):
    put(c, ["kkkk"] + ["kwWk"] * 15 + ["kkkk"], x0, 23)
for i, y in enumerate(range(42, 47)):
    hline(c, 1 - (i > 2), 46 + (i > 2), y, "k" if i % 2 == 0 else "w")
SPRITES["wonder:The Grand Exchange"] = fin32(c)

# The Exalted Archbasilica (key: The Eternal Sepulchre): twin spired towers, red-roofed nave, great rose window, portal
c = cv48()
wall(c, 12, 18, 25, 29, "t")
roof(c, 24, 6, 12)
courses(c, 13, 20, 33, 45)
disc(c, 24, 25, [(1.2, "y"), (3, "c"), (4.6, "a"), (6, "y")])
put(c, ["...kkkkk...", "..kdddddk..", ".kdddddddk.", "kdddddddddk", "kdddddddddk", "kdddddddddk", "kdddddddddk", "kdddddddddk", "kdddddddddk", "kdddddddddk", "kdddddddddk"], 19, 36)
for x0 in (1, 36):
    put(c, CROSS5, x0 + 3, 0)
    spire(c, x0 + 5, 5, 11)
    wall(c, x0, 15, 11, 32, "t")
    courses(c, x0 + 1, 17, x0 + 7, 45)
    for y0 in (18, 27):
        put(c, ["kkkk", "kyyk", "kyyk", "kyYk", "kkkk"], x0 + 4, y0)
    door4(c, x0 + 4, 39, 8)
SPRITES["wonder:The Eternal Sepulchre"] = fin32(c)

# High Chancery: clock tower under a red spire between two long office wings, rows of clerks' windows
c = cv48()
spire(c, 23, 0, 9)
wall(c, 18, 8, 11, 39, "w")
disc(c, 23, 14, [(.6, "k"), (3, "s")])
c[12][23] = c[13][23] = "k"
c[14][24] = "k"
for y0 in (20, 27):
    put(c, ["kkkk", "kyyk", "kyyk", "kkkk"], 22, y0)
put(c, [".kkkk.", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk"], 20, 36)
for x0 in (0, 29):
    wall(c, x0, 20, 19, 27, "w")
    roof(c, x0 + 9, 11, 9)
    for y0 in (22, 29, 36):
        hline(c, x0 + 1, x0 + 17, y0 + 5, "b")
        for o in (1, 5, 9, 13):
            put(c, ["kkkk", "kyyk", "kyYk", "kkkk"], x0 + o + (1 if o == 13 else 0), y0)
SPRITES["wonder:High Chancery"] = fin32(c)


# ================================================================ BATCH 11: skylines + infrastructure
# The far layer: the board fades these toward the sky, so each keeps its old footprint and only gains the 2-tone ramp.
# Tiers climb the same ladder as the holdings: thatch (Hamlet) -> plaster and a stone church (Village) -> stone hall
# (Town) -> towers (City) -> gilded domes and a spire (Metropolis).
def sky(w, h):
    """Canvas for a free-size skyline / infrastructure piece: w wide, h total rows incl. ground."""
    return cv(w, h - 1)


def cypress(c, x, y, h):
    """Tall narrow seasonal tree, 3 wide, top at y, shaded on the right, trunk 2 rows."""
    put(c, [".l."], x, y)
    for j in range(1, h - 2):
        put(c, ["llL" if j % 4 else "lLL"], x, y + j)
    put(c, [".b.", ".b."], x, y + h - 2)


# Hamlet core: thatched longhouse on a knoll, smoke from the ridge, cypress, haystack
c = sky(39, 34)
cypress(c, 0, 3, 30)
put(c, [".s", "s.", ".s"], 18, 0)
wall(c, 8, 16, 21, 11, "w")
roof(c, 18, 4, 12, "y")
win4(c, 10, 18)
win4(c, 23, 18)
door4(c, 16, 20)
put(c, ["....kk....", "...kyyk...", "..kyyyYk..", ".kyyyyYYk.", ".kyyyyyYk.", "kyyyyyyYYk", "kyyybyyYYk", "kyyyyyyYYk", "kyyyyyYYYk", "kyyyyyyYYk", "kyyyyyyYYk", "kkkkkkkkkk"], 29, 15)
for y in range(27, 33):
    for x in range(3, 39):
        if c[y][x] == ".":
            c[y][x] = "L" if x > 30 else "l"
hline(c, 3, 38, 27, "k")
put(c, [".b.", ".b."], 1, 31)
SPRITES["sky:core:Hamlet"] = fin32(c)

c = sky(15, 28)
cypress(c, 6, 0, 22)
fence32(c, 0, 14, 22)
for y in range(22, 27):
    c[y][7] = "b"
SPRITES["sky:fill:Hamlet"] = fin32(c)

# Village core: stone church, tower and red spire between two plastered cottages
c = sky(39, 40)
spire(c, 19, 0, 8)
wall(c, 15, 7, 9, 20, "t")
courses(c, 16, 9, 21, 25)
put(c, ["kkkk", "kdyk", "kyYk", "kkkk"], 17, 9)
put(c, SLIT, 19, 15)
roof(c, 19, 18, 8)
wall(c, 11, 26, 17, 13, "t")
courses(c, 12, 28, 25, 37)
for o in (13, 22):
    put(c, ["kkkk", "kyyk", "kyyk", "kyYk", "kkkk"], o, 28)
put(c, [".kkk.", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk"], 17, 32)
for x0 in (0, 28):
    wall(c, x0, 25, 11, 14, "w")
    roof(c, x0 + 5, 20, 5)
    hline(c, x0 + 1, x0 + 9, 30, "b")
    win4(c, x0 + 1, 26)
    door4(c, x0 + 6, 32)
SPRITES["sky:core:Village"] = fin32(c)

c = sky(15, 28)
wall(c, 1, 7, 13, 20, "w")
roof(c, 7, 0, 7)
for y in (13, 19):
    hline(c, 2, 12, y, "b")
win4(c, 2, 9)
win4(c, 9, 9)
win4(c, 2, 15)
door4(c, 8, 20)
SPRITES["sky:fill:Village"] = fin32(c)

# Town core: crenellated stone hall between two gabled houses
c = sky(36, 30)
cren(c, 9, 0, 17)
wall(c, 9, 2, 17, 27, "t")
courses(c, 10, 4, 22, 27)
for o in (11, 21):
    put(c, ["kkkk", "kyyk", "kyyk", "kkkk", "kyYk", "kkkk"], o, 5)
    put(c, ["kkkk", "kyyk", "kyYk", "kkkk"], o, 14)
put(c, [".kkk.", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk"], 15, 21)
for x0 in (0, 27):
    wall(c, x0, 12, 9, 17, "w")
    roof(c, x0 + 4, 8, 4)
    hline(c, x0 + 1, x0 + 7, 18, "b")
    win4(c, x0 + 2, 13)
    door4(c, x0 + 2, 22)
SPRITES["sky:core:Town"] = fin32(c)

c = sky(15, 21)
wall(c, 1, 6, 13, 14, "w")
roof(c, 7, 0, 6)
hline(c, 2, 12, 12, "b")
win4(c, 2, 7)
win4(c, 9, 7)
door4(c, 6, 13)
SPRITES["sky:fill:Town"] = fin32(c)

# City core: tall red-roofed hall between twin crenellated towers
c = sky(45, 39)
wall(c, 11, 12, 23, 26, "t")
roof(c, 22, 1, 11)
courses(c, 12, 14, 30, 36)
for o in (14, 27):
    put(c, ["kkkk", "kyyk", "kyyk", "kkkk", "kyYk", "kkkk"], o, 15)
    put(c, ["kkkk", "kyyk", "kyYk", "kkkk"], o, 24)
disc(c, 22, 18, [(1, "y"), (2.6, "c")])
put(c, ["..kkkk..", ".kddddk.", "kddddddk", "kddddddk", "kddddddk", "kddddddk", "kddddddk", "kddddddk", "kddddddk"], 18, 29)
for x0 in (3, 34):
    cren(c, x0, 0, 8)
    wall(c, x0, 2, 8, 36, "t")
    courses(c, x0 + 1, 4, x0 + 4, 36)
    for y0 in (6, 15, 24):
        put(c, SLIT, x0 + 3, y0)
SPRITES["sky:core:City"] = fin32(c)

c = sky(12, 26)
wall(c, 0, 6, 11, 19, "w")
roof(c, 5, 1, 5)
for y in (12, 17):
    hline(c, 1, 9, y, "b")
win4(c, 3, 7)
win4(c, 3, 13)
door4(c, 4, 18)
SPRITES["sky:fill:City"] = fin32(c)

# Metropolis core: spired central tower with a gilt finial, gold-domed side halls, arcades, bastions
c = sky(51, 46)
put(c, ["y"], 25, 0)
spire(c, 25, 1, 11)
wall(c, 19, 11, 13, 34, "t")
courses(c, 20, 13, 28, 43)
for y0 in (14, 22):
    for x0 in (21, 26):
        put(c, ["kkkk", "kyyk", "kyyk", "kyYk", "kkkk"], x0, y0)
put(c, ["..kkkk..", ".kddddk.", "kddddddk", "kddddddk", "kddddddk", "kddddddk", "kddddddk", "kddddddk", "kddddddk"], 21, 36)
for x0 in (12, 31):
    wall(c, x0, 30, 8, 15, "w")
    for xa in (x0 + 1, x0 + 4):
        put(c, [".kk.", "kddk", "kddk", "kddk"], xa, 33)
for x0 in (4, 38):
    disc(c, x0 + 4, 20, [(4.6, "y")])
    wall(c, x0, 20, 9, 25, "w")
    for y0 in (23, 31):
        win4(c, x0 + 2, y0)
    door4(c, x0 + 2, 38)
cren(c, 0, 28, 5)
wall(c, 0, 30, 5, 15, "t")
cren(c, 46, 25, 5)
wall(c, 46, 27, 5, 18, "t")
SPRITES["sky:core:Metropolis"] = fin32(c)

c = sky(12, 30)
spire(c, 5, 0, 7)
wall(c, 1, 6, 9, 23, "w")
for y in (13, 20):
    hline(c, 2, 8, y, "b")
win4(c, 3, 8)
win4(c, 3, 15)
door4(c, 3, 22)
SPRITES["sky:fill:Metropolis"] = fin32(c)


# ---------------------------------------------------------------- infrastructure pieces
# Town Hall: half-timbered hall, clock in the gable, gilt finial
c = sky(18, 25)
wall(c, 0, 10, 17, 14, "w")
for xx in (5, 11):
    vline(c, xx, 11, 22, "b")
hline(c, 1, 15, 15, "b")
roof(c, 8, 2, 8)
put(c, ["y", "y"], 8, 0)
disc(c, 8, 6.5, [(.6, "k"), (1.8, "s")])
win4(c, 1, 11)
win4(c, 12, 11)
door4(c, 7, 17)
SPRITES["inf:Town Hall"] = fin32(c)

# Cathedral: gold cross on a red spire, west tower with a rose window and lancet, lean-to aisles either side, great door
c = sky(18, 46)
put(c, CROSS5, 6, 0)
spire(c, 8, 5, 10)
wall(c, 4, 14, 9, 31, "t")
courses(c, 5, 16, 9, 43)
disc(c, 8, 20, [(.8, "y"), (1.8, "c"), (2.8, "a")])
put(c, ["kkkk", "kyyk", "kyyk", "kyyk", "kyYk", "kkkk"], 6, 25)
for x0, x1, step in ((0, 4, 1), (13, 17, -1)):
    for i in range(5):
        y = 32 - i
        xa = x0 + i if step > 0 else x1 - i
        c[y][xa] = "k"
        for x in range(min(xa, x1 if step > 0 else x0), max(xa, x1 if step > 0 else x0) + 1):
            if c[y + 1][x] == ".":
                c[y + 1][x] = "r" if step > 0 else "R"
    for y in range(33, 45):
        for x in range(x0, x1 + 1):
            c[y][x] = "k" if x == (x0 if step > 0 else x1) else ("t" if step > 0 else "T")
    put(c, ["kk", "ky", "ky", "kk"], x0 + 1 if step > 0 else x1 - 2, 36)
put(c, [".kk.", "kddk", "kddk", "kddk", "kddk", "kddk", "kddk", "kddk"], 6, 37)
SPRITES["inf:Cathedral"] = fin32(c)

# Chapel: gold cross, steep red roof, stone walls, lancets
c = sky(18, 27)
put(c, CROSS5, 6, 0)
wall(c, 0, 13, 17, 13, "t")
roof(c, 8, 5, 8)
courses(c, 1, 15, 14, 24)
for o in (2, 11):
    put(c, ["kkkk", "kyyk", "kyyk", "kyYk", "kkkk"], o, 15)
door4(c, 7, 19)
SPRITES["inf:Chapel"] = fin32(c)

# Magistrate's Hall: gilt finial, roundel in the gable, colonnaded upper hall over a stone ground floor
c = sky(21, 28)
put(c, ["y", "y"], 10, 0)
wall(c, 0, 12, 21, 15, "t")
roof(c, 10, 2, 10)
disc(c, 10, 7, [(.6, "k"), (1.8, "s")])
for y in range(13, 18):
    for x in range(1, 20):
        c[y][x] = "w" if x % 3 else "d"
hline(c, 0, 20, 18, "K")
courses(c, 1, 20, 17, 25)
win4(c, 2, 20)
win4(c, 15, 20)
put(c, [".kkk.", "kyyyk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk"], 8, 20)
SPRITES["inf:Magistrate's Hall"] = fin32(c)

# Library: blue-domed reading tower, tall lit windows with shelf mullions
c = sky(18, 25)
put(c, [".k.", "kyk"], 7, 0)
disc(c, 8, 7, [(4.6, "e")])
wall(c, 3, 6, 11, 18, "t")
for y0 in (8, 14):
    put(c, ["kkkkkkk", "kykykyk", "kYkYkYk", "kykykyk", "kkkkkkk"], 5, y0)
door4(c, 7, 19, 5)
SPRITES["inf:Library"] = fin32(c)

# Garrison: narrow crenellated tower with a red pennant
c = sky(9, 37)
flag(c, 4, 0, "c", 4)
cren(c, 0, 4, 9)
wall(c, 0, 6, 9, 30, "t")
courses(c, 1, 8, 5, 33)
for y0 in (9, 18, 25):
    put(c, SLIT, 4, y0)
door4(c, 3, 30, 6)
SPRITES["inf:Garrison"] = fin32(c)

# Keep: broad crenellated keep with a red flag, tall windows, slit, gate
c = sky(15, 37)
flag(c, 7, 0, "c", 4)
cren(c, 0, 4, 15)
wall(c, 0, 6, 15, 30, "t")
courses(c, 1, 8, 11, 33)
put(c, ["kkkk", "kddk", "kddk", "kkkk"], 6, 8)
for o in (2, 9):
    put(c, ["kkkk", "kyyk", "kyyk", "kkkk", "kyYk", "kkkk"], o, 15)
put(c, SLIT, 7, 22)
put(c, [".kkk.", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk"], 5, 29)
SPRITES["inf:Keep"] = fin32(c)

# Muster Field: tall pole with a swallow-tailed red banner
c = sky(6, 34)
vline(c, 0, 0, 32, "k")
put(c, ["ccccC", "ccccC", "cyycC", "cyYcC", "ccccC", "ccccC", "cccCC", "cC.cC", "c...C"], 1, 1)
put(c, ["kk", "kb"], 0, 31)
SPRITES["inf:Muster Field"] = fin32(c)

# walls: tiles repeated across the lot; Stone Walls gets a tower at each end
SPRITES["inf:Wooden Walls"] = art([".k..k.", "kbkkbk", "kbBkbB", "kkkkkk", "kbBkbB", "kbBkbB", "kbBkbB", "kkkkkk", "kbBkbB", "kbBkbB", "kbBkbB"], 6, 12)
SPRITES["inf:Stone Walls"] = art(["kkk...", "ktk...", "kkkkkk", "tttttt", "tTtttt", "TTTTTT", "ttttTt", "tttttt", "TTTTTT", "tTtttt", "tttttt", "tttttt"], 6, 13)
c = sky(9, 17)
cren(c, 0, 0, 9)
wall(c, 0, 2, 9, 14, "t")
courses(c, 1, 4, 5, 14)
put(c, SLIT, 4, 4)
put(c, [".kk.", "kddk", "kddk", "kddk", "kddk", "kddk"], 3, 10)
SPRITES["inf:Stone Walls:tower"] = fin32(c)

# Town Square: the well under its little roof, and the market cross on its steps (front piece, shaded like a holding)
c = cv(17, 15)
roof(c, 5, 0, 5)
for x in (1, 9):
    vline(c, x, 6, 9, "b")
hline(c, 1, 9, 6, "b")
put(c, ["k", "k", "kmk", "mmM"], 4, 7)
wall(c, 0, 10, 11, 5, "t")
for x in (3, 7):
    c[12][x] = "T"
put(c, ["..k..", ".kmk.", "kmmMk", ".kmk.", "..t..", ".ktk.", ".ktT.", ".ktT.", ".ktT.", ".ktT.", "kkkkk", "ktttT", "kkkkk", "ktttT", "kkkkk"], 12, 0)
SPRITES["inf:Town Square"] = fin32(c)

# Road Wardens: wardens' lodge, two mounts tied at a hitching rail (front piece)
c = sky(35, 16)
wall(c, 0, 5, 9, 10, "w")
roof(c, 4, 1, 4)
put(c, ["kkk", "kyk", "kkk"], 1, 6)
door4(c, 4, 8)
put(c, ["k" * 26, "kbbbbbbbbbbbbbbbbbbbbbbbBk"], 9, 8)
for x in (9, 33):
    vline(c, x, 10, 14, "k")
for x0, col in ((10, "b"), (21, "u")):
    sh = SHADE[col]
    put(c, ["..........kk..",
            ".........k" + col * 2 + "k.",
            "........k" + col * 3 + sh + "k",
            "........k" + col + "k" + col + sh + "k",
            ".......k" + col * 2 + "k.kk",
            ".kkkkkk" + col * 2 + "k....",
            "k" + col * 7 + sh * 2 + "k....",
            "k" + col * 6 + sh * 3 + "k....",
            "k" + col * 2 + ("ccc" if col == "b" else "aaa") + col + sh * 2 + "k....",
            ".k" + col + "kkkk" + col + "k.....",
            ".k" + col + "....k" + sh + "k.....",
            ".k" + col + "....k" + sh + "k.....",
            ".kk....kk....."], x0, 2)
SPRITES["inf:Road Wardens"] = fin32(c)

SPRITES["inf:Bridges"] = art(["kkkkkkkkkkkkkkkkkkkkk",
                         "kttttttttttttttttTTTk",
                         "ktTttttTttttTttttTTTk",
                         "kttTkkkkkkkkkkkkkTTTk",
                         "kttk.............kTTk",
                         "ktk...............kTk",
                         "kk.................kk",
                         "k...................k"], 21, 9)
SPRITES["inf:Aqueducts"] = art(["kkkkkkkkkkkk",
                           "eeeeeEeeeeeE",
                           "kkkkkkkkkkkk",
                           "tttttttttttt",
                           "tTtttTtttTtt",
                           "tttttttttttt",
                           "ttttkkkkkttt",
                           "tttk.....ktt",
                           "ttk.......kt",
                           "tTk.......kt",
                           "tTk.......kt",
                           "tTk.......kt",
                           "tTk.......kt",
                           "tTk.......kt",
                           "tTk.......kt",
                           "tTk.......kt",
                           "tTk.......kt",
                           "tTk.......kt",
                           "tTk.......kt",
                           "tTk.......kt",
                           "tTk.......kt"], 12, 22)


# ================================================================ BATCH 12: map pieces, retinues, markers (24)
# Retinues share one body (head rows 3-9, torso 10-16, legs 17-22, feet on the ground row) so they read as a set;
# rank shows in kit: Levy (wool hood, spear) < Man-at-Arms (kettle helm, mail, kite shield, mace) < Sergeant (sallet,
# riveted brigandine, halberd) ; Oathsworn (great helm, pale surcoat, the oath-sword, lance). Lit from the upper left.
# 'p' = owner colour and 'P' its shade, both swapped per player; 'j' = skin in shade.
SPRITES["army:Levy"] = art([
    "................k.......",
    "...............kmk......",
    "...............kmM......",
    "......kkkk.....kbk......",
    ".....kbbbbk.....b.......",
    "....kbbbbbBk....b.......",
    "....kbhhhhBk....b.......",
    "....kbkhkhjk....b.......",
    "....kBhhhhjk....b.......",
    ".....kBjjjk.....b.......",
    "....kkppppkk....b.......",
    "...kpppppppPk...b.......",
    "..kpkpppppPkPk..b.......",
    "..kpkpppppPkPkkhb.......",
    "..khkbbbbbBkkk..b.......",
    "...kkpppppPk....b.......",
    "....kpppkPPk....b.......",
    "....kBBk.kBBk...b.......",
    "....kBbk.kbBk...b.......",
    "....kbBk.kBbk...b.......",
    "....kBBk.kBBk...b.......",
    "...kkddk.kddkk..B.......",
    "...kkkkk.kkkkk..k.......",
])

SPRITES["army:Man-at-Arms"] = art([
    "........................",
    "......kkkkkk............",
    ".....kmmmmmMk...........",
    "...kkkkkkkkkkkk.........",
    ".....kmhhhhMk.....kmk...",
    ".....kmhkhkjk....kmmMk..",
    ".....kmhhhhjk.....kMk...",
    ".....kMmjjjMk.....kbk...",
    "....kkmmmmmmkk...kbk....",
    "..kkkmmmmmmmMMk.kbk.....",
    ".kpppkmmmmmmMMkkhk......",
    "kppyPkmmmmmmMMkkk.......",
    "kppyPkmmmmmMMMk.........",
    "kyyyYkmmmmmMMMk.........",
    "kppyPkbbbbbBBBk.........",
    "kppyPkmmmmmMMMk.........",
    ".kpyPkmmmmMMMMk.........",
    "..kPk.kmmMkkMMk.........",
    "...k..kmMk.kmMk.........",
    "......kmMk.kmMk.........",
    "......kMMk.kMMk.........",
    ".....kkddk.kddkk........",
    ".....kkkkk.kkkkk........",
])

SPRITES["army:Sergeant"] = art([
    "...............kk.......",
    "..............kmmk......",
    ".......kkk....kmMMk.....",
    ".....kkmmmkk..kmMk......",
    "....kmmmmmmMk..kbmk.....",
    "...kkmmmmmmMMk..b.......",
    "....kddddddk....b.......",
    "....khhhhhjk....b.......",
    "....khkhhkjk....b.......",
    ".....kjhhjk.....b.......",
    "....kkmpppkk....b.......",
    "...kmkpypyPkk...b.......",
    "..kmmkpppppkMk..b.......",
    "..kmMkpypyPkMkkhb.......",
    "..khkkbbbbbkkk..b.......",
    "..kmkkpypyPkm...b.......",
    "...k.kppppPkMk..b.......",
    ".....kmMkkMMkk..b.......",
    ".....kmMk.kmMk..b.......",
    ".....kbBk.kbBk..b.......",
    ".....kmMk.kmMk..b.......",
    "....kkddk.kddkk.B.......",
    "....kkkkk.kkkkk.k.......",
])

# Oathsworn (key: Knight Templar)
SPRITES["army:Knight Templar"] = art([
    "................kppp....",
    "................kpPP....",
    "................kpP.....",
    ".....kkkkkk.....kb......",
    "....kmmmmmMk.....b......",
    "....kmmmmmMk.....b......",
    "....kkkkkkkk.....b......",
    "....kmmkmmMk.....b......",
    "....kmmkmMMk.....b......",
    ".....kkkkkk......b......",
    "...kkssssssk.....b......",
    "..kssssspsssZk...b......",
    ".kssssspppsZZkkkhb......",
    ".kmkssssps ZZk..kb......".replace(" ", "s"),
    ".kmkssssps sZk...b......".replace(" ", "s"),
    ".khkbbbbpbbBBk...b......",
    "..kksssspssZk....b......",
    "....ksssssZZk....b......",
    "....kmmkkmMMk....b......",
    "....kmMk.kmMk....b......",
    "....kmMk.kmMk....b......",
    "...kkddk.kddkk...B......",
    "...kkkkk.kkkkk...k......",
])

for _k, _dx in (("army:Levy", 6), ("army:Man-at-Arms", 5), ("army:Sergeant", 6), ("army:Knight Templar", 6)):
    SPRITES[_k] = rank2(SPRITES[_k], _dx)          # each retinue stands as a unit: a second rank behind the first

# bandit army: a hooded leader under a skull banner, a ruffian with a raised club behind (no owner colour)
SPRITES["map:bandit_army"] = art([
    "..k.....................",
    "..bkkkkkkkk.............",
    "..bkssssssZk............",
    "..bkskksksZk......kk....",
    "..bkssssssZk.....kbbk...",
    "..bksskkssZk.....kbBk...",
    "..bkkkkkkkkk.....kbk....",
    "..b.....kkkk....kbk.....",
    "..b....kuuuUk...kbk.....",
    "..b...kuuuuUUk.kbk......",
    "..b...kuddddUkkbkkk.....",
    "..b...kudhkhUkkhkuUk....",
    "..b...kudhhhUk.kuuuUk...",
    "..bkkkkuuuuUUkkuhhUk....",
    ".khhkkbbbbbbBkkkuuuUk...",
    "..b..kbccccCBk.kbbbBk...",
    "..b..kbbbbbbBk.kbbBBk...",
    "..b..kbbbbbBBk..kbbBk...",
    "..b...kbBkkbBk..kbkBk...",
    "..b...kbBk.kbBk.kbkBk...",
    "..b...kdBk.kdBk.kdkdk...",
    "..B..kkddk.kddk.kkkkk...",
    "..k..kkkkk.kkkkk........",
])
# Bandit camps: one tent per point of the camp's Authority (map:camp = 1, then map:camp:2 .. map:camp:4); the board
# picks by the camp's current Authority. The first tent stands in front; each further tent sits farther back — higher,
# smaller, hazier — with its peak showing over the ones in front, so the count reads at a glance.
def _tent(c, cx, top, h, cloth="s", shade=None):
    """A-frame tent, apex at (cx, top), h rows; lit side left, shaded right, dark door, ridge pole tip above."""
    shade = shade or SHADE[cloth]
    c[top - 1][cx] = "b"
    for i in range(h):
        for x in range(cx - i, cx + i + 1):
            if x in (cx - i, cx + i) or i == h - 1:
                c[top + i][x] = "k"
            elif i >= h // 2 and abs(x - cx) <= (i - h // 2) // 2:
                c[top + i][x] = "d"
            else:
                c[top + i][x] = shade if x > cx else cloth


def _campfire(c, x, y):
    put(c, [".y.", "yfy", "fYf", "kbk"], x, y)


CAMP_TENTS = [(11, 13, 10, "s", "Z"),       # front: apex (cx, top), rows, lit, shade
              (7, 11, 8, "s", "Z"),         # behind, left
              (16, 11, 8, "b", "B"),        # behind, right (hide)
              (11, 8, 6, "Z", "T")]         # farthest, hazy, its peak over the front ridge
for n in range(1, 5):
    c = cv(24, 23)
    for cx, top, h, lit, sh in reversed(CAMP_TENTS[:n]):
        _tent(c, cx, top, h, lit, sh)
    _campfire(c, 20, 19)
    SPRITES["map:camp" + ("" if n == 1 else ":" + str(n))] = fin(c)   # outlines kept at map scale; shade_rim adds light

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


# ---------------------------------------------------------------- 2-tone pass: figures, map pieces, markers, icons
# Drawn above as flat art; shaded here so they share the holdings' light without losing their outlines.
# Heraldry (her:) and terrain props (prop:) keep their own tone systems.
for _k in [k for k in SPRITES if k.startswith(("army:", "map:", "mk:", "eq:", "st:"))]:
    SPRITES[_k] = shade_rim(SPRITES[_k], ground=not _k.startswith(("eq:", "st:", "mk:")))

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
        shown = ns.get("NAME_DISPLAY", {}).get(name)          # art keyed by the printed name (id Coliseum, shown Drill Yard)
        if shown and "holding:" + shown in SPRITES:
            return "holding:" + shown
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
    "Bridges": ("gap", ""), "Aqueducts": ("span", ""), "Town Square": ("front", "left"),
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
#   lift - the skyline stands this many px up a rise behind the holdings (clears 32px holdings)
#   head - extra sky above the skyline's ground line (48px wonders on the rise, 48px monuments in front)
SCENE_STYLE = {"fade": 0.15, "sil": 0.6, "halo": 1, "lift": 8, "head": 10}


def feet_key(raw_name):
    """Terrain strip for a ward whose chain is rooted in this Raw Material. None if it has none."""
    k = "feet:" + raw_name
    return k if k in SPRITES else None


def _dims(key):
    if key.startswith(("sky:", "inf:", "feet:", "prop:")):
        return None          # free size: checked for consistency only
    if key.startswith(("monument:", "wonder:")):
        return S48, S48
    if key.startswith("eq:"):
        return S18, S18
    if key.startswith("st:"):
        return S12, S12
    if key.startswith("her:"):
        return S48, S48
    if key.startswith("mk:"):
        return S24, S24
    if key.startswith(("holding:", "group:", "tier:", "scenery:")):
        return S32, S32
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
        if kind == "map" and name not in ns.get("SETTLEMENTS", {}) and name not in ("camp", "bandit_army")                 and not (name.startswith("camp:") and name[5:] in ("2", "3", "4")):
            out.append(f"{key}: not a settlement tier / camp / bandit_army")
    known = set(ns.get("NODES", {})) | set(ns.get("WONDERS", {})) | set(ns.get("SETTLEMENTS", {}))
    known |= {v for k, v in ns.get("NAME_DISPLAY", {}).items() if k in known}   # art keyed by the printed name
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
    nd = ns.get("NAME_DISPLAY", {})
    dn = lambda n: nd.get(n, n)                      # what players read (Artillery Park -> Ordnance Yard); keys stay canonical
    comps = []
    for n, v in ns.get("NODES", {}).items():
        if v.get("type") == "Raw Materials" and feet_key(n):
            kids = [c for c in (v.get("builds_into") or []) if c in ns.get("NODES", {})]
            kid = kids[0] if kids else n
            comps.append({"ft": feet_key(n), "front": sprite_key(kid, ns), "label": dn(n) + " \u2192 " + dn(kid)})
    lab = {k: ":".join(dn(p) for p in k.split(":")) for k in keys}
    data = json.dumps({"S": SPRITES, "K": keys, "L": lab, "P": PALETTES[palette], "C": comps, "pal": palette,
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
D.K.forEach(k=>{const rows=D.S[k];cell(g,rows[0].length,rows.length,D.L[k]||k,c=>paint(c,rows,0,0));});
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
 D.C.forEach(o=>{const ft=D.S[o.ft],fr=D.S[o.front];cell(g,40,30,o.label,c=>{c.fillStyle=SKY;c.fillRect(0,0,40,28);
  c.fillStyle=GR;c.fillRect(0,28,40,2);paint(c,fr,4,28-(fr.length-1),0,true);feetOn(c,ft,1,28);});});}
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