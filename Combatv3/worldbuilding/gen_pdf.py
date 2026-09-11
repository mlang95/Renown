"""
gen_pdf.py
==========
renown_world.pdf — the reader document as a laid-out book.

  1  Title
  2  The Age of Darkness
  3  The Map
  4  The Land            terrain and places, grouped by corner
  5  The Reckoning       vertical timeline, ages as bands, events alongside
  6  The Fifteen         one page per culture: sheet table + prose

Usage:  python gen_pdf.py
"""

import os, textwrap
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, Table, TableStyle, PageBreak, Image,
                                KeepTogether)

import renown_worldlore as W
import gen_cultures as G
G.AUDIENCE = "reader"

PAGE      = A4
MARGIN    = 18 * mm
MAP_FILE  = "/mnt/user-data/uploads/map7.png"

INK   = colors.HexColor("#1c1c20")
MUTE  = colors.HexColor("#6b6b73")
RULE  = colors.HexColor("#c9c6bf")
BAND  = colors.HexColor("#efece5")
DOMC  = {"Prowess":  colors.HexColor("#9E2B25"),
         "Cunning":  colors.HexColor("#1c1c20"),
         "Industry": colors.HexColor("#2E5A8C"),
         "Piety":    colors.HexColor("#B8901F")}

def S(name, **kw):
    base = dict(fontName="Times-Roman", fontSize=10.5, leading=14.5, textColor=INK)
    base.update(kw)
    return ParagraphStyle(name, **base)

BODY    = S("body", alignment=TA_JUSTIFY, spaceAfter=7)
LEAD    = S("lead", fontSize=12, leading=17, alignment=TA_JUSTIFY, spaceAfter=9)
H1      = S("h1", fontName="Times-Bold", fontSize=26, leading=30, spaceAfter=4)
H2      = S("h2", fontName="Times-Bold", fontSize=15, leading=19, spaceBefore=13, spaceAfter=5)
SUB     = S("sub", fontSize=9.5, textColor=MUTE, spaceAfter=12)
LABEL   = S("label", fontName="Times-Bold", fontSize=8.5, leading=11.5)
VALUE   = S("value", fontSize=8.5, leading=11.5)
CENTRE  = S("centre", alignment=TA_CENTER, fontSize=11, leading=16, textColor=MUTE)
TITLE   = S("title", fontName="Times-Bold", fontSize=46, leading=52, alignment=TA_CENTER)
YEAR    = S("year", fontName="Times-Bold", fontSize=9, leading=12)
EVENT   = S("event", fontSize=9, leading=12.5, alignment=TA_JUSTIFY)


MARK_SLOP = True


def txt(s):
    return G.clean(s).replace("&", "&amp;").replace("<", "&lt;")


def sl(s):
    """Mark a passage Gage did not author."""
    if not MARK_SLOP or not s:
        return s
    return "<b>WIP &rarr;</b> " + str(s).lstrip()


def dot(s):
    """Restore the terminal period clean() strips, so paragraphs end in punctuation."""
    if not s:
        return s
    return s if s.rstrip()[-1:] in ".!?" else s.rstrip() + "."


def para(s, style=BODY):
    s = txt(s)
    if s and s[-1] not in ".!?":
        s += "."
    return Paragraph(s, style)


def rule_line(w, colour=RULE, thick=0.6):
    t = Table([[""]], colWidths=[w], rowHeights=[1])
    t.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, -1), thick, colour)]))
    return t


# ------------------------------------------------------------------ sections

def title_page(w):
    return [Spacer(1, 62 * mm), Paragraph("RENOWN", TITLE), Spacer(1, 6 * mm),
            rule_line(w * .45), Spacer(1, 6 * mm),
            Paragraph("the world, its ages, and its fifteen peoples", CENTRE),
            PageBreak()]


def hook_page(w):
    out = [Paragraph("The Hook", H1), rule_line(w), Spacer(1, 7 * mm)]
    for p in W.PROSE.get("THE HOOK", "").split("\n\n"):
        if p.strip():
            out.append(Paragraph(dot(txt(G.decaps(p.strip()))), LEAD))
    out.append(PageBreak())
    return out


def premise_page(w):
    out = [Paragraph("The Age of Darkness", H1), rule_line(w), Spacer(1, 7 * mm)]
    for p in W.PROSE.get("THE PREMISE", "").split("\n\n"):
        if p.strip():
            out.append(Paragraph(dot(txt(G.decaps(p.strip()))), LEAD))
    out.append(PageBreak())
    return out


