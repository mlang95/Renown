#!/usr/bin/env python
# routes.py - new-player route sheet.
#   TOP: "Foundations" trunk = the ~15 universal pursuits everyone builds.
#   THEN: one compact branch per monument = its exclusive tail (distinctive steps),
#         with accessories (dead-ends) hung on the step they key off.
# Short, local lines only. Data = renown_data (builds_into + mastery_req).
import sys, collections
import renown_data as rd

NODES=rd.NODES
CH=collections.defaultdict(list); PA=collections.defaultdict(list)
for n,d in NODES.items():
    for b in (d.get("builds_into") or []):
        if b in NODES: CH[n].append(b); PA[b].append(n)
def parse_req(r):
    if not r or str(r).strip() in("","-","\u2014"): return []
    return [p.strip() for p in str(r).replace(" or ","+").split("+") if p.strip() in NODES]
def desc(n):
    o=set(); q=[n]
    while q:
        x=q.pop()
        for c in CH[x]:
            if c not in o: o.add(c); q.append(c)
    return o
for n,d in NODES.items():
    for r in parse_req(d.get("mastery_req")):
        if n not in desc(r) and n not in CH[r]: CH[r].append(n); PA[n].append(r)

MONS=[n for n,d in NODES.items() if d.get("monument")]
MONSET=set(MONS)
def monreach(n): return (desc(n)&MONSET)|({n} if n in MONSET else set())

# accessory = dead-end (no children) and not a monument
ACC=set(n for n in NODES if not CH[n] and n not in MONSET)
# universal trunk
TRUNK=sorted([n for n in NODES if len(monreach(n))>=6 and n not in ACC])

DOM=["Industry","Prowess","Cunning","Piety"]
DOMC={"Common":"#6a6a72","Industry":"#2E5A8C","Prowess":"#9E2B25","Cunning":"#1c1c20","Piety":"#C6A024"}
def domain_of(n):
    u=NODES[n].get("unlock") or ""
    for x in DOM:
        if x in u: return x
    return "Common"

# per-monument exclusive branch: nodes reaching only this monument, minus trunk,
# ordered by build depth
def branch_of(mon):
    excl=[n for n in NODES if monreach(n)=={mon} and n not in ACC]
    excl=[n for n in excl if n not in TRUNK]
    # order by longest-path depth within the set + trunk feeders
    sub=set(excl)|{mon}
    dep={}
    def d(n,st=()):
        if n in dep: return dep[n]
        if n in st: return 0
        v=0
        for p in PA[n]:
            if p in sub: v=max(v,d(p,st+(n,))+1)
        dep[n]=v; return v
    for n in sub: d(n)
    cols=collections.defaultdict(list)
    for n in sub: cols[dep[n]].append(n)
    return dep, cols, sub

NW,NH=120,24; COLGAP,ROWGAP=52,12
def _esc(t): return str(t).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

def node_svg(x,y,n,small=False):
    col=DOMC[domain_of(n)]; mon=NODES[n].get("monument")
    w=NW*(0.82 if small else 1); h=NH*(0.82 if small else 1)
    fill="#fdf3d0" if mon else ("#efeadd" if small else "#ffffff")
    sw=2.2 if mon else 1.3
    fs=7 if small else 8.2
    s=[f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" rx="4" fill="{fill}" stroke="{col}" stroke-width="{sw}"/>',
       f'<rect x="{x:.0f}" y="{y:.0f}" width="4" height="{h:.0f}" fill="{col}"/>']
    lbl=n if len(n)<=(22 if not small else 18) else n[:(21 if not small else 17)]+"\u2026"
    dia=" \u25c6" if mon else ""
    s.append(f'<text x="{x+8:.0f}" y="{y+h/2+3:.0f}" font-size="{fs}" fill="#2b2620">{_esc(lbl)}{dia}</text>')
    return "".join(s), w, h

