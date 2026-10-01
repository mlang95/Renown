"""display_pdf.py — NAME_DISPLAY for every reportlab sheet (cards, tiles, equipment, combat).

Call install() at the top of a sheet script, BEFORE its reportlab imports:

    import display_pdf; display_pdf.install()

From then on every string drawn on a Canvas (drawString / drawCentredString / drawRightString /
drawAlignedString) and every width measured (Canvas.stringWidth, pdfmetrics.stringWidth) goes through
renown_data.display_text, so a rename in NAME_DISPLAY reaches the PDF and the layout measures the
renamed text it actually draws. Engine ids in the data stay untouched.

D(text) is exported for code that wraps or truncates word-by-word: alias the whole text first, so
multi-word renames ("Artillery Park" -> "Ordinance Yard") are matched before it is split.
"""
_DISP = None


def _disp():
    """renown_data.display_text, imported lazily (after ce_paths has pointed renown_data at the d10 file)."""
    global _DISP
    if _DISP is None:
        try:
            import renown_data as rd
            f = getattr(rd, "display_text", None)
            _DISP = f if (f and getattr(rd, "ALIASES", None)) else (lambda s: s)
        except Exception:
            _DISP = lambda s: s
    return _DISP


def D(text):
    """Display form of a string (non-strings pass through)."""
    return _disp()(text) if isinstance(text, str) else text


_INSTALLED = False


def install():
    global _INSTALLED
    if _INSTALLED:
        return
    _INSTALLED = True
    from reportlab.pdfgen import canvas as _cv
    from reportlab.pdfbase import pdfmetrics as _pm
    C = _cv.Canvas

    def _wrap_draw(orig):
        def f(self, x, y, text, *a, **k):
            return orig(self, x, y, D(text), *a, **k)
        f.__wrapped__ = orig
        return f

    for name in ("drawString", "drawCentredString", "drawRightString", "drawAlignedString"):
        if hasattr(C, name) and not hasattr(getattr(C, name), "__wrapped__"):
            setattr(C, name, _wrap_draw(getattr(C, name)))

    if not hasattr(C.stringWidth, "__wrapped__"):
        _csw = C.stringWidth
        def _c_sw(self, text, fontName=None, fontSize=None):
            return _csw(self, D(text), fontName, fontSize)
        _c_sw.__wrapped__ = _csw
        C.stringWidth = _c_sw

    if not hasattr(_pm.stringWidth, "__wrapped__"):
        _psw = _pm.stringWidth
        def _p_sw(text, fontName, fontSize, encoding="utf8"):
            return _psw(D(text), fontName, fontSize, encoding)
        _p_sw.__wrapped__ = _psw
        _pm.stringWidth = _p_sw
