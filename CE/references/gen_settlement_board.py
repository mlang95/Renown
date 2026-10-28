#!/usr/bin/env python3
"""
gen_settlement_board.py  --  Renown settlement-board emulator generator.

Reads the master data file (renown_data_d10.py) and emits a single self-contained
settlement_board.html.  No mechanics are invented: every innate/mastery/empire_bonus
string is parsed transparently into typed "atoms", and ONLY flat / unconditional
atoms are summed.  Conditional, triggered, seasonal-gated, or non-numeric effects
are shown verbatim but excluded from headline totals.

Sections: Pursuits · Infrastructure · Wonders · Army · Treasury.

Usage:
    python gen_settlement_board.py [--data renown_data_d10.py] [--out settlement_board.html]

Notes / assumptions (also surfaced in the HTML):
  * Pieces assumed ACTIVE / undamaged (Principle 6 not modelled).
  * mastery_req precedence: '+' is AND across ' or ' / '/' groups.
  * Wards counted, not placed (adjacency not enforced); 'efficient' source in pool = free ward.
  * External mastery_req tokens (Cathedral/Keep/Library/Town Hall) are satisfied by
    adding that Infrastructure.
  * Army upkeep = the Army's Retinue-type cost (RETINUES[*]["cost"]) per Army; the
    "Upkeep -X" pool from active pieces is subtracted once from the total of all Armies.
"""
import argparse, json, re, sys, os

def load(datapath):
    ns = {}
    with open(datapath, "r", encoding="utf-8") as fh:
        exec(fh.read(), ns)
    return ns

# ---------- text helpers ----------
def strip_md(s):
    if s is None:
        return ""
    if isinstance(s, (list, tuple)):
        s = ", ".join(str(x) for x in s)
    s = str(s).replace("−", "-")
    s = re.sub(r"\*\*|\*|__", "", s)
    s = s.replace("\u2019", "'")
    return s.strip()

COND_WORDS = [
    " while ", " when ", " per ", " if ", "once/turn", "once /turn", "once per ", " target",
    "for trading", "at war", "besieged", "range 0", "other player", " players",
    "without", "trade partner", "endorsed", "first ", " oppose", " support",
    " vote", "council", "envoy", " action", " muster", " army", "armies", "cavalry",
    "sally", " reach", "each ", "no longer", "instead", " pass", " fail",
    "condemn", "endorse", " domain", "standing", "besiege", " loan", "tithe",
    " recoup", "another player", "every ", "may perform", "targeting", " move ",
]
SEASON_RE = re.compile(r"([+-]?\d{2,})\s*(?:gold\s*)?in\s+(Fall|Winter|Spring|Summer)", re.I)
SCALE_RE  = re.compile(r"\+?(\d+)\s*(?:gold\s*)?(?:for each|per)\s+active\s+(\w+)\s+(?:special\w*|holdings?|pursuits?)\b", re.I)
CRAFT_RE  = re.compile(r"Craft\s*\+?\s*(\d+)", re.I)
FAITH_RE  = re.compile(r"Faith\s*\+?\s*(\d+)", re.I)
DOUBT_RE  = re.compile(r"Doubt\s*\+?\s*(\d+)", re.I)
UPKEEP_RE = re.compile(r"Upkeep\s*(-?\d{2,})", re.I)
AUTH_RE   = re.compile(r"Authority\s*([+\-\u2212]\s?\d+)")   # Envoy score modifier (TERM_ENVOY_SCORE)
INFL_RE   = re.compile(r"(?:(?<!Max )Influence\s*([+-]\s?\d+))|(?:([+-]\s?\d+)\s*Influence)", re.I)   # Influence tokens (canon "Influence +N"; "Max Influence +N" is the vote limit)
EXTORT_RE = re.compile(r"Extort\s*(\d+)", re.I)
BUILDT_RE = re.compile(r"Build Timer\s*(-?\d+)", re.I)
SIEGET_RE = re.compile(r"Siege Timer\s*([+-]?\d+)", re.I)
SPEED_RE  = re.compile(r"Speed\s*([+-]\s?\d+)", re.I)
GOLD_RE   = re.compile(r"^[+-]?\s?(\d{2,})(?:\s*gold)?$")

COMBAT_KW = ["unlock", "tier", "armor", "shield", "weapon", "ranged", "cavalry",
    "serrated", "poison", "parry", "riposte", "recover", "endurance", "immune",
    "nimble", "drilled", "zealous", "man-at-arms", "sergeant", "knight", "muster",
    "reach", "strike", "tactic", "panic", "deadly", "cleave", "dual", "planishing",
    "seize the initiative", "arquebus", "shake", "enduring", "sally", "siege",
    "blunder", "garrison"]
ENVOY_KW = ["envoy", "oppose", "support", "vote", "council", "condemn", "endorse",
    "diplomacy", "tribute", "spread gospel"]

def has_cond(lc):
    return any(w in lc for w in COND_WORDS)

def to_int(x):
    return int(re.sub(r"\s+", "", x))

def classify(clause):
    c = clause.strip().strip(".;,").strip()
    if not c:
        return None
    lc = " " + c.lower() + " "
    lc2 = re.sub(r"(?<!once) per turn|(?<=\d) each empire phase", " ", lc)     # "Influence +1 each Empire Phase" is flat, not conditional
    atom = {"text": c, "cat": "other", "val": None, "season": None,
            "cond": False, "flat": False, "scale": None, "natural": False}

    m = SCALE_RE.search(c)
    if m:
        atom.update(cat="gold", scale={"per": int(m.group(1)), "of": m.group(2).lower()}, cond=True)
        return atom
    m = SEASON_RE.search(c)
    if m:
        atom.update(cat="gold", val=to_int(m.group(1)), season=m.group(2).capitalize(), flat=True)
        return atom
    if c.lower() == "natural":
        atom.update(cat="natural", natural=True); return atom

    cond = has_cond(lc2)
    def finish(cat, val, summable):
        atom.update(cat=cat, val=val, cond=cond)
        atom["flat"] = (val is not None) and (not cond) and (cat in summable)
        return atom

    if EXTORT_RE.search(c):
        v = to_int(EXTORT_RE.search(c).group(1))
        m = re.fullmatch(r"Extort\s*\d+(\s+twice)?\.?", c, re.I)
        if m:                                   # bare "Extort N" (or "twice") = every Empire Phase
            atom.update(every=True); v = v * (2 if m.group(1) else 1)
        m = re.search(r"Extort\s*\d+\s+(?:per|every|from each other)\s+player\s+without\s+(?:an?\s+)?(.+)$", c, re.I)
        if m: atom.update(without=m.group(1).strip())
        return finish("extort", v, set())
    if re.search(r"recoup|loan|tithe", c, re.I):
        atom.update(cat="recoup", cond=True); return atom
    if UPKEEP_RE.search(c):
        return finish("upkeep", to_int(UPKEEP_RE.search(c).group(1)), {"upkeep"})
    if FAITH_RE.search(c):
        return finish("faith", to_int(FAITH_RE.search(c).group(1)), {"faith"})
    if DOUBT_RE.search(c):
        return finish("doubt", to_int(DOUBT_RE.search(c).group(1)), {"doubt"})
    if CRAFT_RE.search(c) and "craft" in lc:
        return finish("craft", to_int(CRAFT_RE.search(c).group(1)), {"craft"})
    if AUTH_RE.search(c):
        return finish("authority", to_int(AUTH_RE.search(c).group(1).replace("\u2212", "-")), set())
    if INFL_RE.search(c):
        mm = INFL_RE.search(c); v = mm.group(1) or mm.group(2)
        return finish("influence", to_int(v), {"influence"})
    if BUILDT_RE.search(c):
        return finish("build_timer", to_int(BUILDT_RE.search(c).group(1)), set())
    if SIEGET_RE.search(c):
        return finish("siege_timer", to_int(SIEGET_RE.search(c).group(1)), set())
    if SPEED_RE.search(c):
        return finish("speed", to_int(SPEED_RE.search(c).group(1)), set())
    if GOLD_RE.match(c):
        return finish("gold", int(GOLD_RE.match(c).group(1)) * (-1 if c.strip().startswith("-") else 1), {"gold"})

    if any(k in lc for k in COMBAT_KW):
        atom["cat"] = "combat"
    elif any(k in lc for k in ENVOY_KW):
        atom["cat"] = "envoy"
    atom["cond"] = cond
    return atom

