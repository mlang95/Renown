"""effect_registry.py -- every rules-text pattern the settlement board acts on, matched once at build time.

The board used to re-split and regex every active piece's text at runtime (srcMatch / srcHas and a few dozen
direct regexes). Here each pattern has an id; `build_efx` runs them over every piece's text and ships the hits
in DATA.efx, so the board reads fields (JS `srcMatch(board, "id")`) instead of text.

Sources (the same text the board used to read; keys in DATA.efx):
    h:<Holding>   NODES[*].innate (strip_md)         hm:<Holding>  NODES[*].mastery (strip_md)
    i:<Infra>     INFRASTRUCTURE[*].empire_bonus     w:<Wonder>    Wondrous-tier empire_bonus
    f:<Faction>   FACTIONS[*].mechanic, ** removed   F:<Faction>   FACTIONS[*].mechanic as written
    s:<Domain>:<Standing>  DOMAIN_BOARD text (windows report only)

Scopes:
    clause  text split like the board (/;|\\.\\s+|\\.$/), each clause trimmed, first match per clause -> [m0, m1, ...]
    craw    same split, clauses NOT trimmed
    text    whole text, first match -> one hit
    all     whole text, every match
    json    first match in the JSON of the infra / wonder record (Reach on Infrastructure)

Patterns are written in the subset shared by Python `re` and JavaScript RegExp (ASCII \\w, IGNORECASE), so
parity_efx.js can replay them in node and compare. Every clause also gets a timing window (see `window_of`)
for the once-per tracker, the Realm action dock and ENVOY_WINDOW_REVIEW.md.
"""
import json, re

SPLIT = re.compile(r";|\.\s+|\.$")
F = re.I | re.A

