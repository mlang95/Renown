#!/usr/bin/env python3
"""combine_docx.py — append the Compendium after the Rules doc as one book:
  - portrait rules  ->  landscape reference (each keeps its own section)
  - a master Table of Contents at the front (whole book; from outline levels)
  - a second Table of Contents at the start of the compendium (compendium only;
    built from hidden TC entry-marks flagged \\f C, which Word AND LibreOffice honor)
  - a footer on every section: "Renown v{VERSION}  .  Page X of Y"
  - flags fields to refresh when the document is opened

Both TOCs need the headings to carry w:outlineLvl (see the one-line edits to
md_to_docx.py and build_compendium.py shipped alongside this file). The master
TOC reads those levels directly; the compendium TOC reads the TC marks this
script injects into each compendium heading.

Version is read from renown_data.VERSION; pass a 5th arg to override.

Usage:  python combine_docx.py Rules.docx Compendium.docx Renown.docx [version]
"""
import sys
from copy import deepcopy
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt

FONT = "EB Garamond"
SIZE = 8            # footer pt
COMP_FLAG = "C"     # TC \f flag identifying compendium entries

try:
    import renown_data as _rd
    VERSION = str(getattr(_rd, "VERSION", ""))
except Exception:
    VERSION = ""

W_T = qn("w:t"); W_P = qn("w:p"); W_PPR = qn("w:pPr"); W_OL = qn("w:outlineLvl"); W_SECT = qn("w:sectPr")


# ── run/field helpers ────────────────────────────────────────────────────────
def _rpr(font=FONT, size=SIZE, bold=False):
    rpr = OxmlElement("w:rPr")
    rf = OxmlElement("w:rFonts")
    for a in ("w:ascii", "w:hAnsi", "w:cs"):
        rf.set(qn(a), font)
    rpr.append(rf)
    if bold:
        rpr.append(OxmlElement("w:b"))
    sz = OxmlElement("w:sz"); sz.set(qn("w:val"), str(int(size * 2))); rpr.append(sz)
    return rpr


def _run(text=None, fldchar=None, instr=None, font=FONT, size=SIZE, bold=False):
    r = OxmlElement("w:r")
    r.append(_rpr(font, size, bold))
    if fldchar is not None:
        fc = OxmlElement("w:fldChar"); fc.set(qn("w:fldCharType"), fldchar)
        if fldchar == "begin":
            fc.set(qn("w:dirty"), "true")
        r.append(fc)
    elif instr is not None:
        it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = instr
        r.append(it)
    else:
        t = OxmlElement("w:t"); t.set(qn("xml:space"), "preserve"); t.text = text
        r.append(t)
    return r


def _para(*runs, after=None):
    p = OxmlElement("w:p")
    if after is not None:
        pPr = OxmlElement("w:pPr")
        sp = OxmlElement("w:spacing"); sp.set(qn("w:after"), str(after)); pPr.append(sp)
        p.append(pPr)
    for r in runs:
        p.append(r)
    return p


def _page_break():
    r = OxmlElement("w:r")
    br = OxmlElement("w:br"); br.set(qn("w:type"), "page"); r.append(br)
    return _para(r)


def _toc_block(title_text, levels="1-2", flag=None, title_size=18):
    if flag:
        instr = f' TOC \\f {flag} \\l "{levels}" \\h \\z '
    else:
        instr = f' TOC \\o "{levels}" \\h \\z \\u '
    title = _para(_run(title_text, size=title_size, bold=True), after=120)
    toc = _para(
        _run(fldchar="begin"),
        _run(instr=instr),
        _run(fldchar="separate"),
        _run("Right-click and Update Field (or press F9) to build the table of contents.", size=10),
        _run(fldchar="end"),
    )
    return [title, toc, _page_break()]


def _appendix_heading(text="Appendix \u2014 The Compendium"):
    """A level-1 divider the master TOC picks up as a single appendix entry."""
    p = _para(_run(text, size=18, bold=True), after=120)
    ol = OxmlElement("w:outlineLvl"); ol.set(qn("w:val"), "0")
    p.find(W_PPR).append(ol)
    return p


