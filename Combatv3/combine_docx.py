#!/usr/bin/env python3
"""combine_docx.py — append the Compendium after the Rules doc as one book,
preserving each part's own section: portrait rules -> landscape reference.

Both inputs are produced elsewhere in :docs
  md_to_docx.py RULES_reorganized_5.md Rules.docx
  build_compendium.py compendium_data.json Compendium.docx

Usage:  python combine_docx.py Rules.docx Compendium.docx Renown.docx
"""
import sys
from copy import deepcopy
from docx import Document
from docx.oxml.ns import qn


def combine(rules_path, comp_path, out_path):
    A = Document(rules_path)
    B = Document(comp_path)
    ab, bb = A.element.body, B.element.body

    # A's body-level sectPr holds the rules' (portrait) page setup. Move it into a
    # trailing paragraph so that section closes at the end of the rules content...
    a_sectPr = ab.findall(qn("w:sectPr"))[-1]
    p = A.add_paragraph()
    p._p.get_or_add_pPr().append(deepcopy(a_sectPr))
    ab.remove(a_sectPr)

    # ...then append the compendium's body. Its children end in B's own body-level
    # sectPr (landscape), which becomes the final section of the merged document.
    for child in list(bb):
        ab.append(deepcopy(child))

    A.save(out_path)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.exit("usage: python combine_docx.py Rules.docx Compendium.docx Renown.docx")
    combine(sys.argv[1], sys.argv[2], sys.argv[3])
    print("wrote", sys.argv[3])