# id -> (scope, source kinds, pattern); kinds are letters: h i w f F, M = hm (Holding Mastery text)
REG = {
    # ---- action riders / Doubt ----
    "doubt_all_plus":      ("clause", "hiwf", r"All player actions that cause Doubt are increased by (\d+)"),
    "doubt_target_minus":  ("clause", "hiwf", r"^(?:(\w+) )?actions targeting this player that cause Doubt are reduced by (\d+)"),
    "cunning_extra_doubt": ("clause", "hiwf", r"^(?:All )?(Endorsed )?Cunning actions give an additional \**Doubt \+?(\d+)\** to Target"),
    # "When your Piety actions give their target Faith, it gains Faith +1 more; when they give Doubt, it gains Doubt +1 more" (Unforgotten Shrine):
    # whole text (the clause split would cut it at the ";"); m[1] Domain, m[2] extra Faith, m[3] extra Doubt — each only where the action gave it
    "basilica_amp":        ("text", "hiwf", r"When your (\w+) actions give their target \**Faith\**, it gains \**Faith \+(\d+)\** more; when they give \**Doubt\**, it gains \**Doubt \+(\d+)\** more"),
    "doubt_backlash":      ("clause", "hiwf", r"Players who target you or your settlements with actions that (?:would )?cause doubt( before modifiers)? gain Doubt \+(\d+)"),
    "rider_extra":         ("clause", "hiwf", r"((?:Endorsed )?(\w+) actions (?:give|cause) an additional (?:Doubt|Faith)[^.;]*)"),
    "rider_your_extra":    ("clause", "hiwf", r"(Your (\w+) actions cause an additional[^.;]*)"),
    "doubt_all_plus_t":    ("clause", "hiwf", r"(All player actions that cause Doubt are increased by \d+)"),
    "doubt_target_minus_t":("clause", "hiwf", r"((?:(\w+) )?actions targeting this player that cause Doubt are reduced by \d+[^.;]*)"),
    "doubt_backlash_t":    ("clause", "hiwf", r"(Players who target you or your settlements with actions that (?:would )?cause doubt(?: before modifiers)? gain Doubt \+\d+)"),
    "cant_target":         ("clause", "hiwf", r"(?:can.t|cannot) be the target of (?:a |an )?([\w ]+?) action"),
    # ---- Envoys / actions ----
    "foster_endorsed":     ("clause", "hiwf", r"Endorsed Foster Rebellion instead places Bandit Armies with (\d+) retinues"),
    "grand_vizier_alt":    ("clause", "hiwf", r"Unlocks Grand Vizier which uses your (Piety Value|Public Order)"),
    "no_envoy_cost":       ("clause", "hiwf", r"no longer pay cost for (\w+) Envoys"),
    "recoup_envoy":        ("clause", "hiwf", r"(Passed|Endorsed) (\w+) envoys \**Recoup (\d+) Gold"),
    "recoup_on_cunning":   ("clause", "hiwf", r"Whenever another player performs a Cunning action, you may recoup (\d+) gold"),
    "envoy_next_fewer":    ("clause", "hiwf", r"send (\d+) fewer Envoys? next turn"),
    "no_alliance":         ("clause", "hiwf", r"(?:can.t|cannot) (?:be in|join) an Alliance"),
    # ---- armies / sieges ----
    "immune_strain_home":  ("clause", "hiwf", r"Armies and Garrisons within controlled Settlements gain\s+Immune Strained"),
    "immune_strain_siege": ("clause", "hiwf", r"Immune Strained during Lay Siege"),
    "besiege_exempt":      ("clause", "hiwf", r"not affected by .Settlements being Besieged. restrictions"),
    "muster_besieged":     ("clause", "hiwf", r"May Muster an Army in a Settlement under Siege|not affected by .Settlements being Besieged. restrictions"),
    "siege_def_plus":      ("clause", "hiwf", r"^(?!.*While your Public Order).*?Siege Timer\s*\+\s?(\d+)"),
    "siege_def_po":        ("clause", "hiwf", r"While your Public Order is (-?\d+) or higher, Lay Siege actions targeting Settlements you Control have Siege Timer \+(\d+)"),
    "siege_att_minus":     ("clause", "hiwf", "Siege Timer\\s*[\\-−]\\s?(\\d+)"),
    "siege_ignore_walls":  ("clause", "hiwf", r"Siege Timers ignore ([\w &]+?) Walls"),
    "siege_winter":        ("clause", "hiwf", r"Sieges Increment in Winter|Siege Timers count down in Winter"),
    "spoils_always":       ("clause", "hiwf", r"collect the Spoils of War whether you win or lose"),
    "faith_battle_loss":   ("clause", "hiwf", r"Faith \+(\d+) in every Battle where you lose (\d+) or more Retinues"),
    "army_free_province":  ("clause", "hiwf", r"Armies do not pay Upkeep while in (?:your )?Province"),
    "army_upkeep_outside": ("clause", "hiwf", r"Upkeep -(\d+) while not in (?:your )?Province"),
    "army_upkeep_home":    ("clause", "hiwf", r"Upkeep -(\d+) while an army is (?:within )?range 0 of (?:controlled settlement|a Settlement you Control)"),
    "danegeld":            ("clause", "hiwf", r"While At War, your Armies (?:within reach of at-war Settlements Extort their upkeep|pay no upkeep in Territory your at-war player controls)"),
    # ---- movement triggers (Toll House, Beacon Towers) ----
    "toll_extort":         ("clause", "hiwf", r"Extort (\d+) when non-Allied Army ends a Move action within your Province"),
    "toll_diplomacy":      ("clause", "hiwf", r"when an Army ends a Move action within your Province,? Perform a Diplomacy action targeting that army.s player"),
    "beacon_move":         ("clause", "hiwf", r"Whenever a non-allied Army ends a Move action within your Province, you may immediately perform a Move action"),
    # ---- Public Order / Faith / Doubt ----
    "po_cap":              ("clause", "hiwf", r"Public Order can.t exceed (-?\d+)"),
    "po_floor":            ("clause", "hiwf", r"Public Order would ever be less than (-?\d+),? set it to (-?\d+)"),
    "immune_war_weariness":("clause", "hiwf", r"Immune War Weariness"),
    "fd_per_empire":       ("clause", "hiwf", r"^(?:[^:]+:\s*)?(?:Gain )?(Faith|Doubt) \+(\d+) (?:per|each) Empire Phase$"),
    "sacred_war_each":     ("clause", "hiwf", r"Each player gains (Doubt|Faith) \+(\d+) (?:per|each) Empire Phase per Sacred War you.re on"),
    "border_fd":           ("clause", "hiwf", r"Each bordering player gains (Doubt|Faith) \+(\d+)"),
    "faith_war":           ("clause", "hiwf", r"Faith \+(\d+) while (not )?at War"),
    "faith_per_war":       ("clause", "hiwf", r"Faith \+(\d+) for every player you.re At War with"),
    "trade_partner_faith": ("clause", "hiwf", r"Faith \+(\d+) per Trade Partner with Craft (\d+)\+, and each of those partners gains Faith \+(\d+)"),
    # ---- economy ----
    "gold_per_craft":      ("clause", "hiwf", r"Gain \+?(\d+)(?: gold)? per (?:total )?Craft"),
    "partner_craft":       ("clause", "hiwf", r"(?:Trade Partners|Players who trade with you) gain Craft \+(\d+)"),
    "trade_extra":         ("clause", "hiwf", r"count as Trading with an additional (\d+) players?"),
    "trade_mult":          ("clause", "hiwf", r"generate (thrice|twice) as much for yourself"),
    "trade_no_roads":      ("clause", "hiwf", r"may trade without Dirt Roads|^Can Trade$"),
    "trade_border":        ("clause", "hiwf", r"may trade so long as your border touches another player"),
    "loan_terms":          ("clause", "hiwf", r"loan money to Trade Partners at (\d+) per (\d+)\s*/\s*turn interest\s*\(minimum (\d+)\)"),
    "loan_default":        ("clause", "hiwf", r"^on Default:\s*Perform (.+)$"),
    "loan_once":           ("clause", "hiwf", r"Once per turn,? (?:you )?may loan money"),
    "tithe_lower":         ("clause", "hiwf", r"Tithe every other player with lower (\w+)"),
    "extort_half_trade":   ("clause", "hiwf", r"Extort half of Trade Income from players who don.t trade with you"),
    "extort_target_faith": ("clause", "hiwf", r"Targets of Extort from (.+?) gain Faith \+(\d+)"),
    # ---- bandits ----
    "bandit_redirect":     ("clause", "hiwf", r"Bandit Camps in your Outlaw Country don.t target you and instead target other players randomly"),
    "bandit_cunning_auth": ("clause", "hiwf", r"Both Bandit Camps & you have (?:Authority|Influence) \+(\d+) on (?:Personal )?Cunning Envoys"),
    # ---- direct text readers (whole text of one source kind) ----
    "first_doubt":         ("text", "h", r"first\s+(?:(one|two|three|four|five|\d+)\s+)?\**Doubt\**\s+(?:(?:per|each) turn|each Empire Phase) reduced by (\d+)|reduce the first instance of Doubt[^.;]*?by (\d+)"),
    "extort_slot":         ("craw", "h", r"^\s*Extort\s*(\d+)(\s+twice)?\.?\s*$"),
    "no_upkeep_tier":      ("all", "h", r"No Upkeep on (\w+) Infrastructure"),
    "tax_double":          ("text", "h", r"Tax Income is Doubled"),
    "po_immune":           ("text", "h", r"No longer affected by all Public Order effects"),
    "po_band_double":      ("text", "h", r"^(.+?) effects are doubled for all players"),
    "immune_uprising":     ("text", "h", r"Immune Uprising"),
    "fd_others_without":   ("text", "h", r"(Faith|Doubt)\s*\+(\d+) to all other players without (?:an? )?([^.;]+)"),
    "fd_per_treaty":       ("text", "h", r"Other non-vassal players gain (Faith|Doubt)\s*\+(\d+) per Signed Treaty with you besides Peace"),
    "ep_lower":            ("text", "hM", r"Each Empire Phase, all (?:other )?non-allied players with a lower (\w+) value gain (Faith|Doubt)\s*\+(\d+)"),
    "build_timer":         ("all", "hM", "Build Timer\\s*([+\\-−])\\s?(\\d+)"),
    "reach_plus":          ("text", "hMF", r"Reach\s*\+\s*(\d+)"),
    "reach_plus_rec":      ("json", "iw", r"Reach\s*\+\s*(\d+)"),
    "garrison_sizes":      ("text", "i", r"Local Armies form \(([\d/ ]+) by Settlement size\)"),
    "garrison":            ("text", "i", r"Local Armies form"),
    "muster_field":        ("text", "i", r"Can Muster"),
    "shipyard":            ("text", "hi", r"Water Territory treated as Grassland"),
    "bridges":             ("text", "hi", r"cross Water Territory at full movement within (?:your )?Province"),
    # ---- faction mechanic as written ----
    "ignore_terrain":      ("text", "F", r"ignore all (?:negative )?terrain Speed modifiers"),
    "fac_type_bonus":      ("text", "f", r"Your ([\w &,]+?) (?:Pursuits|Holdings) have Craft \+(\d+)( and cost no Upkeep)?"),
    "fac_dom_bonus":       ("text", "f", r"Your (?:Pursuits|Holdings) (?:which|that) require (\w+)(?: Standing)? have Craft \+(\d+)( and cost no Upkeep)?"),
    "occupy_tax":          ("text", "F", r"to collect taxes[^.]*end your turn inside it"),
    "morale_cap":          ("text", "F", r"Morale can't be modified beyond (\d+)\+"),
    "raw_noclaim":         ("text", "F", r"Raw Material\s+\w+\s+within (?:your )?Reach are always active"),
    "royal_marriage":      ("text", "F", r"While in that Alliance, each member gains Faith \+(\d+) and (?:\+(\d+) Influence|Influence \+(\d+)) (?:per turn|each Empire Phase)"),
    "mountain_grass":      ("text", "F", r"treat mountain Territory as grassland for movement"),
    "war_on_you_doubt":    ("text", "F", r"When a player Declares War on you, that player and their allies gain Doubt \+(\d+)"),
    "raze_extort":         ("text", "F", r"When you are the target of a Raze action, Extort (\d+) from the (?:target|player) that performed the Raze action"),
    "trade_gate":          ("text", "F", r"No player may trade unless they first hold a Trade Agreement with you(, or are At War with you)?"),
    "build_edict":         ("text", "F", r"When a player builds an? ([\w ]+?), you must (\w+) it as an Edict"),
    "ally_cant":           ("text", "F", r"You \(and your Alliance\) can.t perform ([\w ]+?) actions"),
    "cant_on_you":         ("text", "F", r"Other players can.t perform ([\w ]+?) on you"),
    "no_renown_into":      ("text", "F", r"(?:can.t|cannot) put Renown into (\w+)"),
    "domain_max":          ("text", "F", r"(?:nor|can.t|cannot) have more than (\d+) in (\w+)"),
    "duke_war":            ("text", "F", r"When a player Declares War on the Duke"),
}

