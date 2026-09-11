#!/usr/bin/env python
# world_map.py - schematic map with organic (radial-fBm) coastlines.
from itertools import combinations
from coastline import coastline_path
import math

Wd,Ht=1000,1000; CX,CY=Wd/2,Ht/2
D=["Industry","Prowess","Cunning","Piety"]
DOMC={"Industry":"#2E5A8C","Prowess":"#9E2B25","Cunning":"#3a3a42","Piety":"#C6A024"}
POS={"Industry":(210,210),"Prowess":(790,210),"Cunning":(210,790),"Piety":(790,790)}
ADJ={("Industry","Prowess"),("Industry","Cunning"),("Prowess","Piety"),("Cunning","Piety")}
def adj(a,b): return (a,b) in ADJ or (b,a) in ADJ
SEA="#cfe0e6"; INK="#26262e"; PARCH="#f4efe4"; COAST="#8a7f66"

def txt(x,y,s,size=15,col=INK,wt="bold"):
    return f'<text x="{x:.0f}" y="{y:.0f}" font-family="Georgia,serif" font-size="{size}" fill="{col}" text-anchor="middle" font-weight="{wt}">{s}</text>'
def grad(a,b):
    return f'<linearGradient id="g{a[:2]}{b[:2]}"><stop offset="0" stop-color="{DOMC[a]}"/><stop offset="1" stop-color="{DOMC[b]}"/></linearGradient>'
def land(cx,cy,r,fill,seed,lobes=0.0,lobe_dir=0.0,sw=2.5,op=0.94,blobs=4,spread=0.7,wobble=0.06):
    d=coastline_path(cx,cy,r,seed=seed,lobes=lobes,lobe_dir=lobe_dir,blobs=blobs,spread=spread,wobble=wobble)
    return f'<path d="{d}" fill="{fill}" stroke="{COAST}" stroke-width="{sw}" opacity="{op}"/>'
def cen(pts): return (sum(p[0] for p in pts)/len(pts), sum(p[1] for p in pts)/len(pts))
def ang(fx,fy,tx,ty): return math.atan2(ty-fy,tx-fx)

svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{Wd}" height="{Ht}" viewBox="0 0 {Wd} {Ht}">']
svg.append(f'<rect width="{Wd}" height="{Ht}" fill="{SEA}"/>')
svg.append("<defs>"+"".join(grad(a,b) for a,b in combinations(D,2))+"</defs>")

seed=1
DELTA=70; CDX,CDY=-DELTA,-DELTA//2     # 5-island group shift: 1 left, 1/2 up
# corner continents (big, rugged)
for dom,(x,y) in POS.items():
    x+=CDX; y+=CDY
    svg.append(land(x,y,150,DOMC[dom],seed,sw=3,blobs=5,spread=0.8,wobble=0.05)); seed+=1
    svg.append(txt(x,y-4,dom,20,"#ffffff")); svg.append(txt(x,y+16,"Heartland",12,"#f0ece0",wt="normal"))

# pair archipelagos (main isle bulges toward the *other* parent = gradient side)
DIAG_TARGET={frozenset(("Prowess","Cunning")):"Prowess",frozenset(("Industry","Piety")):"Industry"}
def isle(cx,cy,r,sd): return land(cx,cy,r,PARCH,sd,sw=1.5,op=1,blobs=2,spread=0.4,wobble=0.08)
for a,b in combinations(D,2):
    ax,ay=POS[a]; bx,by=POS[b]; mx,my=(ax+bx)/2,(ay+by)/2
    edge=adj(a,b)
    if not edge:
        tgt=DIAG_TARGET[frozenset((a,b))]; mx=CX+(POS[tgt][0]-CX)*0.42; my=CY+(POS[tgt][1]-CY)*0.42
    r=46 if edge else 40
    ld=ang(mx,my,bx,by)
    svg.append(land(mx,my,r,f"url(#g{a[:2]}{b[:2]})",seed,lobes=0.10,lobe_dir=ld,blobs=3,spread=0.6,wobble=0.06)); seed+=1
    for dx,dy in [(-r-30,2),(r+28,-8),(6,r+30)]:
        svg.append(isle(mx+dx,my+dy,11,seed)); seed+=1
    svg.append(txt(mx,my+4,f"{a[:3]}\u00d7{b[:3]}",13,"#ffffff"))

# triples: offset toward their 3 corners (away from dropped)
TRIPLE_NUDGE = {  # extra (dx,dy); west two get an additional -DELTA left
    ("Industry","Prowess","Cunning"): (-70-DELTA, -18),
    ("Industry","Cunning","Piety"):   (-70-DELTA,  18),
}
for combo in combinations(D,3):
    dropped=[d for d in D if d not in combo][0]
    tx,ty=cen([POS[c] for c in combo]); tx=(tx+CX)/2; ty=(ty+CY)/2
    ndx,ndy=TRIPLE_NUDGE.get(combo,(0,0)); tx+=ndx; ty+=ndy
    svg.append(land(tx,ty,30,PARCH,seed,sw=2,blobs=2,spread=0.4)); seed+=1
    svg.append(txt(tx,ty-1,"\u00d7".join(c[:2] for c in combo),11,"#7a5a1a"))
    svg.append(txt(tx,ty+11,"triple",8,"#8a8072",wt="normal"))

# center basin (polymath): group shift + extra left delta
PX,PY=CX-30+CDX-DELTA+DELTA,CY-40+CDY+DELTA
svg.append(land(PX,PY,26,PARCH,seed,sw=1.8,op=1,blobs=2,spread=0.35)); seed+=1
svg.append(txt(PX,PY+2,"POLY",8,"#7a5a1a"))

svg.append(txt(CX,44,"RENOWN \u2014 The World",22))
svg.append(txt(CX,64,"organic coastlines \u00b7 4 continents \u00b7 6 pairs \u00b7 4 triples \u00b7 polymath core",12,"#555",wt="normal"))
svg.append("</svg>")
open("world_map.svg","w").write("\n".join(svg)); print("wrote world_map.svg")