_DOMS = "Diplomacy|Prowess|Cunning|Piety|Industry"
_N = r"([+\-\u2212]\s?\d+)"
def _iv(x): return int(re.sub(r"\s+", "", x).replace("\u2212", "-"))
def envoy_fx(raw):
    """Structured Envoy/Influence effects for the Table. Unknown clauses are ignored (text still shows).
    kinds: envoy (own Envoy ±X; scope council/personal/all), cap (vote cap), act (own action ±X, stage 2),
           defend (±X to actions targeting you, stage 2), pool (per-turn Influence), jester, noOppose, failPass."""
    out = []
    raw = re.sub(r",\s*except in Spring", " except in Spring", strip_md(raw or ""), flags=re.I)
    raw = re.sub(r"(While the Era is \w+),", r"\1", raw, flags=re.I)
    pend = (0, None)                       # each fx carries "t": the clause it was read from
    # "Whenever a Diplomacy Envoy you send Passes, you may instead perform a Cunning action" (Double Speak);
    # "Once per Envoy Phase, if your non-Cunning Envoy passes or is endorsed, you may instead perform a Cunning action" (Master Conspirator)
    for sen in re.split(r"(?<=\.)\s+|;", raw):
        m = re.search(r"(?:Whenever|if) (?:an?|your) (?:Personal )?(non-)?(" + _DOMS + r") Envoy(?: you send)? (Passes( or is Endorsed)?),? you may instead perform an? (" + _DOMS + r") action", sen, re.I)
        if m:
            om = re.search(r"Once per (\w+) Phase|Once per turn", sen, re.I)
            out.append({"k": "instead", "from": m.group(2).title(), "notFrom": bool(m.group(1)), "to": m.group(5).title(),
                        "outs": ["Passed", "Endorsed"] if m.group(4) else ["Passed"],
                        "once": (om.group(1).lower() if om and om.group(1) else "turn" if om else ""), "t": sen.strip()})
    pend = (len(out), None)
    for c in re.split(r"[;,]|\.\s+", raw):
        c = c.strip().rstrip(".")
        if not c: continue
        for f in out[pend[0]:]: f.setdefault("t", pend[1])
        pend = (len(out), c)
        m = re.search(r"(?:Authority|Influence)\s*" + _N + r"\s+(?:to|on)\s+(?:your\s+)?(non-)?Council Envoys$", c, re.I)
        if m: out.append({"k": "envoy", "val": _iv(m.group(1)), "scope": "personal" if m.group(2) else "council", "dom": "All"}); continue
        m = re.search(r"(?:Authority|Influence)\s*" + _N + r"\s+(?:to|on)\s+(?:your\s+)?(" + _DOMS + r")\s+Envoys$", c, re.I)
        if m: out.append({"k": "envoy", "val": _iv(m.group(1)), "scope": "all", "dom": m.group(2).title()}); continue
        m = re.search(r"(?:Authority|Influence)\s*" + _N + r"\s+(?:to|on)\s+(.+?)\s+(?:Envoys|actions)(\s+from players)?\s+target+ing\s+(?:you|this player|your settlements)", c, re.I)
        if m and m.group(2).lower().startswith("bandit"):
            out.append({"k": "bandit", "val": _iv(m.group(1))}); continue   # Bandit (Cunning) actions targeting you
        if m:
            what = m.group(2).strip(); dm = re.fullmatch(_DOMS, what, re.I)
            out.append({"k": "defend", "val": _iv(m.group(1)), "dom": dm.group(0).title() if dm else None,
                        "action": None if dm else what.title(), "players": bool(m.group(3))}); continue
        m = re.search(r"(?:Authority|Influence)\s*" + _N + r"\s+when performing\s+(" + _DOMS + r")\s+actions", c, re.I)
        if m: out.append({"k": "act", "val": _iv(m.group(1)), "dom": m.group(2).title()}); continue
        m = re.search(r"(?:Authority|Influence)\s*" + _N + r"\s+(?:to|on)\s+(?:your\s+)?(" + _DOMS + r")\s+actions$", c, re.I)
        if m: out.append({"k": "act", "val": _iv(m.group(1)), "dom": m.group(2).title()}); continue
        m = re.search(r"^(?:gain\s+)?(?:" + _N + r"\s*Influence|Influence\s*" + _N + r") per (Domain you are Rising|Established Standing|other player(?: (?:per Turn|each Empire Phase))?)$", c, re.I)
        if m:
            per = {"domain you are rising": "Rising", "established standing": "Established"}.get(m.group(3).lower(), "others")
            out.append({"k": "pool", "val": _iv(m.group(1) or m.group(2)), "per": per}); continue
        m = re.search(r"(?:Gain\s*)?(?:" + _N + r"\s*Influence|Influence\s*" + _N + r") while At War", c, re.I)
        if m: out.append({"k": "pool", "val": _iv(m.group(1) or m.group(2)), "per": "war"}); continue
        if re.search(r"additional Influence per Support or Oppose", c, re.I): out.append({"k": "cap", "val": 1}); continue
        m = re.search(r"Max Influence\s*" + _N + r" on every Envoy", c, re.I)
        if m: out.append({"k": "cap", "val": _iv(m.group(1))}); continue
        m = re.search(r"(First|Second) Oppose on your Envoy(?: each turn| per turn| each Envoy Phase)?: reduce by (\d+)", c, re.I)
        if m: out.append({"k": "jester", "n": 1 if m.group(1).lower() == "first" else 2, "val": int(m.group(2))}); continue
        m = re.search(r"First and second Oppose on (?:an Envoy of yours|your Envoys?)(?: each turn| per turn| each Envoy Phase)?: reduce by (\d+)", c, re.I)
        if m: out += [{"k": "jester", "n": 1, "val": int(m.group(1))}, {"k": "jester", "n": 2, "val": int(m.group(1))}]; continue
        m = re.search(r"^(" + _DOMS + r")? ?Envoys cannot Fail$", c, re.I)
        if m: out.append({"k": "failPass", "dom": m.group(1).title() if m.group(1) else None}); continue
        m = re.search(r"(" + _DOMS + r") actions targeting you can't be Endorsed", c, re.I)
        if m: out.append({"k": "noEndorse", "dom": m.group(1).title()}); continue
        if re.search(r"always vote last", c, re.I): out.append({"k": "voteLast"}); continue
        # "use your <Domain> value for all envoys when determining innate Influence/Authority" (The Illusionists)
        m = re.search(r"use your (" + _DOMS + r") value for all envoys", c, re.I)
        if m: out.append({"k": "domAs", "dom": m.group(1).title(), "for": "All"}); continue
        m = re.search(r"(" + _DOMS + r") Envoys use your (" + _DOMS + r") Standing for their innate", c, re.I)
        if m: out.append({"k": "domAs", "dom": m.group(2).title(), "for": m.group(1).title()}); continue
        m = re.search(r"(" + _DOMS + r") Envoys start at Authority equal to your (" + _DOMS + r") rank", c, re.I)
        if m: out.append({"k": "domAs", "dom": m.group(2).title(), "for": m.group(1).title()}); continue
        # "your Max Influence on Diplomacy Envoys is your Cunning rank" (The Illusionists): that Domain's rank sets the vote limit
        m = re.search(r"your Max Influence on (" + _DOMS + r") Envoys is your (" + _DOMS + r") rank", c, re.I)
        if m: out.append({"k": "capAs", "dom": m.group(2).title(), "for": m.group(1).title()}); continue
        # "can't be in an Alliance" / "cannot form alliances" / "can't join Alliances" / "No Alliances" (flag only)
        if re.search(r"(?:can(?:no|')t|may not) (?:be in an?|be a member of an?|form|join(?: an?)?) Alliances?\b|\bno Alliances\b", c, re.I): out.append({"k": "noAlliance"}); continue
        m = re.search(r"(?:with lower (" + _DOMS + r") (?:value|Standing) )?can't Oppose your (" + _DOMS + r") Envoys", c, re.I)
        if m:
            f = {"k": "noOppose", "dom": m.group(2).title()}
            if m.group(1): f["lower"] = m.group(1).title()   # only players with a lower <Domain> value are blocked
            out.append(f); continue
        if re.search(r"If your Envoy would fail", c, re.I): out.append({"k": "failPass"}); continue
        # faction / holding Envoy rules (fx kinds read by the board's Table)
        m = re.search(r"(?:Authority|Influence)\s*" + _N + r"\s+to\s+envoys sent during the Council Phase", c, re.I)
        if m: out.append({"k": "envoy", "val": _iv(m.group(1)), "scope": "council", "dom": "All"}); continue
        m = re.search(r"Every Envoy you send has (?:Authority|Influence)\s*" + _N + r"(,?\s*except in Spring)?", c, re.I)
        if m: out.append({"k": "envoy", "val": _iv(m.group(1)), "scope": "all", "dom": "All", "noSpring": bool(m.group(2))}); continue
        m = re.search(r"Your Personal Envoys have (?:Authority|Influence)\s*" + _N + r"(,?\s*except in Spring)?", c, re.I)
        if m: out.append({"k": "envoy", "val": _iv(m.group(1)), "scope": "personal", "dom": "All", "noSpring": bool(m.group(2))}); continue
        m = re.search(r"Your (" + _DOMS + r") Envoys have (?:Authority|Influence)\s*" + _N + r" when targeting a player with Public Order (?:above|greater than) (-?\d+)", c, re.I)
        if m: out.append({"k": "act", "val": _iv(m.group(2)), "dom": m.group(1).title(), "tgtPOabove": int(m.group(3))}); continue
        m = re.search(r"Authority\s*" + _N + r" on your (" + _DOMS + r") actions targeting a player with Public Order (-?\d+) or higher", c, re.I)
        if m: out.append({"k": "act", "val": _iv(m.group(1)), "dom": m.group(2).title(), "tgtPOabove": int(m.group(3)) - 1}); continue
        m = re.search(r"(?:^|\b)you have (?:Authority|Influence)\s*" + _N + r" on (Personal )?(" + _DOMS + r") Envoys", c, re.I)
        if m: out.append({"k": "envoy", "val": _iv(m.group(1)), "scope": "personal" if m.group(2) else "all", "dom": m.group(3).title()}); continue
        m = re.search(r"A (" + _DOMS + r") Envoy you send can't fail", c, re.I)
        if m: out.append({"k": "failPass", "dom": m.group(1).title(), "condemned": True}); continue
        m = re.search(r"Each player allied with you has (?:Authority|Influence)\s*" + _N + r" on their (Personal )?Envoys", c, re.I)
        if m: out.append({"k": "allyEnvoy", "val": _iv(m.group(1)), "scope": "personal" if m.group(2) else "all"}); continue
        m = re.search(r"Your Vote counts as (\d+) votes toward Domain selection", c, re.I)
        if m: out.append({"k": "councilVotes", "val": int(m.group(1))}); continue
        if re.search(r"Council Envoys you send are always Endorsed", c, re.I): out.append({"k": "councilEndorse"}); continue
        if re.search(r"you choose every Council Envoy's Domain", c, re.I): out.append({"k": "councilChoose"}); continue
        m = re.search(r"While the Era is (\w+),? you may spend up to (\d+) Influence per Envoy", c, re.I)
        if m: out.append({"k": "capEra", "era": m.group(1).title(), "val": int(m.group(2))}); continue
        m = re.search(r"While the Era is (\w+),? your Max Influence is (\d+) on every Envoy", c, re.I)
        if m: out.append({"k": "capEra", "era": m.group(1).title(), "val": int(m.group(2))}); continue
        if re.search(r"unspent Influence isn't discarded", c, re.I): out.append({"k": "carry"}); continue
        if re.search(r"You Abstain on every vote on other players' Envoys", c, re.I): out.append({"k": "alwaysAbstain"}); continue
        if re.search(r"You abstain (?:on )?every Personal Envoy", c, re.I): out.append({"k": "alwaysAbstain"}); continue   # Council Envoys take no votes
        if re.search(r"You can't vote nor send Council Envoys", c, re.I): out += [{"k": "noVote"}, {"k": "noCouncil"}]; continue
        m = re.search(r"other players must spend (\d+) Influence to affect your Envoys by 1", c, re.I)
        if m: out.append({"k": "voteCost", "val": int(m.group(1))}); continue
        if re.search(r"Ignore the innate Doubt and Influence modifiers for being At War", c, re.I): out.append({"k": "ignoreWar"}); continue
        m = re.search(r"(?:gain\s*)?(?:" + _N + r"\s*Influence|Influence\s*" + _N + r") (?:for every|per) (\d+) (?:Holdings|Pursuits)", c, re.I)
        if m: out.append({"k": "pool", "val": _iv(m.group(1) or m.group(2)), "per": "holdings", "n": int(m.group(3))}); continue
    for f in out[pend[0]:]: f.setdefault("t", pend[1])
    return out

