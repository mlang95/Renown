"""
gen_cultures.py
===============
Reads renown_worldlore.py and writes world.txt — a first-reader document for
someone who has never seen the game, the map, or a single proper noun.

Reading order is a constraint, not a preference: each section must be legible
without the ones after it. Premise -> vocabulary -> how to read -> world ->
gods -> time -> how peoples form -> the fifteen -> what runs the present.

Everything hard-wraps to WIDTH columns with hanging continuation indents, so
wrapped text sits inside its own opening rather than dropping back flush.

Usage:  python gen_cultures.py
Output: world.txt
"""

import re
import textwrap

from renown_worldlore import (
    CULTURES, CULTURE_AXES, DOMAINS, MAP, TIMELINE, AGES,
    GODS, TETRAMORPH, DIVINITY_RULE, MYTHOS, PANTHEON_ADJACENCY,
    FORMATION, RIVALRIES, EVENTS, PRECEPTORY, TERMS,
    ASTRAVANTHELIAD_PARADOX, ARCHIVE_OPPOSITION,
    CUNNING_NARRATION, FALSE_RELIGION_ENGINE, THE_DUKE, MACRO_FRAME,
    REPUTATION, PHONOLOGY, CORE_SPINE, LORE_SEQUENCE, OPEN_THREADS,
    DESIGN_ONLY, PLACE_OWNERS, PLACE_UNOWNED, PROSE, THREADS, OVERVIEW,
    bearing, CULTURE_SEATS,
)

WIDTH = 80          # wrap column
LABEL_W = 17        # width of the "Field:" label column in the facts list
HANG = 2            # extra indent on wrapped continuation lines

# Mark every reader-facing passage NOT authored by Gage. The only prose in the
# document that is his is OVERVIEW; everything else is synthesised placeholder
# and should be rewritten or cut before this goes to anyone.
MARK_SLOP = True
SLOP = "SLOP —> "

# Passages Gage has written. These are never marked.
AUTHORED = {"THE PREMISE"}

# Sections the premise already introduces. No generated opener.
NO_OPENER = {"THE FIFTEEN", "THE MAP", "THE TIMELINE", "THE AGE OF DARKNESS"}


def sl(text):
    """Prefix a placeholder passage."""
    if not MARK_SLOP or not text:
        return text
    return SLOP + str(text).lstrip()

# Audience switch. "reader" suppresses everything listed in DESIGN_ONLY;
# "designer" emits the whole file. Set by main().
AUDIENCE = "reader"


def designing():
    return AUDIENCE == "designer"


def show_dict(name):
    """Should this whole top-level structure appear?"""
    return designing() or name not in DESIGN_ONLY.get("dicts", [])


def visible(struct_name, mapping):
    """Filter a dict's keys against DESIGN_ONLY['keys'][struct_name]."""
    if designing():
        return dict(mapping)
    hidden = set(DESIGN_ONLY.get("keys", {}).get(struct_name, []))
    return {k: v for k, v in mapping.items() if k not in hidden}




# ================================================================ text helpers

# Proper nouns keep a capital when de-shouting; everything else drops to lower.
def _proper_nouns():
    names = set()
    for d in (CULTURES, CULTURE_AXES, GODS, MAP.get("regional_lore", {}),
              MAP.get("sea_stretches", {}), EVENTS, TERMS, DOMAINS):
        for k in d:
            for w in re.split(r"[^A-Za-z']+", str(k)):
                if len(w) > 2:
                    names.add(w.upper())
    names -= {"PROPHET", "FALSE", "GOD", "MONARCHY", "EMPIRE", "BASILICA", "HALL", "HALLS",
              "THE", "AND", "FOR", "NOT", "BUT", "ALL", "ONE", "TWO", "WHO", "WAS", "ARE",
              "ITS", "OUR", "OUT", "OWN", "HAS", "HAD", "CAN", "MAY", "NEW", "OLD", "WAR",
              "GOD", "GODS", "AGE", "SEA", "BAY", "PASS", "ROW", "ISLE", "WOODS", "FIELDS",
              "COURT", "GUILD", "PALACE", "WORD", "TRUE", "LAST", "ORDER", "HOUSE", "WORKS",
              "OFFICE", "MINISTRY", "ROYAL", "MANOR", "POST", "SHOALS", "MOUTH", "REACH"}
    names.update({"DRAGGATH", "VOGEN", "PRAVAK", "KARALIUS", "CLYPSO", "TRUSTI", "CAILEN",
                  "ESSELANTHEUM", "VAELOHK", "LENAVERON", "BLIGHTHOLD", "HEATHPORT",
                  "TETRAMORPH", "INQUISITION", "BLIGHT", "FRACTIONING"})
    return names