# ---- once-per / "may" tracker rows (the board's Once-per card) ----
ONCE_RE = re.compile(r"\b(?:Once\s*/\s*turn|Once per turn|Once per game|Once per \w+ Phase|\d+x\s*(?:/\s*turn|per \w+ Phase)|Each turn|Every turn|Every Skirmish|At the Start of the Empire Phase)\b|\bmay\b(?!\s+not)", F)
XCH_RE = re.compile(r"(\d+)x\s*(?:/\s*turn|per \w+ Phase):?\s*exchange (\d+) gold for (?:(\d+) Influence|Influence \+(\d+))", F)
CANT_RE = re.compile(r"(?:can.t|cannot)\s+(.+?)(?=,?\s+and\s+(?:you\s+)?(?:can.t|cannot)\b|$)", F)
CANT_SKIP = re.compile(r"^(?:be the target|be in an Alliance|pursue|build|equip|use shields|gain Immune|exceed|refuse|choose|vote|be modified|be Razed)|\bon you$", F)
SP_RE = re.compile("Speed\\s*([+\\-−])\\s?(\\d+)", F)


def once_phase(c):
    if re.search(r"\bOnce per turn\b", c, F): return "turn"
    m = re.search(r"per (\w+) Phase|At the (Start) of the Empire Phase|\bin the (\w+) Phase\b", c, F)
    if not m: return ""
    return m.group(1).lower() if m.group(1) else m.group(3).lower() if m.group(3) else "empire"


