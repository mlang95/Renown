#!/usr/bin/env python3
"""pursuit_review.py — generate a single self-contained HTML page for reviewing
every pursuit in renown_data.NODES. Read-only: scan, filter, sort, spot problems,
then edit renown_data.py itself.

Usage:  python pursuit_review.py [pursuit_review.html]
Open the resulting .html in any browser. No dependencies.
"""
import sys, html, json
sys.path.insert(0, ".")
import renown_data as rd

OUT = sys.argv[1] if len(sys.argv) > 1 else "pursuit_review.html"

# ---- domain color hints (for the gate chips) ----
DOMAIN_TINT = {
    "Industry": "#1F4E8C", "Prowess": "#9E1B1B",
    "Cunning": "#1A1A1A", "Piety": "#B8941F",
}
TYPE_ORDER = ["Raw Materials", "Husbandry", "Energy", "Craft", "Power",
              "Civic", "Secrecy", "Monument"]

def clean(s):
    """strip markdown bold/asterisks for display but keep the text."""
    if not s:
        return ""
    s = str(s).replace("**", "")
    return s

def gate_domain(unlock):
    for d in DOMAIN_TINT:
        if d in (unlock or ""):
            return d
    return None

rows = []
for name, d in rd.NODES.items():
    typ = d.get("type", "?")
    unlock = d.get("unlock", "-") or "-"
    rows.append({
        "name": name,
        "type": typ,
        "unlock": unlock,
        "gate_domain": gate_domain(unlock) or "",
        "mastery_req": d.get("mastery_req", "") or "",
        "innate": clean(d.get("innate", "")),
        "mastery": clean(d.get("mastery", "")),
        "builds_into": ", ".join(d.get("builds_into", []) or []),
        "efficient": d.get("efficient", "") or "",
        "monument": bool(d.get("monument")),
        "has_engine": bool(d.get("engine")),
        "has_escalation": bool(d.get("escalation")),
    })

# sort by type-order then name
rows.sort(key=lambda r: (TYPE_ORDER.index(r["type"]) if r["type"] in TYPE_ORDER else 99, r["name"]))

# counts per type for the filter bar
counts = {}
for r in rows:
    counts[r["type"]] = counts.get(r["type"], 0) + 1

data_json = json.dumps(rows)

