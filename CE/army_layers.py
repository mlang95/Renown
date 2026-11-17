"""
army_layers.py — PROTOTYPE: layered army figures at 48x48 (art only, no mechanics; not wired into the board yet).

An army is drawn as a stack: back (carried secondary) -> body (retinue: silhouette, helm, stance)
-> armour (fills the body's torso / arm / leg regions) -> weapon (vertical, its grip on the fist)
-> shield (off hand) -> fists. One 48x48 canvas, art rows 0..46 + a ground row, sprites.py format.

Parts are authored as bare material (no outline); part() adds the black outline, so later parts get a line
where they overlap earlier ones. Template keys used only in bodies (the armour layer replaces them):
    '1' torso   '2' arm   '3' leg
Every other key is a sprites.py palette key ('p' / 'P' = owner colour, swapped per player).
Art follows what players read (NAME_DISPLAY): Estoc is drawn as a Falchion, Javelin as Throwing Axes,
Pilum as Throwing Spears; labels on the sheet use the display names too.

    python army_layers.py --sheet army_layers_sheet.png
"""
import argparse, math, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sprites as SP  # palette, shading

W, H = 48, 47            # art rows; ground row added on output
WX = 37                  # weapon shaft: columns WX, WX+1 (the weapon fist wraps them)
OFFX = 12                # off-hand shaft columns (second Florentine blade / Dagger)
GRIP = {"1h": 27, "2h": 33, "off": 33}     # row the weapon's grip row lands on (2h: the lower fist)


def blank(w=W, h=H):
    return [["."] * w for _ in range(h)]


def put(c, rows, x, y):
    for j, r in enumerate(rows):
        for i, ch in enumerate(r):
            yy, xx = y + j, x + i
            if ch != "." and 0 <= yy < len(c) and 0 <= xx < len(c[0]):
                c[yy][xx] = ch