def combine_parts(innate, mastery):
    """Innate + Mastery merged, same stat summed; each part tagged with where it came from:
    'i' innate only, 'm' mastery only, 'im' both. ['+200', 'im'], ['Craft +2', 'im'], ['Gain X', 'm']"""
    gold = 0; gorg = set(); sums = {}; org = {}; order = []; texts = []; torg = {}
    def parts(raw):   # ';' splits clauses; ',' splits off stat-like pieces only (prose keeps its commas)
        for cl in re.split(r";", strip_md(raw)):
            cl = cl.strip().rstrip(".")
            if not cl or cl in ("-", "\u2014"): continue
            prose = []
            for bit in [b.strip() for b in cl.split(",")]:
                if re.fullmatch(r"[+\-\u2212]\s?\d+|[A-Za-z][A-Za-z' ]*?\s*[+\-\u2212]\s?\d+|[+\-\u2212]\s?\d+\s+[A-Za-z][\w/ ]*", bit):
                    if prose: yield ", ".join(prose); prose = []
                    yield bit
                elif bit: prose.append(bit)
            if prose: yield ", ".join(prose)
    for raw, tag in ((innate or "", "i"), (mastery or "", "m")):
        for c in parts(raw):
            m = re.fullmatch(r"([+\-\u2212])\s?(\d+)", c)
            if m:
                gold += int(m.group(2)) * (-1 if m.group(1) != "+" else 1); gorg.add(tag); continue
            m = re.fullmatch(r"([A-Za-z][A-Za-z' ]*?)\s*([+\-\u2212])\s?(\d+)(?:\s+(.+))?", c)     # "Craft +1", "Upkeep -1000 while …"
            if m:
                k = ("w", m.group(1).strip(), (m.group(4) or "").strip()); v = int(m.group(3)) * (-1 if m.group(2) != "+" else 1)
            else:
                m = re.fullmatch(r"([+\-\u2212])\s?(\d+)\s+([A-Za-z].*)", c)                          # "+1 Influence per …"
                if not m:
                    if c not in torg: texts.append(c); torg[c] = set()
                    torg[c].add(tag); continue
                k = ("n", m.group(3).strip(), ""); v = int(m.group(2)) * (-1 if m.group(1) != "+" else 1)
            if k not in sums: order.append(k); sums[k] = 0; org[k] = set()
            sums[k] += v; org[k].add(tag)
    o = lambda st: "".join(x for x in "im" if x in st)
    out = []
    if gorg and gold: out.append([("+" if gold > 0 else "\u2212") + str(abs(gold)), o(gorg)])
    for k in order:
        v = sums[k]
        if not v: continue
        sv = ("+" if v > 0 else "\u2212") + str(abs(v))
        out.append([(f"{k[1]} {sv}" + (f" {k[2]}" if k[2] else "")) if k[0] == "w" else f"{sv} {k[1]}", o(org[k])])
    return out + [[t, o(torg[t])] for t in texts]

def combine_effects(innate, mastery):
    """Innate + Mastery as one line (Mastery assumed earned): '+100; Craft +1' + '+100; Craft +1; Gain X' -> '+200; Craft +2; Gain X'."""
    return "; ".join(t for t, _ in combine_parts(innate, mastery))

