#!/usr/bin/env python
# render_tree.py - COORDINATE-DRIVEN tree renderer (no auto-layout).
# Reads layout.json: each chart lists nodes with explicit [col,row].
# Draws boxes + elbow/bus edges from renown_data mastery+builds graph.
# Edit layout.json (or a vector tool) to move anything; positions are law.
import sys, json, collections
import renown_data as rd

NODES = rd.NODES
DOM=["Industry","Prowess","Cunning","Piety"]
DOMC={"Common":"#6a6a72","Industry":"#2E5A8C","Prowess":"#9E2B25","Cunning":"#1c1c20","Piety":"#C6A024"}
def domain_of(n):
    u=NODES[n].get("unlock") or ""
    for x in DOM:
        if x in u: return x
    return "Common"
def parse_req(r):
    if not r or str(r).strip() in("","-","\u2014"): return []
    return [p.strip() for p in str(r).replace(" or ","+").split("+") if p.strip() in NODES]

# full edge set: builds_into + mastery_req (cycle-guarded)
CH=collections.defaultdict(list)
for n,d in NODES.items():
    for b in (d.get("builds_into") or []):
        if b in NODES: CH[n].append(b)
def desc(n):
    out=set(); q=[n]
    while q:
        x=q.pop()
        for c in CH[x]:
            if c not in out: out.add(c); q.append(c)
    return out
for n,d in NODES.items():
    for r in parse_req(d.get("mastery_req")):
        if n not in desc(r) and n not in CH[r]:
            CH[r].append(n)

NW,NH=118,24; COLGAP,ROWGAP=54,12
EDGE_COLORS=["#2E5A8C","#9E2B25","#1c9c8c","#C6A024","#6A3D8F","#CC6A1A","#3a7d3a",
             "#b5347a","#2b6f9e","#8a6d1a","#5f5647","#7a2ea0","#0f8a7e","#a83232"]
def _ncolor(n):
    return EDGE_COLORS[hash(n) % len(EDGE_COLORS)]
def _blend(colors):
    rs=gs=bs=0
    for c in colors:
        rs+=int(c[1:3],16); gs+=int(c[3:5],16); bs+=int(c[5:7],16)
    k=len(colors)
    return f"#{rs//k:02x}{gs//k:02x}{bs//k:02x}"

def _esc(t): return str(t).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

def elbow(x1,y1,x2,y2):
    if abs(y1-y2)<2: return f'M{x1:.0f},{y1:.0f} L{x2-7:.0f},{y2:.0f}'
    mx=x1+(x2-x1)*0.45; r=min(9,abs(y2-y1)/2); sg=1 if y2>y1 else -1
    return (f'M{x1:.0f},{y1:.0f} L{mx-r:.0f},{y1:.0f} Q{mx:.0f},{y1:.0f} {mx:.0f},{y1+sg*r:.0f} '
            f'L{mx:.0f},{y2-sg*r:.0f} Q{mx:.0f},{y2:.0f} {mx+r:.0f},{y2:.0f} L{x2-7:.0f},{y2:.0f}')

def build(layout_path, out):
    charts=json.load(open(layout_path))
    # split into 2 landscape pages, balanced by total rows
    tot=[max(v[1] for v in c["nodes"].values())+1 for c in charts]
    cum=0; half=sum(tot)/2; split=len(charts)
    for i,t in enumerate(tot):
        cum+=t
        if cum>=half: split=i+1; break
    pages=[charts[:split], charts[split:]]
    outs=[]
    base=out[:-4] if out.endswith(".svg") else out
    for pi,pg in enumerate(pages):
        po=f"{base}_p{pi+1}.svg"
        _build_page(pg, po); outs.append(po)
    print("pages:", outs)
    # combined multi-page PDF via svglib + reportlab (pure Python, no Cairo DLL)
    try:
        from svglib.svglib import svg2rlg
        from reportlab.graphics import renderPDF
        from pypdf import PdfWriter, PdfReader
        import io
        w = PdfWriter()
        for svg in outs:
            drawing = svg2rlg(svg)
            buf = io.BytesIO(); renderPDF.drawToFile(drawing, buf); buf.seek(0)
            for pg in PdfReader(buf).pages: w.add_page(pg)
        pdf_out = f"{base}.pdf"
        with open(pdf_out, "wb") as f: w.write(f)
        print("pdf:", pdf_out)
    except Exception as e:
        print(f"(PDF skipped: {e}; run: pip install svglib pypdf)")
    return