def overview_pages(w):
    """The fifteen peoples at a glance — authored snapshots, grouped by thread."""
    out = [Paragraph("The Overview", H1), rule_line(w), Spacer(1, 6 * mm)]
    for title, members in W.THREADS:
        out.append(Paragraph(txt(title).title(),
                             ParagraphStyle("ovh", parent=H2, spaceBefore=8)))
        for name in members:
            if name in W.OVERVIEW:
                c = W.CULTURES.get(name, {})
                dom = c.get("domains", [])
                col = DOMC.get(dom[0], INK) if len(dom) == 1 else INK
                out.append(KeepTogether([
                    Paragraph(f"<b>{txt(name)}</b>", ParagraphStyle("ovn", parent=LABEL,
                              fontSize=11, textColor=col)),
                    Paragraph(" / ".join(dom), SUB),
                    Paragraph(dot(txt(W.OVERVIEW[name])), BODY)]))
    out.append(PageBreak())
    return out


def darkness_pages(w):
    """The Age of Darkness (deep dive): WIP. Renders only when old_gods_era['deep_dive']
    is filled; the mid-tier origin now lives in the §2 'The Age of Darkness' prose."""
    og = W.TIMELINE.get("old_gods_era", {})
    deep = og.get("deep_dive", [])
    items = deep if isinstance(deep, list) else ([deep] if deep else [])
    if not items:
        return []
    out = [Paragraph(txt(og.get("deep_name", "The Age of Darkness \u2014 In Depth")), H1),
           rule_line(w), Spacer(1, 4 * mm)]
    for item in items:
        if isinstance(item, dict):
            if item.get("head"):
                out.append(Paragraph(txt(item["head"]), H2))
            if item.get("text"):
                out.append(Paragraph(dot(sl(txt(item["text"]))), BODY))
        elif item:
            out.append(Paragraph(dot(sl(txt(item))), BODY))
    out.append(PageBreak())
    return out


def map_page(w, h):
    out = [Paragraph("The World", H1), rule_line(w), Spacer(1, 5 * mm)]
    if os.path.exists(MAP_FILE):
        from PIL import Image as PILImage
        iw, ih = PILImage.open(MAP_FILE).size
        scale = min(w / iw, (h - 46 * mm) / ih)
        out.append(Image(MAP_FILE, iw * scale, ih * scale))
    out.append(Spacer(1, 4 * mm))
    out.append(Paragraph(dot(sl(txt(W.MAP.get("sea", "")))), BODY))
    out.append(PageBreak())
    return out


CORNERS = [("Prowess", ["Draggath Wastes", "Bleak Highlands", "Glen of Pravak",
                        "Cravencroft", "Hermit's Row", "Vogen's Gallows"]),
           ("Industry", ["Blighthold", "Scarlet Forest", "Coloured Mountains",
                         "Heathport", "Drakenheart"]),
           ("Cunning", ["Dreadwood", "Crag Pass", "Marrow Shoals", "Bay of Pigs"]),
           ("Piety", ["Lenaveron", "Lost Woods", "Wheat Fields",
                      "Tombs of the Old Gods", "Fair Whitewood", "Strait of Sorrow",
                      "Shallow Mire / Quiet Hollow", "Wharf of St. Brannoch"])]
ISLES = ["Vaelohk", "Ivory Isle", "Dead Waters", "Sea of Ash", "Prophet's Landing",
         "The Twelfth Reach", "Cailendroff Isles", "Bay of Lost Hope"]


def land_pages(w):
    rl = W.MAP.get("regional_lore", {})
    out = [Paragraph("The Land", H1), rule_line(w), Spacer(1, 5 * mm)]
    for dom, places in CORNERS:
        out.append(Paragraph(f"{dom} — {W.MAP['corners'].get(dom,'').split('—')[0].strip()}",
                             ParagraphStyle("c", parent=H2, textColor=DOMC.get(dom, INK))))
        for p in places:
            if p in rl:
                out.append(KeepTogether([Paragraph(f"<b>{p}</b>", LABEL),
                                         Paragraph(dot(sl(txt(rl[p]))), BODY)]))
    out.append(Paragraph("The Sea, and the Isles", H2))
    for k, v in W.MAP.get("sea_stretches", {}).items():
        out.append(KeepTogether([Paragraph(f"<b>{k}</b>", LABEL), Paragraph(dot(sl(txt(v))), BODY)]))
    for p in ISLES:
        if p in rl:
            out.append(KeepTogether([Paragraph(f"<b>{p}</b>", LABEL), Paragraph(dot(sl(txt(rl[p]))), BODY)]))
    out.append(PageBreak())
    return out