PHASES = ("empire", "council", "envoy", "battle", "rest")


def window_of(c):
    """Timing window of one clause: {win, lim, may, trig, envoy, scope} (empty strings when the clause has none).
      win   start-empire | empire | council | envoy | battle | rest | turn (any phase, resets each turn) | game | skirmish
      lim   once | Nx | each
      trig  the condition after Whenever / When / If / Before / After (up to the comma)
      scope Envoy predicate: personal | council | '' (the clause names Envoys without either)"""
    w = {"win": "", "lim": "", "may": bool(re.search(r"\bmay\b(?!\s+not)", c, F)), "trig": "", "envoy": bool(re.search(r"\benvoys?\b", c, F)), "scope": ""}
    if re.search(r"\bOnce per game\b", c, F): w.update(win="game", lim="once")
    elif re.search(r"\bAt the Start of the Empire Phase\b", c, F): w.update(win="start-empire", lim="each")
    elif re.search(r"\bOnce per turn\b|\bOnce\s*/\s*turn\b", c, F): w.update(win="turn", lim="once")
    else:
        m = re.search(r"\b(\d+)x\s*/\s*turn\b", c, F)
        if m: w.update(win="turn", lim=m.group(1) + "x")
        else:
            m = re.search(r"\b(Once|\d+x) per (\w+) Phase\b", c, F)
            if m and m.group(2).lower() in PHASES: w.update(win=m.group(2).lower(), lim="once" if m.group(1).lower() == "once" else m.group(1).lower())
            elif re.search(r"\bEach turn\b|\bEvery turn\b|\bper turn\b", c, F): w.update(win="turn", lim="each")
            elif re.search(r"\bEvery Skirmish\b", c, F): w.update(win="skirmish", lim="each")
            else:
                m = re.search(r"\b(?:each|per|every) (\w+) Phase\b|\bin the (\w+) Phase\b|\bduring the (\w+) Phase\b", c, F)
                ph = m and (m.group(1) or m.group(2) or m.group(3) or "").lower()
                if ph in PHASES: w.update(win=ph, lim="each")
    m = re.search(r"\b(?:Whenever|When|If|Before|After)\b\s+([^,:]+)", c, F)
    if m: w["trig"] = m.group(1).strip()
    if w["envoy"]:
        if re.search(r"\bPersonal (?:\w+ )?(?:Actions?|Envoys?)\b|\bnon-Council Envoys?\b", c, F): w["scope"] = "personal"
        elif re.search(r"\bCouncil (?:Envoys?|Phase)\b|\bsent during the Council Phase\b", c, F): w["scope"] = "council"
        # no predicate, but limited to one Phase: Envoy Phase = Personal Envoys, Council Phase = Council Envoys
        elif w["win"] == "envoy": w.update(scope="personal", implied=True)
        elif w["win"] == "council": w.update(scope="council", implied=True)
    return w