def _build_page(charts, out):
    PADL=30
    svg=[]; H=70
    laid=[]
    for c in charts:
        nodes=c["nodes"]
        maxc=max(v[0] for v in nodes.values()); maxr=max(v[1] for v in nodes.values())
        w=(maxc+1)*NW+maxc*COLGAP; h=(maxr+1)*(NH+ROWGAP)
        laid.append((c,w,h)); H+=h+26
    # page width = widest single chart, or the paired Husbandry+Trade row, + margins
    PAGE_W=0
    i=0
    while i < len(laid):
        c,w,h=laid[i]
        if c["title"].startswith("Husbandry") and i+1<len(laid) and laid[i+1][0]["title"].startswith("Trade"):
            row_w = w + 80 + laid[i+1][1]; i+=2
        else:
            row_w = w; i+=1
        PAGE_W=max(PAGE_W, row_w)
    PAGE_W = int(PAGE_W + 2*PADL)
    body=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{PAGE_W}" height="{int(H)}" viewBox="0 0 {PAGE_W} {int(H)}" font-family="Georgia, serif">']
    body.append(f'<rect width="{PAGE_W}" height="{int(H)}" fill="#f4efe4"/>')
    defs=['<defs>']
    for col in EDGE_COLORS+["#8f8672"]:
        defs.append(f'<marker id="arw-{col[1:]}" markerWidth="7" markerHeight="7" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="{col}"/></marker>')
    defs.append('</defs>'); body.append("".join(defs))
    body.append(f'<text x="{PADL}" y="34" font-size="20" font-weight="bold" fill="#2b2620">Pursuit Paths</text>')
    oy=60
    i=0
    while i < len(laid):
        c,w,h=laid[i]
        # pair Husbandry & Provisions with Trade & Works side by side
        pair=None
        if c["title"].startswith("Husbandry") and i+1<len(laid) and laid[i+1][0]["title"].startswith("Trade"):
            pair=laid[i+1]
        _render_chart(body,c,w,h,PADL,oy)
        if pair:
            pc,pw,ph=pair
            # vertical divider bar between Husbandry and Trade columns
            divx=PADL+w+40
            body.append(f'<line x1="{divx}" y1="{oy}" x2="{divx}" y2="{oy+max(h,ph)}" stroke="#c9bfa8" stroke-width="1.4"/>')
            _render_chart(body,pc,pw,ph,PADL+w+80,oy)
            oy=oy+max(h,ph)+26; i+=2; continue
        oy=oy+h+26; i+=1
    body.append("</svg>")
    open(out,"w",encoding="utf-8").write("\n".join(body)); print(f"rendered {len(charts)} charts -> {out}"); return

def _edge(body, d, color="#8f8672", arrow=True, w=1.6):
    body.append(f'<path d="{d}" fill="none" stroke="#f4efe4" stroke-width="{w+3:.1f}" opacity="1"/>')
    marker=f' marker-end="url(#arw-{color[1:]})"' if arrow else ''
    body.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" opacity="0.95"{marker}/>')

def _fit_font(s, maxw, cap=8.2, floor=5.0):
    # shrink font until the label fits maxw (Helvetica metric ~ proxy)
    from reportlab.pdfbase.pdfmetrics import stringWidth
    fs = cap
    while fs > floor and stringWidth(s, "Helvetica", fs) > maxw:
        fs -= 0.2
    return fs

def _draw_node(body, x, y, n):
    col = DOMC[domain_of(n)]; mon = NODES[n].get("monument")
    fill = "#fdf3d0" if mon else "#ffffff"; sw = 2.2 if mon else 1.4
    body.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{NW}" height="{NH}" rx="4" fill="{fill}" stroke="{col}" stroke-width="{sw}"/>')
    body.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="5" height="{NH}" fill="{col}"/>')
    tx = x + 9
    text_maxw = NW - 13 - (11 if mon else 0)   # leave room for the diamond
    fs = _fit_font(n, text_maxw)
    body.append(f'<text x="{tx:.0f}" y="{y+NH/2+3:.0f}" font-size="{fs:.1f}" fill="#2b2620">{_esc(n)}</text>')
    if mon:  # draw a real diamond (polygon), not a font glyph
        cx = x + NW - 8; cy = y + NH/2; r = 3.6
        body.append(f'<polygon points="{cx:.1f},{cy-r:.1f} {cx+r:.1f},{cy:.1f} {cx:.1f},{cy+r:.1f} {cx-r:.1f},{cy:.1f}" fill="#8a6d1a"/>')

