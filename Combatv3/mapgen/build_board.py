#!/usr/bin/env python3
"""build_board.py - print-and-tape Renown board from a procedural map.

Drives off mapgen.generate() (the real pipeline: coastline/rivers/lakes/
ranges/forests/wetlands/tundra/regions/resources on the hexmap territory
graph). Composites hexgen terrain + resource art per hex, tessellates flat-top
(odd-q, matching hexmap) and slices across numbered A4 pages. Trim to the
corner marks, butt pages edge-to-edge, tape to cardboard.

Usage:
    python build_board.py 24 20 --seed 11 --hex 20 --out board.pdf
    python build_board.py 32 26 --seed 7  --hex 20 --param players=6 --param forests=14
Or import generate_board(...).
"""
import math, re, argparse, os, tempfile
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.units import mm
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF, renderPM

import hexgen   # art pipeline: terrain(), resource(), resource_apiary(), constants
import mapgen   # procedural map pipeline -> HexMap

_TMPDIR = tempfile.gettempdir()         # cross-platform (Windows-safe)

H_CX, H_CY, H_R = hexgen.CX, hexgen.CY, hexgen.R          # 60, 54, 54 (px)

# mapgen terrain "plains" has no hexgen tile -> render as grassland
TERRAIN_ART = {"plains": "grassland", "forest": "forest", "mountain": "mountain",
               "water": "water", "wetland": "wetland", "tundra": "tundra"}
# mapgen resource keys -> hexgen resource icon (apiary handled separately)
RES_ART = {"mine": "ore", "quarry": "stone", "arable": "grain",
           "forestry": "wood", "salt": "salt"}

PAPER = {"A4": (210.0, 297.0), "letter": (215.9, 279.4)}  # mm portrait


def _strip(svg):
    return re.sub(r"^<svg[^>]*>", "", svg)[:-len("</svg>")]


def _terrain_bodies():
    return {t: _strip(hexgen.terrain(art)) for t, art in TERRAIN_ART.items()}


def _resource_body(res):
    if res == "apiary":
        return _strip(hexgen.resource_apiary())
    icon = RES_ART.get(res)
    return _strip(hexgen.resource(icon)) if icon else ""


def _hex_center(col, row, R, dx, dy):
    """Flat-top odd-q (matches hexmap): odd columns shoved down half a row."""
    cx = R + col * dx
    cy = (R * math.sqrt(3) / 2) + row * dy + (dy / 2 if col % 2 == 1 else 0.0)
    return cx, cy


def _page_svg(window, hexes, R, page_wmm, page_hmm, margin):
    bx0, by0, win_w, win_h = window
    s = R / H_R
    txp = margin - bx0
    typ = margin - by0
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" '
             f'width="{page_wmm}mm" height="{page_hmm}mm" '
             f'viewBox="0 0 {page_wmm} {page_hmm}">',
             f'<clipPath id="cw"><rect x="{margin}" y="{margin}" '
             f'width="{win_w}" height="{win_h}"/></clipPath>',
             '<g clip-path="url(#cw)">']
    for (cx, cy, body) in hexes:
        gx = txp + cx - H_CX * s
        gy = typ + cy - H_CY * s
        parts.append(f'<g transform="translate({gx:.3f},{gy:.3f}) scale({s:.5f})">{body}</g>')
    parts.append('</g></svg>')
    return "".join(parts)


def _trim_and_label(c, page_wmm, page_hmm, margin, label):
    c.setLineWidth(0.5); c.setStrokeColorRGB(0, 0, 0)
    L = 5 * mm
    x0, y0 = margin * mm, margin * mm
    x1, y1 = (page_wmm - margin) * mm, (page_hmm - margin) * mm
    for (x, y) in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
        c.line(x - L, y, x + L, y); c.line(x, y - L, x, y + L)
    c.setFont("Helvetica", 8); c.setFillColorRGB(0, 0, 0)
    c.drawString(x0, y1 + 2 * mm, label)


def _render_board_png(placed, board_w, board_h, R, out_png, settlements=None,
                      max_px=1600):
    """Render the entire board to a single PNG (whole-map preview), with the
    settlement triangles drawn on top: capital = filled dot, others = hollow."""
    s = R / H_R
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" '
             f'width="{board_w}mm" height="{board_h}mm" '
             f'viewBox="0 0 {board_w} {board_h}">',
             f'<rect x="0" y="0" width="{board_w}" height="{board_h}" fill="#e9ddc2"/>']
    for (cx, cy, body) in placed:
        gx = cx - H_CX * s
        gy = cy - H_CY * s
        parts.append(f'<g transform="translate({gx:.3f},{gy:.3f}) scale({s:.5f})">{body}</g>')
    # settlement overlays
    if settlements:
        dx, dy = 1.5 * R, math.sqrt(3) * R
        rad, sw = R * 0.34, R * 0.10
        for settles in settlements:
            pts = [_hex_center(c, r, R, dx, dy) for (c, r) in settles]
            poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
            parts.append(f'<polygon points="{poly}" fill="none" stroke="#c01616" '
                         f'stroke-width="{sw:.2f}" stroke-dasharray="{R*0.2:.1f} {R*0.15:.1f}"/>')
            cx0, cy0 = pts[0]
            parts.append(f'<circle cx="{cx0:.1f}" cy="{cy0:.1f}" r="{rad:.1f}" '
                         f'fill="#c01616" stroke="#222" stroke-width="{sw:.2f}"/>')
            for (x, y) in pts[1:]:
                parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rad:.1f}" '
                             f'fill="#fff" stroke="#222" stroke-width="{sw:.2f}"/>')
    parts.append('</svg>')
    tmp = os.path.join(_TMPDIR, "_board_preview.svg")
    with open(tmp, "w") as f:
        f.write("".join(parts))
    dpi = max_px * 25.4 / max(board_w, board_h)        # cap longest side ~max_px
    renderPM.drawToFile(svg2rlg(tmp), out_png, fmt="PNG", dpi=dpi)


