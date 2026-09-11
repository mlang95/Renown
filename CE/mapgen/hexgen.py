#!/usr/bin/env python3
"""hexgen.py — generate the Renown hex asset set as standalone SVGs.

Every asset is drawn on the SAME canvas (W x H) around the SAME center, so the
layers composite by simple stacking (terrain -> resource -> road -> settlement
-> walls -> wards -> owner). Edit PALETTE / geometry here and regenerate; this
is the asset pipeline, not hand-drawn art.
"""
import math, os

W, H = 120, 108
CX, CY = 60, 54
R = 54                                  # flat-top hex radius (center->corner)
INK = "#322a20"                         # warm dark outline (not pure black)
OUT = "assets"

PALETTE = {                             # painted-board, heraldic-adjacent
    "grassland": ("#8a9a5b", "#79885090"),
    "forest":    ("#4f6239", "#3c4d2b90"),
    "hills":     ("#b89b63", "#a2854e90"),
    "mountain":  ("#74737c", "#5d5c6590"),
    "water":     ("#5c8aa0", "#4a7689aa"),
    "wetland":   ("#857c42", "#5f5526aa"),
    "tundra":    ("#a6ab98", "#8b9180aa"),
    "parchment": "#e9ddc2",
    "stone":     "#8d8a82",
    "wood":      "#7a5a3a",
    "roof":      "#9c4031",
    "wall":      "#9a958a",
    "gold":      "#c9a227",
}

def hexpts(cx=CX, cy=CY, r=R):
    # flat-top: vertices at 0,60,...,300 degrees
    return [(cx + r*math.cos(math.radians(a)), cy + r*math.sin(math.radians(a)))
            for a in range(0, 360, 60)]

def _poly(pts, fill, stroke=INK, sw=2.4, extra=""):
    d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return f'<polygon points="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>'

def _svg(body, defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
            f'viewBox="0 0 {W} {H}">{defs}{body}</svg>')