_PROPER = None

# Canonical spellings restored verbatim after de-shouting, longest first so that
# "Crag Pass" wins over "Crag" and "Order of the True Word" over "True Word".
_MULTIWORD = sorted(
    set(list(CULTURES) + list(GODS) + list(MAP.get("regional_lore", {}))
        + list(MAP.get("sea_stretches", {})) + list(EVENTS) + list(TERMS)
        + ["Order of the True Word", "God of Gods", "False Prophet", "Last Prophet",
           "Papal Palace", "Inquisitorial Palace", "Great Basilica", "Draggath Monarchy",
           "Draggath Empire", "Academic Hall", "Academic Halls", "Tetramorph",
           "Age of Darkness", "Great Fracture", "Cailendroff Edict",
           "Mason-King", "Warrior-Prophet", "God of Gods"]),
    key=len, reverse=True)
_MULTIWORD = [n[4:] if n.startswith("The ") else n for n in _MULTIWORD]
_MULTIWORD = sorted(set(_MULTIWORD), key=len, reverse=True)


def decaps(s):
    """Reader edition: drop designer emphasis. ALL-CAPS runs become sentence case,
    proper nouns keep their capital."""
    global _PROPER
    if designing():
        return s
    if _PROPER is None:
        _PROPER = _proper_nouns()

    def fix(m):
        w = m.group(0)
        if w.upper() in _PROPER:
            return w[0] + w[1:].lower()
        return w.lower()

    s = re.sub(r"\b[A-Z]{2,}(?:'[A-Z]+)?\b", fix, s)
    # restore capitals at sentence starts
    s = re.sub(r"(^|[.!?]\s+)([a-z])", lambda m: m.group(1) + m.group(2).upper(), s)
    for canon in _MULTIWORD:
        s = re.sub(re.escape(canon), canon, s, flags=re.I)
    return s


def clean(value):
    """Strip editorial [tags]; keep template slots like [name], [Order]."""
    if not value:
        return ""
    if isinstance(value, (list, tuple)):
        value = ", ".join(str(v) for v in value)

    def _drop(m):
        inner = m.group(1)
        if ("FUSE" in inner or "CENTER" in inner or "lead" in inner
                or "veneer" in inner or "grammar" in inner
                or "institutionalized" in inner or "flavored" in inner
                or "inflected" in inner or "defensive" in inner
                or "Prowess+" in inner or "Cunning+" in inner):
            return ""
        return m.group(0)

    s = re.sub(r"\[([^\]]*)\]", _drop, value)
    s = re.sub(r"\s{2,}", " ", s)
    s = decaps(s)
    return s.strip().rstrip(".").strip()


def wrap(text, indent=0, hang=0):
    """Word-wrap to WIDTH. `indent` sets the first line; `hang` indents every
    continuation line FURTHER, so wrapped text sits inside its own opening."""
    return textwrap.fill(
        str(text), width=WIDTH,
        initial_indent=" " * indent,
        subsequent_indent=" " * (indent + hang),
        break_long_words=False, break_on_hyphens=False,
    )


def prose(key, indent=2):
    """A written opener. Paragraphs split on blank lines; no bullet indent."""
    body = PROSE.get(key, "")
    mine = key not in AUTHORED
    if not body:
        return ""
    out = []
    for p in body.split("\n\n"):
        p = decaps(p.strip()) if not designing() else p.strip()
        p = sl(p) if mine else p
        out.append(textwrap.fill(p, width=WIDTH,
                                 initial_indent=" " * indent,
                                 subsequent_indent=" " * indent,
                                 break_long_words=False, break_on_hyphens=False))
    return "\n\n".join(out)


def para(text, indent=2):
    """A prose paragraph with terminal punctuation restored."""
    t = clean(text)
    if not t:
        return ""
    if t[-1] not in ".!?":
        t += "."
    return wrap(t, indent=indent, hang=HANG)


def bullet(label, body="", mark="·", label_indent=2, body_indent=6):
    """'· LABEL' then the full body wrapped beneath it. Never truncates."""
    out = [" " * label_indent + f"{mark} {label}"]
    if body:
        out.append(para(body, indent=body_indent))
    return "\n".join(out)


def fact(label, value):
    """One aligned 'Label: value' line, hanging-indented when it wraps."""
    value = clean(value)
    if not value:
        return None
    first = (label + ":").ljust(LABEL_W) + value
    return textwrap.fill(
        first, width=WIDTH,
        subsequent_indent=" " * (LABEL_W + HANG),
        break_long_words=False, break_on_hyphens=False,
    )


def title_bar(n, title):
    bar = "=" * WIDTH
    return f"\n{bar}\n{f'{n}.  {title}'.center(WIDTH)}\n{bar}\n"