def rules_payload(ns, rules_path):
    """RULES md -> HTML for the Reference view: {{VAL:}} / {{TABLE:}} resolved via wiki_markers (same as the wiki).
    Returns {"html":…, "toc":[[level, id, title], …]} or None."""
    if not rules_path or not os.path.exists(rules_path): return None
    try:
        import types, html as _h
        if "renown_data" not in sys.modules:                 # wiki_markers does `import renown_data`; hand it the loaded data
            m = types.ModuleType("renown_data"); m.__dict__.update(ns); sys.modules["renown_data"] = m
        here = os.path.dirname(os.path.abspath(__file__))
        if here not in sys.path: sys.path.insert(0, here)
        import wiki_markers as wm
    except Exception as e:
        print(f"  (rulebook: wiki_markers unavailable - {e})"); return None
    def slug(t): return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")
    def inline(t):
        t = _h.escape(t)
        t = re.sub(r"\*\*\*(.+?)\*\*\*", r"<strong><em>\1</em></strong>", t)
        t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
        t = re.sub(r"\*(.+?)\*", r"<em>\1</em>", t)
        return re.sub(r"`(.+?)`", r"<code>\1</code>", t)
    import rule_numbers as _rn
    md = wm.preprocess_inline(_rn.number_md(open(rules_path, encoding="utf-8").read(), mode="plain")[0])
    out, toc, stack, lines, i, seen = [], [], [], md.split("\n"), 0, {}
    def close():
        while stack: out.append("</ul>"); stack.pop()
    while i < len(lines):
        ln = lines[i].rstrip()
        if not ln.strip(): close(); i += 1; continue
        m = re.match(r"^(#{1,6})\s+(.*)$", ln)
        if m:
            close(); lvl = len(m.group(1)); t = m.group(2).strip(); sid = "rb-" + slug(t)
            seen[sid] = seen.get(sid, 0) + 1
            if seen[sid] > 1: sid += f"-{seen[sid]}"
            out.append(f"<h{min(lvl+1,6)} id='{sid}'>{inline(t)}</h{min(lvl+1,6)}>")
            if lvl <= 2: toc.append([lvl, sid, re.sub(r"[*`]", "", t)])
            i += 1; continue
        bh = wm.block_html(ln.strip())
        if bh is not None: close(); out.append(bh); i += 1; continue
        if "|" in ln and i + 1 < len(lines) and re.match(r"^\s*\|?[\s:\-|]+\|[\s:\-|]*$", lines[i+1].rstrip()) and "-" in lines[i+1]:
            close()
            cells = lambda r: [c.strip() for c in r.strip().strip("|").split("|")]
            head = cells(ln); i += 2; body = []
            while i < len(lines) and "|" in lines[i] and lines[i].strip(): body.append(cells(lines[i])); i += 1
            out.append("<table class='dtable'><thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr></thead><tbody>"
                       + "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body) + "</tbody></table>")
            continue
        lm = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", ln)
        if lm:
            ind = len(lm.group(1).replace("\t", "    "))
            if not stack or ind > stack[-1]: out.append("<ul>"); stack.append(ind)
            else:
                while len(stack) > 1 and ind < stack[-1]: out.append("</ul>"); stack.pop()
            out.append("<li>" + inline(lm.group(3)) + "</li>"); i += 1; continue
        close(); out.append("<p>" + inline(ln.strip()) + "</p>"); i += 1
    close()
    left = re.findall(r"\{\{[^}]*\}\}", "\n".join(out))
    if left: print(f"  (rulebook: {len(left)} unresolved markers, e.g. {left[0]})")
    return {"html": "\n".join(out), "toc": toc}

def tree_payload(ns, here):
    """Tech-tree charts: layout.json positions + builds_into / mastery_req edges (same graph as render_tree.py)."""
    path = os.path.join(here, "layout.json")
    if ns.get("SIMPLE"):   # one chart per root (gen_layout_roots.py), else one per Monument (gen_layout.py)
        for alt in ("layout_roots.json", "layout_simple.json"):
            if os.path.exists(os.path.join(here, alt)):
                path = os.path.join(here, alt); break
    if not os.path.exists(path): return None
    try: charts = json.load(open(path, encoding="utf-8"))
    except Exception: return None
    NODES = ns.get("NODES", {})
    def parse_req(r):
        if not r or str(r).strip() in ("", "-", "\u2014"): return []
        return [p.strip() for p in str(r).replace(" or ", "+").split("+") if p.strip() in NODES]
    CH = {n: [b for b in (d.get("builds_into") or []) if b in NODES] for n, d in NODES.items()}
    def desc(n):
        out = set(); q = [n]
        while q:
            x = q.pop()
            for c in CH.get(x, []):
                if c not in out: out.add(c); q.append(c)
        return out
    def parents(d):
        if ns.get("SIMPLE"):   # SIMPLE: edges are the efficient links (builds_into already mirrors them)
            e = d.get("efficient"); e = [e] if isinstance(e, str) else list(e or [])
            return [p for p in e if p in NODES]
        return parse_req(d.get("mastery_req"))
    for n, d in NODES.items():
        for r in parents(d):
            if n not in desc(r) and n not in CH[r]: CH[r].append(n)
    return {"charts": [{"title": c.get("title", ""), "nodes": {k: v for k, v in c.get("nodes", {}).items() if k in NODES},
                        "links": [l for l in c.get("links", []) if l[0] in NODES and l[1] in NODES]} for c in charts],
            "edges": {n: k for n, k in CH.items() if k}}

def parse_effects(raw):
    raw = strip_md(raw or "")
    if not raw or raw in ("-", "—"):
        return []
    return [a for a in (classify(cl) for cl in re.split(r"[;,]|\.\s+(?=[A-Z+\-])", raw)) if a]

def parse_mreq(s):
    s = strip_md(s or "")
    if not s or s in ("-", "—"):
        return []
    parts = [p.strip() for p in s.split("+")]
    groups = [[o.strip() for o in re.split(r"\bor\b|/", p, flags=re.I) if o.strip()] for p in parts]
    return [g for g in groups if g]

def classify_req_token(tok, names, settle_names):
    t = tok.strip()
    if re.match(r"^Craft\s+\d+$", t, re.I): return "threshold"
    if re.match(r"^\d+\s+.+$", t):          return "count"
    if t in names:                          return "pursuit"
    if t in settle_names:                   return "settlement"
    return "external"

# ---------- build records ----------
def build(ns):
    N = ns["NODES"]
    names = set(N.keys())
    settle_names = set(ns.get("SETTLEMENTS", {}).keys())
    records = {}
    natural_names = set()
    external = set()
    for name, v in N.items():
        innate = parse_effects(v.get("innate", ""))
        mastery = parse_effects(v.get("mastery", ""))
        if any(a.get("natural") for a in innate):
            natural_names.add(name)
        req_src = v.get("infrastructure_req", "") if ns.get("SIMPLE") else v.get("mastery_req", "")
        mreq = parse_mreq(req_src)
        for g in mreq:
            for opt in g:
                if classify_req_token(opt, names, settle_names) == "external":
                    external.add(opt)
        records[name] = {
            "name": name, "type": v.get("type", "?"), "group": (ns.get("HOLDING_GROUPS") or {}).get(v.get("group"), ""),
            "monument": bool(v.get("monument")),
            "root": bool(v.get("root")),
            "scope": v.get("scope") or ("Realm" if v.get("monument") else "Empire"),          # Root: no Mastery Chain check; efficient (if any) = optional Ward-sharing only
            # SIMPLE: upkeep / Build Timer by Standing (holding_cost); legacy leaves these out
            **(dict(zip(("upkeep", "build_time"), ns["holding_cost"](v))) if ns.get("SIMPLE") and ns.get("holding_cost") else {}),
            "innate_raw": strip_md(v.get("innate", "")),
            "mastery_raw": strip_md(v.get("mastery", "")),
            "mreq_raw": strip_md(req_src),
            "unlock_raw": strip_md(str(v.get("unlock", "") or "")),
            "combo": strip_md(v.get("innate", "")) if ns.get("SIMPLE") else combine_effects(v.get("innate", ""), v.get("mastery", "")),
            "combo_parts": combine_parts(v.get("innate", ""), v.get("mastery", "")),
            "builds_into": [b for b in (v.get("builds_into") or []) if b in N],
            "mastery_for": [m for m, mv in N.items() if m != name and name in re.split(r"\s*(?:\+|/|\bor\b)\s*", strip_md(str(mv.get("mastery_req") or "")))],
            "efficient": [strip_md(x) for x in (v.get("efficient") if isinstance(v.get("efficient"), (list, tuple)) else [v.get("efficient")]) if x and strip_md(x) not in ("-", "\u2014")],
            "innate": innate, "mastery": mastery, "mreq": mreq,
            "innate_fx": envoy_fx(v.get("innate", "")), "mastery_fx": envoy_fx(v.get("mastery", "")),
        }

    def infra_records(src, kind):
        out = {}
        for nm, d in src.items():
            up = d.get("upkeep", 0)
            try: up = int(up)
            except (TypeError, ValueError): up = 0
            out[nm] = {
                "name": nm, "kind": kind,
                "tier": d.get("tier", ""),
                "scope": d.get("scope") or ("Realm" if kind == "wonder" else "Empire"),
                "upkeep": up,
                "build_time": d.get("build_time", ""),
                "requirement": strip_md(d.get("requirement", "")),
                "effect_raw": strip_md(d.get("empire_bonus", "")),
                "fx": envoy_fx(d.get("empire_bonus", "")),
                "atoms": parse_effects(d.get("empire_bonus", "")),
            }
        return out

    _wondrous = {k: v for k, v in ns.get("INFRASTRUCTURE", {}).items() if v.get("tier") == "Wondrous"}   # Wonders = the Wondrous tier
    infra = infra_records({k: v for k, v in ns.get("INFRASTRUCTURE", {}).items() if k not in _wondrous}, "infra")
    wonders = infra_records(_wondrous or ns.get("WONDERS", {}), "wonder")
    retinues = ns.get("RETINUES", {})

    # ---- army source tokens: read from each Holding's text by the data file's shared parser ----
    # (renown_data.holding_combat_tags — the same parser the combat sim's HOLDING_SIM uses)
    htags = ns["holding_combat_tags"]
    REQ_ALIAS = {}                                                 # weapon "requires" tokens are Holding names
    army_src = {}
    for name, v in N.items():
        inn, mas = htags(v.get("innate", ""), sim=True), htags(v.get("mastery", ""), sim=True)
        if inn or mas:
            army_src[name] = {"innate": inn, "mastery": mas}

    glossary = {k: (strip_md(v)[:220]) for k, v in ns.get("GLOSSARY", {}).items()}
    for k, v in ns.get("MORALE_GLOSSARY", {}).items():
        glossary.setdefault(k, strip_md(v)[:220])
    _itd = ns.get("ITEM_TIER_DISPLAY", {}) or {}
    def _lab(src):   # per-item tier label (display only; the real tier still gates)
        return {k: (dict(v, tier_label=_itd[k]) if (k in _itd and isinstance(v, dict)) else v) for k, v in (src or {}).items()}
    equip = {"weapons": _lab(ns.get("WEAPONS", {})), "ranged": _lab(ns.get("RANGED", {})),
             "shields": _lab(ns.get("SHIELDS", {})), "armors": _lab(ns.get("ARMORS", {})),
             "retinues": retinues, "tiers": ns.get("TIERS", []),
             "endurance_regain": ns.get("ENDURANCE_REGAIN", 2),
             "army_max": ns.get("ARMY_MAX_RETINUES", 25), "reqAlias": REQ_ALIAS}
    return (records, sorted(natural_names), sorted(external), infra, wonders,
            army_src, equip, glossary)

# ---------- HTML ----------
MAPGEN_JS = ""

FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
# Latin + Latin-1/Ext-A, Greek (Σ), general punctuation, arrows, math (− ×), box/geometric shapes
_FONT_RANGES = [(0x20, 0x24F), (0x370, 0x3FF), (0x2000, 0x206F), (0x20A0, 0x20BF),
                (0x2100, 0x214F), (0x2190, 0x21FF), (0x2200, 0x22FF), (0x25A0, 0x25FF), (0x2600, 0x26FF)]

def font_faces():
    """@font-face rules with EB Garamond embedded (subset, woff) so the board stays
    self-contained/offline. Missing fonttools or font files -> empty string (falls back to Georgia)."""
    try:
        import base64, io
        from fontTools.subset import Subsetter, Options
        from fontTools.ttLib import TTFont
    except ImportError:
        print("  (fonttools not installed - board falls back to Georgia)"); return ""
    uni = [u for a, b in _FONT_RANGES for u in range(a, b + 1)]
    out = []
    for fname, family, style in (("EBGaramond-VariableFont_wght.ttf", "EB Garamond", "normal"),
                                 ("EBGaramond-Italic-VariableFont_wght.ttf", "EB Garamond", "italic")):
        path = os.path.join(FONT_DIR, fname)
        if not os.path.exists(path):
            print(f"  (font missing: {path} - falls back to Georgia)"); continue
        f = TTFont(path)
        opt = Options(); opt.flavor = "woff"; opt.layout_features = ["*"]
        sub = Subsetter(opt); sub.populate(unicodes=uni); sub.subset(f)
        f.flavor = "woff"; buf = io.BytesIO(); f.save(buf)
        b64 = base64.b64encode(buf.getvalue()).decode("ascii")
        out.append("@font-face{font-family:'%s';font-style:%s;font-weight:400 800;"
                   "font-display:swap;src:url(data:font/woff;base64,%s) format('woff');}" % (family, style, b64))
    return "\n".join(out)

def _pursuit_term_template(tpl, term):
    """SIMPLE: board UI words Pursuit/Pursuits -> the display term. BUILD_TIMERS keys used as ids are kept."""
    keep = ['BTM["Power Pursuit"]', 'BTM["Monument Pursuit"]', "BTM.Pursuit"]
    for i, k in enumerate(keep): tpl = tpl.replace(k, f"\x00KEEP{i}\x00")
    tpl = re.sub(r"\bPursuits\b", term[1], tpl); tpl = re.sub(r"\bPursuit\b", term[0], tpl)
    for i, k in enumerate(keep): tpl = tpl.replace(f"\x00KEEP{i}\x00", k)
    return tpl

def render_html(**data):
    blob = json.dumps(data, ensure_ascii=False)
    tpl = HTML_TEMPLATE
    if data.get("simple") and data.get("pursuitTerm"):
        tpl = _pursuit_term_template(tpl, data["pursuitTerm"])
    return (tpl.replace("/*__FONTS__*/", font_faces())
            .replace("/*__MAPGEN__*/", MAPGEN_JS).replace("/*__DATA__*/", blob))

def _style_js(d):
    """hexstyle.py (CE/mapgen) -> `var RenownStyle=...;` - glyphs + climate palettes,
    the same source the map app and print boards use. '' if absent (board falls back)."""
    p = os.path.join(d, "hexstyle.py")
    if not os.path.isfile(p):
        print("  (hexstyle.py not found - map uses fallback colours, no glyphs)"); return ""
    import importlib.util
    spec = importlib.util.spec_from_file_location("hexstyle", p)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return "var RenownStyle=" + json.dumps(mod.export(), separators=(",", ":")) + ";"

def place_names_payload(data_path):
    """PLACE_NAMES from worldbuilding/renown_worldlore.py (beside the data file) -> {banks, exclude}; None if absent."""
    here = os.path.dirname(os.path.abspath(__file__))
    for d in (os.path.dirname(os.path.abspath(data_path)), os.path.join(here, ".."), here):
        p = os.path.join(d, "worldbuilding", "renown_worldlore.py")
        if not os.path.isfile(p): continue
        import importlib.util
        spec = importlib.util.spec_from_file_location("renown_worldlore_pn", p)
        m = importlib.util.module_from_spec(spec)
        try: spec.loader.exec_module(m)
        except Exception as e:
            print(f"  (place names: {p} failed to load: {e})"); return None
        banks = getattr(m, "PLACE_NAMES", None)
        if not banks: return None
        ex = list(getattr(m, "PLACE_NAMES_EXCLUDE", [])) + list((getattr(m, "MAP", {}) or {}).get("regional_lore", {}))
        print(f"  place names: {p} ({len(banks)} cultures, chronicle {len(getattr(m, 'CHRONICLE', {}) or {})} events)")
        her = {c: (v.get("heraldry") or {}).get("primary") for c, v in (getattr(m, "CULTURES", {}) or {}).items() if (v.get("heraldry") or {}).get("primary")}
        return {"banks": banks, "exclude": ex, "chronicle": getattr(m, "CHRONICLE", None), "heraldry": her}
    return None

def sprite_payload(ns, data_path):
    """sprites.py (next to the data file) -> {S: sprites, P: scene palette, key: name -> sprite key}.
    None if absent (then there is no settlement scene)."""
    here = os.path.dirname(os.path.abspath(__file__))
    for d in (os.path.dirname(os.path.abspath(data_path)), os.path.join(here, ".."), here):
        p = os.path.join(d, "sprites.py")
        if not os.path.isfile(p): continue
        import importlib.util
        spec = importlib.util.spec_from_file_location("renown_sprites", p)
        mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        for w in mod.check(ns): print("  WARN sprites: " + w)
        names = set(ns.get("NODES", {})) | set(ns.get("WONDERS", {})) | set(ns.get("SETTLEMENTS", {})) | set(ns.get("INFRASTRUCTURE", {}))
        keymap = {n: k for n in sorted(names) for k in [mod.sprite_key(n, ns)] if k in mod.SPRITES}
        print(f"  sprites: {os.path.normpath(p)} ({len(mod.SPRITES)} sprites, {len(keymap)} names mapped)")
        raw = sorted(n for n, v in ns.get("NODES", {}).items() if v.get("type") == "Raw Materials")
        return {"scatter": dict(getattr(mod, "SCATTER", {})), "S": mod.SPRITES, "P": mod.PALETTES.get("scene", {}), "key": keymap, "v": getattr(mod, "SPRITE_VERSION", "?"),
                "raw": raw, "skyline": {k: list(v) for k, v in getattr(mod, "SKYLINE", {}).items()},
                "supersedes": dict(getattr(mod, "INFRA_SUPERSEDES", {})), "noInfra": list(getattr(mod, "PLATE_NO_INFRA", [])),
                "style": dict(getattr(mod, "SCENE_STYLE", {})), "eqTile": getattr(mod, "EQ_TILE", "#3a404c")}
    print("  (sprites.py not found - no settlement scene)")
    return None

def find_mapgen(explicit, data_path):
    """Locate gen.js + presets.js (+ hexstyle.py) in CE/mapgen. Returns the JS or ''."""
    here = os.path.dirname(os.path.abspath(__file__))
    cands = [explicit] if explicit else []
    cands += [os.path.join(os.path.dirname(os.path.abspath(data_path)), "mapgen"),
              os.path.join(here, "..", "mapgen"), os.path.join(here, "mapgen"), here]
    for d in cands:
        if d and os.path.isfile(os.path.join(d, "gen.js")) and os.path.isfile(os.path.join(d, "presets.js")):
            js = open(os.path.join(d, "gen.js"), encoding="utf-8").read() + "\n" + \
                 open(os.path.join(d, "presets.js"), encoding="utf-8").read() + "\n" + _style_js(d)
            return js.replace("</script", "<\\/script"), os.path.normpath(d)
    return "", None

BOARD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "board")

