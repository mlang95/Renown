"""sprites_hd_wip.py — 1.5x redraw of sprites.py (WIP; spliced into sprites.py when complete).

Holdings / groups / tiers / scenery / map pieces 24x24, monuments / wonders 36x36,
equipment 18x18, status 12x12, heraldry 48x48, free-size pieces x1.5.
Same palette keys as sprites.py.
"""

HD = {}

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
HD["group:g_logistics"] = fin(c)

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
HD["holding:Butchery"] = fin(c)

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
HD["holding:Smokehouse"] = fin(c)

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
HD["holding:Caravanery"] = fin(c)

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
HD["holding:Coliseum"] = fin(c)

# Conditioning Field: straw pells on posts, archery butt, weapon rack
c = cv()
for x in (1, 7):
    put(c, [".kk.", "kyyk", "kyyk", "kbyk", "kyyk", ".kk.", "..b.", "..b.", "..b.", "..b.", "..b.", ".kbk"], x, 11)
put(c, ["..kkkk..",
        ".kssssk.",
        "kscccssk",
        "kscykcsk",
        "kscccssk",
        ".kssssk.",
        "..kbbk..",
        ".kb..bk.",
        "kb....bk"], 12, 14)
put(c, ["m..m", "b..b", "bbbb", "b..b", "b..b", "bbbb", "b..b"], 20, 16)
HD["holding:Conditioning Field"] = fin(c)

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
HD["holding:Grand Tournament"] = fin(c)

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
HD["holding:Charcoal Burner"] = fin(c)

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
HD["holding:Kiln"] = fin(c)

# Levy Hall: muster hall, half-timber, banner, spear rack with shields
c = cv()
gable(c, 7, 4, 7)
box(c, 0, 11, 15, 12, "w")
for x in (4, 10):
    vline(c, x, 12, 21, "b")
hline(c, 1, 13, 15, "b")
put(c, WIN, 1, 12)
put(c, WIN, 11, 12)
put(c, ["kkkkk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk"], 5, 16)
put(c, ["cc", "cc", "cc", "c."], 7, 11)
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
        "bbbbbbb"], 16, 11)
HD["holding:Levy Hall"] = fin(c)

# Siege Camp: palisade, two tents with pennants, campfire
HD["holding:Siege Camp"] = art([
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

# Siege Works: iron-capped ram slung under a hide-covered mantlet, on wheels
c = cv()
put(c, ["......kkkkkkkkkkkk......",
        "....kkssssssssssssskk...",
        "..kksssksssssksssssssk..",
        ".ksssssksssssksssssssssk",
        "kkkkkkkkkkkkkkkkkkkkkkkk",
        ".kb.....k......k.....bk.",
        ".kb.....k......k.....bk.",
        ".kb.....m......m.....bk.",
        "kmmmkbbbbbbbbbbbbbbbbbk.",
        "kmmmkbbbbbbbbbbbbbbbbbk.",
        ".kb..................bk.",
        "kkkkkkkkkkkkkkkkkkkkkkkk",
        "kbbbbbbbbbbbbbbbbbbbbbbk",
        "kkkkkkkkkkkkkkkkkkkkkkkk"], 0, 4)
put(c, WHEEL, 1, 16)
put(c, WHEEL, 16, 16)
HD["holding:Siege Works"] = fin(c)

# Battery Park: trebuchet, cocked: counterweight up, arm down, shot in the sling
c = cv()
put(c, ["kkkkk...................",
        "kuuuk...................",
        "kutuk...................",
        "kuuuk...................",
        "kkkkkb..................",
        "...k.bb.................",
        "......bb................",
        "......kbb...............",
        ".....kbkbb..............",
        ".....kbmkbb.............",
        "....kb.k..bb............",
        "....kb.....bb...........",
        "...kb.......bb..........",
        "...kbbbbbbbbbbb.........",
        "..kb.........kbb........",
        "..kb..........kbbk......",
        ".kb............kb.kk....",
        "kkkkkkkkkkkkkkkkkkkkkkk.",
        "kbbbbbbbbbbbbbbbbbbbbbk.",
        "kkkkkkkkkkkkkkkkkkkk.kuk"], 0, 2)
put(c, WHEEL5, 1, 18)
put(c, WHEEL5, 14, 18)
HD["holding:Battery Park"] = fin(c)

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
HD["holding:War College"] = fin(c)


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


c = cv(36, 35)
_cart(c, 0, 22)
_cart(c, 12, 22, "c")
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
        ".kk....kk....."], 22, 22)
