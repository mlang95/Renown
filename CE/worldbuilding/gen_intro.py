"""
gen_intro.py
============
intro.txt — narrative only. Every authored passage in the file, in reading
order, with no facts lists, no axes, no places, no notes. The hook.

Usage:  python gen_intro.py
"""

import textwrap
from renown_worldlore import PROSE, THREADS, OVERVIEW, CULTURES
from gen_cultures import WIDTH, decaps, clean, sl, AUTHORED
import gen_cultures as G

G.AUDIENCE = "reader"


def para(t, indent=0):
    t = clean(t)
    if t and t[-1] not in ".!?":
        t += "."
    return textwrap.fill(t, width=WIDTH, initial_indent=" " * indent,
                         subsequent_indent=" " * indent,
                         break_long_words=False, break_on_hyphens=False)


def prose(key, indent=0):
    body = PROSE.get(key, "")
    if not body:
        return ""
    mark = (lambda t: t) if key in AUTHORED else sl
    return "\n\n".join(
        textwrap.fill(mark(decaps(p.strip())), width=WIDTH,
                      initial_indent=" " * indent, subsequent_indent=" " * indent,
                      break_long_words=False, break_on_hyphens=False)
        for p in body.split("\n\n"))


def bar(t, ch="="):
    return f"{ch * WIDTH}\n{t.center(WIDTH)}\n{ch * WIDTH}"


def main(path="intro.txt"):
    out = [bar("RENOWN"), "", prose("THE PREMISE"), ""]

    out += ["", bar("THE FIFTEEN", "="), ""]
    for title, members in THREADS:
        out += ["", bar(title, "-"), ""]
        for name in members:
            c = CULTURES.get(name, {})
            out += ["", f"{name.upper()}   ·   {' x '.join(c.get('domains', []))}", "",
                    para(OVERVIEW.get(name, ""), indent=2), ""]

    txt = "\n".join(out)
    open(path, "w", encoding="utf-8").write(txt)
    print(f"intro.txt — {len(txt.split())} words, {txt.count(chr(10))+1} lines, "
          f"max {max(len(l) for l in txt.split(chr(10)))} cols")


if __name__ == "__main__":
    main()