def _board_template():
    """The page: board/board.css + board/body.html + board/js/*.js (sorted by name, one <script>).
    Edit those files; this only concatenates them (the output stays one self-contained HTML file)."""
    rd = lambda *p: open(os.path.join(BOARD_DIR, *p), encoding="utf-8").read()
    js = "".join(rd("js", f) for f in sorted(os.listdir(os.path.join(BOARD_DIR, "js")))
                 if f.endswith(".js") and not f.startswith("parity_"))
    return ('<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            '<title>Renown — Settlement Board Emulator</title>\n<style>\n/*__FONTS__*/\n' + rd("board.css") +
            '</style>\n</head>\n<body>\n' + rd("body.html") +
            '<script>/*__MAPGEN__*/</script>\n<script>\n' + js + '</script>\n</body>\n</html>\n')

HTML_TEMPLATE = _board_template()

def check_rules(ns, rules_path):
    """Cross-check a few key constants in the rules doc against the data file / tool logic.
    Prints a report; returns the number of hard MISMATCHes."""
    if not os.path.exists(rules_path):
        print(f"rules file not found: {rules_path}"); return 0
    txt = open(rules_path, encoding="utf-8").read().replace("\u2212", "-")   # normalise unicode minus
    WORD = {"one":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7,"eight":8,"nine":9,"ten":10}
    rows = []   # (name, data/tool value, rules value, status)
    def add(name, dv, rv, path=None):
        if path and ("{{VAL:" + path + "}}") in txt: rv = "templated"     # rules read the value from data
        if rv is None: status = "NOT IN RULES"
        elif rv == "templated": status = "templated (auto-synced)"; rv = "{{VAL}}"
        else: status = "MATCH" if str(dv) == str(rv) else "MISMATCH"
        rows.append((name, dv, rv if rv is not None else "—", status))

    def find(pat, cast=int, group=1):
        m = re.search(pat, txt, re.I)
        if not m: return None
        try: return cast(m.group(group))
        except Exception: return m.group(group)

    # PO cap
    m = re.search(r"capped between\s*(-?\d+)\s*and\s*(\d+)", txt, re.I)
    po = ns.get("PUBLIC_ORDER", {})
    keys = [int(k) for k in po] if po else []
    add("PO min", min(keys) if keys else "?", int(m.group(1)) if m else None, "PO_MIN")
    add("PO max", max(keys) if keys else "?", int(m.group(2)) if m else None, "PO_MAX")

    # Endurance regain per turn
    add("Endurance regain / turn", ns.get("ENDURANCE_REGAIN", "?"),
        find(r"gains?\s*\+(\d+)\s*Endurance"), "ENDURANCE_REGAIN")

    # Army max retinues (templated in rules)
    add("Army max Retinues", ns.get("ARMY_MAX_RETINUES", "?"),
        "templated" if "{{VAL:ARMY_MAX_RETINUES}}" in txt else find(r"camp reaches\s*(\d+)"))

    # Trade income per Craft (templated in rules)
    add("Trade income / Craft", ns.get("TRADE_RULES", {}).get("income_per_craft", "?"),
        "templated" if "{{VAL:TRADE_RULES.income_per_craft}}" in txt else None)

    # Domain standing thresholds (tool logic vs rules words three/six/ten)
    r_rising = find(r"reaches\s*\*?([a-z]+)\*?,?\s*you become Rising", cast=lambda w: WORD.get(w.lower()))
    r_est    = find(r"\*?([a-z]+)\*?\s*\(Established\)", cast=lambda w: WORD.get(w.lower()))
    r_sov    = find(r"\*?([a-z]+)\*?\s*\(Sovereign\)", cast=lambda w: WORD.get(w.lower()))
    _stt = ns.get("STANDING_THRESHOLDS", {})
    add("Standing: Rising at",      _stt.get("Rising", 3),       r_rising, "STANDING_THRESHOLDS.Rising")
    add("Standing: Established at", _stt.get("Established", 6),  r_est,    "STANDING_THRESHOLDS.Established")
    add("Standing: Sovereign at",   _stt.get("Sovereign", 10),   r_sov,    "STANDING_THRESHOLDS.Sovereign")

    # Influence by standing (data DOMAIN_BOARD.max_influence_per_vote vs rules)
    mip = ns.get("DOMAIN_BOARD", {}).get("max_influence_per_vote", {})
    m = re.search(r"Untested\s*(\d+),?\s*Rising\s*(\d+),?\s*Established\s*(\d+),?\s*Sovereign\s*(\d+)", txt, re.I)
    for i, st in enumerate(["Untested", "Rising", "Established", "Sovereign"]):
        add(f"Influence cap: {st}", mip.get(st, "?"), int(m.group(i+1)) if m else None, f"DOMAIN_BOARD.max_influence_per_vote.{st}")
        if not m and "{{VAL:STANDING_RANK." + st in txt and rows[-1][3] == "NOT IN RULES": rows[-1] = rows[-1][:2] + ("{{VAL}}", "templated (auto-synced)")   # rules print STANDING_RANK (= this row)

    # Era thresholds (data ERAS vs rules — not present in doc)
    for e, x in ns.get("ERAS", {}).items():
        present = re.search(r"\b"+re.escape(e)+r"\b", txt)
        add(f"Era {e} @ Renown", x.get("renown", "?"), None if ("{{TABLE:eras}}" in txt) else (find(r"\b"+re.escape(e)+r"\b.*?(\d+)") if present else None), f"ERAS.{e}.renown")
        if "{{TABLE:eras}}" in txt and rows[-1][3] == "NOT IN RULES": rows[-1] = rows[-1][:2] + ("{{TABLE}}", "templated (auto-synced)")

    # Tool combat logic vs rules (known drift point)
    add("Fatigue: Morale penalty / token", ns.get("FATIGUE_MORALE", 2), find(r"each token is\s*-(\d+)\s*to that Army"), "FATIGUE_MORALE")
    add("Fatigue: rout at modified Morale", ns.get("ROUT_THR", 11), find(r"modified to\s*(\d+)\s*or more Routs"), "ROUT_THR")

    # Dice system: data is d10, doc may still say D6
    data_d10 = ("d10" in str(ns.get("DICE_PROVENANCE","")).lower()) or (ns.get("BANDIT_FACES")==10)
    if data_d10 and re.search(r"\bD6\b", txt):
        rows.append(("Combat die", "d10", "D6", "MISMATCH"))

    # Placeholder integrity: every {{VAL:path}} must resolve; {{TABLE:name}} should have a data table
    def resolve(path):
        cur = ns
        for seg in path.split('.'):
            if isinstance(cur, dict) and seg in cur: cur = cur[seg]
            else: return False
        return True
    def tbl_ok(name):
        up = name.upper().replace(' ', '_')
        return any(k.upper() == up or up in k.upper() for k in ns)
    reg = None
    try:
        import importlib
        sys.path.insert(0, os.path.dirname(os.path.abspath(rules_path)) or ".")
        reg = set(importlib.import_module("docx_tables").REGISTRY.keys())
    except Exception:
        reg = None
    print("  (TABLE check via " + ("docx_tables.REGISTRY" if reg is not None else "name heuristic — docx_tables not importable") + ")")
    def table_present(name):
        return (name in reg) if reg is not None else tbl_ok(name)
    ph = re.findall(r"\{\{(VAL|TABLE):([^}]+)\}\}", txt)
    for p in sorted({x for k, x in ph if k == "VAL" and not resolve(x)}):
        rows.append(("VAL " + p, "—", "unresolved", "MISMATCH"))
    for p in sorted({x for k, x in ph if k == "TABLE" and not table_present(x)}):
        rows.append(("TABLE " + p, "—", "no builder", "MISMATCH"))
    cats = {str(t) for t, _ in ns.get("GLOSSARY_CATEGORIES", [])}
    for p in sorted(set(re.findall(r"\{\{GLOSSARY:([^}]+)\}\}", txt))):
        if p.strip() not in cats: rows.append(("GLOSSARY " + p, "—", "no category", "MISMATCH"))
    gk = {str(k).lower() for k in ns.get("GLOSSARY", {})}
    for p in sorted(set(re.findall(r"\{\{TERM:([^}]+)\}\}", txt))):
        if p.strip().lower() not in gk: rows.append(("TERM " + p, "—", "not in GLOSSARY", "MISMATCH"))
    # rule anchors: duplicate {{RULE:}} ids, unresolved {{SEE:}} ids and GLOSSARY_SEE anchors (rule_numbers.py)
    try:
        here = os.path.dirname(os.path.abspath(__file__))
        if here not in sys.path: sys.path.insert(0, here)
        import rule_numbers as _rn
        for p in _rn.check(rules_path):
            rows.append(("anchor " + p, "—", "—", "MISMATCH"))
    except Exception as e:
        rows.append(("rule anchors", "—", f"check failed: {e}", "MISMATCH"))
    # board plumbing: phase rule sections the board reads by heading
    for h in ("Empire Phase", "Council Phase", "Envoy Phase", "Battle Phase", "Rest Phase",
              "The Skirmish Steps", "Beginning a Battle", "Ending a Battle"):
        if not re.search(r"^#+\s*" + re.escape(h) + r"\s*$", txt, re.M):
            rows.append(("heading '" + h + "'", "board reads", "missing", "MISMATCH"))

    w = max(len(r[0]) for r in rows)
    print(f"\nRules cross-check  ({rules_path})")
    print(f"{'constant'.ljust(w)}  {'data/tool':>10}  {'rules':>10}  status")
    print("-"*(w+34))
    mism = 0
    for name, dv, rv, st in rows:
        if st == "MISMATCH": mism += 1
        print(f"{name.ljust(w)}  {str(dv):>10}  {str(rv):>10}  {st}")
    print(f"\n{mism} mismatch(es). (NOT IN RULES / templated are informational, not failures.)")
    return mism

