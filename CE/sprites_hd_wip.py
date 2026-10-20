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

# Castle Yard (Coliseum): keep tower, curtain wall with arcade, yard with a pell and banner
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

# Ordnance Yard (Artillery Park): hooped bombard with flared muzzle on a timber bed, kegs, shot pyramid
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
put(c, ["kkk", "kyk", "kyk"][:3], 22, 20) if False else None
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