def _clauses(text, trim=True):
    out = []
    for c in SPLIT.split(text or ""):
        out.append(c.strip() if trim else c)
    return out


def _groups(m):
    return [m.group(0)] + [m.group(i) for i in range(1, (m.re.groups or 0) + 1)]


def sources(ns, records, infra, wonders, strip_md):
    """[(key, name, kind, text)] in the order the board reads them."""
    out = []
    for n, r in records.items():
        out.append(("h:" + n, n, "h", r.get("innate_raw") or ""))
        if r.get("mastery_raw"): out.append(("hm:" + n, n, "hm", r.get("mastery_raw") or ""))
    for n, r in infra.items(): out.append(("i:" + n, n, "i", r.get("effect_raw") or ""))
    for n, r in wonders.items(): out.append(("w:" + n, n, "w", r.get("effect_raw") or ""))
    for n, v in (ns.get("FACTIONS") or {}).items():
        mech = str(v.get("mechanic") or "")
        if not mech: continue
        out.append(("f:" + n, n, "f", mech.replace("**", "")))
        out.append(("F:" + n, n, "F", mech))
    for d, v in (ns.get("DOMAIN_BOARD") or {}).items():
        if isinstance(v, dict):
            for t, x in v.items():
                if isinstance(x, str) and t in ("Rising", "Established", "Sovereign"):
                    out.append(("s:%s:%s" % (d, t), x.split(":")[0].strip(), "s", x))
    return out


def _speed_rows(text, fac=False):
    """Speed clauses as the board's speedOf scanned them: {c, v, k (startProv|others|season|cond|plain), s, yp, en, na}"""
    t = str(text or "").replace("**", "")
    if fac: t = re.sub(r"don.t gain Speed[^.;]*", "", t, flags=F)
    rows = []
    for c in re.split(r"[;.]\s*", t):
        m = SP_RE.search(c)
        if not m: continue
        v = (1 if m.group(1) == "+" else -1) * int(m.group(2))
        r = {"c": c, "v": v, "yp": bool(re.search(r"your Province", c, F)), "en": bool(re.search(r"Enemy", c, F)), "na": bool(re.search(r"non-allied", c, F))}
        if re.search(r"start a Move action within (?:your )?Province", c, F): r["k"] = "startProv"
        elif re.search(r"your Province|non-allied|Enemy", c, F): r["k"] = "others"
        else:
            ms = re.search(r"in (Spring|Summer|Fall|Winter)", c, F)
            if ms: r.update(k="season", s=ms.group(1))
            elif re.search(r"\b(while|if|when)\b", c, F): r["k"] = "cond"
            else: r["k"] = "plain"
        rows.append(r)
    return rows


