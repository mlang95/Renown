#!/usr/bin/env python3
"""worldtxt.py — parse the hand-maintained world.txt lore book into structured
sections + HTML, so build_wiki.py renders whatever is currently in world.txt.

world.txt grammar (all delimiters are hand-editable):
  ====  rule  ====          banner. Numbered centred title => top section;
                            DEMONYM + "Type | Domains" line => a culture.
  ####  #TITLE#  ####       a culture-group header inside THE FIFTEEN.
  -- Title ----             a sub-header (may be "-- Title -- range ----").
  ----                      a plain divider (brackets a culture's attributes).
  · Item / indented desc    a definition entry (term + description).
  Key:      value           an aligned attribute block.
  slop —> / SLOP —>         a draft marker, stripped from rendered prose.
"""
import re, html

RULE_EQ = re.compile(r"^={5,}\s*$")
RULE_HASH = re.compile(r"^#{5,}\s*$")
RULE_DASH = re.compile(r"^-{5,}\s*$")
SUBHEAD = re.compile(r"^\s*--\s+(.*?)\s*-{2,}\s*$")     # -- Title ----
HASHTITLE = re.compile(r"^#\s+(.*?)\s+#\s*$")           # # TITLE #
NUMTITLE = re.compile(r"^\s*\d+\.\s+(.+?)\s*$")         # 1. THE PREMISE
BULLET = re.compile(r"^\s*·\s+(.*)$")
KV = re.compile(r"^\s*([A-Z][A-Za-z0-9 /&'’()-]*?):\s{1,}(\S.*)$")
SLOP = re.compile(r"\bslop\s*[—–-]+>\s*", re.IGNORECASE)
CAPS_HEAD = re.compile(r"^\s*([A-Z][A-Z ’'&/-]{1,40})\s*$")  # bare PLACES / NOTES

def _clean(s):
    return SLOP.sub("", s).strip()

def parse_sections(text):
    """Split into top-level sections: [(title, [body_lines]), ...] in file order."""
    lines = text.split("\n")
    # a top section banner is: RULE_EQ, <numbered title>, RULE_EQ
    marks = []
    for i in range(len(lines) - 2):
        if RULE_EQ.match(lines[i]) and RULE_EQ.match(lines[i + 2]):
            m = NUMTITLE.match(lines[i + 1])
            if m:
                marks.append((i, m.group(1).strip()))
    sections = []
    for idx, (i, title) in enumerate(marks):
        start = i + 3
        end = marks[idx + 1][0] if idx + 1 < len(marks) else len(lines)
        sections.append((title, lines[start:end]))
    return sections