def _tag_heading_as_tc(p, flag):
    """Mark a compendium heading for the compendium-only TOC (TC \\f flag), and strip
    its outlineLvl so the master (\\o) TOC skips it — the compendium collapses to one
    'Appendix' entry up front while keeping full detail in its own TOC."""
    pPr = p.find(W_PPR)
    ol = pPr.find(W_OL) if pPr is not None else None
    if ol is None:
        return
    level = int(ol.get(qn("w:val"))) + 1
    title = "".join(t.text or "" for t in p.findall(".//" + W_T)).replace('"', "'").strip()
    pPr.remove(ol)  # keep it out of the master TOC
    if not title:
        return
    for r in (_run(fldchar="begin"),
              _run(instr=f' TC "{title}" \\f {flag} \\l "{level}" '),
              _run(fldchar="end")):
        p.append(r)


# ── merge ────────────────────────────────────────────────────────────────────
def combine(rules_path, comp_path):
    A = Document(rules_path)
    B = Document(comp_path)
    ab, bb = A.element.body, B.element.body

    # Close A's (portrait) section: move its body-level sectPr into a trailing paragraph.
    a_sectPr = ab.findall(W_SECT)[-1]
    p = A.add_paragraph()
    p._p.get_or_add_pPr().append(deepcopy(a_sectPr))
    ab.remove(a_sectPr)

    # Appendix divider at the START of the compendium (the single master-TOC entry),
    # then the compendium body. The compendium's own contents page goes at the very
    # back of the book (below), like an index.
    ab.append(_appendix_heading())
    for child in list(bb):
        c = deepcopy(child)
        if c.tag == W_P:
            _tag_heading_as_tc(c, COMP_FLAG)
        ab.append(c)  # compendium body; its sectPr (if any) stays last
    # Back-of-book compendium contents: page break + title + TOC, before the final sectPr.
    tb = _toc_block("Compendium Contents", flag=COMP_FLAG, title_size=16)  # [title, toc, break]
    back = [_page_break(), tb[1]]                                           # break, toc (title dropped)
    sect = ab.findall(W_SECT)
    if sect:
        for el in back:
            sect[-1].addprevious(el)
    else:
        for el in back:
            ab.append(el)

    # Master TOC (whole book) at the very front.
    for idx, el in enumerate(_toc_block("Contents", title_size=18)):
        ab.insert(idx, el)
    return A


def add_footers(doc, version):
    for section in doc.sections:
        section.footer.is_linked_to_previous = False
        p = section.footer.paragraphs[0]
        for r in list(p._p.findall(qn("w:r"))):
            p._p.remove(r)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p._p.append(_run(f"Renown v{version}   \u00b7   Page "))
        p._p.append(_run(fldchar="begin")); p._p.append(_run(instr="PAGE")); p._p.append(_run(fldchar="end"))
        p._p.append(_run(" of "))
        p._p.append(_run(fldchar="begin")); p._p.append(_run(instr="NUMPAGES")); p._p.append(_run(fldchar="end"))


def set_update_fields(doc):
    settings = doc.settings.element
    if settings.find(qn("w:updateFields")) is None:
        uf = OxmlElement("w:updateFields"); uf.set(qn("w:val"), "true"); settings.append(uf)



def compact_toc_styles(doc, size=9):
    """Make the compendium index fit one page: zero paragraph spacing on the TOC
    entry styles + a smaller font. Word/LibreOffice apply these named styles when
    they build the TOC field."""
    from docx.enum.style import WD_STYLE_TYPE
    existing = {st.name for st in doc.styles}
    for lvl in range(1, 6):
        name = f"TOC {lvl}"
        try:
            st = doc.styles[name] if name in existing else doc.styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
        except Exception:
            continue
        pf = st.paragraph_format
        pf.space_before = Pt(0); pf.space_after = Pt(0)
        pf.line_spacing = Pt(size + 2)        # EXACT line height -> Word cannot use a taller default
        try:
            st.font.size = Pt(size); st.font.name = FONT
        except Exception:
            pass
        # CRITICAL: python-docx marks new styles customStyle="1"; Word then ignores
        # them for TOC output and uses its own built-in TOC 1. Drop the flag so this
        # definition overrides the built-in style Word applies to TOC entries.
        cs = qn("w:customStyle")
        if cs in st.element.attrib:
            del st.element.attrib[cs]


if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit("usage: python combine_docx.py Rules.docx Compendium.docx Renown.docx [version]")
    version = sys.argv[4] if len(sys.argv) > 4 else VERSION
    doc = combine(sys.argv[1], sys.argv[2])
    add_footers(doc, version)
    set_update_fields(doc)
    compact_toc_styles(doc)
    doc.save(sys.argv[3])
    print(f"wrote {sys.argv[3]} (master TOC + compendium TOC via TC marks, footer Renown v{version})")