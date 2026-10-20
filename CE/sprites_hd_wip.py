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


# group: barn with braced doors, hay bale
c = cv()
gable(c, 9, 3, 9)
box(c, 0, 12, 19, 11, "b")
put(c, ["kkkkkkk", "kbkbkbk", "kkbbbkk", "kbkbkbk"][:1], 6, 13)
put(c, ["kkkkkkk", "kbbkbbk", "kbkbkbk", "kkbbbkk", "kbkbkbk", "kbbkbbk", "kbbkbbk", "kbbkbbk"][:8], 6, 14)
put(c, ["kkk", "kyk", "kkk"], 8, 8)
put(c, HAY, 18, 18)
HD["group:g_husbandry"] = fin(c)

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
HD["holding:Herb Garden"] = fin(c)

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
HD["holding:Animal Husbandry"] = fin(c)

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
HD["holding:Saddlery"] = fin(c)

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
HD["holding:Vineyard"] = fin(c)

# Orchard: two apple trees, ladder, basket of apples
c = cv()
tree(c, 0, 8, "c")
tree(c, 11, 8, "c")
put(c, ["k.k", "kkk", "k.k", "kkk", "k.k", "kkk", "k.k"], 9, 16)
put(c, [".c.c.", "kckck", "kbbbk", "kbbbk", ".kkk."], 19, 18)
HD["holding:Orchard"] = fin(c)

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
HD["holding:Bakery"] = fin(c)

# Meadery: cottage, row of straw skeps on a bench, mead barrel
c = cv()
house(c, 0, 12, 13, 11, door=8, wins=(1,))
for x0 in (13, 17):
    put(c, SKEP, x0, 13)
put(c, ["kkkkkkkk", "b......b", "b......b", "b......b", "b......b"], 13, 18)
put(c, BARREL, 21, 16)
HD["holding:Meadery"] = fin(c)

# Winery: cellar house with arched door, barrels stacked on racks, grapes on the eave
c = cv()
house(c, 0, 12, 15, 11, wall="t", timber=False, door=6)
put(c, ["lalal", "laall", ".lal."], 1, 12)
put(c, WIN, 11, 13)
put(c, BARREL, 15, 9)
put(c, BARREL, 15, 16)
put(c, BARREL, 19, 16)
put(c, ["kkkkkkkkk"], 15, 15)
HD["holding:Winery"] = fin(c)

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
HD["holding:Cidery"] = fin(c)

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
HD["holding:Mill"] = fin(c)


# ---------------------------------------------------------------- husbandry monument (36)
# Manor House: hall with gabled cross-wings, chimneys, porch, hedged garden and gate
c = cv(36, 35)
for x0 in (11, 23):
    put(c, [".s.", "s..", "kk.", "uk.", "uk."], x0, 5)
gable(c, 5, 9, 5)
gable(c, 30, 9, 5)
put(c, ["k" * 20, "k" + "r" * 18 + "k", "k" + "r" * 18 + "k", "k" + "r" * 18 + "k", "k" * 20], 8, 10)
box(c, 0, 14, 11, 16, "w")
box(c, 25, 14, 11, 16, "w")
box(c, 10, 15, 16, 15, "w")
for x0 in (0, 25):
    for xx in (x0 + 3, x0 + 7):
        vline(c, xx, 15, 28, "b")
    hline(c, x0 + 1, x0 + 9, 20, "b")
    put(c, WIN2, x0 + 4, 16)
    put(c, WIN2, x0 + 4, 22)
for o in (11, 21):
    put(c, WIN2, o, 17)
put(c, [".kkkkk.", "kkrrrkk", "kdddddk"[:0] + ".kdddk.", ".kdddk.", ".kdddk.", ".kdddk.", ".kdddk.", ".kdddk."], 15, 21)
for x0 in (1, 24):
    put(c, ["kkkkkkkkkkk", "knnnnnnnnnk", "knnnnnnnnnk", "kkkkkkkkkkk"], x0, 30)
put(c, ["kmk", ".m.", "kmk"], 13, 31)
put(c, ["kmk", ".m.", "kmk"], 20, 31)
for y in range(30, 34):
    for x in range(14, 22):
        if c[y][x] == ".":
            c[y][x] = "t"
