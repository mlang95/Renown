"""
gen_book_json.py
================
book.json — the reader edition as data, for build_docx.js to consume.

Mirrors what gen_pdf.py renders, so the PDF and the DOCX stay identical in
content. Run this before build_docx.js.

    python gen_book_json.py && node build_docx.js
"""

import json
import gen_cultures as G
import renown_worldlore as W

G.AUDIENCE = "reader"

MARK_SLOP = True
SLOP = "WIP \u2192 "
AUTHORED_PROSE = {"THE PREMISE", "THE HOOK"}   # keys Gage has written


def t(s, slop=True):
    """Clean a value; prefix unauthored prose."""
    s = G.clean(s)
    if s and s[-1] not in ".!?":
        s += "."
    return (SLOP + s) if (slop and MARK_SLOP and s) else s


CORNERS = [
    ("Prowess",  ["Draggath Wastes", "Bleak Highlands", "Glen of Pravak", "Cravencroft",
                  "Hermit's Row", "Vogen's Gallows"]),
    ("Industry", ["Blighthold", "Scarlet Forest", "Coloured Mountains", "Heathport",
                  "Drakenheart"]),
    ("Cunning",  ["Dreadwood", "Crag Pass", "Marrow Shoals", "Bay of Pigs"]),
    ("Piety",    ["Lenaveron", "Lost Woods", "Wheat Fields", "Tombs of the Old Gods",
                  "Fair Whitewood", "Strait of Sorrow", "Shallow Mire / Quiet Hollow",
                  "Wharf of St. Brannoch"]),
]
ISLES = ["Vaelohk", "Ivory Isle", "Dead Waters", "Sea of Ash", "Prophet's Landing",
         "The Twelfth Reach", "Cailendroff Isles", "Bay of Lost Hope"]

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
          ("doctrine", "Doctrine"), ("strategy", "Strategy"), ("limits", "Limits"),
          ("pragmatism", "Pragmatism"), ("warband_spectrum", "Warbands"),
          ("the_fund", "The fund"), ("the_army", "Their army"),
          ("governance", "Governance"), ("diplomatic_role", "Diplomacy")]


def relations_for(name):
    """All RELATIONS touching `name`, as rows for the culture page.
    Directed 'A -> B' = A's stance toward B; mutual mirrors it. Returns
    [{head, text}] where head is the other culture (+ how they regard `name`)."""
    R = getattr(W, "RELATIONS", {})
    STANCE_TO = {  # how to phrase `name`'s own stance toward the other
        "ally": "ally", "protector": "protects", "dependency": "depends on",
        "patron": "patron of", "supplier": "supplies", "predator": "preys on",
        "rival": "rival of", "enemy": "enemy of", "resentment": "resents",
        "tolerated": "tolerates", "controls": "controls", "denial": "denies",
        "reverence": "reveres", "contempt": "holds in contempt", "mixed": "mixed with",
        "conditional": "conditional toward", "wary": "wary of", "converts": "seeks to convert",
        "none": "no relation with"}
    seen, out = set(), []
    for k, v in R.items():
        a, b = [s.strip() for s in k.split("->")]
        st, ov = v.get("stance", ""), G.clean(v.get("over", ""))
        if a == name:                       # name's own stance toward b
            out.append({"head": f"{b} \u2014 {STANCE_TO.get(st, st)}", "text": t(ov, slop=False)})
            seen.add(b)
        elif b == name and v.get("mutual"):  # symmetric: name shares stance toward a
            out.append({"head": f"{a} \u2014 {STANCE_TO.get(st, st)}", "text": t(ov, slop=False)})
            seen.add(a)
    for k, v in R.items():                   # incoming-only: how others regard name
        a, b = [s.strip() for s in k.split("->")]
        if b == name and a not in seen and not v.get("mutual"):
            st, ov = v.get("stance", ""), G.clean(v.get("over", ""))
            out.append({"head": f"{a} \u2014 {STANCE_TO.get(st, st)} them", "text": t(ov, slop=False)})
            seen.add(a)
    return out


def prose(key):
    body = W.PROSE.get(key, "")
    if not body:
        return []
    mine = key not in AUTHORED_PROSE
    return [(SLOP if (mine and MARK_SLOP) else "") + G.decaps(p.strip())
            for p in body.split("\n\n") if p.strip()]