def outline(rows):
    """Material pixels get a 'k' line in the empty cells around them (4-neighbour); the stamp grows 1 px each side."""
    w = max(len(r) for r in rows)
    g = [["."] * (w + 2)] + [["."] + list(r.ljust(w, ".")) + ["."] for r in rows] + [["."] * (w + 2)]
    out = [r[:] for r in g]
    for y in range(len(g)):
        for x in range(w + 2):
            if g[y][x] == "." and any(0 <= y + dy < len(g) and 0 <= x + dx < w + 2 and g[y + dy][x + dx] not in ".k"
                                      for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                out[y][x] = "k"
    return ["".join(r) for r in out]


def part(c, rows, x, y):
    """Paste an outlined part so its bare art lands at (x, y)."""
    put(c, outline(rows), x - 1, y - 1)


def raster(w, h, f):
    """Rows from a pixel function f(x, y) -> key or '.'."""
    return ["".join(f(x, y) for x in range(w)) for y in range(h)]


def thick_line(c, x0, y0, x1, y1, ch, r=2.0):
    """A limb as a bare-material stroke (outlined later by the caller's part())."""
    n = max(abs(x1 - x0), abs(y1 - y0)) * 2 + 1
    for i in range(n + 1):
        t = i / n
        cx, cy = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        for yy in range(int(cy - r), int(cy + r) + 1):
            for xx in range(int(cx - r), int(cx + r) + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r and 0 <= yy < len(c) and 0 <= xx < len(c[0]):
                    c[yy][xx] = ch


# ---------------------------------------------------------------- body: Warriors (key Man-at-Arms)
# Kettle helm with an owner-colour band, broad shoulders, square stance.
HELM = [
    "......smmmm.....",
    "....ssmmmmmMM...",
    "...smmmmmmmmMM..",
    "...smmmmmmmmmM..",
    "...pppppppppPP..",
    "mmmmmmmmmmmmmmMM",
    ".MMMMMMMMMMMMMM.",
]
FACE = [
    "hhhhhhhhjj",
    "hkkhhhkkjj",
    "hhkhhhkhjj",
    "hhhhhhhhhj",
    "hhhhjjhhjj",
    "hhhhhhhhjj",
    "hhhjjjjhjj",
    ".hhhhhhjj.",
    "..jjjjjj..",
]
TORSO = (["...111111111111...",
          ".1111111111111111."] +
         ["111111111111111111"] * 10 +
         [".1111111111111111.",
          ".bbbbbbbbyybbbbbb.",
          ".1111111111111111.",
          "..11111111111111.."])
LEGS = ["333333..333333"] * 8
BOOTS = [".dddddd..dddddd.", "ddddddd..ddddddd", "ddddddd..ddddddd"]
FIST = [".hhhj", "hhhhj", "hjhjj", "hhhhj", ".jjj."]
FIST_L = ["hhhh.", "hhhhj", "jhjhj", "hhhhj", ".jjj."]


def body_warriors(c, pose):
    part(c, LEGS, 17, 36)
    part(c, BOOTS, 16, 44)
    part(c, TORSO, 15, 20)
    part(c, ["jjjjjj", "jjjjjj"], 21, 19)                 # neck
    part(c, FACE, 19, 11)
    part(c, HELM, 16, 4)
    arm = blank()
    if pose == "1h":
        thick_line(arm, 13, 23, 12, 31, "2", 2.4)        # off arm hangs to the off fist
        thick_line(arm, 34, 23, 34, 27, "2", 2.4)        # weapon arm: upper arm down ...
        thick_line(arm, 34, 27, 36, 28, "2", 2.2)        # ... forearm forward to the fist
    elif pose == "bow":
        thick_line(arm, 13, 23, 7, 26, "2", 2.3)         # bow arm held out to the left
        thick_line(arm, 34, 23, 30, 28, "2", 2.4)        # draw arm: elbow out ...
        thick_line(arm, 30, 28, 27, 27, "2", 2.2)        # ... hand at the chest
    else:
        thick_line(arm, 34, 23, 36, 24, "2", 2.4)        # weapon arm: fist high on the shaft
        thick_line(arm, 13, 23, 14, 30, "2", 2.4)        # near arm: upper arm ...
        thick_line(arm, 14, 30, 35, 33, "2", 2.2)        # ... forearm across the body to the low fist
    part(c, ["".join(r) for r in arm], 0, 0)


def fists(c, pose, shield):
    if pose == "1h":
        part(c, FIST, 35, 25)
        if not shield:
            part(c, FIST_L, 10, 31)
    else:
        part(c, FIST, 35, 21)
        part(c, FIST, 35, 31)


# ---------------------------------------------------------------- armour (fills '1' torso, '2' arms, '3' legs)
def _cloth(ch, x, y):
    if ch == "3":
        return "B" if x in (22, 30) else "b"
    return "P" if x >= 30 or (ch == "1" and x in (21, 26) and y > 24) else "p"


def _gambeson(ch, x, y):
    if ch == "3":
        return "B" if x in (22, 30) else "b"
    return "Z" if (x + y) % 4 == 0 or (x - y) % 4 == 0 else "s"


def _leather(ch, x, y):
    if ch == "1":
        if y in (25, 29):
            return "B"
        return "y" if x % 4 == 1 and y in (23, 27, 31) else "b"
    if ch == "2":
        return "B" if y % 4 == 0 else "b"
    return "B" if y in (39, 40) else "b"


def _mail(ch, x, y):
    return "M" if (x + 2 * (y % 2)) % 4 in (0, 1) and y % 2 == 0 or (x % 2 == 0 and y % 2) else "m"


def _plate(ch, x, y):
    if ch == "1":
        if 18 <= x <= 19 and y <= 27:
            return "s"
        return "M" if y in (30, 34) else "m"
    if ch == "2":
        return "M" if y % 3 == 0 else "m"
    if y in (39, 40):
        return "s" if x in (18, 26) else "M"
    return "m"


def _gothic(ch, x, y):
    if ch == "1":
        if y <= 21 or y == 35:
            return "y"
        return "M" if x % 3 == 0 else ("s" if x % 3 == 1 and y < 28 else "m")
    if ch == "2":
        return "M" if x % 3 == 0 else "m"
    if y == 39:
        return "y"
    return "M" if x % 3 == 0 else "m"


ARMOURS = {"Cloth": _cloth, "Gambeson": _gambeson, "Leather": _leather,
           "Chainmail": _mail, "Full Plate": _plate, "Gothic Plate": _gothic}


def dress(c, armour):
    f = ARMOURS[armour]
    for y in range(H):
        for x in range(W):
            if c[y][x] in "123":
                c[y][x] = f(c[y][x], x, y)


# ---------------------------------------------------------------- weapons (bare art; shaft on columns sc, sc+1)
# name: (rows, sc, grip row index). 1H weapons grip on the weapon fist (row 27); 2H on the lower fist (row 33).
def shaft(n, sc=3, ch="bB"):
    return ["." * sc + ch] * n


WEAPONS = {
    "Farm Tools": ([
        "..smm...", ".smmmM..", ".smM.mM.", ".smM..mM", ".smM....", ".smM....", "..yY...."] + shaft(8, 2) + ["..BB...."], 2, 11),
    "Cudgel": ([
        "..bbbb..", ".bbbbBB.", "bbBbbbBb", "bbbbbBBB", ".bbBbbB.", "bbbbbBBB", ".bbbbBB.", "..bbbB..", "..bbBB.."]
        + shaft(18) + ["...BB..."], 3, 26),
    "Pitchfork": ([
        ".s.sm.s.", ".m.mM.m.", ".m.mM.m.", ".m.mM.m.", ".m.mM.m.", ".mmmmMm.", "...yY..."] + shaft(30), 3, 33),
    "Bill Hook": ([
        "....sm....", "....sM....", "....sM....", "....sM....", "....sM....", "....smMM..", "....smmMM.", "....smmmMM",
        "....smm.MM", "....smm..M", "MMmmsmm...", "....smm...", "....smM...", "....yY...."] + shaft(26, 4), 4, 33),
    "Daggers": ([
        "..sm..", ".smmM.", ".smmM.", ".smmM.", ".smmM.", ".smmM.", "mmmmmm", "..bB..", "..bB..", "..yY.."], 2, 7),
    "Short Sword": ([
        "....sm....", "...smmM...", "..smmmMM..", "..smmmMM..", "..smmmMM..", "..smmmMM..", "..smmmMM..", "..smmmMM..",
        "..smmmMM..", "...smmM...", ".mmmmmmmm.", "....bB....", "....bB....", "....bB....", "...yyYY..."], 4, 12),
    "Spears": ([
        "...sm...", "..smmM..", ".smmmMM.", ".smmmMM.", ".smmmMM.", "..smmM..", "...sM...", "...yY..."] + shaft(30), 3, 21),
    "Arming Sword": ([
        "....sm....", "...smmM..."] + ["...smmM..."] * 14 + [
        "mmmmmmmmmm", "MMMMMMMMMM", "....bB....", "....bB....", "....bB....", "....bB....", "...yyYY...", "....YY...."], 4, 19),
    "Flail": ([
        ".......m...", ".....m.m.m.", "......smM..", ".....smmmM.", "......mMM..", ".....m.M.m.", ".....M.....",
        "....M......", "...M.......", "..yY.......", "..bB.......", "..bB.......", "..bB.......", "..bB.......",
        "..bB.......", "..bB.......", "..bB.......", "..yY......."], 2, 14),
    "Halberd": ([
        "....sm.....", "....sM.....", "....sM.....", "....sM.....", "....sM.....", "....sm.MM..", "....smmmmM.",
        "MM..smmmmMM", ".MMmsmmmmMM", "..Mmsmmmmm.", "....smmmmM.", "....smMM...", "....yY....."] + shaft(27, 4), 4, 33),
    "Battle Axe": ([
        "...bB......", "...bBMM....", "...bBmmMM..", "...bBmmmMM.", "...bBmmmmMM", "...bBsmmmmM", "...bBsmmmmM",
        "...bBsmmmmM", "...bBmmmmMM", "...bBmmmMM.", "...bBmmMM..", "...bBMM...."] + shaft(20) + ["...BB......"], 3, 30),
    "Cavalry Spear": ([
        "...sm.....", "...smM....", "..smmM....", "..smmM....", "...sM.....", "...yY.....", "...bBppppp", "...bBpppp.",
        "...bBpp.pp"] + shaft(28), 3, 25),
    "Pike": ([
        "...sm...", "..smmM..", "..smmM..", "...sM...", "...yY..."] + shaft(42), 3, 33),
    "Morningstar": ([
        "...m....", ".m.sm.m.", "..smmM..", "ssmmmmMM", ".smmmMM.", "..mMMM..", ".m.MM.m."] + shaft(11) + ["...yY..."], 3, 14),
    "Bastard Sword": ([
        "....sm....", "...smmM..."] + ["...smmM..."] * 18 + [
        "mmmmmmmmmm", "MMMMMMMMMM", "....bB....", "....bB....", "....bB....", "....bB....", "....bB....", "....bB....",
        "...yyYY...", "....YY...."], 4, 24),
    "War Hammer": ([
        "....sm....", "....sM....", "....sM....", "....sM....", "MM..smMMMM", ".MMmsmmmmM", "..MmsmmmmM", "....smMMMM",
        "....sm....", "....yY...."] + shaft(24, 4), 4, 30),
    "Lance": ([
        "....sm....", "....sM....", "....bB....", "....pP....", "....bB....", "....pP....", "....bB....", "...ppPP...",
        "...bbBB...", "...ppPP...", "...bbBB...", "..pppPPP..", "..bbbBBB..", "..pppPPP..", ".smmmmmmM.", "smmmmmmmMM",
        "MMMMMMMMMM", "....bB....", "....bB....", "....bB....", "....bB....", "....bB....", "....pP...."], 4, 19),
    "Estoc": ([                      # drawn as a Falchion (NAME_DISPLAY)
        "......ss..", ".....smMM.", "...smmmmM.", "...smmmmM.", "...smmmmM.", "...smmmmM.", "...smmmmM.", "...smmmmM.",
        "...smmmM..", "...smmM...", "...smmM...", "...smmM...", "...smmM...", "...smmM...", ".mmmmmmmm.", "....bB....",
        "....bB....", "....bB....", "...yyYY..."], 4, 16),
    "Poleaxe": ([
        "....sm.....", "....sM.....", "....sM.....", "....sM.....", "....sM.....", "MMMmsmmmM..", "MmmmsmmmmM.",
        "MmmmsmmmmMM", "MMMmsmmmmM.", "....smmmM..", "....sm.....", "....yY.....", "....yY....."] + shaft(26, 4), 4, 33),
}
TWO_HANDED = {"Cudgel", "Pitchfork", "Bill Hook", "Halberd", "Battle Axe", "Pike", "War Hammer", "Poleaxe"}


def wield(c, name, pose):
    rows, sc, gi = WEAPONS[name]
    part(c, rows, WX - sc, GRIP[pose] - gi)


def wield_off(c, name):
    rows, sc, gi = WEAPONS[name]
    part(c, rows, OFFX - sc, GRIP["off"] - gi)


# ---------------------------------------------------------------- shields (off hand; owner-colour field)
def _disc(r, rim, face, boss, studs=False):
    n = int(2 * r) + 1
    c0 = (n - 1) / 2

    def f(x, y):
        d = math.hypot(x - c0, y - c0)
        if d > r:
            return "."
        if d > r - 1.2:
            return rim
        if d < 1.6:
            return boss
        if studs and abs(d - r * .6) < .5 and (x + y) % 3 == 0:
            return "y"
        return face if x - c0 < r * .45 else ("P" if face == "p" else face)
    return raster(n, n, f)


def _kite(w=12, h=22):
    def f(x, y):
        cx = (w - 1) / 2
        half = w / 2 if y < h * .45 else w / 2 * (1 - (y - h * .45) / (h * .55))
        if y < 2:                                   # rounded top
            half -= (2 - y) * 1.2
        if abs(x - cx) > half:
            return "."
        if abs(x - cx) > half - 1.1 or y == 0:
            return "m"
        if abs(x - cx) < 1 and 3 <= y <= h - 5 or abs(y - 8) < 1 and abs(x - cx) < 3.5:
            return "y"                              # cross
        return "P" if x > cx + 1 else "p"
    return raster(w, h, f)


def _tower(w=14, h=25):
    def f(x, y):
        if x in (0, w - 1) or y in (0, h - 1):
            return "b"
        if x in (1, w - 2) or y in (1, h - 2):
            return "B"
        if x in (w // 2 - 1, w // 2) or y == 9:
            return "y"
        return "P" if x > w // 2 + 2 else "p"
    return raster(w, h, f)


def _heater(w=14, h=17):
    def f(x, y):
        cx = (w - 1) / 2
        half = w / 2 if y < 8 else w / 2 * math.sqrt(max(0.0, 1 - ((y - 8) / (h - 8)) ** 2))
        if abs(x - cx) > half:
            return "."
        if abs(x - cx) > half - 1.1 or y == 0:
            return "m"
        if x - cx > 0 and y < 8:                     # per pale: owner colour / gold quarters
            return "y" if y % 4 < 2 else "p"
        return "P" if x > cx + 2 else "p"
    return raster(w, h, f)


SHIELDS = {          # name: (rows, x, y) — bare art placed over the off fist (about x 10..14, y 31..35)
    "Buckler Shield": (_disc(4.6, "m", "p", "y"), 7, 28),
    "Targe Shield":   (_disc(7.6, "b", "p", "y", studs=True), 4, 25),
    "Kite Shield":    (_kite(), 6, 22),
    "Tower Shield":   (_tower(), 5, 20),
    "Heater Shield":  (_heater(), 5, 23),
}


def strap_shield(c, name):
    rows, x, y = SHIELDS[name]
    part(c, rows, x, y)


# ---------------------------------------------------------------- carried secondary (behind the left shoulder)
def bow(h, d, string=True):
    rows = []
    for y in range(h):
        x = d - round(d * math.sin(math.pi * y / (h - 1)))
        r = ["."] * (d + 3)
        r[x] = "b"
        if 0 < x < d:
            r[x + 1] = "B"
        if string:
            r[d + 2] = "s"
        rows.append("".join(r))
    return rows


BACK_X, BACK_Y = 13, 2       # column the stamp's centre / shaft lands on
BACK = {     # name: (bare rows, centre column)
    "Hunting Bow": (bow(26, 5), 6),
    "Longbow":     (bow(38, 5), 6),
    "Crossbow":    (["bbbbbbbbbbbbb", "Bs.........sB", ".s.........s.", "..s.......s..", "...s.yy..s...", "....smmms....",
                     "......bB.....", "......bB.....", "......bB.....", "......bB.....", "......bB.....", "......bB.....",
                     ".....bbBB....", ".....bbBB...."], 6),
    "Javelin":     (["smM...smM", "smMb..smMb", "MM.b..MM.b", "...b.....b", "...b.....b", "...b.....b", "...b.....b",
                     "...b.....b", "...b.....b"], 5),                          # shown as Throwing Axes
    "Pilum":       (["sM....sM", "sM....sM", ".m.....m", ".m.....m", ".m.....m", ".m.....m", ".M.....M", ".b.....b",
                     ".b.....b", ".b.....b", ".b.....b", ".b.....b", ".b.....b", ".b.....b"], 4),   # Throwing Spears
    "Arquebus":    (["sm", "sm", "sm", "sm", "sm", "sm", "sm", "sm", "sm", "sm", "sm", "yY", "bB", "bBB", "bBBB", "bbBBB",
                     "bbBBB"], 1),
}


def carry(c, name):
    if name in BACK:
        rows, cx = BACK[name]
        part(c, rows, BACK_X - cx, BACK_Y)
    else:                                   # Guige Strap: a 2H weapon carried on the back
        rows, sc, gi = WEAPONS[name]
        part(c, rows, BACK_X - sc, 0)


# ---------------------------------------------------------------- ranged weapon Equipped (aiming pose)
# Bows: held out in the off hand, string drawn to the chest. Crossbow / Arquebus: upright in both fists (2h pose).
# Throwing weapons (Javelin = Throwing Axe, Pilum = Throwing Spear): raised in the weapon fist (1h pose; Shield kept).
BOW_MID_Y, BOW_X, DRAW_HAND = 26, 4, (26, 27)
HELD = {   # name: (pose, rows, sc, gi) — sc / gi as WEAPONS; bows: (pose, h, d)
    "Hunting Bow": ("bow", 26, 5),
    "Longbow":     ("bow", 38, 5),
    "Crossbow":    ("2h", ["bbbbbbbbbbbbb", "Bs.........sB", ".s.........s.", "..s.......s..", "...s.yy..s...",
                           "....smmms....", "......bB.....", "......bB.....", "......bB.....", "......bB.....",
                           "......bB.....", "......bB.....", "......bB.....", "......bB.....", "......bB.....",
                           "......bB.....", ".....bbBB....", ".....bbBB....", ".....bbBB...."], 6, 16),
    "Arquebus":    ("2h", ["sm"] * 20 + ["yY", "bB", "bB", "bBB", "bBBB", "bbBBB", "bbBBB", "bbBBB"], 0, 23),
    "Javelin":     ("1h", ["smM.", "smMb", "MM.b"] + ["...b"] * 9 + ["...B"], 3, 9),
    "Pilum":       ("1h", [".sm.", "smmM", ".mM.", ".mM.", ".mM.", ".mM.", ".mM.", ".MM."] + [".bB."] * 18, 1, 15),
}


def _seg(c, x0, y0, x1, y1, ch):
    n = max(abs(x1 - x0), abs(y1 - y0))
    for i in range(n + 1):
        x, y = round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n)
        if 0 <= y < H and 0 <= x < W:
            c[y][x] = ch


def aim(c, name):
    spec = HELD[name]
    if spec[0] == "bow":
        _, h, d = spec
        top = BOW_MID_Y - h // 2
        part(c, bow(h, d, string=False), BOW_X, top)
        part(c, FIST_L, BOW_X - 2, BOW_MID_Y - 2)
        hx, hy = DRAW_HAND
        _seg(c, BOW_X + d, top, hx, hy, "s")              # the drawn string
        _seg(c, BOW_X + d, top + h - 1, hx, hy, "s")
        part(c, ["hhhj", "hhhj", "jjj."], hx - 1, hy - 1)
    else:
        pose, rows, sc, gi = spec
        part(c, rows, WX - sc, GRIP[pose] - gi)


# ---------------------------------------------------------------- compose
def compose(armour="Cloth", weapon="Arming Sword", shield=None, back=None, florentine=False, ranged=None):
    """ranged: the Ranged Weapon Equipped this Skirmish (aiming pose); the melee weapon is then carried on the back."""
    if ranged:
        pose = HELD[ranged][0]
        back = weapon if weapon not in (None, "Farm Tools") else back
    else:
        pose = "2h" if weapon in TWO_HANDED else "1h"
    c = blank()
    if back:
        carry(c, back)
    body_warriors(c, pose)
    dress(c, armour)
    if ranged:
        aim(c, ranged)
        if pose == "1h":
            fists(c, pose, bool(shield))
            if shield:
                strap_shield(c, shield)
        elif pose == "2h":
            fists(c, pose, False)
        return SP.shade_rim(["".join(r) for r in c] + ["g" * W])
    wield(c, weapon, pose)
    two_blades = pose == "1h" and (florentine or weapon == "Daggers")
    if two_blades:
        wield_off(c, weapon)
    fists(c, pose, shield and not two_blades and pose == "1h")
    if pose == "1h" and shield and not two_blades:
        strap_shield(c, shield)
    rows = ["".join(r) for r in c] + ["g" * W]
    return SP.shade_rim(rows)


# ---------------------------------------------------------------- contact sheet (PNG)
def _display():
    """NAME_DISPLAY from the data: labels say what players read (Estoc -> Falchion, Man-at-Arms -> Warriors)."""
    try:
        import renown_data_d10 as rd
        return lambda n: rd.NAME_DISPLAY.get(n, n)
    except Exception:
        return lambda n: n


def sheet(path, owner="#2f6fd0", scale=3):
    from PIL import Image, ImageDraw
    dn = _display()
    pal = dict(SP.PALETTES["scene"])
    pal["p"] = owner
    pal["P"] = SP._mix(owner, "#000000", .35)
    pal["q"] = SP._mix(owner, "#ffffff", .4)
    R = dn("Man-at-Arms")
    sections = [
        (f"{R} · Weapons (Chainmail; 1H weapons with a Kite Shield)",
         [(dn(w), compose("Chainmail", w, "Kite Shield")) for w in WEAPONS]),
        (f"{R} · Armour (Arming Sword + Heater Shield, then Halberd)",
         [(dn(a), compose(a, "Arming Sword", "Heater Shield")) for a in ARMOURS] +
         [(dn(a) + " 2H", compose(a, "Halberd")) for a in ARMOURS]),
        (f"{R} · Shields (Full Plate, Morningstar) and Florentine",
         [(dn(x), compose("Full Plate", "Morningstar", x)) for x in SHIELDS] +
         [("Florentine", compose("Full Plate", "Arming Sword", florentine=True))]),
        (f"{R} · Secondary carried on the back (Leather, Short Sword + Buckler; Guige: Kite Shield)",
         [("Ranger: " + dn(x), compose("Leather", "Short Sword", "Buckler Shield", back=x)) for x in BACK] +
         [("Guige: " + dn(x), compose("Gambeson", "Arming Sword", "Kite Shield", back=x)) for x in ("Halberd", "Battle Axe")]),
        (f"{R} · Ranged Weapon Equipped (Leather; the melee weapon goes on the back)",
         [(dn(x), compose("Leather", "Short Sword", "Buckler Shield", ranged=x)) for x in HELD] +
         [(dn(x) + " · Gothic", compose("Gothic Plate", "Bastard Sword", None, ranged=x)) for x in ("Longbow", "Arquebus")]),
    ]
    cols = 8
    cell_w, cell_h, lab_h = W * scale + 16, (H + 1) * scale + 8, 14
    rows_n = sum((len(items) + cols - 1) // cols for _, items in sections)
    img = Image.new("RGB", (cols * cell_w + 16, rows_n * (cell_h + lab_h + 4) + len(sections) * 26 + 16), "#14161a")
    d = ImageDraw.Draw(img)
    y = 8
    for title, items in sections:
        d.text((8, y), title, fill="#c8ccd2")
        y += 18
        for i, (lab, spr) in enumerate(items):
            if i and i % cols == 0:
                y += cell_h + lab_h + 4
            x0 = 8 + (i % cols) * cell_w
            d.rectangle([x0, y, x0 + W * scale + 7, y + (H + 1) * scale + 7], fill="#2a2e36")
            for yy, r in enumerate(spr[:-1]):
                for xx, ch in enumerate(r):
                    if ch != ".":
                        d.rectangle([x0 + 4 + xx * scale, y + 4 + yy * scale,
                                     x0 + 4 + (xx + 1) * scale - 1, y + 4 + (yy + 1) * scale - 1], fill=pal.get(ch, "#ff00ff"))
            d.text((x0, y + (H + 1) * scale + 8), lab[:24], fill="#9aa0a8")
        y += cell_h + lab_h + 12
    img.save(path)
    return path


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet", default="army_layers_sheet.png")
    a = ap.parse_args()
    print("wrote", sheet(a.sheet))