def banner(title):
    bar = "#" * WIDTH
    return f"\n{bar}\n#{title.center(WIDTH - 2)}#\n{bar}\n"


def rule(title, extra=""):
    head = f"-- {title} --"
    if extra and len(head) + len(extra) + 2 <= WIDTH - 4:
        head += f" {extra} "
        extra = ""
    head += "-" * max(0, WIDTH - 2 - len(head))
    out = "  " + head
    if extra:
        out += "\n" + wrap(clean(extra), indent=4, hang=HANG)
    return out


def nice(key):
    """dict_key -> Display Label."""
    return key.replace("_", " ").strip().title()


# ================================================================ §1 PREMISE

def sec_premise():
    L = []
    if "the_premise" in visible("MACRO_FRAME", MACRO_FRAME):
        L.append(para(MACRO_FRAME["the_premise"]))
        L.append("")
    L.append(rule("YOUR STORY GOES ANYWHERE IN IT"))
    for k, v in MACRO_FRAME["three_axes_of_agency"].items():
        L.append("")
        L.append(bullet(k, v))
    L.append("")
    for k in ("the_effect", "why_the_world_map_is_lore_only"):
        if k in visible("MACRO_FRAME", MACRO_FRAME):
            L.append("")
            L.append(para(MACRO_FRAME[k]))
    return "\n".join(L)


# ================================================================ §2 DOMAINS

DOMAIN_ROWS = [
    ("core_value",      "Value"),
    ("org_form",        "Organization"),
    ("government",      "Government"),
    ("sacred",          "Sacred"),
    ("economy",         "Economy"),
    ("identity_theory", "Identity"),
    ("taboo",           "Taboo"),
    ("defined_against", "Defined against"),
    ("self_image",      "Self-image"),
]


def sec_domains():
    L = [para("Four domains define every culture, every value, and every quarrel in the world. "
              "Nothing that follows parses without them.")]
    for dom in DOMAINS:
        L.append("")
        L.append(rule(dom.upper()))
        for key, label in DOMAIN_ROWS:
            f = fact(label, DOMAINS[dom].get(key, ""))
            if f:
                L.append("  " + f)
    return "\n".join(L)


# ================================================================ §3 HOW TO READ

def sec_how_to_read():
    L = [para("Every name in this document is somebody's claim. Places carry the name their "
              "neighbours gave them, or the one they gave themselves, and the two rarely agree. "
              "Peoples are not fixed to the ground they stand on. Where an account is thin, or "
              "disagrees with another, that is the account.")]
    if not designing():
        return "\n".join(L)
    L.append("")
    L.append(rule("EVERY NAME IS A CLAIM"))
    for line in CORE_SPINE:
        L.append("")
        L.append(para(line, indent=4))
    L.append("")
    L.append(rule("SOME ENTRIES LIE ON PURPOSE"))
    L.append("")
    L.append(para(CUNNING_NARRATION["principle"], indent=4))
    L.append("")
    L.append(para(CUNNING_NARRATION["the_safeguard"], indent=4))
    L.append("")
    L.append(para(CUNNING_NARRATION["not_uniform"], indent=4))
    for mode, d in CUNNING_NARRATION["modes"].items():
        L.append("")
        L.append(bullet(mode, d.get("where_the_doubt_lives", "")))
        L.append(wrap("Cultures: " + ", ".join(d.get("cultures", [])), indent=6, hang=HANG))
    return "\n".join(L)


# ================================================================ §4 THE WORLD

def sec_map():
    """Corners and sea — orientation, before anyone is introduced."""
    L = [para(MAP.get("world_name", ""))]
    L.append("")
    L.append(rule("THE FOUR CORNERS"))
    for dom, where in MAP.get("corners", {}).items():
        L.append("")
        L.append(bullet(dom.upper(), where))
    L.append("")
    L.append(rule("THE SEA"))
    L.append("")
    L.append(para(MAP.get("sea", ""), indent=4))
    for stretch, desc in MAP.get("sea_stretches", {}).items():
        L.append("")
        L.append(bullet(stretch, desc))
    return "\n".join(L)


def sec_land():
    rl = MAP.get("regional_lore", {})
    L = []
    loose = [p for p in PLACE_UNOWNED if p in rl
             and not str(rl[p]).strip().startswith("UNDEFINED")]
    if loose:
        L.append("")
        L.append(rule("PLACES BELONGING TO NOBODY"))
        for p in loose:
            L.append("")
            L.append(bullet(p, rl[p]))

    undefined = sorted(k for k, v in rl.items() if str(v).strip().startswith("UNDEFINED"))
    if undefined and designing():
        L.append("")
        L.append(rule("NOT YET DESCRIBED"))
        L.append(wrap(", ".join(undefined), indent=4, hang=HANG))

    if "naming_registers" in visible("MAP", MAP):
        L.append("")
        L.append(rule("HOW PLACES ARE NAMED"))
        for reg in MAP.get("naming_registers", []):
            L.append(wrap("- " + clean(reg), indent=4, hang=HANG))
    return "\n".join(L)