HD["monument:Manor House"] = fin(c)


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
HD["group:g_secrecy"] = fin(c)

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
HD["holding:Toll House"] = fin(c)

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
HD["holding:Secret Cellar"] = fin(c)

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
HD["holding:Smuggler's Nook"] = fin(c)

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
HD["holding:Syndicate Hub"] = fin(c)

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
HD["holding:Black Market"] = fin(c)

# Forgery Workshop: cottage, screw press with sheets, wax seal, drying pages
c = cv()
house(c, 0, 12, 13, 11, door=8, wins=(1,))
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
put(c, [".cc.", "cyyc", ".cc.", "kkkk"][:3], 20, 19)
put(c, ["kkkk"], 20, 22)
HD["holding:Forgery Workshop"] = fin(c)

# Toxicarium: glasshouse with a blue glazed roof, poison plants, warning skull, vials
c = cv()
gable(c, 11, 4, 9, "e")
for i in range(2, 9, 2):
    for x in range(11 - i + 1, 11 + i):
        if (x - 11) % 3 == 0:
            c[4 + i][x] = "k"
box(c, 2, 13, 19, 10, "d")
for x in (5, 8, 11, 14, 17):
    vline(c, x, 14, 21, "k")
for x0, a in ((3, "c"), (6, "a"), (9, "l"), (12, "c"), (15, "a"), (18, "l")):
    put(c, [a + ".", "ll", ".l", "ll"], x0, 17)
hline(c, 3, 19, 21, "b")
put(c, SKULL, 20, 18)
HD["holding:Toxicarium"] = fin(c)

# Charnel House: stone bone-house, skull over the door, bone stack against the wall
c = cv()
house(c, 0, 12, 15, 11, wall="t", timber=False)
put(c, SKULL, 5, 12)
put(c, ["kkkkk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk"][:6], 5, 17)
put(c, ["..k.k..", ".ksksk.", "kskskskk"[:7], "ksssssk", "kskskskk"[:7], "ksssssk", "kkkkkkk"], 15, 16)
put(c, [".kkk.", "ksssk", "kdsdk", ".kkk."], 16, 12)
HD["holding:Charnel House"] = fin(c)

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
HD["holding:Beacon Towers"] = fin(c)

# Forgotten Catacombs: ivy-hung arch sunk in a grassy mound, steps into the dark
c = cv()
put(c, ["......kkkkkkkkkk........",
        "....kklllllllllllkk.....",
        "...klllkkkkkkkklllllk...",
        "..kllkkttttttttkklllllk.",
        "..klkttkkkkkkkkttklllllk",
        ".kllkttkddddddkttklllllk",
        ".kllktkddddddddktklllllk",
        "kllllktkddddddddkkllllnk",
        "klnllktkdkkkkkkdktklllllk"[:24],
        "kllllktkddkkkkddktklllnk"[:24],
        "kllllktkdddkkdddktklllk."[:24],
        "kllllktkkkkkkkkkktkllllk"[:24]], 0, 10)
put(c, ["l", "l", "l"], 9, 15)
put(c, ["l", "l"], 15, 15)
HD["holding:Forgotten Catacombs"] = fin(c)

# Cipher Chamber: narrow stone tower, cipher wheel blazon, lit study, scroll rack
c = cv()
put(c, ["k.k.k.k.k", "kkkkkkkkk"], 6, 1)
box(c, 6, 3, 9, 20, "t")
put(c, ["..kkkkk..", ".kyykyyk.", "kykkykkyk", "kyykyyyyk"[:9], "kykkykkyk", ".kyykyyk.", "..kkkkk.."][::1], 6, 4)
put(c, WIN, 9, 12)
put(c, ["kkk", "kdk", "kdk", "kdk", "kdk"], 9, 18)
put(c, ["kkkkkkk", "kskskok"[:5] + "sk", "kkkkkkk", "kskskok"[:5] + "sk", "kkkkkkk", "kb...bk", "kb...bk"], 16, 16)
HD["holding:Cipher Chamber"] = fin(c)


# ---------------------------------------------------------------- secrecy monuments (36)
# Plague Pit: open lime pit of bones, warning post with red cloth, body cart, crows
c = cv(36, 35)
put(c, ["k.k......k.k", ".k........k."], 6, 10)
put(c, ["kkkkkkkkk", "kcccccccck"[:9], "kcccccccck"[:9], "kkkkkkkkk", "....b....", "....b....", "....b....", "....b....", "....b....", "....b....", "....b....", "....b....", "...kbk..."], 3, 16)
put(c, ["......kkkkkkkkkkkkkkkkkk......",
        "....kksssssssssssssssssskk....",
        "..kkssskssdsskssssdssksssskk..",
        ".kssksssskssssdsskssssksssssk.",
        "kuuuuuuuuuuuuuuuuuuuuuuuuuuuuk",
        "kuddddddddddddddddddddddddddduk"[:30],
        "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkk"], 3, 28)
