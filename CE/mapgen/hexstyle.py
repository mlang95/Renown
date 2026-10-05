#!/usr/bin/env python3
"""hexstyle.py - the ONE source for how a board looks.

Two things live here and nowhere else:

  GLYPHS    ink symbol per terrain. The glyph, not the colour, is what says
            "this is forest". Colour is free to shift by region; the glyph
            never does. Drawn on hexgen's 120x108 tile canvas, centre (60,54),
            kept clear of the resource badge (top-right, 86,30 r17).

  CLIMATES  per-region colour sets. A preset names one (region_presets
            `climate=`). Water stays in the blue family in every climate.

Consumers:
  hexgen.terrain()      -> print tiles (build_board)
  build_mapapp.py       -> bakes STYLE into renown-maps.html
Neither re-declares a colour or a glyph.

Glyph markup conventions (so one string serves SVG-in-browser and svglib):
  stroke="currentColor"  -> the ink tone; Python substitutes the literal
  shapes with NO fill attr inherit the tile fill (occlude what's behind)
  fill="none"            -> line art
"""
from __future__ import annotations

INK = "#2b241b"          # glyph ink on light fills
LIGHT = "#f3ead3"        # glyph ink on dark fills
GRID = "#2b241b"         # hex edge
GRID_OPACITY = 0.22
COAST_W = 4.2            # coastline stroke, tile units (R=54)
GLYPH_W = 3.4            # glyph stroke, tile units
GLYPH_OPACITY = 0.88
LUM_SPLIT = 0.26         # fill luminance below this -> LIGHT glyph

TERRAINS = ("plains", "forest", "wetland", "tundra", "mountain", "water")

# ── glyphs ──────────────────────────────────────────────────────────────────
_L = 'fill="none" stroke="currentColor"'          # line art
_S = 'stroke="currentColor"'                      # occluding shape

GLYPHS = {
    # grassland is the blank ground: no glyph
    "plains": "",

    # rolling humps with right-flank hatching (tactical Hill, plains only)
    "hill": (
        f'<path {_S} d="M48 74 Q68 34 90 74 Z"/>'
        f'<path {_L} d="M75 55 l-4 8 M81 63 l-4 8"/>'
        f'<path {_S} d="M24 84 Q44 44 68 84 Z"/>'
        f'<path {_L} d="M51 64 l-4 8 M57 72 l-4 8"/>'),

    # three separate conifers (pine/redwood), staggered, not touching
    "forest": (
        f'<path {_L} d="M38 84 V80"/>'
        f'<polygon {_S} points="29,80 38,64 47,80"/>'
        f'<polygon {_S} points="31.2,70 38,52 44.8,70"/>'
        f'<path {_L} d="M58 68 V64"/>'
        f'<polygon {_S} points="49,64 58,48 67,64"/>'
        f'<polygon {_S} points="51.2,54 58,36 64.8,54"/>'
        f'<path {_L} d="M80 88 V84"/>'
        f'<polygon {_S} points="71,84 80,68 89,84"/>'
        f'<polygon {_S} points="73.2,74 80,56 86.8,74"/>'),

    # marsh: one small dead snag, one reed tuft, a few short still-water
    # dashes. Dashes sit on the shared 23.4 pitch so neighbouring hexes keep
    # a common rhythm without forming continuous lines.
    "wetland": (
        f'<path {_L} stroke-width="1.8" d="M30 30.6 H44 M64 54.0 H84 M26 77.4 H38 M54 77.4 H70"/>'
        f'<path {_L} d="M42 77.4 C42 70 40 64 41 57 '
        f'M41 67 L35 62 L33 57 M41 62 L46 57 L47 52 M41 58 L37 52"/>'
        f'<path {_L} stroke-width="2.4" d="M74 54 l0 -9 M70 54 l-2 -7 M78 54 l2 -7"/>'),

    # tundra (fell-field): monoline like the rest of the set - three faceted
    # boulders (tile-fill, ink outline) with mountain-style flank hatching,
    # and low two-lobed shrub mounds. Boulder shapes seeded once, frozen.
    "tundra": (
        f'<path {_L} d="M48 92 q3 -5 6 0 q3 -5 6 0 M80 58 q3 -5 6 0 q3 -5 6 0 M30 48 q3 -5 6 0 q3 -5 6 0 M64 66 q3 -5 6 0 q3 -5 6 0"/>'
        f'<path {_S} d="M30 72 Q28 71 28 69 L30 62 Q30 60 32 60 L41 58 Q43 58 45 60 L55 65 Q57 67 57 68 L54 73 Q53 75 51 75 L42 77 Q39 77 37 76 Z M78 88 Q76 89 75 88 L70 86 Q68 85 68 84 L68 78 Q68 77 69 77 L75 76 Q76 76 77 76 L81 77 Q82 78 83 79 L85 85 Q85 87 84 87 Z M66 46 Q66 47 66 48 L65 51 Q64 51 63 51 L59 50 Q58 50 57 49 L53 47 Q52 47 53 46 L57 43 Q58 42 59 42 L62 41 Q63 40 63 42 Z"/>'
        f'<path {_L} stroke-width="2.6" d="M48 67 l-3.5 7.0 M45 72 l-3.5 7.0 M80 82 l-2.2 4.5 M78 85 l-2.2 4.5 M63 46 l-1.8 3.5 M61 48 l-1.8 3.5"/>'),

    # twin peaks, hatched shadow flank
    "mountain": (
        f'<polygon {_S} points="28,82 44,54 60,82"/>'
        f'<polygon {_S} points="42,86 64,40 88,86"/>'
        f'<path {_L} d="M71 55 l-5 10 M77 67 l-5 10 M83 79 l-3 6"/>'),

    # water is identified by colour + the coastline: no glyph
    "water": "",
}

