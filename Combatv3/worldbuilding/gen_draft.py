"""
gen_draft.py
============
draft.txt — a feedback draft containing ONLY authored culture prose.

No placeholder framing, no stat blocks, no design notes, no generated
connective tissue. Thread titles are structural labels, not writing. Anything
a reader reacts to here was written deliberately.

Usage:  python gen_draft.py
"""

import textwrap
from renown_worldlore import THREADS, OVERVIEW, CULTURES
import gen_cultures as G

G.AUDIENCE = "reader"
WIDTH = 78


def para(t, indent=2):
    t = G.clean(t)
    if t and t[-1] not in ".!?":
        t += "."
    return textwrap.fill(t, width=WIDTH, initial_indent=" " * indent,
                         subsequent_indent=" " * indent,
                         break_long_words=False, break_on_hyphens=False)


def main(path="draft.txt"):
    out = ["RENOWN — THE FIFTEEN PEOPLES", "draft for comment", ""]
    n = 0
    for title, members in THREADS:
        out += ["", "=" * WIDTH, title, "=" * WIDTH]
        for name in members:
            c = CULTURES.get(name, {})
            out += ["", f"{name.upper()}", f"  {' / '.join(c.get('domains', []))}", "",
                    para(OVERVIEW.get(name, ""))]
            n += 1
        out.append("")
    txt = "\n".join(out) + "\n"
    open(path, "w", encoding="utf-8").write(txt)
    words = sum(len(OVERVIEW[c].split()) for _, l in THREADS for c in l)
    print(f"draft.txt — {n} cultures, {words} words, {txt.count(chr(10))} lines, "
          f"max {max(len(l) for l in txt.split(chr(10)))} cols")


if __name__ == "__main__":
    main()