def _val(ns, path):
    cur = ns
    for part in path.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return None
    return cur

def rules_section(rules_path, heading, ns):
    """Return the markdown body under an exact '### heading' line, {{VAL:x}} resolved from data."""
    if not rules_path or not os.path.exists(rules_path):
        return ""
    lines = open(rules_path, encoding="utf-8").read().splitlines()
    out, on = [], False
    for ln in lines:
        if ln.strip().lstrip("#").strip() == heading and ln.lstrip().startswith("#"):
            on = True; continue
        if on and ln.lstrip().startswith("#"):
            break
        if on:
            out.append(ln)
    txt = re.sub(r"\s*\{\{RULE:[^}]*\}\}", "", "\n".join(out)).strip()   # rule anchors are print/wiki plumbing
    def sub(m):
        v = _val(ns, m.group(1).strip())
        return str(v) if v is not None else m.group(0)
    return re.sub(r"\{\{VAL:([^}]+)\}\}", sub, txt)

def phase_steps(body):
    """Top-level list items of a phase's rules section -> [[label, line]]; label = bold lead, else the line itself."""
    out = []
    for ln in (body or "").splitlines():
        sub = re.match(r"^[ \t]+(?:\d+\.\d+[a-z]?|[-*])\s+(.*)$", ln)   # nested step (3.1 …): folded into its parent's tip
        if sub and out:
            out[-1][1] += " \u00b7 " + re.sub(r"\*\*|\*", "", sub.group(1).strip()); continue
        m = re.match(r"^(?:\d+\.|[-*])\s+(.*)$", ln)          # top level only (nested items are indented)
        if not m: continue
        line = m.group(1).strip()
        b = re.match(r"^\*\*(.+?)\*\*", line)
        plain = re.sub(r"\*\*|\*", "", line)
        label = b.group(1) if b else re.split(r";|\.\s|\.$| \u2014 |\(", plain)[0]
        label = label.rstrip(":").strip()
        out.append([label, plain])
    return out