def extract_places(sections):
    """Return a gazetteer: list of dicts {name, owner, desc, kind}.
      kind='territory' with owner=<demonym>  — a held place
      kind='sea'       with owner=None       — THE MAP > THE SEA entries
      kind='unclaimed' with owner=None       — unheld / contested places

    Preferred source is a dedicated `THE GAZETTEER` section (bullets of the form
    `· Name  —  Holder`, emitted by gen_cultures.py from MAP.regional_lore), which
    lists every described place. If that section is absent (older world.txt), fall
    back to deriving territories from the per-culture PLACES blocks.
    """
    def bullet_entries(block):
        """[(name, desc)] from a block of `· name` + indented continuation lines."""
        out, name, desc = [], None, []
        for l in block:
            mb = BULLET.match(l)
            if mb:
                if name is not None:
                    out.append((name, " ".join(_clean(x) for x in desc).strip()))
                name, desc = mb.group(1).strip(), []
            elif name is not None:
                desc.append(l)
        if name is not None:
            out.append((name, " ".join(_clean(x) for x in desc).strip()))
        return out

    def seas(sections):
        out = []
        for title, body in sections:
            if "MAP" not in title.upper():
                continue
            in_sea = False
            for block in _blocks(body):
                if SUBHEAD.match(block[0]):
                    in_sea = "SEA" in SUBHEAD.match(block[0]).group(1).upper()
                    if in_sea:
                        for nm, d in bullet_entries(block[1:]):
                            out.append({"name": nm, "owner": None, "desc": d, "kind": "sea"})
                elif in_sea and any(BULLET.match(l) for l in block):
                    for nm, d in bullet_entries(block):
                        out.append({"name": nm, "owner": None, "desc": d, "kind": "sea"})
        return out

    # ── preferred: the dedicated gazetteer section ──
    gaz = next((body for title, body in sections if "GAZETTEER" in title.upper()), None)
    if gaz is not None:
        places, seen = [], set()
        for block in _blocks(gaz):
            for label, desc in bullet_entries(block):
                name, owner, kind = label.strip(), None, "territory"
                if "\u2014" in label:
                    left, right = label.split("\u2014", 1)
                    name = left.strip()
                    holder = right.strip()
                    if holder.lower() in ("unclaimed", "contested", "nobody", "none", ""):
                        owner, kind = None, ("unclaimed" if holder else "territory")
                    else:
                        owner = holder
                key = name.lower()
                if key in seen:
                    continue
                seen.add(key)
                places.append({"name": name, "owner": owner, "desc": desc, "kind": kind})
        return places + seas(sections)

    # ── fallback: derive from per-culture PLACES + THE WORLD unclaimed + seas ──
    places = []
    for title, body in sections:
        up = title.upper()
        if "FIFTEEN" in up:
            current = None
            for block in _blocks(body):
                if _is_banner(block):
                    inner = [l.strip() for l in block[1:-1] if l.strip()]
                    if inner and "|" not in inner[0]:
                        current = inner[0].title() if inner[0].isupper() else inner[0]
                    continue
                if block[0].strip().upper() == "PLACES":
                    for nm, d in bullet_entries(block[1:]):
                        places.append({"name": nm, "owner": current, "desc": d, "kind": "territory"})
        elif "WORLD" in up:
            in_unclaimed = False
            for block in _blocks(body):
                m = SUBHEAD.match(block[0])
                if m:
                    in_unclaimed = "BELONGING" in m.group(1).upper() or "NOBODY" in m.group(1).upper()
                    if in_unclaimed:
                        for nm, d in bullet_entries(block[1:]):
                            places.append({"name": nm, "owner": None, "desc": d, "kind": "unclaimed"})
                    continue
                if block[0].strip().upper().startswith("PLACES BELONGING"):
                    in_unclaimed = True
                    for nm, d in bullet_entries(block[1:]):
                        places.append({"name": nm, "owner": None, "desc": d, "kind": "unclaimed"})
                elif in_unclaimed and any(BULLET.match(l) for l in block):
                    for nm, d in bullet_entries(block):
                        places.append({"name": nm, "owner": None, "desc": d, "kind": "unclaimed"})
    return places + seas(sections)


def extract_cultures(sections):
    """Return the list of culture demonyms (from culture banners in THE FIFTEEN)."""
    out = []
    for title, body in sections:
        if "FIFTEEN" not in title.upper():
            continue
        for block in _blocks(body):
            if _is_banner(block):
                inner = [l.strip() for l in block[1:-1] if l.strip()]
                if not inner:
                    continue
                name = inner[0]
                # demonym line has no "|"; the "Type | Domains" line does
                if "|" in name:
                    continue
                out.append(name.title() if name.isupper() else name)
    return out

# ── block splitter: group body lines into blank-line-separated blocks ──
def _blocks(body):
    blk, out = [], []
    for ln in body:
        if ln.strip() == "":
            if blk:
                out.append(blk); blk = []
        else:
            blk.append(ln)
    if blk:
        out.append(blk)
    return out

def _is_banner(block):
    return len(block) >= 3 and RULE_EQ.match(block[0]) and RULE_EQ.match(block[-1])

def _is_hashbox(block):
    return len(block) == 3 and RULE_HASH.match(block[0]) and RULE_HASH.match(block[2])

def _columnar(block):
    """True if every line splits into >=2 columns on runs of 2+ spaces and none
    is a Key: value pair (the aligned ages table)."""
    rows = []
    for ln in block:
        if ":" in ln:
            return None
        parts = re.split(r"\s{2,}", ln.strip())
        if len(parts) < 2:
            return None
        rows.append(parts)
    width = max(len(r) for r in rows)
    if width < 2:
        return None
    return [r + [""] * (width - len(r)) for r in rows]

def _fmt_defs(entries, esc):
    """entries: list of (term, [desc_lines]) -> <dl class='wl-defs'>."""
    out = ["<dl class='wl-defs'>"]
    for term, desc in entries:
        d = " ".join(_clean(x) for x in desc).strip()
        out.append(f"<dt>{esc(term)}</dt>")
        if d:
            out.append(f"<dd>{esc(d)}</dd>")
    out.append("</dl>")
    return "".join(out)

