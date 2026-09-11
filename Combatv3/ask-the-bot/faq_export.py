#!/usr/bin/env python3
"""faq_export.py — dump renown_data.GLOSSARY (and a few key rules) into a flat
`keyword | answer` text file for the Discord bot's local !ask FAQ. No API, no
cost — the bot just serves your own rules back. Re-run whenever the glossary
changes so the FAQ tracks renown_data.

Answers inline-link their own subject to the public wiki via [text](url) so the
bot's replies are clickable in Discord. Set WIKI_BASE to your Pages URL.

Usage:  python faq_export.py [output.txt]
Default output: renown_faq.txt  (copy to the bot's storage dir)
"""
import sys
sys.path.insert(0, ".")
import renown_data as rd

# ── Wiki linking ────────────────────────────────────────────────────────────
WIKI_BASE = "https://mlang95.github.io/RenownWiki"

def _slug(s):
    import re
    s = str(s).lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s

def wlink(text, page, anchor=None):
    """Markdown link for Discord: [text](WIKI_BASE/page[#anchor])."""
    url = f"{WIKI_BASE}/{page}"
    if anchor:
        url += f"#{anchor}"
    return f"[{text}]({url})"

def entry(key, answer):
    """Build a 'key | answer' line, sanitizing | out of the ANSWER only so the
    delimiter is never clobbered. (Links in the answer are preserved.)"""
    return f"{key} | {str(answer).replace('|', '/')}"

# Which wiki page each escalation node lives on (all on the combat pursuits page).
ESC_NODES = rd.get_data("escalation")