def timeline_pages(w):
    """Vertical: age bands down the page, events alongside in a spine."""
    out = [Paragraph("The Reckoning", H1), rule_line(w), Spacer(1, 4 * mm)]
    out.append(para(W.TIMELINE.get("epoch", ""), BODY))
    out.append(Spacer(1, 4 * mm))

    starts = W.TIMELINE.get("age_starts", {})
    names = W.AGES.get("names", {})
    order = list(starts)
    evs = W.TIMELINE.get("events", [])

    # (Age of Darkness is now its own §7 — not folded into the timeline.)
    yz = W.TIMELINE.get("year_zero", {})
    if yz:
        out.append(age_band(w, "Year 0", yz.get("event", ""), None))
        out.append(spine(w, [("0", yz.get("content", ""))]))

    for i, dom in enumerate(order):
        nxt = starts[order[i + 1]] if i + 1 < len(order) else None
        span = f"{starts[dom]}–{nxt}" if nxt is not None else f"{starts[dom]}–present"
        out.append(age_band(w, names.get(dom, dom), span, DOMC.get(dom)))
        rows, seen = [], None
        for e in evs:
            if str(e.get("age", "")).split(" ")[0].split("(")[0].strip() != dom:
                continue
            y = str(e.get("year", ""))
            rows.append(("" if y == seen else y, e.get("event", "")))
            seen = y
        if rows:
            out.append(spine(w, rows))
    out.append(PageBreak())
    return out


def age_band(w, name, span, colour):
    t = Table([[Paragraph(f"<b>{txt(name)}</b>", S("ab", fontName="Times-Bold", fontSize=13)),
                Paragraph(txt(span), S("as", fontSize=9, textColor=MUTE,
                                       alignment=2))]],
              colWidths=[w * .62, w * .38])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BAND),
        ("LINEBEFORE", (0, 0), (0, -1), 3, colour or MUTE),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    return KeepTogether([Spacer(1, 4 * mm), t, Spacer(1, 2 * mm)])


def spine(w, rows):
    data = [[Paragraph(txt(y), YEAR), Paragraph(sl(txt(e)), EVENT)] for y, e in rows if e]
    if not data:
        return Spacer(0, 0)
    t = Table(data, colWidths=[w * .17, w * .83])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBEFORE", (1, 0), (1, -1), 0.6, RULE),
        ("LEFTPADDING", (1, 0), (1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 2)]))
    return t


SHEET = [("government", "government", "Government"),
         ("authority", "source_of_authority", "Authority"),
         ("sacred", "sacred", "Sacred"),
         ("org_form", "org_form", "Organisation"),
         ("economy", "economy", "Economy"),
         ("kinship_unit", "kinship_unit", "Kinship"),
         ("identity_theory", "identity_theory", "Identity"),
         ("succession", "succession", "Succession"),
         ("attitude_to_change", "attitude_to_change", "Change"),
         ("military_doctrine", "military_doctrine", "War doctrine"),
         ("taboo", "taboo", "Taboo"),
         ("defined_against", "defined_against", "Defined against"),
         ("naming", "naming_grammar", "Naming"),
         ("monuments", "monuments", "Monuments")]

EXTRAS = [("trade_role", "Trade"), ("trade_relation", "Trade"),
          ("internal_conflict", "Internal conflict"), ("role", "Role"),
          ("the_antagonist", "Expansion"), ("the_economy", "Economy"),
          ("doctrine", "Doctrine"), ("strategy", "Strategy"),
          ("limits", "Limits"), ("pragmatism", "Pragmatism"),
          ("warband_spectrum", "Warbands"), ("the_fund", "The fund"),
          ("the_army", "Their army"), ("governance", "Governance"),
          ("diplomatic_role", "Diplomacy")]


def culture_pages(w):
    out = []
    for title, members in W.THREADS:
        out += [Paragraph(txt(title).title(), H1), rule_line(w), Spacer(1, 4 * mm),
                PageBreak()]
        for name in members:
            out += culture_page(w, name)
    return out


