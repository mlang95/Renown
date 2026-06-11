#!/usr/bin/env python3
"""build_escalation.py — fill {{TABLE:x}} markers in the authored Escalation
master with data tables generated from renown_data.

  python build_escalation.py ESCALATION_master.md ESCALATION_CAMPAIGN.md

Markers: {{TABLE:retinues|melee|ranged|shields|armor|domain_board}}.
Prose (Dice Principle, Turn Sequence, Battle Walkthrough, Glossary) is left
untouched — only the data tables regenerate, so the doc can't drift from canon.
"""
import sys, re
sys.path.insert(0, ".")
import escalation_tables as et

def build(src_path, out_path):
    s = open(src_path, encoding="utf-8").read()
    filled = []
    def repl(m):
        key = m.group(1)
        fn = et.TABLES.get(key)
        if not fn:
            return m.group(0)  # leave unknown markers
        filled.append(key)
        return fn()
    s = re.sub(r"\{\{TABLE:(\w+)\}\}", repl, s)
    open(out_path, "w", encoding="utf-8").write(s)
    print(f"filled {len(filled)} table(s): {', '.join(filled)} -> {out_path}")
    return filled

if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "ESCALATION_master.md"
    out = sys.argv[2] if len(sys.argv) > 2 else "ESCALATION_CAMPAIGN.md"
    build(src, out)