def battle_data(ns, rules_path):
    M = ns.get("TACTIC_MATRIX", {})
    return {
        "tactics": list(ns.get("TACTICS", [])),
        "matrix": [[a, b, ma, mb] for (a, b), (ma, mb) in M.items()],
        "frontMax": ns.get("FRONT_LINE_MAX"), "reserveMax": ns.get("RESERVE_MAX"),
        "moraleDiceMax": ns.get("MORALE_DICE_MAX"), "parryBase": ns.get("PARRY_BASE"),
        "unstoppableMod": ns.get("UNSTOPPABLE_MOD", 2), "improvedParryMod": ns.get("IMPROVED_PARRY_MOD", 1),
        "recoverBase": ns.get("RECOVER_BASE"),
        "serratedMod": ns["SERRATED_MOD"] if "SERRATED_MOD" in ns else (lambda m: int(m.group(1)) if m else 2)(re.search(r"-(\d+) penalty to the defender's Recover", str(ns.get("GLOSSARY", {}).get(ns.get("SERRATED", "Serrated"), "")))),
        "standingFx": {f"{d}|{t}": v for (d, t), v in ns.get("STANDING_EFFECTS", {}).items()},
        "tacticNotes": dict(ns.get("TACTIC_NOTES", {}) or {}),
        "panicThreshold": ns.get("PANIC_CASUALTY_THRESHOLD"), "fatigueMorale": ns.get("FATIGUE_MORALE"),
        "fatigueStrike": ns.get("FATIGUE_STRIKE"), "capThr": ns.get("CAP_THR"), "routThr": ns.get("ROUT_THR"),
        "faces": ns.get("FACES"), "focusedThr": ns.get("FOCUSED_THR"), "deadlyAp": ns.get("DEADLY_AP"),
        "tacticalGlobal": list(ns.get("TACTICAL_GLOBAL", [])),
        "steps": rules_section(rules_path, "The Skirmish Steps", ns),
        "seize": rules_section(rules_path, "Beginning a Battle", ns),
        "resolve": rules_section(rules_path, "Ending a Battle", ns),
    }

def bandit_loadouts(ns, equip):
    """Map BANDIT_EQUIPMENT_PER_ERA prose onto equipment names. Exact name match only
    (a trailing plural 's' is dropped); anything unmatched is reported, not guessed."""
    cats = {"weapon": equip.get("weapons", {}), "armor": equip.get("armors", {}),
            "shield": {k: v for k, v in equip.get("shields", {}).items() if k != "null"}}
    rets = equip.get("retinues", {}) or {}
    out, warns = {}, []
    for era, txt in (ns.get("BANDIT_EQUIPMENT_PER_ERA") or {}).items():
        lo = {"weapon": "Farm Tools", "armor": "Cloth", "shield": "None", "retinue": None, "unmatched": []}
        found = {"weapon": False, "armor": False, "shield": False}
        txt = str(txt)
        # optional "Retinue: gear…" prefix (e.g. "Man-at-Arms: Halberd + Chainmail")
        m = re.match(r"\s*([^:]+?)\s*:\s*(.*)$", txt)
        if m:
            if m.group(1) in rets:
                lo["retinue"] = m.group(1); txt = m.group(2)
            else:
                warns.append(f"BANDIT_EQUIPMENT_PER_ERA[{era}]: retinue '{m.group(1)}' matches no RETINUES entry")
                txt = m.group(2)
        for tok in re.split(r"\s*(?:,|\+|&)\s*", txt):
            tok = tok.strip()
            if not tok:
                continue
            cands = [tok, tok[:-1] if tok.endswith("s") else tok]
            cands += [c.replace(" Armor", "").replace(" Shields", " Shield") for c in list(cands)]
            hit = None
            for cat, items in cats.items():
                for c in cands:
                    if c in items:
                        hit = (cat, c); break
                if hit:
                    break
            if hit:
                lo[hit[0]] = hit[1]; found[hit[0]] = True
            else:
                lo["unmatched"].append(tok)
                warns.append(f"BANDIT_EQUIPMENT_PER_ERA[{era}]: '{tok}' matches no equipment name")
        out[era] = lo
    return out, warns

# Rule constants passed through to the board as DATA.rulesConst (plumbing for mechanics the board
# shows or flags; anything the board hard-codes should read from here instead).
RULES_CONSTS = ("PHASES", "MARCH_MULTIPLIER", "MUSTER_RANGE", "CHARTER_MIN_RANGE", "HAMLET_RANGE",
                "OUTLAW_BUFFER_RANGE", "SACK_EXTORT_PER_TIER", "INTERCEPT_EXTORT_PER_CRAFT", "WEALTH_EDICT_GOLD", "EDICT_UNIQUE", "CUNNING_EXTORT", "GAME_TURN_LIMIT", "VASSAL_EXCHANGE_CAP",
                "BLUNDER_THR", "STANDING_ARMY_SIEGE_MODIFIER", "BANDIT_BEHAVIOR", "UPKEEP_TRACKS",
                "GLOSSARY_CATEGORIES", "STARTING_TREASURY", "EMPIRE_START_TIERS", "TERM_ENVOY_SCORE", "RENOWN_MAX",
                "CAPITAL_EDGE_RANGE", "AGE_YEAR_SEASON",
                "PRESENCE_RANGE", "FAITH_FICKLE_PO", "WARD_MODEL", "SETUP_HAMLET_HOLDINGS",
                "SETUP_CAPITAL_PICKS", "SETUP_HAMLET_PICKS", "HAMLET_REPEATABLE", "AGE_YEAR_ROLL_MEAN", "AGE_YEAR_ROLL_SD",
                "AI_DOMAIN_POINTS", "AI_PRIORITIES", "AI_FAITH_AVOID", "AI_DIPLOMACY", "AI_PROFILES",
                "AI_STYLE", "AI_MUSTER", "AI_ARCHETYPE", "AI_PO_GOLD")