put(c, ["kkkkkkkk", "kbbbbbbk", "kbksskbk"[:8], "kkkkkkkk"], 26, 23)
put(c, WHEEL5, 28, 27)
HD["monument:Plague Pit"] = fin(c)

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
HD["monument:Thieves' Guild"] = fin(c)

# Outlaw Rookery: timber huts on stilts among bare trees, rope bridges, crows
c = cv(36, 35)
put(c, ["k.k.....k.k", ".k.......k."], 12, 0)
for x0, y0 in ((1, 12), (13, 6), (25, 12)):
    gable(c, x0 + 5, y0, 5, "b")
    box(c, x0, y0 + 5, 11, 6, "b")
    put(c, ["kkk", "kyk", "kkk"], x0 + 4, y0 + 6)
    for x in (x0 + 2, x0 + 8):
        vline(c, x, y0 + 11, 33, "b")
        c[33][x - 1] = "k"; c[33][x + 1] = "k"
    for yy in range(y0 + 13, 33, 4):
        hline(c, x0 + 3, x0 + 7, yy, "b")
for x in range(11, 14):
    c[18][x] = "b"
for x in range(23, 26):
    c[18][x] = "b"
HD["monument:Outlaw Rookery"] = fin(c)

# Whispering Undercroft: half-sunk vaulted crypt, ribbed arches, small chapel cap, lit grilles
c = cv(36, 35)
put(c, [".k.", "kkk", ".k."], 16, 4)
gable(c, 17, 7, 6, "u")
box(c, 11, 13, 13, 8, "t")
put(c, WINT, 16, 15)
put(c, ["kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk",
        "kuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuk",
        "kukkkkkuukkkkkuukkkkkuukkkkkuukkkk"[:34],
        "kukdddkuukdddkuukdddkuukdddkuukddk"[:34],
        "kukdydkuukdddkuukdddkuukdddkuukydk"[:34],
        "kukdddkuukdddkuukdddkuukdydkuukddk"[:34],
        "kukkkkkuukkkkkuukkkkkuukkkkkuukkkk"[:34],
        "kuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuk",
        "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk"], 1, 21)
for x in range(0, 36):
    for y in (30, 31, 32, 33):
        if c[y][x] == ".":
            c[y][x] = "l" if (x + y) % 4 else "n"
    c[30][x] = "k" if c[30][x] in "ln" else c[30][x]
put(c, ["kkkkkk", "kddddk", "kdkkdk", "kddddk"], 15, 30)
HD["monument:Whispering Undercroft"] = fin(c)

# Outrider Intercept Post: stilted timber watchtower, ladder, signal flag, tethered horse, fence
c = cv(36, 35)
put(c, ["k...", "kcc.", "kcc.", "k..."], 15, 0)
gable(c, 15, 4, 7, "b")
box(c, 8, 11, 15, 6, "b")
put(c, ["kkkkkkkkkkkkk", "kdydddddddydk", "kkkkkkkkkkkkk"], 9, 12)
for x in (9, 21):
    vline(c, x, 17, 33, "b")
for yy in range(19, 33, 3):
    hline(c, 13, 17, yy, "b")
vline(c, 13, 17, 33, "k")
vline(c, 17, 17, 33, "k")
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
        ".kk....kk....."], 22, 21)
fence(c, 0, 7, 30)
HD["monument:Outrider Intercept Post"] = fin(c)


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
HD["group:g_works"] = fin(c)

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
HD["holding:Masonry"] = fin(c)

# Workyard: log stack, sawpit trestle with a two-man saw, A-frame hoist
c = cv()
put(c, ["....kk....",
        "....kb....",
        "...kmkk...",
        "...b..b...",
        "..b....b..",
        "..b..m.b..",
        ".b...m..b.",
        ".bbbbubbb.",
        "b........b",
        "b........b",
        "b........b",
        "b........b",
        "b........b",
        "k........k"], 14, 9)
