#!/usr/bin/env python3
"""faq_export.py — dump renown_data.GLOSSARY (and a few key rules) into a flat
`keyword | answer` text file for the Discord bot's local !ask FAQ. No API, no
cost — the bot just serves your own rules back. Re-run whenever the glossary
changes so the FAQ tracks renown_data.

Usage:  python faq_export.py [output.txt]
Default output: renown_faq.txt  (copy to the bot's storage dir)
"""
import sys
sys.path.insert(0, ".")
import renown_data as rd

def build(out_path):
    lines = []
    # 1) every glossary term
    for term, definition in sorted(rd.GLOSSARY.items()):
        d = " ".join(str(definition).split())          # collapse whitespace
        d = d.replace("|", "/")                          # | is the delimiter
        lines.append(f"{term} | {d}")

    # 2) a few high-value rules people will ask about, pulled from data
    tr = dict(rd.TRADE_RULES) if hasattr(rd, "TRADE_RULES") else {}
    if tr:
        lines.append("trade | Income = 100 x Craft x partners x 0.75. "
                     f"No trade in {tr.get('no_trade_season','Spring')}. "
                     f"Tax only in {tr.get('tax_season','Winter')}. "
                     "Requires bordering, Dirt Road, and a Trade Agreement.")
    # monument cap (commonly asked)
    lines.append("monument cap | You may build at most 2 Monuments.")
    # tier ladder (matches the card markers)
    lines.append("tiers | 1.Cr Crude (start) -> 2.Ca Cast (Furnace) -> 3.W Wrought "
                 "(Blacksmith) -> 4.F Forged (Forge) -> 5.Cf Crafted (ABF).")

    # 3) retinues (people ask "what is Knight Templar")
    for n, r in rd.RETINUES.items():
        kw = " Unbreakable." if r.get("unbreakable") else ""
        lines.append(f"{n} | Retinue. Strike {r.get('to_hit')}+, Endurance "
                     f"{r.get('endurance')}, Morale {r.get('shaking')}+, cost {r.get('cost')}.{kw}")

    # 4) weapons / ranged (stats + keywords)
    def _wline(n, w, kind):
        tags = ", ".join(w.get("tags") or []) or "none"
        return f"{n} | {kind} ({w.get('tier','')}). AP {w.get('ap','')}, Init {w.get('init',0):+d}. Keywords: {tags}."
    for n, w in rd.WEAPONS.items():
        if w.get("tier") == "Crude" or True:
            lines.append(_wline(n, w, "Melee weapon"))
    for n, w in rd.RANGED.items():
        lines.append(_wline(n, w, "Ranged weapon"))
    for n, sh in rd.SHIELDS.items():
        if not n: continue
        tags = ", ".join(sh.get("tags") or []) or "none"
        lines.append(f"{n} | Shield ({sh.get('tier','')}). Save +{sh.get('save_bonus','')}, "
                     f"Init {sh.get('init',0):+d}. Keywords: {tags}.")
    for n, a in rd.ARMORS.items():
        tags = ", ".join(a.get("tags") or []) or "none"
        lines.append(f"{n} | Armor ({a.get('tier','')}). Save {a.get('save','')}+. Keywords: {tags}.")

    # 4b) tier category lists: "wrought weapons", "crafted weapons", etc.
    TIERS = ["Crude", "Cast", "Wrought", "Forged", "Crafted"]
    for tier in TIERS:
        melee  = [n for n, w in rd.WEAPONS.items() if w.get("tier") == tier]
        ranged = [n for n, w in rd.RANGED.items() if w.get("tier") == tier]
        members = melee + ranged
        if members:
            lines.append(f"{tier.lower()} weapons | {tier} tier ({len(members)}): " + ", ".join(members))
        # also list gear (shield+armor) at this tier
        sh = [n for n, s in rd.SHIELDS.items() if n and s.get("tier") == tier]
        ar = [n for n, a in rd.ARMORS.items() if a.get("tier") == tier]
        gear = members + sh + ar
        if gear:
            lines.append(f"{tier.lower()} gear | {tier} tier: weapons [{', '.join(members) or 'none'}], "
                         f"shields [{', '.join(sh) or 'none'}], armor [{', '.join(ar) or 'none'}].")
    lines.append("weapon tiers | Crude (start) -> Cast (Furnace) -> Wrought (Blacksmith) -> "
                 "Forged (Forge) -> Crafted (ABF). Ask e.g. 'wrought weapons' for a tier's list.")

    # 5) factions (name | feel/difficulty/strength + mechanic)
    for n, fac in rd.FACTIONS.items():
        if isinstance(fac, dict):
            feel = fac.get("feel", ""); diff = fac.get("difficulty", ""); stg = fac.get("strength", "")
            mech = " ".join(str(fac.get("mechanic", "")).split())
            meta = f"Faction ({diff} difficulty, {stg} strength, {feel})." if diff else "Faction."
            lines.append(f"{n} | {meta} {mech}".replace("|", "/"))
        elif fac:
            lines.append(f"{n} | Faction. {' '.join(str(fac).split())}")

    # 5b) faction category lists (difficulty / strength) — answers "low difficulty factions" etc.
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
    # synonyms players might type
    lines.append("easy factions | See 'low difficulty factions'.")
    lines.append("hard factions | See 'high difficulty factions'.")
    lines.append("strong factions | See 'high strength factions'.")
    lines.append("powerful factions | See 'high strength factions'.")
    lines.append("weak factions | See 'low strength factions'.")
    lines.append("factions | " + str(len(rd.FACTIONS)) + " factions. Filter by 'low/medium/high "
                 "difficulty factions' or 'low/medium/high strength factions', or ask a faction by name.")

    # 6) pursuits (name | innate / mastery effect)
    for n, node in rd.NODES.items():
        inn = (node.get("innate") or "").strip()
        mas = (node.get("mastery") or "").strip()
        parts = []
        if inn: parts.append("Innate: " + inn)
        if mas: parts.append("Mastery: " + mas)
        if parts:
            txt = " ".join(" / ".join(parts).split()).replace("|", "/").replace("**", "")
            lines.append(f"{n} | Pursuit ({node.get('type','')}). {txt}")


    # 7) eras (each era's stats) + an "era" overview entry
    era_names = list(rd.ERAS.keys()) if hasattr(rd, "ERAS") else []
    for n, e in (rd.ERAS.items() if hasattr(rd, "ERAS") else []):
        lines.append(f"{n} | Era. Renown {e.get('renown')}, armies {e.get('armies')}, "
                     f"cities {e.get('cities')}, influence/turn {e.get('influence_per_turn')}, "
                     f"envoys: {e.get('envoys','')}. Unlocks: {e.get('unlocks','')}".replace("|", "/"))
    if era_names:
        lines.append("era | Eras are the empire's growth stages: " + " -> ".join(era_names)
                     + ". Each raises Renown, armies, cities, influence, and envoys.")
        lines.append("eras | Eras are the empire's growth stages: " + " -> ".join(era_names) + ".")

    # 8) settlements
    for n, st in (rd.SETTLEMENTS.items() if hasattr(rd, "SETTLEMENTS") else []):
        lines.append(f"{n} | Settlement (tier {st.get('tier')}). Tax {st.get('tax_income')}, "
                     f"muster {st.get('muster_limit')}, build {st.get('build_time')}, "
                     f"wards {st.get('wards')}, reach {st.get('reach')}. "
                     f"{st.get('notes','')}".replace("|", "/"))
    if hasattr(rd, "SETTLEMENTS"):
        lines.append("settlements | Settlement tiers: " + ", ".join(rd.SETTLEMENTS.keys())
                     + ". Each has tax, muster, wards, and reach values.")

    # 9) seasons
    for n, se in (rd.SEASONS.items() if hasattr(rd, "SEASONS") else []):
        nm = se.get("name", "")
        lines.append(f"{n} | Season ({nm}). {se.get('effect','')}".replace("|", "/"))
    if hasattr(rd, "SEASONS"):
        lines.append("seasons | The four seasons: " + ", ".join(rd.SEASONS.keys())
                     + ". Each applies a global effect (e.g. Winter = tax + Speed -1).")

    # 10) public order bands
    for k, v in (rd.PUBLIC_ORDER.items() if hasattr(rd, "PUBLIC_ORDER") else []):
        if isinstance(v, tuple):
            state, effect = v[0], v[1] if len(v) > 1 else ""
            lines.append(f"PO {k} | Public Order {k} ({state}): {effect}".replace("|", "/"))
    lines.append("public order | Faith/Doubt scale; each band (from Uprising to high Faith) "
                 "applies effects. See 'PO <number>' for a specific band.")

    # 11) domain standings
    _STANDINGS = {"Rising", "Established", "Sovereign"}
    real_domains = []
    for dom, tiers in (rd.DOMAIN_BOARD.items() if hasattr(rd, "DOMAIN_BOARD") else []):
        if isinstance(tiers, dict) and set(tiers.keys()) == _STANDINGS:
            real_domains.append(dom)
            parts = "; ".join(f"{tier}: {txt}" for tier, txt in tiers.items())
            lines.append(f"{dom} | Domain standing. {parts}".replace("|", "/"))
    if real_domains:
        lines.append("domains | The domains: " + ", ".join(real_domains)
                     + ". Standings (Rising/Established/Sovereign) grant empire effects.")


    # 12) wonders
    for n, w in (rd.WONDERS.items() if hasattr(rd, "WONDERS") else []):
        bonus = " ".join(str(w.get("empire_bonus","")).split()).replace("**","").replace("|","/")
        lines.append(f"{n} | Wonder. Upkeep {w.get('upkeep')} ({w.get('upkeep_frequency','')}). {bonus}")
    if hasattr(rd, "WONDERS"):
        lines.append("wonders | Grand build projects: " + ", ".join(rd.WONDERS.keys())
                     + ". Each grants a powerful empire bonus; completing one scores its Edict.")

    # 13) infrastructure
    for n, inf in (rd.INFRASTRUCTURE.items() if hasattr(rd, "INFRASTRUCTURE") else []):
        bonus = " ".join(str(inf.get("empire_bonus","")).split()).replace("**","").replace("|","/")
        lines.append(f"{n} | Infrastructure ({inf.get('tier','')}). Upkeep {inf.get('upkeep')} "
                     f"({inf.get('upkeep_frequency','')}), build {inf.get('build_time','')}. {bonus}")
    if hasattr(rd, "INFRASTRUCTURE"):
        lines.append("infrastructure | Empire-wide structures: " + ", ".join(rd.INFRASTRUCTURE.keys()) + ".")

    # 14) win conditions / Edicts — break out each path so players can ask directly
    lines.append("how to win | Win by scoring Edicts: reach a Sovereign Standing, complete a "
                 "Monument, or fulfill a victory condition (Wonder, wealth, Vassalize, Living "
                 "Saints, or Last Standing). The game is about playing well, not just winning.")
    lines.append("win | See 'how to win'. Win paths are Edicts: Sovereign Standing, Monument, "
                 "Wonder, wealth, Vassalize, Living Saints, Last Standing.")
    lines.append("edicts | The win paths / scoring achievements: Sovereign Standing, complete a "
                 "Monument, Wonder, wealth, Vassalize, Living Saints, Last Standing.")
    lines.append("victory | See 'how to win' / 'edicts'.")
    lines.append("vassalize | Win path (Edict): force other players into vassalage. See Vassalization rules.")
    lines.append("living saints | Win path (Edict): a Piety-based victory condition.")
    lines.append("last standing | Win path (Edict): be the last empire standing.")

    # 15) procedural orientation entries (the 'how do I' questions a keyword FAQ misses)
    lines.append("how to trade | Build a Dirt Road, border or ally a trade partner, sign a Trade "
                 "Agreement. Income = 100 x Craft x partners x 0.75. No trade in Spring.")
    lines.append("turn structure | Each turn players take actions (Host, Trade, Council, Nobility, "
                 "Pursuit) resolved via the influence vote; seasons cycle Winter->Spring->Summer->Fall.")
    lines.append("turn order | See 'turn structure'.")
    lines.append("how to attack | Resolve battles via the Escalation combat system: muster a Host, "
                 "Move into an enemy, fight skirmishes (Strike/Parry/Recover) until one side Routs.")
    lines.append("combat | See 'how to attack'. Battles use the Escalation skirmish system.")

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