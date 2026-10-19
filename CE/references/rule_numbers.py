#!/usr/bin/env python3
"""rule_numbers.py — MTG-style rule numbers for the rules markdown, computed at render time.

The source .md stays unnumbered (the board reads its headings verbatim); numbers are
derived from structure every build, so inserting a rule renumbers everything after it.

  # Chapter                      -> 2 Core Rules
  ## Section / ### Subsection    -> 2.4 The Turn / 2.4.2 Empire Phase   (nearest numbered parent + index)
  paragraph / top-level list     -> 2.4.2.3                              (running rule counter per section)
  list after a "...:" paragraph  -> 2.4.1a, 2.4.1b                       (lettered under that paragraph)
  nested item under a rule       -> 2.2.13a                              (lettered under its parent item)
  italic-only line               -> unnumbered (reminder / example / note)
  tables, {{BLOCK}} markers      -> unnumbered

Anchors and cross-references (both markers are removed from the output):
  {{RULE:id}}  anywhere in a numbered line   -> registers id -> that line's number
  every heading                              -> registers slug(title) -> its number ("council-phase")
  {{SEE:id}}   anywhere in prose             -> docx: "3.6.3";  plain (wiki/board): "3.6.3 (Council Phase)"

API
  number_md(text, mode="docx"|"plain") -> (text, anchors)   also fills ANCHORS
  load(path)            number a rules file into ANCHORS (wiki/board call this with their rules path)
  resolve_plain(text)   strip {{RULE:}}, resolve {{SEE:}} from ANCHORS (wiki_markers.preprocess_inline)
  ref(id) -> (number, title) | None

CLI
  python rule_numbers.py RULES.md                 # print the numbered markdown
  python rule_numbers.py RULES.md --anchors       # list every anchor
  python rule_numbers.py RULES.md --check         # unresolved {{SEE:}} / GLOSSARY_SEE ids, duplicate {{RULE:}} ids
"""
import os, re, sys

UNNUMBERED = {"Renown", "Index"}                     # title page and back-of-book index
APPENDICES = ("Holdings", "Equipment", "Factions")   # reference chapters, lettered A, B, C
PROSE_ONLY = {"Introduction", "Game Synopsis"}       # flavour text: the heading is numbered, its paragraphs aren't

HEAD_RE  = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
LIST_RE  = re.compile(r"^([ \t]*)([-*]|\d+\.(?:\d+\.?)*[a-z]?)\s+(.*)$")
BLOCK_RE = re.compile(r"^\s*\{\{(TABLE|ACTIONS|LIST|COLS|GLOSSARY|TOC|INDEX)(?::[^}]*)?\}\}\s*$")
RULE_RE  = re.compile(r"\s*\{\{RULE:([a-z0-9\-]+)\}\}")
SEE_RE   = re.compile(r"\{\{SEE:([a-z0-9\-]+)\}\}")
ITALIC_RE = re.compile(r"^\*(?!\*)[^*].*(?<!\*)\*\.?$")   # *whole line italic* (not **bold**)
TAIL_MK  = re.compile(r"(\{\{(?:IDX|RULE):[^}]*\}\}|\s)+$")

ANCHORS = {}          # id -> (number, section title)
DUPLICATES = []       # {{RULE:id}} used more than once


def slug(title):
    return re.sub(r"[^a-z0-9]+", "-", re.sub(r"\{\{[^}]*\}\}", "", title).lower()).strip("-")


def _letters(n):
    """1 -> a, 26 -> z, 27 -> aa."""
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(97 + r) + s
    return s


def _indent(ws):
    return len(ws.replace("\t", "    "))