put(c, [".kk.kk.kk.",
        "kbbkbbkbbk",
        "kbkkbkkbkk",
        ".kkbkkbkk.",
        "..kbbkbbk.",
        "..kbkkbkk.",
        "...kk.kk..",
        "kkkkkkkkkk"][:7], 0, 16)
put(c, ["kbkkbkkbk."], 0, 22)
put(c, ["kkkkkkk", "bb...bb"], 10, 19)
HD["holding:Workyard"] = fin(c)

# Storehouse: big gabled warehouse, loft door with hoist, braced doors, sacks and crates
c = cv()
gable(c, 11, 1, 11)
put(c, ["kkkk", "kddk", "kkkk"], 10, 6)
box(c, 0, 12, 23, 11, "b")
put(c, ["kkkkkkkkk", "kbkbbbkbk", "kkbkbkbkk", "kbbkbkbbk", "kbbbkbbbk", "kbbkbkbbk", "kkbkbkbkk", "kbkbbbkbk", "kbkbbbkbk"], 7, 14)
put(c, SACK, 1, 19)
put(c, CRATE, 17, 18)
HD["holding:Storehouse"] = fin(c)

# Census Hall: civic hall, ledger board over the door, clerk's lit window, scroll rolls
c = cv()
house(c, 0, 10, 19, 13, wall="t", timber=False, door=8)
put(c, ["kkkkkkkkk", "kswswswsk"[:9], "kssssssk"[:0] + "kswswswsk", "kkkkkkkkk"], 5, 12)
put(c, WIN2, 1, 15)
put(c, WIN2, 14, 15)
put(c, [".kk..", "kssk.", "kssk.", "kkkkk", "kskssk"[:5], "kkkkk"], 19, 17)
HD["holding:Census Hall"] = fin(c)

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
HD["holding:Granary"] = fin(c)

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
HD["holding:Supply Depot"] = fin(c)

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
HD["holding:Trade Guild"] = fin(c)

# College of Engineering: hall with a great gear blazon in the gable, arch model on a trestle
c = cv()
gable(c, 8, 1, 8)
put(c, [".k.k.", "kmmmk", ".mkm.", "kmmmk", ".k.k."], 6, 4)
box(c, 0, 9, 17, 14, "t")
for o in (1, 13):
    put(c, WINT, o, 11)
put(c, ["kkkkk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk"], 6, 16)
put(c, [".kkkk.", "kttttk", "kt..tk", "kt..tk", "kkkkkkk"[:6], "kb..bk", "kb..bk", "kb..bk"], 17, 15)
HD["holding:College of Engineering"] = fin(c)

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
HD["holding:Masons' Guild"] = fin(c)

# Burgages: three narrow plot-houses, gable end to the street, garden strips behind
c = cv()
for x0, col in ((0, "w"), (8, "t"), (16, "w")):
    gable(c, x0 + 3, 6, 3)
    box(c, x0, 9, 7, 14, col)
    put(c, WIN, x0 + 2, 10)
    put(c, ["kkk", "kdk", "kdk", "kdk", "kdk"], x0 + 2, 18)
    put(c, ["k" if x0 != 16 else "k"], x0 + 7, 22)
for x in (7, 15):
    put(c, [".", "l", "n", "l", "b", "b"][1:], x, 17)
HD["holding:Burgages"] = fin(c)

# Citadel: white-stone stepped fortress, inner keep, banner
c = cv()
put(c, ["k...", "kcc.", "kc..", "k..."], 12, 0)
put(c, ["k.k.k.k", "kkkkkkk"], 9, 4)
box(c, 9, 6, 7, 5, "s")
put(c, SLIT, 12, 7)
put(c, ["k.k.k.k.k.k.k.k", "kkkkkkkkkkkkkkk"], 5, 10)
box(c, 5, 12, 15, 4, "s")
for o in (7, 12, 17):
    c[13][o] = "k"; c[14][o] = "k"
put(c, ["k.k.k.k.k.k.k.k.k.k.k.k.", "kkkkkkkkkkkkkkkkkkkkkkkk"], 0, 15)
box(c, 0, 17, 24, 6, "s")
put(c, ["kkkk", "kddk", "kddk", "kddk", "kddk"], 10, 18)
for o in (3, 19):
    put(c, SLIT, o, 18)
HD["holding:Citadel"] = fin(c)

# Castle Hall: great hall with tall windows, round stair tower with banner, porch
c = cv()
gable(c, 7, 6, 7)
box(c, 0, 13, 15, 10, "t")
for o in (2, 10):
    put(c, WINT, o, 14)