# ================================================================ §5 THE GODS

def sec_gods():
    L = []
    if designing():
        L.append(para(DIVINITY_RULE))
        L.append("")

    L.append("")
    L.append(rule("THE TETRAMORPH — THE FOUR YOU MAY APPROACH"))
    L.append("")
    if TETRAMORPH.get("function") and designing():
        L.append(para(TETRAMORPH["function"], indent=4))
    for god in ("Ollanenor", "Anumaranth", "Melvanar", "Lorenthal"):
        g = GODS.get(god, {})
        if not g:
            continue
        head = f"{god.upper()} — {g.get('domain','')}"
        L.append("")
        L.append(bullet(head, g.get("nature", "")))
        for k in ("seat", "order", "adherents"):
            if g.get(k):
                L.append(para(f"{nice(k)}: {g[k]}", indent=6))

    L.append("")
    L.append(rule("THE ONE YOU MAY NOT"))
    e = GODS.get("Esselantheum", {})
    if e:
        L.append("")
        L.append(bullet(f"ESSELANTHEUM — {e.get('title','')}", e.get("nature", "")))
        for k in ("the_name", "tell"):
            if e.get(k):
                L.append("")
                L.append(para(e[k], indent=6))
    for k in ("inquisition_remit", "inquisitors_burden", "why_no_crusade"):
        if TETRAMORPH.get(k):
            L.append("")
            L.append(bullet(nice(k), TETRAMORPH[k]))

    fp = GODS.get("The False Prophet", {})
    if fp:
        L.append("")
        L.append(rule("AND THE ONE WHO SELLS ACCESS"))
        L.append("")
        L.append(bullet("THE FALSE PROPHET", fp.get("nature", "")))
        if TERMS.get("Order of the Last Prophet"):
            L.append("")
            L.append(para(TERMS["Order of the Last Prophet"], indent=6))

    L.append("")
    L.append(rule("WHAT EACH DOMAIN DOES WITH ALL THIS"))
    for dom, d in PANTHEON_ADJACENCY.items():
        L.append(wrap(f"{dom:<10} pious: {d.get('if_pious','')}", indent=4, hang=HANG))
        L.append(wrap(f"{'':<10} not:   {d.get('if_not_pious','')}", indent=4, hang=HANG))

    myth = visible("MYTHOS", MYTHOS)
    if len(myth) > (1 if "rule" in myth else 0):
        L.append("")
        L.append(rule("MONSTERS ARE NOT GODS"))
    L.append("")
    if designing() and MYTHOS.get("rule"):
        L.append(para(MYTHOS["rule"], indent=4))
    for k, v in visible("MYTHOS", MYTHOS).items():
        if k == "rule":
            continue
        L.append("")
        L.append(bullet(k, v))
    return "\n".join(L)


# ================================================================ §6 RECKONING

def sec_reckoning():
    L = []
    for k in [x for x in ("epoch", "unit", "gradient_rule", "present")
              if x in visible("TIMELINE", TIMELINE)]:
        if TIMELINE.get(k):
            L.append(para(TIMELINE[k], indent=2))
    og = TIMELINE.get("old_gods_era", {})
    if og:
        L.append("")
        L.append(rule(og.get("name", "THE AGE OF DARKNESS").upper(), og.get("dating", "")))
        if og.get("premise"):
            L.append("")
            L.append(para(og["premise"], indent=4))
        L.append("")

    yz = TIMELINE.get("year_zero", {})
    if yz:
        L.append("")
        L.append(rule("YEAR 0 — " + yz.get("event", ""), ""))
        for k in ("content", "untouched", "note"):
            if yz.get(k):
                L.append("")
                L.append(para(yz[k], indent=4))
        L.append("")

    starts = TIMELINE.get("age_starts", {})
    names = AGES.get("names", {})
    order = list(starts)
    if starts:
        L.append("")
        L.append(rule("THE FIVE AGES"))
        L.append("")
        for i, dom in enumerate(order):
            nxt = starts[order[i + 1]] if i + 1 < len(order) else None
            span = f"{starts[dom]}-{nxt}" if nxt is not None else f"{starts[dom]}-present"
            L.append(f"    {span:<15}{dom:<11}{names.get(dom, '')}")
        for k in ("structure", "naming_logic"):
            if k in visible("AGES", AGES) and AGES.get(k):
                L.append("")
                L.append(para(AGES[k], indent=4))

    evs = TIMELINE.get("events", [])
    if evs:
        L.append("")
        L.append(rule("THE CHRONICLE"))
        current, last_label = None, None
        for e in evs:
            dom = str(e.get("age", "")).split(" ")[0].split("(")[0].strip()
            if dom != current:
                current = dom
                span = ""
                if dom in starts:
                    i = order.index(dom)
                    nxt = starts[order[i + 1]] if i + 1 < len(order) else None
                    span = f"{starts[dom]}-{nxt}" if nxt is not None else f"{starts[dom]}-present"
                L.append("")
                L.append(rule(names.get(dom, dom).upper(), span))
                last_label = None
            label = str(e.get("year", ""))
            if e.get("provisional"):
                label += "   (provisional)"
            if label == last_label:
                L.append(para(e.get("event", ""), indent=6))
            else:
                L.append("")
                L.append(bullet(label, e.get("event", "")))
                last_label = label

    imp = TIMELINE.get("implications", {}) if "implications" in visible("TIMELINE", TIMELINE) else {}
    if imp:
        L.append("")
        L.append(rule("WHAT THE RECKONING IMPLIES"))
        for k, v in imp.items():
            L.append("")
            L.append(bullet(nice(k), v))
    return "\n".join(L)