def build(out_path):
    lines = []

    # combat keywords get the keywords-ref page; everything else the glossary.
    # The keyword subset mirrors card_sheet / the wiki keywords page.
    KW_TERMS = {rd.STEADY, rd.UNWIELDY, rd.TWO_H, rd.SHATTER_ARMOR, rd.UNSTOPPABLE,
                rd.CLEAVE, rd.POISON, rd.NIMBLE, rd.DRILLED, rd.DESTROY_SHIELD,
                rd.BLUNDER, rd.ONE_SHOT, rd.DEFLECT, rd.IMMUNE_PANIC, rd.UNBREAKABLE,
                rd.PARRY, rd.RIPOSTE, rd.RECOVER, rd.SERRATED, rd.PLANISHING,
                rd.FATIGUE_TOKEN, rd.MINUS_1_TBH}

    # 1) every glossary term  (subject links to keywords page if combat, else glossary)
    for term, definition in sorted(rd.GLOSSARY.items()):
        d = " ".join(str(definition).split())          # collapse whitespace
        d = d.replace("|", "/")                          # | is the delimiter
        if term in KW_TERMS:
            link = wlink(term, "keywords-ref.html", _slug(term))
        else:
            link = wlink(term, "glossary.html", _slug(term))
        lines.append(f"{term} | {link}: {d}")

    # 2) a few high-value rules people will ask about, pulled from data
    tr = dict(rd.TRADE_RULES) if hasattr(rd, "TRADE_RULES") else {}
    if tr:
        lines.append("trade | " + wlink("Trade rules", "reference-tables.html") +
                     ": Income = 100 x Craft x partners x 0.75. "
                     f"No trade in {tr.get('no_trade_season','Spring')}. "
                     f"Tax only in {tr.get('tax_season','Winter')}. "
                     "Requires bordering, Dirt Road, and a Trade Agreement.")
    lines.append("monument cap | You may build at most 2 Monuments.")
    lines.append("tiers | " + wlink("Tier ladder", "reference-tables.html") +
                 ": 1.Cr Crude (start) -> 2.Ca Cast (Furnace) -> 3.W Wrought "
                 "(Blacksmith) -> 4.F Forged (Forge) -> 5.Cf Crafted (ABF).")

    # 3) retinues
    for n, r in rd.RETINUES.items():
        kw = " Unbreakable." if r.get("unbreakable") else ""
        lines.append(f"{n} | " + wlink(n, "equipment-ref.html") +
                     f" Retinue. Strike {r.get('to_hit')}+, Endurance "
                     f"{r.get('endurance')}, Morale {r.get('shaking')}+, cost {r.get('cost')}.{kw}")

    # 4) weapons / ranged (stats + keywords)
    def _wline(n, w, kind):
        tags = ", ".join(w.get("tags") or []) or "none"
        return (f"{n} | " + wlink(n, "equipment-ref.html") +
                f" {kind} ({w.get('tier','')}). AP {w.get('ap','')}, "
                f"Init {w.get('init',0):+d}. Keywords: {tags}.")
    for n, w in rd.WEAPONS.items():
        lines.append(_wline(n, w, "Melee weapon"))
    for n, w in rd.RANGED.items():
        lines.append(_wline(n, w, "Ranged weapon"))
    for n, sh in rd.SHIELDS.items():
        if not n: continue
        tags = ", ".join(sh.get("tags") or []) or "none"
        lines.append(f"{n} | " + wlink(n, "equipment-ref.html") +
                     f" Shield ({sh.get('tier','')}). Save +{sh.get('save_bonus','')}, "
                     f"Init {sh.get('init',0):+d}. Keywords: {tags}.")
    for n, a in rd.ARMORS.items():
        tags = ", ".join(a.get("tags") or []) or "none"
        lines.append(f"{n} | " + wlink(n, "equipment-ref.html") +
                     f" Armor ({a.get('tier','')}). Save {a.get('save','')}+. Keywords: {tags}.")

    # 4b) tier category lists
    TIERS = ["Crude", "Cast", "Wrought", "Forged", "Crafted"]
    for tier in TIERS:
        melee  = [n for n, w in rd.WEAPONS.items() if w.get("tier") == tier]
        ranged = [n for n, w in rd.RANGED.items() if w.get("tier") == tier]
        members = melee + ranged
        if members:
            lines.append(f"{tier.lower()} weapons | " + wlink(f"{tier} tier", "equipment-ref.html") +
                         f" ({len(members)}): " + ", ".join(members))
        sh = [n for n, s in rd.SHIELDS.items() if n and s.get("tier") == tier]
        ar = [n for n, a in rd.ARMORS.items() if a.get("tier") == tier]
        if members or sh or ar:
            lines.append(f"{tier.lower()} gear | {tier} tier: weapons [{', '.join(members) or 'none'}], "
                         f"shields [{', '.join(sh) or 'none'}], armor [{', '.join(ar) or 'none'}].")
    lines.append("weapon tiers | " + wlink("Equipment", "equipment-ref.html") +
                 ": Crude (start) -> Cast (Furnace) -> Wrought (Blacksmith) -> "
                 "Forged (Forge) -> Crafted (ABF). Ask e.g. 'wrought weapons' for a tier's list.")

    # 5) factions
    for n, fac in rd.FACTIONS.items():
        if isinstance(fac, dict):
            feel = fac.get("feel", ""); diff = fac.get("difficulty", ""); stg = fac.get("strength", "")
            mech = " ".join(str(fac.get("mechanic", "")).split())
            meta = f"Faction ({diff} difficulty, {stg} strength, {feel})." if diff else "Faction."
            lines.append(entry(n, wlink(n, "factions.html") + f" {meta} {mech}"))
        elif fac:
            lines.append(f"{n} | " + wlink(n, "factions.html") + f" Faction. {' '.join(str(fac).split())}")

    # 5b) faction category lists
    def _facs_by(field, value):
        return [n for n, f in rd.FACTIONS.items()
                if isinstance(f, dict) and str(f.get(field, "")).lower() == value.lower()]
    for lvl in ("Low", "Medium", "High"):
        d = _facs_by("difficulty", lvl)
        if d:
            lines.append(f"{lvl.lower()} difficulty factions | {len(d)} factions: " + ", ".join(d))
        st = _facs_by("strength", lvl)
        if st:
            lines.append(f"{lvl.lower()} strength factions | {len(st)} factions: " + ", ".join(st))
    lines.append("easy factions | See 'low difficulty factions'.")
    lines.append("hard factions | See 'high difficulty factions'.")
    lines.append("strong factions | See 'high strength factions'.")
    lines.append("powerful factions | See 'high strength factions'.")
    lines.append("weak factions | See 'low strength factions'.")
    lines.append("factions | " + wlink(str(len(rd.FACTIONS)) + " factions", "factions.html") +
                 ". Filter by 'low/medium/high difficulty factions' or "
                 "'low/medium/high strength factions', or ask a faction by name.")

    # 6) pursuits (name | innate / mastery effect) — escalation pursuits point at the combat page
    for n, node in rd.NODES.items():
        inn = (node.get("innate") or "").strip()
        mas = (node.get("mastery") or "").strip()
        parts = []
        if inn: parts.append("Innate: " + inn)
        if mas: parts.append("Mastery: " + mas)
        if parts:
            txt = " ".join(" / ".join(parts).split()).replace("|", "/").replace("**", "")
            page = "escalation-pursuits.html" if n in ESC_NODES else "pursuits.html"
            lines.append(f"{n} | " + wlink(n, page) + f" Pursuit ({node.get('type','')}). {txt}")

    # 7) eras
    era_names = list(rd.ERAS.keys()) if hasattr(rd, "ERAS") else []
    for n, e in (rd.ERAS.items() if hasattr(rd, "ERAS") else []):
        lines.append(entry(n, wlink(n, "eras-ref.html") +
                     f" Era. Renown {e.get('renown')}, armies {e.get('armies')}, "
                     f"cities {e.get('cities')}, influence/turn {e.get('influence_per_turn')}, "
                     f"envoys: {e.get('envoys','')}. Unlocks: {e.get('unlocks','')}"))
    if era_names:
        lines.append("era | " + wlink("Eras", "eras-ref.html") +
                     " are the empire's growth stages: " + " -> ".join(era_names) +
                     ". Each raises Renown, armies, cities, influence, and envoys.")
        lines.append("eras | " + wlink("Eras", "eras-ref.html") + ": " + " -> ".join(era_names) + ".")

    # 8) settlements
    for n, st in (rd.SETTLEMENTS.items() if hasattr(rd, "SETTLEMENTS") else []):
        lines.append(entry(n, wlink(n, "settlements-ref.html") +
                     f" Settlement (tier {st.get('tier')}). Tax {st.get('tax_income')}, "
                     f"muster {st.get('muster_limit')}, build {st.get('build_time')}, "
                     f"wards {st.get('wards')}, reach {st.get('reach')}. "
                     f"{st.get('notes','')}"))
    if hasattr(rd, "SETTLEMENTS"):
        lines.append("settlements | " + wlink("Settlements", "settlements-ref.html") +
                     ": " + ", ".join(rd.SETTLEMENTS.keys()) +
                     ". Each has tax, muster, wards, and reach values.")

    # 9) seasons
    for n, se in (rd.SEASONS.items() if hasattr(rd, "SEASONS") else []):
        nm = se.get("name", "")
        lines.append(entry(n, wlink(n, "seasons-ref.html") +
                     f" Season ({nm}). {se.get('effect','')}"))
    if hasattr(rd, "SEASONS"):
        lines.append("seasons | " + wlink("Seasons", "seasons-ref.html") + ": " +
                     ", ".join(rd.SEASONS.keys()) +
                     ". Each applies a global effect (e.g. Winter = tax + Speed -1).")

    # 10) public order bands
    for k, v in (rd.PUBLIC_ORDER.items() if hasattr(rd, "PUBLIC_ORDER") else []):
        if isinstance(v, tuple):
            state, effect = v[0], v[1] if len(v) > 1 else ""
            lines.append(entry(f"PO {k}", wlink(f"Public Order {k}", "public-order-ref.html") +
                         f" ({state}): {effect}"))
    lines.append("public order | " + wlink("Public Order", "public-order-ref.html") +
                 ": Faith/Doubt scale; each band (from Uprising to high Faith) applies "
                 "effects. See 'PO <number>' for a specific band.")

    # 11) domain standings
    _STANDINGS = {"Rising", "Established", "Sovereign"}
    real_domains = []
    for dom, tiers in (rd.DOMAIN_BOARD.items() if hasattr(rd, "DOMAIN_BOARD") else []):
        if isinstance(tiers, dict) and set(tiers.keys()) == _STANDINGS:
            real_domains.append(dom)
            parts = "; ".join(f"{tier}: {txt}" for tier, txt in tiers.items())
            lines.append(entry(dom, wlink(dom, "domain-board-ref.html") +
                         f" Domain standing. {parts}"))
    if real_domains:
        lines.append("domains | " + wlink("Domains", "domain-board-ref.html") + ": " +
                     ", ".join(real_domains) +
                     ". Standings (Rising/Established/Sovereign) grant empire effects.")

    # 12) wonders
    for n, w in (rd.WONDERS.items() if hasattr(rd, "WONDERS") else []):
        bonus = " ".join(str(w.get("empire_bonus","")).split()).replace("**","").replace("|","/")
        lines.append(f"{n} | " + wlink(n, "wonders-ref.html") +
                     f" Wonder. Upkeep {w.get('upkeep')} ({w.get('upkeep_frequency','')}). {bonus}")
    if hasattr(rd, "WONDERS"):
        lines.append("wonders | " + wlink("Wonders", "wonders-ref.html") + ": " +
                     ", ".join(rd.WONDERS.keys()) +
                     ". Each grants a powerful empire bonus; completing one scores its Edict.")

    # 13) infrastructure
    for n, inf in (rd.INFRASTRUCTURE.items() if hasattr(rd, "INFRASTRUCTURE") else []):
        bonus = " ".join(str(inf.get("empire_bonus","")).split()).replace("**","").replace("|","/")
        lines.append(f"{n} | " + wlink(n, "infrastructure-ref.html") +
                     f" Infrastructure ({inf.get('tier','')}). Upkeep {inf.get('upkeep')} "
                     f"({inf.get('upkeep_frequency','')}), build {inf.get('build_time','')}. {bonus}")
    if hasattr(rd, "INFRASTRUCTURE"):
        lines.append("infrastructure | " + wlink("Infrastructure", "infrastructure-ref.html") +
                     ": " + ", ".join(rd.INFRASTRUCTURE.keys()) + ".")

    # 14) win conditions / Edicts
    lines.append("how to win | " + wlink("Edicts", "rules-edicts.html") +
                 ": reach a Sovereign Standing, complete a Monument, or fulfill a victory "
                 "condition (Wonder, wealth, Vassalize, Living Saints, or Last Standing). "
                 "The game is about playing well, not just winning.")
    lines.append("win | See 'how to win'. Win paths are Edicts: Sovereign Standing, Monument, "
                 "Wonder, wealth, Vassalize, Living Saints, Last Standing.")
    lines.append("edicts | " + wlink("Edicts", "rules-edicts.html") +
                 ": Sovereign Standing, complete a Monument, Wonder, wealth, Vassalize, "
                 "Living Saints, Last Standing.")
    lines.append("victory | See 'how to win' / 'edicts'.")
    lines.append("vassalize | Win path (Edict): force other players into vassalage.")
    lines.append("living saints | Win path (Edict): a Piety-based victory condition.")
    lines.append("last standing | Win path (Edict): be the last empire standing.")

    # 15) procedural orientation entries
    lines.append("how to trade | Build a Dirt Road, border or ally a trade partner, sign a Trade "
                 "Agreement. Income = 100 x Craft x partners x 0.75. No trade in Spring.")
    lines.append("turn structure | Each turn players take actions (Host, Trade, Council, Nobility, "
                 "Pursuit) resolved via the influence vote; seasons cycle Winter->Spring->Summer->Fall.")
    lines.append("turn order | See 'turn structure'.")
    lines.append("how to attack | Resolve battles via the Escalation combat system: muster a Host, "
                 "Move into an enemy, fight skirmishes (Strike/Parry/Recover) until one side Routs.")
    lines.append("combat | See 'how to attack'. Battles use the Escalation skirmish system.")

    # ── 16) ESCALATION CAMPAIGN (data-driven from escalation.ranks + rules) ──
    ESC = "escalation"
    lines.append("escalation | " + wlink("Escalation Campaign", "escalation.html") +
                 ": a fast, battle-driven mode for 2+ players. Start with 25 Levy + Crude gear; "
                 "every Battle is fought at army size 25. Win VP each turn, then unlock a Standing "
                 "and Build one Pursuit. See 'escalation rules', 'escalation pursuits', "
                 "'tactic matrix', and the Combat Keywords.")
    lines.append("escalation rules | " + wlink("Escalation Battle Rules", "escalation-rules.html") +
                 ": setup, turn sequence, victory points, and the 12-step Skirmish walkthrough.")
    lines.append("escalation campaign | See 'escalation'.")
    lines.append("escalation setup | " + wlink("Escalation setup", "escalation-rules.html") +
                 ": each player starts with 25 Levy retinues, Farm Tools, Cloth armor, no shield; "
                 "all Domains Untested; 0 VP.")
    lines.append("escalation pursuits | " + wlink("Combat Pursuits", "escalation-pursuits.html") +
                 ": the pursuits available in Escalation, grouped by Domain, with their unlock "
                 "standing and rank effects.")
    lines.append("escalation victory | " + wlink("VP", "escalation-rules.html") +
                 ": Decisive Win +3, Minor Victory (enemy Fell Back) +2, successful Fall Back +1, "
                 "any other loss 0. Edicts (Sovereign Standing or mastered Monument) score VP too.")
    lines.append("victory points | See 'escalation victory'.")
    lines.append("vp | See 'escalation victory'.")
    lines.append("starting forces | " + wlink("Escalation setup", "escalation-rules.html") +
                 ": 25 Levy, Farm Tools, Cloth armor, no shield. Re-equip freely before each Battle "
                 "with anything unlocked.")

    # per-node escalation entries from ranks (keyed 'escalation <name>' to avoid
    # colliding with the full-game pursuit entry of the same name)
    for n, node in ESC_NODES.items():
        e = node.get("escalation", {}) or {}
        ranks = e.get("ranks", {}) or {}
        standing = e.get("standing", node.get("unlock", ""))
        r1 = (ranks.get(1, "") or "").strip()
        r2 = (ranks.get(2, "") or "").strip()
        body = f"Unlock: {standing}."
        if r1: body += f" Rank 1 (Innate): {r1}."
        if r2: body += f" Rank 2 (Mastery): {r2}."
        link = wlink(n, "escalation-pursuits.html")
        lines.append(entry(f"escalation {n}", f"{link} (Escalation). {body}"))

    # de-dup (a manual line may shadow a glossary one — keep the last)
    seen = {}
    for ln in lines:
        k = ln.split("|", 1)[0].strip().lower()
        seen[k] = ln
    final = [seen[k] for k in sorted(seen)]
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(final) + "\n")
    print(f"wrote {len(final)} FAQ entries -> {out_path}")

    # also emit a structured faction table CSV for the bot's tabulate view
    import csv, os as _os
    csv_path = _os.path.join(_os.path.dirname(out_path) or ".", "factions_table.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as cf:
        w = csv.writer(cf)
        w.writerow(["Faction", "Difficulty", "Strength", "Mechanic"])
        for n, fac in rd.FACTIONS.items():
            if isinstance(fac, dict):
                mech = str(fac.get("mechanic",""))
                mname = mech.split(":",1)[0].strip() if ":" in mech else ""
                w.writerow([n, fac.get("difficulty",""), fac.get("strength",""), mname])
    print(f"wrote faction table -> {csv_path}")

    # equipment table CSV for the bot's tabulate tier view
    eq_path = _os.path.join(_os.path.dirname(out_path) or ".", "equipment_table.csv")
    with open(eq_path, "w", newline="", encoding="utf-8") as ef:
        w = csv.writer(ef)
        w.writerow(["Item", "Type", "Tier", "AP_or_Save", "Init", "Keywords"])
        for n, d in rd.WEAPONS.items():
            w.writerow([n, "Melee", d.get("tier",""), d.get("ap",""), d.get("init",""),
                        ", ".join(d.get("tags") or [])])
        for n, d in rd.RANGED.items():
            w.writerow([n, "Ranged", d.get("tier",""), d.get("ap",""), d.get("init",""),
                        ", ".join(d.get("tags") or [])])
        for n, d in rd.SHIELDS.items():
            if not n: continue
            w.writerow([n, "Shield", d.get("tier",""), "+%s" % d.get("save_bonus",""),
                        d.get("init",""), ", ".join(d.get("tags") or [])])
        for n, d in rd.ARMORS.items():
            w.writerow([n, "Armor", d.get("tier",""), "%s+" % d.get("save",""), "",
                        ", ".join(d.get("tags") or [])])
    print(f"wrote equipment table -> {eq_path}")

if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "renown_faq.txt")