put(c, ["kkkkk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk"], 5, 17)
put(c, ["k...", "kcc.", "kcc.", "k..."], 19, 0)
put(c, ["..kkkk..", ".krrrrk.", "krrrrrrk", "kkkkkkkk"], 15, 3)
box(c, 15, 7, 8, 16, "t")
for y0 in (9, 14):
    put(c, SLIT, 18, y0)
put(c, ["kkk", "kdk", "kdk", "kdk"], 17, 19)
HD["holding:Castle Hall"] = fin(c)


# ---------------------------------------------------------------- works monuments (36)
# Office of Works: stone tower rising in scaffolding, treadwheel crane lifting a block, plans table
c = cv(36, 35)
box(c, 10, 10, 15, 24, "t")
for y0 in range(12, 34, 3):
    for x0 in range(11, 24, 3):
        c[y0][x0 + (y0 % 2)] = "u"
put(c, ["k.k.k.k.k.k.k.k", "kkkkkkkkkkkkkkk"], 10, 8)
put(c, ["kkkkk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk"], 15, 27)
for x in (8, 26):
    vline(c, x, 6, 33, "b")
for yy in (6, 13, 20, 27):
    hline(c, 7, 27, yy, "b")
for yy in (6, 13, 20, 27):
    for x in range(7, 28, 3):
        c[yy + 1][x] = "b" if c[yy + 1][x] == "." else c[yy + 1][x]
c[5][8] = "k"; c[5][26] = "k"
treadwheel(c, 24, 12)
put(c, ["kkkkkk", "kswssk", "kkkkkk", ".kb.kb"[:0] + "kb..bk", "kb..bk"], 0, 29)
HD["monument:Office of Works"] = fin(c)

# Imperial Palace: gilded central dome with crown, colonnaded wings, corner pavilions, purple banners
c = cv(36, 35)
put(c, [".y.y.y.", ".yyyyy.", "..kyk.."], 14, 0)
put(c, ["....kkkkk....", "..kkyyyyykk..", ".kyyyyyyyyyk.", "kyyyyyyyyyyyk", "kkkkkkkkkkkkk"], 11, 3)
box(c, 11, 8, 13, 8, "w")
for o in (13, 17, 21):
    put(c, WINT, o, 9)
for x0 in (1, 30):
    put(c, ["k..", "kaa", "kaa", "kay", "k..", "k.."], x0 + 2, 2)
    put(c, ["..k..", ".kyk.", "kyyyk", "kkkkk"], x0, 8)
    box(c, x0, 12, 5, 22, "w")
    for y0 in (14, 20, 26):
        put(c, ["kkk", "kyk", "kkk"], x0 + 1, y0)
hline(c, 5, 30, 15, "k")
hline(c, 5, 30, 16, "y")
hline(c, 5, 30, 17, "k")
box(c, 5, 17, 26, 17, "w")
for x0 in (6, 9, 12, 22, 25, 28):
    put(c, ["kk"] + ["tt"] * 15, x0, 18)
put(c, ["kkkkkkkk", "kddddddk", "kddyyddk", "kddddddk", "kddddddk", "kddddddk", "kddddddk", "kddddddk"], 14, 26)
for o in (15, 19):
    put(c, WIN, o, 20)
HD["monument:Imperial Palace"] = fin(c)


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
HD["group:g_raw"] = fin(c)

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
HD["holding:Quarry"] = fin(c)

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
HD["holding:Salt Works"] = fin(c)

# Apiary: three box hives on a stand, bees, flowering meadow
c = cv()
put(c, ["y.....y......y....", "...y......y.....y."], 3, 6)
for x0 in (1, 9, 17):
    put(c, [".kkkkk.", "krrrrrk", "kkkkkkk", "kbbbbbk", "kbkkkbk", "kbbbbbk", "kbbdbbk", "kkkkkkk"], x0, 11)
put(c, ["kkkkkkkkkkkkkkkkkkkkkkkk", ".kb...kb.......kb...kb.", ".kb...kb.......kb...kb.", ]  , 0, 19)
for x in range(24):
    c[22][x] = "l" if x % 3 else ("a" if x % 2 else "y")
HD["holding:Apiary"] = fin(c)