def build(out):
    PAGE_W=1180; PADL=30
    body=[]; H=110
    # measure: trunk row + monument branches (2 per row)
    trunk_h = ((len(TRUNK)+4)//5)*(NH+ROWGAP)+20
    H += trunk_h + 30
    branches=[(m,)+branch_of(m) for m in MONS]
    # branch heights
    bmeta=[]
    for m,dep,cols,sub in branches:
        rows=max(len(v) for v in cols.values()) if cols else 1
        ncol=max(cols)+1 if cols else 1
        bmeta.append((m,dep,cols,sub,rows,ncol))
    # pack 2 branches per band
    per=2; bandpad=52
    i=0; bandsH=0
    while i<len(bmeta):
        band=bmeta[i:i+per]
        bandsH += max(b[4] for b in band)*(NH+ROWGAP)+bandpad
        i+=per
    H += bandsH

    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{PAGE_W}" height="{int(H)}" viewBox="0 0 {PAGE_W} {int(H)}" font-family="Georgia, serif">']
    svg.append(f'<rect width="{PAGE_W}" height="{int(H)}" fill="#f4efe4"/>')
    svg.append(f'<text x="{PADL}" y="38" font-size="24" font-weight="bold" fill="#2b2620">Pursuit Routes</text>')
    svg.append(f'<text x="{PADL}" y="58" font-size="12" fill="#6f6f77">build the Foundations, then follow your goal\u2019s branch \u00b7 \u25c6 gold = Monument \u00b7 shaded = optional accessory</text>')

    # Foundations trunk
    oy=86
    svg.append(f'<text x="{PADL}" y="{oy}" font-size="14" font-weight="bold" fill="#5f5647">FOUNDATIONS \u2014 everyone builds these</text>')
    svg.append(f'<line x1="{PADL}" y1="{oy+7}" x2="{PAGE_W-PADL}" y2="{oy+7}" stroke="#c9bfa8" stroke-width="1.2"/>')
    ty=oy+18
    for idx,n in enumerate(TRUNK):
        r,c=divmod(idx,5)
        x=PADL+c*(NW+COLGAP); y=ty+r*(NH+ROWGAP)
        sv,_,_=node_svg(x,y,n); svg.append(sv)
    oy=ty+((len(TRUNK)+4)//5)*(NH+ROWGAP)+24

    # monument branches, 2 per band
    def draw_branch(bx,by,m,dep,cols,sub,maxrows):
        col=DOMC[domain_of(m)]
        svg.append(f'<text x="{bx}" y="{by}" font-size="12.5" font-weight="bold" fill="{col}">{_esc(m)}</text>')
        svg.append(f'<line x1="{bx}" y1="{by+6}" x2="{bx+ (max(cols)+1)*(NW+COLGAP)-COLGAP if cols else 200}" y2="{by+6}" stroke="{col}" stroke-width="1" opacity="0.5"/>')
        oy2=by+16
        pos={}
        for c in sorted(cols):
            colnodes=sorted(cols[c], key=lambda n: (0 if n not in ACC else 1, n))
            for r,n in enumerate(colnodes):
                pos[n]=(bx+c*(NW+COLGAP), oy2+r*(NH+ROWGAP))
        # edges (within branch only)
        for n in sub:
            for k in CH[n]:
                if k in pos and k in sub:
                    x1,y1=pos[n]; x1+=NW; y1+=NH/2
                    x2,y2=pos[k]; y2+=NH/2
                    mx=x1+(x2-x1)*0.5
                    svg.append(f'<path d="M{x1:.0f},{y1:.0f} C{mx:.0f},{y1:.0f} {mx:.0f},{y2:.0f} {x2-6:.0f},{y2:.0f}" fill="none" stroke="#8f8672" stroke-width="1.1" opacity="0.8" marker-end="url(#arw)"/>')
        for n,(x,y) in pos.items():
            sv,_,_=node_svg(x,y,n,small=(n in ACC)); svg.append(sv)

    svg.append('<defs><marker id="arw" markerWidth="7" markerHeight="7" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#8f8672"/></marker></defs>')
    i=0
    while i<len(bmeta):
        band=bmeta[i:i+per]
        rh=max(b[4] for b in band)*(NH+ROWGAP)
        for j,(m,dep,cols,sub,rows,ncol) in enumerate(band):
            bx=PADL+j*(PAGE_W//2-10)
            draw_branch(bx,oy,m,dep,cols,sub,rows)
        oy+=rh+bandpad
        i+=per
    svg.append("</svg>")
    open(out,"w").write("\n".join(svg))
    print(f"routes -> {out}  ({PAGE_W}x{int(H)})  trunk={len(TRUNK)} monuments={len(MONS)} accessories={len(ACC)}")

if __name__=="__main__":
    build(sys.argv[1] if len(sys.argv)>1 else "pursuit_routes.svg")