def culture_page(w, name):
    c = W.CULTURES.get(name, {})
    a = W.CULTURE_AXES.get(name, {})
    dom = c.get("domains", [])
    col = DOMC.get(dom[0], INK) if len(dom) == 1 else INK

    out = [Paragraph(txt(name), ParagraphStyle("cn", parent=H1, textColor=col)),
           Paragraph(f"{c.get('type','').capitalize()} &nbsp;·&nbsp; "
                     f"{' / '.join(dom)} &nbsp;·&nbsp; {txt(c.get('region',''))}", SUB),
           rule_line(w, col, 1.2), Spacer(1, 5 * mm)]

    rows = []
    is_pure = c.get("type") == "pure"
    D = W.DOMAINS.get(dom[0], {}) if dom else {}
    for ak, dk, lab in SHEET:
        v = D.get(dk, "") if is_pure else (a.get(ak) or D.get(dk, ""))
        if v:
            rows.append([Paragraph(lab, LABEL), Paragraph(txt(v), VALUE)])
    if rows:
        t = Table(rows, colWidths=[w * .21, w * .79])
        t.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LINEBELOW", (0, 0), (-1, -2), 0.35, RULE),
            ("TOPPADDING", (0, 0), (-1, -1), 3.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
            ("LEFTPADDING", (0, 0), (0, -1), 0)]))
        out += [t, Spacer(1, 6 * mm)]

    if W.OVERVIEW.get(name):
        out.append(para(W.OVERVIEW[name], LEAD))

    seen = set()
    for f, lab in EXTRAS:
        if c.get(f) and lab not in seen:
            seen.add(lab)
            out.append(Paragraph(lab, H2))
            out.append(Paragraph(dot(sl(txt(c[f]))), BODY))

    R = getattr(W, "RELATIONS", {})
    ST = {"ally": "ally", "protector": "protects", "dependency": "depends on",
          "patron": "patron of", "supplier": "supplies", "predator": "preys on",
          "rival": "rival of", "enemy": "enemy of", "resentment": "resents",
          "tolerated": "tolerates", "controls": "controls", "denial": "denies",
          "reverence": "reveres", "contempt": "holds in contempt", "mixed": "mixed with",
          "conditional": "conditional toward", "wary": "wary of", "converts": "seeks to convert",
          "none": "no relation with"}
    rel_rows, seen = [], set()
    for k, v in R.items():
        a, b = [s.strip() for s in k.split("->")]
        if a == name:
            rel_rows.append((f"{b} — {ST.get(v.get('stance',''), v.get('stance',''))}", v.get("over",""))); seen.add(b)
        elif b == name and v.get("mutual"):
            rel_rows.append((f"{a} — {ST.get(v.get('stance',''), v.get('stance',''))}", v.get("over",""))); seen.add(a)
    for k, v in R.items():
        a, b = [s.strip() for s in k.split("->")]
        if b == name and a not in seen and not v.get("mutual"):
            rel_rows.append((f"{a} — {ST.get(v.get('stance',''), v.get('stance',''))} them", v.get("over",""))); seen.add(a)
    if rel_rows:
        out.append(Paragraph("Relations", H2))
        for head, ov in rel_rows:
            out.append(Paragraph(f"<b>{txt(head)}</b> — " + dot(txt(ov)), BODY))

    places = [p for p in W.PLACE_OWNERS.get(name, [])
              if p in W.MAP.get("regional_lore", {})]
    if places:
        out.append(Paragraph("Holdings", H2))
        out.append(para(", ".join(places), BODY))

    for ev, d in W.EVENTS.items():
        if name in (d.get("cultures") or []):
            out.append(Paragraph(txt(ev), H2))
            body = " ".join(str(v) for k, v in d.items()
                            if isinstance(v, str) and k not in ("cultures", "year", "type",
                                                                "hero", "teaches"))
            out.append(Paragraph(dot(sl(txt(body))), BODY))

    out.append(PageBreak())
    return out


def build(path="renown_world.pdf"):
    w = PAGE[0] - 2 * MARGIN
    h = PAGE[1] - 2 * MARGIN
    doc = BaseDocTemplate(path, pagesize=PAGE,
                          leftMargin=MARGIN, rightMargin=MARGIN,
                          topMargin=MARGIN, bottomMargin=MARGIN + 6 * mm,
                          title="Renown — The World")

    def deco(canv, d):
        canv.saveState()
        canv.setFont("Times-Roman", 8)
        canv.setFillColor(MUTE)
        if canv.getPageNumber() > 1:
            canv.drawCentredString(PAGE[0] / 2, MARGIN * .65, str(canv.getPageNumber()))
        canv.restoreState()

    doc.addPageTemplates([PageTemplate(id="p",
                          frames=[Frame(MARGIN, MARGIN + 6 * mm, w, h - 6 * mm, id="f")],
                          onPage=deco)])

    story = (title_page(w) + hook_page(w) + premise_page(w) + overview_pages(w) +
             map_page(w, h) + land_pages(w) + timeline_pages(w) +
             culture_pages(w) + darkness_pages(w))
    doc.build(story)
    print(f"{path} — built")


if __name__ == "__main__":
    build()
