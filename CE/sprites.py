"""
sprites.py — pixel sprites for the settlement board scene (skins: farmstead, blackletter, scene).

Art only. No mechanics. Which sprite a thing gets is decided by the data file:
    Holding        -> its own sprite, else its group     (16x16, "holding:<name>" / "group:<g_key>")
    Raw Material   -> also a terrain strip at the feet    (20x4, "feet:<name>") of the ward's frontmost holding
    Monument       -> its own sprite, else its group     (24x24, "monument:<name>")
    Wonder         -> its own sprite                     (24x24, "wonder:<name>")
    Settlement     -> a skyline behind its holdings: "sky:core:<tier>" centred, "sky:fill:<tier>" tiled
                      across the lot (fallback 16x16 "tier:<tier>")
    Infrastructure -> skyline pieces "inf:<name>", placed per SKYLINE; INFRA_SUPERSEDES hides the replaced one

Format: each sprite is a list of equal-length strings, one char per pixel.
'.' is transparent; every other char is a palette key (KEYS). The last row is ground ('g'),
which the scene renderer skips so every building stands on one ground line.
_s() only pads (top rows and right edge); it never truncates, so oversize art fails --check.

    python sprites.py --data ../renown_data_d10.py --check
    python sprites.py --data ../renown_data_d10.py --sheet sprites_sheet.html
"""
import argparse, json, os, sys

SPRITE_VERSION = "0.4"

KEYS = {
    "k": "outline", "w": "plaster wall", "t": "stone", "u": "dark stone", "r": "roof",
    "d": "door / shadow", "y": "lit window / gold", "f": "fire", "s": "pale (smoke, canvas, bone)",
    "m": "metal", "b": "wood", "l": "leaf (seasonal)", "n": "evergreen needles", "c": "red cloth", "a": "royal cloth", "e": "water",
    "g": "ground (skipped in scene)",
}