# ── terrain bases ──────────────────────────────────────────────────────────
def terrain(kind):
    base, patch = PALETTE[kind]
    pts = hexpts()
    body = [_poly(pts, base)]
    # subtle inner texture so flat tiles read as painted, not solid
    if kind == "water":
        for i, y in enumerate((44, 56, 68)):
            body.append(f'<path d="M{38+ (i%2)*6} {y} q10 -5 20 0 q10 5 20 0" '
                        f'fill="none" stroke="{patch}" stroke-width="2.2" stroke-linecap="round"/>')
    elif kind == "forest":
        for (x, y, s) in [(46,40,12),(70,46,13),(54,62,12),(76,66,11),(40,60,10)]:
            body.append(f'<circle cx="{x}" cy="{y}" r="{s}" fill="{patch}"/>')
            body.append(f'<polygon points="{x},{y-s} {x-s*0.7:.0f},{y+s*0.5:.0f} {x+s*0.7:.0f},{y+s*0.5:.0f}" '
                        f'fill="#3c4d2b" stroke="{INK}" stroke-width="1.4"/>')
    elif kind == "mountain":
        body.append(f'<polygon points="60,24 84,72 36,72" fill="{patch}" stroke="{INK}" stroke-width="2"/>')
        body.append(f'<polygon points="60,24 70,44 50,44" fill="#e9ddc2"/>')
        body.append(f'<polygon points="44,48 60,72 28,72" fill="#5d5c65" stroke="{INK}" stroke-width="1.6"/>')
    elif kind == "hills":
        for (x, y, rx) in [(46,58,18),(74,60,16),(60,50,15)]:
            body.append(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{rx*0.7:.0f}" fill="{patch}"/>')
    elif kind == "wetland":
        for (x, y, rx, ry) in [(50,52,15,9),(74,58,13,8),(60,66,12,7)]:
            body.append(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{patch}"/>')
        for (x, y) in [(44,46),(66,44),(80,52),(54,60)]:
            body.append(f'<path d="M{x} {y} l-2 -8 M{x} {y} l0 -9 M{x} {y} l2 -8" '
                        f'stroke="#3c4d2b" stroke-width="1.6" fill="none" stroke-linecap="round"/>')
    elif kind == "tundra":
        for (x, y, r) in [(48,50,4),(70,46,3),(58,62,4),(80,58,3),(40,60,3)]:
            body.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#ecefe6"/>')
        for (x, y) in [(54,54),(72,60)]:
            body.append(f'<circle cx="{x}" cy="{y}" r="5" fill="{patch}"/>')
    else:  # grassland — faint tufts
        for (x, y) in [(46,50),(72,46),(58,64),(80,62),(40,62)]:
            body.append(f'<path d="M{x} {y} l-3 -7 M{x} {y} l0 -8 M{x} {y} l3 -7" '
                        f'stroke="{patch}" stroke-width="1.8" fill="none" stroke-linecap="round"/>')
    return _svg("".join(body))

# ── resource toppers (top-right, clear of buildings) ────────────────────────
def resource(kind):
    x, y = 86, 30
    if kind == "wood":
        b = (f'<g stroke="{INK}" stroke-width="1.6">'
             f'<rect x="{x-10}" y="{y-2}" width="20" height="8" rx="2" fill="{PALETTE["wood"]}"/>'
             f'<rect x="{x-7}" y="{y-9}" width="14" height="8" rx="2" fill="#8a6a44"/>'
             f'<circle cx="{x-10}" cy="{y+2}" r="3" fill="#b58a55"/>'
             f'<circle cx="{x+10}" cy="{y+2}" r="3" fill="#b58a55"/></g>')
    elif kind == "stone":
        b = (f'<g stroke="{INK}" stroke-width="1.6" fill="{PALETTE["stone"]}">'
             f'<rect x="{x-11}" y="{y}" width="11" height="9" rx="2"/>'
             f'<rect x="{x}" y="{y}" width="11" height="9" rx="2"/>'
             f'<rect x="{x-6}" y="{y-8}" width="12" height="9" rx="2"/></g>')
    elif kind == "salt":
        b = (f'<g stroke="{INK}" stroke-width="1.6" fill="#f2efe6">'
             f'<polygon points="{x},{y-9} {x+9},{y+6} {x-9},{y+6}"/>'
             f'<polygon points="{x-9},{y-3} {x-3},{y+6} {x-15},{y+6}"/></g>')
    elif kind == "grain":
        b = (f'<g stroke="{PALETTE["gold"]}" stroke-width="2.4" stroke-linecap="round">'
             f'<line x1="{x-6}" y1="{y+8}" x2="{x-6}" y2="{y-8}"/>'
             f'<line x1="{x}" y1="{y+8}" x2="{x}" y2="{y-9}"/>'
             f'<line x1="{x+6}" y1="{y+8}" x2="{x+6}" y2="{y-8}"/>'
             f'<g stroke="#dcc04a"><path d="M{x} {y-9} l-5 3 M{x} {y-9} l5 3 M{x} {y-4} l-5 3 M{x} {y-4} l5 3"/></g></g>')
    else:  # ore
        b = (f'<g stroke="{INK}" stroke-width="1.6">'
             f'<polygon points="{x},{y-8} {x+9},{y} {x+4},{y+8} {x-6},{y+6} {x-9},{y-2}" fill="#5a5550"/>'
             f'<polygon points="{x-1},{y-3} {x+4},{y} {x+1},{y+4} {x-4},{y+2}" fill="{PALETTE["gold"]}"/></g>')
    return _svg(f'<circle cx="{x}" cy="{y}" r="17" fill="{PALETTE["parchment"]}" '
                f'stroke="{INK}" stroke-width="1.6" opacity="0.92"/>' + b)


def resource_apiary():
    x, y = 86, 30
    b = (f'<g stroke="{INK}" stroke-width="1.6">'
         f'<path d="M{x-9} {y+7} q9 -18 18 0 z" fill="#d8a838"/>'      # skep dome
         f'<line x1="{x-7}" y1="{y+1}" x2="{x+7}" y2="{y+1}" stroke="#9c7320"/>'
         f'<line x1="{x-8}" y1="{y+4}" x2="{x+8}" y2="{y+4}" stroke="#9c7320"/>'
         f'<circle cx="{x+9}" cy="{y-6}" r="2" fill="#3a3228"/></g>')   # a bee
    return _svg(f'<circle cx="{x}" cy="{y}" r="17" fill="{PALETTE["parchment"]}" '
                f'stroke="{INK}" stroke-width="1.6" opacity="0.92"/>' + b)

# ── settlements (scale by tier) ─────────────────────────────────────────────
def _house(x, y, w, h, roof=None):
    roof = roof or PALETTE["roof"]
    return (f'<g stroke="{INK}" stroke-width="1.8">'
            f'<rect x="{x-w/2:.0f}" y="{y}" width="{w}" height="{h}" fill="#d8c9a6"/>'
            f'<polygon points="{x-w/2-2:.0f},{y} {x:.0f},{y-h*0.7:.0f} {x+w/2+2:.0f},{y}" fill="{roof}"/></g>')

def settlement(tier):
    cfg = {"Hamlet":  [(60,58,14,12)],
           "Village": [(60,56,16,14),(46,60,11,10)],
           "Town":    [(60,54,16,14),(44,60,12,11),(76,60,12,11)],
           "City":    [(60,50,16,15),(42,58,12,12),(78,58,12,12),(60,64,13,10)],
           "Metropolis":[(60,46,15,16),(40,56,12,13),(80,56,12,13),(50,64,11,10),(70,64,11,10)]}
    body = []
    if tier in ("City", "Metropolis"):   # central tower/spire
        body.append(f'<g stroke="{INK}" stroke-width="1.8">'
                     f'<rect x="55" y="34" width="10" height="22" fill="#cdbf9c"/>'
                     f'<polygon points="53,34 60,22 67,34" fill="{PALETTE["gold"]}"/></g>')
    for (x, y, w, h) in cfg[tier]:
        body.append(_house(x, y, w, h))
    return _svg("".join(body))

# ── walls ring (inset hex, crenellated for stone) ───────────────────────────
def walls(kind):
    pts = hexpts(r=R-9)
    col = PALETTE["wall"] if kind == "stone" else PALETTE["wood"]
    body = [_poly(pts, "none", stroke=col, sw=6),
            _poly(pts, "none", stroke=INK, sw=1.4)]
    if kind == "stone":                  # crenellation nubs at vertices
        for (x, y) in pts:
            body.append(f'<rect x="{x-3:.0f}" y="{y-3:.0f}" width="6" height="6" '
                        f'fill="{col}" stroke="{INK}" stroke-width="1.2"/>')
    return _svg("".join(body))

# ── road overlay (edge band; demo = E-W connector) ──────────────────────────
def road(kind):
    col = PALETTE["stone"] if kind == "stone" else "#b8966010"
    fill = PALETTE["stone"] if kind == "stone" else "#a9824e"
    band = f'<rect x="6" y="{CY-7}" width="108" height="14" fill="{fill}" opacity="0.95"/>'
    seg = ""
    if kind == "stone":
        seg = "".join(f'<line x1="{x}" y1="{CY-7}" x2="{x}" y2="{CY+7}" '
                      f'stroke="{INK}" stroke-width="1.2" opacity="0.5"/>' for x in range(16, 114, 12))
    return _svg(band + seg)

# ── ward pips (open vs filled pursuit slots) ────────────────────────────────
def wards(filled, total):
    body, x0, y = [], 60 - (total-1)*7, 80
    for i in range(total):
        x = x0 + i*14
        f = PALETTE["gold"] if i < filled else PALETTE["parchment"]
        body.append(f'<circle cx="{x}" cy="{y}" r="5.5" fill="{f}" stroke="{INK}" stroke-width="1.6"/>')
    return _svg("".join(body))

# ── owner banner (heraldic accent) ──────────────────────────────────────────
def army_token(color):
    """A player army: heraldic shield on a round base, with a banner pole."""
    return _svg(
        f'<ellipse cx="{CX}" cy="78" rx="26" ry="8" fill="#00000033"/>'           # shadow
        f'<g stroke="{INK}" stroke-width="2">'
        f'<rect x="{CX-2}" y="22" width="4" height="30" fill="#6b5a3a"/>'           # pole
        f'<polygon points="{CX+2},24 {CX+24},28 {CX+2},36" fill="{color}"/>'        # pennant
        # shield body
        f'<path d="M{CX-20} 44 H{CX+20} V62 Q{CX} 86 {CX-20} 62 Z" '
        f'fill="{color}"/>'
        f'<path d="M{CX-20} 44 H{CX+20} V62 Q{CX} 86 {CX-20} 62 Z" '
        f'fill="none"/>'
        # crossed swords on the shield
        f'<line x1="{CX-11}" y1="50" x2="{CX+11}" y2="68" stroke="{PALETTE["parchment"]}" stroke-width="3"/>'
        f'<line x1="{CX+11}" y1="50" x2="{CX-11}" y2="68" stroke="{PALETTE["parchment"]}" stroke-width="3"/>'
        f'</g>')


def _tent(x, y, w, h, fill, ink=INK):
    return (f'<polygon points="{x},{y} {x+w/2},{y-h} {x+w},{y}" '
            f'fill="{fill}" stroke="{ink}" stroke-width="1.8"/>'
            f'<line x1="{x+w/2}" y1="{y-h}" x2="{x+w/2}" y2="{y}" stroke="{ink}" stroke-width="1.4"/>')


def bandit_camp():
    """A lawless camp: rough tents around a campfire, earthy/dark."""
    return _svg(
        f'<ellipse cx="{CX}" cy="80" rx="34" ry="9" fill="#00000040"/>'
        + _tent(CX-30, 74, 26, 22, "#6e5b43")
        + _tent(CX+6, 74, 26, 22, "#5d4b36")
        + _tent(CX-10, 62, 22, 18, "#7a6549")
        # campfire
        + f'<polygon points="{CX},48 {CX+5},58 {CX-5},58" fill="#d8762e" stroke="{INK}" stroke-width="1.2"/>'
        + f'<polygon points="{CX},52 {CX+3},58 {CX-3},58" fill="#f0c419"/>'
        + f'<line x1="{CX-8}" y1="60" x2="{CX+8}" y2="60" stroke="#3a2f22" stroke-width="2.5"/>')


def bandit_army():
    """A roving bandit warband: dark pennant with crossed blades over a tent."""
    return _svg(
        f'<ellipse cx="{CX}" cy="80" rx="30" ry="8" fill="#00000044"/>'
        + _tent(CX-14, 76, 28, 20, "#574636")
        + f'<g stroke="{INK}" stroke-width="2">'
        + f'<rect x="{CX-2}" y="26" width="4" height="34" fill="#4a3c2c"/>'          # pole
        + f'<polygon points="{CX+2},28 {CX+26},33 {CX+2},42" fill="#3a3330"/>'        # black flag
        + f'</g>'
        # crossed blades emblem on the flag
        + f'<line x1="{CX+6}" y1="31" x2="{CX+18}" y2="39" stroke="#b03030" stroke-width="2.4"/>'
        + f'<line x1="{CX+18}" y1="31" x2="{CX+6}" y2="39" stroke="#b03030" stroke-width="2.4"/>')


def outlaw_hex():
    """Outlaw Country territory — very dark grey, with a faint camp glyph."""
    pts = hexpts()
    body = _poly(pts, "#2b2b2e", sw=2.0)                                            # dark dark grey
    # faint tents to read as lawless ground
    body += (f'<g opacity="0.55">'
             + _tent(CX-18, 66, 20, 15, "#4a4a4e", ink="#15151a")
             + _tent(CX+2, 66, 20, 15, "#3f3f44", ink="#15151a")
             + f'</g>')
    return _svg(body)


def banner(color):
    return _svg(f'<g stroke="{INK}" stroke-width="1.6">'
                f'<rect x="14" y="20" width="6" height="26" fill="#6b5a3a"/>'
                f'<polygon points="20,22 40,22 34,30 40,38 20,38" fill="{color}"/></g>')

def write(name, svg):
    with open(os.path.join(OUT, name + ".svg"), "w") as f:
        f.write(svg)

def main():
    os.makedirs(OUT, exist_ok=True)
    for t in ("grassland", "forest", "hills", "mountain", "water", "wetland", "tundra"):
        write(f"terrain_{t}", terrain(t))
    for r in ("wood", "stone", "salt", "grain", "ore"):
        write(f"res_{r}", resource(r))
    write("res_apiary", resource_apiary())
    for s in ("Hamlet", "Village", "Town", "City", "Metropolis"):
        write(f"settle_{s.lower()}", settlement(s))
    for w in ("wooden", "stone"):
        write(f"walls_{w}", walls(w))
    for rd_ in ("dirt", "stone"):
        write(f"road_{rd_}", road(rd_))
    write("wards_1of3", wards(1, 3))
    write("wards_3of3", wards(3, 3))
    for name, col in (("red", "#8c2f2f"), ("blue", "#2f4a8c"), ("gold", "#c9a227")):
        write(f"banner_{name}", banner(col))
    for name, col in (("red", "#8c2f2f"), ("blue", "#2f4a8c"), ("gold", "#c9a227"),
                      ("green", "#3a7d44"), ("purple", "#6a3d8c"), ("orange", "#b5651d")):
        write(f"army_{name}", army_token(col))
    write("bandit_camp", bandit_camp())
    write("bandit_army", bandit_army())
    write("outlaw_hex", outlaw_hex())
    print("wrote", len(os.listdir(OUT)), "assets to", OUT)

if __name__ == "__main__":
    main()
