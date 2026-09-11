#!/usr/bin/env python
# svg_to_pdf.py - combine SVG pages into ONE PDF.
# Default: each page is sized to the tree's own proportions and scaled up large,
#          so the content fills the whole page with no wasted space (fit-to-content).
# Use --size letter|a4|tabloid to force a standard sheet (content centered, may letterbox).
#   python svg_to_pdf.py out.pdf p1.svg p2.svg [--width IN] [--size letter] [--portrait]
import sys, os, traceback

def main():
    args = sys.argv[1:]
    size = "letter"; portrait = False; target_w_in = 14.0
    rest = []
    while args:
        a = args.pop(0)
        if a == "--size" and args: size = args.pop(0).lower()
        elif a == "--portrait": portrait = True
        elif a == "--width" and args: target_w_in = float(args.pop(0))
        else: rest.append(a)
    if len(rest) >= 2:
        out = rest[0]; svgs = rest[1:]
    else:
        d = "cards" if os.path.isdir("cards") else "."
        svgs = [os.path.join(d, "pursuit_tree_p1.svg"), os.path.join(d, "pursuit_tree_p2.svg")]
        out = os.path.join(d, "pursuit_tree.pdf")
    for s in svgs:
        if not os.path.exists(s):
            print("MISSING:", s); return 1
    try:
        from svglib.svglib import svg2rlg
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter, A4, landscape, portrait as _portrait
        from reportlab.graphics import renderPDF
    except Exception:
        print("IMPORT ERROR:"); traceback.print_exc()
        print('Fix: "...\\kotr\\python.exe" -m pip install svglib reportlab')
        return 1
    try:
        c = canvas.Canvas(out)
        M = 14  # small margin
        for s in svgs:
            d = svg2rlg(s)
            if d is None: print("svg2rlg None for", s); return 1
            if size:  # standard sheet, centered
                base = {"letter": letter, "a4": A4,
                        "tabloid": (792, 1224)}.get(size, letter)
                PW, PH = (_portrait(base) if portrait else landscape(base))
                sc = min((PW-2*M)/d.width, (PH-2*M)/d.height)
            else:     # fit-to-content: page == tree, scaled to target width
                sc = (target_w_in*72) / d.width
                PW, PH = d.width*sc + 2*M, d.height*sc + 2*M
            d.scale(sc, sc); d.width *= sc; d.height *= sc
            c.setPageSize((PW, PH))
            renderPDF.draw(d, c, (PW-d.width)/2, (PH-d.height)/2)
            c.showPage()
        c.save()
        mode = f"{size}{' portrait' if portrait else ' landscape'}" if size else f"fit-to-content @ {target_w_in}in wide"
        print("WROTE:", out, f"({len(svgs)} pages, {mode})")
        return 0
    except Exception:
        print("CONVERT ERROR:"); traceback.print_exc(); return 1

if __name__ == "__main__":
    sys.exit(main())