def effects_report(ns, records, infra, wonders, out_md):
    """ENVOY_WINDOW_REVIEW.md: every clause that names Envoys, its timing window and Personal / Council predicate
    (from effect_registry.window_of), so wording can change freely and the board follows the text."""
    import effect_registry as ER
    rows = ER.envoy_window_review(ns, records, infra, wonders, strip_md)
    efx = ER.build_efx(ns, records, infra, wonders, strip_md)
    esc = lambda t: str(t).replace("|", "\\|")
    flag = [r for r in rows if r["issue"].startswith("names a Phase")]
    both = [r for r in rows if r["issue"].startswith("no window")]
    L = ["# Envoy timing windows — review list", "",
         "Generated by `gen_settlement_board.py --effects-report` from `effect_registry.window_of` (re-run after any wording change).", "",
         "An Envoy clause with no **Personal** / **Council** predicate covers both kinds: Council Envoys resolve in the Council Phase,",
         "Personal Envoys in the Envoy Phase. A clause limited to one Phase (\"Once per Envoy Phase\") without a predicate therefore",
         "can't reach the other Phase's Envoys: it is read as that Phase's Envoys (Envoy Phase = Personal, Council Phase = Council), shown as",
         "\"(by Phase)\" in the Predicate column. The board reads the window from the text, so changing the wording changes the board.", "",
         "## To review: limited to one Phase, no Personal / Council predicate (%d)" % len(flag), "",
         "| Piece | Kind | Clause | Window | Limit |", "|---|---|---|---|---|"]
    L += ["| %s | %s | %s | %s | %s |" % (esc(r["name"]), r["kind"], esc(r["clause"]), r["window"], r["limit"]) for r in flag]
    L += ["", "## No window, no predicate: applies to Council and Personal Envoys alike (%d)" % len(both), "",
          "| Piece | Kind | Clause |", "|---|---|---|"]
    L += ["| %s | %s | %s |" % (esc(r["name"]), r["kind"], esc(r["clause"])) for r in both]
    L += ["", "## Every Envoy clause (%d)" % len(rows), "", "| Piece | Kind | Clause | Window | Limit | Predicate |", "|---|---|---|---|---|---|"]
    L += ["| %s | %s | %s | %s | %s | %s |" % (esc(r["name"]), r["kind"], esc(r["clause"]), r["window"], r["limit"], r["scope"]) for r in rows]
    hit = {k: sorted(x for x in e if not x.startswith("_")) for k, e in efx.items()}
    used = sorted({i for v in hit.values() for i in v})
    L += ["", "## Registry coverage", "", "%d of %d registry patterns match at least one piece." % (len(used), len(ER.REG)), ""]
    dead = [k for k in ER.REG if k not in used]
    if dead: L += ["Patterns with no match in the current data (wording changed, or the piece is gone): " + ", ".join("`%s`" % k for k in dead), ""]
    with open(out_md, "w", encoding="utf-8") as fh: fh.write("\n".join(L) + "\n")
    print(f"wrote {out_md}  ({len(flag)} to review, {len(both)} both-Phase, {len(rows)} Envoy clauses, {len(used)}/{len(ER.REG)} patterns used)")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="renown_data_d10.py")
    ap.add_argument("--out", default="settlement_board.html")
    ap.add_argument("--rules", default="RULES_reorganized_6.md")
    ap.add_argument("--wiki-base", default="", help="URL/prefix of the rules wiki for hover links; overrides both defaults below")
    ap.add_argument("--wiki-home", default="https://mlang95.github.io/RenownWiki/",
                    help="hosted wiki used when the board is NOT the wiki's own copy (server.py, local file)")
    ap.add_argument("--mapgen", default="", help="folder with gen.js + presets.js (default: <data dir>/mapgen or ../mapgen)")
    ap.add_argument("--check-rules", action="store_true",
                    help="cross-check key constants in the rules doc against the data file, then exit")
    ap.add_argument("--effects-report", default="", metavar="MD",
                    help="write the effect-registry report (Envoy timing windows to review + unmatched clauses) to MD, then exit")
    a = ap.parse_args()
    if not os.path.exists(a.data):
        sys.exit(f"data file not found: {a.data}")
    ns = load(a.data)
    if a.check_rules:
        sys.exit(1 if check_rules(ns, a.rules) else 0)
    (records, natural, external, infra, wonders,
     army_src, equip, glossary) = build(ns)
    import effect_registry as ER
    if a.effects_report:
        effects_report(ns, records, infra, wonders, a.effects_report)
        return
    efx = ER.build_efx(ns, records, infra, wonders, strip_md)
    pn_payload = place_names_payload(a.data)
    _spr = sprite_payload(ns, a.data)
    for c, an in ((pn_payload or {}).get("heraldry") or {}).items():
        if _spr and "her:" + an not in _spr["S"]: print(f"  WARN heraldry: no sprite her:{an} for culture {c}")
    po = {str(k): v for k, v in ns.get("PUBLIC_ORDER", {}).items()}
    b_lo, b_warn = bandit_loadouts(ns, equip)
    for w in b_warn:
        print("  WARN " + w)
    global MAPGEN_JS
    MAPGEN_JS, mg_dir = find_mapgen(a.mapgen, a.data)
    print(f"  map generator: {mg_dir}" if mg_dir else "  (gen.js/presets.js not found - map import limited to JSON)")
    rules_path = a.rules if os.path.exists(a.rules) else os.path.join(os.path.dirname(os.path.abspath(a.data)), os.path.basename(a.rules))
    if not os.path.exists(rules_path):
        print(f"  (rules file not found: {a.rules} - battle rules panel will be empty)")
    html = render_html(
        records=records, naturalNames=natural, externalTokens=external, simple=bool(ns.get("SIMPLE")),
        chainTerm=ns.get("CHAIN_TERM", "Efficient"), pursuitTerm=list(ns.get("PURSUIT_TERM", ("Pursuit", "Pursuits"))),
        infra=infra, wonders=wonders, armySrc=army_src, equip=equip, glossary=glossary,
        domainBoard=ns.get("DOMAIN_BOARD", {}), publicOrder=po,
        domainBoardFx={d: {t: envoy_fx(x) for t, x in v.items() if isinstance(x, str) and envoy_fx(x)}
                       for d, v in ns.get("DOMAIN_BOARD", {}).items() if isinstance(v, dict)},
        poByEra={e: {str(k): v for k, v in t.items()} for e, t in ns.get("PUBLIC_ORDER_BY_ERA", {}).items()}, wikiBase=a.wiki_base, wikiHome=a.wiki_home,
        tree=tree_payload(ns, os.path.dirname(os.path.abspath(__file__))),
        rulebook=rules_payload(ns, rules_path if os.path.exists(rules_path) else None),
        limits={"poMin": ns.get("PO_MIN", -5), "poMax": ns.get("PO_MAX", 10),
                "initMin": ns.get("INITIATIVE_MIN", -2), "initMax": ns.get("INITIATIVE_MAX", 2),
                "standing": ns.get("STANDING_THRESHOLDS", {"Untested": 1, "Rising": 3, "Established": 6, "Sovereign": 10})},
        eras=ns.get("ERAS", {}), edicts=ns.get("EDICTS", {}),
        envoyOutcomes=ns.get("ENVOY_OUTCOMES", {}), outcomeThresh=ns.get("ENVOY_OUTCOME_THRESHOLDS", {}),
        startPhase=ns.get("STARTING_TURN_PHASE_OPENER", "Council"),
        actions={k: {"domain": v.get("domain", ""), "cost": v.get("cost", ""), "endorsed": v.get("endorsed", ""),
                     "requires": v.get("requires", ""), "effect": v.get("effect", ""), "notes": list(v.get("notes", []) or [])}
                 for k, v in ns.get("ACTIONS", {}).items()},
        phaseRules={k: rules_section(rules_path, h, ns) for k, h in
                    (("empire", "Empire Phase"), ("council", "Council Phase"), ("envoy", "Envoy Phase"),
                     ("battle", "Battle Phase"), ("rest", "Rest Phase"))},
        phaseSteps={k: phase_steps(rules_section(rules_path, h, ns)) for k, h in
                    (("empire", "Empire Phase"), ("council", "Council Phase"), ("envoy", "Envoy Phase"),
                     ("battle", "Battle Phase"), ("rest", "Rest Phase"))},
        rulesConst={k: ns.get(k) for k in RULES_CONSTS if k in ns},
        ages=[{"name": n, "rising": a.get("rising"), "years": list(a.get("years", (0, 0)))}
              for n, a in ns.get("AGES", {}).items()],
        domains=["Industry", "Prowess", "Cunning", "Piety"],
        standings=["Rising", "Established", "Sovereign"],
        tradePerCraft=ns.get("TRADE_RULES", {}).get("income_per_craft", 100),
        noTradeSeason=ns.get("TRADE_RULES", {}).get("no_trade_season", ""),
        tradeBorder=bool(ns.get("TRADE_RULES", {}).get("requires_border", False)),
        renownPerTurn=ns.get("RENOWN_PER_TURN", 1), dpPerTurn=ns.get("DOMAIN_POINTS_PER_TURN", 1),
        settlements=ns.get("SETTLEMENTS", {}),
        battle=battle_data(ns, rules_path),
        terrainRef={"terrain": ns.get("TERRAIN", {}), "movement": ns.get("MOVEMENT_MODIFIERS", {}),
                    "tactical": ns.get("TACTICAL_TERRAIN", {}), "tacticalGlobal": list(ns.get("TACTICAL_GLOBAL", []))},
        banditLoadouts=b_lo,
        bandits={
            "campStart": ns.get("BANDIT_CAMP_START"), "campGold": ns.get("BANDIT_CAMP_GOLD", 0), "armyThreshold": ns.get("BANDIT_ARMY_THRESHOLD"),
            "growth": ns.get("BANDIT_GROWTH_PER_ERA", {}), "equipment": ns.get("BANDIT_EQUIPMENT_PER_ERA", {}),
            "cunningMin": ns.get("BANDIT_CUNNING_MIN"), "faces": ns.get("BANDIT_FACES"),
            "outlawStart": ns.get("OUTLAW_COUNTRY_START"), "outlawBuffer": ns.get("OUTLAW_BUFFER_RANGE"),
            "wild": ns.get("WILD_OUTLAW", {}), "campReach": ns.get("BANDIT_CAMP_REACH"),
            "cunningTable": [list(x) for x in ns["die_table_ranges"](ns["BANDIT_CUNNING_TABLE"])] if "die_table_ranges" in ns and "BANDIT_CUNNING_TABLE" in ns else [],
            "tacticTable": [list(x) for x in ns["die_table_ranges"](ns["BANDIT_TACTIC_TABLE"])] if "die_table_ranges" in ns and "BANDIT_TACTIC_TABLE" in ns else [],
            "outcomeThresh": ns.get("ENVOY_OUTCOME_THRESHOLDS", {}),
            "cunningOutcomes": ns.get("ENVOY_OUTCOMES", {}).get("Cunning", {}),
            "cunningActions": {k: {"effect": v.get("effect", ""), "endorsed": v.get("endorsed", ""), "cost": v.get("cost", "")}
                               for k, v in ns.get("ACTIONS", {}).items() if v.get("domain") == "Cunning"},
        },
        treaties=ns.get("TREATIES", {}), allianceRules=list(ns.get("ALLIANCE_RULES", [])),
        startTiers=list(ns.get("EMPIRE_START_TIERS", ())), startTreasury=ns.get("STARTING_TREASURY", 0),
        pursuitUpkeep={"byType": ns.get("PURSUIT_UPKEEP_BY_TYPE", {}), "def": ns.get("PURSUIT_UPKEEP_DEFAULT", 0)},
        buildTimers=ns.get("BUILD_TIMERS", {}), infraTiers=list(ns.get("INFRA_TIERS", [])), timers=ns.get("TIMERS", {}), seasons=ns.get("SEASONS", {}),
        poModifiers=ns.get("PO_MODIFIERS", {}), vassalInfluenceTake=ns.get("VASSAL_INFLUENCE_TAKE", 0),
        aliases=ns.get("ALIASES", {}) or {}, scoreTerm=ns.get("TERM_ENVOY_SCORE", "Influence"), costs=ns.get("COSTS", {}), influenceGain=ns.get("INFLUENCE_GAIN", {}),
        siege={"calculus": ns.get("SIEGE_CALCULUS", {}), "sources": ns.get("SIEGE_SOURCE_VALUES", {})},
        factions={k: {"final": bool(v.get("final_cut")), "difficulty": v.get("difficulty", ""), "strength": v.get("strength", ""),
                      "feel": v.get("feel", ""), "mechanic": v.get("mechanic", ""), "pair": v.get("pair", ""), "complement": v.get("complement", ""),
                      "fx": envoy_fx(v.get("mechanic", "")), "body": ns["faction_body"](k) if "faction_body" in ns else v.get("mechanic", ""),
                      "mname": v.get("mechanic_name", ""), "summary": v.get("summary", "")}
                  for k, v in ns.get("FACTIONS", {}).items()},
        cultures={k: {"type": v.get("type", ""), "domains": list(v.get("domains", [])), "archetype": v.get("archetype", ""), "monuments": list(v.get("monuments", [])),
                      "wonders": list(v.get("wonders", [])), "mechanics": list(v.get("mechanic_name", [])),
                      "factions": list(v.get("factions", []))} for k, v in ns.get("CULTURES", {}).items()},
        cultureSelf=ns.get("CULTURE_SELF_MADE", "Self-made"), placeNames=pn_payload,
        warnings=b_warn, version=ns.get("VERSION", "?"), sprites=_spr, efx=efx,
    )
    with open(a.out, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"wrote {a.out}  ({len(records)} pursuits, {len(infra)} infra, "
          f"{len(wonders)} wonders, {len(army_src)} army-tag nodes)")

if __name__ == "__main__":
    main()