# ================================================================ §7 FORMATION

def sec_darkness():
    """Before the count: the four peoples, and how the other eleven came to be."""
    L = []
    og = TIMELINE.get("old_gods_era", {})
    if og:
        L.append(rule("THE FOUR FOUNDINGS"))
        for people, text in og.get("the_four_foundings", {}).items():
            L.append("")
            L.append(bullet(people.upper(), text))
        exp = og.get("the_slow_expansion", {})
        if exp:
            L.append("")
            L.append(rule("AND IN TIME"))
            for people, text in exp.items():
                L.append("")
                L.append(bullet(people.upper(), text))
        if og.get("consequence"):
            L.append("")
            L.append(para(og["consequence"], indent=4))
        L.append("")
        L.append("")
    return "\n".join(L) + sec_formation()


def sec_formation():
    L = []
    if designing() and LORE_SEQUENCE.get("why"):
        L.append(para(LORE_SEQUENCE["why"]))
        L.append("")

    # ---- the vocabulary ----
    for dom in DOMAINS:
        L.append("")
        L.append(rule(dom.upper()))
        for key, label in DOMAIN_ROWS:
            f = fact(label, DOMAINS[dom].get(key, ""))
            if f:
                L.append("  " + f)

    # ---- how the other eleven came to be ----
    L.append("")
    L.append("")
    if "rule" in visible("FORMATION", FORMATION):
        L.append(para(FORMATION["rule"]))
        L.append("")
    L.append(rule("THE INDUSTRY DIASPORA"))
    for k, v in FORMATION.get("industry_diaspora", {}).items():
        L.append("")
        L.append(bullet(k if k != "second_order" else "SECOND-ORDER CONTACT", v))
    L.append("")
    L.append(rule("THE FOUR THAT FORMED ANOTHER WAY"))
    for k, v in FORMATION.get("non_industry", {}).items():
        L.append("")
        L.append(bullet(k, v))
    centre = FORMATION.get("the_centre", {})
    if centre:
        L.append("")
        L.append(rule("AND THE CENTRE"))
        for k, v in centre.items():
            L.append("")
            L.append(bullet(k if k[0].isupper() else nice(k), v))
    if FORMATION.get("the_kragh_wound"):
        L.append("")
        L.append(rule("THE KRAGH WOUND"))
        L.append("")
        L.append(para(FORMATION["the_kragh_wound"], indent=4))
    return "\n".join(L)


# ================================================================ §8 PROFILES

FACT_FIELDS = [
    ("government",         "government",           "Government"),
    ("authority",          "source_of_authority",  "Authority"),
    ("sacred",             "sacred",               "Sacred"),
    ("org_form",           "org_form",             "Organization"),
    ("economy",            "economy",              "Economy"),
    ("kinship_unit",       "kinship_unit",         "Kinship"),
    ("identity_theory",    "identity_theory",      "Identity"),
    ("succession",         "succession",           "Succession"),
    ("attitude_to_change", "attitude_to_change",   "Change"),
    ("military_doctrine",  "military_doctrine",    "War doctrine"),
    ("taboo",              "taboo",                "Taboo"),
    ("defined_against",    "defined_against",      "Defined against"),
    ("naming",             "naming_grammar",       "Naming"),
    ("monuments",          "monuments",            "Monuments"),
]