# ── climates ────────────────────────────────────────────────────────────────
# Sampled from the world map (map7.png): dominant colours per region box.
# Water is the map's sea teal in every climate, lightened for shallows.
_T = {"plains": "#7fa452", "forest": "#24502a", "wetland": "#556b4a",
      "tundra": "#8b6a45", "mountain": "#6e6a62", "water": "#4e7470"}


def _c(label, **kw):
    d = dict(_T); d.update(kw); d["label"] = label
    return d


CLIMATES = {
    # Vaelohk, Twelfth Reach: deep greens, tan interior
    "temperate": _c("Temperate"),
    # Draggath / Glen / Bleak: orange-gold badlands
    "wastes":    _c("Wastes", plains="#d29a3a", forest="#4a5a26", tundra="#a8732f",
                    mountain="#7d6a55", water="#4a6f6c"),
    # Drakenhart / Hermit's Row: pale cream-sand
    "steppe":    _c("Steppe", plains="#c2ad7a", forest="#4f5a3a", wetland="#7a7458",
                    tundra="#9c8458", mountain="#8a8070", water="#4c726f"),
    # Fair Whitewood / Lenaveron / Tombs: snow-grey
    "frozen":    _c("Frozen", plains="#b0ad9e", forest="#3a4a3a", wetland="#7a7a68",
                    tundra="#e8e8e2", mountain="#74716b", water="#5a7a78"),
    # Blighthold: olive-khaki heath, near-black forest
    "heath":     _c("Heath", plains="#8f8456", forest="#1d3d12", wetland="#5e5634",
                    tundra="#7c5f3e", mountain="#6e675a"),
    # Coloured Mountains / Crag Pass: ochre-brown valleys, grey rock
    "uplands":   _c("Uplands", plains="#9a8150", forest="#3a3f1e", wetland="#5e5a3a",
                    tundra="#7a5a33", mountain="#7a7466"),
    # Dreadwood: saturated green
    "lush":      _c("Lush", plains="#5f9435", forest="#1d5210", wetland="#3f5f2a",
                    water="#456b66"),
    # Lost Woods: dark olive-brown old growth
    "deepwood":  _c("Deepwood", plains="#6f6c38", forest="#283412", wetland="#4a4a26",
                    water="#455f55"),
    # Shallow Mire / Quiet Hollow: khaki-olive
    "mire":      _c("Mire", plains="#8a8250", forest="#3a4422", wetland="#625a38",
                    water="#4f6a5c"),
    # Marrow Shoals: vivid island green, light shallows
    "warm":      _c("Warm coast", plains="#6f9c3e", forest="#285a2a", wetland="#4f6c45",
                    water="#4f8077"),
    # Wheat Fields: olive-gold
    "olive":     _c("Olive", plains="#9c9548", forest="#3a4a1e", wetland="#5e5f36"),
    # Scarlet Forest: by request (map7 does not show it red)
    "scarlet":   _c("Scarlet", plains="#bc5442", forest="#7a2224", wetland="#6d4038"),
    # monochrome print: glyphs carry everything
    "ink":       _c("Print (ink)", plains="#ffffff", forest="#c8c8c8", wetland="#e0e0e0",
                    tundra="#f4f4f4", mountain="#8c8c8c", water="#dcdcdc"),
}
DEFAULT_CLIMATE = "temperate"


def colors(climate=None):
    c = CLIMATES.get(climate or DEFAULT_CLIMATE, CLIMATES[DEFAULT_CLIMATE])
    return {t: c[t] for t in TERRAINS}


# ── tone rule (mirrored in app_shell.html glyphTone) ────────────────────────
def luminance(hexcol):
    h = hexcol.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda v: v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def tone(fill):
    return LIGHT if luminance(fill) < LUM_SPLIT else INK


def lighten(hexcol, k=1.16):
    h = hexcol.lstrip("#")
    return "#" + "".join(f"{min(255, round(int(h[i:i+2], 16) * k)):02x}"
                         for i in (0, 2, 4))


SHADE_K, HILITE_K, DEEP_K = 0.80, 1.14, 0.58   # relief tones, relative to the tile fill


def glyph_svg(kind, fill):
    """Glyph fragment ready for svglib: literal colours, inherited fill.
    SHADE / HILITE tokens are relief tones derived from the fill."""
    ink = tone(fill)
    body = (GLYPHS[kind].replace("currentColor", ink)
            .replace('"SHADE"', f'"{lighten(fill, SHADE_K)}"')
            .replace('"HILITE"', f'"{lighten(fill, HILITE_K)}"')
            .replace('"DEEP"', f'"{lighten(fill, DEEP_K)}"'))
    return (f'<g fill="{fill}" stroke-width="{GLYPH_W}" stroke-linecap="round" '
            f'stroke-linejoin="round" opacity="{GLYPH_OPACITY}">{body}</g>')


def export():
    """Everything the browser app needs, as JSON-safe data."""
    return {"ink": INK, "light": LIGHT, "grid": GRID, "grid_opacity": GRID_OPACITY,
            "coast_w": COAST_W, "glyph_w": GLYPH_W, "glyph_opacity": GLYPH_OPACITY,
            "lum_split": LUM_SPLIT, "glyphs": GLYPHS,
            "shade_k": SHADE_K, "hilite_k": HILITE_K, "deep_k": DEEP_K, "climates": CLIMATES,
            "default_climate": DEFAULT_CLIMATE}