# Peat Bog: reeds, stacked cut peat, bog water, spade
c = cv()
for x0 in (0, 3, 19, 22):
    put(c, ["l.", "l.", "ll", ".l", ".l", "ll", ".l"], x0, 13)
put(c, ["..kkkk..", ".kbbbbk.", "kkkkkkkk", "kbbkbbbk", "kkkkkkkk", "kbbbkbbk", "kkkkkkkk"], 7, 13)
put(c, ["k", "b", "b", "b", "m", "m"], 16, 14)
put(c, ["kkkkkkkkkkkkkkkkkkkkkkkk", "kddeddeddddeddddeddeddek", "deeddeeddeeddeeddeeddeed"], 0, 20)
HD["holding:Peat Bog"] = fin(c)

# Forestry: two firs, forester's log pile, axe in a stump
c = cv()
pine(c, 0, 3, 20)
pine(c, 13, 1, 22)
put(c, [".kk.kk.", "kbbkbbk", "kbkkbkk", ".kkbkk.", "kbbkbbk", "kbkkbkk", "kkkkkkk"], 8, 16)
HD["holding:Forestry"] = fin(c)

# Fishmongery: quayside shop, fish strung under the eave, creel, water
c = cv()
water(c, 21)
house(c, 1, 11, 13, 9, door=8, wins=(1,))
put(c, ["kkkkkkkk", "k.k.k.k.", "e.e.e.e.", "eee.eee."[:0] + "e.e.e.e.", "s.s.s.s."], 14, 11)
put(c, ["kkkkkkkkkkkkkkkkkkkkkkkk", "kbbbbbbbbbbbbbbbbbbbbbbk"], 0, 19)
put(c, [".kkkk.", "kbebek", "kbbbbk", "kkkkkk"], 16, 15)
HD["holding:Fishmongery"] = fin(c)

# Mine: hill with a timbered entrance, rails, ore cart, pick
c = cv()
mound(c, 0, 7, 20, 16, "u", "t")
put(c, ["kkkkkkkkk", "kbbbbbbbk", "kbkkkkkbk", "kbkdddkbk", "kbkdddkbk", "kbkdddkbk", "kbkdddkbk", "kkkdddkkk"], 3, 15)
put(c, ["kkkkkkk", "kumyumk", "kkkkkkk", ".kmk.kmk"[:7]], 14, 18)
put(c, ["kkkkkkkkkkkkkkkkkkkkkkkk"], 0, 22)
put(c, ["m.", "mm", ".b", ".b"], 22, 18)
HD["holding:Mine"] = fin(c)

# Arable Land: ploughed strips with three wheat stooks
c = cv()
for x0 in (1, 9, 17):
    put(c, ["...y...", "..yyy..", "..yyy..", ".yykyy.", ".yyyyy.", "yykyyky", "yyyyyyy", "ybykyby"], x0, 11)
for x in range(24):
    c[19][x] = "b"
    c[20][x] = "y" if x % 2 else "b"
    c[21][x] = "b"
    c[22][x] = "k" if x % 3 == 0 else "b"
HD["holding:Arable Land"] = fin(c)

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
HD["holding:Common Land"] = fin(c)


# ---------------------------------------------------------------- feet strips (30 wide; ground row skipped)
def strip(rows):
    w = 30
    rows = [r.ljust(w, ".")[:w] for r in rows]
    return rows + ["g" * w]


HD["feet:Quarry"] = strip(["..kk..............kkk.........",
                           ".kttk..kk........kttuk...kk.k.",
                           "kttutkkttk.....kktttttk.kttktk",
                           "kttttkkttuk...kttuttttkkttkttk"])
HD["feet:Salt Works"] = strip(["..k.......................k...",
                               ".ksk.......k.............ksk..",
                               "ksssk.eeeeskeeeseeeeesee.ksssk",
                               "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkk"])
HD["feet:Apiary"] = strip(["..y.......y.........y.....y...",
                           ".l.a..l.y....a..l.....a..l...l",
                           "lllallllallllllallllyllllallll",
                           "llllllllllllllllllllllllllllll"])
HD["feet:Peat Bog"] = strip([".l.l..................l..l.l..",
                             ".l.l...kkk........kkk.l..l.l..",
                             "dllddeekbbkddeeddkbbkdeelddeed",
                             "deeddeeddeeddeeddeeddeeddeedde"])