EXTRA_FIELDS = [
    ("trade_role",       "Trade role"),
    ("trade_relation",   "Trade"),
    ("internal_conflict", "Internal conflict"),
    ("role",             "Role"),
    ("doctrine",         "Doctrine"),
    ("strategy",         "Strategy"),
    ("limits",           "Limits"),
    ("pragmatism",       "Pragmatism"),
    ("warband_spectrum", "Warbands"),
    ("the_antagonist",   "Their expansion"),
    ("the_economy",      "Their economy"),
    ("the_fund",         "The fund"),
    ("the_army",         "Their army"),
    ("governance",       "Governance"),
    ("diplomatic_role",  "Diplomacy"),
]

# culture -> (mode, where the doubt lives)
_DOUBT = {}
for _mode, _d in CUNNING_NARRATION.get("modes", {}).items():
    for _c in _d.get("cultures", []):
        _DOUBT[_c] = (_mode, _d.get("where_the_doubt_lives", ""))


def resolve_axes(name):
    c = CULTURES.get(name, {})
    a = CULTURE_AXES.get(name, {})
    is_pure = c.get("type") == "pure"
    dom = DOMAINS.get(c["domains"][0], {}) if c.get("domains") else {}
    out = {}
    for ax_key, dom_key, label in FACT_FIELDS:
        val = dom.get(dom_key, "") if is_pure else (a.get(ax_key) or dom.get(dom_key, ""))
        if val:
            out[label] = val
    return out


def get_origin(name):
    return (FORMATION.get("industry_diaspora", {}).get(name)
            or FORMATION.get("non_industry", {}).get(name)
            or FORMATION.get("the_centre", {}).get(name))


def get_rivals(name):
    out = []
    for key, data in RIVALRIES.items():
        if not isinstance(data, dict) or " vs " not in key:
            continue
        a, b = [s.strip() for s in key.split(" vs ", 1)]
        if name == a:
            out.append((b, data.get("over", "")))
        elif name == b:
            out.append((a, data.get("over", "")))
    return out


def get_notes(name):
    notes = []
    c = CULTURES.get(name, {})
    for field, label in EXTRA_FIELDS:
        if c.get(field):
            notes.append((label, c[field]))

    if name == "Belvarath":
        for k in ("the_draghen", "the_pairing", "one_name_between_two", "why_it_holds",
                  "the_taboo_explained", "the_oldest_monument", "the_horror"):
            if k in visible("PRECEPTORY", PRECEPTORY) and PRECEPTORY.get(k):
                notes.append((nice(k), PRECEPTORY[k]))
    if name == "Astravantheliad":
        for k in ("internal_self_image", "external_reputation", "why_illegible"):
            if k in visible("ASTRAVANTHELIAD_PARADOX", ASTRAVANTHELIAD_PARADOX) \
                    and ASTRAVANTHELIAD_PARADOX.get(k):
                notes.append((nice(k), ASTRAVANTHELIAD_PARADOX[k]))
    if name in ("Shassolin", "Ossensteins"):
        notes.append(("See also", "Section 9 — the Order of the Last Prophet, the machine they "
                                  "run and are run by"))
    if name == "Astravantheliad":
        notes.append(("See also", "Section 9 — the Duke, the fixed point they measure distance to"))

    for ev_name, ev in EVENTS.items():
        owners = ev.get("cultures")
        if owners is not None:
            linked = name in owners
        else:
            linked = name.lower() in " ".join(str(v) for v in ev.values()).lower()
        if linked:
            body = " ".join(
                str(v) for k, v in ev.items()
                if k not in ("cultures", "year", "type", "hero")
                and k not in DESIGN_ONLY.get("event_keys", [])
                and isinstance(v, str)
            )
            if body:
                label = f"Event - {ev_name}"
                if ev.get("year"):
                    yr = str(ev["year"])
                    label += f" — {yr}" if "(" in yr else f" ({yr})"
                notes.append((label, body))
    return notes