def number_md(text, mode="docx"):
    """Number a rules markdown. mode="docx" prints numbers; mode="plain" leaves the text unnumbered
    but still strips {{RULE:}} and resolves {{SEE:}} (for the wiki and the board)."""
    ANCHORS.clear(); DUPLICATES.clear()
    lines = text.split("\n")
    out = []
    chapter, appendix = 0, 0
    heads = []            # stack of (level, number|None, child_count)
    sec, sec_title, prose = None, "", False
    # one counter per section, shared by its rules and its child sections (no 2.4.1 rule vs 2.4.1 heading clash)
    parent = None         # number of the last numbered rule (letters hang off it)
    letter = 0
    colon = False         # last paragraph ended with ':' -> a following list is lettered under it
    top_lettered = False  # the current top-level list item was itself lettered
    in_table = False
    rule_ids = set()

    def next_rule():
        l, pn, cc = heads[-1]
        heads[-1] = (l, pn, cc + 1)
        return f"{sec}.{cc + 1}"

    def anchor(line, num):
        for m in RULE_RE.finditer(line):
            if m.group(1) in rule_ids:
                DUPLICATES.append(m.group(1))
            if m.group(1) in ANCHORS and m.group(1) not in rule_ids:
                print(f"  rule_numbers: {{{{RULE:{m.group(1)}}}}} shadows a heading slug", file=sys.stderr)
            rule_ids.add(m.group(1))
            ANCHORS[m.group(1)] = (num, sec_title)
        return RULE_RE.sub("", line)

    for raw in lines:
        s = raw.strip()
        if not s:
            in_table = False
            out.append(raw); continue

        h = HEAD_RE.match(raw)
        if h:
            lvl, title = len(h.group(1)), h.group(2)
            while heads and heads[-1][0] >= lvl:
                heads.pop()
            num = None
            if lvl == 1:
                if title in APPENDICES:
                    appendix += 1; num = chr(64 + appendix)
                elif title not in UNNUMBERED:
                    chapter += 1; num = str(chapter)
            else:
                for i in range(len(heads) - 1, -1, -1):
                    if heads[i][1] is not None:
                        l, pn, cc = heads[i]
                        heads[i] = (l, pn, cc + 1)
                        num = f"{pn}.{cc + 1}"
                        break
            heads.append((lvl, num, 0))
            key, n2 = slug(title), 2
            while key in ANCHORS:
                key = f"{slug(title)}-{n2}"; n2 += 1
            ANCHORS[key] = (num, title)
            sec, sec_title, prose = num, title, (title in PROSE_ONLY)
            parent, letter, colon, top_lettered = None, 0, False, False
            out.append(f"{h.group(1)} {num} {title}" if (mode == "docx" and num) else raw)
            continue

        if BLOCK_RE.match(raw) or s.startswith("|") or in_table:
            in_table = s.startswith("|")
            colon = False
            out.append(raw); continue

        numbering = sec is not None and not prose
        lm = LIST_RE.match(raw)
        if lm:
            ws, marker, body = lm.groups()
            ind = _indent(ws)
            if not numbering:
                out.append(RULE_RE.sub("", raw)); continue
            if ind < 2:                                   # top-level item
                if colon and parent:
                    letter += 1; num = f"{parent}{_letters(letter)}"; top_lettered = True
                else:
                    num = next_rule(); parent, letter, top_lettered = num, 0, False
                body = anchor(body, num)
                lead = "    " if top_lettered else ""
                out.append(f"{lead}{num} {body}" if mode == "docx" else f"{ws}{marker} {body}")
            elif not top_lettered and parent:             # nested under a numbered item -> letter
                letter += 1; num = f"{parent}{_letters(letter)}"
                body = anchor(body, num)
                out.append(f"    {num} {body}" if mode == "docx" else f"{ws}{marker} {body}")
            else:                                         # nested under a lettered item -> plain bullet, one level deeper
                line = anchor(raw, parent or sec)
                out.append("    " + line if mode == "docx" else line)
            continue

        colon_next = bool(TAIL_MK.sub("", s).endswith(":"))
        if not numbering or ITALIC_RE.match(s):
            out.append(anchor(raw, parent or sec) if numbering else RULE_RE.sub("", raw))
            colon = False
            continue
        num = next_rule()
        parent, letter, top_lettered, colon = num, 0, False, colon_next
        body = anchor(raw, num)
        out.append(f"{num} {body.strip()}" if mode == "docx" else body)

    text = "\n".join(out)
    text = SEE_RE.sub(lambda m: _see(m.group(1), mode), text)
    return text, dict(ANCHORS)


def _see(aid, mode):
    r = ANCHORS.get(aid)
    if not r or not r[0]:
        print(f"  rule_numbers: unresolved anchor '{aid}'", file=sys.stderr)
        return f"[{aid}?]"
    return r[0] if mode == "docx" else f"{r[0]} ({r[1]})"


def ref(aid):
    if not ANCHORS:
        _ensure()
    r = ANCHORS.get(aid)
    return r if r and r[0] else None


def load(path):
    """Number a rules file into ANCHORS (plain mode)."""
    if path and os.path.exists(path):
        number_md(open(path, encoding="utf-8").read(), mode="plain")
    return ANCHORS


def _ensure():
    """No rules file numbered yet: fall back to the CE rules prose for the current SIMPLE flag."""
    try:
        import renown_data as rd
        simple = getattr(rd, "SIMPLE", True)
    except Exception:
        simple = True
    here = os.path.dirname(os.path.abspath(__file__))
    for d in (os.path.join(here, ".."), here, os.getcwd()):
        p = os.path.join(d, "RULES_push_simple.md" if simple else "RULES_push.md")
        if os.path.exists(p):
            return load(p)


def resolve_plain(text):
    """Strip {{RULE:}} and resolve {{SEE:}} against ANCHORS (wiki / board prose)."""
    if "{{SEE:" in text and not ANCHORS:
        _ensure()
    return SEE_RE.sub(lambda m: _see(m.group(1), "plain"), RULE_RE.sub("", text))


def check(path):
    """Return a list of problems: duplicate {{RULE:}} ids, unresolved {{SEE:}} ids, unresolved GLOSSARY_SEE anchors."""
    txt = open(path, encoding="utf-8").read()
    number_md(txt, mode="plain")
    probs = [f"duplicate {{{{RULE:{d}}}}}" for d in DUPLICATES]
    probs += [f"{{{{SEE:{a}}}}} unresolved" for a in sorted(set(SEE_RE.findall(txt))) if not ref(a)]
    try:
        import renown_data as rd
        for term, v in getattr(rd, "GLOSSARY_SEE", {}).items():
            aid = v[1] if isinstance(v, tuple) else v
            if not ref(aid):
                probs.append(f"GLOSSARY_SEE '{term}' -> '{aid}' unresolved")
    except ImportError:
        pass
    return probs


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    path = sys.argv[1]
    if "--check" in sys.argv:
        p = check(path)
        print("\n".join(p) if p else "rule anchors OK")
        sys.exit(1 if p else 0)
    out, anchors = number_md(open(path, encoding="utf-8").read())
    if "--anchors" in sys.argv:
        for a, (n, t) in anchors.items():
            print(f"{a:40s} {n or '-':12s} {t}")
    else:
        print(out)
