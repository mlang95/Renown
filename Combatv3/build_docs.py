#!/usr/bin/env python3
"""build_docs.py — fill {{TABLE:name}}, {{GLOSSARY}}, and {{DEF:term}} markers in an
authored .docx with content generated live from renown_data (via docx_tables.py).

PORTABLE: a .docx is a zip archive, so this edits word/document.xml directly with
Python's stdlib zipfile — no external unpack/pack scripts, no Node. Runs anywhere
Python + python-docx are installed.

Usage:  python build_docs.py authored.docx output.docx
Markers: run `python docx_tables.py` to list available table names.
"""
import re, sys, zipfile, shutil, os
sys.path.insert(0, ".")
import docx_tables

def _xesc(t):
    return t.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

MARKER      = re.compile(r"\{\{TABLE:([a-z_]+)\}\}")
GLOSSARY_MK = re.compile(r"\{\{GLOSSARY\}\}")
DEF_MK      = re.compile(r"\{\{DEF:([^}]+)\}\}")

def _transform(xml):
    """Replace each <w:p> containing a block marker with generated XML; inline DEF subs."""
    out, count, pos = [], 0, 0
    for m in re.finditer(r"<w:p\b.*?</w:p>", xml, re.DOTALL):
        seg = m.group(0)
        text = re.sub(r"<[^>]+>", "", seg)
        if MARKER.search(text):
            out.append(xml[pos:m.start()])
            out.append(docx_tables.get(MARKER.search(text).group(1)))
            pos = m.end(); count += 1
        elif GLOSSARY_MK.search(text):
            out.append(xml[pos:m.start()])
            out.append(docx_tables.glossary_block())
            pos = m.end(); count += 1
    out.append(xml[pos:])
    result = "".join(out)
    def _sub_def(mm):
        d = docx_tables.definition(mm.group(1).strip())
        return _xesc(d) if d else mm.group(0)
    count += len(DEF_MK.findall(result))
    result = DEF_MK.sub(_sub_def, result)
    return result, count

def fill(in_docx, out_docx):
    # copy the source archive, then rewrite only word/document.xml inside it
    if os.path.abspath(in_docx) != os.path.abspath(out_docx):
        shutil.copyfile(in_docx, out_docx)
    with zipfile.ZipFile(in_docx, "r") as z:
        names = z.namelist()
        xml = z.read("word/document.xml").decode("utf-8")
        payloads = {n: z.read(n) for n in names}
    new_xml, count = _transform(xml)
    payloads["word/document.xml"] = new_xml.encode("utf-8")
    # rewrite the whole zip preserving all other parts
    with zipfile.ZipFile(out_docx, "w", zipfile.ZIP_DEFLATED) as z:
        for n in names:
            z.writestr(n, payloads[n])
    return count, True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit("usage: python build_docs.py authored.docx output.docx")
    n, ok = fill(sys.argv[1], sys.argv[2])
    print(f"filled {n} marker(s) -> {sys.argv[2]}")