hline(c, 24, 25, 29, "k")
HD["monument:Baggage Train"] = fin(c)

# Royal Pavilion: great striped tent, crown finial, stone flanking lodges, standards
c = cv(36, 35)
put(c, ["..y.y..", "..yyy..", "..kyk.."], 15, 2)
put(c, ["k", "k", "k"], 18, 5)
for i in range(11):
    for x in range(18 - i - 1, 18 + i + 2):
        if 0 <= x < 36:
            edge = x in (18 - i - 1, 18 + i + 1)
            c[8 + i][x] = "k" if edge else ("a" if ((x - 18) // 2) % 2 == 0 else "y")
hline(c, 5, 31, 19, "k")
for x in range(6, 31):
    c[20][x] = "y" if x % 2 else "k"
for j in range(21, 34):
    for x in range(7, 30):
        c[j][x] = "a" if ((x - 7) // 2) % 2 == 0 else "y"
    c[j][6] = "k"
    c[j][30] = "k"
put(c, ["kkkkk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk"], 16, 25)
for x0 in (0, 31):
    box(c, x0, 21, 5, 13, "t")
    put(c, ["k.k.k", "kkkkk"], x0, 19)
    put(c, SLIT, x0 + 2, 23)
    put(c, ["kkk", "kdk", "kdk", "kdk"], x0 + 1, 29)
put(c, ["k..", "kcc", "kcc", "k..", "k..", "k..", "k.."], 2, 12)
put(c, ["k..", "kcc", "kcc", "k..", "k..", "k..", "k.."], 33, 12)
HD["monument:Royal Pavilion"] = fin(c)

# Ordnance Yard (key: Artillery Park; NAME_DISPLAY spells it 'Ordinance Yard'): hooped bombard with flared muzzle on a timber bed, kegs, shot pyramid
c = cv(36, 35)
put(c, ["............................kkkk....",
        "...........kkkkkkkkkkkkkkkkkmmmmk...",
        "...kkkkkkkkmmkmmmkmmmkmmmkmmmmmmmk..",
        "..kmmmkmmmkmmkmmmkmmmkmmmkmmmkkkkmk.",
        "..kmmmkmmmkmmkmmmkmmmkmmmkmmkdddkmk.",
        "..kmmmkmmmkmmkmmmkmmmkmmmkmmkdddkmk.",
        "..kmmmkmmmkmmkmmmkmmmkmmmkmmmkkkkmk.",
        "...kkkkkkkkmmkmmmkmmmkmmmkmmmmmmmk..",
        "...........kkkkkkkkkkkkkkkkkmmmmk...",
        "............................kkkk....",
        ".kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk....",
        ".kbbbbbbbbbbbbbbbbbbbbbbbbbbbbbk....",
        ".kbkbbbbkbbbbkbbbbkbbbbkbbbbkbbk....",
        ".kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk....",
        ".kbbbk...................kbbbk......",
        ".kbkbk...................kbkbk......",
        ".kbbbk...................kbbbk......",
        ".kbkbk...................kbkbk......",
        ".kkkkk...................kkkkk......"], 0, 16)
put(c, [".s.s", "s..s", ".s.."], 32, 13)
put(c, [".kkk.", "kbbbk", "kmmmk", "kbbbk", "kmmmk", "kbbbk", ".kkk."], 7, 28)
put(c, [".kkk.", "kbbbk", "kmmmk", "kbbbk", "kmmmk", "kbbbk", ".kkk."], 13, 28)
put(c, ["....kk....",
        "...kuuk...",
        "..kkkkkk..",
        ".kuukkuuk.",
        "kkkkkkkkkk",
        "kuukkuukku",
        "kkkkkkkkkk"], 19, 28)
put(c, ["kkkkk", "kbkbk", "kkbkk", "kbkbk", "kkbkk", "kbkbk", "kkkkk"], 31, 28)
HD["monument:Artillery Park"] = fin(c)

# Ministry of Military Strategy: hall with war-map window, keep with royal finial, banner tower
c = cv(36, 35)
gable(c, 7, 12, 7)
box(c, 0, 19, 15, 15, "t")
put(c, ["kkkkkkkkk",
        "kmeemmmek",
        "kemcmmeek",
        "kmeemcmmk",
        "kkkkkkkkk"], 3, 21)
put(c, ["c.....c", "c.....c", "c.....c"], 4, 27)
put(c, ["kkkk", "kddk", "kddk", "kddk", "kddk"], 6, 29)
put(c, ["....k....",
        "...kak...",
        "..kaaak..",
        ".kaaaaak.",
        "kkkkkkkkk"], 14, 0)
box(c, 14, 5, 9, 29, "t")
put(c, ["kkkkk", "kykyk", "kkkkk"], 16, 8)
put(c, ["kkk", "kyk", "kyk", "kkk"], 17, 14)
put(c, ["kkk", "kyk", "kyk", "kkk"], 17, 20)
put(c, ["kkkkk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk"], 16, 28)
put(c, ["k.k.k.k.k", "kkkkkkkkk"], 24, 6)
box(c, 24, 8, 9, 26, "t")
for y in (10, 18, 26):
    put(c, SLIT, 28, y)
put(c, ["ccc", "ccc", "ccc", "ccc", "c.c"], 25, 11)
put(c, ["ccc", "ccc", "ccc", "ccc", "c.c"], 30, 19)
put(c, ["kkk", "kdk", "kdk"], 27, 31)
HD["monument:Ministry of Military Strategy"] = fin(c)


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
# group: smithy — chimney smoke, shield on the wall, glowing forge door, anvil
c = cv()
house(c, 0, 12, 17, 11, chimney=12)
put(c, [".kkk.", "kcack", "kcack", ".kck.", "..k.."], 2, 13)
put(c, ["kkkkk", "kfffk", "kfyfk", "kfyfk", "kfffk"], 10, 17)
put(c, ANVIL, 17, 17)
HD["group:g_arms"] = fin(c)

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
HD["holding:Carpentry"] = fin(c)

# Fletchery: workshop, arrow sheaf in a barrel, straw target
c = cv()
house(c, 0, 12, 13, 11, door=8, wins=(1,))
put(c, ["s.s.s",
        ".mmm.",
        "..b..",
        ".kkk.",
        "kbbbk",
        "kmmmk",
        "kbbbk",
        ".kkk."], 13, 14)
put(c, [".kkkk.",
        "kssssk",
        "ksccsk",
        "kscysk",
        "ksccsk",
        "kssssk",
        ".kkkk.",
        ".b..b.",
        "b....b"], 18, 13)
HD["holding:Fletchery"] = fin(c)

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
HD["holding:Tannery"] = fin(c)

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
HD["holding:Joinery"] = fin(c)

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
HD["holding:Furnace"] = fin(c)

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
HD["holding:Blacksmith"] = fin(c)

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
HD["holding:Armory"] = fin(c)

# Master Workshop: forge wing with chimney, gabled hall with a great gear
c = cv()
put(c, [".y.", "y..", ".y."], 1, 2)
box(c, 1, 5, 3, 9, "u")
box(c, 0, 12, 12, 11, "u")
put(c, ["kkkk", "kffk", "kfyk", "kfyk", "kffk"], 3, 17)
house(c, 11, 11, 13, 12, door=16)
put(c, [".k.k.", "kmmmk", ".mkm.", "kmmmk", ".k.k."], 12, 12)
put(c, WIN, 19, 12)
HD["holding:Master Workshop"] = fin(c)

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
HD["holding:Gilded Foundry"] = fin(c)

# Stable: long timber stable, three stall doors with horse heads, hay bale
c = cv()
gable(c, 10, 3, 10)
box(c, 0, 13, 21, 10, "b")
for x0 in (1, 8, 15):
    put(c, ["kkkkk", "kdddk", "kdbbk", "kdbhk", "kkkkk", "kbkbk", "kkbkk", "kbkbk", "kkkkk"][:9], x0, 13)
put(c, ["kkkk", "kyyk", "kyyk"], 20, 20)
HD["holding:Stable"] = fin(c)

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
HD["holding:Forge"] = fin(c)

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
HD["holding:Tiltyard"] = fin(c)

# Court Armoury: stone hall, royal hangings, crest with crossed blades over the door, tall windows
c = cv()
house(c, 0, 10, 23, 13, wall="t", timber=False, door=10)
put(c, ["aa", "aa", "aa", "aa", "a."], 2, 12)
put(c, ["aa", "aa", "aa", "aa", "a."], 19, 12)
for o in (5, 10, 15):
    put(c, WINT, o, 11)
put(c, ["m...m", ".kak.", ".kak.", "m.k.m"], 9, 4)
HD["holding:Court Armoury"] = fin(c)

# Advanced Blast Furnace (36): stone stack, water-driven bellows wheel, tapping glow, ore cart
c = cv(36, 35)
put(c, [".s..s.", "s..s..", ".s..s.", "..s..."], 9, 0)
put(c, ["..kkkkkkk..",
        "..kuuuuuk..",
        "..kuuuuuk..",
        "..kuuuuuk..",
        "..kuuuuuk..",
        ".kuuuuuuuk.",
        ".kuuuuuuuk.",
        ".kuuuuuuuk.",
        "kuuuuuuuuuk",
        "kuuuuuuuuuk",
        "kuuuuuuuuuk"], 7, 4)
box(c, 2, 15, 22, 19, "t")
for y0 in range(17, 33, 3):
    for x0 in range(3, 23, 4):
        c[y0][x0 + (y0 % 2) * 2] = "u"
put(c, ["...kkkkkkk...",
        "..kkfffffkk..",
        ".kkfffffffkk.",
        ".kffffyffffk.",
        ".kfffyyyfffk.",
        ".kffyyyyyffk.",
        ".kfffyyyfffk.",
        ".kkkkkkkkkkk."], 6, 25)
put(c, ["....kkkkk....",
        "..kkbbbbbkk..",
        ".kbbk.k.kbbk.",
        ".kbkbbbbbkbk.",
        "kbb.kbkbk.bbk",
        "kbkbbbkbbbkbk",
        "kbb.kbkbk.bbk",
        ".kbkbbbbbkbk.",
        ".kbbk.k.kbbk.",
        "..kkbbbbbkk..",
        "....kkkkk...."], 23, 21)
put(c, ["kkkkkkkkkkkk", "keeeeeeeeeek", "keeeeeeeeeek", "kkkkkkkkkkkk"], 24, 30)
HD["monument:Advanced Blast Furnace"] = fin(c)


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
HD["group:g_commerce"] = fin(c)

# Alchemy: tower workshop with purple roof, alembic on a stand bubbling fumes, crates
c = cv()
house(c, 0, 10, 11, 13, roof="a", wall="t", timber=False, door=6)
put(c, WIN, 2, 11)
put(c, WIN, 2, 15)
put(c, [".l..e.", "..l.e.", ".l.e..", "..kk..", ".kllk.", "kllllk", "kllllk", ".kkkk.", "..bb..", ".kbbk.", "kb..bk"], 12, 9)
put(c, ["kkkk", "kemk", "kkkk", "keek"], 19, 15)
put(c, ["kkkkk", "kbkbk", "kkbkk", "kbkbk", "kkkkk"], 18, 18)
HD["holding:Alchemy"] = fin(c)

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
HD["holding:Weavery"] = fin(c)

# Jewelry Foundry: gilded-roof shop, gem sign, crucible furnace with chimney
c = cv()
house(c, 0, 12, 13, 11, roof="y", wall="t", timber=False, door=8)
put(c, [".kak.", "kaaak", ".kak.", "..k.."], 1, 14)
put(c, [".s.", "s..", "kk.", "uk.", "uk.", "uk."], 17, 9)
put(c, ["..kkkkk..", ".kuuuuuk.", "kuuuuuuuk", "kuukkkuuk", "kukfyfkuk", "kukfffkuk", "kuuuuuuuk", "kkkkkkkkk"], 14, 15)
HD["holding:Jewelry Foundry"] = fin(c)

# Market Square: two stalls flanking a stone market cross
c = cv()
stall(c, 0, 13, 10, "c", "s", "yfl")
stall(c, 14, 13, 10, "a", "s", "ysf")
put(c, ["..k..", ".kmk.", "..k..", "..k..", "..t..", "..t..", ".ktk.", ".ktk.", "kkkkk", "kttttk"[:5]], 9, 12)
HD["holding:Market Square"] = fin(c)

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
HD["holding:Spice Merchant"] = fin(c)

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
HD["holding:Harbor"] = fin(c)

# Merchant Quarter: three tall townhouses, stepped gables, shop windows
c = cv()
for x0, h0, col in ((0, 7, "w"), (8, 3, "w"), (16, 6, "w")):
    put(c, ["..kkk...", ".kkrkk..", ".krrrk..", "kkrrrkk.", "krrrrrk."], x0, h0)
    box(c, x0, h0 + 5, 7, 18 - h0, col)
    for yy in range(h0 + 6, 19, 4):
        put(c, WIN, x0 + 2, yy)
    put(c, ["kkkk", "kydk", "kydk", "kydk"][:4], x0 + 1, 19)
HD["holding:Merchant Quarter"] = fin(c)

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
HD["holding:Money Lending"] = fin(c)

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
HD["holding:Shipyard"] = fin(c)

# Courtyard: arcaded walls round a garden court with a fountain
c = cv()
put(c, ["kkkkkkkkkkkkkkkkkkkkkkkk", "krrrrrrrrrrrrrrrrrrrrrrk", "kkkkkkkkkkkkkkkkkkkkkkkk"], 0, 7)
box(c, 0, 10, 24, 13, "w")
for x0 in range(2, 22, 4):
    put(c, ["kk", "dd", "dd"], x0, 11)
hline(c, 1, 22, 14, "b")
for x0 in range(1, 23):
    c[15][x0] = "l" if x0 % 3 else "n"
put(c, ["..e..", ".kek.", "..t..", "kkkkk", "keeek", "kkkkk"], 9, 15)
for x0 in (2, 18):
    put(c, [".ll.", "llnl", ".lb.", "..b."], x0, 16)
hline(c, 1, 22, 21, "t")
HD["holding:Courtyard"] = fin(c)

# Artisan Workshop: workshop with hanging sign, potter's wheel and glazed vases
c = cv()
house(c, 0, 12, 13, 11, door=8, wins=(1,))
put(c, ["kkkk", ".kbk", ".kak"], 12, 13)
put(c, [".kk.", "kcck", "kcck", ".kk."], 14, 19)
put(c, [".k.", "kak", "kak", "kak", ".k."], 18, 18)
put(c, [".kk..", "kyyk.", ".kyyk", ".kkk."], 19, 19)
HD["holding:Artisan Workshop"] = fin(c)

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
HD["holding:Court Artists"] = fin(c)

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
HD["holding:Emporium"] = fin(c)


# ---------------------------------------------------------------- commerce monuments (36)
# Aristocratic Court: palatial manor, gilded cornices, central pavilion, banners
c = cv(36, 35)
put(c, ["k..", "kaa", "kaa", "k..", "k..", "k.."], 3, 3)
put(c, ["k..", "kaa", "kaa", "k..", "k..", "k.."], 31, 3)
for x0 in (2, 30):
    box(c, x0, 9, 4, 25, "w")
    put(c, ["kk", "yy"], x0 + 1, 9)
gable(c, 17, 6, 9)
put(c, ["kyk"], 16, 9)
box(c, 6, 15, 24, 19, "w")
hline(c, 6, 29, 15, "k")
for x in range(7, 29):
    c[16][x] = "y" if x % 2 else "r"
hline(c, 7, 28, 17, "k")
for row in (19, 25):
    for x0 in range(8, 28, 4):
        if x0 in (16,) and row == 25:
            continue
        put(c, WINT, x0, row)
put(c, ["kkkkkk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk"], 15, 28)
for x0 in (2, 30):
    for row in (12, 18, 24):
        put(c, ["kk", "ky"], x0 + 1, row)
hline(c, 0, 35, 34, "k")
HD["monument:Aristocratic Court"] = fin(c)

# Port Authority: customs tower with flag, counting hall, long quay with a moored ship
c = cv(36, 35)
water(c, 30)
put(c, ["k...", "kaa.", "kaa.", "k..."], 6, 0)
put(c, ["..kkk..", ".krrrk.", "krrrrrk", "kkkkkkk"], 3, 4)
box(c, 3, 8, 7, 22, "t")
put(c, WIN, 5, 10)
put(c, WINT, 5, 15)
put(c, WINT, 5, 21)
house(c, 9, 17, 13, 13, wall="w", door=5, wins=(1, 9))
put(c, ["kkkkkkkkkkkkkkkkkkkkkkk", "kbbbbbbbbbbbbbbbbbbbbbk", ".kb.....kb.....kb...kb."], 0, 29)
put(c, ["......k......",
        "......kcc....",
        "...kkkkkkk...",
        "...kssssssk..",
        "...kssssssk..",
        "...kssssssk..",
        "....kkkkkk...",
        "......k......",
        "......k......",
        "kk....k....kk",
        "kbkkkkkkkkkbk",
        ".kbbbbbbbbbk.",
        "..kkkkkkkkk.."], 23, 20)
HD["monument:Port Authority"] = fin(c)


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
HD["group:g_court"] = fin(c)

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
HD["holding:Inn"] = fin(c)

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
HD["holding:Jester's Court"] = fin(c)

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
HD["holding:Bell Tower"] = fin(c)

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
HD["holding:Embassy"] = fin(c)

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
HD["holding:Academy"] = fin(c)

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
HD["holding:University"] = fin(c)

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
HD["holding:Courier Network"] = fin(c)


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
HD["monument:Senate Hall"] = fin(c)

# Studium Generale: grand college, clock tower over the gate, long red-roofed ranges, quad arch
c = cv(36, 35)
put(c, ["...k...", "..kyk..", "..kyk..", ".krrrk.", "krrrrrk", "kkkkkkk"], 14, 0)
box(c, 14, 6, 8, 28, "t")
put(c, [".kkkk.", "kyyyyk", "kykkyk"[:6], "kyyyyk", ".kkkk."], 15, 8)
put(c, WINT, 16, 15)
put(c, ["kkkkkk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk"], 15, 26)
for x0, x1 in ((0, 14), (22, 36)):
    w = x1 - x0
    put(c, ["k" * w, "k" + "r" * (w - 2) + "k", "k" + "r" * (w - 2) + "k", "k" * w], x0, 12)
    box(c, x0, 16, w, 18, "w")
    for o in range(1, w - 3, 4):
        put(c, WINT, x0 + o, 18)
        put(c, WIN, x0 + o, 25)
    hline(c, x0 + 1, x1 - 2, 30, "b")
HD["monument:Studium Generale"] = fin(c)


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
HD["group:g_devotion"] = fin(c)

# Chandlery: shop with dipped-candle racks, great candle sign
c = cv()
house(c, 0, 12, 13, 11, door=8, wins=(1,))
put(c, ["k.k.k", "s.s.s", "s.s.s"], 2, 16)
put(c, ["..y..", "..f..", ".kkk.", ".kwk.", ".kwk.", ".kwk.", ".kwk.", ".kwk.", ".kwk.", ".kwk.", "kkkkk", "kbbbk", "kbbbk", "kkkkk"][::1], 14, 9)
put(c, [".y.y.", ".s.s.", ".s.s.", "kkkkk", "kbbbk"], 19, 18)
HD["holding:Chandlery"] = fin(c)

# Interrogation Chambers: squat dark keep, barred windows, iron-studded door, red lantern
c = cv()
put(c, ["k.k.k.k.k.k.k.k.k.", "kkkkkkkkkkkkkkkkkk"], 1, 7)
box(c, 1, 9, 18, 14, "u")
for x0 in (3, 13):
    put(c, ["kkkk", "kmdm"[:4], "kdmd"[:4], "kkkk"], x0, 11)
put(c, ["kkkkkk", "kmdmdk", "kdmdmk", "kmdmdk", "kdmdmk", "kmdmdk"], 7, 17)
put(c, ["kkk", "..k", "..k", ".kck", ".kck", "..k"], 19, 9)
HD["holding:Interrogation Chambers"] = fin(c)

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
HD["holding:Priory"] = fin(c)

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
HD["holding:Abbey"] = fin(c)

# Reliquary Sanctum (key: Reliquary): gilded shrine-house, open door showing a glowing casket, candles
c = cv()
put(c, CROSS, 10, 0)
gable(c, 11, 4, 9, "y")
box(c, 3, 13, 17, 10, "t")
put(c, ["kkkkkkk", "kdddddk", "kdyyydk", "kykkkyk", "kyyyyyk", "kdddddk", "kdddddk", "kdddddk", "kdddddk"], 8, 14)
for x0 in (4, 16):
    put(c, ["y", "s", "s", "k"], x0, 18)
HD["holding:Reliquary"] = fin(c)

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
HD["holding:Monastery"] = fin(c)

# Execution Dock: gallows on a pier over the water, noose, warning cage
c = cv()
water(c, 19)
put(c, ["kkkkkkkkkkkkkk",
        "bbbbbbbbbbbbbk",
        "bk.........m..",
        "b..........m..",
        "b..........m..",
        "b.........kmk.",
        "b.........m.m.",
        "b.........kmk.",
        "b.............",
        "b.............",
        "b.............",
        "b............."], 4, 3)
put(c, ["k.", "bk", "b.", "b."], 5, 4)
put(c, ["kkkkkkkkkkkkkkkkkkkkkk", "kbbbbbbbbbbbbbbbbbbbbk", ".kb....kb....kb....kb.", ".kb....kb....kb....kb.", ".kb....kb....kb....kb."], 1, 15)
put(c, [".kkk.", "kmkmk", "kmkmk", ".kkk.", "..k.."], 18, 10)
HD["holding:Execution Dock"] = fin(c)

# Hospitaller: hall with tall windows, black banner with a white cross
c = cv()
house(c, 0, 12, 15, 11, wall="t", timber=False, door=6)
for o in (2, 10):
    put(c, WINT, o, 13)
put(c, ["kkkkkkk", "bdddddd", "bddsddd", "bdssssd", "bddsddd", "bddsddd", "bdddddd", "b.ddd..", "b......", "b......", "b......", "b......", "b......", "b......", "b......", "b......", "b......", "kk....."], 16, 5)
HD["holding:Hospitaller"] = fin(c)

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
HD["holding:Episcopal Court"] = fin(c)

# Apothecary: shop with drying herbs under the eaves, jars in the window, mortar-and-pestle sign
c = cv()
house(c, 0, 12, 13, 11, door=8)
put(c, ["l.n.l.", "l.n.l.", "..n..."][:2], 2, 12)
put(c, ["kkkkk", "kekak", "kkkkk", "kclyk", "kkkkk"], 1, 15)
put(c, ["kkkkk", "....k", "..kkkk"[:6], ".kmmk.", ".kmmmk"[:6], "..kk.."], 12, 10)
put(c, ["l.l..", "lllll", ".kkk.", "kbbbk", "kbbbk", "kkkkk"], 18, 17)
HD["holding:Apothecary"] = fin(c)

# Infirmary: long ward with red cross over the door, row of lit windows, bench
c = cv()
gable(c, 11, 4, 11)
box(c, 0, 15, 23, 8, "w")
for o in (1, 5, 15, 19):
    put(c, WIN, o, 16)
put(c, ["..k..", ".kck.", "kcccck"[:5], ".kck.", "..k.."], 9, 8)
put(c, ["kkkkk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk"], 9, 17)
HD["holding:Infirmary"] = fin(c)

# Pilgrimage Site: grassy mound, tall stone cross, path of pilgrims' candles
c = cv()
put(c, ["...kkk...",
        "...ktk...",
        "kkkktkkkk",
        "kttttttttk"[:9],
        "kkkktkkkk",
        "...ktk...",
        "...ktk...",
        "...ktk...",
        "...ktk...",
        "...ktk...",
        "..kkkkk..",
        "..kuuuk.."], 7, 1)
for i, w in enumerate((8, 12, 16, 20, 24)):
    x0 = (24 - w) // 2
    for x in range(x0, x0 + w):
        c[13 + i * 2][x] = "k" if x in (x0, x0 + w - 1) else "l"
        c[14 + i * 2][x] = "k" if x in (x0, x0 + w - 1) else ("n" if (x + i) % 5 == 0 else "l")
for x0, y0 in ((5, 17), (17, 17), (3, 21), (19, 21)):
    put(c, ["y", "s"], x0, y0 - 1)
put(c, ["ss", "ss", "ss"], 13, 19)
HD["holding:Pilgrimage Site"] = fin(c)

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
HD["holding:Unforgotten Shrine"] = fin(c)


# ---------------------------------------------------------------- devotion monuments (36)
# Papal Palace: gilded dome with tiara finial, pillared front, twin bell turrets
c = cv(36, 35)
put(c, ["..k..", ".kyk.", "kyyyk", ".kyk.", "..k.."], 16, 0)
put(c, ["....kkkkk....", "..kkyyyyykk..", ".kyyyyyyyyyk.", "kyyyyyyyyyyyk", "kkkkkkkkkkkkk"], 12, 5)
box(c, 11, 10, 15, 6, "w")
for o in (13, 17, 21):
    put(c, WIN, o, 11)
hline(c, 4, 31, 16, "k")
hline(c, 4, 31, 17, "y")
box(c, 4, 18, 28, 16, "w")
for x0 in (6, 10, 23, 27):
    put(c, ["kk"] + ["tt"] * 13, x0, 19)
for o in (13, 20):
    put(c, WINT, o, 19)
put(c, ["kkkkkk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk", "kddddk"], 15, 27)
for x0 in (0, 31):
    put(c, ["..k..", ".kyk.", "kkkkk"], x0, 8)
    box(c, x0, 11, 5, 23, "w")
    put(c, ["kkk", "kyk", "kkk"], x0 + 1, 13)
    put(c, SLIT, x0 + 2, 20)
HD["monument:Papal Palace"] = fin(c)

# Inquisitorial Palace: dark gothic hall, crocketed spires, red banners, iron gate
c = cv(36, 35)
for x0, top in ((4, 5), (11, 1), (18, 0), (25, 1), (32, 5)):
    put(c, ["k"], x0, top)
    for y in range(top + 1, 14):
        hw = min(2, (y - top) // 3)
        for x in range(x0 - hw, x0 + hw + 1):
            c[y][x] = "k" if x in (x0 - hw, x0 + hw) else "u"
box(c, 2, 13, 33, 21, "u")
hline(c, 2, 34, 13, "k")
for x0 in (4, 31):
    put(c, ["cc", "cc", "cc", "cc", "cc", "cc", "c."], x0, 15)
for o in (8, 25):
    put(c, ["kkkk", "kdmk", "kmdk", "kdmk", "kkkk"], o, 15)
put(c, [".kkkkk.", "kdddddk", "kmdddmk", "kdmdmdk", "kddmddk", "kdmdmdk", "kmdddmk", "kdddddk", "kmdmdmk", "kdddddk"], 15, 24)
put(c, [".kkkkk.", "kcccck"[:0] + "kccccck", "kckkkck", "kccccck", ".kkkkk."], 15, 15)
HD["monument:Inquisitorial Palace"] = fin(c)

# Sacred Preceptory (key: Preceptory of the Knight's Templar): fortress house of the Oathsworn, oath-sword banner and blazon, crenellations
c = cv(36, 35)
put(c, ["k....", "kssms", "kskmk", "kssms", "kssms", "kssss", "k....", "k...."], 17, 0)
put(c, ["k.k.k.k.k", "kkkkkkkkk"], 13, 8)
box(c, 13, 10, 9, 24, "t")
put(c, ["kkkkk", "kcmck", "kmmmk", "kcmck", "kcmck", "kkkkk"], 15, 11)
put(c, ["kkkkk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk"], 15, 26)
for x0, x1 in ((0, 13), (22, 36)):
    put(c, ["".join("k" if (i % 2 == 0) else "." for i in range(x1 - x0)), "k" * (x1 - x0)], x0, 14)
    box(c, x0, 16, x1 - x0, 18, "t")
    for o in range(2, x1 - x0 - 3, 5):
        put(c, WIN, x0 + o, 18)
        put(c, SLIT, x0 + o + 1, 25)
for x0 in (0, 33):
    put(c, ["k.k", "kkk"], x0, 10)
    box(c, x0, 12, 3, 22, "t")
HD["monument:Preceptory of the Knight's Templar"] = fin(c)

# Eternal Sepulchre (key: Exalted Basilica): tomb-shrine on the pilgrims' mound, stone cross, glowing niche, candles
c = cv(36, 35)
put(c, ["...kkk...",
        "...ktk...",
        "kkkktkkkk",
        "ktttttttk",
        "kkkktkkkk",
        "...ktk...",
        "...ktk..."], 13, 0)
gable(c, 17, 7, 10, "t")
for j in range(9, 17, 2):
    for x in range(17 - (j - 7) + 1, 17 + (j - 7)):
        if (x + j) % 4 == 0:
            c[j][x] = "u"
box(c, 7, 17, 21, 10, "t")
put(c, [".kkkkk.", "kdyyydk", "kyyyyyk", "kyykyyk", "kyyyyyk", "kdyyydk", "kkkkkkk"], 14, 18)
for x0 in (9, 24):
    put(c, ["kkk", "kyk", "kkk"], x0, 19)
for i, w in enumerate((26, 30, 34, 36)):
    x0 = (36 - w) // 2
    for x in range(x0, x0 + w):
        c[27 + i * 2][x] = "k" if x in (x0, x0 + w - 1) else "l"
        c[28 + i * 2][x] = "k" if x in (x0, x0 + w - 1) else ("n" if (x + i) % 6 == 0 else "l")
for x0 in (6, 10, 25, 29):
    put(c, ["y", "s", "s"], x0, 25)
put(c, ["ss", "ss", "ss", "ss", "ss", "ss"], 17, 29)
HD["monument:Exalted Basilica"] = fin(c)