def profile(name):
    c = CULTURES.get(name, {})
    a = CULTURE_AXES.get(name, {})
    dom = " x ".join(c.get("domains", []))

    ov = OVERVIEW.get(name) if not designing() else None
    L = ["=" * WIDTH, name.upper()]
    meta = f"{c.get('type','').capitalize()}  |  {dom}"
    if not ov:
        meta += f"  |  {c.get('region','')}"
    L.append(wrap(meta, hang=HANG))
    L.append("=" * WIDTH)
    L.append("")

    if ov:
        L.append(wrap(clean(ov) + ".", hang=0))
        L.append("")
        L.append("-" * WIDTH)
        for _, _, label in FACT_FIELDS:
            axes0 = resolve_axes(name)
            if label in axes0:
                f = fact(label, axes0[label])
                if f:
                    L.append(f)
        L.append("-" * WIDTH)
        pl = [p for p in PLACE_OWNERS.get(name, [])
              if p in MAP.get("regional_lore", {}) and p.lower() not in ov.lower()]
        if pl:
            L.append("")
            L.append("PLACES")
            for p in pl:
                L.append(bullet(p, MAP["regional_lore"][p]))
                L.append("")
            L.pop()
        for blk, head in ((get_rivals(name), "RIVALS"), ):
            if blk:
                L.append("")
                L.append(head)
                for other, over in blk:
                    L.append(para(f"{other} — {sl(clean(over))}", indent=2))
        notes0 = get_notes(name)
        if notes0:
            L.append("")
            L.append("NOTES")
            for label, text in notes0:
                L.append(para(f"{label}: {sl(clean(text))}", indent=2))
                L.append("")
            L.pop()
        return "\n".join(L)

    identity = c.get("identity", "").strip()
    text = identity
    if "lead" not in DESIGN_ONLY.get("culture_axes_keys", []) or designing():
        lead = clean(a.get("lead", ""))
        if lead and lead.lower() not in identity.lower():
            text = f"{identity} In essence: {lead}."
    L.append(wrap(clean(text) + ".", hang=0))

    if name in _DOUBT and designing():
        mode, where = _DOUBT[name]
        L.append("")
        L.append("HOW TO READ THIS ENTRY")
        L.append(para(f"{mode}. {where}", indent=2))

    origin = get_origin(name)
    if origin:
        L.append("")
        L.append("ORIGIN")
        L.append(para(sl(origin), indent=2))

    axes = resolve_axes(name)
    if axes:
        L.append("")
        L.append("-" * WIDTH)
        for _, _, label in FACT_FIELDS:
            if label in axes:
                f = fact(label, axes[label])
                if f:
                    L.append(f)
        L.append("-" * WIDTH)

    places = [p for p in PLACE_OWNERS.get(name, []) if p in MAP.get("regional_lore", {})]
    if places:
        L.append("")
        L.append("PLACES")
        for p in places:
            L.append(bullet(p, MAP["regional_lore"][p], label_indent=2, body_indent=6))
            L.append("")
        L.pop()

    rivals = get_rivals(name)
    if rivals:
        L.append("")
        L.append("RIVALS")
        for other, over in rivals:
            L.append(para(f"{other} — {sl(clean(over))}", indent=2))

    notes = get_notes(name)
    if notes:
        L.append("")
        L.append("NOTES")
        for label, text in notes:
            L.append(para(f"{label}: {sl(clean(text))}", indent=2))
            L.append("")
        L.pop()
    return "\n".join(L)


def sec_fifteen():
    L = []
    for title, members in THREADS:
        L.append(banner(title))
        for name in members:
            if name in CULTURES:
                L.append(profile(name))
                L.append("")
                L.append("")
    return "\n".join(L)


# ================================================================ §9 THE PRESENT

def sec_present():
    L = [para("Three things shape the world as it stands. None of them is a country.")]

    L.append("")
    L.append(rule("I.  THE ORDER OF THE LAST PROPHET"))
    for k, v in visible("FALSE_RELIGION_ENGINE", FALSE_RELIGION_ENGINE).items():
        if k == "the_three_stories":
            continue
        L.append("")
        L.append(bullet(nice(k), v))
    stories = FALSE_RELIGION_ENGINE.get("the_three_stories", {})
    if stories:
        L.append("")
        L.append(rule("THE SAME MAN, THREE WAYS"))
        for k, v in stories.items():
            L.append("")
            L.append(bullet(k if not k.startswith("why") else nice(k), v))

    L.append("")
    L.append(rule("II.  THE DUKE"))
    for k, v in THE_DUKE.items():
        L.append("")
        L.append(bullet(nice(k), v))

    L.append("")
    L.append(rule("III.  THE TWO ARCHIVES"))
    for k, v in ARCHIVE_OPPOSITION.items():
        L.append("")
        L.append(bullet(k if not k.startswith("the_") else nice(k), v))
    return "\n".join(L)


# ================================================================ §10 APPENDIX