def render_section(title, body, esc=None, slug=None):
    """Render one section body to HTML. esc(text)->safe-inline, slug(text)->id."""
    if esc is None:
        esc = lambda s: html.escape(s)
    if slug is None:
        slug = lambda s: re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    out = []
    for block in _blocks(body):
        # culture banner: ==== / DEMONYM / Type|Domains / ====
        if _is_banner(block):
            inner = [l for l in block[1:-1]]
            demonym = inner[0].strip() if inner else ""
            typ = inner[1].strip() if len(inner) > 1 else ""
            out.append(f"<h3 id='{slug(demonym)}' class='wl-culture'>{esc(demonym)}</h3>")
            if typ:
                out.append(f"<div class='wl-type'>{esc(typ)}</div>")
            continue
        if _is_hashbox(block):
            m = HASHTITLE.match(block[1].strip())
            t = m.group(1).strip() if m else block[1].strip("# ").strip()
            out.append(f"<h2 class='wl-group'>{esc(t)}</h2>")
            continue
        # single-line sub-header: -- Title ----
        if len(block) == 1 and SUBHEAD.match(block[0]):
            t = SUBHEAD.match(block[0]).group(1).strip()
            out.append(f"<h3 class='wl-sub'>{esc(t)}</h3>")
            continue
        # plain divider only -> skip
        if all(RULE_DASH.match(l) or RULE_EQ.match(l) for l in block):
            continue
        # strip leading/trailing pure-rule lines (e.g. the ---- brackets around a
        # culture's attribute block) so the inner content classifies cleanly
        while block and (RULE_DASH.match(block[0]) or RULE_EQ.match(block[0])):
            block = block[1:]
        while block and (RULE_DASH.match(block[-1]) or RULE_EQ.match(block[-1])):
            block = block[:-1]
        if not block:
            continue
        # a block may lead with a sub-header line then content (e.g. inside cultures)
        lead_html = ""
        if SUBHEAD.match(block[0]):
            lead_html = f"<h3 class='wl-sub'>{esc(SUBHEAD.match(block[0]).group(1).strip())}</h3>"
            block = block[1:]
        elif CAPS_HEAD.match(block[0]) and not BULLET.match(block[0]):
            lead_html = f"<h4 class='wl-label'>{esc(CAPS_HEAD.match(block[0]).group(1).strip())}</h4>"
            block = block[1:]
        if lead_html:
            out.append(lead_html)
        if not block:
            continue
        # bullet definition entries (one or more · with indented descriptions)
        if any(BULLET.match(l) for l in block):
            entries, term, desc = [], None, []
            for l in block:
                mb = BULLET.match(l)
                if mb:
                    if term is not None:
                        entries.append((term, desc))
                    term, desc = mb.group(1).strip(), []
                else:
                    if term is None:
                        term = l.strip()
                    else:
                        desc.append(l)
            if term is not None:
                entries.append((term, desc))
            out.append(_fmt_defs(entries, esc))
            continue
        # aligned key: value block (values may wrap onto indented continuation lines)
        kv_hits = sum(1 for l in block if KV.match(l))
        if KV.match(block[0]) and kv_hits >= 2:
            rows, k, v = [], None, []
            for l in block:
                m = KV.match(l)
                if m:
                    if k is not None:
                        rows.append((k, " ".join(v).strip()))
                    k, v = m.group(1), [m.group(2)]
                else:
                    v.append(l.strip())
            if k is not None:
                rows.append((k, " ".join(v).strip()))
            out.append("<table class='kv wl-attrs'>" +
                       "".join(f"<tr><th>{esc(k)}</th><td>{esc(_clean(v))}</td></tr>" for k, v in rows) +
                       "</table>")
            continue
        # aligned columnar table (the ages table)
        cols = _columnar(block)
        if cols:
            out.append("<table class='pursuits wl-table'><tbody>" +
                       "".join("<tr>" + "".join(f"<td>{esc(c)}</td>" for c in r) + "</tr>" for r in cols) +
                       "</tbody></table>")
            continue
        # otherwise: prose paragraph (join wrapped lines, strip slop markers)
        para = " ".join(_clean(l) for l in block).strip()
        if para:
            out.append(f"<p>{esc(para)}</p>")
    return "".join(out)

if __name__ == "__main__":
    import sys
    txt = open(sys.argv[1] if len(sys.argv) > 1 else "world.txt", encoding="utf-8").read()
    secs = parse_sections(txt)
    print("SECTIONS:", [t for t, _ in secs])
    print("CULTURES:", extract_cultures(secs))
    for t, b in secs:
        h = render_section(t, b)
        print(f"\n### {t}: {len(h)} chars html; "
              f"h2={h.count('<h2')} h3={h.count('<h3')} h4={h.count('<h4')} "
              f"dl={h.count('<dl')} kv={h.count('wl-attrs')} tbl={h.count('wl-table')} p={h.count('<p>')}")