HD["feet:Forestry"] = strip(["..kkkk..................kkkk..",
                             ".kbbbbk...l.......l....kbbbbk.",
                             "kbkbbkbk.lll.....lll..kbkbbkbk",
                             "kkkkkkkk..b.......b...kkkkkkkk"])
HD["feet:Fishmongery"] = strip([".kk.......................kk..",
                                "kmbk.....................kbmk.",
                                "kbbkeeeeeeseeeeeeeeseeeeekbbk.",
                                "kkkkeeeeeeeeeeeeeeeeeeeeekkkk."])
HD["feet:Mine"] = strip(["..tt.........ttt.........tt...",
                         ".tuut..m.m..tuyut.......tuut..",
                         "tuuutkkkkkktuuuuut.m.m.tuuuut.",
                         "kkkkkkkkkkkkkkkkkkkkkkkkkkkkkk"])
HD["feet:Arable Land"] = strip(["y.y.y...................y.y.y.",
                                "yyyyy...................yyyyy.",
                                "bybyb.bbbbbbbbbbbbbbbbb.bybyb.",
                                "bbbbbbybybybybybybybybybbbbbbb"])
HD["feet:Common Land"] = strip([".kkk...................kkk....",
                                "ksssk.....l..l..l.....ksssk...",
                                "kssssk..l..l..l..l...kssssk...",
                                ".k.k.....................k.k.."])

# ---------------------------------------------------------------- scenery
c = cv()
pine(c, 0, 3, 20)
pine(c, 11, 8, 15)
HD["scenery:tree"] = fin(c)

c = cv()
put(c, ["kkkkkkkkkk", "kbbbbbbbbk", "kbsssssbbk"[:10], "kkkkkkkkkk", "....kbk...", "....kbk...", "....kbk...", "....kbk...", "....kbk..."], 7, 14)
put(c, ["k", "b", "b"], 1, 20)
put(c, ["k", "b", "b"], 22, 20)
HD["scenery:plot"] = fin(c)


# ================================================================ BATCH 10: settlement tiers (fallback), wonders
# tier:<name> — 24x24 fallback when a skyline piece is missing
c = cv()
gable(c, 7, 9, 6, "b")
box(c, 1, 15, 13, 8, "w")
put(c, WIN, 3, 16)
put(c, ["kkk", "kdk", "kdk", "kdk", "kdk"], 8, 17)
fence(c, 15, 23, 19)
HD["tier:Hamlet"] = fin(c)

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
HD["tier:Village"] = fin(c)

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
HD["tier:Town"] = fin(c)

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
HD["tier:City"] = fin(c)

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
HD["tier:Metropolis"] = fin(c)


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
HD["wonder:Colossus"] = fin(c)

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
HD["wonder:The Grand Exchange"] = fin(c)

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
HD["wonder:The Eternal Sepulchre"] = fin(c)

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
HD["wonder:High Chancery"] = fin(c)


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
HD["sky:core:Hamlet"] = fin(c)

c = sky(15, 28)
cypress(c, 6, 0, 22)
fence(c, 0, 14, 22)
c[22][7] = "l"
for y in range(23, 27):
    c[y][7] = "b"
HD["sky:fill:Hamlet"] = fin(c)

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
HD["sky:core:Village"] = fin(c)

c = sky(15, 28)
gable(c, 7, 0, 7)
box(c, 1, 7, 13, 20, "w")
put(c, WIN, 3, 10)
put(c, WIN, 9, 10)
put(c, WIN, 3, 16)
put(c, ["kkk", "kdk", "kdk", "kdk", "kdk", "kdk"], 7, 21)
HD["sky:fill:Village"] = fin(c)

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
HD["sky:core:Town"] = fin(c)

c = sky(15, 21)
gable(c, 7, 0, 6)
box(c, 1, 6, 13, 14, "w")
put(c, WIN, 3, 8)
put(c, WIN, 9, 8)
put(c, ["kkk", "kdk", "kdk", "kdk", "kdk"], 6, 15)
HD["sky:fill:Town"] = fin(c)

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
HD["sky:core:City"] = fin(c)

c = sky(12, 26)
put(c, ["....kk....", "...krrk...", "..krrrrk.."], 1, 0)
box(c, 1, 3, 10, 22, "w")
for y0 in (5, 12):
    put(c, WIN, 4, y0)
put(c, ["kkk", "kdk", "kdk", "kdk", "kdk"], 4, 19)
HD["sky:fill:City"] = fin(c)

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
HD["sky:core:Metropolis"] = fin(c)