def sec_appendix():
    L = [para("Reference, not narrative.")]

    L.append("")
    L.append(rule("HOW EACH DOMAIN SEES THE OTHERS"))
    L.append("")
    L.append(para("Read down: the viewer. Read across: the judged. Asymmetric by design — each "
                  "judges by its own value.", indent=4))
    L.append("")
    colw = (WIDTH - 4 - 12) // len(REPUTATION)
    L.append(" " * 4 + "viewer".ljust(12)
             + "".join(d[:colw - 1].ljust(colw) for d in REPUTATION))
    for viewer, row in REPUTATION.items():
        line = " " * 4 + viewer.ljust(12)
        for subject in REPUTATION:
            line += clean(row.get(subject, ""))[:colw - 2].ljust(colw)
        L.append(line.rstrip())

    L.append("")
    L.append(rule("NAMING GRAMMARS"))
    for dom, d in DOMAINS.items():
        L.append("")
        L.append(bullet(dom.upper(), f"{d.get('naming_grammar','')} — e.g. "
                                     f"{d.get('naming_example','')}. "
                                     f"{d.get('affiliation_display','')}"))

    if show_dict("PHONOLOGY"):
        L.append("")
        L.append(rule("PHONOLOGY"))
        for dom, d in DOMAINS.items():
            L.append(wrap(f"{dom:<10}{d.get('phonology_signature','')}", indent=4, hang=HANG))
            L.append(wrap("consonants: " + ", ".join(d.get("consonants", [])),
                          indent=14, hang=HANG))
        for k in ("vowel_harmony", "endings", "collision_fix", "cunning_signature"):
            if PHONOLOGY.get(k):
                L.append("")
                L.append(bullet(nice(k), PHONOLOGY[k]))

    L.append("")
    L.append(rule("TERMS"))
    for k, v in TERMS.items():
        L.append("")
        L.append(bullet(k, v))

    if OPEN_THREADS and show_dict("OPEN_THREADS"):
        L.append("")
        L.append(rule("OPEN THREADS"))
        for t in OPEN_THREADS:
            L.append("")
            L.append(para("- " + t, indent=4))
    return "\n".join(L)


# ================================================================ main

# (title, builder, designer_only)
DOC_ALL = [
    ("THE PREMISE",           sec_premise,     False),
    ("HOW TO READ THIS",      sec_how_to_read, True),
    ("THE MAP",               sec_map,         False),
    ("THE FIFTEEN",           sec_fifteen,     False),
    ("THE WORLD",             sec_land,        False),
    ("THE TIMELINE",          sec_reckoning,   False),
    ("THE AGE OF DARKNESS",   sec_darkness,    False),
    ("THE GODS",              sec_gods,      True),
    ("WHAT RUNS THE PRESENT", sec_present,   True),
    ("APPENDIX",              sec_appendix,  True),
]


def doc():
    return [(t, f) for t, f, d in DOC_ALL if designing() or not d]


def contents():
    title = "RENOWN — THE WORLD" if not designing() else "RENOWN — THE WORLD (designer edition)"
    L = ["=" * WIDTH, title.center(WIDTH), "=" * WIDTH, "", "CONTENTS", ""]
    for i, (title, _) in enumerate(doc(), 1):
        L.append(f"    {i:>2}.  {title}")
    return "\n".join(L)


def main(path=None, audience="reader"):
    global AUDIENCE
    AUDIENCE = audience
    if path is None:
        path = "world.txt" if audience == "reader" else "world_design.txt"
    out = [contents()]
    for i, (title, fn) in enumerate(doc(), 1):
        out.append(title_bar(i, title))
        if title not in NO_OPENER:
            opener = prose(title)
            if opener:
                out.append(opener)
                out.append("")
        out.append(fn())
        out.append("")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    lines = sum(1 for _ in open(path, encoding="utf-8"))
    print(f"[{audience:<8}] {path:<18} {len(doc())} sections, {len(CULTURES)} cultures, "
          f"{lines} lines")


def direction_guide():
    """Every overview should orient itself against the culture the reader just
    met — not against a place four entries back. Prints the correct anchor for
    each, and flags any that reference something other than their predecessor."""
    import re
    pat = re.compile(r"\b(north-west|north-east|south-west|south-east|north|south|east|west)\b",
                     re.I)
    print("\n  ORIENT EACH OVERVIEW AGAINST THE ONE BEFORE IT")
    prev = None
    for title, members in THREADS:
        print(f"    == {title}")
        for name in members:
            if prev is None:
                print(f"       {name:<17} opens the document — absolute framing")
            else:
                want = bearing(prev, name)
                seat = CULTURE_SEATS.get(prev, prev)
                head = OVERVIEW.get(name, "")[:180]
                names_pred = (prev.lower() in head.lower()
                              or seat.split(" /")[0].lower() in head.lower())
                said = [d.lower() for d in pat.findall(head)]
                ok = names_pred and (not said or any(d in want for d in said))
                flag = "" if ok else "   <-- rewrite"
                print(f"       {name:<17} {want:<12} of {prev} ({seat}){flag}")
            prev = name
    print()


if __name__ == "__main__":
    main(audience="reader")
    main(audience="designer")
    direction_guide()