def build(path="book.json"):
    rl = W.MAP.get("regional_lore", {})
    d = {
        "hook": prose("THE HOOK"),
        "premise": prose("THE PREMISE"),
        "overview": [{"title": title.title(),
                      "entries": [{"name": n,
                                   "domains": W.CULTURES.get(n, {}).get("domains", []),
                                   "text": t(W.OVERVIEW.get(n, ""), slop=False)}
                                  for n in members if n in W.OVERVIEW]}
                     for title, members in W.THREADS],
        "sea": t(W.MAP.get("sea", "")),
        "land": [{"corner": c,
                  "where": W.MAP["corners"].get(c, "").split("—")[0].strip(),
                  "places": [{"name": p, "text": t(rl[p])} for p in pl if p in rl]}
                 for c, pl in CORNERS],
        "stretches": [{"name": k, "text": t(v)}
                      for k, v in W.MAP.get("sea_stretches", {}).items()],
        "isles": [{"name": p, "text": t(rl[p])} for p in ISLES if p in rl],
        "ages": [],
        "threads": [],
    }

    # ---- timeline: Year 0, then the five ages  (Age of Darkness is its own §7)
    yz = W.TIMELINE.get("year_zero", {})
    if yz:
        d["ages"].append({"name": "Year 0", "span": yz.get("event", ""), "domain": "",
                          "events": [{"year": "0", "text": t(yz.get("content", ""))}]})

    starts, names = W.TIMELINE["age_starts"], W.AGES["names"]
    order = list(starts)
    for i, dom in enumerate(order):
        nxt = starts[order[i + 1]] if i + 1 < len(order) else None
        span = f"{starts[dom]}\u2013{nxt}" if nxt is not None else f"{starts[dom]}\u2013present"
        evs, seen = [], None
        for e in W.TIMELINE["events"]:
            if str(e.get("age", "")).split(" ")[0].split("(")[0].strip() != dom:
                continue
            y = str(e.get("year", ""))
            evs.append({"year": "" if y == seen else y, "text": t(e.get("event", ""))})
            seen = y
        d["ages"].append({"name": names.get(dom, dom), "span": span,
                          "domain": dom, "events": evs})

    # ---- the fifteen
    for title, members in W.THREADS:
        th = {"title": title.title(), "prose": [], "cultures": []}
        for n in members:
            c, a = W.CULTURES[n], W.CULTURE_AXES.get(n, {})
            dom = c.get("domains", [])
            D = W.DOMAINS.get(dom[0], {}) if dom else {}
            pure = c.get("type") == "pure"

            rows = []
            for ak, dk, lab in SHEET:
                v = D.get(dk, "") if pure else (a.get(ak) or D.get(dk, ""))
                if v:
                    rows.append([lab, G.clean(v)])

            secs, seen = [], set()
            for f, lab in EXTRAS:
                if c.get(f) and lab not in seen:
                    seen.add(lab)
                    secs.append({"head": lab, "text": t(c[f])})

            rivals = relations_for(n)

            evs = []
            for ev, dd in W.EVENTS.items():
                if n in (dd.get("cultures") or []):
                    body = " ".join(str(v) for k, v in dd.items()
                                    if isinstance(v, str)
                                    and k not in ("cultures", "year", "type", "hero", "teaches"))
                    evs.append({"head": ev, "text": t(body)})

            th["cultures"].append({
                "name": n, "type": c.get("type", "").capitalize(), "domains": dom,
                "region": G.clean(c.get("region", "")), "rows": rows,
                "overview": t(W.OVERVIEW.get(n, ""), slop=False),   # authored — never marked
                "sections": secs, "rivals": rivals, "events": evs,
                "holdings": [p for p in W.PLACE_OWNERS.get(n, []) if p in rl]})
        d["threads"].append(th)

    # ---- Age of Darkness (deep dive): WIP. Fills from old_gods_era["deep_dive"];
    #      the mid-tier origin now lives in §2 (PROSE["THE PREMISE"]).
    og = W.TIMELINE.get("old_gods_era", {})
    deep = og.get("deep_dive", [])
    blocks = []
    for item in (deep if isinstance(deep, list) else [deep]):
        if isinstance(item, dict):
            blocks.append({"head": item.get("head", ""), "text": t(item.get("text", ""))})
        elif item:
            blocks.append({"head": "", "text": t(item)})
    d["darkness"] = {"name": og.get("deep_name", "The Age of Darkness \u2014 In Depth"),
                     "dating": og.get("dating", ""), "blocks": blocks}

    json.dump(d, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{path} — hook {len(d['hook'])}p, premise {len(d['premise'])}p, "
          f"overview {sum(len(o['entries']) for o in d['overview'])} entries, "
          f"{len(d['threads'])} threads / {sum(len(t['cultures']) for t in d['threads'])} cultures, "
          f"{len(d['ages'])} ages, darkness {len(d['darkness']['blocks'])} blocks")


if __name__ == "__main__":
    build()
