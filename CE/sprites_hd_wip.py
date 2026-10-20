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
