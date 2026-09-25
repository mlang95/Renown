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
  * ARMY UPKEEP IS ENTERED MANUALLY, PER ARMY.  Retinue per-unit costs are deprecated
    and are NOT used.
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
    " while ", " when ", " per ", " if ", "once/turn", "once /turn", " target",
    "for trading", "at war", "besieged", "range 0", "other player", " players",
    "without", "trade partner", "endorsed", "first ", " oppose", " support",
    " vote", "council", "envoy", " muster", " army", "armies", "cavalry",
    "sally", " reach", "each ", "no longer", "instead", " pass", " fail",
    "condemn", "endorse", " domain", "standing", "besiege", " loan", "tithe",
    " recoup", "another player", "every ", "may perform", "targeting", " move ",
]
SEASON_RE = re.compile(r"([+-]?\d{2,})\s*(?:gold\s*)?in\s+(Fall|Winter|Spring|Summer)", re.I)
SCALE_RE  = re.compile(r"\+?(\d+)\s*(?:gold\s*)?(?:for each|per)\s+active\s+(\w+)\s+special", re.I)
CRAFT_RE  = re.compile(r"Craft\s*\+?\s*(\d+)", re.I)
FAITH_RE  = re.compile(r"Faith\s*\+?\s*(\d+)", re.I)
DOUBT_RE  = re.compile(r"Doubt\s*\+?\s*(\d+)", re.I)
UPKEEP_RE = re.compile(r"Upkeep\s*(-?\d{2,})", re.I)
INFL_RE   = re.compile(r"(?:Influence\s*([+-]\s?\d+))|(?:([+-]\s?\d+)\s*Influence)", re.I)
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
    lc2 = lc.replace("per turn", " ")     # "+1 Influence per turn" is flat, not conditional
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
        return finish("extort", to_int(EXTORT_RE.search(c).group(1)), set())
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

def parse_effects(raw):
    raw = strip_md(raw or "")
    if not raw or raw in ("-", "—"):
        return []
    return [a for a in (classify(cl) for cl in re.split(r"[;,]", raw)) if a]

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
        mreq = parse_mreq(v.get("mastery_req", ""))
        for g in mreq:
            for opt in g:
                if classify_req_token(opt, names, settle_names) == "external":
                    external.add(opt)
        records[name] = {
            "name": name, "type": v.get("type", "?"),
            "monument": bool(v.get("monument")),
            "innate_raw": strip_md(v.get("innate", "")),
            "mastery_raw": strip_md(v.get("mastery", "")),
            "mreq_raw": strip_md(v.get("mastery_req", "")),
            "efficient": strip_md(v.get("efficient", "")),
            "innate": innate, "mastery": mastery, "mreq": mreq,
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
                "upkeep": up,
                "build_time": d.get("build_time", ""),
                "requirement": strip_md(d.get("requirement", "")),
                "effect_raw": strip_md(d.get("empire_bonus", "")),
                "atoms": parse_effects(d.get("empire_bonus", "")),
            }
        return out

    infra = infra_records(ns.get("INFRASTRUCTURE", {}), "infra")
    wonders = infra_records(ns.get("WONDERS", {}), "wonder")
    retinues = ns.get("RETINUES", {})

    # ---- army source tokens: engine tags (curated) + unlocks derived from text ----
    ret_keys = set(retinues.keys())
    RET_NORM = {"Sergeants": "Sergeant", "Knight's Templar": "Knight Templar",
                "Knights Templar": "Knight Templar", "Man at Arms": "Man-at-Arms"}
    def norm_ret(x):
        x = x.strip()
        return RET_NORM.get(x, x if x in ret_keys else x)
    def derived_unlocks(text):
        t = strip_md(text)
        out = []
        if re.search(r"Unlocks?\s+Ranged\s+Weapons", t, re.I): out.append("ranged")
        if re.search(r"Unlocks?\s+Cavalry\s+Weapons", t, re.I): out.append("cavalry")
        m = re.search(r"Unlocks?\s+(.+?)\s+for\s+Muster", t, re.I)
        if m: out.append("retinue:" + norm_ret(m.group(1)))
        return out
    army_src = {}
    for name, v in N.items():
        e = v.get("engine") or {}
        inn = list(e.get("innate_tags", [])) + derived_unlocks(v.get("innate", ""))
        mas = list(e.get("mastery_tags", [])) + derived_unlocks(v.get("mastery", ""))
        if inn or mas:
            army_src[name] = {"innate": inn, "mastery": mas}

    glossary = {k: (strip_md(v)[:220]) for k, v in ns.get("GLOSSARY", {}).items()}
    for k, v in ns.get("MORALE_GLOSSARY", {}).items():
        glossary.setdefault(k, strip_md(v)[:220])
    equip = {"weapons": ns.get("WEAPONS", {}), "ranged": ns.get("RANGED", {}),
             "shields": ns.get("SHIELDS", {}), "armors": ns.get("ARMORS", {}),
             "retinues": retinues, "tiers": ns.get("TIERS", []),
             "endurance_regain": ns.get("ENDURANCE_REGAIN", 2),
             "army_max": ns.get("ARMY_MAX_RETINUES", 25)}
    return (records, sorted(natural_names), sorted(external), infra, wonders,
            army_src, equip, glossary)

# ---------- HTML ----------
MAPGEN_JS = ""

def render_html(**data):
    blob = json.dumps(data, ensure_ascii=False)
    return HTML_TEMPLATE.replace("/*__MAPGEN__*/", MAPGEN_JS).replace("/*__DATA__*/", blob)