HTML = """<!doctype html><html><head><meta charset="utf-8">
<title>Renown Pursuit Review</title>
<style>
:root{--bg:#fafafa;--card:#fff;--line:#e3e3e3;--ink:#1c1c1c;--mut:#777;
--ind:#1F4E8C;--pro:#9E1B1B;--cun:#1A1A1A;--pie:#B8941F;--mon:#5B2A86;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
font:14px/1.45 -apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;}
header{position:sticky;top:0;background:var(--bg);border-bottom:1px solid var(--line);
padding:12px 18px;z-index:10;box-shadow:0 1px 6px rgba(0,0,0,.04)}
h1{margin:0 0 8px;font-size:18px;letter-spacing:.3px}
.controls{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
#q{flex:1;min-width:220px;padding:8px 11px;border:1px solid var(--line);border-radius:7px;font-size:14px}
.chip{padding:5px 11px;border:1px solid var(--line);border-radius:20px;background:#fff;
cursor:pointer;font-size:12.5px;user-select:none;white-space:nowrap}
.chip.active{background:var(--ink);color:#fff;border-color:var(--ink)}
.meta{color:var(--mut);font-size:12px;margin-left:auto}
main{padding:16px 18px;max-width:1180px;margin:0 auto}
.typehead{margin:22px 0 8px;font-size:13px;text-transform:uppercase;letter-spacing:1.2px;
color:var(--mut);font-weight:700;border-bottom:1px solid var(--line);padding-bottom:4px}
table{width:100%;border-collapse:collapse;background:var(--card);
border:1px solid var(--line);border-radius:8px;overflow:hidden;margin-bottom:6px}
th{background:#f3f3f3;text-align:left;padding:7px 10px;font-size:11px;text-transform:uppercase;
letter-spacing:.5px;color:var(--mut);border-bottom:1px solid var(--line);cursor:pointer;white-space:nowrap}
td{padding:8px 10px;border-bottom:1px solid #f0f0f0;vertical-align:top}
tr:last-child td{border-bottom:none}
tr:hover td{background:#fcfbff}
.nm{font-weight:700;white-space:nowrap}
.gate{display:inline-block;padding:1px 7px;border-radius:11px;font-size:11px;font-weight:600;color:#fff;white-space:nowrap}
.gate.Industry{background:var(--ind)}.gate.Prowess{background:var(--pro)}
.gate.Cunning{background:var(--cun)}.gate.Piety{background:var(--pie)}
.gate.none{background:#bbb}
.mon{color:var(--mon);font-weight:700}
.eff{max-width:340px}
.req{color:var(--mut);font-size:12.5px;max-width:180px}
.flags{font-size:11px;color:var(--mut);white-space:nowrap}
.dim{color:#bbb}
.hidden{display:none}
mark{background:#ffe96b;padding:0 1px}
</style></head><body>
<header>
<h1>Renown Pursuit Review <span style="color:var(--mut);font-weight:400;font-size:13px">— __TOTAL__ pursuits</span></h1>
<div class="controls">
<input id="q" placeholder="Search name / effect / gate / requirement…" autofocus>
<span id="chips"></span>
<span class="meta" id="meta"></span>
</div>
</header>
<main id="main"></main>
<script>
const DATA = __DATA__;
const TYPES = __TYPES__;
let activeType = null, sortKey = null, sortDir = 1, query = "";

const chips = document.getElementById('chips');
chips.innerHTML = '<span class="chip active" data-t="">All</span>' +
  TYPES.map(t=>`<span class="chip" data-t="${t.k}">${t.k} (${t.n})</span>`).join('');
chips.querySelectorAll('.chip').forEach(c=>c.onclick=()=>{
  chips.querySelectorAll('.chip').forEach(x=>x.classList.remove('active'));
  c.classList.add('active'); activeType = c.dataset.t||null; render();
});
document.getElementById('q').oninput = e=>{query=e.target.value.toLowerCase();render();};

const COLS = [
 ["name","Pursuit"],["unlock","Gate"],["mastery_req","Build Req"],
 ["innate","Innate"],["mastery","Mastery"],["builds_into","Builds Into"],
 ["efficient","Efficient"],["flags","Flags"]
];

function hl(s){ s=String(s==null?"":s); if(!query||!s) return esc(s);
  const i=s.toLowerCase().indexOf(query);
  if(i<0) return esc(s);
  return esc(s.slice(0,i))+'<mark>'+esc(s.slice(i,i+query.length))+'</mark>'+esc(s.slice(i+query.length));
}
function esc(s){return String(s==null?"":s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}

function matches(r){
  if(activeType && r.type!==activeType) return false;
  if(!query) return true;
  return [r.name,r.unlock,r.mastery_req,r.innate,r.mastery,r.builds_into,r.efficient]
    .join(" ").toLowerCase().includes(query);
}

function render(){
  const main=document.getElementById('main'); main.innerHTML="";
  let shown=0;
  const groups={};
  DATA.filter(matches).forEach(r=>{(groups[r.type]=groups[r.type]||[]).push(r);shown++;});
  const order = TYPES.map(t=>t.k).filter(t=>groups[t]);
  for(const typ of order){
    let rows=groups[typ];
    if(sortKey){rows=rows.slice().sort((a,b)=>{
      let x=(a[sortKey]||"")+"",y=(b[sortKey]||"")+"";return x.localeCompare(y)*sortDir;});}
    const h=document.createElement('div');h.className='typehead';h.textContent=`${typ} — ${rows.length}`;
    main.appendChild(h);
    const t=document.createElement('table');
    t.innerHTML="<thead><tr>"+COLS.map(c=>`<th data-k="${c[0]}">${c[1]}</th>`).join("")+"</tr></thead><tbody>"+
      rows.map(r=>{
        const gd=r.gate_domain||"none";
        const flags=[r.monument?'<span class="mon">◆ Monument</span>':"",
                     r.has_engine?"engine":"", r.has_escalation?"esc":""].filter(Boolean).join(" · ");
        return "<tr>"+
          `<td class="nm">${hl(r.name)}</td>`+
          `<td><span class="gate ${gd}">${hl(r.unlock)}</span></td>`+
          `<td class="req">${hl(r.mastery_req)||'<span class=dim>—</span>'}</td>`+
          `<td class="eff">${hl(r.innate)||'<span class=dim>—</span>'}</td>`+
          `<td class="eff">${hl(r.mastery)||'<span class=dim>—</span>'}</td>`+
          `<td class="req">${hl(r.builds_into)||'<span class=dim>—</span>'}</td>`+
          `<td class="req">${hl(r.efficient)||'<span class=dim>—</span>'}</td>`+
          `<td class="flags">${flags||'<span class=dim>—</span>'}</td>`+
        "</tr>";
      }).join("")+"</tbody>";
    t.querySelectorAll('th').forEach(th=>th.onclick=()=>{
      const k=th.dataset.k; if(k==='flags')return;
      if(sortKey===k)sortDir*=-1;else{sortKey=k;sortDir=1;} render();});
    main.appendChild(t);
  }
  document.getElementById('meta').textContent=`${shown} shown`;
  if(!shown)main.innerHTML='<p style="color:#999;padding:30px;text-align:center">No matches.</p>';
}
render();
</script></body></html>"""

types_for_js = [{"k": t, "n": counts[t]} for t in TYPE_ORDER if t in counts]
HTML = (HTML.replace("__DATA__", data_json)
            .replace("__TYPES__", json.dumps(types_for_js))
            .replace("__TOTAL__", str(len(rows))))

with open(OUT, "w", encoding="utf-8") as f:
    f.write(HTML)
print(f"wrote {len(rows)} pursuits -> {OUT}  (open in a browser)")
