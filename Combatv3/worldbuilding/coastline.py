#!/usr/bin/env python
# coastline.py - metaball landmass outline. Sum of a few offset circular fields;
# trace the iso-contour -> lumpy, conjoined, non-round continental shapes.
import math, random

def coastline_path(cx, cy, r, seed=0, points=360, blobs=4, spread=0.7,
                   lobes=0.0, lobe_dir=0.0, wobble=0.06):
    """blobs=how many metaball lumps, spread=how far they scatter (peninsulas),
    wobble=fine coastline noise."""
    rng = random.Random(seed)
    # scatter blob centers within the mass; varied strengths/radii
    B = []
    for _ in range(blobs):
        ang = rng.uniform(0, 2*math.pi)
        dist = rng.uniform(0, spread) * r
        B.append((cx + dist*math.cos(ang), cy + dist*math.sin(ang),
                  rng.uniform(0.55, 1.0) * r * 0.62))
    B.append((cx, cy, r*0.6))                 # anchor core
    phase = [rng.uniform(0, 2*math.pi) for _ in range(4)]

    def field(px, py):                        # metaball potential
        s = 0.0
        for bx, by, br in B:
            d2 = (px-bx)**2 + (py-by)**2 + 1
            s += (br*br) / d2
        return s
    ISO = 0.9

    pts = []
    for i in range(points):
        a = 2*math.pi*i/points
        dirx, diry = math.cos(a), math.sin(a)
        # march outward along the ray until field drops below ISO -> boundary
        lo, hi = 0.2*r, 2.4*r
        for _ in range(26):                   # bisection on the iso-surface
            mid = (lo+hi)/2
            if field(cx+dirx*mid, cy+diry*mid) > ISO: lo = mid
            else: hi = mid
        rr = lo
        rr *= 1 + wobble*sum(math.sin((k+2)*a+phase[k]) for k in range(4))/4
        rr *= 1 + lobes*math.cos(a-lobe_dir)
        pts.append((cx+rr*dirx, cy+rr*diry))
    # smooth closed bezier
    d=f"M {pts[0][0]:.1f} {pts[0][1]:.1f} "; N=len(pts)
    for i in range(N):
        p0,p1,p2,p3=pts[(i-1)%N],pts[i],pts[(i+1)%N],pts[(i+2)%N]
        c1=(p1[0]+(p2[0]-p0[0])/6,p1[1]+(p2[1]-p0[1])/6)
        c2=(p2[0]-(p3[0]-p1[0])/6,p2[1]-(p3[1]-p1[1])/6)
        d+=f"C {c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f} "
    return d+"Z"

if __name__=="__main__":
    print(coastline_path(200,200,120,seed=3)[:60],"...")
