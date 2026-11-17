"""lab_guard — keep a notebook "Run All" going past a failing cell.

    import lab_guard; lab_guard.install()      # once, in the first cell
    ...
    lab_guard.report()                         # last cell: every cell that failed this session

After install(), each cell runs inside try/except: an exception prints its full traceback under the cell
(as stderr text) and is recorded, and the cell then ends normally, so the next cell still runs. The cell's
last expression is still displayed (a trailing ";" still hides it). KeyboardInterrupt / SystemExit are not
caught, so the stop button still stops the run. uninstall() turns it off.

IPython's own showtraceback() is not used: ipykernel would mark the cell as failed, and Jupyter stops a
Run All at the first failed cell, which is exactly what this avoids.
"""
import ast
import sys

FAILURES = []          # (execution count, exception type, message, first line of the cell)
_NS_SHOW, _NS_FAIL = "_lab_guard_show", "_lab_guard_fail"


class _Wrap(ast.NodeTransformer):
    def visit_Module(self, node):
        body = node.body
        if not body:
            return node
        # __future__ imports must stay first and outside the try
        head = []
        while body and isinstance(body[0], ast.ImportFrom) and body[0].module == "__future__":
            head.append(body.pop(0))
        if not body:
            node.body = head
            return node
        if isinstance(body[-1], ast.Expr):                 # keep "last expression is shown"
            body[-1] = ast.Expr(ast.Call(ast.Name(_NS_SHOW, ast.Load()), [body[-1].value], []))
        handler = ast.ExceptHandler(type=ast.Name("Exception", ast.Load()), name=None,
                                    body=[ast.Expr(ast.Call(ast.Name(_NS_FAIL, ast.Load()), [], []))])
        node.body = head + [ast.Try(body=body, handlers=[handler], orelse=[], finalbody=[])]
        return ast.fix_missing_locations(node)


_WRAP = _Wrap()


def _ip():
    try:
        return get_ipython()          # noqa: F821  (defined inside IPython)
    except NameError:
        return None


def _show(value):
    ip = _ip()
    if ip is not None and value is not None:
        ip.displayhook(value)         # same path IPython uses: Out[n], _, trailing ";" respected


def _fail():
    ip = _ip()
    etype, value, tb = sys.exc_info()
    n = getattr(ip, "execution_count", None)
    try:
        src = (ip.history_manager.input_hist_raw[-1] if ip is not None else "") or ""
        first = next((l.strip() for l in src.splitlines() if l.strip()), "")[:100]
    except Exception:
        first = ""
    FAILURES.append((n, etype.__name__, str(value)[:300], first))
    sys.stdout.flush()
    try:
        tb_next = tb.tb_next if tb is not None and tb.tb_next is not None else tb   # skip the guard frame
        text = "\n".join(ip.InteractiveTB.structured_traceback(etype, value, tb_next))
    except Exception:
        import traceback
        text = "".join(traceback.format_exception(etype, value, tb))
    sys.stderr.write(text + f"\n[lab_guard] cell {n} failed ({etype.__name__}); the lab carries on.\n")
    sys.stderr.flush()


def install():
    """Wrap every following cell. Safe to call twice."""
    ip = _ip()
    if ip is None:
        return False
    ip.user_ns[_NS_SHOW] = _show
    ip.user_ns[_NS_FAIL] = _fail
    if not any(isinstance(t, _Wrap) for t in ip.ast_transformers):
        ip.ast_transformers.append(_WRAP)
    return True


def uninstall():
    ip = _ip()
    if ip is not None:
        ip.ast_transformers[:] = [t for t in ip.ast_transformers if not isinstance(t, _Wrap)]


def report():
    """Print every cell that failed since install() (or the last clear())."""
    if not FAILURES:
        print("lab_guard: no cell failed.")
        return
    print(f"lab_guard: {len(FAILURES)} cell(s) failed:")
    for n, et, msg, first in FAILURES:
        print(f"  [{n}] {et}: {msg.splitlines()[0] if msg else ''}\n        cell starts: {first}")


def clear():
    FAILURES.clear()