def _render_chart(body,c,w,h,PADL,oy):
    import json
    nodes=c["nodes"]; anchors=c["anchor"]; anchors=anchors if isinstance(anchors,list) else [anchors]
    accent=DOMC[domain_of(anchors[0])] if anchors and anchors[0] else "#5f5647"
    oy2=oy+4
    def px(n):
        cc,rr=nodes[n]; return (PADL+cc*(NW+COLGAP), oy2+rr*(NH+ROWGAP))
    # build edge list; each edge = (parent, child, path_d, [segments])
    def segs_of(x1,y1,x2,y2):
        # approximate an elbow as its 3 axis-aligned segments for overlap testing
        if abs(y1-y2)<2: return [("h",round(y1),x1,x2-7)]
        mx=x1+(x2-x1)*0.45
        return [("h",round(y1),x1,mx),("v",round(mx),y1,y2),("h",round(y2),mx,x2-7)]
    edges=[]
    for n in nodes:
        kids=[k for k in CH[n] if k in nodes and nodes[k][0] > nodes[n][0]]
        if not kids: continue
        x1,y1=px(n); x1+=NW; y1+=NH/2
        if len(kids)==1:
            k=kids[0]; bx,by=px(k); x2,y2=bx,by+NH/2
            edges.append([n,k,elbow(x1,y1,x2,y2),segs_of(x1,y1,x2,y2),True])
        else:
            fx=x1+COLGAP*0.45; cys=[px(k)[1]+NH/2 for k in kids]
            lo,hi=min(cys+[y1]),max(cys+[y1])
            edges.append([n,None,f"M{x1:.0f},{y1:.0f} L{fx:.0f},{y1:.0f}",[("h",round(y1),x1,fx)],False])
            if hi-lo>1: edges.append([n,None,f"M{fx:.0f},{lo:.0f} L{fx:.0f},{hi:.0f}",[("v",round(fx),lo,hi)],False])
            for k,cy in zip(kids,cys):
                bx=px(k)[0]
                edges.append([n,k,f"M{fx:.0f},{cy:.0f} L{bx-6:.0f},{cy:.0f}",[("h",round(cy),fx,bx-6)],True])
    # overlap detection: two segments overlap if same orientation+line and ranges intersect,
    # OR a crossing (h seg and v seg intersecting)
    def rng(a,b): return (min(a,b),max(a,b))
    def overlaps(s1,s2):
        o1,l1,a1,b1=s1; o2,l2,a2,b2=s2
        if o1==o2 and l1==l2:
            (lo1,hi1),(lo2,hi2)=rng(a1,b1),rng(a2,b2)
            return lo1<hi2-2 and lo2<hi1-2
        if o1!=o2:
            h=s1 if o1=="h" else s2; v=s2 if o1=="h" else s1
            hy=h[1]; hx0,hx1=rng(h[2],h[3]); vx=v[1]; vy0,vy1=rng(v[2],v[3])
            return hx0-2<=vx<=hx1+2 and vy0-2<=hy<=vy1+2
        return False
    flagged=[False]*len(edges)
    for i in range(len(edges)):
        for j in range(i+1,len(edges)):
            if edges[i][0]==edges[j][0]: continue  # same parent fan shares trunk legitimately
            hit=any(overlaps(a,b) for a in edges[i][3] for b in edges[j][3])
            if hit: flagged[i]=flagged[j]=True
    for idx,(pn,cn,d,sg,arrow) in enumerate(edges):
        _edge(body,d,"#8f8672",arrow=arrow)
    for n in nodes:
        x,y=px(n); _draw_node(body,x,y,n)

def _dead(c,w,h,PADL,oy):
    for c,w,h in []:
        nodes=c["nodes"]; anchors=c["anchor"]; anchors=anchors if isinstance(anchors,list) else [anchors]
        accent=DOMC[domain_of(anchors[0])] if anchors and anchors[0] else "#5f5647"
        body.append(f'<text x="{PADL}" y="{oy}" font-size="12.5" font-weight="bold" fill="{accent}">{_esc(c["title"])}</text>')
        body.append(f'<line x1="{PADL}" y1="{oy+6}" x2="{PADL+w}" y2="{oy+6}" stroke="{accent}" stroke-width="1" opacity="0.5"/>')
        oy2=oy+16
        def px(n): 
            cc,rr=nodes[n]; return (PADL+cc*(NW+COLGAP), oy2+rr*(NH+ROWGAP))
        # edges within chart
        for n in nodes:
            kids=[k for k in CH[n] if k in nodes]
            if not kids: continue
            x1,y1=px(n); x1+=NW; y1+=NH/2
            if len(kids)==1:
                bx,by=px(kids[0]); _edge(body, elbow(x1,y1,bx,by+NH/2))
            else:
                fx=x1+COLGAP*0.45; cys=[px(k)[1]+NH/2 for k in kids]
                lo,hi=min(cys+[y1]),max(cys+[y1])
                body.append(f'<path d="M{x1:.0f},{y1:.0f} L{fx:.0f},{y1:.0f}" stroke="#8f8672" stroke-width="1.4" fill="none" opacity="0.85"/>')
                if hi-lo>1: body.append(f'<path d="M{fx:.0f},{lo:.0f} L{fx:.0f},{hi:.0f}" stroke="#8f8672" stroke-width="1.4" fill="none" opacity="0.85"/>')
                for k,cy in zip(kids,cys):
                    bx=px(k)[0]; body.append(f'<path d="M{fx:.0f},{cy:.0f} L{bx-6:.0f},{cy:.0f}" stroke="#8f8672" stroke-width="1.2" fill="none" opacity="0.85" marker-end="url(#arw)"/>')
        for n in nodes:
            x,y=px(n); _draw_node(body,x,y,n)
        oy=oy2+h+40
    body.append("</svg>")
    open(out,"w",encoding="utf-8").write("\n".join(body))
    print(f"rendered {len(charts)} charts -> {out}")

if __name__=="__main__":
    build(sys.argv[1] if len(sys.argv)>1 else "layout.json",
          sys.argv[2] if len(sys.argv)>2 else "pursuit_tree.svg")