c = sky(12, 30)
put(c, ["......k.....", "......k.....", ".....kkk....", "....krrk....", "...krrrrk..."], 0, 0)
box(c, 2, 5, 9, 24, "w")
for y0 in (8, 16):
    put(c, WIN, 4, y0)
put(c, ["kkk", "kdk", "kdk", "kdk", "kdk"], 4, 23)
HD["sky:fill:Metropolis"] = fin(c)


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
HD["inf:Town Hall"] = fin(c)

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
HD["inf:Cathedral"] = fin(c)

c = sky(18, 27)
put(c, ["..y..", ".yyy.", "..y..", "..k..", ".kkk."], 6, 0)
gable2(c, 8, 4, 7)
box(c, 1, 12, 16, 14, "t")
for o in (4, 12):
    put(c, WINT, o, 14)
put(c, ["kkkk", "kddk", "kddk", "kddk", "kddk", "kddk"], 7, 20)
HD["inf:Chapel"] = fin(c)

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
HD["inf:Magistrate's Hall"] = fin(c)

c = sky(18, 25)
put(c, ["..kkkkk..", ".keeeeek.", "keeeeeeek", "kkkkkkkkk"], 4, 0)
box(c, 4, 4, 9, 20, "t")
for y0 in (6, 12):
    put(c, ["kkkkk", "kyyyk", "kyyyk", "kkkkk"][:4], 6, y0)
    for x in (7, 9):
        c[y0 + 1][x] = "k"; c[y0 + 2][x] = "k"
put(c, ["kkk", "kdk", "kdk", "kdk", "kdk"], 7, 19)
HD["inf:Library"] = fin(c)

c = sky(9, 37)
put(c, ["...kcc..", "...kc...", "...k....", "k.k.k.k.k"[:9]], 0, 0)
put(c, ["kkkkkkkkk"], 0, 4)
box(c, 0, 5, 9, 31, "t")
for y0 in (8, 17, 26):
    put(c, SLIT, 4, y0)
put(c, ["kkk", "kdk", "kdk"], 3, 33)
HD["inf:Garrison"] = fin(c)

c = sky(15, 37)
put(c, ["......kccc", "......kcc.", "......k..."], 0, 0)
put(c, ["k.kk.kk.kk.kk.k", "kkkkkkkkkkkkkkk"], 0, 3)
box(c, 0, 5, 15, 31, "t")
put(c, ["kkkk", "kddk", "kddk", "kkkk"], 6, 8)
for o in (2, 10):
    put(c, WINT, o, 16)
put(c, SLIT, 7, 22)
put(c, ["kkkkk", "kdddk", "kdddk", "kdddk", "kdddk", "kdddk"], 5, 30)
HD["inf:Keep"] = fin(c)

c = sky(6, 34)
put(c, ["kcccc", "kcccc", "kccc.", "kcc..", "kc..."], 0, 0)
for y in range(5, 33):
    c[y][0] = "k"
HD["inf:Muster Field"] = fin(c)

HD["inf:Wooden Walls"] = art(["k..k..", "kb.kb.", "bbbbbb", "bbbbbb", "kkkkkk", "bbbbbb", "bkbbkb", "bbbbbb", "bbbbbb", "kkkkkk", "bbbbbb"], 6, 12)
HD["inf:Stone Walls"] = art(["kk..kk", "kk..kk", "kkkkkk", "tttttt", "tutttt", "kkkkkk", "tttutt", "tttttt", "kkkkkk", "tuttt t".replace(" ", "t")[:6], "tttttt", "tttttt"], 6, 13)
HD["inf:Stone Walls:tower"] = art(["k.kk.kk.k",
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
HD["inf:Hitching Post"] = art(["kkkkkkkk", "bbbbbbbb", "b..m...b", "b..m...b", "b.kmk..b", "b......b", "b......b", "b......b"], 8, 9)

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
HD["inf:Road Wardens"] = fin(c)

HD["inf:Bridges"] = art(["kkkkkkkkkkkkkkkkkkkkk",
                         "ktttttttttttttttttttk",
                         "ktuttttttttttttttuttk",
                         "ktttkkkkkkkkkkkkktttk",
                         "kttk.............kttk",
                         "ktk...............ktk",
                         "kk.................kk",
                         "k...................k"], 21, 9)
HD["inf:Aqueducts"] = art(["kkkkkkkkkkkk",
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