def build_efx(ns, records, infra, wonders, strip_md):
    """DATA.efx: {source key: {id: hits}} plus per-clause rows: _once (tracker), _cant (restrictions), _sp / _spo (Speed),
    _win (every clause with a timing window or an Envoy mention: [clause, window])."""
    comp = {k: (sc, kinds, re.compile(p, F)) for k, (sc, kinds, p) in REG.items()}
    recs = dict(infra); recs.update(wonders)
    efx = {}
    for key, name, kind, text in sources(ns, records, infra, wonders, strip_md):
        e = {}
        for rid, (sc, kinds, rx) in comp.items():
            if {"hm": "M"}.get(kind, kind) not in kinds: continue
            hits = []
            if sc == "clause":
                for c in _clauses(text):
                    m = rx.search(c)
                    if m: hits.append(_groups(m))
            elif sc == "craw":
                for c in _clauses(text, trim=False):
                    m = rx.search(c)
                    if m: hits.append(_groups(m))
            elif sc == "text":
                m = rx.search(text)
                if m: hits.append(_groups(m))
            elif sc == "all":
                hits = [_groups(m) for m in rx.finditer(text)]
            elif sc == "json":
                m = rx.search(json.dumps(recs.get(name, {}), ensure_ascii=False, separators=(",", ":")))
                if m: hits.append(_groups(m))
            if hits: e[rid] = hits
        if kind in "hiwf":
            once, cant = [], []
            for c in _clauses(text):
                if c and ONCE_RE.search(c):
                    i = ONCE_RE.search(c).start(); cm = c.rfind(", ", 0, i + 2)
                    cc = c[cm + 2:] if cm > 0 else c
                    x = XCH_RE.search(cc)
                    once.append({"c": cc, "ph": once_phase(cc), "game": bool(re.search(r"Once per game", cc, F)),
                                 "x": _groups(x) if x else None, "w": window_of(cc)})
            for cl in _clauses(text, trim=False):
                for m in CANT_RE.finditer(cl):
                    if not CANT_SKIP.search(m.group(1)): cant.append(m.group(1))
            if once: e["_once"] = once
            if cant: e["_cant"] = cant
        if kind in ("h", "i"):
            sp = _speed_rows(text)
            if sp: e["_sp"] = sp
        if kind == "F":
            sp = _speed_rows(text, fac=True)
            if sp: e["_sp"] = sp
            spo = _speed_rows(text)
            if spo: e["_spo"] = spo
        if kind in "hiwfs":
            wins = [[c, window_of(c)] for c in _clauses(text) if c]
            wins = [x for x in wins if x[1]["win"] or x[1]["envoy"]]
            if wins: e["_win"] = wins
        if e: efx[key] = e
    return efx


def envoy_window_review(ns, records, infra, wonders, strip_md):
    """ENVOY_WINDOW_REVIEW.md rows: every clause that names Envoys, with its window and its Personal / Council predicate.
    A clause with no predicate covers Council Envoys (Council Phase) and Personal Envoys (Envoy Phase)."""
    efx = build_efx(ns, records, infra, wonders, strip_md)
    label = {"h": "Holding", "i": "Infrastructure", "w": "Wonder", "f": "Faction", "s": "Standing"}
    rows = []
    for key, e in efx.items():
        kind, _, name = key.partition(":")
        if kind not in label: continue
        for c, w in e.get("_win", []):
            if not w["envoy"]: continue
            issue = ""
            if not w["scope"] and w["win"] in ("council", "envoy"):
                issue = "names a Phase but no Personal / Council predicate: Envoys of the other Phase are out of reach"
            elif not w["scope"] and not w["win"]:
                issue = "no window: applies in both Council and Envoy Phases"
            rows.append({"kind": label[kind], "name": name if kind != "s" else key[2:].replace(":", " "), "clause": c,
                         "window": w["win"] or "-", "limit": w["lim"] or "-", "scope": (w["scope"] + (" (by Phase)" if w.get("implied") else "")) or "-", "issue": issue})
    return rows