def find_mapgen(explicit, data_path):
    """Locate gen.js + presets.js (CE/mapgen). Returns the concatenated JS or ''."""
    here = os.path.dirname(os.path.abspath(__file__))
    cands = [explicit] if explicit else []
    cands += [os.path.join(os.path.dirname(os.path.abspath(data_path)), "mapgen"),
              os.path.join(here, "..", "mapgen"), os.path.join(here, "mapgen"), here]
    for d in cands:
        if d and os.path.isfile(os.path.join(d, "gen.js")) and os.path.isfile(os.path.join(d, "presets.js")):
            js = open(os.path.join(d, "gen.js"), encoding="utf-8").read() + "\n" + \
                 open(os.path.join(d, "presets.js"), encoding="utf-8").read()
            return js.replace("</script", "<\\/script"), os.path.normpath(d)
    return "", None

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Renown — Settlement Board Emulator</title>
<style>
  :root{
    --bg:#0f1115; --panel:#161a21; --panel2:#1c222b; --line:#262d38;
    --ink:#e6eaf0; --dim:#8b95a3; --dim2:#5c6674;
    --income:#4caf50; --craft:#26c6da; --influence:#ab47bc; --order:#ffb300;
    --upkeep:#ef5350; --season:#8d6e63; --build:#5c6bc0; --battle:#78909c;
    --envoy:#ec407a; --other:#7a828e;
    --chip:#12161d; --barbg:#222937; --topbar:#0c0e12;
    --sel:#222937; --line2:#3a4453;
    --serif:Georgia,"Iowan Old Style",serif;
    --mono:"Iosevka","SF Mono",ui-monospace,"Cascadia Code",monospace;
    --radius:10px; --radius-sm:6px; --pill:999px;
  }
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--ink);
    font-family:var(--mono);font-size:13px;line-height:1.45}
  h1,h2,h3{font-family:var(--serif);font-weight:600;margin:0}
  .app{display:grid;grid-template-columns:300px 1fr 340px;height:100vh}
  @media(max-width:1100px){.app{grid-template-columns:1fr;height:auto}}
  .col{overflow-y:auto;padding:14px;border-right:1px solid var(--line);min-width:0}
  .col:last-child{border-right:none;border-left:1px solid var(--line)}
  .hd{display:flex;align-items:baseline;gap:8px;margin-bottom:10px}
  .hd h2{font-size:16px}.hd .v{color:var(--dim2);font-size:11px}
  input,select,button{font-family:inherit;font-size:12px;color:var(--ink);
    background:var(--panel2);border:1px solid var(--line);border-radius:var(--radius-sm);padding:6px 8px}
  input::placeholder{color:var(--dim2)} button{cursor:pointer} button:hover{border-color:var(--line2)}
  .search{width:100%;margin-bottom:8px}
  .tabs{display:flex;gap:4px;margin-bottom:8px}
  .tab{flex:1;text-align:center;padding:5px 4px;border:1px solid var(--line);border-radius:var(--radius-sm);
    background:var(--panel2);color:var(--dim);font-size:11px;cursor:pointer}
  .tab.on{color:var(--ink);border-color:var(--line2);background:var(--sel)}
  .filters{display:flex;flex-wrap:wrap;gap:4px;margin-bottom:8px}
  .chip{border:1px solid var(--line);border-radius:var(--pill);padding:2px 8px;font-size:11px;
    color:var(--dim);background:var(--panel2);cursor:pointer;user-select:none}
  .chip.on{color:var(--ink);border-color:var(--line2);background:var(--sel)}
  .typegroup{margin-bottom:6px}
  .catctl{display:flex;gap:6px;margin-bottom:6px}
  .typegroup>.th{color:var(--dim);font-size:11px;letter-spacing:.03em;padding:4px 2px;
    border-bottom:1px solid var(--line);position:sticky;top:-14px;background:var(--bg);z-index:1}
  .row{display:flex;align-items:center;gap:6px;padding:3px 2px}
  .row .nm{flex:1;cursor:pointer;overflow-wrap:anywhere}
  .row .nm:hover{color:var(--ink);text-decoration:underline}
  .row.mon .nm{color:var(--order)} .row.have .nm{color:var(--income)}
  .row .meta{color:var(--dim2);font-size:10px}
  .addbtn{width:24px;height:22px;padding:0;line-height:1}

  details.section{margin-bottom:14px;border:1px solid var(--line);border-radius:var(--radius);background:var(--panel)}
  details.section>summary{list-style:none;cursor:pointer;padding:8px 12px;display:flex;
    align-items:center;gap:8px;font-family:Georgia,serif;font-size:15px;border-bottom:1px solid var(--line)}
  details.section>summary::-webkit-details-marker{display:none}
  details.section>summary .cnt{color:var(--dim2);font-size:11px;font-family:inherit}
  details.section[open]>summary .caret::before{content:"▾"} .caret::before{content:"▸";color:var(--dim)}
  .sectionbody{padding:12px}
  .board{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:10px}
  .settbuild{display:flex;gap:6px;align-items:center;margin-bottom:10px;flex-wrap:wrap}
  .flash{color:var(--order);font-size:11px;opacity:0;transition:opacity .2s;margin-left:6px}
  .sgroup{border:1px dashed var(--line);border-radius:var(--radius);padding:8px;margin-bottom:10px}
  .sgroup.active{border-color:var(--income);border-style:solid}
  .sgroup-hd{display:flex;align-items:center;gap:10px;margin-bottom:8px;cursor:pointer;flex-wrap:wrap}
  .sgroup-hd .stitle{font-family:Georgia,serif;font-size:14px}
  .sgroup-hd .rm{font-size:11px}
  /* ward slots + solitaire piles (efficient riders stack on their host) */
  #board-pursuit.board{display:block}   /* settlements = full-width rows; wards tile inside */
  .wards{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:10px;align-items:start}
  .ward{border:1px solid var(--line);border-radius:var(--radius);padding:6px;background:var(--panel2);min-height:128px;display:flex;flex-direction:column}
  .ward-lbl{font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:var(--dim);margin:0 2px 5px;display:flex;justify-content:space-between;gap:6px}
  .ward.empty{border:2px dashed var(--line2);background:transparent;cursor:pointer}
  .ward.empty:hover{border-color:var(--income)}
  .ward.empty .emp{flex:1;display:flex;align-items:center;justify-content:center;color:var(--dim2);font-family:Georgia,serif;font-size:13px;font-style:italic}
  .ward.over{border-color:var(--upkeep);background:rgba(239,83,80,.10)}
  .ward.over .ward-lbl{color:var(--upkeep)}
  .pile{position:relative}
  .pc{position:relative}
  .pc.buried{height:34px}
  .pc.buried>.card{position:absolute;left:0;right:0;top:0;max-height:34px;overflow:hidden}
  .pile .pc+.pc>.card{box-shadow:0 -3px 6px rgba(0,0,0,.35)}
  .pc.buried:hover{z-index:19!important}
  .pc.buried:hover>.card{max-height:none;overflow:visible;outline:1px solid var(--line2);box-shadow:0 8px 22px rgba(0,0,0,.6)}

  .card{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:10px;
    border-left:4px solid var(--other);min-width:0;overflow-wrap:anywhere}
  .card h3{font-size:14px;display:flex;align-items:center;gap:6px;flex-wrap:wrap}
  .pcaret{color:var(--dim);width:10px}
  .acard.routed{border-left-color:var(--upkeep);background:rgba(239,83,80,.12)}
  .routebar{color:var(--bg);background:var(--upkeep);border-radius:var(--radius-sm);padding:2px 8px;font-size:11px;font-weight:600;margin-top:8px;display:inline-block}
  .card h3 .nm{overflow-wrap:anywhere}
  .card .sub{color:var(--dim);font-size:11px;margin:2px 0 6px}
  .qty{display:flex;align-items:center;gap:6px;margin-left:auto}
  .qty button{width:22px;height:20px;padding:0}
  .badge{font-size:10px;padding:1px 6px;border-radius:var(--pill);border:1px solid;white-space:nowrap}
  .badge.mon{color:var(--order);border-color:var(--order)}
  .badge.tier{color:var(--dim);border-color:var(--line)}
  .badge.earn{color:var(--income);border-color:var(--income)}
  .badge.noearn{color:var(--upkeep);border-color:var(--upkeep)}
  .badge.nomast{color:var(--dim2);border-color:var(--line)}

  .block{background:var(--panel2);border:1px solid var(--line);border-radius:var(--radius);padding:7px;margin-top:7px}
  .block.mastery{border-left:3px solid var(--dim2)}
  .block.mastery.on{border-left-color:var(--income)}
  .block.mastery.off{border-left-color:var(--upkeep)}
  .block .lbl{display:flex;align-items:center;gap:6px;color:var(--dim2);font-size:10px;
    letter-spacing:.06em;margin-bottom:5px;font-weight:600}
  .block .lbl .sp{flex:1}
  .atoms{display:flex;flex-wrap:wrap;gap:4px}
  .atom{font-size:11px;padding:1px 7px;border-radius:var(--radius-sm);border:1px solid;background:var(--chip);
    white-space:normal;overflow-wrap:anywhere;max-width:100%}
  .atom.cond{opacity:.6;border-style:dashed}
  .atom .s{font-size:9px;color:var(--season);margin-left:3px}
  .verb{color:var(--dim);font-size:11px;margin-top:5px;overflow-wrap:anywhere}
  .req{color:var(--dim);font-size:11px;margin-top:4px;overflow-wrap:anywhere}
  .miss{color:var(--upkeep);font-size:11px;margin-top:3px;overflow-wrap:anywhere}
  .badge.manual{color:var(--order);border-color:var(--order)}
  .ttab{font-size:11px;width:100%} .ttab td{vertical-align:top}
  .bcun{margin-top:5px;padding:5px;border:1px solid var(--line);border-radius:var(--radius-sm);background:var(--panel2)}
  .bcrow{display:flex;flex-wrap:wrap;gap:8px;align-items:center;font-size:12px}
  .ttab tr.broll td{background:rgba(255,179,0,.18);font-weight:700}
  .ttwrap{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:10px;margin-top:10px;align-items:start}
  .tsw{display:inline-block;width:11px;height:11px;border:1px solid #0005;border-radius:2px;margin-right:5px;vertical-align:-1px}
  .dpcell{text-align:center;font-size:12px;font-family:ui-monospace,monospace;padding:4px 6px;border:1px solid var(--line)}
  button:disabled{opacity:.45;cursor:not-allowed}
  .grip{cursor:grab;color:var(--dim2);font-size:12px;letter-spacing:-2px;padding:2px 5px 2px 0;touch-action:none;user-select:none;-webkit-user-select:none}
  .grip:hover{color:var(--ink)}
  body.dnd,body.dnd *{cursor:grabbing!important;user-select:none;-webkit-user-select:none}
  .dragging{opacity:.35}
  .dragghost{position:fixed;z-index:1000;pointer-events:none;background:var(--panel);border:1px solid var(--line2);border-radius:var(--radius);padding:5px 8px;box-shadow:0 8px 22px rgba(0,0,0,.5);font-family:Georgia,serif;font-size:12px;max-width:260px}
  .dragghost .gw{font-family:inherit;font-size:10px;margin-top:3px} .dragghost .gw.ok{color:var(--income)} .dragghost .gw.bad{color:var(--upkeep)}
  .drop-ok{outline:2px solid var(--income)!important;outline-offset:-2px}
  .drop-bad{outline:2px solid var(--upkeep)!important;outline-offset:-2px}
  .sgroup.unp-empty{display:none} body.dnd .sgroup.unp-empty{display:block;min-height:60px}
  .flagbox{border:1px solid var(--upkeep);background:rgba(239,83,80,.08);color:var(--upkeep);border-radius:var(--radius);padding:6px 10px;margin-bottom:10px;font-size:12px}
  .flagbox ul{margin:3px 0 0 16px;padding:0} .flagbox li{margin:1px 0}
  .ireq{font-size:11px;margin-top:3px;display:flex;gap:5px;align-items:baseline;flex-wrap:wrap}
  .ireq .ok{color:var(--income)} .ireq .no{color:var(--upkeep)} .ireq .mn{color:var(--order)}
  .ireq .why{color:var(--dim)}
  .card.illegal{background:rgba(239,83,80,.08)}
  .poladder{margin-top:6px;display:flex;flex-direction:column;gap:1px;font-size:11px}
  .poladder .pr{display:grid;grid-template-columns:22px 92px 1fr;gap:6px;padding:1px 4px;border-radius:var(--radius-sm);color:var(--dim2)}
  .poladder .pr.on.neg{color:var(--upkeep);background:rgba(239,83,80,.10)}
  .poladder .pr.on.pos{color:var(--income);background:rgba(102,187,106,.10)}
  .poladder .pr.cur{font-weight:700;outline:1px solid var(--line2)}
  .poladder .pr .v{text-align:right}
  .rm{color:var(--dim2);border:none;background:none;font-size:14px;cursor:pointer;margin-left:auto}
  .rm:hover{color:var(--upkeep)}
  .empty{color:var(--dim2);text-align:center;padding:24px 10px}

  .toolbar{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px}
  .toolbar label{display:flex;align-items:center;gap:4px}
  /* army */
  .acard{background:var(--panel);border:1px solid var(--line);border-left:4px solid var(--battle);
    border-radius:var(--radius);padding:10px;margin-bottom:8px;min-width:0;overflow-wrap:anywhere}
  .acard .top{display:flex;gap:6px;align-items:center;flex-wrap:wrap}
  .acard .top input.lab{flex:1;min-width:100px}
  .acard select,.acard input{font-size:11px;padding:4px 6px}
  .loadout{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:6px;margin-top:8px}
  .fld{display:flex;flex-direction:column;gap:2px}
  .fld label{color:var(--dim2);font-size:9px;letter-spacing:.05em}
  .fld select{width:100%}
  .fld select option.locked{color:var(--dim2)}
  .stats{display:flex;flex-wrap:wrap;gap:5px;margin-top:8px}
  .stat{background:var(--panel2);border:1px solid var(--line);border-radius:var(--radius-sm);padding:2px 7px;font-size:11px}
  .stat b{color:var(--ink);font-family:Georgia,serif}
  .stat .k{color:var(--dim2);font-size:9px;letter-spacing:.04em;margin-right:3px}
  .status{display:flex;gap:6px;margin-top:8px;flex-wrap:wrap}
  .stog{border:1px solid var(--line);border-radius:var(--pill);padding:2px 9px;font-size:11px;color:var(--dim);cursor:pointer;user-select:none}
  .stog.on{color:var(--bg);background:var(--upkeep);border-color:var(--upkeep)}
  .stog.blunder.on{background:var(--order);border-color:var(--order)}
  .endr{display:flex;align-items:center;gap:4px}
  .endr button{width:20px;height:20px;padding:0}
  .kwrow{display:flex;flex-wrap:wrap;gap:4px;margin-top:8px}
  .kw{font-size:10px;padding:1px 6px;border-radius:var(--radius-sm);border:1px solid var(--battle);color:var(--battle);background:var(--chip)}
  .kw.mod{border-color:var(--influence);color:var(--influence)}
  .unlocks .grp{margin:3px 0}
  .unlocks .grp .h{color:var(--dim2);font-size:10px;letter-spacing:.05em;margin-right:4px}
  /* summary */
  .tot{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:12px;margin-bottom:10px}
  .big{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:2px}
  .big .n{font-family:Georgia,serif;font-size:24px}
  .big .n.neg{color:var(--upkeep)} .big .n.pos{color:var(--income)}
  .kv{display:flex;justify-content:space-between;padding:2px 0;border-bottom:1px solid var(--line);gap:8px}
  .kv:last-child{border-bottom:none} .kv .k{color:var(--dim)} .kv .val{font-variant-numeric:tabular-nums;white-space:nowrap}
  .season-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin-top:8px}
  .scell{background:var(--panel2);border:1px solid var(--line);border-radius:var(--radius);padding:6px;text-align:center}
  .scell .sn{color:var(--dim);font-size:10px}.scell .sv{font-family:Georgia,serif;font-size:16px}
  .legend{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0}
  .legend .li{display:flex;align-items:center;gap:4px;font-size:10px;color:var(--dim)}
  .sw{width:10px;height:10px;border-radius:var(--radius-sm)}
  .bar{display:flex;height:8px;border-radius:var(--radius-sm);overflow:hidden;margin-top:6px;border:1px solid var(--line)}
  .bar>span{display:block}
  .treas{display:flex;align-items:center;gap:6px;margin:6px 0}
  .treas input{width:120px;font-family:Georgia,serif;font-size:16px}
  details.notes{margin-top:10px} summary{cursor:pointer}
  .note{color:var(--dim2);font-size:11px;line-height:1.45} .note b{color:var(--dim)}
  .set-grid{display:grid;grid-template-columns:1fr auto;gap:4px 8px;align-items:center;margin-top:6px}
  .stepper{display:flex;gap:4px;align-items:center} .stepper button{width:20px;height:20px;padding:0}
  .stepper .q{min-width:16px;text-align:center}
  .warn{color:#e6a23c;font-size:10px}
  /* inspector modal */
  .kw,.stat.click{cursor:pointer}
  .kw:hover{filter:brightness(1.3)}
  .modal{position:fixed;inset:0;background:rgba(0,0,0,.6);display:flex;align-items:center;
    justify-content:center;z-index:50;padding:16px}
  .modalcard{background:var(--panel);border:1px solid var(--line2);border-radius:var(--radius);max-width:440px;
    width:100%;max-height:80vh;overflow-y:auto;padding:16px;box-shadow:0 10px 40px rgba(0,0,0,.5)}
  .modalcard h3{font-size:18px;display:flex;align-items:center;gap:8px}
  .modalcard .close{margin-left:auto;background:none;border:none;color:var(--dim);font-size:18px;cursor:pointer}
  .modalcard .def{color:var(--ink);margin:8px 0;line-height:1.5}
  .modalcard .nodef{color:var(--dim2);font-style:italic}
  .modalcard .sgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(90px,1fr));gap:6px;margin:10px 0}
  .modalcard .sgrid .stat{cursor:default}
  .modalcard .lbl2{color:var(--dim2);font-size:10px;letter-spacing:.05em;margin:10px 0 4px}
  .modalcard .note{margin-top:8px}
  .lochips{display:flex;flex-wrap:wrap;gap:5px;margin-top:8px}
  .lochip{font-size:11px;padding:2px 8px;border-radius:var(--radius-sm);border:1px solid var(--battle);
    color:var(--battle);background:var(--chip);cursor:pointer}
  .lochip .k{color:var(--dim2);font-size:9px;margin-right:3px}
  .lochip:hover{filter:brightness(1.3)}
  /* top bar / views / players */
  .topbar{display:flex;align-items:center;gap:16px;padding:6px 12px;border-bottom:1px solid var(--line);background:var(--topbar);position:sticky;top:0;z-index:20;flex-wrap:wrap}
  .views{display:flex;gap:4px}
  .vtab{padding:6px 12px;border:1px solid var(--line);border-radius:var(--radius);background:var(--panel2);color:var(--dim);cursor:pointer;font-family:Georgia,serif}
  .vtab.on{color:var(--ink);border-color:var(--line2);background:var(--sel)}
  .players{display:flex;gap:6px;align-items:center;flex-wrap:wrap}
  .pchip{display:flex;align-items:center;gap:5px;padding:3px 8px;border:1px solid var(--line);border-radius:var(--pill);cursor:pointer;font-size:12px;color:var(--dim)}
  .pchip.on{color:var(--ink);border-color:var(--line2);background:var(--sel)}
  .pdot{width:10px;height:10px;border-radius:50%}
  .app{height:calc(100vh - 47px)}
  @media(max-width:1100px){.app{height:auto}}
  .viewpane{height:calc(100vh - 47px)}
  .dtable{width:100%;border-collapse:collapse;font-size:13px;max-width:1000px}
  .dtable th,.dtable td{border:1px solid var(--line);padding:6px 9px;text-align:left}
  .dtable th{color:var(--dim);font-weight:600;font-family:Georgia,serif}
  .edb .edn{font-size:18px;font-weight:700;min-width:22px;text-align:center}
  .edb button{padding:1px 6px;font-size:11px}
  .dtable td.num{text-align:right;font-variant-numeric:tabular-nums}
  .goldbtns{display:flex;gap:4px;margin-top:6px}
  .goldbtns button{flex:1;padding:4px 2px}
  .mtoolbar{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:10px}
  .hexwrap{overflow:auto;border:1px solid var(--line);border-radius:var(--radius);background:var(--topbar);max-height:calc(100vh - 160px)}
  .rdom select{font-size:12px;padding:4px 6px}
  .sboard{max-width:1000px}
  .dtrack{display:flex;align-items:stretch;gap:6px;margin-bottom:5px}
  .dtrack .dname{width:78px;font-family:Georgia,serif;color:var(--dim);display:flex;align-items:center;font-size:13px}
  .dtrack .cells{display:grid;grid-template-columns:repeat(11,1fr);gap:2px;flex:1}
  .dcell{min-height:34px;border:1px solid var(--line);border-radius:var(--radius-sm);display:flex;flex-direction:column;align-items:center;padding-top:2px;font-size:9px;color:var(--dim2)}
  .dcell.b-untested{background:var(--chip)}
  .dcell.b-rising{background:rgba(38,198,218,.09)}
  .dcell.b-established{background:rgba(255,179,0,.11)}
  .dcell.b-sovereign{background:rgba(76,175,80,.13)}
  .dcell .dots{display:flex;flex-wrap:wrap;gap:2px;justify-content:center;margin-top:1px}
  .pdotsm{width:15px;height:15px;border-radius:50%;font-size:9px;color:#0c0e12;display:inline-flex;align-items:center;justify-content:center;font-weight:700;border:1px solid #000}
  .bandrow{display:flex;gap:14px;margin:2px 0 4px 84px;font-size:10px;color:var(--dim2)}
  .dctrls{display:flex;gap:12px;flex-wrap:wrap;margin:0 0 10px 84px}
  .dctrl{display:flex;align-items:center;gap:3px}
  .dctrl button{width:18px;height:18px;padding:0;line-height:1}
  .dctrl .dcv{min-width:14px;text-align:center;font-variant-numeric:tabular-nums}
  .budget{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin:6px 0 0 84px}
  .bchip{display:flex;align-items:center;gap:4px;font-size:11px;color:var(--dim);border:1px solid var(--line);border-radius:var(--pill);padding:2px 8px}
  .bchip.over{color:var(--upkeep);border-color:var(--upkeep)}
  .ptable{width:100%;font-size:12px}
  .ptable th,.ptable td{padding:3px 6px;vertical-align:middle}
  .ptable td .atoms{gap:3px}
  .ptable td .atom{font-size:10px;padding:0 5px}
  .ptable select{font-size:11px;padding:2px 4px}
  .ptable .pcaret{width:9px;display:inline-block}
</style>
</head>
<body>
<div class="topbar">
  <div class="views" id="viewTabs">
    <div class="vtab on" data-v="board">Board</div>
    <div class="vtab" data-v="dash">Dashboards</div>
    <div class="vtab" data-v="renown">Renown &amp; Domains</div>
    <div class="vtab" data-v="map">Map</div>
    <div class="vtab" data-v="battle" id="vtabBattle" style="display:none">Battle</div>
  </div>
  <div class="players" id="playerBar"></div>
  <details id="modBox" style="margin-left:auto;position:relative"><summary class="note" style="cursor:pointer">modules</summary>
    <div style="position:absolute;right:0;z-index:20;background:var(--panel);border:1px solid var(--line);padding:8px;min-width:190px">
      <label style="display:block"><input type="checkbox" class="modcb" data-m="diplomacy"> Diplomacy (Dashboards)</label>
      <label style="display:block"><input type="checkbox" class="modcb" data-m="battle"> Battle tab</label>
    </div></details>
  <select id="themeSel" title="visual style">
    <option value="ink">Ink (dark)</option>
    <option value="parchment">Parchment</option>
    <option value="midnight">Midnight</option>
    <option value="slate">Slate (light)</option>
    <option value="royal">Royal</option>
  </select>
  <select id="shapeSel" title="shape">
    <option value="rounded">Rounded</option>
    <option value="soft">Soft</option>
    <option value="sharp">Sharp</option>
    <option value="square">Square</option>
  </select>
</div>
<div class="app" id="appBoard">
  <!-- CATALOG -->
  <div class="col" id="catalog">
    <div class="hd"><h2>Catalog</h2><span class="v" id="ver"></span></div>
    <div class="tabs" id="tabs">
      <div class="tab on" data-k="pursuit">Pursuits</div>
      <div class="tab" data-k="infra">Infra</div>
      <div class="tab" data-k="wonder">Wonders</div>
    </div>
    <input class="search" id="search" placeholder="filter…">
    <div class="filters" id="typeFilters"></div>
    <div id="list"></div>
  </div>

  <!-- BOARD -->
  <div class="col" id="boardcol">
    <div class="hd"><h2>Board</h2><span class="v" id="poolcount"></span></div>
    <div class="toolbar">
      <button id="clear">clear all</button>
      <button id="export">export</button>
      <button id="import">import</button>
      <input type="file" id="file" accept="application/json" style="display:none">
      <label><input type="checkbox" id="hideCombat"> hide combat/other</label>
    </div>

    <details class="section" open id="sec-pursuit"><summary><span class="caret"></span>Pursuits <span class="cnt" id="c-pursuit"></span></summary>
      <div class="sectionbody"><div class="board" id="board-pursuit"></div><div class="empty" id="e-pursuit">Add pursuits from the catalog.</div></div></details>

    <details class="section" open id="sec-infra"><summary><span class="caret"></span>Infrastructure <span class="cnt" id="c-infra"></span></summary>
      <div class="sectionbody"><div class="board" id="board-infra"></div><div class="empty" id="e-infra">Empire-wide. Adds upkeep; satisfies infra mastery reqs.</div></div></details>

    <details class="section" open id="sec-wonder"><summary><span class="caret"></span>Wonders <span class="cnt" id="c-wonder"></span></summary>
      <div class="sectionbody"><div class="board" id="board-wonder"></div><div class="empty" id="e-wonder">One per game each.</div></div></details>

    <details class="section" open id="sec-army"><summary><span class="caret"></span>Army <span class="cnt" id="c-army"></span></summary>
      <div class="sectionbody">
        <div class="block" id="armyUnlocks" style="margin-top:0"></div>
        <div id="armyList"></div>
        <button id="addArmy" style="margin-top:8px">+ add army</button>
        <div class="kv" style="margin-top:8px"><span class="k">Army cost (Σ, gross)</span><span class="val" id="armyTotal">0</span></div>
      </div></details>
  </div>

  <!-- SUMMARY -->
  <div class="col" id="summary">
    <div class="hd"><h2>Totals</h2><span class="v">flat atoms only</span></div>

    <div class="tot">
      <div class="big"><span class="k">Net gold / turn</span><span class="n" id="netgold">0</span></div>
      <div class="note" id="netnote"></div>
    </div>

    <div class="tot">
      <h3 style="font-size:13px">Treasury</h3>
      <div class="treas">
        <span class="k">gold</span>
        <input type="number" id="treasury" step="100" value="0">
        <button id="endturn">end turn ▸</button>
      </div>
      <div class="goldbtns">
        <button data-gold="-2000">−2k</button><button data-gold="-500">−500</button>
        <button data-gold="500">+500</button><button data-gold="2000">+2k</button>
      </div>
      <div class="kv" style="margin-top:6px"><span class="k">turn</span><span class="val" id="turn">0</span></div>
      <label class="note" style="display:flex;gap:6px;align-items:center;margin-top:4px">
        <input type="checkbox" id="autoNet" checked> auto-apply net gold on end turn</label>
    </div>

    <div class="tot">
      <h3 style="font-size:13px">Public Order</h3>
      <div class="treas">
        <button id="poMinus">−</button>
        <span class="n" id="poVal" style="font-size:22px;min-width:36px;text-align:center">0</span>
        <button id="poPlus">+</button>
        <span class="note" id="poBand"></span>
      </div>
      <div class="note" id="poEffect"></div>
      <div class="poladder" id="poLadder"></div>
    </div>

    <div class="tot">
      <div class="kv"><span class="k">Gold income (flat)</span><span class="val" id="t_gold">0</span></div>
      <div class="kv"><span class="k">Scaling gold</span><span class="val" id="t_scale">0</span></div>
      <div class="kv"><span class="k">Upkeep — infra/wonder</span><span class="val" id="t_upkeep">0</span></div>
      <div class="kv"><span class="k">Upkeep reductions (pool)</span><span class="val" id="t_reduce">0</span></div>
      <div class="kv"><span class="k">Upkeep — army (net)</span><span class="val" id="t_army">0</span></div>
      <div class="kv"><span class="k">Craft X</span><span class="val" id="t_craft">0</span></div>
      <div class="kv"><span class="k">→ trade income / agreement</span><span class="val" id="t_trade">0</span></div>
      <div class="kv"><span class="k">Influence (flat)</span><span class="val" id="t_infl">0</span></div>
      <div class="kv"><span class="k">Faith − Doubt (PO/turn)</span><span class="val" id="t_po">0</span></div>
    </div>

    <div class="tot">
      <h3 style="font-size:13px">Net gold by season</h3>
      <div class="season-grid" id="seasons"></div>
    </div>

    <div class="tot">
      <h3 style="font-size:13px">Settlements (ward budget)</h3>
      <div class="set-grid" id="setGrid"></div>
      <div class="kv" style="margin-top:6px"><span class="k">Wards used / avail</span><span class="val" id="wards">0 / 0</span></div>
      <div class="bar" id="wardbar"></div>
      <div class="kv"><span class="k">Winter tax</span><span class="val" id="tax">0</span></div>
    </div>

    <div class="tot">
      <h3 style="font-size:13px">Effects by phase</h3>
      <div class="legend" id="legend"></div>
    </div>

    <details class="notes"><summary class="note">parser warnings</summary>
      <div class="note" id="assump"></div></details>

    <details class="tot" id="srvBox" style="margin-top:10px">
      <summary style="cursor:pointer;display:flex;align-items:center;gap:6px">
        <span id="srvDot" style="width:9px;height:9px;border-radius:50%;background:var(--dim2);display:inline-block"></span>
        <span class="note" id="srvStat">local cache (no server)</span>
      </summary>
      <input id="srvToken" type="password" placeholder="access token (only if server requires one)" style="width:100%;margin-top:8px">
      <div style="display:flex;gap:6px;margin-top:6px;flex-wrap:wrap">
        <input id="buildName" placeholder="build name" style="flex:1;min-width:90px">
        <button id="buildSave">save</button>
        <button id="buildSnap" title="save a timestamped snapshot">snapshot</button>
      </div>
      <div style="display:flex;gap:6px;margin-top:6px;flex-wrap:wrap">
        <select id="buildList" style="flex:1;min-width:90px"><option value="">— saved builds —</option></select>
        <button id="buildLoad">load</button>
        <button id="buildDel">del</button>
      </div>
    </details>
  </div>
</div>

<div id="viewDash" class="viewpane" style="display:none"></div>
<div id="viewRenown" class="viewpane" style="display:none"></div>
<div id="viewMap" class="viewpane" style="display:none"></div>
<div id="viewBattle" class="viewpane" style="display:none"></div>

<div id="inspect" class="modal" style="display:none"><div class="modalcard" id="inspectCard"></div></div>
<script>/*__MAPGEN__*/</script>
<script>
const DATA = /*__DATA__*/;
const R = DATA.records, INFRA = DATA.infra, WON = DATA.wonders;
const EQ = DATA.equip, ARMYSRC = DATA.armySrc, GLOSS = DATA.glossary || {};
const TIER_RANK = {Crude:0,Cast:1,Wrought:2,Forged:3,Crafted:4};
const ARMOR_TAG = {Gambeson:"Gambeson",Leather:"Leather",Chainmail:"Chainmail",FullPlate:"Full Plate"};
const NAMES = Object.keys(R).sort();
const NATURAL = new Set(DATA.naturalNames);
const PHASE = {gold:"income",scale:"income",extort:"income",recoup:"income",tax:"income",
  craft:"craft",influence:"influence",faith:"order",doubt:"order",upkeep:"upkeep",
  build_timer:"build",siege_timer:"battle",speed:"battle",combat:"battle",envoy:"envoy",
  natural:"other",other:"other"};
const PHASE_COLOR={income:"--income",craft:"--craft",influence:"--influence",order:"--order",
  upkeep:"--upkeep",build:"--build",battle:"--battle",envoy:"--envoy",season:"--season",other:"--other"};
const PHASE_LABEL={income:"Income / Extort",craft:"Craft → Trade",influence:"Influence",
  order:"Public Order",upkeep:"Upkeep",build:"Build timers",battle:"Battle / siege",
  envoy:"Council / Envoy",season:"Seasonal",other:"Other"};
const SEASONS=["Spring","Summer","Fall","Winter"];
const DOMAINS=DATA.domains||["Industry","Prowess","Piety","Cunning"];
const STANDINGS=DATA.standings||["Rising","Established","Sovereign"];
const DBOARD=DATA.domainBoard||{};
const PO=DATA.publicOrder||{};
const ERAS=DATA.eras||{};
const EDICTS=DATA.edicts||{};
const STAND_THRESH={Rising:3,Established:6,Sovereign:10};
const PLAYER_COLORS=["#4caf50","#ef5350","#42a5f5","#ffb300","#ab47bc","#26c6da","#ec407a"];
const THEMES={
  ink:{},
  parchment:{"--bg":"#efe7d6","--panel":"#f7f0dd","--panel2":"#efe6cd","--line":"#d9cba6","--line2":"#c3b48f","--ink":"#2c2114","--dim":"#6b5c43","--dim2":"#9c8b6a","--chip":"#efe6cd","--barbg":"#d9cba6","--topbar":"#e7dcc2","--sel":"#e3d7b8","--income":"#2e7d32","--craft":"#00838f","--influence":"#6a1b9a","--order":"#b8860b","--upkeep":"#c62828","--season":"#6d4c41","--build":"#3949ab","--battle":"#546e7a","--envoy":"#ad1457","--other":"#7a6f5a","--serif":"'Iowan Old Style',Georgia,serif"},
  midnight:{"--bg":"#000000","--panel":"#0b0b0d","--panel2":"#131318","--line":"#2a2a33","--line2":"#3a3a45","--ink":"#f5f5f7","--dim":"#a7a7b2","--dim2":"#6c6c78","--chip":"#0f0f14","--barbg":"#20202a","--topbar":"#000000","--sel":"#1a1a22","--income":"#39d353","--craft":"#22d3ee","--influence":"#c084fc","--order":"#fbbf24","--upkeep":"#f87171","--season":"#a1887f","--build":"#818cf8","--battle":"#94a3b8","--envoy":"#f472b6","--other":"#8a8a96"},
  slate:{"--bg":"#eef1f5","--panel":"#ffffff","--panel2":"#f3f5f9","--line":"#d6dbe3","--line2":"#c3ccd8","--ink":"#1f2430","--dim":"#5b6572","--dim2":"#93a0af","--chip":"#f3f5f9","--barbg":"#dfe4ec","--topbar":"#ffffff","--sel":"#e4e9f1","--income":"#2e7d32","--craft":"#0277bd","--influence":"#6a1b9a","--order":"#c77700","--upkeep":"#c62828","--season":"#795548","--build":"#3949ab","--battle":"#607d8b","--envoy":"#c2185b","--other":"#78889a","--serif":"'Iowan Old Style',Georgia,serif","--mono":"ui-monospace,'SF Mono',monospace"},
  royal:{"--bg":"#0c1024","--panel":"#141a38","--panel2":"#1b2450","--line":"#2a356b","--line2":"#37456f","--ink":"#eef1ff","--dim":"#9aa6d6","--dim2":"#5b6aa0","--chip":"#101632","--barbg":"#222c5e","--topbar":"#0a0e20","--sel":"#202a5a","--income":"#5bd6a0","--craft":"#5cc8ff","--influence":"#c9a0ff","--order":"#ffd166","--upkeep":"#ff7a85","--season":"#b0885f","--build":"#8aa0ff","--battle":"#8ea2c8","--envoy":"#ff8ac0","--other":"#8f9bc0"}
};
const THEME_VARS=["--bg","--panel","--panel2","--line","--line2","--ink","--dim","--dim2","--income","--craft","--influence","--order","--upkeep","--season","--build","--battle","--envoy","--other","--chip","--barbg","--topbar","--sel","--serif","--mono"];
function applyTheme(name){
  const root=document.documentElement.style;THEME_VARS.forEach(v=>root.removeProperty(v));
  const t=THEMES[name]||{};Object.keys(t).forEach(v=>root.setProperty(v,t[v]));
}
const SKINS={
  rounded:{"--radius":"10px","--radius-sm":"6px","--pill":"999px"},
  soft:{"--radius":"6px","--radius-sm":"4px","--pill":"6px"},
  sharp:{"--radius":"2px","--radius-sm":"2px","--pill":"2px"},
  square:{"--radius":"0px","--radius-sm":"0px","--pill":"0px"}
};
const SKIN_VARS=["--radius","--radius-sm","--pill"];
function applySkin(name){
  const root=document.documentElement.style;SKIN_VARS.forEach(v=>root.removeProperty(v));
  const t=SKINS[name]||SKINS.rounded;Object.keys(t).forEach(v=>root.setProperty(v,t[v]));
}

// ---- state: multiplayer dashboard ----
function startDoms(){return (D&&D.startDomains)?D.startDomains:{Industry:1,Prowess:1,Piety:1,Cunning:1};}
// every game starts with 1 Hamlet, 1 Village, 1 Town — the Town is the capital
function startSettlements(){return [{id:1,tier:"Hamlet"},{id:2,tier:"Village"},{id:3,tier:"Town",capital:true}];}
function newBoard(){return {placed:[],settlements:startSettlements(),infra:{},wonders:{},armies:[],
  treasury:0,turn:0,autoNet:true,expanded:[],po:0,domains:Object.assign({},startDoms()),edicts:{},edictLog:{},edictTimers:{}};}
function newPlayer(i){return {id:i,name:"Player "+i,color:PLAYER_COLORS[(i-1)%PLAYER_COLORS.length],board:newBoard()};}
let D={players:[],active:0,view:"board",renown:1,theme:"parchment",
       startDomains:{Industry:1,Prowess:1,Piety:1,Cunning:1},
       map:{seed:"",cols:16,rows:12,markers:[]}};
D.players=[newPlayer(1)];
let S=null;                              // alias to active player's board
let tab="pursuit", activeTypes=new Set(), aid=1, pid=1, sid=1, activeSid=null, catOpen=new Set(), mid=1, mtool="Army";

try{const d=JSON.parse(localStorage.getItem("renown_dash")||"null");if(d&&d.players)D=d;}catch(e){}
// migrate single-board board3 -> player 1
try{
  if(D.players.length===1 && !D.players[0].board.placed.length){
    const old=JSON.parse(localStorage.getItem("renown_board3")||"null");
    if(old){D.players[0].board=Object.assign(newBoard(),old);}
  }
}catch(e){}
function normalizeD(){
  D.startDomains=D.startDomains||{Industry:1,Prowess:1,Piety:1,Cunning:1};
  D.theme=D.theme||"parchment"; D.shape=D.shape||"sharp"; D.pursuitView=D.pursuitView||"cards";
  D.players=(D.players&&D.players.length)?D.players:[newPlayer(1)];
  D.players.forEach(p=>{p.board=Object.assign(newBoard(),p.board);
    const dm=p.board.domains||{},nd={};
    Object.keys(dm).forEach(k=>{const v=dm[k];nd[k]=typeof v==="number"?v:(STAND_THRESH[v]||0);});
    p.board.domains=nd; p.board.edicts=p.board.edicts||{};
    p.board.edictLog=p.board.edictLog||{}; p.board.edictTimers=p.board.edictTimers||{};
    // migrate legacy status dropdown: "Complete" -> one logged entry
    Object.keys(p.board.edicts).forEach(k=>{if(p.board.edicts[k]==="Complete"&&!(p.board.edictLog[k]||[]).length)p.board.edictLog[k]=[""];});
    p.board.edicts={};});
  if(typeof D.renown!=="number")D.renown=1;
  if(D.active>=D.players.length)D.active=0;
  D.map=D.map||{seed:"",cols:16,rows:12,markers:[]}; D.map.cells=D.map.cells||{};
}
normalizeD();

function activeBoard(){return D.players[D.active].board;}
function reindex(){
  S=activeBoard();
  aid=1;pid=1;sid=1;
  S.armies=S.armies||[];S.placed=S.placed||[];S.settlements=S.settlements||[];
  S.armies.forEach(a=>{if(a.id>=aid)aid=a.id+1;});
  S.placed.forEach(p=>{if(p.id>=pid)pid=p.id+1;});
  S.settlements.forEach(s=>{if(s.id>=sid)sid=s.id+1;});
  const cp=S.settlements.find(x=>x.capital);activeSid=cp?cp.id:(S.settlements[0]?S.settlements[0].id:null);
}
(D.map.markers||[]).forEach(m=>{if(m.id>=mid)mid=m.id+1;});
reindex();

let PC={};                              // name -> count (derived, active board)
function recomputePC(){PC={};S.placed.forEach(p=>PC[p.name]=(PC[p.name]||0)+1);}
function withBoard(b,fn){const pS=S,pPC=PC;S=b;recomputePC();const r=fn();S=pS;PC=pPC;return r;}

// ---- persistence: server API (same-origin) with localStorage fallback ----
const API={online:null};
let TOKEN="";try{TOKEN=localStorage.getItem("renown_token")||"";}catch(e){}
async function apiFetch(method,path,body){
  try{
    const h={};if(body!==undefined)h["Content-Type"]="application/json";if(TOKEN)h["X-Renown-Token"]=TOKEN;
    const r=await fetch(path,{method,headers:h,body:body!==undefined?JSON.stringify(body):undefined});
    if(r.status===401){setOnline(false);const t=document.getElementById("srvStat");if(t)t.textContent="unauthorized — check access token";return null;}
    if(!r.ok)throw 0;
    setOnline(true);
    const ct=r.headers.get("content-type")||"";
    return ct.includes("json")?await r.json():await r.text();
  }catch(e){setOnline(false);return null;}
}
function setOnline(ok){if(API.online===ok)return;API.online=ok;
  const el=document.getElementById("srvDot");if(el){el.style.background=ok?cvar("--income"):cvar("--dim2");}
  const t=document.getElementById("srvStat");if(t)t.textContent=ok?"server connected":"local cache (no server)";}
// ---- multi-client sync ----
// State splits into parts: "shared" (everything but per-browser UI keys + roster) and
// "board:<id>" per player. Only changed parts are written, each against the version it
// was based on; a stale write gets 409 and is 3-way merged. Polling pulls others' edits.
const LOCAL_KEYS=new Set(["active","view","theme","shape","pursuitView"]);
const POLL_MS=2500;
const SYNC={ready:false,rev:0,base:{},ver:{},pushing:false,dirty:false};
function clone(o){return o===undefined?undefined:JSON.parse(JSON.stringify(o));}
function jeq(a,b){return JSON.stringify(a)===JSON.stringify(b);}
function isObj(o){return o!==null&&typeof o==="object"&&!Array.isArray(o);}
// 3-way merge: keep local edits, take remote edits, numeric fields combine deltas
function merge3(b,l,r){
  if(jeq(l,b))return clone(r);
  if(jeq(r,b))return clone(l);
  if(isObj(l)&&isObj(r)){const out={},bb=isObj(b)?b:{};
    new Set([...Object.keys(l),...Object.keys(r),...Object.keys(bb)]).forEach(k=>{
      const v=merge3(bb[k],l[k],r[k]);if(v!==undefined)out[k]=v;});return out;}
  if(typeof l==="number"&&typeof r==="number"&&typeof b==="number")return r+(l-b);
  return clone(l);
}
function splitD(){
  const parts={},shared={roster:{}};
  Object.keys(D).forEach(k=>{if(!LOCAL_KEYS.has(k)&&k!=="players")shared[k]=D[k];});
  D.players.forEach(p=>{shared.roster[String(p.id)]={name:p.name,color:p.color};parts["board:"+p.id]=p.board;});
  parts.shared=shared;return clone(parts);
}
function joinD(parts){
  const act=(D.players[D.active]||{}).id,sh=parts.shared||{};
  Object.keys(D).forEach(k=>{if(!LOCAL_KEYS.has(k))delete D[k];});
  Object.keys(sh).forEach(k=>{if(k!=="roster")D[k]=clone(sh[k]);});
  const ids=Object.keys(sh.roster||{}).sort((a,b)=>(+a)-(+b));
  D.players=ids.map(id=>({id:isNaN(+id)?id:+id,name:sh.roster[id].name,color:sh.roster[id].color,
    board:clone(parts["board:"+id])||newBoard()}));
  normalizeD();
  const ix=D.players.findIndex(p=>p.id===act);D.active=ix>=0?ix:Math.min(D.active||0,D.players.length-1);
}
async function apiRaw(method,path,body){
  try{
    const h={};if(body!==undefined)h["Content-Type"]="application/json";if(TOKEN)h["X-Renown-Token"]=TOKEN;
    const r=await fetch(path,{method,headers:h,body:body!==undefined?JSON.stringify(body):undefined});
    if(r.status===401){setOnline(false);const t=document.getElementById("srvStat");if(t)t.textContent="unauthorized — check access token";return null;}
    setOnline(true);
    return {status:r.status,json:await r.json().catch(()=>null)};
  }catch(e){setOnline(false);return null;}
}
let _saveT=null;
function save(){
  try{localStorage.setItem("renown_dash",JSON.stringify(D));}catch(e){}
  clearTimeout(_saveT);_saveT=setTimeout(push,400);
}
async function push(){
  if(!SYNC.ready)return;
  if(SYNC.pushing){SYNC.dirty=true;return;}
  SYNC.pushing=true;SYNC.dirty=false;
  try{
    for(let attempt=0;attempt<5;attempt++){
      const parts=splitD();let conflict=false;
      const keys=new Set([...Object.keys(parts),...Object.keys(SYNC.base)]);
      for(const k of keys){
        const del=!(k in parts);
        if(!del&&jeq(parts[k],SYNC.base[k]))continue;
        const res=del?await apiRaw("DELETE","/api/part/"+encodeURIComponent(k),{base:SYNC.ver[k]||0})
                     :await apiRaw("PUT","/api/part/"+encodeURIComponent(k),{data:parts[k],base:SYNC.ver[k]||0});
        if(!res)return;                                   // offline: localStorage still holds it
        if(res.status===200){
          if(del){delete SYNC.base[k];delete SYNC.ver[k];}
          else{SYNC.base[k]=parts[k];SYNC.ver[k]=res.json.version;}
        }else if(res.status===409){                       // someone wrote first: merge, retry
          const srv=res.json.data===null?undefined:res.json.data;
          const merged=merge3(SYNC.base[k],del?undefined:parts[k],srv);
          SYNC.base[k]=srv;SYNC.ver[k]=res.json.version;
          if(srv===undefined){delete SYNC.base[k];delete SYNC.ver[k];}
          const cur=splitD();if(merged===undefined)delete cur[k];else cur[k]=merged;
          joinD(cur);conflict=true;
        }
      }
      if(!conflict)break;
      reindex();render();
    }
  }finally{SYNC.pushing=false;if(SYNC.dirty)push();}
}
function editing(){const a=document.activeElement;
  return a&&(a.tagName==="TEXTAREA"||a.tagName==="SELECT"||(a.tagName==="INPUT"&&!["button","checkbox","radio","color","file"].includes(a.type)));}
async function poll(){
  if(!SYNC.ready||SYNC.pushing||editing())return;
  const res=await apiRaw("GET","/api/state?since="+SYNC.rev);
  if(!res||res.status!==200||!res.json||!res.json.changed)return;
  if(SYNC.pushing||editing())return;                  // user acted while request was in flight
  const j=res.json,cur=splitD();let touched=false;
  Object.keys(j.parts).forEach(k=>{const srv=j.parts[k];
    if(SYNC.ver[k]===srv.version)return;
    const m=merge3(SYNC.base[k],cur[k],srv.data);
    SYNC.base[k]=clone(srv.data);SYNC.ver[k]=srv.version;
    if(!jeq(m,cur[k])){cur[k]=m;touched=true;}});
  Object.keys(SYNC.base).forEach(k=>{if(!j.keys.includes(k)){          // removed remotely
    const unchanged=jeq(cur[k],SYNC.base[k]);delete SYNC.base[k];delete SYNC.ver[k];
    if(unchanged&&k in cur){delete cur[k];touched=true;}}});
  SYNC.rev=j.rev;
  if(touched){joinD(cur);reindex();render();renderList();}
  if(!jeq(splitD(),SYNC.base))save();
}
function cvar(v){return getComputedStyle(document.documentElement).getPropertyValue(v).trim();}
function fmt(n){return (n>0?"+":"")+Math.round(n).toLocaleString();}
function cap(s){return s.charAt(0).toUpperCase()+s.slice(1);}

// ---- settlement / ward helpers ----
function settMeta(sid){const s=S.settlements.find(x=>x.id===sid);return s?DATA.settlements[s.tier]:null;}
function settTier(sid){const s=S.settlements.find(x=>x.id===sid);return s?s.tier:null;}
function occupants(sid){return S.placed.filter(p=>p.sid===sid);}
function hamletOK(name){return R[name].type==="Husbandry"||name==="Arable Land";}
// efficient forms CHAINS not branches: each pursuit hosts at most ONE efficient rider.
// exemptionsOf(occ): set of occupant ids that ride free (one rider per source), for an explicit occupant list.
function exemptionsOf(occ){
  const present=new Set(occ.map(o=>o.name));
  const bySource={};
  occ.forEach(o=>{const eff=R[o.name].efficient; if(eff&&present.has(eff))(bySource[eff]=bySource[eff]||[]).push(o);});
  const free=new Set();
  Object.keys(bySource).forEach(src=>{const rs=bySource[src].slice().sort((a,b)=>(b.ride||0)-(a.ride||0)||a.id-b.id);free.add(rs[0].id);});
  return free;
}
function wardExemptions(sid){ return exemptionsOf(occupants(sid)); }
function isFreeRider(p){ return p.sid!=null && wardExemptions(p.sid).has(p.id); }
function wardUse(sid){ // {cap, used, free, typeBad}
  const meta=settMeta(sid), cap=meta?meta.wards:0, occ=occupants(sid), tier=settTier(sid);
  const exempt=exemptionsOf(occ);
  let typeBad=false; occ.forEach(p=>{ if(tier==="Hamlet"&&!hamletOK(p.name))typeBad=true; });
  const used=occ.length-exempt.size;
  return {cap, used, free:cap-used, typeBad};
}
// can pursuit `name` be placed into settlement sid?  simulate the resulting ward count,
// so adding a PARENT later (which lets an existing tile ride it) is allowed even when full.
function canPlace(name, sid){
  if(sid==null)return {ok:true};
  const tier=settTier(sid);
  if(tier==="Hamlet"&&!hamletOK(name))return {ok:false,why:"Hamlet holds Husbandry / Arable Land only"};
  const meta=settMeta(sid), cap=meta?meta.wards:0;
  const sim=occupants(sid).concat([{id:1e9,name}]);   // hypothetical (high id → existing riders keep their slot)
  const exempt=exemptionsOf(sim);
  const used=sim.length-exempt.size;
  if(used<=cap)return {ok:true, rider:exempt.has(1e9)};
  return {ok:false, why:"no free ward slot (efficient slot taken — chains, can't branch)"};
}

// ---- uniqueness + tier progression ----
const TIER_CHAIN=["Village","Town","City","Metropolis"];
function capitalSett(){return S.settlements.find(s=>s.capital)||null;}
function setCapital(id){S.settlements.forEach(s=>{s.capital=(s.id===id);});}
// ---- era / legality flags (ERAS caps; SETTLEMENTS notes) ----
function isCityPlus(t){return TIER_CHAIN.indexOf(t)>=TIER_CHAIN.indexOf("City");}
function eraCap(k){const E=ERAS[currentEra()]||{};return typeof E[k]==="number"?E[k]:null;}
function cityCount(exceptId){return S.settlements.filter(s=>isCityPlus(s.tier)&&s.id!==exceptId).length;}
// can a settlement (id, or new when id==null) become tier t under the current Era?
function eraAllows(t,id){
  if(isCityPlus(t)&&!(id!=null&&isCityPlus(settTier(id)))){const c=eraCap("cities");
    if(c!=null&&cityCount(id)+1>c)return {ok:false,why:currentEra()+" allows "+c+" Cit"+(c===1?"y":"ies")+(c===0?" — reach Ascension (Renown "+((ERAS.Ascension||{}).renown||"?")+") first":"")};}
  if(t==="Metropolis"&&((S.domains||{}).Industry||0)<10)return {ok:false,why:"Metropolis requires Sovereign Industry"};
  return {ok:true};
}
function boardFlags(){
  const f=[],era=currentEra();
  const cc=cityCount(),cCap=eraCap("cities");if(cCap!=null&&cc>cCap)f.push("Cities "+cc+" / "+cCap+" allowed in "+era);
  const sCap=eraCap("max_settlements");if(sCap!=null&&S.settlements.length>sCap)f.push("Settlements "+S.settlements.length+" / "+sCap+" allowed in "+era);
  const aCap=eraCap("armies");if(aCap!=null&&S.armies.length>aCap)f.push("Armies "+S.armies.length+" / "+aCap+" allowed in "+era);
  if(!capitalSett())f.push("No capital set");
  const m=S.settlements.find(s=>s.tier==="Metropolis");
  if(m&&!m.capital)f.push("Metropolis is not the capital (capital only)");
  if(m&&((S.domains||{}).Industry||0)<10)f.push("Metropolis without Sovereign Industry");
  S.settlements.forEach(s=>{if(wardUse(s.id).typeBad)f.push(s.tier+": non-Husbandry pursuit in Hamlet");});
  S.settlements.forEach(s=>{const w=wardUse(s.id);if(w.free<0)f.push(s.tier+": "+(-w.free)+" ward(s) over cap");});
  Object.keys(S.infra).forEach(n=>{const st=infraReqStatus(INFRA[n]);if(!st.ok)f.push(n+": req unmet ("+st.missing.join(", ")+")");});
  Object.keys(S.wonders).forEach(n=>{const st=infraReqStatus(WON[n]);if(!st.ok)f.push(n+": req unmet ("+st.missing.length+" infra missing/invalid)");});
  return f;
}
function hasMetropolis(exceptId){return S.settlements.some(s=>s.tier==="Metropolis"&&s.id!==exceptId);}
function onBoard(name){return S.placed.some(p=>p.name===name);}      // one of each name, anywhere
function nextTier(t){const i=TIER_CHAIN.indexOf(t);return i>=0&&i<TIER_CHAIN.length-1?TIER_CHAIN[i+1]:null;}
// place any Unplaced pursuits into free ward slots (called after adding/expanding a settlement)
function autoFill(){
  let moved=true;
  while(moved){
    moved=false;
    const unplaced=S.placed.filter(p=>p.sid==null);
    for(const p of unplaced){
      for(const s of S.settlements){
        const c=canPlace(p.name,s.id);
        if(c.ok){p.sid=s.id;moved=true;break;}
      }
    }
  }
}

// ---- catalog ----
const TYPES=[...new Set(NAMES.map(n=>R[n].type))].sort();
document.querySelectorAll(".tab").forEach(t=>t.onclick=()=>{
  tab=t.dataset.k; document.querySelectorAll(".tab").forEach(x=>x.classList.toggle("on",x===t));
  document.getElementById("typeFilters").style.display = tab==="pursuit"?"flex":"none";
  renderList();
});
function buildFilters(){
  const box=document.getElementById("typeFilters"); box.innerHTML="";
  TYPES.forEach(t=>{const c=document.createElement("span");c.className="chip";c.textContent=t;
    c.onclick=()=>{activeTypes.has(t)?activeTypes.delete(t):activeTypes.add(t);c.classList.toggle("on");renderList();};
    box.appendChild(c);});
}
function renderList(){
  const q=document.getElementById("search").value.toLowerCase();
  const list=document.getElementById("list"); list.innerHTML="";
  if(tab==="pursuit"){
    const searching=q.length>0;
    const shown=TYPES.filter(t=>!(activeTypes.size&&!activeTypes.has(t)) && NAMES.some(n=>R[n].type===t&&n.toLowerCase().includes(q)));
    // expand/collapse all row
    const ctl=document.createElement("div");ctl.className="catctl";
    const ea=document.createElement("span");ea.className="chip";ea.textContent="expand all";
    ea.onclick=()=>{shown.forEach(t=>catOpen.add(t));renderList();};
    const ca=document.createElement("span");ca.className="chip";ca.textContent="collapse all";
    ca.onclick=()=>{catOpen.clear();renderList();};
    ctl.appendChild(ea);ctl.appendChild(ca);list.appendChild(ctl);
    shown.forEach(t=>{
      const mem=NAMES.filter(n=>R[n].type===t&&n.toLowerCase().includes(q));
      const openT=searching||catOpen.has(t);
      const g=document.createElement("div");g.className="typegroup";
      const th=document.createElement("div");th.className="th";th.style.cursor="pointer";
      th.textContent=(openT?"▾ ":"▸ ")+t+" ("+mem.length+")";
      th.onclick=()=>{catOpen.has(t)?catOpen.delete(t):catOpen.add(t);renderList();};
      g.appendChild(th);
      if(openT) mem.forEach(n=>g.appendChild(itemRow(n,R[n].monument,(PC[n]||0)>0)));
      list.appendChild(g);
    });
  } else {
    const src=tab==="infra"?INFRA:WON, have=tab==="infra"?S.infra:S.wonders;
    Object.keys(src).filter(n=>n.toLowerCase().includes(q)).forEach(n=>{
      const r=src[n];const row=itemRow(n,false,!!have[n]);
      const meta=document.createElement("span");meta.className="meta";
      const rs=infraReqStatus(r);
      meta.textContent=r.tier+(r.upkeep?(" · up "+r.upkeep):"")+(!rs.ok?" · 🔒":rs.manual?" · ?":"");
      if(!rs.ok||rs.manual)meta.title=(!rs.ok?"missing: "+rs.missing.join(", "):"")+(rs.manual?(rs.ok?"":"\n")+"check manually: "+rs.toks.filter(x=>x.ok===null).map(x=>x.tok).join(", "):"");
      row.insertBefore(meta,row.lastChild);list.appendChild(row);
    });
  }
}
function itemRow(n,mon,have){
  const row=document.createElement("div");row.className="row"+(mon?" mon":"")+(have?" have":"");
  const nm=document.createElement("span");nm.className="nm";nm.textContent=n;nm.onclick=()=>addItem(n);
  const b=document.createElement("button");b.className="addbtn";b.textContent="+";
  b.onclick=(e)=>{e.stopPropagation();addItem(n);};
  row.appendChild(nm);row.appendChild(b);return row;
}
function flash(msg){const el=document.getElementById("flash");el.textContent=msg;el.style.opacity=1;
  clearTimeout(flash._t);flash._t=setTimeout(()=>el.style.opacity=0,2200);}
function addItem(n){
  if(tab==="infra"){S.infra[n]=1;save();render();renderList();return;}
  if(tab==="wonder"){S.wonders[n]=1;save();render();renderList();return;}
  // pursuit — one of each name only (covers Monuments, Principle 15)
  if(onBoard(n)){flash(n+" already on board — one per name");return;}
  let target=activeSid, note="";
  if(target!=null){const c=canPlace(n,target);if(!c.ok){target=null;note=" — "+c.why+", left Unplaced";}}
  S.placed.push({id:pid++,name:n,sid:target});
  if(note)flash(n+note);
  save();render();renderList();
}
function removeInstance(id){S.placed=S.placed.filter(p=>p.id!==id);save();render();renderList();}
function removeOneByName(n){ // remove an unplaced one first, else last placed
  let i=S.placed.findIndex(p=>p.name===n&&p.sid==null);
  if(i<0)i=S.placed.map(p=>p.name).lastIndexOf(n);
  if(i>=0)S.placed.splice(i,1);save();render();renderList();
}
function addByName(n){addItem(n);}   // used by card '+' (respects active settlement)
function moveInstance(id,sid){
  const p=S.placed.find(x=>x.id===id);if(!p)return;
  if(sid!=null){const c=canPlace(p.name,sid);if(!c.ok){flash(c.why);return;}}
  p.sid=sid;save();render();
}

// ---- mastery ----
// ---- infrastructure / wonder requirements ----
// requirement string = '+'-joined tokens. Token kinds:
//   <Infra name>          → that Infrastructure built AND its own requirements met
//   One Tier <Tier>       → every Infrastructure of that tier built  (reading: full tier; data has no rules definition)
//   All Infrastructure…   → every Infrastructure built and requirement-valid (Wonders)
//   …Capital City…        → your capital is City tier or higher (City / Metropolis)
//   …Capital…             → you have a capital settlement (every player has one)
//   anything else         → not modelled → manual "?" flag, non-blocking
function infraReqToks(rec){const s=((rec&&rec.requirement)||"").trim();
  if(!s||/^none$/i.test(s))return [];return s.split("+").map(t=>t.trim()).filter(Boolean);}
function infraTokStatus(tok,seen){
  let m;seen=seen||new Set();
  if(m=tok.match(/^One\s+Tier\s+(\w+)$/i)){const t=m[1].toLowerCase();
    const all=Object.keys(INFRA).filter(n=>(INFRA[n].tier||"").toLowerCase()===t),miss=all.filter(n=>!S.infra[n]);
    return {tok,ok:!miss.length,missing:miss,why:"all "+cap(t)+" ("+(all.length-miss.length)+"/"+all.length+")"};}
  if(/^All\s+Infrastructure/i.test(tok)){const all=Object.keys(INFRA),miss=all.filter(n=>!infraValid(n,seen));
    return {tok,ok:!miss.length,missing:miss,why:"all Infrastructure ("+(all.length-miss.length)+"/"+all.length+")"};}
  if(INFRA[tok]){const built=!!S.infra[tok],ok=built&&infraValid(tok,seen);
    return {tok,ok,missing:ok?[]:[tok+(built?" (req unmet)":"")],why:tok};}
  if(/capital\s+city/i.test(tok)){const c=capitalSett(),ok=!!c&&TIER_CHAIN.indexOf(c.tier)>=TIER_CHAIN.indexOf("City");
    return {tok,ok,missing:ok?[]:[c?"Capital is a "+c.tier+" (needs City)":"a Capital"],why:"Capital is a City+"+(c?" (now "+c.tier+")":" — none set")};}
  if(/capital/i.test(tok)){const c=capitalSett();return {tok,ok:!!c,missing:c?[]:["a Capital"],why:"Capital"+(c?" ("+c.tier+")":" — none set")};}
  return {tok,ok:null,missing:[],why:tok+" — check manually"};
}
function infraReqStatus(rec,seen){
  const st=infraReqToks(rec).map(t=>infraTokStatus(t,seen));
  const bad=st.filter(x=>x.ok===false),man=st.filter(x=>x.ok===null);
  return {ok:!bad.length,manual:man.length>0,toks:st,missing:[].concat(...bad.map(x=>x.missing))};
}
function infraValid(n,seen){               // built + requirements met (manual tokens don't block)
  const src=INFRA[n]?S.infra:S.wonders, rec=INFRA[n]||WON[n];
  if(!rec||!src[n])return false;
  seen=seen||new Set(); if(seen.has(n))return true; const s2=new Set(seen);s2.add(n);
  return infraReqStatus(rec,s2).ok;
}
function infraActive(tok){return infraValid(tok);}
function infraReqLinesHTML(rec){
  return infraReqStatus(rec).toks.map(x=>'<div class="ireq"><span class="'+(x.ok===true?'ok':x.ok===false?'no':'mn')+'">'+(x.ok===true?'✓':x.ok===false?'✗':'?')+'</span><span>'+esc(x.why)+'</span>'+(x.ok===false&&x.missing.length?'<span class="why">missing: '+esc(x.missing.join(", "))+'</span>':'')+'</div>').join("");
}
// infra/wonder tokens a pursuit's mastery depends on
function masteryInfraToks(r){return [...new Set([].concat(...r.mreq).map(t=>t.trim()).filter(t=>INFRA[t]||WON[t]))];}
function masteryInfraHTML(r){
  const toks=masteryInfraToks(r);if(!toks.length)return "";
  return '<div class="lbl" style="margin-top:6px">INFRASTRUCTURE REQ</div>'+toks.map(t=>{const rec=INFRA[t]||WON[t],built=!!(INFRA[t]?S.infra:S.wonders)[t],st=infraReqStatus(rec),ok=built&&st.ok;
    return '<div class="ireq"><span class="'+(ok?'ok':'no')+'">'+(ok?'✓':'✗')+'</span><span>'+esc(t)+'</span><span class="why">'+
      (!built?'not built':!st.ok?'built — its req unmet: '+esc(st.missing.join(", ")):'active')+(st.manual?' · ? '+esc(st.toks.filter(x=>x.ok===null).map(x=>x.tok).join(", ")):'')+'</span></div>'+
      (rec.requirement&&!/^none$/i.test(rec.requirement)?'<div class="ireq"><span class="why" style="margin-left:14px">'+esc(t)+' needs: '+esc(rec.requirement)+'</span></div>':'');}).join("");
}
function annotReqTok(o){o=o.trim();
  if(INFRA[o]||WON[o]){const built=!!(INFRA[o]?S.infra:S.wonders)[o];
    if(!built)return o+" [infra: not built]";
    const st=infraReqStatus(INFRA[o]||WON[o]);if(!st.ok)return o+" [infra req unmet: "+st.missing.join(", ")+"]";}
  return o;}
function optionMet(tok,have,craft,tc){
  tok=tok.trim();let m;
  if(m=tok.match(/^Craft\s+(\d+)$/i))return craft>=+m[1];
  if(m=tok.match(/^(\d+)\s+(.+)$/))return (tc[m[2].trim()]||0)>=+m[1];
  if(R[tok])return have.has(tok);
  if(DATA.settlements[tok])return S.settlements.some(s=>s.tier===tok);
  return infraActive(tok);
}
function reqStatus(rec,have,craft,tc){
  if(!rec.mreq.length)return{earned:true,missing:[]};
  const missing=[];let ok=true;
  rec.mreq.forEach(g=>{if(!g.some(o=>optionMet(o,have,craft,tc))){ok=false;missing.push(g.map(annotReqTok).join(" / "));}});
  return{earned:ok,missing};
}
function computeEarned(have){
  const tc={};Object.keys(PC).forEach(n=>tc[R[n].type]=(tc[R[n].type]||0)+PC[n]);
  let earned={},craft=0;
  for(let it=0;it<4;it++){
    craft=0;
    Object.keys(PC).forEach(n=>{const r=R[n],q=PC[n];
      r.innate.forEach(a=>{if(a.flat&&a.cat==="craft")craft+=a.val*q;});
      if(earned[n])r.mastery.forEach(a=>{if(a.flat&&a.cat==="craft")craft+=a.val*q;});});
    Object.keys(S.infra).forEach(n=>INFRA[n].atoms.forEach(a=>{if(a.flat&&a.cat==="craft")craft+=a.val;}));
    Object.keys(S.wonders).forEach(n=>WON[n].atoms.forEach(a=>{if(a.flat&&a.cat==="craft")craft+=a.val;}));
    const ne={};Object.keys(PC).forEach(n=>{ne[n]=reqStatus(R[n],have,craft,tc).earned;});
    earned=ne;
  }
  return{earned,craft,tc};
}

// ---- atom chip ----
function atomEl(a){
  const phase=a.season?"season":(PHASE[a.cat]||"other");const col=cvar(PHASE_COLOR[phase]);
  const el=document.createElement("span");el.className="atom"+(a.cond?" cond":"");
  el.style.borderColor=col;el.style.color=col;
  el.textContent=a.scale?("+"+a.scale.per+"/"+a.scale.of+" spec"):a.text;
  if(a.season){const s=document.createElement("span");s.className="s";s.textContent="["+a.season+"]";el.appendChild(s);}
  el.title=(a.flat?"flat — summed":"conditional/triggered — not summed")+" · "+PHASE_LABEL[phase];
  return el;
}
function atomsBlock(atoms,hideCombat){
  const wrap=document.createElement("div");wrap.className="atoms";
  const vis=atoms.filter(a=>!(hideCombat&&(a.cat==="combat"||a.cat==="other"||a.cat==="natural")));
  if(!vis.length){const s=document.createElement("span");s.className="note";s.textContent="—";wrap.appendChild(s);}
  else vis.forEach(a=>wrap.appendChild(atomEl(a)));
  return wrap;
}

// ---- render ----
function render(){
  reindex();                    // S := active board, ids synced
  applyTheme(D.theme||"parchment");
  applySkin(D.shape||"sharp");
  renderTopBar();
  if(D.view==="battle"&&!mods().battle)D.view="board";
  const view=D.view||"board";
  document.getElementById("vtabBattle").style.display=mods().battle?"":"none";
  document.querySelectorAll(".modcb").forEach(cb=>{cb.checked=!!mods()[cb.dataset.m];
    if(!cb._w){cb._w=1;cb.onchange=()=>{mods()[cb.dataset.m]=cb.checked;save();render();};}});
  document.getElementById("viewBattle").style.display = view==="battle"?"":"none";
  document.getElementById("appBoard").style.display = view==="board"?"":"none";
  document.getElementById("viewDash").style.display = view==="dash"?"":"none";
  document.getElementById("viewRenown").style.display = view==="renown"?"":"none";
  document.getElementById("viewMap").style.display = view==="map"?"":"none";
  document.querySelectorAll(".vtab").forEach(t=>t.classList.toggle("on",t.dataset.v===view));
  if(view==="dash"){renderDash();save();return;}
  if(view==="renown"){renderRenown();save();return;}
  if(view==="map"){renderMap();save();return;}
  if(view==="battle"){renderBattle();save();return;}

  recomputePC();
  const have=new Set(Object.keys(PC));
  const {earned,craft,tc}=computeEarned(have);
  const hideCombat=document.getElementById("hideCombat").checked;
  renderPursuitBoard(earned,craft,tc,hideCombat,have);
  renderInfraSection("infra",INFRA,S.infra,hideCombat);
  renderInfraSection("wonder",WON,S.wonders,hideCombat);
  renderArmy();
  computeTotals(have,earned,tc);
  renderSettlements();
  renderPO();
  trIn.value=S.treasury;document.getElementById("turn").textContent=S.turn;document.getElementById("autoNet").checked=!!S.autoNet;
  const total=S.placed.length;
  document.getElementById("poolcount").textContent=total?(total+" placed · "+Object.keys(PC).length+" types"):"";
  save();
}

// ---- top bar: view tabs + player switcher ----
document.querySelectorAll(".vtab").forEach(t=>t.onclick=()=>{D.view=t.dataset.v;save();render();});
function renderTopBar(){
  const ts=document.getElementById("themeSel");
  if(ts){ts.value=D.theme||"parchment";if(!ts._wired){ts._wired=1;ts.onchange=()=>{D.theme=ts.value;applyTheme(D.theme);save();render();};}}
  const sh=document.getElementById("shapeSel");
  if(sh){sh.value=D.shape||"sharp";if(!sh._wired){sh._wired=1;sh.onchange=()=>{D.shape=sh.value;applySkin(D.shape);save();render();};}}
  const bar=document.getElementById("playerBar");bar.innerHTML="";
  const chips=[];
  D.players.forEach((p,i)=>{
    const c=document.createElement("span");c.className="pchip"+(i===D.active?" on":"");
    c.innerHTML='<span class="pdot" style="background:'+p.color+'"></span><span class="pname">'+esc(p.name)+'</span>';
    c.onclick=()=>{D.active=i;reindex();render();renderList();};
    bar.appendChild(c);chips.push(c);
  });
  const add=document.createElement("span");add.className="pchip";add.textContent="+ player";
  add.onclick=()=>{const np=newPlayer(D.players.length+1);np.id=Math.max(Date.now(),1+Math.max(0,...D.players.map(p=>+p.id||0)));D.players.push(np);D.active=D.players.length-1;reindex();save();render();renderList();};
  bar.appendChild(add);
  const p=D.players[D.active], chip=chips[D.active];
  const nm=document.createElement("input");nm.value=p.name;nm.style.width="110px";nm.title="rename player";
  nm.oninput=()=>{p.name=nm.value;const l=chip&&chip.querySelector(".pname");if(l)l.textContent=p.name;save();};
  const col=document.createElement("input");col.type="color";col.value=p.color;col.style.width="30px";col.style.padding="0";col.title="player color";
  col.oninput=()=>{p.color=col.value;const d=chip&&chip.querySelector(".pdot");if(d)d.style.background=p.color;};
  col.onchange=()=>{p.color=col.value;save();render();};
  bar.appendChild(nm);bar.appendChild(col);
  if(D.players.length>1){const del=document.createElement("button");del.className="rm";del.textContent="✕ player";
    del.onclick=()=>{D.players.splice(D.active,1);D.active=0;reindex();save();render();renderList();};bar.appendChild(del);}
}
function toggleEmpty(k,n){const e=document.getElementById("e-"+k);if(e)e.style.display=n?"none":"block";
  const c=document.getElementById("c-"+k);if(c)c.textContent=n?("· "+n):"";}

function settBar(sid){
  const wu=wardUse(sid);const wrap=document.createElement("div");
  const bar=document.createElement("div");bar.className="bar";bar.style.width="120px";
  const pct=wu.cap?Math.min(100,wu.used/wu.cap*100):0;
  const f=document.createElement("span");f.style.width=pct+"%";f.style.background=wu.used>wu.cap?cvar("--upkeep"):cvar("--income");
  const rest=document.createElement("span");rest.style.width=(100-pct)+"%";rest.style.background=cvar("--barbg");
  bar.appendChild(f);bar.appendChild(rest);wrap.appendChild(bar);return wrap;
}

function renderPursuitBoard(earned,craft,tc,hideCombat,have){
  const host=document.getElementById("board-pursuit");host.innerHTML="";
  // settlement builder toolbar
  const tb=document.createElement("div");tb.className="settbuild";
  const sel=document.createElement("select");
  Object.keys(DATA.settlements).forEach(t=>{const o=document.createElement("option");o.value=t;
    o.textContent=t+" ("+DATA.settlements[t].wards+"w)";
    if(t==="Metropolis")o.disabled=true;sel.appendChild(o);});   // Metropolis: capital only (expand the capital)
  const addB=document.createElement("button");addB.textContent="+ settlement";
  addB.onclick=()=>{
    if(sel.value==="Metropolis"){flash("Metropolis is capital only — expand your capital");return;}
    {const ea=eraAllows(sel.value,null);if(!ea.ok){flash(ea.why);return;}
     const sc=eraCap("max_settlements");if(sc!=null&&S.settlements.length+1>sc){flash(currentEra()+" allows "+sc+" settlements");return;}}
    const id=sid++;S.settlements.push({id,tier:sel.value});activeSid=id;autoFill();save();render();};
  tb.appendChild(sel);tb.appendChild(addB);
  const exAll=document.createElement("button");exAll.textContent="expand all";
  exAll.onclick=()=>{S.expanded=S.placed.map(p=>p.id);save();render();};
  const colAll=document.createElement("button");colAll.textContent="collapse all";
  colAll.onclick=()=>{S.expanded=[];save();render();};
  tb.appendChild(exAll);tb.appendChild(colAll);
  const vt=document.createElement("button");vt.textContent=(D.pursuitView==="table")?"▤ cards":"▦ table";
  vt.title="toggle card / dense table view";
  vt.onclick=()=>{D.pursuitView=(D.pursuitView==="table")?"cards":"table";save();render();};
  tb.appendChild(vt);
  const fl=document.createElement("span");fl.id="flash";fl.className="flash";tb.appendChild(fl);
  host.appendChild(tb);
  const flags=boardFlags();
  if(flags.length){const fb=document.createElement("div");fb.className="flagbox";
    fb.innerHTML='<b>⚑ '+flags.length+' flag'+(flags.length>1?'s':'')+'</b><ul>'+flags.map(x=>'<li>'+esc(x)+'</li>').join("")+'</ul>';
    host.appendChild(fb);}

  const groups=[...S.settlements.map(s=>s.id), null];
  let any=false;
  groups.forEach(gid=>{
    const occ=S.placed.filter(p=>p.sid===gid);
    const unpEmpty=(gid==null&&!occ.length);
    any=any||occ.length>0||gid!=null;
    const closed=(S.settClosed||[]).includes(gid==null?"unplaced":gid);
    const key=(gid==null?"unplaced":gid);
    const grp=document.createElement("div");grp.className="sgroup"+(gid===activeSid?" active":"")+(unpEmpty?" unp-empty":"");
    grp.dataset.dropSid=(gid==null?"none":gid);
    const hd=document.createElement("div");hd.className="sgroup-hd";
    const car=document.createElement("span");car.className="pcaret";car.style.cursor="pointer";car.textContent=closed?"▸":"▾";
    car.onclick=(e)=>{e.stopPropagation();S.settClosed=S.settClosed||[];const i=S.settClosed.indexOf(key);
      if(i<0)S.settClosed.push(key);else S.settClosed.splice(i,1);save();render();};
    hd.appendChild(car);
    if(gid!=null){
      const tier=settTier(gid),wu=wardUse(gid);
      const t=document.createElement("span");t.className="stitle";t.style.cursor="pointer";
      t.onclick=()=>{activeSid=gid;render();};
      const isCap=!!(S.settlements.find(x=>x.id===gid)||{}).capital;
      t.innerHTML=(gid===activeSid?"● ":"")+(isCap?"★ ":"")+tier+(isCap?' <span class="badge earn">Capital</span>':'')+' <span class="note">wards '+wu.used+'/'+wu.cap+(wu.free>0?' · <b style="color:var(--income)">'+wu.free+' empty</b>':'')+(wu.free<0?' · <b style="color:var(--upkeep)">'+(-wu.free)+' over</b>':'')+' · '+occ.length+' pursuits'+(wu.typeBad?' · <span style="color:var(--upkeep)">type!</span>':'')+(tier==="Hamlet"?' · Husbandry/Arable only':'')+'</span>';
      hd.appendChild(t);hd.appendChild(settBar(gid));
      const cb=document.createElement("button");cb.textContent=isCap?"★ capital":"☆ make capital";
if(isCap)cb.style.color="var(--income)";
      cb.onclick=(e)=>{e.stopPropagation();if(isCap){flash("every player has a capital — set another to move it");return;}
        if(S.settlements.some(x=>x.tier==="Metropolis"&&x.id!==gid)){flash("Metropolis is capital only — can't move the capital off it");return;}
        setCapital(gid);save();render();};
      hd.appendChild(cb);
      const nt=nextTier(tier);
      if(nt&&!(nt==="Metropolis"&&!isCap)){
        const ea=eraAllows(nt,gid);
        const ex=document.createElement("button");ex.textContent="expand ▲ "+nt+(ea.ok?"":" 🔒");ex.title=ea.ok?"upgrade to "+nt:ea.why;
        if(!ea.ok)ex.style.opacity=".55";
        ex.onclick=(e)=>{e.stopPropagation();
          if(nt==="Metropolis"&&(!isCap||hasMetropolis(gid))){flash("Metropolis is capital only");return;}
          {const ea=eraAllows(nt,gid);if(!ea.ok){flash(ea.why);return;}}
          const s=S.settlements.find(x=>x.id===gid);s.tier=nt;autoFill();save();render();};
        hd.appendChild(ex);
      }
      const del=document.createElement("button");del.className="rm";del.textContent="✕ settlement";
      del.onclick=(e)=>{e.stopPropagation();occ.forEach(p=>p.sid=null);S.settlements=S.settlements.filter(s=>s.id!==gid);
        if(activeSid===gid)activeSid=S.settlements[0]?S.settlements[0].id:null;save();render();};
      hd.appendChild(del);
    } else {
      const t=document.createElement("span");t.className="stitle";
      t.innerHTML='Unplaced <span class="note">('+occ.length+')</span>';
      hd.appendChild(t);
    }
    grp.appendChild(hd);
    if(!closed){
      if((D.pursuitView||"cards")==="table"){
        grp.appendChild(pursuitTable(occ,earned,craft,tc,hideCombat,have));
      } else if(gid!=null){
        grp.appendChild(wardGrid(gid,occ,earned,craft,tc,hideCombat,have));
      } else {
        const board=document.createElement("div");board.className="board";
        occ.sort((a,b)=>R[a.name].type.localeCompare(R[b.name].type)||a.name.localeCompare(b.name));
        occ.forEach(p=>board.appendChild(pursuitCard(p,earned,craft,tc,hideCombat,have)));
        grp.appendChild(board);
      }
    }
    host.appendChild(grp);
  });
  document.getElementById("e-pursuit").style.display=S.placed.length?"none":"block";
  document.getElementById("c-pursuit").textContent=S.placed.length?("· "+S.placed.length):"";
}

// piles: each ward-consuming pursuit is a pile root; its efficient rider chain stacks on top (chains, not branches)
function wardPiles(occ){
  const exempt=exemptionsOf(occ), riderOf={};
  occ.forEach(o=>{if(exempt.has(o.id))riderOf[R[o.name].efficient]=o;});
  const used=new Set(), piles=[];
  occ.filter(o=>!exempt.has(o.id))
     .sort((a,b)=>R[a.name].type.localeCompare(R[b.name].type)||a.name.localeCompare(b.name))
     .forEach(root=>{const pile=[root];used.add(root.id);let cur=root;
       while(riderOf[cur.name]&&!used.has(riderOf[cur.name].id)){cur=riderOf[cur.name];used.add(cur.id);pile.push(cur);}
       piles.push(pile);});
  occ.filter(o=>!used.has(o.id)).forEach(o=>piles.push([o]));   // safety: orphaned riders
  return piles;
}
function wardGrid(gid,occ,earned,craft,tc,hideCombat,have){
  const wu=wardUse(gid), piles=wardPiles(occ), n=Math.max(wu.cap,piles.length);
  const grid=document.createElement("div");grid.className="wards";
  for(let i=0;i<n;i++){
    const w=document.createElement("div");w.className="ward";w.dataset.dropSid=gid;const pile=piles[i];
    const lbl=document.createElement("div");lbl.className="ward-lbl";
    lbl.innerHTML='<span>Ward '+(i+1)+(i>=wu.cap?' · over cap':'')+'</span>'+(pile&&pile.length>1?'<span>⚡ '+(pile.length-1)+' stacked</span>':'');
    w.appendChild(lbl);
    if(i>=wu.cap)w.classList.add("over");
    if(!pile){
      w.classList.add("empty");
      const e=document.createElement("div");e.className="emp";e.textContent="empty ward";w.appendChild(e);
      w.onclick=()=>{activeSid=gid;render();};
    } else {
      const pl=document.createElement("div");pl.className="pile";
      pile.forEach((p,j)=>{const pc=document.createElement("div");pc.className="pc"+(j<pile.length-1?" buried":"");
        pc.style.zIndex=j+1;pc.dataset.pid=p.id;pc.appendChild(pursuitCard(p,earned,craft,tc,hideCombat,have));pl.appendChild(pc);});
      w.appendChild(pl);
    }
    grid.appendChild(w);
  }
  return grid;
}
// ---- drag & drop (pointer events: mouse + touch) ----
// grab a pile's root → whole pile moves; grab any other card → just that card.
// drop on a card → ride it (must be efficient with it; replaces its current rider).
// drop on a ward / settlement → move in.  Riders that lose their stack keep a ward if free, else → Unplaced.
function unitFor(inst){
  if(inst.sid==null)return [inst];
  const pl=wardPiles(occupants(inst.sid)).find(p=>p[0].id===inst.id);
  return pl?pl.slice():[inst];
}
function tryMove(unit,t,commit){
  const snap=S.placed.map(p=>[p,p.sid,p.ride]);
  const restore=()=>snap.forEach(([p,sd,r])=>{p.sid=sd;p.ride=r;});
  const ids=new Set(unit.map(u=>u.id)),root=unit[0],src=root.sid;
  let onto=null,displaced=null,tsid;
  if(t.kind==="card"){
    onto=S.placed.find(p=>p.id===t.pid);
    if(!onto||ids.has(onto.id)||onto.sid==null)return {ok:false,why:""};
    if(R[root.name].efficient!==onto.name)return {ok:false,why:root.name+" is not efficient with "+onto.name};
    tsid=onto.sid;
    const ex=exemptionsOf(occupants(tsid));
    displaced=occupants(tsid).find(o=>ex.has(o.id)&&R[o.name].efficient===onto.name&&!ids.has(o.id))||null;
  } else {
    tsid=t.sid==="none"?null:+t.sid;
    if(tsid===src)return {ok:false,why:""};
  }
  if(tsid!=null&&settTier(tsid)==="Hamlet"){const bad=unit.find(u=>!hamletOK(u.name));if(bad)return {ok:false,why:"Hamlet holds Husbandry / Arable Land only"};}
  const before={};[src,tsid].forEach(x=>{if(x!=null)before[x]=exemptionsOf(occupants(x));});
  unit.forEach(u=>u.sid=tsid);
  if(onto){root.ride=1+Math.max(0,...S.placed.map(p=>p.ride||0));if(displaced)displaced.ride=0;}
  else root.ride=(tsid==null?0:-1);           // plain move never steals an existing rider's slot
  const evicted=[];
  for(const x of [tsid,src]){if(x==null)continue;let guard=200;
    while(wardUse(x).free<0&&guard--){
      const ex=exemptionsOf(occupants(x));
      const c=occupants(x).filter(o=>!ex.has(o.id)&&!ids.has(o.id));
      const pick=c.find(o=>displaced&&o.id===displaced.id)||c.find(o=>before[x]&&before[x].has(o.id));
      if(!pick){restore();return {ok:false,why:"no free ward in "+settTier(x)};}
      pick.sid=null;pick.ride=0;evicted.push(pick.name);
    }}
  if(!commit)restore();
  return {ok:true,evicted,displaced:displaced?displaced.name:null,to:tsid==null?"Unplaced":settTier(tsid)};
}
let DRAG=null;
function scrollHost(el){for(let e=el;e&&e!==document.body;e=e.parentElement){const cs=getComputedStyle(e);if(/(auto|scroll)/.test(cs.overflowY)&&e.scrollHeight>e.clientHeight)return e;}return null;}
function dropTargetAt(x,y){
  const el=document.elementFromPoint(x,y);if(!el)return null;
  const pc=el.closest(".ward [data-pid]");
  if(pc)return {kind:"card",pid:+pc.dataset.pid,el:pc.firstElementChild||pc};
  const w=el.closest("[data-drop-sid]");
  if(w)return {kind:"sett",sid:w.dataset.dropSid,el:w};
  return null;
}
function clearDropHL(){document.querySelectorAll(".drop-ok,.drop-bad").forEach(e=>e.classList.remove("drop-ok","drop-bad"));}
function armDrag(handle,inst,threshold){
  handle.addEventListener("pointerdown",ev=>{
    if(ev.button!==0)return;
    if(threshold&&ev.pointerType!=="mouse")return;           // header drag = mouse only; touch uses the grip
    if(ev.target.closest("button,select,input")||(threshold&&ev.target.closest(".grip")))return;
    const sx=ev.clientX,sy=ev.clientY;let started=false;
    if(!threshold){ev.preventDefault();}
    const move=e=>{
      if(!started){if(Math.hypot(e.clientX-sx,e.clientY-sy)<threshold)return;started=true;beginDrag(inst,handle,e);}
      e.preventDefault();dragMove(e.clientX,e.clientY);};
    const up=e=>{window.removeEventListener("pointermove",move);window.removeEventListener("pointerup",up);window.removeEventListener("pointercancel",cancel);
      if(started){handle._suppressClick=true;setTimeout(()=>handle._suppressClick=false,0);dragEnd(true);}};
    const cancel=()=>{window.removeEventListener("pointermove",move);window.removeEventListener("pointerup",up);window.removeEventListener("pointercancel",cancel);if(started)dragEnd(false);};
    window.addEventListener("pointermove",move,{passive:false});window.addEventListener("pointerup",up);window.addEventListener("pointercancel",cancel);
    if(!threshold){started=true;beginDrag(inst,handle,ev);dragMove(ev.clientX,ev.clientY);}
  });
}
function beginDrag(inst,handle,ev){
  const unit=unitFor(inst);
  const ghost=document.createElement("div");ghost.className="dragghost";
  ghost.innerHTML=unit.map((u,i)=>'<div class="gl"'+(i?' style="margin-left:'+(i*8)+'px"':'')+'>'+esc(u.name)+'</div>').join("")+'<div class="gw"></div>';
  document.body.appendChild(ghost);document.body.classList.add("dnd");
  const srcEl=handle.closest(".pile")&&unit.length>1?handle.closest(".pile"):(handle.closest(".pc")||handle.closest(".card"));
  if(srcEl)srcEl.classList.add("dragging");
  DRAG={unit,ghost,srcEl,t:null,res:null,x:ev.clientX,y:ev.clientY,sc:scrollHost(document.getElementById("board-pursuit")),raf:0};
  const loop=()=>{if(!DRAG)return;const h=DRAG.sc,y=DRAG.y,E=60,sp=14;
    if(h){const r=h.getBoundingClientRect();if(y<r.top+E)h.scrollTop-=sp;else if(y>r.bottom-E)h.scrollTop+=sp;}
    if(y<E)window.scrollBy(0,-sp);else if(y>window.innerHeight-E)window.scrollBy(0,sp);
    DRAG.raf=requestAnimationFrame(loop);};
  DRAG.raf=requestAnimationFrame(loop);
}
function dragMove(x,y){
  if(!DRAG)return;DRAG.x=x;DRAG.y=y;
  DRAG.ghost.style.left=(x+12)+"px";DRAG.ghost.style.top=(y+10)+"px";
  const t=dropTargetAt(x,y),key=t?(t.kind+":"+(t.pid||t.sid)):"";
  if(key===(DRAG.key||""))return;DRAG.key=key;DRAG.t=t;clearDropHL();
  const gw=DRAG.ghost.querySelector(".gw");
  if(!t){DRAG.res=null;gw.textContent="";return;}
  const r=tryMove(DRAG.unit,t,false);DRAG.res=r;
  t.el.classList.add(r.ok?"drop-ok":"drop-bad");
  gw.textContent=r.ok?("→ "+(t.kind==="card"?"ride "+(S.placed.find(p=>p.id===t.pid)||{}).name:r.to)+(r.displaced?" · "+r.displaced+" bumped":"")+(r.evicted.length?" · to Unplaced: "+r.evicted.join(", "):"")):r.why;
  gw.className="gw "+(r.ok?"ok":"bad");
}
function dragEnd(drop){
  if(!DRAG)return;const d=DRAG;DRAG=null;cancelAnimationFrame(d.raf);
  d.ghost.remove();document.body.classList.remove("dnd");clearDropHL();if(d.srcEl)d.srcEl.classList.remove("dragging");
  if(drop&&d.t&&d.res&&d.res.ok){const r=tryMove(d.unit,d.t,true);save();render();
    if(r.ok&&(r.evicted.length||r.displaced))flash((r.displaced?r.displaced+" bumped":"")+(r.evicted.length?(r.displaced?" · ":"")+"to Unplaced: "+r.evicted.join(", "):""));}
  else if(drop&&d.res&&!d.res.ok&&d.res.why)flash(d.res.why);
}
document.addEventListener("keydown",e=>{if(e.key==="Escape"&&DRAG)dragEnd(false);});
function placementSelect(inst){
  const n=inst.name, psel=document.createElement("select");psel.style.fontSize="11px";
  const uo=document.createElement("option");uo.value="";uo.textContent="Unplaced";psel.appendChild(uo);
  S.settlements.forEach(s=>{const c=canPlace(n,s.id);const o=document.createElement("option");
    o.value=s.id;const wu=wardUse(s.id);
    o.textContent=(s.capital?"★ ":"")+s.tier+" ("+wu.used+"/"+wu.cap+")"+(c.ok?"":" 🔒");
    if(!c.ok && s.id!==inst.sid)o.disabled=true;psel.appendChild(o);});
  psel.value=inst.sid==null?"":String(inst.sid);
  psel.onchange=()=>moveInstance(inst.id, psel.value===""?null:+psel.value);
  return psel;
}
function contribChips(r,masteryEarned){
  const acc={};
  const addA=(atoms,act)=>{if(!act)return;atoms.forEach(a=>{if(a.flat&&!a.season&&["gold","craft","faith","doubt","influence","upkeep"].includes(a.cat))acc[a.cat]=(acc[a.cat]||0)+a.val;});};
  addA(r.innate,true); if(r.mastery_raw)addA(r.mastery,masteryEarned);
  const wrap=document.createElement("div");wrap.className="atoms";
  ["gold","upkeep","craft","influence","faith","doubt"].forEach(catk=>{
    if(!acc[catk])return;const ph=PHASE[catk],col=cvar(PHASE_COLOR[ph]);
    const s=document.createElement("span");s.className="atom";s.style.borderColor=col;s.style.color=col;
    s.textContent=(catk==="gold"?"":cap(catk)+" ")+(acc[catk]>0?"+":"")+acc[catk];wrap.appendChild(s);});
  return wrap;
}
function pursuitDetail(r,hideCombat,me){
  const wrap=document.createElement("div");
  const bi=document.createElement("div");bi.className="block";bi.innerHTML='<div class="lbl">INNATE</div>';
  bi.appendChild(atomsBlock(r.innate,hideCombat));
  if(r.innate_raw){const v=document.createElement("div");v.className="verb";v.textContent=r.innate_raw;bi.appendChild(v);}
  wrap.appendChild(bi);
  const bm=document.createElement("div");bm.className="block mastery"+(r.mastery_raw?(me.earned?" on":" off"):"");
  const badge=r.mastery_raw?('<span class="badge '+(me.earned?"earn":"noearn")+'">'+(me.earned?"earned ✓":"not earned ✗")+'</span>'):'<span class="badge nomast">none</span>';
  bm.innerHTML='<div class="lbl">MASTERY<span class="sp"></span>'+badge+'</div>';
  if(r.mastery_raw){
    const ab=atomsBlock(r.mastery,hideCombat);if(!me.earned)ab.style.opacity=".5";bm.appendChild(ab);
    if(r.mreq_raw){const rq=document.createElement("div");rq.className="req";rq.textContent="req: "+r.mreq_raw;bm.appendChild(rq);}
    {const ih=masteryInfraHTML(r);if(ih){const d=document.createElement("div");d.innerHTML=ih;bm.appendChild(d);}}
    if(!me.earned){const mm=document.createElement("div");mm.className="miss";mm.textContent="missing: "+me.missing.join("  +  ");bm.appendChild(mm);}
    const v=document.createElement("div");v.className="verb";v.textContent=r.mastery_raw;bm.appendChild(v);
  }
  wrap.appendChild(bm);return wrap;
}
// dense row-per-pursuit table for one settlement group
function pursuitTable(occ,earned,craft,tc,hideCombat,have){
  occ.sort((a,b)=>R[a.name].type.localeCompare(R[b.name].type)||a.name.localeCompare(b.name));
  const tbl=document.createElement("table");tbl.className="dtable ptable";
  tbl.innerHTML='<thead><tr><th>Pursuit</th><th>Type</th><th>Contribution</th><th>Mastery</th><th>Ward</th><th>Place</th><th></th></tr></thead>';
  const tb=document.createElement("tbody");
  occ.forEach(inst=>{
    const n=inst.name,r=R[n],me=reqStatus(r,have,craft,tc),open=S.expanded.includes(inst.id);
    const tr=document.createElement("tr");
    const c1=document.createElement("td");c1.style.cursor="pointer";
    c1.innerHTML='<span class="pcaret">'+(open?"▾":"▸")+'</span> '+esc(n)+(r.monument?' <span class="badge mon">M</span>':'');
    c1.onclick=()=>{const i=S.expanded.indexOf(inst.id);if(i<0)S.expanded.push(inst.id);else S.expanded.splice(i,1);save();render();};
    const c2=document.createElement("td");c2.className="note";c2.textContent=r.type;
    const c3=document.createElement("td");c3.appendChild(contribChips(r,me.earned));
    const c4=document.createElement("td");c4.innerHTML=r.mastery_raw?('<span class="badge '+(me.earned?"earn":"noearn")+'">'+(me.earned?"✓":"✗")+'</span>'):'<span class="note">—</span>';
    if(!me.earned&&me.missing.length)c4.title="missing: "+me.missing.join("  +  ");
    const c5=document.createElement("td");c5.innerHTML=(inst.sid!=null&&isFreeRider(inst))?'<span class="badge earn" title="efficient rider">⚡</span>':'<span class="note">·</span>';
    const c6=document.createElement("td");c6.appendChild(placementSelect(inst));
    const c7=document.createElement("td");const rm=document.createElement("button");rm.className="rm";rm.textContent="✕";rm.onclick=()=>removeInstance(inst.id);c7.appendChild(rm);
    [c1,c2,c3,c4,c5,c6,c7].forEach(td=>tr.appendChild(td));tb.appendChild(tr);
    if(open){const dr=document.createElement("tr");const dc=document.createElement("td");dc.colSpan=7;
      dc.appendChild(pursuitDetail(r,hideCombat,me));dr.appendChild(dc);tb.appendChild(dr);}
  });
  tbl.appendChild(tb);return tbl;
}

function pursuitCard(inst,earned,craft,tc,hideCombat,have){
  const n=inst.name, r=R[n], me=reqStatus(r,have,craft,tc);
  const open=S.expanded.includes(inst.id);
  const card=document.createElement("div");card.className="card";
  card.style.borderLeftColor=cvar(PHASE_COLOR[PHASE[(r.innate[0]||{}).cat]||"other"]);
  const h=document.createElement("h3");h.style.cursor="pointer";
  const grip=document.createElement("span");grip.className="grip";grip.textContent="⋮⋮";
  grip.onclick=e=>e.stopPropagation();h.appendChild(grip);armDrag(grip,inst,0);armDrag(h,inst,6);
  const car=document.createElement("span");car.className="pcaret";car.textContent=open?"▾":"▸";h.appendChild(car);
  const nm=document.createElement("span");nm.className="nm";nm.textContent=n;h.appendChild(nm);
  if(r.monument){const b=document.createElement("span");b.className="badge mon";b.textContent="Monument";h.appendChild(b);}
  if(r.mastery_raw){const b=document.createElement("span");b.className="badge "+(me.earned?"earn":"noearn");b.textContent=me.earned?"✓":"✗";h.appendChild(b);}
  if(inst.sid!=null && isFreeRider(inst)){const b=document.createElement("span");b.className="badge earn";b.textContent="⚡";b.title="efficient rider";h.appendChild(b);}
  const rm=document.createElement("button");rm.className="rm";rm.textContent="✕";rm.onclick=(e)=>{e.stopPropagation();removeInstance(inst.id);};
  h.appendChild(rm);
  h.onclick=()=>{if(h._suppressClick)return;const i=S.expanded.indexOf(inst.id);if(i<0)S.expanded.push(inst.id);else S.expanded.splice(i,1);save();render();};
  card.appendChild(h);

  const sub=document.createElement("div");sub.className="sub";
  sub.textContent=r.type+(r.efficient?(" · efficient: "+r.efficient):"");card.appendChild(sub);

  // placement dropdown (always visible for quick moves)
  const place=document.createElement("div");place.className="sub";
  place.appendChild(placementSelect(inst));card.appendChild(place);

  if(!open){   // collapsed: header + placement + compact contribution summary
    const sum=contribChips(r,me.earned);sum.style.marginTop="4px";
    if(sum.children.length)card.appendChild(sum);
    return card;
  }

  // INNATE
  const bi=document.createElement("div");bi.className="block";bi.innerHTML='<div class="lbl">INNATE</div>';
  bi.appendChild(atomsBlock(r.innate,hideCombat));
  if(r.innate_raw){const v=document.createElement("div");v.className="verb";v.textContent=r.innate_raw;bi.appendChild(v);}
  card.appendChild(bi);
  // MASTERY
  const bm=document.createElement("div");bm.className="block mastery"+(r.mastery_raw?(me.earned?" on":" off"):"");
  const badge=r.mastery_raw?('<span class="badge '+(me.earned?"earn":"noearn")+'">'+(me.earned?"earned ✓":"not earned ✗")+'</span>'):'<span class="badge nomast">none</span>';
  bm.innerHTML='<div class="lbl">MASTERY<span class="sp"></span>'+badge+'</div>';
  if(r.mastery_raw){
    const ab=atomsBlock(r.mastery,hideCombat);if(!me.earned)ab.style.opacity=".5";bm.appendChild(ab);
    if(r.mreq_raw){const rq=document.createElement("div");rq.className="req";rq.textContent="req: "+r.mreq_raw;bm.appendChild(rq);}
    {const ih=masteryInfraHTML(r);if(ih){const d=document.createElement("div");d.innerHTML=ih;bm.appendChild(d);}}
    if(!me.earned){const mm=document.createElement("div");mm.className="miss";mm.textContent="missing: "+me.missing.join("  +  ");bm.appendChild(mm);}
    const v=document.createElement("div");v.className="verb";v.textContent=r.mastery_raw;bm.appendChild(v);
  }
  card.appendChild(bm);
  return card;
}

function renderInfraSection(kind,src,have,hideCombat){
  const box=document.getElementById("board-"+kind);box.innerHTML="";
  const keys=Object.keys(have);
  keys.forEach(n=>{
    const open=(S.eqOpen||[]).includes(n);
    const r=src[n];const card=document.createElement("div");card.className="card";
    card.style.borderLeftColor=cvar(PHASE_COLOR[PHASE[(r.atoms[0]||{}).cat]||"other"]);
    const h=document.createElement("h3");h.style.cursor="pointer";
    const car=document.createElement("span");car.className="pcaret";car.textContent=open?"▾":"▸";h.appendChild(car);
    const nm=document.createElement("span");nm.className="nm";nm.textContent=n;h.appendChild(nm);
    const tb=document.createElement("span");tb.className="badge tier";tb.textContent=r.tier;h.appendChild(tb);
    const rs=infraReqStatus(r);
    if(infraReqToks(r).length){const qb=document.createElement("span");qb.className="badge "+(!rs.ok?"noearn":rs.manual?"manual":"earn");
      qb.textContent=!rs.ok?"req ✗":rs.manual?"req ?":"req ✓";qb.title=r.requirement;h.appendChild(qb);}
    if(!rs.ok)card.classList.add("illegal");
    if(r.upkeep){const ub=document.createElement("span");ub.className="badge";ub.style.borderColor="var(--upkeep)";ub.style.color="var(--upkeep)";ub.textContent="up "+r.upkeep;h.appendChild(ub);}
    const rm=document.createElement("button");rm.className="rm";rm.textContent="✕";
    rm.onclick=(e)=>{e.stopPropagation();delete have[n];save();render();renderList();};h.appendChild(rm);
    h.onclick=()=>{S.eqOpen=S.eqOpen||[];const i=S.eqOpen.indexOf(n);if(i<0)S.eqOpen.push(n);else S.eqOpen.splice(i,1);save();render();};
    card.appendChild(h);
    if(!rs.ok){const mm=document.createElement("div");mm.className="miss";mm.textContent="missing: "+rs.missing.join(", ");card.appendChild(mm);}
    if(open){
      const sub=document.createElement("div");sub.className="sub";
      sub.textContent="upkeep "+r.upkeep+(r.requirement?(" · req: "+r.requirement):"");card.appendChild(sub);
      if(infraReqToks(r).length){const rq=document.createElement("div");rq.className="block";rq.innerHTML='<div class="lbl">REQUIREMENTS</div>'+infraReqLinesHTML(r);card.appendChild(rq);}
      const bi=document.createElement("div");bi.className="block";bi.innerHTML='<div class="lbl">EMPIRE EFFECT</div>';
      bi.appendChild(atomsBlock(r.atoms,hideCombat));
      if(r.effect_raw){const v=document.createElement("div");v.className="verb";v.textContent=r.effect_raw;bi.appendChild(v);}
      card.appendChild(bi);
    }
    box.appendChild(card);
  });
  toggleEmpty(kind,keys.length);
}

// ---- army: aggregate unlocks/modifiers from pool (innate always, mastery if mastered) ----
function armyUnlocks(earned){
  const active=[];               // {tok, node, via}
  Object.keys(PC).forEach(n=>{
    const src=ARMYSRC[n]; if(!src)return;
    src.innate.forEach(t=>active.push({tok:t,node:n,via:"innate"}));
    if(earned[n]) src.mastery.forEach(t=>active.push({tok:t,node:n,via:"mastery"}));
  });
  const tset=new Set(active.map(a=>a.tok));
  const wTiers=new Set(["Crude"]), armors=new Set(["Cloth"]);
  let shields=false, ranged=false, cavalry=false;
  const retinues=new Set(["Levy"]); const mods=[];
  active.forEach(a=>{
    const t=a.tok;
    if(t.startsWith("tier:")){
      const x=t.slice(5);
      if(TIER_RANK.hasOwnProperty(x)) wTiers.add(x);
      else if(ARMOR_TAG[x]) armors.add(ARMOR_TAG[x]);
      else if(x==="Shields") shields=true;
    } else if(t==="ranged") ranged=true;
    else if(t==="cavalry") cavalry=true;
    else if(t.startsWith("retinue:")) retinues.add(t.slice(8));
    else mods.push(a);           // keyword / modifier
  });
  // armor also implied by weapon tiers? no — armor unlocked only by explicit armor tags.
  return {set:tset,wTiers,armors,shields,ranged,cavalry,retinues,mods,active};
}
function unlockedShieldTiers(u){ // shields gated by weapon-tier progression when Shields unlocked
  return u.shields ? u.wTiers : new Set();
}

function tierOK(tier,tiers){ return tier==null || tiers.has(tier); }
function gloss(k){ return GLOSS[k]?(k+": "+GLOSS[k]):k; }

// ---- inspector ----
const TAG2SRC={};
Object.keys(ARMYSRC).forEach(n=>{
  (ARMYSRC[n].innate||[]).forEach(t=>{(TAG2SRC[t]=TAG2SRC[t]||[]).push({node:n,via:"innate"});});
  (ARMYSRC[n].mastery||[]).forEach(t=>{(TAG2SRC[t]=TAG2SRC[t]||[]).push({node:n,via:"mastery"});});
});
const SYN={"Strain":"Strained"};
function glossLookup(tok){
  if(GLOSS[tok]) return {term:tok,def:GLOSS[tok]};
  let base=tok.replace(/\s*[:+].*$/,"").replace(/\s+\d+$/,"").trim();
  base=SYN[base]||base;
  if(base && GLOSS[base]) return {term:base,def:GLOSS[base],mod:tok};
  let m=tok.match(/^(Immune|Negate)\s+(.+)$/i);
  if(m){let x=SYN[m[2]]||m[2]; if(GLOSS[x]) return {term:x,def:GLOSS[x],mod:tok,prefix:m[1]};}
  return {term:tok,def:null};
}
function openModal(html){
  document.getElementById("inspectCard").innerHTML=html;
  document.getElementById("inspect").style.display="flex";
}
function closeModal(){document.getElementById("inspect").style.display="none";}
function kwChipHTML(tok,cls){return '<span class="kw '+(cls||"")+'" data-tok="'+esc(tok)+'">'+esc(tok)+'</span>';}
function esc(s){return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/"/g,"&quot;");}
function inspectKeyword(tok){
  const g=glossLookup(tok);
  let h='<h3>'+esc(tok)+'<button class="close" onclick="closeModal()">✕</button></h3>';
  if(g.mod && g.term!==tok) h+='<div class="note">base keyword: <b>'+esc(g.term)+'</b>'+(g.prefix?(" ("+g.prefix+")"):"")+'</div>';
  if(g.def) h+='<div class="def">'+esc(g.def)+'</div>';
  // sources: engine-tag grants + any node whose innate/mastery text names the keyword
  const seen=new Set(), srcs=[];
  (TAG2SRC[tok]||[]).forEach(s=>{const k=s.node+"|"+s.via;if(!seen.has(k)){seen.add(k);srcs.push(s);}});
  const base=(g.term||tok);
  [tok,base].forEach(term=>{
    let re;try{re=new RegExp("\\b"+term.replace(/[.*+?^${}()|[\]\\]/g,"\\$&")+"\\b","i");}catch(e){return;}
    Object.keys(R).forEach(n=>{["innate","mastery"].forEach(via=>{
      const txt=R[n][via+"_raw"]||"";if(re.test(txt)){const k=n+"|"+via;if(!seen.has(k)){seen.add(k);srcs.push({node:n,via});}}});});
  });
  if(srcs.length){
    h+='<div class="lbl2">DEFINED / GRANTED BY</div>';
    srcs.slice(0,6).forEach(s=>{const r=R[s.node];const txt=(s.via==="mastery"?r.mastery_raw:r.innate_raw)||"";
      h+='<div class="note"><b>'+esc(s.node)+'</b> ('+s.via+')'+(txt?': '+esc(txt):"")+'</div>';});
  }
  if(!g.def && !srcs.length) h+='<div class="def nodef">No glossary entry — see rulebook.</div>';
  openModal(h);
}
function inspectItem(kind,name){
  const src={weapon:EQ.weapons,ranged:EQ.ranged,armor:EQ.armors,shield:EQ.shields,retinue:EQ.retinues}[kind];
  const it=src&&src[name]; if(!it){openModal('<h3>'+esc(name)+'<button class="close" onclick="closeModal()">✕</button></h3>');return;}
  let h='<h3>'+esc(name);
  if(it.tier)h+=' <span class="badge tier">'+it.tier+'</span>';
  h+='<button class="close" onclick="closeModal()">✕</button></h3>';
  const S_=[];
  const push=(k,v)=>{if(v!==undefined&&v!==null&&v!=="")S_.push('<span class="stat"><span class="k">'+k+'</span><b>'+v+'</b></span>');};
  if(kind==="retinue"){push("TO-STRIKE",it.to_hit+"+");push("ENDURANCE",it.endurance);push("SHAKING",it.shaking+"+");push("SPEED",it.speed);push("MAX",it.max_size);push("COST",it.cost);}
  if(kind==="weapon"||kind==="ranged"){push("AP",it.ap);push("INIT",(it.init>=0?"+":"")+it.init);}
  if(kind==="armor"){push("SAVE",it.save+"+");}
  if(kind==="shield"){push("SAVE +",it.save_bonus);push("INIT",(it.init>=0?"+":"")+it.init);}
  if(S_.length)h+='<div class="sgrid">'+S_.join("")+'</div>';
  if(it.tags&&it.tags.length){h+='<div class="lbl2">KEYWORDS (tap for detail)</div><div class="atoms">'+it.tags.map(t=>kwChipHTML(t)).join(" ")+'</div>';}
  if(it.requires)h+='<div class="note">Requires: '+it.requires.map(esc).join(", ")+'</div>';
  if(it.tactics_allowed)h+='<div class="note">Tactics: '+it.tactics_allowed.map(esc).join(", ")+'</div>';
  if(it.note)h+='<div class="note">'+esc(it.note)+'</div>';
  openModal(h);
}

function optionList(sel, items, tierset, u, chosen, extra){
  // items: {name:record}; build <option>s, marking locked
  sel.innerHTML="";
  Object.keys(items).forEach(name=>{
    const it=items[name]; const o=document.createElement("option"); o.value=name;
    let ok = tierOK(it.tier, tierset);
    if(extra) ok = ok && extra(name,it);
    o.textContent=(ok?"":"🔒 ")+name+(it.tier?(" ["+it.tier+"]"):"");
    if(!ok) o.className="locked";
    sel.appendChild(o);
  });
  sel.value = chosen && items[chosen] ? chosen : sel.querySelector("option")?.value;
}

function renderArmy(){
  recomputePC();const have=new Set(Object.keys(PC));
  const {earned}=computeEarned(have);
  const u=armyUnlocks(earned);


  // top unlocks panel — everything the army can pull, in one place
  const up=document.getElementById("armyUnlocks");
  const g=(h,body)=>'<div class="grp"><span class="h">'+h+'</span>'+body+'</div>';
  const wt=[...u.wTiers].sort((a,b)=>TIER_RANK[a]-TIER_RANK[b]).join(", ");
  const modChips=u.mods.length
    ? u.mods.map(m=>'<span class="kw mod" data-tok="'+m.tok.replace(/"/g,"&quot;")+'" title="'+gloss(m.tok).replace(/"/g,"&#39;")+'">'+m.tok+' <span style="opacity:.6">('+m.node+(m.via==="mastery"?"·M":"")+')</span></span>').join(" ")
    : '<span class="note">none</span>';
  up.className="block unlocks";
  up.innerHTML='<div class="lbl">ARMY UNLOCKS &amp; MODIFIERS</div>'
    + g("Weapon tiers", wt)
    + g("Ranged", u.ranged?"yes":"no") + g("Cavalry", u.cavalry?"yes":"no")
    + g("Armor", [...u.armors].join(", "))
    + g("Shields", u.shields?("yes ("+[...unlockedShieldTiers(u)].sort((a,b)=>TIER_RANK[a]-TIER_RANK[b]).join(", ")+")"):"no")
    + g("Retinues", [...u.retinues].join(", "))
    + '<div class="grp"><span class="h">Modifiers</span></div><div class="kwrow">'+modChips+'</div>';

  // army cards
  const list=document.getElementById("armyList"); list.innerHTML="";
  S.armies.forEach(a=>list.appendChild(armyCard(a,u)));
  const tot=S.armies.reduce((s,a)=>s+(+a.upkeep||0),0);
  document.getElementById("armyTotal").textContent=fmt(-tot);
  document.getElementById("c-army").textContent=S.armies.length?("· "+S.armies.length):"";
}

function armyCard(a,u){
  if(a.open===undefined)a.open=true;
  const routed=isRouted(a);
  const card=document.createElement("div");card.className="acard"+(routed?" routed":"");

  // header: caret, label, morale summary, upkeep, remove
  const top=document.createElement("div");top.className="top";
  const car=document.createElement("span");car.className="pcaret";car.style.cursor="pointer";car.textContent=a.open?"▾":"▸";
  car.onclick=()=>{a.open=!a.open;save();render();};top.appendChild(car);
  const lab=document.createElement("input");lab.className="lab";lab.placeholder="army label";lab.value=a.label||"";
  lab.oninput=()=>{a.label=lab.value;save();};top.appendChild(lab);
  const mor=document.createElement("span");mor.className="badge "+(routed?"noearn":"tier");
  mor.textContent="morale "+effMorale(a)+"+"+(a.fatigue?(" ("+moraleBase(a)+"+ +"+(2*a.fatigue)+")"):"");top.appendChild(mor);
  const upL=document.createElement("span");upL.className="note";upL.textContent="upkeep";top.appendChild(upL);
  const up=document.createElement("input");up.type="number";up.step="100";up.style.width="80px";up.value=a.upkeep||0;
  up.oninput=()=>{a.upkeep=+up.value||0;save();computeAll();};top.appendChild(up);
  const rm=document.createElement("button");rm.className="rm";rm.textContent="✕";
  rm.onclick=()=>{S.armies=S.armies.filter(x=>x!==a);save();render();};top.appendChild(rm);
  card.appendChild(top);

  if(routed){const b=document.createElement("div");b.className="routebar";
    b.textContent="ROUTED — morale ≥ 11+, retinues drop to 0";card.appendChild(b);}
  if(!a.open) return card;

  // loadout selects
  const lo=document.createElement("div");lo.className="loadout";
  function field(labelTxt,key,items,tierset,extra){
    const f=document.createElement("div");f.className="fld";
    f.innerHTML='<label>'+labelTxt+'</label>';
    const sel=document.createElement("select");
    optionList(sel,items,tierset,u,a[key],extra);
    if(!a[key]||!items[a[key]]) a[key]=sel.value;
    sel.onchange=()=>{a[key]=sel.value;save();render();};
    f.appendChild(sel);lo.appendChild(f);return sel;
  }
  const retItems={};Object.keys(EQ.retinues).forEach(k=>retItems[k]={tier:null});
  const rsel=field("Retinue","retinue",retItems,new Set(Object.keys(EQ.retinues)),(name)=>u.retinues.has(name));
  rsel.onchange=()=>{a.retinue=rsel.value;const rt=EQ.retinues[a.retinue];if(rt){a.upkeep=rt.cost;a.endurance=rt.endurance;}save();render();};
  field("Weapon","weapon",EQ.weapons,u.wTiers,(name,it)=>reqMet(it,u)&&noteMet(it));
  const rangedItems=Object.assign({"None":{tier:null}},EQ.ranged);
  field("Ranged","ranged",rangedItems,u.wTiers,(name,it)=>name==="None"||(u.ranged&&reqMet(it,u)));
  field("Armor","armor",EQ.armors,new Set(EQ.tiers),(name)=>u.armors.has(name)||name==="Cloth");
  const shieldItems={};Object.keys(EQ.shields).forEach(k=>shieldItems[k==="null"?"None":k]=EQ.shields[k]);
  field("Shield","shield",shieldItems,unlockedShieldTiers(u),(name)=>name==="None"||u.shields);
  card.appendChild(lo);

  card.appendChild(armyStats(a,u));

  // clickable loadout chips
  const loch=document.createElement("div");loch.className="lochips";
  [["Retinue","retinue",a.retinue],["Weapon","weapon",a.weapon],["Ranged","ranged",a.ranged],
   ["Armor","armor",a.armor],["Shield","shield",a.shield]].forEach(([lbl,kind,val])=>{
    if(!val||val==="None")return;
    const c=document.createElement("span");c.className="lochip";c.dataset.kind=kind;c.dataset.item=val;
    c.innerHTML='<span class="k">'+lbl+'</span>'+esc(val);loch.appendChild(c);
  });
  card.appendChild(loch);

  // counters: retinues, endurance, fatigue
  const line=document.createElement("div");line.className="status";
  const cnt=document.createElement("div");cnt.className="endr";
  cnt.innerHTML='<span class="stat"><span class="k">RETINUES</span></span>';
  const cin=document.createElement("input");cin.type="number";cin.min="0";cin.max=EQ.army_max;cin.style.width="52px";
  cin.value=a.count||0;cin.oninput=()=>{a.count=Math.max(0,Math.min(EQ.army_max,+cin.value||0));save();};
  cnt.appendChild(cin);cnt.insertAdjacentHTML("beforeend",'<span class="note">/'+EQ.army_max+'</span>');
  line.appendChild(cnt);
  const end=document.createElement("div");end.className="endr";
  end.innerHTML='<span class="stat"><span class="k">ENDURANCE</span></span>';
  const eminus=document.createElement("button");eminus.textContent="−";eminus.onclick=()=>{a.endurance=(a.endurance||0)-1;save();render();};
  const eval_=document.createElement("span");eval_.textContent=(a.endurance!=null?a.endurance:0);
  const eplus=document.createElement("button");eplus.textContent="+";eplus.onclick=()=>{a.endurance=(a.endurance||0)+1;save();render();};
  end.appendChild(eminus);end.appendChild(eval_);end.appendChild(eplus);line.appendChild(end);
  const fat=document.createElement("div");fat.className="endr";
  fat.innerHTML='<span class="stat"><span class="k">FATIGUE</span></span>';
  const fminus=document.createElement("button");fminus.textContent="−";
  fminus.onclick=()=>{a.fatigue=Math.max(0,(a.fatigue||0)-1);save();render();};
  const fval=document.createElement("span");fval.textContent=(a.fatigue||0);
  const fplus=document.createElement("button");fplus.textContent="+";
  fplus.onclick=()=>{a.fatigue=(a.fatigue||0)+1; if(isRouted(a))a.count=0; save();render();};
  fat.appendChild(fminus);fat.appendChild(fval);fat.appendChild(fplus);line.appendChild(fat);
  card.appendChild(line);

  // status toggles
  const st=document.createElement("div");st.className="status";
  [["strained","Strained"],["blunder","Blunder"]].forEach(([key,lbl])=>{
    const c=document.createElement("span");c.className="stog"+(key==="blunder"?" blunder":"")+(a[key]?" on":"");
    c.textContent=lbl;c.onclick=()=>{a[key]=!a[key];save();render();};st.appendChild(c);
  });
  card.appendChild(st);
  return card;
}

function reqMet(it,u){ if(!it.requires)return true; return it.requires.every(r=>u.set.has(r)); }
function noteMet(it){ if(it.note&&/Needs Stable/i.test(it.note)) return !!PC["Stable"]; return true; }
// morale characteristic = retinue Shaking + 2 per Fatigue token; >=11 = instant rout
function moraleBase(a){const rt=EQ.retinues[a.retinue];return rt?rt.shaking:0;}
function effMorale(a){return moraleBase(a)+2*(a.fatigue||0);}
function isRouted(a){return effMorale(a)>=11;}

function armyStats(a,u){
  const box=document.createElement("div");box.className="stats";
  const rt=EQ.retinues[a.retinue]||{}, w=EQ.weapons[a.weapon]||{},
        r=(a.ranged&&a.ranged!=="None")?EQ.ranged[a.ranged]:null,
        ar=EQ.armors[a.armor]||{}, shKey=(a.shield==="None"||!a.shield)?"null":a.shield,
        sh=EQ.shields[shKey]||{save_bonus:0,init:0,tags:[]};
  const strikePlus=u.mods.filter(m=>m.tok==="Strike +1").length;
  const initPlus=u.mods.filter(m=>m.tok==="Init +1").length;
  const toStrike=(rt.to_hit!=null?rt.to_hit:0)-strikePlus;
  const save=(ar.save!=null?ar.save:0)-(sh.save_bonus||0);
  const wpn=r||w;
  const init=(wpn.init||0)+(sh.init||0)+initPlus;
  const stat=(k,v)=>{const s=document.createElement("span");s.className="stat";s.innerHTML='<span class="k">'+k+'</span><b>'+v+'</b>';box.appendChild(s);};
  stat("TO-STRIKE",toStrike+"+");
  stat("SAVE",save+"+");
  stat("INIT",(init>=0?"+":"")+init);
  stat("AP",(wpn.ap!=null?wpn.ap:0));
  stat("SPEED",rt.speed!=null?rt.speed:"—");
  stat("MORALE",effMorale(a)+"+"+(isRouted(a)?" ⚠":""));
  stat("BASE END",rt.endurance!=null?rt.endurance:"—");
  // keywords: weapon + ranged + shield + armor + army modifiers
  const kws=new Set([...(w.tags||[]),...(r?r.tags:[]),...(sh.tags||[]),...(ar.tags||[])]);
  const kwrow=document.createElement("div");kwrow.className="kwrow";
  [...kws].forEach(k=>{const s=document.createElement("span");s.className="kw";s.dataset.tok=k;s.title=gloss(k).replace(/"/g,"'");s.textContent=k;kwrow.appendChild(s);});
  u.mods.filter(m=>!/^(Strike|Init) \+1$/.test(m.tok)).forEach(m=>{
    const s=document.createElement("span");s.className="kw mod";s.dataset.tok=m.tok;s.title=gloss(m.tok).replace(/"/g,"'");s.textContent=m.tok;kwrow.appendChild(s);});
  const wrap=document.createElement("div");wrap.appendChild(box);
  if(kwrow.children.length)wrap.appendChild(kwrow);
  const note=document.createElement("div");note.className="note";note.style.marginTop="4px";
  note.textContent="lower To-Strike/Save = better. Keyword interactions not resolved — reference only.";
  wrap.appendChild(note);
  return wrap;
}

// ---- totals ----
function calcMetrics(have,earned,tc){
  let gold=0,reduce=0,craft=0,infl=0,faith=0,doubt=0,scale=0,infraUp=0;
  const seasonAdd={Spring:0,Summer:0,Fall:0,Winter:0};
  const phaseCount={};
  const naturalCount=Object.keys(PC).filter(n=>NATURAL.has(n)).reduce((a,n)=>a+PC[n],0);
  function eat(atoms,active,q){
    atoms.forEach(a=>{
      const ph=a.season?"season":(PHASE[a.cat]||"other");phaseCount[ph]=(phaseCount[ph]||0)+q;
      if(!active)return;
      if(a.scale){const cnt=a.scale.of==="natural"?naturalCount:(tc[cap(a.scale.of)]||0);scale+=a.scale.per*cnt*q;return;}
      if(!a.flat)return;
      if(a.season){seasonAdd[a.season]+=a.val*q;return;}
      if(a.cat==="gold")gold+=a.val*q;
      else if(a.cat==="upkeep")reduce+=(-a.val)*q;
      else if(a.cat==="craft")craft+=a.val*q;else if(a.cat==="influence")infl+=a.val*q;
      else if(a.cat==="faith")faith+=a.val*q;else if(a.cat==="doubt")doubt+=a.val*q;
    });
  }
  Object.keys(PC).forEach(n=>{const r=R[n],q=PC[n];
    eat(r.innate,true,q); if(r.mastery_raw)eat(r.mastery,!!earned[n],q);});
  Object.keys(S.infra).forEach(n=>{eat(INFRA[n].atoms,true,1);infraUp+=INFRA[n].upkeep;});
  Object.keys(S.wonders).forEach(n=>{eat(WON[n].atoms,true,1);infraUp+=WON[n].upkeep;});
  const armyGross=S.armies.reduce((s,a)=>s+(+a.upkeep||0),0);
  const netArmy=Math.max(0,armyGross-reduce);
  const unusedReduce=Math.max(0,reduce-armyGross);
  const baseNet=gold+scale-infraUp-netArmy;
  return {gold,reduce,craft,infl,faith,doubt,scale,infraUp,armyGross,netArmy,unusedReduce,baseNet,seasonAdd,phaseCount};
}
function computeTotals(have,earned,tc){
  const m=calcMetrics(have,earned,tc);
  set("t_gold",fmt(m.gold));set("t_scale",fmt(m.scale));set("t_upkeep",fmt(-m.infraUp));
  set("t_reduce",m.reduce?("pool "+fmt(m.reduce)+(m.unusedReduce?(" · "+fmt(-m.unusedReduce)+" unused"):"")):"0");
  set("t_army",fmt(-m.netArmy));set("t_craft",fmt(m.craft));
  set("t_trade",fmt(m.craft*DATA.tradePerCraft)+" g");set("t_infl",fmt(m.infl));set("t_po",fmt(m.faith-m.doubt));
  const ng=document.getElementById("netgold");ng.textContent=fmt(m.baseNet);
  ng.className="n "+(m.baseNet<0?"neg":m.baseNet>0?"pos":"");
  document.getElementById("netnote").innerHTML=
    "gold "+fmt(m.gold)+(m.scale?(" · scaling "+fmt(m.scale)):"")+" · infra "+fmt(-m.infraUp)+
    " · army ("+String(m.armyGross)+" cost − "+m.reduce+" reduce = "+fmt(-m.netArmy)+")"+
    " &nbsp;<span class='note'>(flat, active-mastery only)</span>";
  const sg=document.getElementById("seasons");sg.innerHTML="";
  SEASONS.forEach(s=>{const v=m.baseNet+m.seasonAdd[s];const c=document.createElement("div");c.className="scell";
    c.innerHTML='<div class="sn">'+s+'</div><div class="sv" style="color:'+(v<0?cvar("--upkeep"):v>m.baseNet?cvar("--income"):cvar("--ink"))+'">'+fmt(v)+'</div>';sg.appendChild(c);});
  const leg=document.getElementById("legend");leg.innerHTML="";
  Object.keys(PHASE_LABEL).forEach(ph=>{const li=document.createElement("div");li.className="li";
    li.innerHTML='<span class="sw" style="background:'+cvar(PHASE_COLOR[ph])+'"></span>'+PHASE_LABEL[ph]+(m.phaseCount[ph]?(" ("+m.phaseCount[ph]+")"):"");leg.appendChild(li);});
  window._net=m.baseNet;
}
// metrics for any board (used by dashboards)
function boardMetrics(b){
  return withBoard(b,()=>{const have=new Set(Object.keys(PC));const {earned,tc}=computeEarned(have);
    const m=calcMetrics(have,earned,tc);
    return {net:m.baseNet,gold:m.gold,craft:m.craft,infl:m.infl,po:m.faith-m.doubt,netArmy:m.netArmy};});
}

// ---- Public Order tracker ----
function poBandName(v){let best=null;Object.keys(PO).map(Number).sort((a,b)=>a-b).forEach(k=>{if(k<=v)best=k;});return best!=null?PO[String(best)]:null;}
// Public Order is cumulative in both directions: at +4 bands 1..4 are all active; at −3 bands −1..−3 are all active.
function poActiveKeys(v){return Object.keys(PO).map(Number).filter(k=>v>0?(k>=1&&k<=v):v<0?(k<=-1&&k>=v):k===0).sort((a,b)=>Math.abs(a)-Math.abs(b));}
function poActiveEffects(v){return poActiveKeys(v).map(k=>PO[String(k)]).filter(b=>b&&!/^no effect$/i.test(b[1]));}
function renderPO(){
  const v=Math.max(-5,Math.min(10,S.po||0));S.po=v;
  set("poVal",v);const band=poBandName(v);
  document.getElementById("poBand").textContent=band?band[0]:"";
  const act=poActiveEffects(v);
  document.getElementById("poEffect").textContent=act.length?("active ("+act.length+"): "+act.map(b=>b[1]).join(" · ")):"no active effects";
  const on=new Set(poActiveKeys(v)), curK=Math.max(...Object.keys(PO).map(Number).filter(k=>k<=v));
  const lad=document.getElementById("poLadder");
  lad.innerHTML=Object.keys(PO).map(Number).sort((a,b)=>b-a).map(k=>{const b=PO[String(k)];
    return '<div class="pr'+(on.has(k)?' on '+(k<0?'neg':'pos'):'')+(k===curK?' cur':'')+'"><span class="v">'+(k>0?'+':'')+k+'</span><span>'+esc(b[0])+'</span><span>'+esc(b[1])+'</span></div>';}).join("");
}

// ---- Dashboards view ----
function renderDash(){
  const host=document.getElementById("viewDash");
  const era=currentEra(),E=ERAS[era]||{};
  let h='<h2 style="margin-bottom:6px">Player dashboards</h2>'+
    '<div class="note" style="margin-bottom:10px">Renown '+(D.renown||1)+' · Era <b style="color:var(--ink)">'+era+'</b>'+
    ' — armies '+(E.armies??'?')+' / cities '+(E.cities??'?')+' / max settlements '+(E.max_settlements??'?')+' / influence '+(E.influence_per_turn||'?')+'/turn'+
    (E.unlocks?' · '+esc(E.unlocks):'')+'</div>'+
    '<table class="dtable"><thead><tr>'+
    '<th>Player</th><th>Net gold/turn</th><th>Treasury</th><th>Public Order</th>'+
    '<th>Settlements</th><th>Wards</th><th>Armies</th><th>Craft</th><th>Domain pts</th><th>Sovereign domains</th></tr></thead><tbody>';
  D.players.forEach((p,i)=>{
    const b=p.board,m=boardMetrics(b);
    let wu=0,wa=0;withBoard(b,()=>{b.settlements.forEach(s=>{const w=wardUse(s.id);wu+=w.used;wa+=w.cap;});});
    const po=Math.max(-5,Math.min(10,b.po||0)),band=poBandName(po),poAct=poActiveEffects(po);
    const sov=DOMAINS.filter(d=>((b.domains||{})[d]||0)>=10);
    const dsum=DOMAINS.reduce((a,d)=>a+((b.domains||{})[d]||0),0),dmax=DOMAINS.reduce((a,d)=>a+((D.startDomains||{})[d]||0),0)+((D.renown||1)-1),dover=dsum>dmax;
    h+='<tr>'+
      '<td><span class="pdot" style="display:inline-block;background:'+p.color+'"></span> '+esc(p.name)+(i===D.active?' <span class="note">(active)</span>':'')+'</td>'+
      '<td class="num" style="color:'+(m.net<0?cvar("--upkeep"):cvar("--income"))+'">'+fmt(m.net)+'</td>'+
      '<td class="num">'+(b.treasury||0).toLocaleString()+'</td>'+
      '<td class="num" title="'+esc(poAct.map(x=>x[0]+": "+x[1]).join("\n")||"no active effects")+'">'+po+(band?' <span class="note">'+esc(band[0])+(poAct.length?' ×'+poAct.length:'')+'</span>':'')+'</td>'+
      '<td class="num">'+b.settlements.length+'</td>'+
      '<td class="num">'+wu+'/'+wa+'</td>'+
      '<td class="num">'+b.armies.length+'</td>'+
      '<td class="num">'+m.craft+'</td>'+
      '<td class="num"'+(dover?' style="color:var(--upkeep)"':'')+'>'+dsum+'/'+dmax+(dover?' ⚠':'')+'</td>'+
      '<td class="note">'+(sov.length?sov.join(", "):"—")+'</td></tr>';
  });
  h+='</tbody></table>';host.innerHTML=h;
  if(mods().diplomacy){host.insertAdjacentHTML("beforeend",diploHTML());wireDiplo(host);}
}

function domBand(v){return v>=10?"Sovereign":v>=6?"Established":v>=3?"Rising":"Untested";}
function standingsBoardHTML(){
  let h='<div class="tot sboard"><h3 style="font-size:13px">Standings board — all players at a glance</h3>'+
    '<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:8px">'+
    D.players.map((p,i)=>'<span style="display:flex;align-items:center;gap:5px;font-size:12px;color:var(--dim)"><span class="pdotsm" style="background:'+p.color+'">'+(i+1)+'</span>'+esc(p.name)+'</span>').join('')+'</div>';
  DOMAINS.forEach(d=>{
    h+='<div class="dtrack"><div class="dname">'+d+'</div><div class="cells">';
    for(let v=0;v<=10;v++){
      const band=domBand(v).toLowerCase();
      const dots=D.players.map((p,i)=>(((p.board.domains||{})[d]||0)===v)?'<span class="pdotsm" style="background:'+p.color+'" title="'+esc(p.name)+'">'+(i+1)+'</span>':'').join('');
      h+='<div class="dcell b-'+band+'"><span>'+(v===0?'–':v)+'</span><div class="dots">'+dots+'</div></div>';
    }
    h+='</div></div>';
    h+='<div class="dctrls">'+D.players.map((p,i)=>{const v=(p.board.domains||{})[d]||0;
      return '<span class="dctrl"><span class="pdotsm" style="background:'+p.color+'">'+(i+1)+'</span>'+
        '<button class="dcbtn" data-pi="'+i+'" data-dom="'+d+'" data-delta="-1">−</button>'+
        '<span class="dcv">'+v+'</span>'+
        '<button class="dcbtn" data-pi="'+i+'" data-dom="'+d+'" data-delta="1">+</button></span>';}).join('')+'</div>';
  });
  h+='<div class="bandrow"><span>– Untested</span><span>1–3 Rising</span><span>4–6 Established</span><span>7–10 Sovereign</span></div>';
  // domain-point budget: total cube value ≤ setupTotal + (Renown − 1)   (setup pts + 1/turn)
  const setupTotal=DOMAINS.reduce((a,d)=>a+((D.startDomains||{})[d]||0),0);
  const maxAllowed=setupTotal+((D.renown||1)-1);
  h+='<div class="budget"><span class="note">Domain points (max '+maxAllowed+'):</span>'+
     D.players.map((p,i)=>{const sum=DOMAINS.reduce((a,d)=>a+((p.board.domains||{})[d]||0),0);const over=sum-maxAllowed;
       return '<span class="bchip'+(over>0?' over':'')+'"><span class="pdotsm" style="background:'+p.color+'">'+(i+1)+'</span> '+sum+'/'+maxAllowed+(over>0?' ⚠ over by '+over:'')+'</span>';}).join('')+
     '</div>';
  // shared renown track
  const era=currentEra(),eraAt={};Object.keys(ERAS).forEach(e=>eraAt[ERAS[e].renown]=e);
  h+='<div style="margin-top:8px"><div style="color:var(--dim);font-family:Georgia,serif;margin-bottom:3px">Renown (shared): '+(D.renown||1)+' · Era '+era+'</div>'+
     '<div style="display:grid;grid-template-columns:repeat(30,1fr);gap:1px">';
  for(let r=1;r<=30;r++){
    const cur=r===(D.renown||1);
    let best=null,br=-1;Object.keys(ERAS).forEach(e=>{if(ERAS[e].renown<=r&&ERAS[e].renown>br){br=ERAS[e].renown;best=e;}});
    const col=best==="Zenith"?"rgba(76,175,80,.18)":best==="Eminence"?"rgba(255,179,0,.15)":best==="Ascension"?"rgba(38,198,218,.12)":"var(--chip)";
    h+='<div title="Renown '+r+(eraAt[r]?" — "+eraAt[r]:"")+'" style="min-height:20px;border:1px solid '+(cur?"var(--ink)":"var(--line)")+';background:'+(cur?"var(--income)":col)+';border-radius:2px;font-size:8px;text-align:center;color:'+(cur?"#0c0e12":"var(--dim2)")+'">'+(cur?r:(eraAt[r]?"▲":""))+'</div>';
  }
  h+='</div></div></div>';
  return h;
}
// ============================================================================
// ---- optional modules (shared table settings) ----
function mods(){D.modules=D.modules||{};return D.modules;}

// ---- Diplomacy (Dashboards) ----
const TREATIES=DATA.treaties||{};
const TRUCE_LEN=(()=>{const m=/Truce Timer\s*(\d+)/i.exec((TREATIES["Peace Treaty"]||{}).effect||"");return m?+m[1]:0;})();
function diplo(){D.diplo=D.diplo||{};const d=D.diplo;d.pairs=d.pairs||{};d.alliances=d.alliances||{};d.member=d.member||{};d.suzerain=d.suzerain||{};return d;}
function pk(a,b){return [String(a),String(b)].sort().join("|");}
function pairOf(a,b){if(String(a)===String(b))return null;const d=diplo(),k=pk(a,b);return d.pairs[k]=d.pairs[k]||{war:false,trade:false,nap:false,truce:0};}
function pname(id){const p=D.players.find(q=>String(q.id)===String(id));return p?p.name:"?";}
function allianceLabel(gid){const a=diplo().alliances[gid];return a?(a.type+" Alliance "+gid):"";}
function pboard(id){const p=D.players.find(q=>String(q.id)===String(id));return p&&p.board||{};}
function hasRoad(id){return !!((pboard(id).infra||{})["Dirt Roads"]);}
// alliance types locked by Era (TREATIES[<type> Alliance].era)
function eraRank(e){const ks=Object.keys(ERAS).sort((a,b)=>ERAS[a].renown-ERAS[b].renown);return ks.indexOf(e);}
function allianceEra(type){return ((TREATIES[type+" Alliance"]||{}).era)||"Any";}
function allianceOK(type){const e=allianceEra(type);return e==="Any"||eraRank(currentEra())>=eraRank(e);}
function dStatus(x){return x.war?"W":x.truce>0?"TR":"P";}
// letter codes (no emoji)
const DCODE={W:"War",P:"Peace",TR:"Truce (turns left)",TA:"Trade Agreement",NAP:"Non-Aggression Pact",AL:"same Alliance",VS:"Vassal / Suzerain"};
let DIPLO_SEL=null;
function diploHTML(){
  const d=diplo(),P=D.players;
  let h='<div class="tot" style="margin-top:12px"><h3 style="font-size:13px">Diplomacy</h3>'+
    '<div class="note" style="margin-bottom:6px">'+Object.keys(DCODE).map(k=>'<b>'+k+'</b> '+DCODE[k]).join(' · ')+'</div>'+
    '<div style="overflow-x:auto"><table class="dtable"><thead><tr><th></th>'+P.map(p=>'<th><span class="pdotsm" style="background:'+p.color+'"></span> '+esc(p.name)+'</th>').join('')+'</tr></thead><tbody>';
  P.forEach(r=>{
    h+='<tr><th style="text-align:left"><span class="pdotsm" style="background:'+r.color+'"></span> '+esc(r.name)+'</th>';
    P.forEach(c=>{
      if(r.id===c.id){const g=d.member[r.id],sz=d.suzerain[r.id];
        h+='<td class="note" style="background:var(--chip);text-align:center">self'+(g?'<br>AL '+esc(allianceLabel(g)):'')+(sz?'<br>VS of '+esc(pname(sz)):'')+'</td>';return;}
      const x=pairOf(r.id,c.id),b=[];
      const st=dStatus(x);
      b.push(st==="W"?'<b style="color:var(--upkeep)">W</b>':st==="TR"?'<b style="color:var(--order)">TR'+x.truce+'</b>':'<span style="color:var(--income)">P</span>');
      if(x.trade)b.push('TA');if(x.nap)b.push('NAP');
      if(d.member[r.id]&&d.member[r.id]===d.member[c.id])b.push('AL');
      if(String(d.suzerain[r.id])===String(c.id)||String(d.suzerain[c.id])===String(r.id))b.push('VS');
      const sel=DIPLO_SEL===pk(r.id,c.id);
      h+='<td class="dpcell" data-a="'+r.id+'" data-b="'+c.id+'" style="cursor:pointer;'+(sel?'outline:2px solid var(--ink);':'')+(x.war?'background:rgba(198,40,40,.12)':'')+'">'+b.join(' ')+'</td>';});
    h+='</tr>';});
  h+='</tbody></table></div>';
  if(DIPLO_SEL){const [a,b]=DIPLO_SEL.split("|"),x=pairOf(a,b);
    const sameAl=d.member[a]&&d.member[a]===d.member[b];
    const warNo=x.war?"already at war":x.truce>0?"truce active ("+x.truce+")":x.nap?"Non-Aggression Pact in force":sameAl?"same alliance":"";
    const warFlag="";
    const trNo=x.trade?"":(!hasRoad(a)||!hasRoad(b))?"needs active Dirt Road ("+[a,b].filter(q=>!hasRoad(q)).map(pname).join(", ")+" missing)":"";
    const btn=(act,label,dis,tip)=>'<button class="dpa" data-act="'+act+'"'+(dis?' disabled title="'+esc(dis)+'"':(tip?' title="'+esc(tip)+'"':''))+'>'+esc(label)+'</button> ';
    h+='<div class="tot" style="margin-top:8px;background:var(--panel2)"><b>'+esc(pname(a))+' – '+esc(pname(b))+'</b> '+
      '<span class="note">status: <b>'+DCODE[dStatus(x)]+(x.truce>0&&!x.war?' '+x.truce:'')+'</b>'+(x.trade?' · TA':'')+(x.nap?' · NAP':'')+'</span>'+
      '<div style="margin-top:6px;display:flex;flex-wrap:wrap;gap:4px;align-items:center">'+
      btn("war","Declare War",warNo)+
      btn("peace","Peace Treaty"+(TRUCE_LEN?" (truce "+TRUCE_LEN+")":""),x.war?"":"not at war")+
      (x.trade?btn("endtrade","End Trade Agreement"):btn("trade","Trade Agreement",x.war?"at war":trNo))+
      (x.nap?btn("endnap","End NAP"+(TRUCE_LEN?" (truce "+TRUCE_LEN+")":"")):btn("nap","Non-Aggression Pact",x.war?"at war":""))+
      '<span style="margin-left:6px">Truce <button class="dpt" data-d="-1">−</button> '+x.truce+' <button class="dpt" data-d="1">+</button></span></div>'+
      '<div class="note" style="margin-top:4px">'+Object.keys(TREATIES).map(t=>'<b>'+esc(t)+'</b> ('+esc(TREATIES[t].era||'')+'): '+esc(TREATIES[t].effect||'')).join('<br>')+'</div></div>';}
  // alliances + vassals
  h+='<div style="display:flex;gap:14px;flex-wrap:wrap;margin-top:8px">'+P.map(p=>{
      const g=d.member[p.id]||"",opts=Object.keys(d.alliances).map(k=>'<option value="'+k+'"'+(k===g?' selected':'')+(!allianceOK(d.alliances[k].type)&&k!==g?' disabled':'')+'>'+esc(allianceLabel(k))+'</option>').join('');
      const sz=d.suzerain[p.id]||"";
      return '<div><span class="pdotsm" style="background:'+p.color+'"></span> '+esc(p.name)+'<br>'+
        '<select class="dal" data-p="'+p.id+'"><option value="">no alliance</option>'+opts+''+["Military","Defensive"].map(t=>'<option value="+'+t+'"'+(allianceOK(t)?'':' disabled')+'>+ new '+t+(allianceOK(t)?'':' ('+allianceEra(t)+')')+'</option>').join('')+'</select> '+
        '<select class="dvs" data-p="'+p.id+'"><option value="">not a vassal</option>'+P.filter(q=>q.id!==p.id).map(q=>'<option value="'+q.id+'"'+(String(sz)===String(q.id)?' selected':'')+'>vassal of '+esc(q.name)+'</option>').join('')+'</select></div>';}).join('')+'</div>'+
    (()=>{const bad=Object.keys(d.alliances).filter(k=>!allianceOK(d.alliances[k].type));
      return bad.length?'<div class="flagbox" style="margin-top:8px">⚑ '+bad.map(k=>esc(allianceLabel(k))+' requires '+esc(allianceEra(d.alliances[k].type))+' (now '+esc(currentEra())+')').join(' · ')+'</div>':'';})()+
    '<div style="margin-top:8px"><button id="truceTick">−1 all truce timers</button> '+
    '<span class="note">'+(DATA.allianceRules||[]).map(esc).join(' · ')+'</span></div></div>';
  return h;
}
function wireDiplo(host){
  const d=diplo();
  host.querySelectorAll(".dpcell").forEach(td=>td.onclick=()=>{if(td.dataset.a===td.dataset.b)return;const k=pk(td.dataset.a,td.dataset.b);DIPLO_SEL=DIPLO_SEL===k?null:k;render();});
  const cur=()=>{const [a,b]=DIPLO_SEL.split("|");return pairOf(a,b);};
  host.querySelectorAll(".dpt").forEach(b=>b.onclick=()=>{const x=cur();x.truce=Math.max(0,x.truce+(+b.dataset.d));save();render();});
  host.querySelectorAll(".dpa").forEach(b=>b.onclick=()=>{const x=cur();
    const act=b.dataset.act;
    if(act==="war"){if(x.nap||x.war||x.truce>0)return;x.war=true;x.trade=false;}   // declaring war ends trade
    if(act==="peace"){if(!x.war)return;x.war=false;x.truce=TRUCE_LEN;}
    if(act==="trade")x.trade=true;
    if(act==="endtrade")x.trade=false;
    if(act==="nap")x.nap=true;
    if(act==="endnap"){x.nap=false;x.truce=TRUCE_LEN;}
    save();render();});
  host.querySelectorAll(".dal").forEach(s=>s.onchange=()=>{let v=s.value;
    {const ty=v.startsWith("+")?v.slice(1):(d.alliances[v]||{}).type;if(v&&ty&&!allianceOK(ty)){s.value=d.member[s.dataset.p]||"";return;}}
    if(v.startsWith("+")){let n=1;while(d.alliances[String(n)])n++;v=String(n);d.alliances[v]={type:s.value.slice(1)};}
    if(v)d.member[s.dataset.p]=v;else delete d.member[s.dataset.p];
    Object.keys(d.alliances).forEach(k=>{if(!Object.values(d.member).includes(k))delete d.alliances[k];});save();render();});
  host.querySelectorAll(".dvs").forEach(s=>s.onchange=()=>{const me=s.dataset.p,v=s.value;
    if(v&&(String(v)===String(me)||String(d.suzerain[v])===String(me))){s.value=d.suzerain[me]||"";return;}   // no self / mutual vassalage
    if(v)d.suzerain[me]=v;else delete d.suzerain[me];save();render();});
  const tt=host.querySelector("#truceTick");if(tt)tt.onclick=()=>{Object.values(d.pairs).forEach(x=>{if(x.truce>0)x.truce--;});save();render();};
}

// ---- Battle ----
const BT=DATA.battle||{tactics:[],matrix:[]};
const TMX={};(BT.matrix||[]).forEach(([a,b,ma,mb])=>{TMX[a+"|"+b]=[ma,mb];});
function newSide(){return {pid:null,aid:null,front:null,adj:{I:0,TH:0,TS:0,M:0},cas:0};}
function battle(){D.battle=D.battle||{id:null,sk:1,round:0,dice:true,seize:"",A:newSide(),B:newSide(),rev:null,rolls:{},log:[],start:{}};return D.battle;}
const BLO=DATA.banditLoadouts||{};
function banditArmy(camp){camp.army=camp.army||{retinue:"",endurance:0,fatigue:0,weapon:"",ranged:"None",armor:"",shield:"None",strained:false};
  return new Proxy(camp.army,{get:(t,k)=>k==="count"?camp.n:k==="label"?"Bandits":t[k],
    set:(t,k,v)=>{if(k==="count")camp.n=v;else t[k]=v;return true;}});}
const BANDIT_DEFAULT_RETINUE="Levy";   // ruling: bandits default to Levies, changeable per battle
function armBandits(camp){const a=banditArmy(camp);
  if(!a.retinue&&EQ.retinues[BANDIT_DEFAULT_RETINUE]){a.retinue=BANDIT_DEFAULT_RETINUE;a.endurance=EQ.retinues[BANDIT_DEFAULT_RETINUE].endurance;}
  const lo=BLO[currentEra()];if(!lo)return;a.weapon=lo.weapon;a.armor=lo.armor;a.shield=lo.shield;}
function sideArmy(sd){
  if(sd.kind==="bandit"){const camp=mapState().camps[sd.camp];return camp?{p:null,a:banditArmy(camp),camp,bandit:true}:{};}
  const p=D.players.find(q=>String(q.id)===String(sd.pid));if(!p)return {};
  return {p,a:(p.board.armies||[]).find(x=>String(x.id)===String(sd.aid))};}
function blog(msg){const B=battle();B.log.unshift("S"+B.sk+": "+msg);B.log=B.log.slice(0,80);}
function d10(n){const r=[];for(let i=0;i<n;i++)r.push(1+Math.floor(Math.random()*10));return r;}
function sideCalc(X){
  const B=battle(),sd=B[X],o=B[X==="A"?"B":"A"],{p,a}=sideArmy(sd);if(!a)return null;
  const eo=sideArmy(o).a;
  if(!p&&!a.retinue)return null;
  const u=p?withBoard(p.board,()=>{const have=new Set(Object.keys(PC));const {earned}=computeEarned(have);
    return {mods:armyUnlocks(earned).mods,outInnate:(PC["Outrider Intercept Post"]||0)>0,outMastery:!!earned["Outrider Intercept Post"]};})
    :{mods:[],outInnate:false,outMastery:false};
  const rt=EQ.retinues[a.retinue]||{},w=EQ.weapons[a.weapon]||{},r=(a.ranged&&a.ranged!=="None")?EQ.ranged[a.ranged]:null,
        ar=EQ.armors[a.armor]||{},sh=EQ.shields[(a.shield==="None"||!a.shield)?"null":a.shield]||{save_bonus:0,init:0,tags:[]};
  const wpn=r||w;
  let ewpn={ap:0};if(eo){const ew=EQ.weapons[eo.weapon]||{},er=(eo.ranged&&eo.ranged!=="None")?EQ.ranged[eo.ranged]:null;ewpn=er||ew;}
  const strikePlus=u.mods.filter(m=>m.tok==="Strike +1").length,initPlus=u.mods.filter(m=>m.tok==="Init +1").length;
  const rev=B.rev&&B.rev.sk===B.sk?B.rev:null,cell=rev?TMX[rev.A+"|"+rev.B]:null,tm=cell?(X==="A"?cell[0]:cell[1]):{I:0,TH:0,TS:0};
  const seize=B.seize===X&&B.sk===1?1:0;
  const rawI=(wpn.init||0)+(sh.init||0)+initPlus+(tm.I||0)+seize+(a.strained?-1:0)+sd.adj.I;
  const I=Math.max(-2,Math.min(2,rawI)),blunder=I<=-2;
  const thMod=(tm.TH||0)+sd.adj.TH;
  let toStrike=(rt.to_hit||0)-strikePlus-thMod;if(blunder)toStrike=10+Math.max(0,-thMod);
  const save=(ar.save||0)-(ewpn.ap||0)-(sh.save_bonus||0)-(tm.TS||0)-sd.adj.TS;
  const morale=effMorale(a)+sd.adj.M;
  const front=Math.min(a.count||0,sd.front!=null?sd.front:(BT.frontMax||10));
  const tags=[...new Set([...(w.tags||[]),...(r?r.tags:[]),...(sh.tags||[]),...(ar.tags||[]),...u.mods.map(m=>m.tok)])];
  return {p,a,rt,I,rawI,blunder,toStrike,save,morale,front,tags,tm,seize,cell:!!cell,outrider:(u.outMastery||(u.outInnate&&B.sk===1)),outMastery:u.outMastery};
}
// hidden picks: server when online, in-page when not
const LOCAL_PICKS={};let PICKS={A:{picked:false},B:{picked:false},revealed:false},PEEK=false,_pickT=null;
function pickKey(){const B=battle();return B.sk*10+(B.round||0)%10;}
function viewerSide(){const B=battle(),me=(D.players[D.active]||{}).id;
  return String(B.A.pid)===String(me)?"A":String(B.B.pid)===String(me)?"B":"-";}
async function loadPicks(){
  const B=battle();if(!B.id)return;
  if(API.online){
    const res=await apiRaw("GET","/api/battle/"+B.id+"/"+pickKey()+"?viewer="+viewerSide()+"&peek="+(PEEK?1:0));
    if(res&&res.status===200&&res.json)PICKS=res.json;
  }else{const L=LOCAL_PICKS[B.id+":"+pickKey()]||{},v=viewerSide(),both=!!(L.A&&L.B),opp=v==="A"?"B":v==="B"?"A":null;
    PICKS={revealed:both};["A","B"].forEach(s=>{PICKS[s]={picked:!!L[s]};if(L[s]&&(both||s===v||(PEEK&&s===opp)))PICKS[s].tactic=L[s];});}
  if(PICKS.revealed&&PICKS.A.tactic&&PICKS.B.tactic&&!(B.rev&&B.rev.sk===B.sk)){
    B.rev={sk:B.sk,A:PICKS.A.tactic,B:PICKS.B.tactic};blog("Tactics revealed — A: "+B.rev.A+", B: "+B.rev.B);save();}
}
async function pickTactic(side,t){
  const B=battle();
  if(API.online){const r=await apiRaw("PUT","/api/battle/"+B.id+"/"+pickKey()+"/"+side,{tactic:t});if(r&&r.status===409)flash("both sides already locked in");}
  else{const k=B.id+":"+pickKey();LOCAL_PICKS[k]=LOCAL_PICKS[k]||{};if(!(LOCAL_PICKS[k].A&&LOCAL_PICKS[k].B))LOCAL_PICKS[k][side]=t;}
  await loadPicks();render();
}
function mdLite(t){return esc(t||"").replace(/\*\*(.+?)\*\*/g,"<b>$1</b>").replace(/\*(.+?)\*/g,"<i>$1</i>").replace(/\n/g,"<br>");}
function fmtMod(m){if(!m)return"—";const o=[];["I","TH","TS"].forEach(k=>{if(m[k])o.push(k+(m[k]>0?"+":"")+m[k]);});
  if(m.no_combat)o.push("no combat");if(m.end)o.push("ends");if(m.strain)o.push("Strained");return o.join(" ")||"·";}
function rollHTML(X){const R=(battle().rolls||{})[X];if(!R)return"";
  return '<div class="note" style="margin-top:4px">'+esc(R.kind)+' vs '+R.target+'+: '+R.dice.slice().sort((x,y)=>y-x).map(v=>'<span style="display:inline-block;min-width:18px;text-align:center;border:1px solid var(--line);margin:1px;'+(v>=R.target?'background:var(--sel);font-weight:700':'opacity:.6')+'">'+v+'</span>').join('')+
    ' → <b>'+R.succ+'</b> succeed, <b>'+(R.dice.length-R.succ)+'</b> fail'+(R.nat10?' · nat 10 ×'+R.nat10:'')+'</div>';}
function sideHTML(X){
  const B=battle(),sd=B[X],c=sideCalc(X),v=viewerSide(),mine=v===X,O=X==="A"?"B":"A";
  let h='<div class="tot" style="flex:1;min-width:300px"><h3 style="font-size:14px">Side '+X+(X==="A"?" (attacker)":"")+'</h3>'+
    '<div style="display:flex;gap:6px;flex-wrap:wrap;margin:6px 0"><select class="bsel" data-x="'+X+'" data-f="pid"><option value="">player…</option>'+
    D.players.map(p=>'<option value="'+p.id+'"'+(sd.kind!=="bandit"&&String(p.id)===String(sd.pid)?' selected':'')+'>'+esc(p.name)+'</option>').join('')+
    Object.keys(mapState().camps).map(k=>{const cp=mapState().camps[k];return '<option value="bandit:'+k+'"'+(sd.kind==="bandit"&&sd.camp===k?' selected':'')+'>☠ Bandit '+(cp.n>=(BAN.armyThreshold||25)?'Army':'Camp')+' @ '+k+' ('+cp.n+')</option>';}).join('')+'</select>';
  if(sd.kind==="bandit"){const {a}=sideArmy(sd),lo=BLO[currentEra()]||{};
    h+=a?'<select class="bret" data-x="'+X+'"><option value="">retinue…</option>'+Object.keys(EQ.retinues).map(r=>'<option'+(a.retinue===r?' selected':'')+'>'+esc(r)+'</option>').join('')+'</select></div>'+
      '<div class="note">Armed for '+esc(currentEra())+': '+esc(((BAN.equipment||{})[currentEra()])||'—')+' → '+esc([a.weapon,a.armor,a.shield].filter(x=>x&&x!=="None").join(', '))+
      ((lo.unmatched||[]).length?' <span style="color:var(--upkeep)">· not found in equipment data: '+esc(lo.unmatched.join(', '))+'</span>':'')+
      '<br>Retinue defaults to '+BANDIT_DEFAULT_RETINUE+'.</div>':'<div class="note">camp removed from map</div>';
    if(!c)return h+'</div>';}
  const pl=sd.kind==="bandit"?null:D.players.find(p=>String(p.id)===String(sd.pid));
  h+='<select class="bsel" data-x="'+X+'" data-f="aid"><option value="">army…</option>'+(pl?(pl.board.armies||[]).map(a=>'<option value="'+a.id+'"'+(String(a.id)===String(sd.aid)?' selected':'')+'>'+esc(a.label||("Army "+a.id))+' — '+esc(a.retinue||"")+' ×'+(a.count||0)+'</option>').join(''):'')+'</select></div>';
  if(sd.kind==="bandit")h=h.replace(/<select class="bsel" data-x="[AB]" data-f="aid">[\s\S]*?<\/select><\/div>$/,'');
  if(!c)return h+'<div class="note">Pick a player and one of their armies.</div></div>';
  const a=c.a,stat=(k,v,t)=>'<span class="stat" title="'+esc(t||"")+'"><span class="k">'+k+'</span><b>'+v+'</b></span>';
  h+='<div class="stats">'+stat("INIT",(c.I>=0?"+":"")+c.I+(c.rawI!==c.I?" ("+c.rawI+")":""),"clamped −2..+2")+stat("TO-STRIKE",c.toStrike+"+"+(c.blunder?" BLUNDER":""))+
    stat("SAVE vs enemy",c.save+"+","armor − enemy AP − shield − TS")+stat("MORALE",c.morale+"+"+(c.morale>=11?" ROUT":""))+
    stat("ENDURANCE",a.endurance||0)+stat("FATIGUE",a.fatigue||0)+'</div>';
  h+='<div class="note">'+(c.seize?'Seize +1 I · ':'')+(a.strained?'Strained −1 I · ':'')+(c.cell?'Tactic '+fmtMod(c.tm):'Tactic mods apply once both reveal')+'</div>';
  if(c.tags.length)h+='<div class="kwrow">'+c.tags.map(t=>'<span class="kw" data-tok="'+esc(t)+'">'+esc(t)+'</span>').join('')+'</div>';
  // retinues / front / manual adjust
  const num=(f,val,lbl)=>'<span class="dctrl"><span class="note">'+lbl+'</span><button class="badj" data-x="'+X+'" data-f="'+f+'" data-d="-1">−</button><span class="dcv">'+val+'</span><button class="badj" data-x="'+X+'" data-f="'+f+'" data-d="1">+</button></span>';
  h+='<div class="dctrls" style="margin:6px 0 0 0;flex-wrap:wrap">'+num("count",a.count||0,"retinues")+num("front",c.front,"front")+num("endurance",a.endurance||0,"end.")+num("fatigue",a.fatigue||0,"fatigue")+'</div>'+
    '<div class="dctrls" style="margin:4px 0 0 0;flex-wrap:wrap"><span class="note">enemy/other effects:</span>'+num("adj.I",sd.adj.I,"I")+num("adj.TH",sd.adj.TH,"TH")+num("adj.TS",sd.adj.TS,"TS")+num("adj.M",sd.adj.M,"Morale")+
    '<label class="note"><input type="checkbox" class="bstr" data-x="'+X+'"'+(a.strained?' checked':'')+'> Strained</label></div>';
  // tactic
  const pk2=PICKS[X]||{},op=PICKS[O]||{};
  h+='<div style="margin-top:8px"><b>Tactic</b> '+(pk2.tactic?'<span class="badge earn">'+esc(pk2.tactic)+'</span>':(pk2.picked?'<span class="badge tier">picked (hidden)</span>':'<span class="note">not picked</span>'))+'</div>';
  if(B.id&&sd.kind==="bandit"&&!(B.rev&&B.rev.sk===B.sk)){
    h+=op.picked&&!pk2.picked?'<div style="margin-top:4px"><button class="bbroll" data-x="'+X+'">roll bandit tactic (d'+(BAN.faces||10)+')</button></div>'
      :(pk2.picked?'':'<div class="note">Bandits roll their Tactic once the other side has picked.</div>');
  }
  else if(B.id&&(mine||!API.online)&&!(B.rev&&B.rev.sk===B.sk)){
    if(sideCalc(O)&&sideCalc(O).outrider&&!pk2.picked)h+='<div class="note" style="color:var(--order)">Opponent has Outrider: pick first — your Tactic is shown to them.</div>';
    h+='<div style="display:flex;flex-wrap:wrap;gap:4px;margin-top:4px">'+BT.tactics.map(t=>'<button class="btac" data-x="'+X+'" data-t="'+esc(t)+'"'+(pk2.tactic===t?' style="border-color:var(--income);color:var(--income)"':'')+'>'+esc(t)+'</button>').join('')+'</div>';
    if(mine&&c.outrider)h+='<div style="margin-top:4px"><button id="bpeek"'+(PEEK?' disabled':'')+'>Outrider: reveal opponent'+(op.picked?'':' (once they pick)')+'</button> <span class="note">'+(c.outMastery?'mastery: every Skirmish':'innate: first Skirmish')+'</span></div>';
  }
  // dice
  if(B.dice&&B.id){
    const oc=sideCalc(O),inc=(B.rolls[O]&&B.rolls[O].kind==="Strike")?B.rolls[O].succ:0;
    h+='<div style="display:flex;gap:4px;flex-wrap:wrap;margin-top:8px">'+
      '<button class="broll" data-x="'+X+'" data-k="Strike">Strike ×'+c.front+'</button>'+
      '<button class="broll" data-x="'+X+'" data-k="Parry">Parry ×'+inc+'</button>'+
      '<button class="broll" data-x="'+X+'" data-k="Save">Save ×'+inc+'</button>'+
      '<button class="broll" data-x="'+X+'" data-k="Morale">Morale ×'+Math.min(c.front,BT.moraleDiceMax||5)+'</button>'+
      '<input type="number" min="0" value="'+inc+'" class="bn" data-x="'+X+'" style="width:52px" title="dice count override for Parry/Save">'+
      '</div>'+rollHTML(X);
  }
  h+='<div style="display:flex;gap:4px;align-items:center;margin-top:6px"><span class="note">casualties</span><input type="number" min="0" value="0" class="bcas" data-x="'+X+'" style="width:52px"><button class="bcasgo" data-x="'+X+'">apply</button>'+
    '<span class="note">this Skirmish: '+(sd.cas||0)+((BT.panicThreshold&&sd.cas>=BT.panicThreshold)?' — <b style="color:var(--upkeep)">Panic check before striking back</b>':'')+'</span></div>';
  return h+'</div>';
}
function renderBattle(){
  const host=document.getElementById("viewBattle"),B=battle();
  let h='<div style="padding:14px;overflow-y:auto;height:100%"><h2 style="margin-bottom:6px">Battle</h2>'+
    '<div class="toolbar"><button id="bStart">'+(B.id?'restart battle':'start battle')+'</button>'+
    '<span class="note">Skirmish <b>'+(B.id?B.sk:'—')+'</b></span>'+
    '<label class="note">Seize the Initiative: <select id="bSeize"><option value="">—</option><option value="A"'+(B.seize==="A"?" selected":"")+'>A</option><option value="B"'+(B.seize==="B"?" selected":"")+'>B</option></select></label>'+
    '<label class="note"><input type="checkbox" id="bDice"'+(B.dice?' checked':'')+'> emulate dice</label>'+
    (B.id?'<button id="bReset">reset picks</button><button id="bEndSk" style="border-color:var(--order)">end Skirmish ▸</button><button id="bEndBattle" style="border-color:var(--upkeep)">end Battle</button>':'')+'</div>';
  const v=viewerSide();
  h+='<div class="note" style="margin-bottom:6px">Viewing as <b>'+esc((D.players[D.active]||{}).name||"?")+'</b>'+(v==="-"?' (spectator — switch player in the top bar to pick)':' = side '+v)+(API.online?'':' · no server: picks stay on this device (pass-and-play)')+'</div>';
  if(B.rev&&B.rev.sk===B.sk){const cell=TMX[B.rev.A+"|"+B.rev.B];
    h+='<div class="tot"><b>Revealed:</b> A '+esc(B.rev.A)+' ('+fmtMod(cell&&cell[0])+') · B '+esc(B.rev.B)+' ('+fmtMod(cell&&cell[1])+')</div>';}
  const cA=sideCalc("A"),cB=sideCalc("B");
  if(cA&&cB)h+='<div class="note" style="margin-bottom:6px">'+(cA.I===cB.I?'<b>Simultaneous</b> — both sides Strike with their full front line':'Strikes first: <b>'+(cA.I>cB.I?"A":"B")+'</b>')+' (I '+cA.I+' vs '+cB.I+')</div>';
  h+='<div style="display:flex;gap:10px;flex-wrap:wrap">'+sideHTML("A")+sideHTML("B")+'</div>';
  h+='<div class="tot"><h3 style="font-size:13px">Log</h3><div class="note">'+(B.log||[]).map(esc).join('<br>')+'</div></div>';
  h+='<details class="tot"><summary><b>Rules — Skirmish steps</b></summary><div class="note" style="margin-top:6px">'+mdLite(BT.seize)+'<br><br>'+mdLite(BT.steps)+'<br><br><b>Resolve Battle</b><br>'+mdLite(BT.resolve)+
    ((BT.tacticalGlobal||[]).length?'<br><br>'+BT.tacticalGlobal.map(esc).join('<br>'):'')+'</div></details>';
  h+='<details class="tot"><summary><b>Tactic matrix</b> <span class="note">(row = A, column = B; cell = A mods | B mods)</span></summary><div style="overflow-x:auto"><table class="dtable" style="font-size:11px"><thead><tr><th>A \\ B</th>'+
    BT.tactics.map(t=>'<th>'+esc(t)+'</th>').join('')+'</tr></thead><tbody>'+BT.tactics.map(a=>'<tr><th>'+esc(a)+'</th>'+BT.tactics.map(b=>{const c=TMX[a+"|"+b];
      return '<td>'+(c?fmtMod(c[0])+' | '+fmtMod(c[1]):'')+'</td>';}).join('')+'</tr>').join('')+'</tbody></table></div></details></div>';
  host.innerHTML=h;wireBattle(host);
}
function roll(X,kind,nOverride){
  const B=battle(),c=sideCalc(X);if(!c)return;const O=X==="A"?"B":"A";
  const inc=(B.rolls[O]&&B.rolls[O].kind==="Strike")?B.rolls[O].succ:0;
  let n,target;
  if(kind==="Strike"){n=c.front;target=c.toStrike;}
  else if(kind==="Parry"){n=nOverride!=null?nOverride:inc;target=BT.parryBase||8;}
  else if(kind==="Save"){n=nOverride!=null?nOverride:inc;target=c.save;}
  else{n=Math.min(c.front,BT.moraleDiceMax||5);target=c.morale;}
  const dice=d10(n).sort((x,y)=>y-x),succ=dice.filter(v=>v>=target).length,nat10=dice.filter(v=>v===10).length;
  B.rolls[X]={kind,target,dice,succ,nat10};
  blog(X+" "+kind+" "+n+"d10 vs "+target+"+ ["+dice.join(",")+"] → "+succ+" succeed"+(kind==="Morale"?", "+(n-succ)+" casualties":"")+(nat10?" (nat 10 ×"+nat10+")":""));
  save();render();
}
function applyCas(X,n){const {a}=sideArmy(battle()[X]);if(!a||!n)return;n=Math.min(n,a.count||0);a.count-=n;battle()[X].cas=(battle()[X].cas||0)+n;blog(X+" loses "+n+" retinue(s) → "+a.count);save();render();}
function endSkirmish(){
  const B=battle();const cell=B.rev&&B.rev.sk===B.sk?TMX[B.rev.A+"|"+B.rev.B]:null;
  ["A","B"].forEach((X,i)=>{const c=sideCalc(X);if(!c)return;const a=c.a,tm=cell?cell[i]:null;
    if(!tm||tm.endurance_loss!==false){a.endurance=Math.max(0,(a.endurance||0)-1);}
    if((a.endurance||0)===0){
      if(B.dice){const n=Math.min(c.front,BT.moraleDiceMax||5),dice=d10(n).sort((x,y)=>y-x),fail=dice.filter(v=>v<c.morale).length,lost=Math.min(fail,a.count||0);
        a.count-=lost;blog(X+" Fatigued — Break check "+n+"d10 vs "+c.morale+"+ ["+dice.join(",")+"] → "+lost+" casualties");}
      else blog(X+" Fatigued — take Break check (morale "+c.morale+"+, up to "+(BT.moraleDiceMax||5)+" dice)");
      a.fatigue=(a.fatigue||0)+1;blog(X+" gains Fatigue token ("+a.fatigue+") → morale "+effMorale(a)+"+");}
    if(tm&&tm.strain){a.strained=true;blog(X+" becomes Strained");}
    if(tm&&tm.end)blog(X+" tactic ends the Battle (Fall Back)");
    if(effMorale(a)>=11)blog(X+" ROUTS (morale "+effMorale(a)+"+)");
    if((a.count||0)===0)blog(X+" wiped out");
    B[X].cas=0;});
  B.sk++;B.round=0;B.rev=null;B.rolls={};PEEK=false;blog("— Skirmish begins —");save();loadPicks().then(render);
}
function endBattle(){
  const B=battle();
  ["A","B"].forEach(X=>{const c=sideCalc(X);if(!c)return;c.a.fatigue=0;});
  ["A","B"].forEach(X=>{const O=X==="A"?"B":"A",oc=sideCalc(O);if(!oc)return;
    const lost=Math.max(0,(B.start[O]||0)-(oc.a.count||0)),cost=(oc.rt.cost||0)*lost;
    blog(X+" destroyed "+lost+" "+(oc.a.retinue||"")+" — spoils if "+X+" won: "+cost.toLocaleString()+" gold");});
  blog("Battle ended — Fatigue tokens removed");B.id=null;B.rev=null;B.rolls={};save();render();
}
function wireBattle(host){
  const B=battle();
  host.querySelectorAll(".bsel").forEach(s=>s.onchange=()=>{const sd=B[s.dataset.x];
    if(s.dataset.f==="pid"&&s.value.startsWith("bandit:")){sd.kind="bandit";sd.camp=s.value.slice(7);sd.pid=null;sd.aid=null;
      const cp=mapState().camps[sd.camp];if(cp)armBandits(cp);}
    else{if(s.dataset.f==="pid"){sd.kind=null;sd.camp=null;sd.aid=null;}sd[s.dataset.f]=s.value||null;}
    save();render();});
  host.querySelectorAll(".bret").forEach(s=>s.onchange=()=>{const {a}=sideArmy(B[s.dataset.x]);if(!a)return;
    a.retinue=s.value;const rt=EQ.retinues[s.value];if(rt)a.endurance=rt.endurance;save();render();});
  host.querySelectorAll(".bbroll").forEach(b=>b.onclick=()=>{const v=1+Math.floor(Math.random()*(BAN.faces||10)),t=dieLookup(BAN.tacticTable,v);
    blog(b.dataset.x+" bandits roll d"+(BAN.faces||10)+": "+v+" → "+t);save();pickTactic(b.dataset.x,t);});
  const st=host.querySelector("#bStart");if(st)st.onclick=()=>{
    if(!sideCalc("A")||!sideCalc("B")){flash("pick both armies first");return;}
    if(B.id&&!confirm("Restart the battle?"))return;
    ["A","B"].forEach(X=>{if(B[X].kind==="bandit"){const cp=mapState().camps[B[X].camp];if(cp)armBandits(cp);}});
    B.id=Date.now().toString(36);B.sk=1;B.round=0;B.rev=null;B.rolls={};B.log=[];PEEK=false;
    B.start={A:sideCalc("A").a.count||0,B:sideCalc("B").a.count||0};B.A.cas=0;B.B.cas=0;blog("Battle begins");save();loadPicks().then(render);};
  const sz=host.querySelector("#bSeize");if(sz)sz.onchange=()=>{B.seize=sz.value;save();render();};
  const dc=host.querySelector("#bDice");if(dc)dc.onchange=()=>{B.dice=dc.checked;save();render();};
  const rs=host.querySelector("#bReset");if(rs)rs.onclick=()=>{B.round=(B.round||0)+1;B.rev=null;PEEK=false;blog("Tactic picks reset");save();loadPicks().then(render);};
  const es=host.querySelector("#bEndSk");if(es)es.onclick=endSkirmish;
  const eb=host.querySelector("#bEndBattle");if(eb)eb.onclick=()=>{if(confirm("End the battle? Removes Fatigue tokens."))endBattle();};
  host.querySelectorAll(".btac").forEach(b=>b.onclick=()=>pickTactic(b.dataset.x,b.dataset.t));
  const pe=host.querySelector("#bpeek");if(pe)pe.onclick=()=>{PEEK=true;loadPicks().then(render);};
  host.querySelectorAll(".badj").forEach(b=>b.onclick=()=>{const X=b.dataset.x,f=b.dataset.f,dl=+b.dataset.d,sd=B[X],{a}=sideArmy(sd);
    if(f.startsWith("adj.")){sd.adj[f.slice(4)]+=dl;}
    else if(f==="front"){const c=sideCalc(X);sd.front=Math.max(0,c.front+dl);}
    else if(a){a[f]=Math.max(0,(a[f]||0)+dl);if(f==="count"&&a.count>EQ.army_max)a.count=EQ.army_max;}
    save();render();});
  host.querySelectorAll(".bstr").forEach(cb=>cb.onchange=()=>{const {a}=sideArmy(B[cb.dataset.x]);if(a){a.strained=cb.checked;save();render();}});
  host.querySelectorAll(".broll").forEach(b=>b.onclick=()=>{const X=b.dataset.x,k=b.dataset.k,inp=host.querySelector('.bn[data-x="'+X+'"]');
    roll(X,k,(k==="Parry"||k==="Save")&&inp?Math.max(0,+inp.value||0):null);});
  host.querySelectorAll(".bcasgo").forEach(b=>b.onclick=()=>{const inp=host.querySelector('.bcas[data-x="'+b.dataset.x+'"]');applyCas(b.dataset.x,Math.max(0,+inp.value||0));});
}
setInterval(()=>{if((D.view==="battle")&&battle().id&&!editing()){const before=JSON.stringify(PICKS);loadPicks().then(()=>{if(JSON.stringify(PICKS)!==before)render();});}},2000);
// ---- Edict scoreboard ----
// RULES: any Edict repeatable; each completion = +1 shared Renown; most Edicts wins.
const EDICT_NAMES=Object.keys(EDICTS);
const NUMWORD={one:1,two:2,three:3,four:4,five:5,six:6,seven:7,eight:8,nine:9,ten:10};
function edictTimerLen(e){const m=/(\w+)\s+consecutive turns/i.exec(e.requirement||"");if(!m)return 0;
  const w=m[1].toLowerCase();return NUMWORD[w]||(+w)||0;}
function edictChoices(name,pi){const e=EDICTS[name]||{};
  if(e.type==="Standing")return DOMAINS.slice();
  if(/monument/i.test(name))return NAMES.filter(n=>R[n]&&R[n].monument);
  if(/wonder/i.test(name))return Object.keys(WON||{});
  if(e.type==="Conquest")return D.players.filter((q,j)=>j!==pi).map(q=>q.name);
  return null;}
function edictTotal(p){const L=p.board.edictLog||{};return EDICT_NAMES.reduce((a,k)=>a+((L[k]||[]).length),0);}
function edictOwners(name,label){const o=[];D.players.forEach((q,j)=>{if(((q.board.edictLog||{})[name]||[]).includes(label))o.push("P"+(j+1));});return o;}
function bumpRenown(d){D.renown=Math.max(1,Math.min(30,(D.renown||1)+d));}
function edictBoardHTML(){
  const P=D.players,tot=P.map(edictTotal),best=Math.max(0,...tot);
  let h='<div class="tot" style="max-width:1000px"><h3 style="font-size:13px">Edicts — scoreboard</h3>'+
    '<div style="overflow-x:auto"><table class="dtable edb"><thead><tr><th>Edict</th>'+
    P.map((p,i)=>'<th style="min-width:130px"><span class="pdotsm" style="background:'+p.color+'">'+(i+1)+'</span> '+esc(p.name)+'</th>').join('')+
    '</tr></thead><tbody>';
  EDICT_NAMES.forEach((name,ek)=>{const e=EDICTS[name],tl=edictTimerLen(e);
    h+='<tr><td title="'+esc(e.requirement||"")+'"><b>'+esc(name)+'</b><div class="note">'+esc(e.type||"")+(tl?' · '+tl+'-turn timer':'')+'</div></td>';
    P.map((p,pi)=>{const L=(p.board.edictLog||{})[name]||[],ch=edictChoices(name,pi);
      let c='<div style="display:flex;align-items:center;gap:6px"><span class="edn">'+L.length+'</span>';
      if(ch){c+='<select class="edsel" data-pi="'+pi+'" data-ek="'+ek+'" style="max-width:120px"><option value="">+ add…</option>'+
        ch.map(o=>{const own=edictOwners(name,o);return '<option value="'+esc(o)+'">'+esc(o)+(own.length?' ('+own.join(',')+')':'')+'</option>';}).join('')+'</select>';}
      else c+='<button class="edb-act" data-act="add" data-pi="'+pi+'" data-ek="'+ek+'">+</button>';
      c+='</div>';
      if(L.length)c+='<div style="display:flex;flex-wrap:wrap;gap:3px;margin-top:4px">'+
        L.map((lab,ix)=>'<span class="badge tier">'+esc(lab||"✓")+' <a href="#" class="edb-act" data-act="del" data-pi="'+pi+'" data-ek="'+ek+'" data-ix="'+ix+'" style="color:var(--upkeep);text-decoration:none">×</a></span>').join('')+'</div>';
      if(tl){const t=(p.board.edictTimers||{})[name]||0,done=t>=tl;
        c+='<div style="display:flex;align-items:center;gap:4px;margin-top:4px;font-size:11px">'+
          '<span class="note" style="color:'+(done?'var(--income)':'var(--dim)')+'">timer '+t+'/'+tl+'</span>'+
          '<button class="edb-act" data-act="tadd" data-pi="'+pi+'" data-ek="'+ek+'">+1</button>'+
          '<button class="edb-act" data-act="treset" data-pi="'+pi+'" data-ek="'+ek+'">reset</button>'+
          (done?'<button class="edb-act" data-act="claim" data-pi="'+pi+'" data-ek="'+ek+'" style="border-color:var(--income);color:var(--income)">claim</button>':'')+'</div>';}
      h+='<td style="vertical-align:top">'+c+'</td>';});
    h+='</tr>';});
  h+='<tr><td><b>Total</b></td>'+tot.map(t=>'<td class="num" style="font-size:16px;'+(t===best&&best>0?'color:var(--income);font-weight:700':'')+'">'+t+(t===best&&best>0?' ★':'')+'</td>').join('')+'</tr>';
  h+='</tbody></table></div></div>';
  return h;
}
function wireEdicts(host){
  const log=(pi,name)=>{const b=D.players[pi].board;b.edictLog=b.edictLog||{};return b.edictLog[name]=b.edictLog[name]||[];};
  host.querySelectorAll("select.edsel").forEach(sel=>{sel.onchange=()=>{if(!sel.value)return;
    log(+sel.dataset.pi,EDICT_NAMES[+sel.dataset.ek]).push(sel.value);bumpRenown(1);save();render();};});
  host.querySelectorAll(".edb-act").forEach(el=>{el.onclick=ev=>{ev.preventDefault();
    const pi=+el.dataset.pi,name=EDICT_NAMES[+el.dataset.ek],b=D.players[pi].board,act=el.dataset.act;
    b.edictTimers=b.edictTimers||{};
    if(act==="add"||act==="claim"){log(pi,name).push("");bumpRenown(1);}
    else if(act==="del"){log(pi,name).splice(+el.dataset.ix,1);bumpRenown(-1);}
    else if(act==="tadd"){b.edictTimers[name]=(b.edictTimers[name]||0)+1;}
    else if(act==="treset"){b.edictTimers[name]=0;}
    save();render();};});
}
// ---- Renown & Domains view ----
function currentEra(){
  let best=null,bestR=-1;
  Object.keys(ERAS).forEach(e=>{const r=ERAS[e].renown;if(r<=(D.renown||1)&&r>bestR){bestR=r;best=e;}});
  return best||Object.keys(ERAS)[0];
}
function renderRenown(){
  const host=document.getElementById("viewRenown");
  const era=currentEra(),E=ERAS[era]||{};
  const eraOrder=Object.keys(ERAS).sort((a,b)=>ERAS[a].renown-ERAS[b].renown);
  let h='<h2 style="margin-bottom:10px">Renown &amp; Domains</h2>';

  // shared renown + era
  h+='<div class="tot" style="max-width:1000px"><div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">'+
     '<span class="k">Renown (shared)</span>'+
     '<button id="rnMinus">−</button><input id="rnVal" type="number" min="1" max="30" value="'+(D.renown||1)+'" style="width:70px">'+
     '<button id="rnPlus">+</button>'+
     '<span class="badge mon" style="font-size:13px">Era: '+era+'</span></div>'+
     '<table class="dtable" style="margin-top:8px"><thead><tr><th>Era</th><th>Renown</th><th>Armies</th><th>Cities</th><th>Max settlements</th><th>Influence/turn</th><th>Unlocks</th></tr></thead><tbody>'+
     eraOrder.map(e=>{const x=ERAS[e];const on=e===era;
       return '<tr'+(on?' style="background:var(--sel)"':'')+'><td>'+(on?'● ':'')+e+'</td><td class="num">'+x.renown+'</td><td class="num">'+x.armies+'</td><td class="num">'+x.cities+'</td><td class="num">'+x.max_settlements+'</td><td class="num">'+x.influence_per_turn+'</td><td>'+esc(x.unlocks||'—')+'</td></tr>';}).join('')+
     '</tbody></table>'+
     (E.envoys?'<div class="note" style="margin-top:6px">Envoys: '+esc(E.envoys)+'</div>':'')+'</div>';

  h+=edictBoardHTML();

  h+=standingsBoardHTML();

  // starting universe (default domain allocation)
  h+='<div class="tot" style="max-width:1000px"><h3 style="font-size:13px">Starting universe — domains new players begin with</h3>'+
     '<div class="dctrls" style="margin-left:0">'+DOMAINS.map(d=>{const v=(D.startDomains||{})[d]||0;
       return '<span class="dctrl"><span class="note" style="min-width:64px">'+d+'</span>'+
         '<button class="sdbtn" data-dom="'+d+'" data-delta="-1">−</button><span class="dcv">'+v+'</span>'+
         '<button class="sdbtn" data-dom="'+d+'" data-delta="1">+</button></span>';}).join('')+
     '</div><div style="margin-top:6px"><button id="applyStart">apply to all players</button></div></div>';

  // standing effects (actions) for the active player, achieved highlighted
  const ap=D.players[D.active],ab=ap.board;
  h+='<div class="tot" style="max-width:1000px"><h3 style="font-size:13px">Standing effects — '+esc(ap.name)+'</h3>'+
     '';
  DOMAINS.forEach(d=>{const v=(ab.domains||{})[d]||0;
    h+='<div style="margin-bottom:8px"><div style="color:var(--dim);font-family:Georgia,serif;margin-bottom:2px">'+d+' <span class="note">(cube '+v+' · '+domBand(v)+')</span></div>';
    ["Rising","Established","Sovereign"].forEach(st=>{const eff=(DBOARD[d]||{})[st]||"";const has=v>=STAND_THRESH[st];
      h+='<div style="display:flex;gap:8px;padding:3px 6px;border-left:3px solid '+(has?'var(--income)':'var(--line)')+';opacity:'+(has?'1':'.55')+';margin-bottom:2px">'+
         '<span style="min-width:88px;color:'+(has?'var(--income)':'var(--dim2)')+'">'+st+' ('+STAND_THRESH[st]+')</span>'+
         '<span>'+esc(eff)+'</span></div>';});
    h+='</div>';});
  h+='</div>';

  host.innerHTML=h;
  document.getElementById("rnPlus").onclick=()=>{D.renown=Math.min(30,(D.renown||1)+1);save();render();};
  document.getElementById("rnMinus").onclick=()=>{D.renown=Math.max(1,(D.renown||1)-1);save();render();};
  document.getElementById("rnVal").onchange=e=>{D.renown=Math.max(1,Math.min(30,+e.target.value||1));save();render();};
  host.querySelectorAll(".dcbtn").forEach(b=>b.onclick=()=>{
    const i=+b.dataset.pi,dom=b.dataset.dom,dl=+b.dataset.delta,bd=D.players[i].board;
    bd.domains=bd.domains||{};bd.domains[dom]=Math.max(0,Math.min(10,(bd.domains[dom]||0)+dl));save();render();});
  host.querySelectorAll(".sdbtn").forEach(b=>b.onclick=()=>{
    const dom=b.dataset.dom,dl=+b.dataset.delta;D.startDomains=D.startDomains||{};
    D.startDomains[dom]=Math.max(0,Math.min(10,(D.startDomains[dom]||0)+dl));save();render();});
  const ap2=document.getElementById("applyStart");if(ap2)ap2.onclick=()=>{
    if(confirm("Set every player's domains to the starting values?")){
      D.players.forEach(p=>{p.board.domains=Object.assign({},D.startDomains);});save();render();}};
  wireEdicts(host);
}

// ---- Map view ----
// ---- Map view: region generator (gen.js) + free placement + Outlaw Country + Bandits ----
const MG=(typeof RenownGen!=="undefined")?RenownGen:null, MP=(typeof RenownPresets!=="undefined")?RenownPresets:{};
const BAN=DATA.bandits||{};
const BOARD_SIZE={2:[19,15],3:[23,18],4:[26,21],5:[29,24],6:[32,26],7:[35,28]};   // mirrors renown-maps.html
const TCOL={plains:'#96b060',forest:'#2e5c34',wetland:'#5e7054',tundra:'#d6dad6',mountain:'#6e6864',water:'#4a748c'};
// region art palettes (mirror of mapgen/app_shell.html PALETTES); picked from the map's `art`, else its preset's
const TPAL={default:TCOL,
  wastes:Object.assign({},TCOL,{plains:'#d4b84e',tundra:'#c49854',mountain:'#7d7469'}),
  scarlet:Object.assign({},TCOL,{plains:'#bc5442',forest:'#7a2224',wetland:'#6d4038'})};
const RULE_NAME={plains:'Grassland',forest:'Forest',wetland:'Wetlands',tundra:'Tundra',mountain:'Mountains',water:'Water'};
const TREF=DATA.terrainRef||{terrain:{},movement:{},tactical:{},tacticalGlobal:[]};
function mapArt(g){if(!g)return {};return (g.art&&Object.keys(g.art).length)?g.art:((MP[g.preset]||{}).art||{});}
function mapPal(g){const a=mapArt(g);return TPAL[a.plains?(a.plains==='wastes'?'wastes':'scarlet'):'default'];}
const RCOL={mine:'#161616',quarry:'#8a3b2e',arable:'#7a4f2a',forestry:'#2f5d2f',apiary:'#e8c020',salt:'#ece6d6'};
const C2T={p:'plains',f:'forest',w:'wetland',t:'tundra',m:'mountain','~':'water'};
let MAPVIEW=null;                                   // decoded grid cache {sig, hex:{key:{t,res,reg,hill}}}
function mapState(){const M=D.map;M.cells=M.cells||{};M.outlaw=M.outlaw||{};M.camps=M.camps||{};return M;}
function hexDist(a,b){if(MG)return MG.dist(a,b);
  const cu=(c,r)=>{const x=c,z=r-((c-(c&1))>>1);return [x,-x-z,z];},A=cu(a[0],a[1]),B=cu(b[0],b[1]);
  return (Math.abs(A[0]-B[0])+Math.abs(A[1]-B[1])+Math.abs(A[2]-B[2]))/2;}
function decodeGrid(g){
  const sig=g?(g.preset+":"+g.seed+":"+g.width+"x"+g.height+":"+(g.terrain||[]).join("").length):"none";
  if(MAPVIEW&&MAPVIEW.sig===sig)return MAPVIEW;
  const hex={};
  if(g){let m=null;try{if(MG)m=MG.importMap(g);}catch(e){m=null;}
    for(let c=0;c<g.width;c++)for(let r=0;r<g.height;r++){const k=c+","+r;
      const h=m?m.get([c,r]):null;
      hex[k]={t:C2T[(g.terrain[c]||"")[r]]||"plains",res:(g.resources||{})[k]||null,reg:(g.regions||{})[k],hill:!!(h&&h.tactical==="hill")};}}
  MAPVIEW={sig,hex};return MAPVIEW;
}
function seedCode(g){return g?(g.preset+"/"+g.seed+"/"+g.players+"/"+g.width+"x"+g.height):"";}
function generateMap(preset,seed,players,w,h){
  if(!MG||!MP[preset]){flash("map generator not bundled");return false;}
  const res=MG.generateRegion(MP[preset],{seed:+seed,players:+players,width:+w,height:+h});
  const ex=MG.exportMap(res.map,res.params,+seed,res.violations);
  const M=mapState();M.grid=ex;M.cols=ex.width;M.rows=ex.height;M.seed=String(seed);MAPVIEW=null;
  if(ex.violations&&ex.violations.length)flash("generated with "+ex.violations.length+" validator note(s)");
  return true;
}
function parseSeedCode(s){ // Region/seed/players[/WxH]
  const p=String(s||"").split("/").map(x=>x.trim());if(p.length<3)return null;
  const [preset,seed,pl]=p,wh=(p[3]||"").split("x"),n=+pl,def=BOARD_SIZE[n]||BOARD_SIZE[6];
  if(!MP[preset]||isNaN(+seed)||!n)return null;
  return {preset,seed:+seed,players:n,w:+wh[0]||def[0],h:+wh[1]||def[1]};
}
function mapSVG(M){
  const V=decodeGrid(M.grid),g=M.grid,cols=g?g.width:(M.cols||16),rows=g?g.height:(M.rows||12);
  const R=15,dx=1.5*R,dy=Math.sqrt(3)*R,W=cols*dx+R*2,H=rows*dy+dy,PAL=mapPal(g);
  const pts=(cx,cy)=>{let a=[];for(let k=0;k<6;k++){const t=Math.PI/180*60*k;a.push((cx+R*Math.cos(t)).toFixed(1)+","+(cy+R*Math.sin(t)).toFixed(1));}return a.join(" ");};
  const lighten=(hex,k)=>{const n=parseInt(hex.slice(1),16),f=v=>Math.min(255,Math.round(v*k));
    return "#"+[f(n>>16&255),f(n>>8&255),f(n&255)].map(v=>v.toString(16).padStart(2,"0")).join("");};
  const letter={Army:"A",Hamlet:"Ha",Village:"V",Town:"T",City:"C",Metropolis:"M"};
  let s='<svg width="'+W.toFixed(0)+'" height="'+H.toFixed(0)+'" style="display:block"><defs><pattern id="olh" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="3" height="6" fill="rgba(120,20,20,.45)"/></pattern></defs>';
  for(let c=0;c<cols;c++)for(let r=0;r<rows;r++){
    const k=c+","+r,cx=R+c*dx,cy=dy/2+r*dy+(c%2?dy/2:0),h=V.hex[k];
    let fill=h?PAL[h.t]:"var(--chip)";if(h&&h.hill)fill=lighten(fill,1.16);
    s+='<polygon data-cell="'+k+'" points="'+pts(cx,cy)+'" fill="'+fill+'" stroke="#00000030" stroke-width="1" style="cursor:pointer"><title>'+k+(h?" · "+(RULE_NAME[h.t]||h.t)+(h.hill?" (Hill)":"")+(h.res?" · "+h.res:"")+(h.reg!=null?" · region "+h.reg:""):"")+'</title></polygon>';
    if(M.outlaw[k])s+='<polygon points="'+pts(cx,cy)+'" fill="url(#olh)" stroke="#7a1414" stroke-width="1.5" pointer-events="none"/>';
    if(h&&h.res&&M.showRes!==false)s+='<circle cx="'+cx.toFixed(1)+'" cy="'+(cy+R*.45).toFixed(1)+'" r="'+(R*.22).toFixed(1)+'" fill="'+RCOL[h.res]+'" stroke="#0006" pointer-events="none"/>';
  }
  if(g&&M.showStarts)(g.settlements||[]).forEach(reg=>reg.forEach(st=>{const cx=R+st[0]*dx,cy=dy/2+st[1]*dy+(st[0]%2?dy/2:0),w=R*.42;
    s+='<rect x="'+(cx-w).toFixed(1)+'" y="'+(cy-w).toFixed(1)+'" width="'+(w*2).toFixed(1)+'" height="'+(w*2).toFixed(1)+'" fill="none" stroke="#b3392f" stroke-width="1.6" stroke-dasharray="3 2" pointer-events="none"/>';}));
  Object.keys(M.cells).forEach(k=>{const cell=M.cells[k],[c,r]=k.split(",").map(Number),cx=R+c*dx,cy=dy/2+r*dy+(c%2?dy/2:0);
    const pl=D.players.find(pp=>pp.id===cell.player),col=pl?pl.color:"#888";
    s+='<circle cx="'+cx.toFixed(1)+'" cy="'+cy.toFixed(1)+'" r="'+(R*.62).toFixed(1)+'" fill="'+col+'" stroke="#111" pointer-events="none"/>'+
       '<text x="'+cx.toFixed(1)+'" y="'+(cy+4).toFixed(1)+'" text-anchor="middle" font-size="10" font-weight="700" fill="#fff" pointer-events="none">'+(letter[cell.type]||"?")+'</text>';});
  Object.keys(M.camps).forEach(k=>{const cp=M.camps[k],[c,r]=k.split(",").map(Number),cx=R+c*dx,cy=dy/2+r*dy+(c%2?dy/2:0),army=cp.n>=(BAN.armyThreshold||25);
    s+='<rect x="'+(cx-R*.62).toFixed(1)+'" y="'+(cy-R*.5).toFixed(1)+'" width="'+(R*1.24).toFixed(1)+'" height="'+(R).toFixed(1)+'" fill="'+(army?"#5a0d0d":"#1b1b1b")+'" stroke="#e0b060" pointer-events="none"/>'+
       '<text x="'+cx.toFixed(1)+'" y="'+(cy+3.5).toFixed(1)+'" text-anchor="middle" font-size="9" font-weight="700" fill="#f3d38a" pointer-events="none">☠'+cp.n+'</text>';});
  return s+'</svg>';
}
function outlawReport(M){
  const V=decodeGrid(M.grid),by={},warn=[];
  const cen=(M.grid&&M.grid.centers)||[];
  Object.keys(M.outlaw).forEach(k=>{const h=V.hex[k],a=k.split(",").map(Number);
    let rg=h&&h.reg!=null?h.reg:null;
    if(rg===null&&cen.length){let bd=1e9;cen.forEach((c,i)=>{const d=hexDist(a,c);if(d<bd){bd=d;rg=i;}});}
    rg=rg===null?"?":rg;by[rg]=(by[rg]||0)+1;
    Object.keys(M.cells).forEach(sk=>{const cell=M.cells[sk];if(cell.type==="Army")return;
      const b=sk.split(",").map(Number);if(BAN.outlawBuffer&&hexDist(a,b)<BAN.outlawBuffer)warn.push(k+" is within "+BAN.outlawBuffer+" of "+cell.type+" "+sk);});});
  return {by,warn};
}
function banditDomain(n){return Math.floor(n/5)*2;}
const STAND_INF={Untested:1,Rising:2,Established:3,Sovereign:4};
function envoyOutcome(net){const T=BAN.outcomeThresh||{};
  if(T.Condemned!=null&&net<=T.Condemned)return "Condemned";
  if(T.Failed!=null&&net<=T.Failed)return "Failed";
  if(T.Endorsed!=null&&net>=T.Endorsed)return "Endorsed";
  return "Passed";}
function banditCunningHTML(k,cp){
  const cv=banditDomain(cp.n),st=domBand(cv),inf=STAND_INF[st]||1,mod=+cp.cmod||0,net=inf+mod,oc=envoyOutcome(net);
  const col=oc==="Condemned"||oc==="Failed"?"var(--upkeep)":"var(--income)";
  const O=BAN.cunningOutcomes||{},A=BAN.cunningActions||{},tbl=BAN.cunningTable||[],canRoll=cp.n>=(BAN.cunningMin||10);
  const act=cp.croll?dieLookup(tbl,cp.croll):null;
  let h='<div class="bcun"><div class="bcrow"><span><b>Cunning</b> '+cv+' · '+st+'</span><span>Influence '+inf+'</span>'+
    '<span>mod <input class="bcm" data-k="'+k+'" type="number" value="'+mod+'" style="width:48px"></span>'+
    '<span>net <b>'+net+'</b> → <b style="color:'+col+'">'+oc+'</b></span></div>';
  if(O[oc.toLowerCase()])h+='<div class="note">'+esc(oc)+': '+esc(O[oc.toLowerCase()])+'</div>';
  h+='<table class="dtable ttab" style="margin-top:4px"><thead><tr><th>d'+(BAN.faces||10)+'</th><th>Action</th><th>Effect</th></tr></thead><tbody>'+
    tbl.map(([lo,hi,a])=>{const on=cp.croll&&cp.croll>=lo&&cp.croll<=hi;
      return '<tr'+(on?' class="broll"':'')+'><td>'+(lo===hi?lo:lo+'–'+hi)+'</td><td>'+esc(a)+'</td><td>'+esc((A[a]||{}).effect||'')+(on&&oc==="Endorsed"&&(A[a]||{}).endorsed?' <b>Endorsed:</b> '+esc(A[a].endorsed):'')+'</td></tr>';}).join('')+'</tbody></table>';
  h+='<div class="bcrow" style="margin-top:4px">'+(canRoll?'<button class="bcr" data-k="'+k+'" data-r="cunning">roll d'+(BAN.faces||10)+'</button>':'<span class="note">'+(BAN.cunningMin||10)+'+ retinues to roll</span>')+
    '<span>rolled <input class="bcv" data-k="'+k+'" type="number" min="1" max="'+(BAN.faces||10)+'" value="'+(cp.croll||'')+'" style="width:48px"'+(canRoll?'':' disabled')+'></span>'+
    (act?'<span>→ <b>'+esc(act)+'</b></span>':'')+'</div></div>';
  return h;
}
function dieLookup(tbl,v){const x=(tbl||[]).find(([lo,hi])=>v>=lo&&v<=hi);return x?x[2]:"?";}
function terrainTablesHTML(PAL){
  const T=TREF.terrain||{},MV=TREF.movement||{},X=TREF.tactical||{};
  const sw=(c,hill)=>'<i class="tsw" style="background:'+c+(hill?';filter:brightness(1.16)':'')+'"></i>';
  const fx=v=>Array.isArray(v)?v.join(' '):(v||'—');
  let h='<div class="ttwrap"><div class="tot"><h3 style="font-size:13px">Terrain</h3><table class="dtable ttab"><thead><tr><th>Terrain</th><th>Effect</th><th>Raw Materials</th></tr></thead><tbody>';
  Object.keys(RULE_NAME).forEach(k=>{const nm=RULE_NAME[k],e=T[nm]||{};
    h+='<tr><td>'+sw(PAL[k])+esc(nm)+'</td><td>'+esc(fx(e.Effect))+'</td><td>'+esc((e["Raw Materials"]||[]).join(", ")||'—')+'</td></tr>';});
  if(T.Hill)h+='<tr><td>'+sw(PAL.plains,1)+'Hill</td><td>'+esc(fx(T.Hill.Effect))+'</td><td>—</td></tr>';
  h+='</tbody></table></div>';
  if(Object.keys(MV).length)h+='<div class="tot"><h3 style="font-size:13px">Movement</h3><table class="dtable ttab"><thead><tr><th>Source</th><th>Effect</th></tr></thead><tbody>'+
    Object.keys(MV).map(k=>'<tr><td>'+esc(k)+'</td><td>'+esc(fx((MV[k]||{}).Effect))+'</td></tr>').join('')+'</tbody></table></div>';
  if(Object.keys(X).length){h+='<div class="tot"><h3 style="font-size:13px">Battle terrain</h3><table class="dtable ttab"><thead><tr><th>Tile</th><th>Map</th><th>Effect</th></tr></thead><tbody>'+
    Object.keys(X).map(k=>'<tr><td>'+esc(k)+'</td><td>'+esc(X[k].identify||'')+'</td><td>'+esc(X[k].effect||'')+'</td></tr>').join('')+'</tbody></table>';
    if((TREF.tacticalGlobal||[]).length)h+='<div class="note" style="margin-top:4px">'+TREF.tacticalGlobal.map(esc).join(' ')+'</div>';h+='</div>';}
  return h+'</div>';
}
function renderMap(){
  const host=document.getElementById("viewMap"),M=mapState(),g=M.grid;
  const tools=["Army","Hamlet","Village","Town","City","Metropolis","Outlaw Country","Bandit Camp","Erase"];
  const p=D.players[D.active],era=currentEra();
  const presets=Object.keys(MP),np=D.players.length>=2?Math.min(7,D.players.length):4,def=BOARD_SIZE[np]||BOARD_SIZE[6];
  let h='<div style="padding:10px;overflow-y:auto;height:100%"><div class="mtoolbar">'+
    (MG?'<select id="mPreset">'+presets.map(n=>'<option'+((g?g.preset:"Default")===n?' selected':'')+'>'+esc(n)+'</option>').join('')+'</select>'+
      ' seed <input id="mSeedN" type="number" value="'+esc(g?g.seed:(M.seed||Math.floor(Math.random()*100000)))+'" style="width:80px">'+
      ' players <input id="mPl" type="number" min="2" max="7" value="'+(g?g.players:np)+'" style="width:46px">'+
      ' size <input id="mW" type="number" value="'+(g?g.width:def[0])+'" style="width:46px">×<input id="mH" type="number" value="'+(g?g.height:def[1])+'" style="width:46px">'+
      ' <button id="mGen">generate</button>':'<span class="note">map generator not bundled — JSON import only</span>')+
    ' <input id="mCode" placeholder="Region/seed/players[/WxH]" style="width:210px" value="'+esc(seedCode(g))+'"><button id="mCodeGo">load code</button>'+
    ' <button id="mImp">import map JSON</button><input type="file" id="mFile" accept="application/json" style="display:none">'+
    '</div><div class="mtoolbar">tool <select id="mTool">'+tools.map(t=>'<option'+(t===mtool?' selected':'')+'>'+t+'</option>').join('')+'</select>'+
    ' <span class="note">placing as</span> <span class="pdot" style="display:inline-block;background:'+p.color+'"></span> '+esc(p.name)+
    ' <label class="note"><input type="checkbox" id="mRes"'+(M.showRes!==false?' checked':'')+'> resources</label>'+
    ' <label class="note"><input type="checkbox" id="mStarts"'+(M.showStarts?' checked':'')+'> suggested settlement spots</label>'+
    ' <button id="mClear">clear markers</button></div>';
  h+='<div class="note" style="margin-bottom:6px">'+(g?'Board: <b>'+esc(g.preset)+'</b> seed '+g.seed+' · '+g.players+' players · '+g.width+'×'+g.height+' · generator '+esc(g.generator||'?')+
      '':'No terrain loaded')+'</div>';
  h+='<div style="display:flex;gap:10px;align-items:flex-start;flex-wrap:wrap"><div class="hexwrap" style="flex:1;min-width:320px">'+mapSVG(M)+'</div>';
  // side panel: outlaw + bandits
  const rep=outlawReport(M);
  h+='<div style="width:420px;max-width:100%"><div class="tot"><h3 style="font-size:13px">Outlaw Country</h3>'+
    '<div class="note">'+(BAN.outlawStart?BAN.outlawStart+' per player at setup, within range 1 of each other, range '+BAN.outlawBuffer+'+ from any Settlement.':'')+'</div>'+
    '<div style="margin-top:4px">'+(Object.keys(rep.by).length?Object.keys(rep.by).map(rg=>'<span class="badge tier">region '+esc(rg)+': '+rep.by[rg]+'</span>').join(' '):'<span class="note">none marked</span>')+'</div>'+
    (rep.warn.length?'<div class="note" style="color:var(--upkeep);margin-top:4px">'+rep.warn.slice(0,6).map(esc).join('<br>')+'</div>':'')+'</div>';
  const camps=Object.keys(M.camps);
  h+='<div class="tot"><h3 style="font-size:13px">Bandits</h3><div class="note">Era '+esc(era)+': grow +'+((BAN.growth||{})[era]||0)+'/turn · armed with '+esc((BAN.equipment||{})[era]||'—')+
    ' · camp starts at '+(BAN.campStart||'?')+', becomes an Army at '+(BAN.armyThreshold||'?')+'.</div>'+
    '<div style="margin:6px 0"><button id="bGrow">grow all camps</button> <button id="bSpawn">spawn at selected hex</button></div>';
  camps.forEach(k=>{const cp=M.camps[k],army=cp.n>=(BAN.armyThreshold||25),dv=banditDomain(cp.n);
    h+='<div style="border-top:1px solid var(--line);padding:5px 0"><b>'+(army?'Bandit Army':'Bandit Camp')+'</b> <span class="note">@ '+k+'</span>'+
      '<div class="dctrls" style="margin:3px 0 0 0"><span class="dctrl"><span class="note">retinues</span><button class="bcn" data-k="'+k+'" data-d="-1">−</button><span class="dcv">'+cp.n+'</span><button class="bcn" data-k="'+k+'" data-d="1">+</button></span>'+
      '<span class="note">treasury</span><input class="bct" data-k="'+k+'" type="number" step="100" value="'+(cp.gold||0)+'" style="width:80px"></div>'+
      '<div class="note">Prowess +'+dv+'</div>'+banditCunningHTML(k,cp)+
      '<div style="display:flex;gap:4px;margin-top:3px">'+
      '<button class="bcr" data-k="'+k+'" data-r="tactic">tactic roll</button><button class="bcx" data-k="'+k+'">remove</button></div>'+
      (cp.last?'<div class="note">'+esc(cp.last)+'</div>':'')+'</div>';});
  h+='</div></div></div>'+terrainTablesHTML(mapPal(g))+'</div>';
  host.innerHTML=h;
  const $=id=>document.getElementById(id);
  if(MG){$("mGen").onclick=()=>{if(g&&!confirm("Replace the current terrain? Markers stay."))return;
      if(generateMap($("mPreset").value,$("mSeedN").value,$("mPl").value,$("mW").value,$("mH").value)){save();render();}};
    $("mPl").onchange=()=>{const d=BOARD_SIZE[+$("mPl").value];if(d){$("mW").value=d[0];$("mH").value=d[1];}};}
  $("mCodeGo").onclick=()=>{const c=parseSeedCode($("mCode").value);if(!c){flash("code format: Region/seed/players[/WxH]");return;}
    if(generateMap(c.preset,c.seed,c.players,c.w,c.h)){save();render();}};
  $("mImp").onclick=()=>$("mFile").click();
  $("mFile").onchange=e=>{const f=e.target.files[0];if(!f)return;const rd=new FileReader();
    rd.onload=()=>{try{const j=JSON.parse(rd.result);if(!j.terrain||!j.width)throw 0;M.grid=j;M.cols=j.width;M.rows=j.height;M.seed=String(j.seed);MAPVIEW=null;save();render();}
      catch(err){flash("not a renown-maps JSON export");}};rd.readAsText(f);};
  $("mTool").onchange=e=>{mtool=e.target.value;};
  $("mRes").onchange=e=>{M.showRes=e.target.checked;save();render();};
  $("mStarts").onchange=e=>{M.showStarts=e.target.checked;save();render();};
  $("mClear").onclick=()=>{if(confirm("Clear settlements, armies, Outlaw Country and camps? Terrain stays.")){M.cells={};M.outlaw={};M.camps={};save();render();}};
  host.querySelectorAll("[data-cell]").forEach(el=>el.onclick=()=>{
    const k=el.dataset.cell;MAPSEL=k;
    if(mtool==="Erase"){delete M.cells[k];delete M.outlaw[k];delete M.camps[k];}
    else if(mtool==="Outlaw Country"){if(M.outlaw[k])delete M.outlaw[k];else M.outlaw[k]=true;}
    else if(mtool==="Bandit Camp"){if(!M.camps[k])M.camps[k]={n:BAN.campStart||5,gold:0};}
    else M.cells[k]={type:mtool,player:D.players[D.active].id};
    save();render();});
  $("bGrow").onclick=()=>{const gr=(BAN.growth||{})[era]||0,cap=BAN.armyThreshold||25;Object.values(M.camps).forEach(cp=>{cp.n=Math.min(cap,cp.n+gr);});save();render();};
  $("bSpawn").onclick=()=>{if(!MAPSEL){flash("click a hex first");return;}if(!M.camps[MAPSEL])M.camps[MAPSEL]={n:BAN.campStart||5,gold:0};save();render();};
  host.querySelectorAll(".bcn").forEach(b=>b.onclick=()=>{const cp=M.camps[b.dataset.k];cp.n=Math.max(0,Math.min(BAN.armyThreshold||25,cp.n+(+b.dataset.d)));save();render();});
  host.querySelectorAll(".bct").forEach(i=>i.onchange=()=>{M.camps[i.dataset.k].gold=+i.value||0;save();});
  host.querySelectorAll(".bcx").forEach(b=>b.onclick=()=>{delete M.camps[b.dataset.k];save();render();});
  host.querySelectorAll(".bcr").forEach(b=>b.onclick=()=>{const cp=M.camps[b.dataset.k],v=1+Math.floor(Math.random()*(BAN.faces||10));
    if(b.dataset.r==="cunning")cp.croll=v;else cp.last="Tactic d"+(BAN.faces||10)+": "+v+" → "+dieLookup(BAN.tacticTable,v);save();render();});
  host.querySelectorAll(".bcv").forEach(i=>i.onchange=()=>{const cp=M.camps[i.dataset.k];if(!cp)return;const v=Math.round(+i.value),F=BAN.faces||10,nv=(v>=1&&v<=F)?v:null;
    if(nv===(cp.croll||null))return;cp.croll=nv;save();setTimeout(render,0);});
  host.querySelectorAll(".bcm").forEach(i=>i.onchange=()=>{const cp=M.camps[i.dataset.k];if(!cp)return;const nv=Math.round(+i.value)||0;
    if(nv===(+cp.cmod||0))return;cp.cmod=nv;save();setTimeout(render,0);});
}
let MAPSEL=null;
function set(id,v){const e=document.getElementById(id);if(e)e.textContent=v;}
function computeAll(){recomputePC();const have=new Set(Object.keys(PC));const {earned,craft,tc}=computeEarned(have);computeTotals(have,earned,tc);renderArmy();}

// ---- settlements overview (read-only; build/place happens in the Pursuits section) ----
function renderSettlements(){
  const grid=document.getElementById("setGrid");grid.innerHTML="";const SET=DATA.settlements;
  const byTier={};S.settlements.forEach(s=>byTier[s.tier]=(byTier[s.tier]||0)+1);
  let avail=0,used=0,tax=0;
  S.settlements.forEach(s=>{const wu=wardUse(s.id);avail+=wu.cap;used+=wu.used;tax+=(SET[s.tier].tax_income||0);});
  Object.keys(byTier).forEach(t=>{
    const lbl=document.createElement("div");
    lbl.innerHTML=t+' ×'+byTier[t]+' <span class="note">('+SET[t].wards+'w'+(SET[t].tax_income?', '+SET[t].tax_income+'g':'')+')</span>';
    const sp=document.createElement("div");sp.className="note";sp.textContent="";
    grid.appendChild(lbl);grid.appendChild(sp);
  });
  if(!S.settlements.length){const d=document.createElement("div");d.className="note";d.textContent="no settlements — add them in the Pursuits section";grid.appendChild(d);grid.appendChild(document.createElement("div"));}
  const unplaced=S.placed.filter(p=>p.sid==null).length;
  document.getElementById("wards").textContent=used+" / "+avail+(unplaced?("  ("+unplaced+" unplaced)"):"");
  document.getElementById("tax").textContent=fmt(tax);
  const bar=document.getElementById("wardbar");bar.innerHTML="";const pct=avail?Math.min(100,used/avail*100):0;
  const f=document.createElement("span");f.style.width=pct+"%";f.style.background=used>avail?cvar("--upkeep"):cvar("--income");
  const rest=document.createElement("span");rest.style.width=(100-pct)+"%";rest.style.background=cvar("--barbg");
  bar.appendChild(f);bar.appendChild(rest);
}

// ---- treasury ----
const trIn=document.getElementById("treasury");
trIn.value=S.treasury;document.getElementById("turn").textContent=S.turn;
document.getElementById("autoNet").checked=S.autoNet;
trIn.oninput=()=>{S.treasury=+trIn.value||0;save();};
document.getElementById("autoNet").onchange=e=>{S.autoNet=e.target.checked;save();};
document.getElementById("endturn").onclick=()=>{
  S.turn++;
  if(S.autoNet){S.treasury+=Math.round(window._net||0);trIn.value=S.treasury;}
  const dpo=boardMetrics(S).po;                         // Faith − Doubt this turn
  S.po=Math.max(-5,Math.min(10,(S.po||0)+dpo));
  S.armies.forEach(a=>{if(!a.strained)a.endurance=(a.endurance||0)+EQ.endurance_regain; a.strained=false;});
  document.getElementById("turn").textContent=S.turn;save();render();
};
document.getElementById("poMinus").onclick=()=>{S.po=Math.max(-5,(S.po||0)-1);save();render();};
document.getElementById("poPlus").onclick=()=>{S.po=Math.min(10,(S.po||0)+1);save();render();};
document.querySelectorAll("[data-gold]").forEach(b=>b.onclick=()=>{S.treasury=(S.treasury||0)+(+b.dataset.gold);trIn.value=S.treasury;save();});

// ---- toolbar ----
document.getElementById("clear").onclick=()=>{const b=activeBoard();b.placed=[];b.settlements=startSettlements();b.infra={};b.wonders={};b.armies=[];reindex();save();render();renderList();};
document.getElementById("export").onclick=()=>{const b=new Blob([JSON.stringify(D,null,2)],{type:"application/json"});
  const a=document.createElement("a");a.href=URL.createObjectURL(b);a.download="renown_build.json";a.click();};
document.getElementById("import").onclick=()=>document.getElementById("file").click();
document.getElementById("file").onchange=e=>{const f=e.target.files[0];if(!f)return;const rd=new FileReader();
  rd.onload=()=>{try{const j=JSON.parse(rd.result); if(j&&j.players){D=j;}else{D={players:[newPlayer(1)],active:0,view:D.view,renown:1,map:D.map};D.players[0].board=Object.assign(newBoard(),j);} normalizeD(); D.active=0; reindex();
    trIn.value=S.treasury;document.getElementById("turn").textContent=S.turn;document.getElementById("autoNet").checked=S.autoNet;
    save();render();renderList();}catch(err){alert("bad json");}};rd.readAsText(f);};
document.getElementById("addArmy").onclick=()=>{const L=EQ.retinues.Levy||{};S.armies.push({id:aid++,label:"",upkeep:L.cost||0,retinue:"Levy",count:1,endurance:L.endurance||0,fatigue:0,weapon:"Farm Tools",ranged:"None",armor:"Cloth",shield:"None",strained:false,blunder:false,open:true});save();render();};
document.getElementById("hideCombat").onchange=render;
document.getElementById("search").oninput=renderList;

document.getElementById("ver").textContent=DATA.version;
if(DATA.warnings&&DATA.warnings.length)document.getElementById("assump").innerHTML="<span class='warn'>"+DATA.warnings.join("<br>")+"</span>";
else document.getElementById("assump").closest("details").remove();

document.addEventListener("click",e=>{
  const it=e.target.closest("[data-item]"); if(it){inspectItem(it.dataset.kind,it.dataset.item);return;}
  const k=e.target.closest("[data-tok]"); if(k){inspectKeyword(k.dataset.tok);return;}
});
document.getElementById("inspect").onclick=e=>{if(e.target.id==="inspect")closeModal();};
document.addEventListener("keydown",e=>{if(e.key==="Escape")closeModal();});

// ---- server build management ----
async function refreshBuilds(){
  const res=await apiFetch("GET","/api/builds");
  const sel=document.getElementById("buildList");
  if(!res||!res.builds){sel.innerHTML='<option value="">— saved builds —</option>';return;}
  sel.innerHTML='<option value="">— saved builds —</option>'+
    res.builds.map(b=>'<option value="'+esc(b.name)+'">'+esc(b.name)+' ('+(b.updated_at||"").slice(0,16).replace("T"," ")+')</option>').join("");
}
document.getElementById("buildSave").onclick=async()=>{
  const name=document.getElementById("buildName").value.trim();if(!name){flash("name the build first");return;}
  const r=await apiFetch("PUT","/api/builds/"+encodeURIComponent(name),{data:S});
  flash(r?("saved “"+name+"”"):"no server — use export instead");refreshBuilds();
};
document.getElementById("buildSnap").onclick=async()=>{
  const name=document.getElementById("buildName").value.trim()||"autosnap";
  const r=await apiFetch("POST","/api/builds/"+encodeURIComponent(name)+"/snapshot",{data:S});
  flash(r?("snapshot recorded"):"no server");
};
document.getElementById("buildLoad").onclick=async()=>{
  const name=document.getElementById("buildList").value;if(!name){flash("pick a build");return;}
  const r=await apiFetch("GET","/api/builds/"+encodeURIComponent(name));
  if(r&&r.data){const j=r.data; if(j.players){D=j;}else{D.players[0].board=Object.assign(newBoard(),j);} normalizeD(); reindex();document.getElementById("buildName").value=name;save();render();flash("loaded “"+name+"”");}
  else flash("load failed");
};
document.getElementById("buildDel").onclick=async()=>{
  const name=document.getElementById("buildList").value;if(!name){flash("pick a build");return;}
  await apiFetch("DELETE","/api/builds/"+encodeURIComponent(name));refreshBuilds();flash("deleted “"+name+"”");
};
async function initServer(){
  const tok=document.getElementById("srvToken");
  if(tok){tok.value=TOKEN;tok.onchange=()=>{TOKEN=tok.value.trim();try{localStorage.setItem("renown_token",TOKEN);}catch(e){}initServer();};}
  SYNC.ready=false;
  const res=await apiRaw("GET","/api/state");       // full server state
  if(!res||res.status!==200||!res.json)return;
  const j=res.json;SYNC.base={};SYNC.ver={};SYNC.rev=j.rev;
  Object.keys(j.parts).forEach(k=>{SYNC.base[k]=j.parts[k].data;SYNC.ver[k]=j.parts[k].version;});
  if(j.parts.shared){joinD(Object.fromEntries(Object.keys(j.parts).map(k=>[k,j.parts[k].data])));reindex();render();renderList();}
  SYNC.ready=true;
  if(!j.parts.shared)push();                         // empty server: seed it from this browser
  refreshBuilds();
}
setInterval(poll,POLL_MS);

buildFilters();document.getElementById("typeFilters").style.display="flex";renderList();render();
initServer();
</script>
</body>
</html>
"""

def check_rules(ns, rules_path):
    """Cross-check a few key constants in the rules doc against the data file / tool logic.
    Prints a report; returns the number of hard MISMATCHes."""
    if not os.path.exists(rules_path):
        print(f"rules file not found: {rules_path}"); return 0
    txt = open(rules_path, encoding="utf-8").read().replace("\u2212", "-")   # normalise unicode minus
    WORD = {"one":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7,"eight":8,"nine":9,"ten":10}
    rows = []   # (name, data/tool value, rules value, status)
    def add(name, dv, rv):
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
    add("PO min", min(keys) if keys else "?", int(m.group(1)) if m else None)
    add("PO max", max(keys) if keys else "?", int(m.group(2)) if m else None)

    # Endurance regain per turn
    add("Endurance regain / turn", ns.get("ENDURANCE_REGAIN", "?"),
        find(r"gains?\s*\+(\d+)\s*Endurance"))

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
    add("Standing: Rising at",     3,  r_rising)
    add("Standing: Established at",6,  r_est)
    add("Standing: Sovereign at",  10, r_sov)

    # Influence by standing (data DOMAIN_BOARD.max_influence_per_vote vs rules)
    mip = ns.get("DOMAIN_BOARD", {}).get("max_influence_per_vote", {})
    m = re.search(r"Untested\s*(\d+),?\s*Rising\s*(\d+),?\s*Established\s*(\d+),?\s*Sovereign\s*(\d+)", txt, re.I)
    for i, st in enumerate(["Untested", "Rising", "Established", "Sovereign"]):
        add(f"Influence cap: {st}", mip.get(st, "?"), int(m.group(i+1)) if m else None)

    # Era thresholds (data ERAS vs rules — not present in doc)
    for e, x in ns.get("ERAS", {}).items():
        present = re.search(r"\b"+re.escape(e)+r"\b", txt)
        add(f"Era {e} @ Renown", x.get("renown", "?"), find(r"\b"+re.escape(e)+r"\b.*?(\d+)") if present else None)

    # Tool combat logic vs rules (known drift point)
    add("Fatigue: Morale penalty / token", 2, find(r"each token is\s*-(\d+)\s*to that Army"))
    add("Fatigue: rout at modified Morale", 11, find(r"modified to\s*(\d+)\s*or more Routs"))

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
    txt = "\n".join(out).strip()
    def sub(m):
        v = _val(ns, m.group(1).strip())
        return str(v) if v is not None else m.group(0)
    return re.sub(r"\{\{VAL:([^}]+)\}\}", sub, txt)

def battle_data(ns, rules_path):
    M = ns.get("TACTIC_MATRIX", {})
    return {
        "tactics": list(ns.get("TACTICS", [])),
        "matrix": [[a, b, ma, mb] for (a, b), (ma, mb) in M.items()],
        "frontMax": ns.get("FRONT_LINE_MAX"), "reserveMax": ns.get("RESERVE_MAX"),
        "moraleDiceMax": ns.get("MORALE_DICE_MAX"), "parryBase": ns.get("PARRY_BASE"),
        "panicThreshold": ns.get("PANIC_CASUALTY_THRESHOLD"), "fatigueMorale": ns.get("FATIGUE_MORALE"),
        "tacticalGlobal": list(ns.get("TACTICAL_GLOBAL", [])),
        "steps": rules_section(rules_path, "The Skirmish Steps", ns),
        "seize": rules_section(rules_path, "Begin the Battle — Seize the Initiative", ns),
        "resolve": rules_section(rules_path, "Resolve Battle", ns),
    }

def bandit_loadouts(ns, equip):
    """Map BANDIT_EQUIPMENT_PER_ERA prose onto equipment names. Exact name match only
    (a trailing plural 's' is dropped); anything unmatched is reported, not guessed."""
    cats = {"weapon": equip.get("weapons", {}), "armor": equip.get("armors", {}),
            "shield": {k: v for k, v in equip.get("shields", {}).items() if k != "null"}}
    out, warns = {}, []
    for era, txt in (ns.get("BANDIT_EQUIPMENT_PER_ERA") or {}).items():
        lo = {"weapon": "Farm Tools", "armor": "Cloth", "shield": "None", "unmatched": []}
        found = {"weapon": False, "armor": False, "shield": False}
        for tok in re.split(r"\s*(?:,|\+|&)\s*", str(txt)):
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

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="renown_data_d10.py")
    ap.add_argument("--out", default="settlement_board.html")
    ap.add_argument("--rules", default="RULES_reorganized_6.md")
    ap.add_argument("--mapgen", default="", help="folder with gen.js + presets.js (default: <data dir>/mapgen or ../mapgen)")
    ap.add_argument("--check-rules", action="store_true",
                    help="cross-check key constants in the rules doc against the data file, then exit")
    a = ap.parse_args()
    if not os.path.exists(a.data):
        sys.exit(f"data file not found: {a.data}")
    ns = load(a.data)
    if a.check_rules:
        sys.exit(1 if check_rules(ns, a.rules) else 0)
    (records, natural, external, infra, wonders,
     army_src, equip, glossary) = build(ns)
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
        records=records, naturalNames=natural, externalTokens=external,
        infra=infra, wonders=wonders, armySrc=army_src, equip=equip, glossary=glossary,
        domainBoard=ns.get("DOMAIN_BOARD", {}), publicOrder=po,
        eras=ns.get("ERAS", {}), edicts=ns.get("EDICTS", {}),
        domains=["Industry", "Prowess", "Cunning", "Piety"],
        standings=["Rising", "Established", "Sovereign"],
        tradePerCraft=ns.get("TRADE_RULES", {}).get("income_per_craft", 100),
        settlements=ns.get("SETTLEMENTS", {}),
        battle=battle_data(ns, rules_path),
        terrainRef={"terrain": ns.get("TERRAIN", {}), "movement": ns.get("MOVEMENT_MODIFIERS", {}),
                    "tactical": ns.get("TACTICAL_TERRAIN", {}), "tacticalGlobal": list(ns.get("TACTICAL_GLOBAL", []))},
        banditLoadouts=b_lo,
        bandits={
            "campStart": ns.get("BANDIT_CAMP_START"), "armyThreshold": ns.get("BANDIT_ARMY_THRESHOLD"),
            "growth": ns.get("BANDIT_GROWTH_PER_ERA", {}), "equipment": ns.get("BANDIT_EQUIPMENT_PER_ERA", {}),
            "cunningMin": ns.get("BANDIT_CUNNING_MIN"), "faces": ns.get("BANDIT_FACES"),
            "outlawStart": ns.get("OUTLAW_COUNTRY_START"), "outlawBuffer": ns.get("OUTLAW_BUFFER_RANGE"),
            "cunningTable": [list(x) for x in ns["die_table_ranges"](ns["BANDIT_CUNNING_TABLE"])] if "die_table_ranges" in ns and "BANDIT_CUNNING_TABLE" in ns else [],
            "tacticTable": [list(x) for x in ns["die_table_ranges"](ns["BANDIT_TACTIC_TABLE"])] if "die_table_ranges" in ns and "BANDIT_TACTIC_TABLE" in ns else [],
            "outcomeThresh": ns.get("ENVOY_OUTCOME_THRESHOLDS", {}),
            "cunningOutcomes": ns.get("ENVOY_OUTCOMES", {}).get("Cunning", {}),
            "cunningActions": {k: {"effect": v.get("effect", ""), "endorsed": v.get("endorsed", ""), "cost": v.get("cost", "")}
                               for k, v in ns.get("ACTIONS", {}).items() if v.get("domain") == "Cunning"},
        },
        treaties=ns.get("TREATIES", {}), allianceRules=list(ns.get("ALLIANCE_RULES", [])),
        warnings=b_warn, version=ns.get("VERSION", "?"),
    )
    with open(a.out, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"wrote {a.out}  ({len(records)} pursuits, {len(infra)} infra, "
          f"{len(wonders)} wonders, {len(army_src)} army-tag nodes)")

if __name__ == "__main__":
    main()