def generate_board(width, height, *, seed=7, place_resources=True,
                   out_pdf="renown_board.pdf", hex_mm=40.0, paper="A4",
                   margin_mm=6.0, mapgen_params=None):
    """Generate a numbered, tileable A4 PDF board from mapgen.

    width, height   : hex grid dimensions (passed to mapgen).
    seed            : mapgen seed (deterministic).
    place_resources : stamp raw-material toppers (else terrain only).
    hex_mm          : center-to-corner radius in mm.
    mapgen_params   : dict of extra mapgen PARAMS overrides (players, forests=...).
    """
    if paper not in PAPER:
        raise ValueError(f"paper must be one of {list(PAPER)}")
    mp = dict(mapgen_params or {})
    m = mapgen.generate(width=width, height=height, seed=seed, **mp)

    R = float(hex_mm)
    dx = 1.5 * R
    dy = math.sqrt(3) * R
    tbody = _terrain_bodies()

    placed = []
    for h in m.all():
        cx, cy = _hex_center(h.col, h.row, R, dx, dy)
        body = tbody[h.terrain]
        if place_resources and h.resource:
            body = body + _resource_body(h.resource)
        placed.append((cx, cy, body))

    xs = [p[0] for p in placed]; ys = [p[1] for p in placed]
    board_w = max(xs) + R
    board_h = max(ys) + R * math.sqrt(3) / 2

    page_wmm, page_hmm = PAPER[paper]
    win_w = page_wmm - 2 * margin_mm
    win_h = page_hmm - 2 * margin_mm
    pcols = math.ceil(board_w / win_w)
    prows = math.ceil(board_h / win_h)

    c = rl_canvas.Canvas(out_pdf, pagesize=(page_wmm * mm, page_hmm * mm))
    n = 0
    for pr in range(prows):
        for pc in range(pcols):
            bx0, by0 = pc * win_w, pr * win_h
            sel = [p for p in placed
                   if bx0 - R <= p[0] <= bx0 + win_w + R
                   and by0 - R <= p[1] <= by0 + win_h + R]
            svg = _page_svg((bx0, by0, win_w, win_h), sel, R, page_wmm, page_hmm, margin_mm)
            tmp = os.path.join(_TMPDIR, f"_pg_{pr}_{pc}.svg")
            with open(tmp, "w") as f:
                f.write(svg)
            renderPDF.draw(svg2rlg(tmp), c, 0, 0)
            label = (f"Renown  {width}x{height}  seed={seed}  | "
                     f"page col {pc} row {pr}  (of {pcols}x{prows})")
            _trim_and_label(c, page_wmm, page_hmm, margin_mm, label)
            c.showPage()
            n += 1
    c.save()
    out_png = os.path.splitext(out_pdf)[0] + ".png"
    try:
        _render_board_png(placed, board_w, board_h, R, out_png,
                          settlements=getattr(m, "settlements", None))
    except Exception as e:                 # preview is non-essential; PDF is the deliverable
        out_png = f"(preview failed: {e})"
    terr, res, regions = mapgen.stats(m)
    return {"pdf": out_pdf, "png": out_png, "pages": n, "page_grid": (pcols, prows),
            "board_mm": (round(board_w, 1), round(board_h, 1)),
            "terrain": dict(terr), "resources": dict(res),
            "regions": dict(sorted(regions.items()))}


def _coerce(v):
    try:
        return int(v)
    except ValueError:
        try:
            return float(v)
        except ValueError:
            return v


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("width", type=int)
    ap.add_argument("height", type=int)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--hex", type=float, default=40.0, dest="hex_mm")
    ap.add_argument("--paper", default="A4")
    ap.add_argument("--margin", type=float, default=6.0, dest="margin_mm")
    ap.add_argument("--no-resources", action="store_true")
    ap.add_argument("--param", action="append", default=[],
                    help='mapgen override, e.g. --param players=6 --param forests=14')
    ap.add_argument("--out", default="renown_board.pdf", dest="out_pdf")
    a = ap.parse_args()
    mparams = {}
    for kv in a.param:
        k, v = kv.split("=", 1)
        mparams[k] = _coerce(v)
    info = generate_board(a.width, a.height, seed=a.seed, hex_mm=a.hex_mm,
                          paper=a.paper, margin_mm=a.margin_mm,
                          place_resources=not a.no_resources,
                          out_pdf=a.out_pdf, mapgen_params=mparams)
    print(info)