PALETTES = {
    "farmstead":   {"k": "#3b2414", "w": "#f0d8a8", "t": "#b8b0a0", "u": "#7a7068", "r": "#b8432f", "d": "#4a2a16",
                    "y": "#ffd84a", "f": "#ff8a2a", "s": "#ece6da", "m": "#8a8f9a", "b": "#9a6a32", "l": "#5a9a32",
                    "c": "#c8302a", "a": "#4a5ab8", "e": "#4a8ad8", "n": "#2f6a2a", "g": "#5a8a2e"},
    "blackletter": {"k": "#0a0807", "w": "#9a8e7c", "t": "#8a8070", "u": "#4a423a", "r": "#6b2a2a", "d": "#1a1410",
                    "y": "#d8b45a", "f": "#e0602a", "s": "#c8bca8", "m": "#a0a0a8", "b": "#6b4a2a", "l": "#4a6a2a",
                    "c": "#9a2020", "a": "#3a3a7a", "e": "#3a5a7a", "n": "#2a4428", "g": "#2c2521"},
    "scene":       {"k": "#0e1220", "w": "#e8d8b0", "t": "#a8a0a0", "u": "#605a68", "r": "#a03a3a", "d": "#2a1f30",
                    "y": "#ffd27a", "f": "#ff9a3a", "s": "#e8e4dc", "m": "#8a96b0", "b": "#8a5a3a", "l": "#3a7a2a",
                    "c": "#c83a3a", "a": "#5a4ab0", "e": "#3a7ac8", "n": "#24563a", "g": "#2f4a2a"},
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


S16, S24 = 16, 24
SPRITES = {}

# ---------------------------------------------------------------- settlement tiers (16)
SPRITES["tier:Hamlet"] = _s([
    ".....kkkk.......",
    "....kbbbbk......",
    "...kbbbbbbk.....",
    "..kbbbbbbbbk....",
    "..kkkkkkkkkk....",
    "...kwwkdkwk.....",
    "...kwwkdkwk..k.k",
    "...kwwkdkwk.kkkk",
    "...kkkkkkkk..k.k",
], S16)
SPRITES["tier:Village"] = _s([
    "..........kkk...",
    ".........krrrk..",
    "...kkk..krrrrrk.",
    "..krrrk.kkkkkkk.",
    ".krrrrrk.kwykwk.",
    ".kkkkkkk.kwwwwk.",
    "..kwykk..kwdwwk.",
    "..kwwdk..kwdwwk.",
    "..kkkkk..kkkkkk.",
], S16)
SPRITES["tier:Town"] = _s([
    "..k.k......k.k..",
    "..kkk......kkk..",
    "..ktk......ktk..",
    "..ktkkkkkkkktk..",
    "..kttttttttttk..",
    "..kttkttttkttk..",
    "..kttttttttttk..",
    ".kkkkkkkkkkkkkk.",
    ".kttttttttttttk.",
    ".ktykttttttkytk.",
    ".kttttkddkttttk.",
    ".kttttkddkttttk.",
    ".kttttkddkttttk.",
    ".kkkkkkkkkkkkkk.",
], S16)
SPRITES["tier:City"] = _s([
    ".k.k....",
    ".kkk...k",
    ".ktk..kc",
    ".ktk..kr",
    ".ktk.krr",
    ".ktkkrrr",
    ".ktkkkkk",
    ".ktkktty",
    "kkkkkttt",
    "kttttttt",
    "ktuttktt",
    "kttttkdd",
    "kttttkdd",
    "kkkkkkkk",
], S16, mirror=True)
SPRITES["tier:Metropolis"] = _s([
    ".......k",
    "......kk",
    ".......k",
    "k.k...ky",
    "kkk...ky",
    "ktk..krr",
    "ktk.krrr",
    "ktkkrrrr",
    "ktkkkkkk",
    "ktkkwwww",
    "kkkkwyky",
    "ktttkwww",
    "ktytkwkd",
    "ktttkwkd",
    "kkkkkkkk",
], S16, mirror=True)

# ---------------------------------------------------------------- holding groups (16)
SPRITES["group:g_arms"] = _s([            # smithy: chimney smoke, shield on wall, forge door, anvil
    "...........ss...",
    "..........s.....",
    "..........kk....",
    "....kkkkkkkkk...",
    "...krrrrrrrrrk..",
    "..krrrrrrrrrrrk.",
    ".krrrrrrrrrrrrrk",
    "..kwwwwwwwwwwwk.",
    "..kwkmmkwwkkkwk.",
    "..kwkmmkwwkffwk.",
    "..kwwkkwwwkffwk.",
    "..kwwwwwwwkffwk.",
    "kmmkwwwwwwkffwk.",
    ".kk.kkkkkkkkkkk.",
], S16)
SPRITES["group:g_logistics"] = _s([       # covered wagon
    "....kkkkkkk.....",
    "...kssssssk.....",
    "..kssssssssk....",
    "..kssssssssk....",
    "..kssssssssk....",
    ".kbbbbbbbbbbk...",
    ".kbbbbbbbbbbkkk.",
    "..kkkkkkkkkk..kk",
    "..kmk....kmk....",
    ".kmbmk..kmbmk...",
    "..kmk....kmk....",
], S16)
SPRITES["group:g_works"] = _s([           # crane over a workshop
    "kkkkkkkkk.......",
    ".k.k....m.......",
    "..kk....m.......",
    "...k...kmk......",
    "...k...kbk......",
    "...k............",
    "...k..kkkkkkkk..",
    "...k.krrrrrrrrk.",
    "...kkrrrrrrrrrrk",
    "...kkwwwwwwwwwk.",
    "...kkwkkwwwkkwk.",
    "...kkwkykwwkdwk.",
    "..kkkwkkwwwkdwk.",
    "..kbkkkkkkkkkkk.",
    "..kkk...........",
], S16)
SPRITES["group:g_commerce"] = _s([        # market stall, striped awning, goods
    "..kkkkkkkkkkkk..",
    ".kcscscscscscsk.",
    "kcscscscscscscsk",
    "kkkkkkkkkkkkkkkk",
    ".kb..........bk.",
    ".kb..........bk.",
    ".kb.yy.ff.ll.bk.",
    ".kbkkkkkkkkkkbk.",
    ".kbbbbbbbbbbbbk.",
    ".kbkkkkkkkkkkbk.",
    ".kbk........kbk.",
    ".kkk........kkk.",
], S16)
SPRITES["group:g_devotion"] = _s([        # chapel with steeple and cross
    ".......k",
    "......kk",
    ".......k",
    "......kt",
    "......kt",
    ".....krr",
    "....krrr",
    "...krrrr",
    "..krrrrr",
    ".krrrrrr",
    "..kwwwww",
    "..kwykkd",
    "..kwykkd",
    "..kwwwkd",
    "..kkkkkk",
], S16, mirror=True)
SPRITES["group:g_court"] = _s([           # hall with banners
    "..k.....",
    "..kaa...",
    "..kaa...",
    "..k.....",
    ".kkk....",
    ".ktk.kkk",
    ".ktkkrrr",
    ".ktkrrrr",
    "kkkkkkkk",
    "kttttttt",
    "ktykttyt",
    "ktttttkd",
    "ktykttkd",
    "ktttttkd",
    "kkkkkkkk",
], S16, mirror=True)
SPRITES["group:g_secrecy"] = _s([         # shuttered dark house, lantern post
    "....kkkkk.......",
    "...kuuuuuk......",
    "..kuuuuuuuk.....",
    ".kkkkkkkkkkk....",
    "..kuuuuuuuk.....",
    "..kudkuuuuk.....",
    "..kudkuukyk..k..",
    "..kuuuuuuuk.kyk.",
    "..kuuuuuuuk..k..",
    "..kuukddkuk..k..",
    "..kuukddkuk..k..",
    "..kuukddkuk..k..",
    "..kkkkkkkkk.kkk.",
], S16)
SPRITES["group:g_husbandry"] = _s([       # barn and hay bale
    "......kk........",
    ".....krrk.......",
    "....krrrrk......",
    "...krrrrrrk.....",
    "..krrrrrrrrk....",
    ".krrrrrrrrrrk...",
    "..kwwwwwwwwk....",
    "..kwkbbbbkwk....",
    "..kwkbkkbkwk..k.",
    "..kwkbbbbkwk.kyk",
    "..kwkbkkbkwkkyyy",
    "..kwkbbbbkwkkyyy",
    "..kkkkkkkkkkkkkk",
], S16)
SPRITES["group:g_raw"] = _s([             # timbered mine entrance in a rock mound
    "......kkkk......",
    "....kkttttkk....",
    "...kttuttttk....",
    "..kttttttuttk...",
    ".kttuttbbbbttk..",
    ".kttttbkddkbttk.",
    "kttttbkdddkbuttk",
    "ktuttbkdddkbtttk",
    "kttttbkdddkbtttk",
    "kkkkkkkkkkkkkkkk",
], S16)


# ---------------------------------------------------------------- batch 1: raw materials (16) + terrain backdrops (32x20)
SPRITES["holding:Quarry"] = _s([
    "....kkkkkkk.....", "...kttttttuk....", "..kttuttttttk...", "..ktkkkkkkktk...", "..ktktttttktk...",
    ".kkkkkkkkkkkkk..", ".kttttktttttttk.", ".kttttkttuttttk.", ".kkkkkkkkkkkkkk.", "...kttk..kttk...",
    "...kttk..kttkm..", "...kkkk..kkkkmb.",
], S16)
SPRITES["holding:Salt Works"] = _s([
    "........kkk.....", ".......krrrk....", "......krrrrrk...", "......kwwwwwk...", "......kwdwwwk...",
    "..k...kwdwwwk...", ".ksk..kkkkkkk...", "kssskk..........", "kkkkkkkkkkkkkkkk", "keeseeeesseeeeek",
    "kkkkkkkkkkkkkkkk",
], S16)
SPRITES["holding:Apiary"] = _s([
    "..........y.....", "....y........y..", "................", "...kkk.....kkk..", "..kbbbk...kbbbk.",
    ".kbkkkbk.kbkkkbk", ".kbbbbbk.kbbbbbk", ".kbkkkbk.kbkkkbk", ".kbbdbbk.kbbdbbk", "kkkkkkkkkkkkkkkk",
    ".kb..........bk.",
], S16)
SPRITES["holding:Peat Bog"] = _s([
    ".l..l.......l..l", ".l..l.......l..l", ".ll.l..kkk..ll.l", "..l.l.kbbbk..l.l", "..lll.kkkkk..lll",
    "...l.kbkbbk...l.", "...l.kkkkkkk..l.", "kkkkkkkkkkkkkkkk", "kdeddeddddeddedk",
], S16)
SPRITES["holding:Forestry"] = _s([
    "...n........n...", "..nnn......nnn..", "..nnn......nnn..", ".nnnnn....nnnnn.", "..nnn......nnn..",
    ".nnnnn....nnnnn.", "nnnnnnn..nnnnnnn", "...b........b...", "...b..kkkk..b...", "...b.kbbbbk.b...",
    "....kbkbkbbk....", "....kbbbbbbk....", "....kkkkkkkk....",
], S16)
SPRITES["holding:Fishmongery"] = _s([
    ".....kkkkk......", "....krrrrrk.....", "...krrrrrrrk....", "..kkkkkkkkkkk...", "...kwwwwwwwk....",
    "...kwkdkwmwk.m..", "...kwkdkwwwk.m..", "kkkkkkkkkkkkkkkk", "kbbbbbbbbbbbbbbk", "eekeeeeekeeeeeke",
], S16)
SPRITES["holding:Mine"] = _s([
    "......kkkk......", "....kkttttkk....", "...kttuttttk....", "..kttttttuttk...", ".kttuttbbbbttk..",
    ".kttttbkddkbttk.", "kttttbkdddkbuttk", "ktuttbkdddkbtttk", "kttttbkdddkbtttk", "kkkkkkkkkkkkkkkk",
], S16)
SPRITES["holding:Arable Land"] = _s([   # two wheat sheaves on stubble
    "..y.y......y.y..", ".yyyyy....yyyyy.", "yyyyyyy..yyyyyyy", ".yyyyy....yyyyy.", "..yyy......yyy..",
    "..kbk......kbk..", "..yyy......yyy..", ".y.y.y....y.y.y.", "y..y..y..y..y..y", "bybybybybybybyby",
], S16)
SPRITES["holding:Common Land"] = _s([
    "..kkkk..........", ".kssssk.........", "ksssssskk...k..k", "ksssssskdk..kkkk", ".kkkkkkkk...k..k",
    ".k.k..k.k...kkkk", ".k.k..k.k...k..k",
], S16)


# ---------------------------------------------------------------- batch 2: husbandry (16)
SPRITES["holding:Herb Garden"] = _s([   # potting shed, herb beds
    "..kk............", ".krrk...........", "krrrrk..........", "kkkkkkk.l..a..l.", "kwywwk.a..y..a..",
    "kwwdwk.lalllylal", "kwwdwk.lllllllll", "kkkkkkbbbbbbbbbb",
], S16)

SPRITES["holding:Animal Husbandry"] = _s([   # barn and cow
    "...........k....", "..........krk...", ".........krrrk..", "........krrrrrk.", "kk.....kkkkkkkkk",
    "kskkkkk.kbbbbbk.", "ksssksk.kbkdkbk.", ".kssssk.kbdddbk.", ".k.k.k..kbdddbk.", ".k.k.k..kkdddkk.",
], S16)

SPRITES["holding:Saddlery"] = _s([   # finer stable: cupola + gold vane, timbered plaster, horses at the half-doors, saddle on a rack
    "......y.........", ".....kmk........", ".....kyk........", "....krrrk.......", "...krrrrrk......",
    "..krrrrrrrk.....", ".krrrrrrrrrk....", "krrrrrrrrrrrk...", "kkkkkkkkkkkkk...", "kwbwwbwbwwbwk...",
    "kwbbbwwwbbbwk...", "kwdbdwywdbdwk.cc", "kwdsdwwwdsdwkccc", "kwbbbwdwbbbwkbcb", "kkkkkkkkkkkkkkbk",
], S16)

SPRITES["holding:Vineyard"] = _s([   # trellised vines
    "bllllllllllllllb", "b.aa.b.aa.b.aa.b", "b.a..b.a..b.a..b", "b....b....b....b", "b....b....b....b",
    "bllllllllllllllb", "b.aa.b.aa.b.aa.b", "b.a..b.a..b.a..b", "b....b....b....b", "b....b....b....b",
    "llllllllllllllll",
], S16)

SPRITES["holding:Orchard"] = _s([   # fruit trees, apple basket
    "..lll.....lll...", ".lllll...lllll..", "llclcll.llclcll.", "lllllll.lllllll.", ".lclll...lclll..",
    "..lbl.....lbl...", "...b.......b....", "...b.......b....", "...b..ccc..b....", "...b.kbbbk.b....",
], S16)

SPRITES["holding:Bakery"] = _s([   # chimney smoke, loaves
    ".......kk.......", "......krrk......", ".....krrrrks....", "....krrrrrsk....", "...krrrrrrkkk...",
    "..krrrrrrrkkrk..", ".kkkkkkkkkkkkkk.", "..kwwwwwwwwwwk..", "..kwyywwwwdwwk..", "..kwwwwwwwdwwk..",
    "..kwbbbwwwdwwk..", "..kkkkkkkkkkkk..",
], S16)

SPRITES["holding:Meadery"] = _s([   # thatch, skep, casks
    ".......kk.......", "......kbbk......", ".....kbbbbk.....", "....kbbbbbbk....", "...kbbbbbbbbk...",
    "..kkkkkkkkkkkkkk", "...kwwwwwwwwkbmb", ".k.kwywwwwdwkkbk", "kbkkwwwwwwdwkkkk", "bybkwwwwwwdwkbmb",
    "kbkkkkkkkkkkkkbk",
], S16)

SPRITES["holding:Winery"] = _s([   # press house, grape-purple trim, barrels
    "................", "................", "................", ".....kk.........", "....krrk........",
    "...krrrrk.......", "..krrrrrrk......", ".krrrrrrrrk.....", "kkkkkkkkkkkk....", "kaaaaaaaaaak.kk.",
    "kwyykwwyywwkkbbk", "kwyykwwyywwkkbbk", "kwwwkddkwwwkbkkb", "kwwwkddkwwwkkbbk", "kkkkkkkkkkkkkkkk",
], S16)

SPRITES["holding:Cidery"] = _s([   # press shed, cider press
    "....k...........", "...krk..........", "..krrrk.........", ".krrrrrk........", "krrrrrrrk.kkkkk.",
    "kkkkkkkkkk.kmk..", "kbbbbbbbk..kmk..", "kbybbbdbk.kbbbk.", "kbbbbbdbk.kbbbkc", "kbbbbbdbkckkkkcc",
    "kkkkkkkkk.k...k.",
], S16)

SPRITES["holding:Mill"] = _s([   # stone mill, sails
    "...sb.......bs..", "....sb.....bs...", ".....sb.k.bs....", ".......brb......", "......krkrk.....",
    ".....krbrbrk....", "....ksbkkkbsk...", "....sbkkkkkbs...", "...sbktttttkbs..", ".....kttyttk....",
    ".....ktttttk....", ".....kttdttk....", ".....kttdttk....", ".....kttdttk....", ".....kkkkkkk....",
], S16)

# ---------------------------------------------------------------- nods: first holdings built on raw materials (16)
SPRITES["holding:Carpentry"] = _s([   # timber workshop, saw on sawhorse
    "....k...........", "...krk..........", "..krrrk.........", ".krrrrrk........", "krrrrrrrk.......",
    "kkkkkkkkkk......", "kbbbbbbbk..mmmb.", "kbybbbdbk.bbbbbb", "kbbbbbdbk..k..k.", "kbbbbbdbk..k..k.",
    "kkkkkkkkk.k.kk.k",
], S16)

SPRITES["holding:Furnace"] = _s([   # stone furnace, stack, ore heap
    "..........s.....", ".........s......", "........kuk.....", "........kuk.....", "........kuk.....",
    "........kuk.....", "........kuk.....", "........kuk.....", ".kkkkkkkkkk.....", ".kttttttttk.....",
    ".ktkkkkkttk.....", ".ktkfffkttk.....", ".ktkfyfkttk...k.", ".ktkfyfkttk..kuk", ".kkkfffkkkk.kuuk",
], S16)

SPRITES["holding:Harbor"] = _s([   # pier, crate, lamp, moored boat
    ".......y.....b..", ".......k.....bs.", ".......k.....bss", ".kkk...k.....bss", ".kbk...k.....bs.",
    ".kkk...k.....b..", "bbbbbbbbbbk..b.k", "ebeeebeeebkccccc", "ebeeebeeebekkkke", "ebeeebeeebeeeeee",
], S16)

SPRITES["holding:Butchery"] = _s([   # shop, hams on a rack
    "....kk..........", "...krrk.........", "..krrrrk........", ".krrrrrrk..bbbbb", "krrrrrrrrk.bm.mb",
    "kkkkkkkkkkkbcmcb", "kwwwwwwwwk.bcccb", "kwyywwwdwk.bscsb", "kwwwwwwdwk.b...b", "kwwwwwwdwk.b...b",
    "kkkkkkkkkk.b...b",
], S16)

SPRITES["holding:Alchemy"] = _s([   # workroom, books and flask, cauldron, glassware
    "...k............", "..kak...........", ".kaaak..........", "kaaaaak.........", "kkkkkkkks...s...",
    "kkkkkkkee..l....", "ktttttkee....l..", "ktytdtkcckllllks", "ktttdtkaakuuuuka", "ktttdtkbb.kuuk.a",
    "kkkkkkkcck.ff.kk",
], S16)

# ---------------------------------------------------------------- batch 3: arms (16)
SPRITES["holding:Fletchery"] = _s([   # shop, target with arrow
    "...kk...........", "..krrk..........", ".krrrrk....kkk..", "krrrrrrk..kcwck.", "kkkkkkkkcbbwywk.",
    "kbbbbbbk..kcwck.", "kbybbdbk...kkk..", "kbbbbdbk....b...", "kbbbbdbk...b.b..", "kkkkkkkk..b...b.",
], S16)

SPRITES["holding:Tannery"] = _s([   # hide on frame, vat
    "...k............", "..krk...bbbbb...", ".krrrk..b.s.b...", "krrrrrk.bsssb...", "kkkkkkkkbsssb...",
    "kwwwwwk.b.s.b...", "kwywdwk.bbbbb...", "kwwwdwk.b...bkkk", "kwwwdwk.b...bkdk", "kkkkkkk.b...bkkk",
], S16)

SPRITES["holding:Joinery"] = _s([   # workshop, chair and table
    "....k...........", "...krk..........", "..krrrk.........", ".krrrrrk........", "krrrrrrrk.......",
    "kkkkkkkkkk......", "kwwwwwwwkb......", "kwywwwdwkb..bbbb", "kwwwwwdwkbbbb..b", "kwwwwwdwkb.bb..b",
    "kkkkkkkkkb.bb..b",
], S16)

SPRITES["holding:Blacksmith"] = _s([   # open forge, anvil
    "........s.......", "....kk.s........", "...krrkkk.......", "..krrrrkk.......", ".krrrrrkk.......",
    "krrrrrrrrk......", "kkkkkkkkkkk.....", "kkkkkkkkkk......", "kttttttttk......", "ktddddddtk......",
    "ktddddddtk.mmmmm", "ktdfyfddtk..kmk.", "ktdfffddtk..kmk.", "kkkkkkkkkk.kkkkk",
], S16)

SPRITES["holding:Armory"] = _s([   # shield, spear rack
    ".....k..........", "....krk.........", "...krrrk........", "..krrrrrk.......", ".krrrrrrrk..m.m.",
    "krrrrrrrrrk.m.m.", "kkkkkkkkkkkkb.b.", "kkkkkkkkkkk.b.b.", "ktmmmmttttk.b.b.", "ktmccmttttk.b.b.",
    "ktmccmttdtk.bbbb", "kttmmtttdtk.b.b.", "ktttttttdtk.b.b.", "kkkkkkkkkkk.b.b.",
], S16)

SPRITES["holding:Master Workshop"] = _s([   # the hall behind, the forge it grew from in front (stack, hearth)
    "..........kk....", "..y......krrk...", ".kuk....krrrrk..", ".kuk...krrrrrrk.", ".kuk..krrrrrrrrk",
    ".kuk..kkkkkkkkkk", ".kuk..kwywwywwyk", ".kuk..kwwwwwwwwk", "kkkkkkkkkkkkwwwk", "kuuuuuuuuuukwmwk",
    "kuukkkkkuuukmmmk", "kuukfffkuuukwmwk", "kuukfyfkuuukwwdk", "kuukfyfkuuukwwdk", "kkkkfffkkkkkkkkk",
], S16)

SPRITES["holding:Gilded Foundry"] = _s([   # gold trim, crucible, ingots
    "....kk..........", "...kyyk.........", "..kyyyyk........", ".kyyyyyyk.......", "kyyyyyyyyk......",
    "kkkkkkkkkkk.....", "kkkkkkkkkk......", "kkkktttttk.kyyyk", "kkyktttttk.kmmmk", "kttttttdtk..kfk.",
    "kttttttdtk..yy..", "kttttttdtk.yyyy.", "kkkkkkkkkkyyyyyy",
], S16)

SPRITES["holding:Stable"] = _s([   # stalls, horse heads, hay
    "......kk........", ".....krrk.......", "....krrrrk......", "...krrrrrrk.....", "..krrrrrrrrk....",
    ".krrrrrrrrrrk...", "krrrrrrrrrrrrk..", "kkkkkkkkkkkkkkk.", "kkkkkbbkkkbbkk..", "kbbbbbsbbbbsbk..",
    "kddbbdbbbbdbbk..", "kddbbkkkbbkkkkyy", "kddbbbbbbbbbbkyy", "kkkkkkkkkkkkkkyy",
], S16)

SPRITES["holding:Forge"] = _s([   # dark stone, twin stacks, hearth
    "...........y....", "...y........y...", "..kuk.....kuk...", "..kuk.....kuk...", "..kuk.....kuk...",
    "..kuk.....kuk...", "kkkukkkkkkkukkk.", "kkkkkkkkkkkkkkk.", "kkkkkkkkkkkkkk..", "kuuuuuuuuuuuuk..",
    "kuuukkkkkkuuuk..", "kuuukffffkuuuk..", "kuuukfyyfkuuuk..", "kuuukfyyfkuuuk..", "kkkkkffffkkkkk..",
], S16)

SPRITES["holding:Tiltyard"] = _s([   # tilt barrier, pennants
    ".bcc........aab.", ".bc..........ab.", ".b............b.", ".b............b.", ".b............b.",
    ".b............b.", ".b............b.", "kkkkkkkkkkkkkkkk", "cwcwcwcwcwcwcwcw", "kkkkkkkkkkkkkkkk",
    ".b.b....b...b.b.", ".b.b....b...b.b.",
], S16)

SPRITES["holding:Court Armoury"] = _s([   # royal banners, armour display
    ".....krrrrk.....", "....krrrrrrk....", "...krrrrrrrrk...", "..krrrrrrrrrrk..", ".krrrrrrrrrrrrk.",
    "krrrrrrrrrrrrrrk", "kkkkkkkkkkkkkkkk", "kkkkkkkkkkkkkkkk", "kaattttttttttaak", "kaadkddttttttaak",
    "kaakmkdddttttaak", "ktammmdddttttatk", "kttdmddddttttttk", "kttmdmdddttttttk", "kkkkkkkkkkkkkkkk",
], S16)

# ---------------------------------------------------------------- batch 4: commerce (16)
SPRITES["holding:Weavery"] = _s([   # cloth on a line, bolts
    "...kk...........", "..krrk..........", ".krrrrk..kkkkkkk", "krrrrrrk.bcc.aab", "kkkkkkkkkbcc.aab",
    "kwwwwwwk.bcc.aab", "kwywwdwk.b...aab", "kwwwwdwk.byy.ccb", "kwwwwdwk.byy.ccb", "kkkkkkkk.baa.ccb",
], S16)

SPRITES["holding:Jewelry Foundry"] = _s([   # gold roof, gem sign, furnace
    "....k.........s.", "...kyk.......y..", "..kyyyk......kk.", ".kyyyyyk.....kk.", "kyyyyyyyk....kk.",
    "kkkkkkkkkk...kk.", "kkkkkkkkk....kk.", "ktttttttk.kkkkkk", "ktatttttk.kuuuuk", "kayattdtk.kuuuuk",
    "ktatttdtk.kuffuk", "ktttttdtk.kuyfuk", "kkkkkkkkk.kuffuk",
], S16)

SPRITES["holding:Market Square"] = _s([   # two stalls, crates
    "kkkkkkk..kkkkkkk", "scscscs..sasasas", "b.....b..b.....b", "b.....b..b.....b", "by.f.lb..by.f.lb",
    "bbbbbbbkkbbbbbbb", "b.....bbbb.....b", "b.....bkkb.....b",
], S16)

SPRITES["holding:Spice Merchant"] = _s([   # tent, spice sacks
    ".......kk.......", "......kffk......", ".....kffffk.....", "....kffffffk....", "...kffffffffk...",
    "..kkkkkkkkkkkk..", ".y.ddddkkdfdd.c.", "kykddddkkkfkdkck", "kbkddddkkkbkdkbk",
], S16)

SPRITES["holding:Merchant Quarter"] = _s([   # three townhouses
    ".......kk.......", "......krrk......", "..kk.kkkkkk.....", ".krrkkwwwwk.kk..", "kkkkkkwywwkkrrk.",
    "kwwwwkwwwwkkkkkk", "kwywwkwwwwkwwwwk", "kwwwwkwwwwkwywck", "kwwwykwwwwkwwwwk", "kwwwwkwwwwkwwwwk",
    "kwwdwkwwdwkwwdwk", "kwwdwkwwdwkwwdwk", "kkkkkkkkkkkkkkkk",
], S16)

SPRITES["holding:Money Lending"] = _s([   # bank: pediment, columns, steps
    "......kttk......", ".....kttttk.....", "....kttttttk....", "...ktttyytttk...", "..kttttyyttttk..",
    ".kttttttttttttk.", "kkkkkkkkkkkkkkkk", "kkkkkkkkkkkkkkkk", "dwwdwwddddwwdwwd", "dwwdwwdyydwwdwwd",
    "dwwdwwdyydwwdwwd", "dwwdwwdyydwwdwwd", "dwwdwwdyydwwdwwd", "tttttttttttttttt", "uuuuuuuuuuuuuuuu",
], S16)

SPRITES["holding:Shipyard"] = _s([   # hull on slipway, scaffold
    "............bbbb", "............m.b.", "............m.b.", "..............b.", "..b.b.b.b.b.b.b.",
    ".b.b.b.b.b.b.bb.", ".bbbbbbbbbbbbbb.", "..kkkkkkkkkkk.b.", "...kbbbbbbbk..b.", "....kkkkkkk...b.",
    "kkkkkkkkkkkkkkkk", "bbbbbbbbbbbbbbbb",
], S16)

SPRITES["holding:Courtyard"] = _s([   # empty paved square, dormered arcade behind
    "kkkkkkkkkkkkkkkk", "rrwrrrwrrrwrrrwr", "rrrrrrrrrrrrrrrr", "wwwwwwwwwwwwwwww", "wddwddwddwddwddw",
    "tttttttttttttttt", "wddwddwddwddwddw", "ssstssstssstssst", "sstssstssstwssts", "stssstssstsastss",
    "tssswssstssstsss", "ssstcsstssstssst", "sstssstssstsssts",
], S16)

SPRITES["holding:Artisan Workshop"] = _s([   # pots and vases
    "....k...........", "...krk..........", "..krrrk.........", ".krrrrrk........", "krrrrrrrk.......",
    "kkkkkkkkkk......", "kwwwwwwwk.k.....", "kwywwwdwkkck..k.", "kwwwwwdwkkck.kak", "kwwwwwdwk.k..kak",
    "kkkkkkkkkkck..k.",
], S16)

SPRITES["holding:Court Artists"] = _s([   # studio, easel, bust
    "...kk...........", "..kaak...kkkkk..", ".kaaaak..klyek..", "kaaaaaak.kcyak..", "kkkkkkkkkkkkkk..",
    "kwwwwwwk..b.b..s", "kwywwdwk..b.b.ss", "kwwwwdwk.b...b.k", "kwwwwdwk.b...bkt", "kkkkkkkk.b...bkt",
], S16)

SPRITES["holding:Emporium"] = _s([   # quay warehouse, crane, casks
    "...krk..........", "..krrrk.........", ".krrrrrk........", "krrrrrrrkbbbbbbb", "kkkkkkkkkk..b..m",
    "............b..m", "....y.......b..m", "kkkkkkkkk...b.kk", "kbbdddbbk...b.kk", "kbbdddbbkkkkb...",
    "kbbdddbbkbmbb...", "kbbdddbbkkbkb...", "tttttttttttttttt", "eeeeeeeeeeeeeeee", "eeeeeeeeeeeeeeee",
], S16)

# ---------------------------------------------------------------- batch 5: works (16)
SPRITES["holding:Masonry"] = _s([   # lodge, half-built wall, blocks
    "...k............", "..krk...........", ".krrrk..........", "krrrrrk.b....b..", "kkkkkkkkbkkkkb..",
    "ktttttk.bttutb..", "ktttdtk.bkkkkb..", "ktttdtk.bttttkk.", "ktttdtk.kkkkktt.", "kkkkkkk.tutt.tt.",
], S16)

SPRITES["holding:Workyard"] = _s([   # A-frame hoist, lumber, handcart
    "...........kkk..", "............m...", "............m...", "............m...", "...........bmb..",
    "...........bmb..", "...........bmb..", "..........kbbbk.", "..........b...b.", "..........b...b.",
    "..........b...b.", "kbbbbk....b...b.", "bkbkbbbbbb.....b", "kbbbbb..bb.....b", "bkbkbkmk.b.....b",
], S16)

SPRITES["holding:Storehouse"] = _s([   # warehouse, big doors, sacks
    "......krrk......", ".....krrrrk.....", "....krrrrrrk....", "...krrrrrrrrk...", "..krrrrrrrrrrk..",
    ".krrrrrrrrrrrrk.", "krrrrrrrrrrrrrrk", "kkkkkkkkkkkkkkkk", "kkkkkkkkkkkkkkkk", "kbbbbbbbbbbbbbbk",
    "kbbbbddddddbbbbk", "kbbbbddkkddbbbbk", "kssbbddkkddbbssk", "kssbbddkkddbsssk", "kkkkkddkkddkkkkk",
], S16)

SPRITES["holding:Census Hall"] = _s([   # stone hall, notice board
    ".....krk........", "....krrrk.......", "...krrrrrk......", "..krrrrrrrk.....", ".krrrrrrrrrk....",
    "krrrrrrrrrrrk...", "kkkkkkkkkkkkkk..", "kkkkkkkkkkkkk...", "kbbbbbbbttttk...", "kbsssssbttttk...",
    "kbskkksbttttk...", "kbsssssbtdttk...", "kbskkssbtdttk...", "kbbbbbbbtdttkttt", "kkkkkkkkkkkkkttt",
], S16)

SPRITES["holding:Granary"] = _s([   # on staddle stones, thatch, sacks
    ".......kk.......", "......kyyk......", ".....kyyyyk.....", "....kyyyyyyk....", "...kyyyyyyyyk...",
    "..kkkkkkkkkkkk..", "...kbbbddbbbk...", "...kbbbddbbbk...", "...kbbbddbbbk...", "...kkkkkkkkkk...",
    "....tttttt.ttt..", ".....t..t...t.ss", ".....t..t...tsss", ".....t..t...tsss",
], S16)

SPRITES["holding:Supply Depot"] = _s([   # tent, marked crates
    "....k...........", "...ksk...kkk....", "..kssdk..kck....", "..ksdsk..kkkkk..", ".kssdssk.kckckk.",
    ".ksdddsk.kkkkkb.", "kssdddsskkbkbkk.",
], S16)

SPRITES["holding:Trade Guild"] = _s([   # half-timbered, jettied, banner
    "....krrrrk......", "...krrrrrrk.....", "..krrrrrrrrk....", ".krrrrrrrrrrk...", "krrrrrrrrrrrrk..",
    "kkkkkkkkkkkkkkk.", "bwwwbwwwwbwwwbkk", "bwywbwywwbwywbac", "bwwwbwwwwbwwwbaa", "bkkkbkkkkbkkkba.",
    ".kkkkkkkkkkkk...", ".kwywwddwwwwk...", ".kwwwwddwwwwk...", ".kwwwwddwwwwk...", ".kkkkkkkkkkkk...",
], S16)

SPRITES["holding:College of Engineering"] = _s([   # gear on gable, arch model
    ".....k..........", "....mrm.........", "...mmmmm........", "..krmkmrk.......", ".krmmmmmrk......",
    "krrrmrmrrrk.....", "kkkkkkkkkkkk....", "kkkkkkkkkkk.....", "ktttttttttk.....", "ktyttyttttk.kkk.",
    "ktttttttdtkkb.bk", "ktttttttdtkb...b", "ktttttttdtkb...b", "kkkkkkkkkkkb...b",
], S16)

SPRITES["holding:Burgages"] = _s([   # two cottages, garden plots
    "..k.......k.....", ".krk.....krk....", "krrrk...krrrk...", "kkkkkk.kkkkkkk..", "kwwwk...kwwwk...",
    "kwwwkk..kwwwkk..", "kwdwkk.lkwdwkk.l", "kwdwkkllkwdwkkll", "kkkkkkkkkkkkkkkk",
], S16)

SPRITES["holding:Citadel"] = _s([   # tiered white city, ring walls, tall tower
    ".......kkc......", "......kssk......", "......kssk......", "......kssk......", "......kssk......",
    "....kkkkkkkk....", "....ssdssdss....", "....ssssssss....", "..kkkkkkkkkkkk..", "..ssdssssssdss..",
    "..tsssssssssst..", "kkkkkkkkkkkkkkkk", "ssussussssussuss", "sssssssddsssssss", "sssssssddsssssss",
], S16)

SPRITES["holding:Castle Hall"] = _s([   # great hall, keep, banner
    ".....kk.......ck", "....krrk..k.k.c.", "...krrrrk.kkkkkk", "..krrrrrrkkttttk", ".krrrrrrrrkttttk",
    "krrrrrrrrrrkdttk", "kkkkkkkkkkkkkttk", "kkkkkkkkkkkktttk", "kttttttttttktttk", "ktyttttttytktttk",
    "ktyttddttytktttk", "ktyttddttytktttk", "kttttddttttktttk", "kttttddttttktttk", "kkkkkkkkkkkkkkkk",
], S16)

# ---------------------------------------------------------------- batch 6: logistics (16)
SPRITES["holding:Smokehouse"] = _s([   # hut, roof smoke, fish on a rack
    "........s.......", "...s............", "....sk..s.......", "...srrks........", "..kdrrrd........",
    ".krrrrrrk.......", "krrrrrrrrk.bbbbb", "kkkkkkkkkkkbm.mb", "kbbbbbbdbk.bm.mb", "kbbbbbbdbk.b...b",
    "kbbbbbbdbk.b...b", "kkkkkkkkkk.b...b",
], S16)

SPRITES["holding:Caravanery"] = _s([   # inn with arched gate, covered wagon
    "k.k.k.k.k.......", "kkkkkkkkkk......", "kkkkkkkkkkkkkkk.", "kwwwddwwwksssssk", "kwwddddwwksssssk",
    "kwwddddwwkbbbbbb", "kwwddddwwkkmk.km", "kwwddddwwk......", "kkkddddkkk......",
], S16)

SPRITES["holding:Coliseum"] = _s([   # castle yard: quintain, weapon rack, dirt yard
    "k.kk............", "kkkk............", "kttk............", "kttkk.k.k.k.k.k.", "ktdkkkkkkkkkkkkk",
    "kttkuuuuuuuukuuu", "kttkuukuubbbbbbb", "kttkmumumcmubuuk", "kdtkmumumcmubuss", "kttkmumuumuubuss",
    "kttkbubuuuuubusu", "kttkbbbbuuuubuuu", "bbbbbbbbbbbbbbbb", "bbbbbdbbdbbbbbbb",
], S16)

SPRITES["holding:Conditioning Field"] = _s([   # training dummies, fence, weights
    "...yy....yy.....", "...yy....yy.....", ".bbbbbbbbbbbb...", "...yy....yy.....", "...yy....yy.....",
    "...yy....yy..bbb", "....b.....b...b.", "....b.....b...b.", "....b.....b..kk.", "....b.....b..tu.",
], S16)

SPRITES["holding:Grand Tournament"] = _s([   # striped pavilions, pennants
    "...k........k...", "...kcc......kaa.", "...k........k...", "..k.k......k.k..", ".kcsck....kasak.",
    "kcscsck..kasasak", ".scscs....sasas.", ".scscs....sasas.", ".scdcs....sadas.", ".scdcs....sadas.",
    ".scdcs....sadas.", ".scdcs....sadas.",
], S16)

SPRITES["holding:Charcoal Burner"] = _s([   # smoking clamp, log stack
    ".......s........", "......s.........", "................", ".....s..........", "......s.........",
    ".....s..........", ".....kkk........", "...kuuuuuk......", "..kuuuuuuuk.....", ".kuuuuuuuuukkbk.",
    ".kuuuuuuuuukbkbk", ".kufuuuufuukkbkb", ".kkkkkkkkkkkbkbk",
], S16)

SPRITES["holding:Kiln"] = _s([   # bottle kiln, fire mouth, pots
    ".....s..........", ".....kk.........", ".....rr.........", "....krrk........", "....krrk........",
    "...krrrrk.......", "..krrrrrrk......", "..krrrrrrk......", "..krrrrrrk......", "..krrrrrrk......",
    "..krrkkrrk......", "..krkffkrk......", "..krkfykrk...k.k", "..krkffkrk..kckc", "..kkkkkkkk..kckc",
], S16)

SPRITES["holding:Levy Hall"] = _s([   # muster hall, spear stack, banner
    ".....k..........", "....krk.........", "...krrrk........", "..krrrrrk..m.m.m", ".krrrrrrrk.b.b.b",
    "krrrrrrrrkc.bbb.", "kkkkkkkkkkck.b..", "kkkkkkkkkkk.bbb.", "kbbbbbbbbkkb.b.b", "kbybbbbbykkb.b.b",
    "kbbbbdbbbbkb.b.b", "kbbbbdbbbbkb.b.b", "kbbbbdbbbbkb.b.b", "kkkkkkkkkkkb.b.b",
], S16)

SPRITES["holding:Siege Works"] = _s([   # ram slung under a timber mantlet, on wheels
    "................", "................", "....kkkkkkkk....", "..kkbbbbbbbbkk..", ".kbbbbbbbbbbbbk.",
    "kbbbbbbbbbbbbbbk", "kkkkkkkkkkkkkkkk", ".b...s....s...b.", ".b...s....s...b.", "mmmbbbbbbbbbbbb.",
    ".b............b.", "kkkkkkkkkkkkkkkk", "kbbbbbbbbbbbbbbk", ".kmk........kmk.", ".kkk........kkk.",
], S16)

SPRITES["holding:Siege Camp"] = _s([   # palisade, tents, campfire
    "...k........k...", "..ksk......ksk..", ".kssdk....kssdk.", ".kssdk.f.kssssdk", ".kkkkkfy.kkkkkkk",
    "k.k.k.k.k.k.k.k.", "bbbbbbbbbbbbbbbb", "kbkbkbkbkbkbkbkb", "bbbbbbbbbbbbbbbb", "bbbbbbbbbbbbbbbb",
    "bbbbbbbbbbbbbbbb",
], S16)

SPRITES["holding:War College"] = _s([   # crossed swords, watchtower
    ".....k..........", "....krk.........", "...krrrk...k.k.k", "..krrrrrk..kkkkk", ".krrrrrrrk.ktttk",
    "krrrrrrrrrkktttk", "kkkkkkkkkkkktdtk", "kkkkkkkkkkkktttk", "kttmtttmttkktttk", "ktttmtmtttkktdtk",
    "kttttmttttkktttk", "ktttbdbtttkktttk", "kttttdttttkktttk", "kttttdttttkktttk", "kkkkkkkkkkkkkkkk",
], S16)

# ---------------------------------------------------------------- batch 7: devotion (16)
SPRITES["holding:Chandlery"] = _s([   # shop, candle sign, lit candles
    ".....k..........", "....krk......y..", "...krrrk.....y..", "..krrrrrk...kkk.", ".krrrrrrrk..kwk.",
    "krrrrrrrrrk.kwk.", "kkkkkkkkkkkkkwk.", "kwwwwwwwwwk.kwk.", "kywywywwdwk.kwk.", "kswswswwdwk.kwk.",
    "kkkkkkwwdwk.kwk.", "kkkkkkkkkkk.kkk.",
], S16)

SPRITES["holding:Interrogation Chambers"] = _s([   # dark block, barred window, lantern
    "k.k.k.k.k.k.k.k.", "kkkkkkkkkkkkkkk.", ".kuuuuuuuuuuukk.", ".kudmdmuuuuuukc.", ".kudmdmumuuuukk.",
    ".kudmdmumudduk..", ".kuuuuuukudduk..", ".kuuuuuuuudduk..", ".kuuuuuuuudduk..", ".kkkkkkkkkkkkk..",
], S16)

SPRITES["holding:Abbey"] = _s([   # nave, bell tower, cross
    "...........kkk..", "...........krk..", "....kk....kkkkk.", "...krrk...ktttk.", "..krrrrk..ktttk.",
    ".krrrrrrk.ktytk.", "krrrrrrrrkktttk.", "kkkkkkkkkkktttk.", "kkkkkkkkkkktdtk.", "kttttttttkktttk.",
    "kttyttyttkktttk.", "kttttttttkktttkt", "ktttdttttkktttkt", "ktttdttttkktttkt", "kkkkkkkkkkkkkkkt",
], S16)

SPRITES["holding:Reliquary"] = _s([   # shrine, glowing niche, gold casket
    ".......ky.......", "......kyyk......", ".....kyyyyk.....", "....kyyyyyyk....", "...kyyyyyyyyk...",
    "..kkkkkkkkkkkk..", "...kttttttttk...", "...ktkkddkktk...", "...ktkddddktk...", "...ktkkyykktk...",
    "...ktkyyyyktk...", "...ktkkttkktk...", "...ktkdttdktk...", "...kkkkkkkkkk...",
], S16)

SPRITES["holding:Monastery"] = _s([   # dormitory range, chapel, wall
    "............k...", "....k......kkk..", "...krk....kkykk.", "..krrrk..krrrrrk", ".krrrrrkkkkkkkkk",
    "krrrrrrrkkkkkkkk", "kkkkkkkkkkwwwwwk", "kkkkkkkkkkwwwwwk", "ktttttttkkwwwwwk", "ktytytytkkwwwwwk",
    "ktttttttkkwwdwwk", "ktttttttkkwwdwwk", "kkkkkkkkkkkkkkkk", "tltltltttttttttt",
], S16)

SPRITES["holding:Execution Dock"] = _s([   # gallows on a pier
    "....bbbbbbb.....", "....bb...m......", "....b....m......", "....b....m......", "....b....m......",
    "....b...m.m.....", "....b....m......", "....b...........", "....b...........", "bbbbbbbbbbbbb...",
    "ebeeeebeeeebeeee", "ebeeeebeeeebeeee", "ebeeeebeeeebeeee",
], S16)

SPRITES["holding:Hospitaller"] = _s([   # hall, black banner with white cross
    "....kk.....bkkkk", "...krrk....bkksk", "..krrrrk...bksss", ".krrrrrrk..bkksk", "krrrrrrrrk.bkksk",
    "kkkkkkkkkkkbkkkk", "kkkkkkkkkk.b....", "kttttttttk.b....", "ktytyttttk.b....", "ktttttdttk.b.k..",
    "ktttttdttk.bksk.", "ktttttdttk.bkssk", "kkkkkkkkkk.bkssk",
], S16)

SPRITES["holding:Episcopal Court"] = _s([   # bishop's hall, purple roof and banners
    ".....kasyak.....", "....kaaysaak....", "...kaaaaaaaak...", "..kaaaaaaaaaak..", ".kaaaaaaaaaaaak.",
    "kaaaaaaaaaaaaaak", "kkkkkkkkkkkkkkkk", "kkkkkkkkkkkkkkkk", "kattttttttttttak", "katyttttttttytak",
    "katttttddtttttak", "kttttttddttttttk", "kttttttddttttttk", "kttttttddttttttk", "kkkkkkkkkkkkkkkk",
], S16)

SPRITES["holding:Apothecary"] = _s([   # shop, jars, mortar sign, herbs
    ".....k..........", "....krk.........", "...krrrk........", "..krrrrrk.......", ".krrrrrrrk......",
    "krrrrrrrrrk.....", "kkkkkkkkkkkkkkk.", "kekaklkkkkk.b.b.", "kbbbbbbwwwk.l.l.", "kcwywewwwwk.l...",
    "kwwwwwwwdwk.k.k.", "kwwwwwwwdwk.ktk.", "kwwwwwwwdwk..k..", "kkkkkkkkkkk.kkk.",
], S16)

SPRITES["holding:Infirmary"] = _s([   # long ward, red cross over the door, beds in the windows
    "................", "................", "................", "....krrrrrrrk...", "...krrrrrrrrrk..",
    "..krrrrrrrrrrrk.", ".krrrrrrrrrrrrrk", "kkkkkkkkkkkkkkkk", "kwwwwwwwcwwwwwwk", "kwkkkkwcccwkkkkk",
    "kwksskwwcwwksskk", "kwkkkkwwwwwkkkkk", "kwwwwwwkddkwwwwk", "kwwwwwwkddkwwwwk", "kkkkkkkkkkkkkkkk",
], S16)

SPRITES["holding:Pilgrimage Site"] = _s([   # stone cross on a mound, candles, pilgrim
    ".......kk.......", ".......tt.......", ".....kkttkk.....", ".....tttttt.....", ".....kkttkk.....",
    ".......tt.......", ".......tt.......", ".......tt.......", "...y..kttky.....", "....kkkkkkk.....",
    "..kllllllllk.w..", ".kllllllllllka..", "kllllssllllllab.", "llllsslllllllll.",
], S16)


# ---------------------------------------------------------------- batch 8: court (16)
SPRITES["holding:Inn"] = _s([   # half-timbered inn, tankard sign, barrel
    "...krrrrk.......", "..krrrrrrk......", ".krrrrrrrrk.....", "krrrrrrrrrrk....", "kkkkkkkkkkkkk...",
    "bkkkbkkbkkkb....", "bwwwbwwbwwwbbbb.", "bwywbwwbwywb.kk.", "bwwwbwwbwwwb.yk.", "bbbbbbbbbbbb.yy.",
    "kwwwwddwwwwk....", "kwywwddwwywk....", "kwwwwddwwwwk.kkk", "kwwwwddwwwwk.bmb", "kkkkkkkkkkkk.kbk",
], S16)

SPRITES["holding:Jester's Court"] = _s([   # harlequin hall, jester pennant
    ".....kak........", "....kaaak.......", "...kaaaaak...bcy", "..kaaaaaaak..bc.", ".kaaaaaaaaak.by.",
    "kaaaaaaaaaaakb.a", "kkkkkkkkkkkkkb..", "kkkkkkkkkkkkkby.", "kacyaycacyaykb..", "kcyaycacyayckb.c",
    "kyaycacyaycakb..", "kaycacdaycackb..", "kycacydycacykb..", "kcacyadcacyakb..", "kkkkkkkkkkkkkb..",
], S16)

SPRITES["holding:Bell Tower"] = _s([   # slender tower, open belfry, bell
    ".......kk.......", "......krrk......", ".....krrrrk.....", "....kkkkkkkk....", ".....kddddk.....",
    ".....kdyyyk.....", ".....kdyyyk.....", ".....kddddk.....", ".....kttttk.....", ".....kttttk.....",
    ".....ktddtk.....", ".....ktddtk.....", ".....ktddtk.....", ".....ktddtk.....", ".....kttttk.....",
], S16)

SPRITES["holding:Embassy"] = _s([   # columned front, foreign flags
    "..kcy.kas.klykes", "..kcc.kaa.kllkee", "..k...k...k..k..", "..k...k...k..k..", "..k...k...k..k..",
    "tttttttttttttttt", "kkkkkkkkkkkkkkkk", "wtwwtwwwwwwtwwtw", "wtwwtwwwwwwtwwtw", "wtwwtwwddwwtwwtw",
    "wtwwtwwddwwtwwtw", "wtwwtwwddwwtwwtw", "wtwwtwwddwwtwwtw", "tttttttttttttttt",
], S16)

SPRITES["holding:Academy"] = _s([   # dome, lamp-of-learning emblem, steps
    ".......kkk......", "......kyyyk.....", ".....kyyyyyk....", ".kkkkkkkkkkkkkk.", ".kkkkkkkykkkkkk.",
    ".ktttttyfyttttk.", ".kttttttktttttk.", ".ktttttmmmttttk.", ".ktyttkkkkktytk.", ".ktttttddtttttk.",
    ".ktttttddtttttk.", "tttttttttttttttt",
], S16)

SPRITES["holding:University"] = _s([   # gate tower with clock, wings, pointed windows
    ".......kk.......", "......kaak......", "......aaaa......", ".....kkkkkk.....", "..kk.kttttk.kk..",
    ".kaakkttytkkaak.", "kaaaaktyytkaaaak", "kkkkkkttttkkkkkk", "kkkkkkttttkkkkkk", "ktktkkttttktktkk",
    "ktytyktkktktytyk", "ktytyktddtktytyk", "kttttktddtkttttk", "kttttktddtkttttk", "kkkkkktddtkkkkkk",
], S16)

SPRITES["holding:Courier Network"] = _s([   # dovecote, birds, post-horn stable
    "..........s.....", "...kkk..........", "..kaaak.....s...", ".kaaaaak.s......", ".kkkkkkk....k...",
    ".kwwwwwk...krk..", ".kwdwdwk..krrrk.", ".kwwwwwk.krrrrrk", ".kwdwdwkkkkkkyyk", ".kwwwwwk.kbbbbyk",
    ".kwdwdwk.kbdddbk", ".kwwdwwk.kbdddbk", ".kwwdwwk.kbdddbk", ".kwwdwwk.kkdddkk",
], S16)

# ---------------------------------------------------------------- batch 9: secrecy (16)
SPRITES["holding:Toll House"] = _s([   # gatehouse, barrier pole, coin box
    "...k............", "..krk...........", ".krrrk..........", "krrrrrk.........", "kkkkkkkk........",
    "kkkkkkk.........", "ktttttk.........", "ktttytkscscscscs", "ktttttkkbkkkkkkk", "kttdttk.b.......",
    "kttdttk.b....kkk", "kttdttk.b....kyk", "kkkkkkk.b....kkk",
], S16)

SPRITES["holding:Secret Cellar"] = _s([   # cottage, open cellar hatch, lantern
    "....k...........", "...krk..........", "..krrrk.........", ".krrrrrk........", "krrrrrrrk.......",
    "kkkkkkkkkk......", "kkkkkkkkk.......", "kwwwwwwwkk......", "kwwwwwywkbk.....", "kwwdwwwwkbbk....",
    "kwwdwwwwkbbbk.k.", "kwwdwwwwkkdddky.", "kkkkkkkkkkddddk.",
], S16)

SPRITES["holding:Smuggler's Nook"] = _s([   # cove, crates, rowboat, lantern
    "..kkkkkk........", ".kuuuuuuk.......", "kuuuuuuuuk......", "kuuddduuuuk.....", "kuddddduuuuk....",
    "kuddddyduuuuk...", "uudkkdduuuuuu...", "uudbbdduuuuuu...", "uuuuuuuuukbbbbbk", "eeeeeeeeeekkkkke",
    "eeeeeeeeeeeeeeee", "eeeeeeeeeeeeeeee",
], S16)

SPRITES["holding:Syndicate Hub"] = _s([   # dark townhouses, one lit window, key sign
    "..k.............", ".kuk.........k..", "kkkkk.......kuk.", "kuuuk...k..kkkkk", "kuduk..kuk.kuuuk",
    "kuuuk.kkkkkkuduk", "kuuuk.kuuukkuuuk", "kuduk.kudukkuuuk", "kuuuk.kuuukkuduk", "kuuuk.kuyukkuuuk",
    "kuduy.kudukkuuuk", "kuuuy.kuuukkuduk", "kuuuy.kuuukkuduk", "kuuuk.kuuukkuduk", "kkkkk.kkkkkkkkkk",
], S16)

SPRITES["holding:Black Market"] = _s([   # dark awning, hooded seller, goods
    "kkkkkkkkkkkkkkkk", "kadadadadadadadk", "b............k.b", "b......kk....y.b", "b.....kddk.....b",
    "b.....kddk.....b", "b......dd......b", "b......dd......b", "byaekcykkmekya.b", "bkkkkkkkkkkkkk.b",
], S16)

SPRITES["holding:Forgery Workshop"] = _s([   # screw press, sealed papers
    "...kk...........", "..krrk..........", ".krrrrk.........", "krrrrrrk.kkkkkk.", "kkkkkkkkk.k..k..",
    "kkkkkkkk..kmmk..", "kwwwwwwk..k.mk..", "kwywwwwk.kkkkkk.", "kwwwwdwk.bssssb.", "kwwwwdwk.b.cc.b.",
    "kwwwwdwk.b....b.", "kkkkkkkk.b....b.",
], S16)

SPRITES["holding:Toxicarium"] = _s([   # glasshouse, poison plants in a soil bed, skull plaque
    "......keek......", ".....keeeek.....", "....keeeeeek....", "...keessseeek...", "..keeekskeeeek..",
    ".keeeeeeeeeeeek.", "kkkkkkkkkkkkkkkk", "kdddkdddkdddkddk", "kddckddlkddakddk", "kdalkddlkdclkdlk",
    "kdllkdalkdllkdlk", "kdllkdllkdllkdlk", "kdllkdllkdllkdlk", "kbbbbbbbbbbbbbbk", "kkkkkkkkkkkkkkkk",
], S16)

SPRITES["holding:Charnel House"] = _s([   # ossuary, skull, stacked bones
    ".....k..........", "....krk.........", "...krrrk........", "..krrrrrk.......", ".krrrrrrrk......",
    "krrrrrrrrrk.....", "kkkkkkkkkkkk....", "kkkkkkkkkkk.....", "ktttssstttk.....", "ktttksktttk.....",
    "kttttsttttk.....", "kttttdttttks.s.s", "kttttdttttksssss", "kttttdttttks.s.s", "kkkkkkkkkkksssss",
], S16)

SPRITES["holding:Beacon Towers"] = _s([   # tower with blazing beacon, second tower
    ".......s........", "......s.........", ".......ff.......", "......fyyf......", ".....kffffk.....",
    ".....kkkkkk.....", ".....kttttk.....", ".....kttttk.....", ".....ktdttk.kfk.", ".....kttttk.kkkk",
    ".....kttttk.kttk", ".....kttdtk.kttk", ".....ktddtk.kttk", ".....ktddtk.kttk", ".....kttttk.kkkk",
], S16)

SPRITES["holding:Forgotten Catacombs"] = _s([   # crumbling arch, stairs down, ivy
    "....kkkkkk......", "...kttttttk.....", "..kttkkkkttk....", "..ktkddddktl....", "..ktkddddktl....",
    "..ktkddddktl....", "..ktkdkkdktk....", "..ktkkddkkuk....", "..kkdddddddk..kk", "ktkdddddddddkkuu",
    "tu...........ktu",
], S16)

SPRITES["holding:Cipher Chamber"] = _s([   # tower, cipher wheel, candlelit slit
    "....k.kk.k.k....", "....kkkkkkkk....", "....ktkkkktk....", "....kkymmykk....", "....kkmykmkk....",
    "....kkmkymkk....", "....kkymmykk....", "....ktkkkktk....", "....kttttttk....", "....kttyyttk....",
    "....kttttttk....", "....kttddttkkss.", "....kttddttkksk.", "....kkkkkkkkkkk.",
], S16)

# ---------------------------------------------------------------- skyline: settlement cores and fillers, infrastructure pieces, raw feet strips
SPRITES["sky:core:Hamlet"] = _b([   # steep-thatched longhouse on a rise, poplar, hayrick
    "............sk............", "............kk............",
    ".l.........kbbk...........", ".l.........kbbk...........",
    "lll.......kbbbbk..........", "lll.......kbbbbk..........",
    "lll......kbbbbbbk.........", "lll......kbbbbbbk.........",
    "lll.....kbbbbbbbbk........", "lll.....kbbbbbbbbk.....k..",
    "lll....kbbbbbbbbbbk...kyk.", "lll....kkkkkkkkkkkk..kyyyk",
    "lll.....kwwwwwwwwk...kyyyk", "lll.....kywwwwwwyk...kyyyk",
    "lll.....kwwdwwwwwk...kyyyk", "lll.....kwwdwwwwwk...kyyyk",
    "lll.....kwwdwwwwwk...kyyyk", "lll....lkkkdkkkkkkl..kyyyk",
    ".b...llllllllllllllllkyyyk", ".b.llllllllllllllllllkyyyk",
    ".b.llllllllllllllllllkkkkk", ".b.lllllllllllllllllllb.b.",
], 26, 23)

SPRITES["sky:fill:Hamlet"] = _b([   # poplar behind a fence
    ".....l....", ".....l....", "....lll...", "....lll...",
    "....lll...", "....lll...", "....lll...", "....lll...",
    "....lll...", "....lll...", "....lll...", "....lll...",
    "....lll...", "....lll...", "k.k.klk.k.", "kkkkkkkkkk",
    "k.k.kbk.k.", "k.k.kbk.k.",
], 10, 19)

SPRITES["sky:core:Village"] = _b([   # chapel with steeple between two houses
    "............kk............", "............kk............",
    "...........kttk...........", "...........kkkk...........",
    "...........kkkk...........", "...........kttk...........",
    "...........kyyk...........", "...........kyyk...........",
    "...........kttk...........", "...........kttk...........",
    "...........kttk...........", "...........kkkk...........",
    "...........krrk.......k...", "...k......krrrrk.....krk..",
    "..krk....krrrrrrk...krrrk.", ".krrrk..krrrrrrrrk.krrrrrk",
    "krrrrrkkkkkkkkkkkkkkkkkkkk", "kkkkkkkkkkkkkkkkkk.kkkkkkk",
    "kkkkkkk.kttttttttk.kwwwwwk", "kwwwwwk.ktyttttytk.kywwwwk",
    "kywwwwk.kttttttttk.kwwwwwk", "kwwwwwk.kttttttttk.kwwwwwk",
    "kwwwwwk.ktttddtttk.kwwwwwk", "kwwdwwk.ktttddtttk.kwwdwwk",
    "kwwdwwk.ktttddtttk.kwwdwwk", "kkkkkkk.kkkkkkkkkk.kkkkkkk",
], 26, 27)

SPRITES["sky:fill:Village"] = _b([   # steep-roofed house
    "....kk....", "....kk....", "...krrk...", "...krrk...",
    "..krrrrk..", "..krrrrk..", ".krrrrrrk.", ".krrrrrrk.",
    "krrrrrrrrk", "kkkkkkkkkk", ".kkkkkkkk.", ".kwwwwwwk.",
    ".kywwwwwk.", ".kwwwwwwk.", ".kwwwwwwk.", ".kwwdwwwk.",
    ".kwwdwwwk.", ".kkkkkkkk.",
], 10, 19)

SPRITES["sky:core:Town"] = _b([   # keep between houses
    "......k.k.k.k.k.k.......", "......kkkkkkkkkkkk......",
    "......kttttttttttk......", "......kttttttttttk......",
    "......kttttttttttk..k...", "...k..kttyttttyttk.krk..",
    "..krk.kttttttttttkkrrrk.", ".krrrkkttttttttttkrrrrrk",
    "krrrrrktttttttttkkkkkkkk", "kkkkkkkktttttttttkkkkkkk",
    "kkkkkkkttyttttyttkwwwwwk", "kwwwwwkttttttttttkwywwwk",
    "kwywwwkttttttttttkwwwwwk", "kwwwwwkttttttttttkwwwwwk",
    "kwwwwwkttttddttttkwwwwwk", "kwwwwwkttttddttttkwwwwwk",
    "kwwwwwkttttddttttkwwwwwk", "kwwwwwkttttddttttkwwwwwk",
    "kkkkkkkkkkkkkkkkkkkkkkkk",
], 24, 20)

SPRITES["sky:fill:Town"] = _b([   # house
    "....kk....", "...krrk...", "..krrrrk..", ".krrrrrrk.",
    "kkkkkkkkkk", ".kkkkkkkk.", ".kwwwwwwk.", ".kwywwywk.",
    ".kwwwwwwk.", ".kwwwwwwk.", ".kwwdwwwk.", ".kwwdwwwk.",
    ".kkkkkkkk.",
], 10, 14)

SPRITES["sky:core:City"] = _b([   # central hall, two towers
    "..k.k.k................k.k.k..",
    "..kkkkk.......kk.......kkkkk..",
    "..ktttk......krrk......ktttk..",
    "..ktttk.....krrrrk.....ktttk..",
    "..ktttk....krrrrrrk....ktttk..",
    "..ktdtk...krrrrrrrrk...ktdtk..",
    "..ktttk..krrrrrrrrrrk..ktttk..",
    "..ktttk.krrrrrrrrrrrrk.ktttk..",
    "..ktttkkkkkkkkkkkkkkkkkktttk..",
    "..ktttk.kkkkkkkkkkkkkk.ktttk..",
    "..ktdtk.kttttttttttttk.ktdtk..",
    "..ktttk.kttttttttttttk.ktttk..",
    "..ktttk.kttttttttttttk.ktttk..",
    "..ktttk.kttyttttttyttk.ktttk..",
    "..ktttk.kttttttttttttk.ktttk..",
    "..ktdtk.kttttttttttttk.ktdtk..",
    "..ktttk.kttttttttttttk.ktttk..",
    "..ktttk.kttttttttttttk.ktttk..",
    "..ktttk.kttyttttttyttk.ktttk..",
    "..ktttk.kttttttttttttk.ktttk..",
    "..ktttk.ktttttddtttttk.ktttk..",
    "..ktttk.ktttttddtttttk.ktttk..",
    "..ktttk.ktttttddtttttk.ktttk..",
    "..ktttk.ktttttddtttttk.ktttk..",
    "..kkkkk.kkkkkkkkkkkkkk.kkkkk..",
], 30, 26)

SPRITES["sky:fill:City"] = _b([   # tall narrow house
    "...kk...", "..krrk..", ".kkkkkk.", ".kkkkkk.", ".kwwwwk.",
    ".kwywwk.", ".kwwwwk.", ".kwwwwk.", ".kwwwwk.", ".kwywwk.",
    ".kwwwwk.", ".kwwwwk.", ".kwwwwk.", ".kwdwwk.", ".kwdwwk.",
    ".kkkkkk.",
], 8, 17)

SPRITES["sky:core:Metropolis"] = _b([   # spired hall, gold domes
    "................yk................",
    "................kk................",
    "................kk................",
    "................kk................",
    "...............kkkk...............",
    "..............krrrrk..............",
    ".............krrrrrrk.............",
    "............kkkkkkkkkk............",
    ".............kkkkkkkk.............",
    ".............kttttttk.............",
    ".....kkk.....kttttttk.............",
    "....kyyyk....ktyttytk.............",
    "...kyyyyyk...kttttttk.....kkk.....",
    "...kkkkkkk...kttttttk....kyyyk....",
    "...kwwwwwk...kttttttk...kyyyyyk...",
    "...kwwwwwk...kttttttk...kkkkkkk...",
    "...kwywywk...kttttttk...kwwwwwk...",
    "...kwwwwwk...ktyttytk...kwwwwwk...",
    "...kwwwwwk...kttttttk...kwywywkkkk",
    "...kwwwwwk...kttttttk...kwwwwwkktk",
    "kkkkwwwwwk...kttttttk...kwwwwwkktk",
    "ktkkwywywk...kttttttk...kwwwwwkktk",
    "ktkkwwwwwk...kttttttk...kwwwwwkktk",
    "ktkkwwwwwk...kttttttk...kwywywkktk",
    "ktkkwwwwwk...kttttttk...kwwwwwkktk",
    "ktkkwwwwwk...kttddttk...kwwwwwkktk",
    "ktkkwwwwwk...kttddttk...kwwwwwkktk",
    "ktkkwwwwwk...kttddttk...kwwwwwkktk",
    "ktkkwwwwwk...kttddttk...kwwwwwkktk",
    "kkkkkkkkkk...kkkkkkkk...kkkkkkkkkk",
], 34, 31)

SPRITES["sky:fill:Metropolis"] = _b([   # tall house with chimney
    ".....k..", ".....k..", "...kkk..", "..krrk..", ".kkkkkk.",
    ".kwwwwk.", ".kwwwwk.", ".kwywwk.", ".kwwwwk.", ".kwwwwk.",
    ".kwwwwk.", ".kwywwk.", ".kwwwwk.", ".kwwwwk.", ".kwwwwk.",
    ".kwwwwk.", ".kwdwwk.", ".kwdwwk.", ".kkkkkk.",
], 8, 20)

SPRITES["inf:Town Hall"] = _b([   # hall, clock gable
    ".....kk.....", "....krrk....", "...krkykk...", "..krrrrrrk..",
    ".krrrrrrrrk.", "kkkkkkkkkkkk", ".kwwwwwwwwk.", ".kwwwwwwwwk.",
    ".kwwwwwwwwk.", ".kywwwwwwyk.", ".kwwwwwwwwk.", ".kwwwwwwwwk.",
    ".kwwwddwwwk.", ".kwwwddwwwk.", ".kwwwddwwwk.", ".kkkkkkkkkk.",
], 12, 17)

SPRITES["inf:Cathedral"] = _b([   # spire, rose window, nave
    ".....kk.....", ".....kk.....", ".....kk.....", ".....kk.....",
    "....kttk....", ".....kk.....", ".....kk.....", "....kttk....",
    "....kttk....", "....kttk....", "....kkkk....", "....krrk....",
    "...krrrrk...", "..krrrrrrk..", ".kkkkkkkkkk.", "..kttttttk..",
    "..kttttttk..", "..kttttttk..", "..kttyyttk..", "..kttyyttk..",
    "..kttttttk..", ".tkttttttkt.", ".tkttttttkt.", ".tkttttttkt.",
    ".tkttttttkt.", ".tkttttttkt.", ".tkttddttkt.", ".tkttddttkt.",
    ".tkttddttkt.", ".tkkkkkkkkt.",
], 12, 31)

SPRITES["inf:Library"] = _b([   # domed reading hall
    "....kkk.....", "...keeek....", "..keeeeek...", "..kkkkkkk...",
    "..ktttttk...", "..kkkkkkk...", "..ktttttk...", "..kytytyk...",
    "..kytytyk...", "..kytytyk...", "..kytytyk...", "..ktttttk...",
    "..ktttttk...", "..kttdttk...", "..kttdttk...", "..kkkkkkk...",
], 12, 17)

SPRITES["inf:Garrison"] = _b([   # tower, pennant
    "..kc..", "k.kk.k", "kkkkkk", "kttttk", "kttttk", "kttttk",
    "ktdttk", "kttttk", "kttttk", "kttttk", "kttttk", "kttdtk",
    "kttttk", "kttttk", "kttttk", "kttttk", "ktdttk", "kttttk",
    "kttttk", "kttttk", "kttttk", "kttttk", "kttttk", "kkkkkk",
], 6, 25)

SPRITES["inf:Muster Field"] = _b([   # flagpole, standard
    "kccc", "kccc", "kcc.", "kc..", "k...", "k...", "k...", "k...",
    "k...", "k...", "k...", "k...", "k...", "k...", "k...", "k...",
    "k...", "k...", "k...", "k...", "k...", "k...",
], 4, 23)

SPRITES["inf:Wooden Walls"] = _b([   # palisade tile (repeats)
    "k.b.", "bbbb", "bbbb", "kkkk", "bbbb", "bbbb", "bbbb",
], 4, 8)

SPRITES["inf:Stone Walls"] = _b([   # curtain-wall tile (repeats)
    "k.k.", "kkkk", "tttt", "tutt", "tttt", "ttut", "tttt", "tttt",
], 4, 9)

SPRITES["inf:Stone Walls:tower"] = _b([   # wall tower at each end
    "k.kk.k", "kkkkkk", "kttttk", "kttttk", "ktdttk", "kttttk",
    "kttttk", "kttttk", "kttttk", "kttttk", "kkkkkk",
], 6, 12)

SPRITES["inf:Hitching Post"] = _b([   # rail and ring (foreground)
    "bbbbb", "b.m.b", "b...b", "b...b", "b...b",
], 5, 6)

SPRITES["inf:Bridges"] = _b([   # stone arch over the stream between settlements
    "kkkkkkkkkkkkkk", "kttttttttttttk", "kt.kkkkkkkk.tk",
    "ktk........ktk", "kk..........kk",
], 14, 6)

SPRITES["inf:Aqueducts"] = _b([   # arcade tile (repeats across the whole scene)
    "kkkkkkkk", "eeeeeeee", "tttttttt", "tttttttt", "tttttt..",
    "ttt..t..", "tt......", "tt......", "tt......", "tt......",
    "tt......", "tt......", "tt......", "tt......",
], 8, 15)

SPRITES["feet:Quarry"] = _b([   # terrain at the holding's feet
    "..kk.........kk.....", ".ktuk..kk...ktttk.k.",
    "ktttukktuk.kttuttkuk",
], 20, 4)

SPRITES["feet:Salt Works"] = _b([   # terrain at the holding's feet
    "..k..............k..", ".ksk....k.......ksk.",
    "kssskeeeseeeeeeksssk",
], 20, 4)

SPRITES["feet:Apiary"] = _b([   # terrain at the holding's feet
    "..y......y.......y..", ".l.a..l.....a..l...l",
    "llallllalllllalllall",
], 20, 4)

SPRITES["feet:Peat Bog"] = _b([   # terrain at the holding's feet
    ".l.l............l.l.", ".l.l..kk.....kk.l.l.",
    "deedeekbkdeekbkdeedd",
], 20, 4)

SPRITES["feet:Forestry"] = _b([   # terrain at the holding's feet
    ".kkkk..........kkkk.", "kbkbbk.l.....l.kbbkb",
], 20, 3)

SPRITES["feet:Fishmongery"] = _b([   # terrain at the holding's feet
    ".kk.............kk..", "kmbkeeeeeeeeeeeekbmk",
], 20, 3)

SPRITES["feet:Mine"] = _b([   # terrain at the holding's feet: loose rubble and ore, no outline (reads as rubble, not a shadow)
    ".tt.......tttt...tt.", "tuut.m.m.tuyut.tuut.",
], 20, 3)

SPRITES["feet:Arable Land"] = _b([   # terrain at the holding's feet
    "y.y.y..........y.y.y", "yyyyy..........yyyyy",
    "bybyb..........bybyb",
], 20, 4)

SPRITES["feet:Common Land"] = _b([   # terrain at the holding's feet
    ".kkk............kkk.", "ksssk...l..l...ksssk",
], 20, 3)

# ---------------------------------------------------------------- infrastructure + scenery (16)
SPRITES["scenery:tree"] = _s([          # pine pair (evergreen: keeps its needles in Winter)
    ".....n..........", "....nnn.........", "...nnnnn........", "....nnn.....n...", "...nnnnn...nnn..",
    "..nnnnnnn.nnnnn.", "...nnnnn...nnn..", "..nnnnnnn.nnnnn.", ".nnnnnnnnnnnnnnn", "..nnnnnnn..nnn..",
    ".nnnnnnnnnnnnnnn", "nnnnnnnnnn.b....", ".....b.....b....", ".....b.....b....",
], S16)
SPRITES["scenery:plot"] = _s([            # open ward: signpost
    "....kkkkkkk.....",
    "....kbbbbbk.....",
    "....kkkkkkk.....",
    "......kbk.......",
    "......kbk.......",
    "......kbk.......",
    "......kbk.......",
], S16)

# ---------------------------------------------------------------- monuments (24)
SPRITES["monument:Exalted Basilica"] = _s([
    "...........k", "..........km", "...........k", "..........kt", "..........kr",
    ".........krr", "........krrr", ".......krrrr", "......krrrkk", ".....krrrkyy",
    "....krrrrkyy", "...krrrrrkky", "..kwwwwwwwww", "..kwkykwwwww", "..kwkykwwwww",
    "..kwwwwwwkkk", "..kwkykwkddd", "..kwkykwkddd", "..kwwwwwkddd", "..kwwwwwkddd",
    "..kkkkkkkkkk",
], S24, mirror=True)
SPRITES["monument:Papal Palace"] = _s([   # gold dome, cross, flanking towers
    "...........k", "..........kk", "...........k", "..........ky", "........kkyy",
    ".......kyyyy", "......kyyyyy", "......kkkkkk", ".k.k..kwwwww", ".kkk..kwykwy",
    ".ktk..kwwwww", ".ktkkkkkkkkk", ".ktkwwwwwwww", ".ktkwykwykwy", ".ktkwwwwwwww",
    "kkkkwykwykkd", "ktttwwwwwkdd", "ktytwykwykdd", "ktttwwwwwkdd", "kkkkkkkkkkkk",
], S24, mirror=True)
SPRITES["monument:Inquisitorial Palace"] = _s([   # needle spires, red banners, barred windows
    "...........kk...........", "...........uu...........", "......k....uu....k......", "......u...kuuk...u......",
    "..k...u...kuuk...u...k..", "..u..kuk..kuuk..kuk..u..", "..u...u...kcck...u...u..", ".kuk..u...kcck...u..kuk.",
    "..u...u...kcck...u...u..", "..u...u...kuuk...u...u..", "..u...u...kuuk...u...u..", ".kukkkukkkkuukkkkukkkuk.",
    ".kucuuuuuuuuuuuuuuuucuk.", ".kucuuuuuuuuuuuuuuuucuk.", ".kucmduumduuuuumduumcuk.", ".kucdmuudmuuuuudmuudcuk.",
    ".kucdduuddkkkkudduudcuk.", ".kuuuuuuuukddkuuuuuuuuk.", ".kuuuuuuuukddkuuuuuuuuk.", ".kuuuuuuuukddkuuuuuuuuk.",
    ".kuuuuuuuukddkuuuuuuuuk.", ".kuuuuuuuukddkuuuuuuuuk.", ".kuuuuuuuukddkuuuuuuuuk.",
], S24)
SPRITES["monument:Preceptory of the Knight's Templar"] = _s([   # keep with red-cross banner
    "...........k", "..........kk", "..........kc", "..........kc", "..........k.",
    "..k.k.k...k.", "..kkkkk..kkk", "..ktttk..ktt", "..ktytk.kttt", "..ktttk.ktsc",
    "..ktttkkktcc", "..ktttttttsc", "kkkkkkkkkkkk", "kttttttttttt", "ktytkttttttt",
    "ktttkttttkkk", "kttttttttkdd", "ktytkttttkdd", "ktttkttttkdd", "kkkkkkkkkkkk",
], S24, mirror=True)
SPRITES["monument:Senate Hall"] = _s([     # pediment and columns
    ".........kkk", ".......kkttt", ".....kkttttt", "...kktttyttt", ".kkttttttttt",
    "kkkkkkkkkkkk", "kttttttttttt", "kkkkkkkkkkkk", ".kwk.kwk.kwk", ".kwk.kwk.kwk",
    ".kwk.kwk.kwk", ".kwk.kwk.kwk", ".kwk.kwk.kwk", ".kwk.kwk.kwk", ".kwk.kwk.kwk",
    "kkkkkkkkkkkk", "kttttttttttt", "kkkkkkkkkkkk",
], S24, mirror=True)
SPRITES["monument:Studium Generale"] = _s([   # college: clock tower, many windows
    "..........kk", ".........krr", "........krrr", "........kttt", "........ktky",
    "........ktty", "........kttt", "..kkkkkkkttt", ".krrrrrrrkkk", "krrrrrrrrrrr",
    "kkkkkkkkkkkk", "kwwwwwwwwwww", "kwykwykwykwy", "kwykwykwykwy", "kwwwwwwwwwww",
    "kwykwykwykkd", "kwwwwwwwwkdd", "kwwwwwwwwkdd", "kkkkkkkkkkkk",
], S24, mirror=True)
SPRITES["monument:Imperial Palace"] = _s([   # three domes, royal banners
    "..k........k", "..kaa......k", "..kaa.....kk", "..k......kyy", ".kkk....kyyy",
    "kyyyk..kyyyy", "kyyyk..kkkkk", "kkkkkkkkwwww", "kwwwwwwkwyyw", "kwywwywkwyyw",
    "kwwwwwwkwwww", "kkkkkkkkkkkk", "kwwwwwwwwwww", "kwykwykwykwy", "kwwwwwwwwwww",
    "kwykwykwykkd", "kwwwwwwwwkdd", "kwykwykwwkdd", "kkkkkkkkkkkk",
], S24, mirror=True)
SPRITES["monument:Royal Pavilion"] = _s([   # arena of arches behind a broad royal pavilion
    "...........kkcc.........", "...........kkc..........", "...........kk...........", "..kcc......kk......cck..",
    "..kc......kayk.....c.k..", "..k......kaayyk......k..", "..k.....kyaayyak.....k..", "..k....kyyaayyaak....k..",
    "..kkkkkayyaayyaaykkkkk..", ".ktttkaayyaayyaayyktttk.", "kttttkaayyaayyaayykttttk", "kttttykykykykykykykttttk",
    "kddtdkaayyaayyaayykddtdd", "kddtdkaayyaayyaayykddtdd", "kddtdkaayyaayyaayykddtdd", "kttttkaayykddkaayykttttk",
    "kttttkaayykddkaayykttttk", "kddtdkaayykddkaayykddtdd", "kddtdkaayykddkaayykddtdd", "kddtdkaayykddkaayykddtdd",
    "kddtdkaayykddkaayykddtdd", "kttttkaayykddkaayykttttk",
], S24)
SPRITES["monument:Manor House"] = _s([     # manor, twin chimneys, garden hedges
    "....kk......", "....kk......", "..kkkkkkkkkk", ".krrrrrrrrrr", "krrrrrrrrrrr",
    "kkkkkkkkkkkk", ".kwwwwwwwwww", ".kwykwykwykw", ".kwwwwwwwwww", ".kwykwykwkkk",
    ".kwwwwwwwkdd", ".kwwwwwwwkdd", "kkkkkkkkkkkk", "kllllk......", "kllllk......",
], S24, mirror=True)
SPRITES["monument:Aristocratic Court"] = _s([   # palace front, gold trim, royal banners
    "..k.........", "..kaa.......", "..kaa...kkkk", "..k....kyyyy", ".kkk..kyrrrr",
    ".kyk.kyrrrrr", ".ktk.kkkkkkk", ".ktkkwwwwwww", ".ktkkwykwykw", ".ktkkwwwwwww",
    "kkkkkkkkkkkk", "kyyyyyyyyyyy", "kwwwwwwwwwww", "kwykwykwykwy", "kwwwwwwwwkkk",
    "kwykwykwwkdd", "kwwwwwwwwkdd", "kkkkkkkkkkkk",
], S24, mirror=True)
SPRITES["monument:Office of Works"] = _s([   # scaffolded tower under construction
    "......kkkkkk", "......kttttt", "......ktuttt", "...kkkkkkkkk", "...b..ktttt.",
    "...bkkkkkkkk", "...b..kttutt", "...b..kttttt", "...bkkkkkkkk", "...b..kttttt",
    "...b..ktuttt", "...bkkkkkkkk", "...b..ktttkk", "...b..ktttkd", "...b..ktttkd",
    "kkkkkkkkkkkk",
], S24, mirror=True)
SPRITES["monument:Ministry of Military Strategy"] = _s([   # clock tower and spire, crossed swords, watchtower, red banners
    "............k...........", "...........kak..........", "..........kaaak.........", ".........kkkkkkk.k.k.k.k",
    ".........ktttttk.kkkkkkk", "....kk...ktttttk.ktttttk", "...krrk..ktkyktk.ktttttk", "..krrrrk.ktykytk.ktttttk",
    ".krrrrrrkktkyktk.kttdttk", "krrrrrrrrktttttk.kctttck", "kkkkkkkkkktttttk.kctttck", "kkkkkkkkkktytytk.kctttck",
    "ktmtttttmktytytk.kctdtck", "kctmtttmcktttttk.kctttck", "kcttmtmtcktttttk.ktttttk", "kctttmttcktttttk.ktttttk",
    "kcttmtmtcktkkktk.kttdttk", "kttttttttktdddtk.ktttttk", "ktttddtttktdddtk.ktttttk", "ktttddtttktdddtk.ktttttk",
    "ktttddtttktdddtk.ktttttk", "ktttddtttktdddtk.ktttttk", "kkkkkkkkkktdddtk.kkkkkkk",
], S24)
SPRITES["monument:Whispering Undercroft"] = _s([   # crypt stair under a small shrine
    "..........kk", ".........kuu", "........kuuu", ".......kuuuu", "......kkkkkk",
    ".......kuuuu", ".......kudku", ".......kudku", ".......kuuuu", "kkkkkkkkkkkk",
    "kuuuuuuuuuuu", "kuuuukdddddd", "kuuukdkkkkkk", "kuukdkkdddddd"[:12], "kukdkkdkkkkk",
    "kkkkkkkkkkkk",
], S24, mirror=True)
SPRITES["monument:Outrider Intercept Post"] = _s([   # timber watchtower on stilts
    "........kkkk", ".......kbbbb", "......kbbbbb", "......kkkkkk", ".......kbbbb",
    ".......kbdyd", ".......kbbbb", ".......kkkkk", "........kb..", "........kbk.",
    "........kb.k", "........kb..", "........kbk.", "........kb.k", "........kb..",
    ".......kkbk.",
], S24, mirror=True)
SPRITES["monument:Thieves' Guild"] = _s([   # crooked dark townhouse, hanging sign, lantern
    "..........kk............",
    ".........kuuk...........",
    "........kuuuuk..........",
    ".......kuuuuuuk.........",
    "......kuuuuuuuuk........",
    ".....kkkkkkkkkkkk.......",
    "......kuuuuuuuuk........",
    "......kudkuudkuk........",
    "......kuuuuuuuuk.kkkk...",
    "......kuuuuuuuukkk..k...",
    "......kudkuudkuk.kbbk...",
    "......kuuuuuuuuk.kbbk...",
    ".....kkkkkkkkkkkk.kk....",
    ".....kuuuuuuuuuuk.......",
    ".....kudkuukdkuuk...k...",
    ".....kuuuuukdkuuk..kyk..",
    ".....kuuuuukdkuuk...k...",
    ".....kuuuuukdkuuk...k...",
    ".....kkkkkkkkkkkk..kkk..",
], S24)
SPRITES["monument:Outlaw Rookery"] = _s([   # ramshackle shacks on stilts, crows
    "...k.k..................",
    "....k.......k.k.........",
    ".............k..........",
    "..........kkk...........",
    ".........kbbbk..........",
    "........kbbbbbk.........",
    ".......kkkkkkkkk........",
    "...kkk..kbbdbbk..kkk....",
    "..kbbbk.kbbdbbk.kbbbk...",
    ".kbbbbbkkbbbbbkkbbbbbk..",
    ".kkkkkkk.kkkkkk.kkkkkkk.",
    "..kbdbk...kbk....kbbdk..",
    "..kbdbk...kbk....kbbdk..",
    "..kkkkk...kbk....kkkkk..",
    "...k.k.....k......k.k...",
    "...k.k.....k......k.k...",
    "...k.k.....k......k.k...",
], S24)
SPRITES["monument:Plague Pit"] = _s([    # pit with bones, warning sign
    "..............k.........",
    ".............kbk........",
    "..........kkkkkkkk......",
    "..........kcccccck......",
    "..........kkkkkkkk......",
    "..............kbk.......",
    "..............kbk.......",
    "..............kbk.......",
    "....kk........kbk.......",
    "...kssk.......kbk..kk...",
    "...ksdk.......kbk.kssk..",
    ".kkkkkkkkkkkkkkkkkkkkkkk",
    ".kduuduuuduuuduuuduuuk..",
    "..kuusuuuuuusuuuuusuk...",
    "...kkkkkkkkkkkkkkkkkk...",
], S24)
SPRITES["monument:Baggage Train"] = _s([   # two wagons and a mule
    "........................",
    "..kkkkkk.......kkkkkk...",
    ".ksssssk......ksssssk...",
    ".ksssssk......ksssssk...",
    "kbbbbbbbk....kbbbbbbbk..",
    "kbbbbbbbkkkkkkbbbbbbbkkk",
    ".kkkkkkkk....kkkkkkkk.kk",
    ".kmk..kmk....kmk..kmkkbk",
    "kmbmkkmbmk..kmbmkkmbmkbk",
    ".kmk..kmk....kmk..kmk.kk",
], S24)
SPRITES["monument:Artillery Park"] = _s([   # trebuchet and stacked shot
    "..........kkkkkkkkkk....",
    ".........kbbk.......k...",
    "........kbbk........m...",
    ".......kbbk........kmk..",
    "......kbbk.........kmk..",
    ".....kbbk...............",
    "....kbbk................",
    "...kbbkk................",
    "...kmmmk................",
    "..kbkkkbk...............",
    "..kb...bk...............",
    ".kb.....bk.......kk.....",
    ".kb.....bk......kmmk....",
    "kbbbbbbbbbk....kmmmmk...",
    "kmk.....kmk...kmmkmmk...",
    "kkk.....kkk...kkkkkkk...",
], S24)
SPRITES["monument:Advanced Blast Furnace"] = _s([   # tall stack, glowing furnace
    "...ss...................",
    "..s.....................",
    "...ss...................",
    "..kkkk..................",
    "..kuuk..................",
    "..kuuk..................",
    "..kuuk..................",
    "..kuuk..kkkk............",
    "..kuuk.kuuuuk...........",
    "..kuukkuuuuuuk..........",
    ".kkuuuuuuuuuuuk.........",
    ".kuuuuuuuuuuuuuk........",
    ".kuuuukkkkkuuuuk........",
    ".kuuukfffffkuuuk.kkkkkk.",
    ".kuuukfyyyfkuuuk.kbbbbk.",
    ".kuuukfyyyfkuuukkkbbbbk.",
    ".kuuukfffffkuuuk.kmmmmk.",
    ".kkkkkkkkkkkkkkk.kkkkkk.",
], S24)
SPRITES["monument:Port Authority"] = _s([   # harbour office on a pier, flag, water
    ".....k..................",
    ".....kaa................",
    ".....kaa................",
    ".....k..................",
    "...kkkkk................",
    "..krrrrrk...............",
    ".krrrrrrrk..............",
    "kkkkkkkkkkk.............",
    ".kwwwwwwwk..............",
    ".kwykwykwk..............",
    ".kwwwwwwwk..............",
    ".kwwwkdkwk..............",
    ".kwwwkdkwk..............",
    "kkkkkkkkkkkkkkkkkkkkkkkk",
    "kbbbbbbbbbbbbbbbbbbbbbbk",
    "kkbkkkkbkkkkbkkkkbkkkkbk",
    "eekeeeekeeeekeeeekeeeeke",
    "eeeeeeeeeeeeeeeeeeeeeeee",
], S24)

# ---------------------------------------------------------------- wonders (24)
SPRITES["wonder:Colossus"] = _s([         # bronze figure on a plinth, raised torch
    "........f...............",
    ".......kfk..............",
    ".......kmk..............",
    ".......kmk..kkk.........",
    ".......kmk.kmmmk........",
    "........kmkkmmmk........",
    ".........kmmmmmk........",
    "..........kmmmmmk.......",
    "..........kmmmmmmk......",
    "..........kmmmmkmk......",
    "..........kmmmmk.mk.....",
    "..........kmmmmk........",
    "..........kmmmmk........",
    "..........kmk.kmk.......",
    "..........kmk.kmk.......",
    "..........kmk.kmk.......",
    "........kkkkkkkkkk......",
    "........kttttttttk......",
    "........ktuttttutk......",
    "........kttttttttk......",
    ".......kkkkkkkkkkkk.....",
], S24)
SPRITES["wonder:The Grand Exchange"] = _s([   # domed exchange hall, gold
    "..........ky", ".........kyy", "........kyyy", ".......kyyyy", "......kkkkkk",
    "......kwwwww", "....kkkkkkkk", "...kyyyyyyyy", "..kkkkkkkkkk", "..kwkwkwkwkw",
    "..kwkwkwkwkw", "..kwkwkwkwkw", "..kwkwkwkwkk", "..kwkwkwkwkd", "..kwkwkwkwkd",
    "kkkkkkkkkkkk", "kyyyyyyyyyyy", "kkkkkkkkkkkk",
], S24, mirror=True)
SPRITES["wonder:The Eternal Sepulchre"] = _s([   # stepped tomb
    "...........k", "..........kt", ".........ktt", "........kttt", ".......kkkkk",
    ".......ktttt", "......kkkkkk", "......kttttt", ".....kkkkkkk", ".....ktuttt",
    "....kkkkkkkk", "....kttttttt", "...kkkkkkkkk", "...kttuttkkk", "..kkkkkkkkdd",
    "..kttttttkdd", ".kkkkkkkkkdd", "kkkkkkkkkkkk",
], S24, mirror=True)
SPRITES["wonder:High Chancery"] = _s([    # tall seat of government, clock and spires
    ".....k.....k", ".....k.....k", "....kkk...kr", "....krk..krr", "....krk.krrr",
    "....ktk.kttt", "....ktk.ktyy", "....ktk.ktyy", "....ktkkkttt", "..kkkkkkkkkk",
    ".krrrrrrrrrr", "krrrrrrrrrrr", "kkkkkkkkkkkk", "kwwwwwwwwwww", "kwykwykwykwy",
    "kwwwwwwwwwww", "kwykwykwwkkk", "kwwwwwwwwkdd", "kwykwykwwkdd", "kkkkkkkkkkkk",
], S24, mirror=True)


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
    "Bridges": ("gap", ""), "Aqueducts": ("span", ""), "Hitching Post": ("front", ""),
}
# display only: when both are built, draw the upgrade (data: Stone Roads requires Dirt Roads,
# Stone Walls requires Wooden Walls)
INFRA_SUPERSEDES = {"Stone Roads": "Dirt Roads", "Stone Walls": "Wooden Walls"}
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
    if key.startswith(("sky:", "inf:", "feet:")):
        return None          # free size: checked for consistency only
    if key.startswith(("monument:", "wonder:")):
        return S24, S24
    return S16, S16


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
        if any(c != "g" for c in rows[-1]):
            out.append(f"{key}: last row is not ground")
        elif all(len(r) == w for r in rows):
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
    for n in infra - set(SKYLINE):
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
  const hide=new Set(Object.keys(D.SUP).map(k=>D.SUP[k]));const on=n=>all&&!hide.has(n);
  for(let x=0;x<W;x+=w("sky:fill:"+t)+1)at("sky:fill:"+t,x);
  const cw=w("sky:core:"+t),cx=Math.floor((W-cw)/2);
  if(on("Cathedral"))at("inf:Cathedral",Math.floor((W-w("inf:Cathedral"))/2));
  if(on("Library"))at("inf:Library",Math.max(0,cx-w("inf:Library")+3));
  if(on("Town Hall"))at("inf:Town Hall",Math.min(W-w("inf:Town Hall"),cx+cw-3));
  at("sky:core:"+t,cx);
  if(on("Muster Field"))at("inf:Muster Field",0);if(on("Garrison"))at("inf:Garrison",W-w("inf:Garrison"));
  ["Stone Walls","Wooden Walls"].filter(on).forEach(n=>{for(let x=0;x<W;x+=w("inf:"+n))at("inf:"+n,x);
    if(D.S["inf:"+n+":tower"]){at("inf:"+n+":tower",0);at("inf:"+n+":tower",W-w("inf:"+n+":tower"));}});}
if(D.T.length){g=sec("settlement skylines (faded 20% toward the sky); Town+ also shown with every skyline infrastructure piece");
 D.T.forEach(t=>{const W=72,H=40,G=H-6;[false,true].forEach(all=>{if(all&&D.NI.includes(t))return;
  cell(g,W,H,t+(all?" + infra":""),c=>{c.fillStyle=SKY;c.fillRect(0,0,W,G+1);c.fillStyle=GR;c.fillRect(0,G+1,W,H-G-1);skyline(c,t,W,G,all);});});});}
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