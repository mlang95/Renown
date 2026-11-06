"""display_lab.py — NAME_DISPLAY for the combat lab (notebook tables, plots, printed output, exports).

The engine and every frame keep canonical ids (Knight Templar, Recover 6, Javelin, ...); only what a person
READS is renamed through renown_data.display_text, the same layer the rules, wiki, board and PDF sheets use.

    import display_lab; display_lab.install()        # notebook prelude: plots + DataFrame HTML (+ print)

  install(plots=True, frames=True, print_=True)
    plots   every matplotlib Text (titles, axis labels, tick labels, legends, annotations)
    frames  every DataFrame / Styler shown as HTML in Jupyter (cells, index, columns)
    print_  every print() of a string or DataFrame-as-text
  D(s) / disp_df(df) / disp_obj(o)  for code that builds its own output (build_rank, the HTML explorer).
Filtering still uses the canonical ids: R[R.retinue == "Knight Templar"], not the displayed name.
"""
_RD = None


def _rd():
    global _RD
    if _RD is None:
        import renown_data as rd
        _RD = rd
    return _RD


def D(s):
    """Display form of a string (non-strings pass through)."""
    if not isinstance(s, str):
        return s
    f = getattr(_rd(), "display_text", None)
    return f(s) if f else s


def disp_obj(o):
    """D over every string VALUE in a JSON-able structure (dict keys left alone: they are field names)."""
    if isinstance(o, str):
        return D(o)
    if isinstance(o, dict):
        return {k: disp_obj(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return type(o)(disp_obj(v) for v in o)
    return o


def disp_df(df):
    """Copy of a DataFrame with string cells, index labels and column labels in display form."""
    import pandas as pd
    out = df.copy()
    for c in out.columns:
        if out[c].dtype == object or str(out[c].dtype) in ("string", "category"):
            out[c] = out[c].map(D)
    def lab(ix):
        if isinstance(ix, pd.MultiIndex):
            return ix.set_levels([[D(v) for v in lv] for lv in ix.levels])
        return ix.map(lambda v: D(v) if isinstance(v, str) else v)
    out.index = lab(out.index)
    out.columns = lab(out.columns)
    return out


_INSTALLED = set()


def install(plots=True, frames=True, print_=True):
    if plots and "plots" not in _INSTALLED:
        import matplotlib.text as mt
        orig = mt.Text.set_text
        if not hasattr(orig, "__wrapped__"):
            def set_text(self, s):
                return orig(self, D(s) if isinstance(s, str) else s)
            set_text.__wrapped__ = orig
            mt.Text.set_text = set_text
        _INSTALLED.add("plots")
    if frames and "frames" not in _INSTALLED:
        try:
            import pandas as pd
            from IPython import get_ipython
            ip = get_ipython()
            if ip is not None:
                html = ip.display_formatter.formatters["text/html"]
                dh = _rd().display_html
                html.for_type(pd.DataFrame, lambda df: dh(df._repr_html_()))
                try:
                    from pandas.io.formats.style import Styler
                    html.for_type(Styler, lambda st: dh(st._repr_html_()))
                except Exception:
                    pass
                _INSTALLED.add("frames")
        except Exception:
            pass
    if print_ and "print" not in _INSTALLED:
        import builtins
        orig_print = builtins.print
        if not hasattr(orig_print, "__wrapped__"):
            def _print(*args, **kw):
                conv = lambda a: D(a) if isinstance(a, str) else (
                    D(str(a)) if type(a).__module__.split(".")[0] == "pandas" else a)
                return orig_print(*[conv(a) for a in args], **kw)
            _print.__wrapped__ = orig_print
            builtins.print = _print
        _INSTALLED.add("print")
    return sorted(_INSTALLED)
