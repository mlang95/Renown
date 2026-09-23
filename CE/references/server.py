#!/usr/bin/env python3
"""
Renown settlement-board server  —  stdlib only, no pip installs.

Serves settlement_board.html and persists state to SQLite.

Multi-client sync (v2):
  * State is split into parts: "shared" (renown, map, roster, start domains…)
    and one "board:<player_id>" per player. Clients only write parts they changed.
  * Every part carries a version. A write must name the version it was based on;
    a stale write gets 409 + the current copy, and the client merges and retries.
  * A global revision counter lets clients poll cheaply:
    GET /api/state?since=<rev> returns only parts written after <rev>.

Run:
    python server.py                         # http://localhost:8000
    PORT=9000 python server.py
    RENOWN_DB=/path/board.db python server.py
    RENOWN_TOKEN=<secret> python server.py   # require X-Renown-Token on /api/*
    RENOWN_ORIGIN=https://board.example.com  # lock CORS (default *)

API (JSON):
    GET    /                                   -> the app
    GET    /api/state[?since=N]                -> {rev, keys:[...], parts:{key:{data,version}}}
    PUT    /api/part/<key>      {data, base}   -> {version, rev} | 409 {data, version}
    DELETE /api/part/<key>      {base}         -> {rev}          | 409 {data, version}
    GET    /api/builds                         -> {builds:[{name,updated_at}]}
    GET    /api/builds/<name>                  -> {name,data,updated_at}
    PUT    /api/builds/<name>   {data}         -> upsert named build
    DELETE /api/builds/<name>                  -> delete named build
    POST   /api/builds/<name>/snapshot {data}  -> append timestamped snapshot
    GET    /api/builds/<name>/snapshots        -> {snapshots:[{id,ts}]}
    GET    /api/builds/<name>/snapshots/<id>   -> {id,ts,data}

Hidden tactic picks (battle module) — kept out of shared state:
    PUT    /api/battle/<bid>/<sk>/<side>  {tactic}   -> 200 | 409 once both sides are locked in
    GET    /api/battle/<bid>/<sk>?viewer=A|B|-&peek=0|1
        -> {A:{picked,tactic?}, B:{picked,tactic?}, revealed}
        A side's tactic is returned only if: both picked, OR it is the viewer's own,
        OR peek=1 and it is the viewer's opponent (Outrider Intercept Post carve-out).
"""
import http.server, socketserver, json, os, sqlite3, urllib.parse, datetime, threading, hmac, re

HERE   = os.path.dirname(os.path.abspath(__file__))
HTML   = os.path.join(HERE, "settlement_board.html")
DB     = os.environ.get("RENOWN_DB", os.path.join(HERE, "renown.db"))
PORT   = int(os.environ.get("PORT", "8000"))
TOKEN  = os.environ.get("RENOWN_TOKEN", "")
ORIGIN = os.environ.get("RENOWN_ORIGIN", "*")

LOCAL_KEYS = {"active", "view", "theme", "shape", "pursuitView"}   # per-browser UI, never shared
BATTLE_RE = re.compile(r"^/api/battle/([A-Za-z0-9_-]{1,40})/(\d{1,4})(?:/([AB]))?$")
PART_RE = re.compile(r"^(shared|board:[A-Za-z0-9_-]{1,40})$")
LOCK = threading.Lock()                                            # serialises part writes

def db():
    c = sqlite3.connect(DB, timeout=10); c.row_factory = sqlite3.Row; return c

def now():
    return datetime.datetime.now().isoformat(timespec="seconds")

def split_state(D):
    """Legacy whole-state blob -> {part_key: data}. Mirrors splitD() in the HTML."""
    shared = {k: v for k, v in D.items() if k not in LOCAL_KEYS and k != "players"}
    shared["roster"] = {}
    parts = {}
    for p in D.get("players") or []:
        pid = str(p.get("id"))
        shared["roster"][pid] = {"name": p.get("name"), "color": p.get("color")}
        parts["board:" + pid] = p.get("board") or {}
    parts["shared"] = shared
    return parts

def init_db():
    c = db()
    c.executescript("""
      CREATE TABLE IF NOT EXISTS state(id INTEGER PRIMARY KEY CHECK(id=1), data TEXT, updated_at TEXT);
      CREATE TABLE IF NOT EXISTS parts(key TEXT PRIMARY KEY, data TEXT, version INTEGER, rev INTEGER, updated_at TEXT);
      CREATE TABLE IF NOT EXISTS meta(k TEXT PRIMARY KEY, v INTEGER);
      CREATE TABLE IF NOT EXISTS builds(name TEXT PRIMARY KEY, data TEXT, updated_at TEXT);
      CREATE TABLE IF NOT EXISTS snapshots(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, data TEXT, ts TEXT);
      CREATE TABLE IF NOT EXISTS battle_picks(bid TEXT, sk INTEGER, side TEXT, tactic TEXT, ts TEXT,
                                              PRIMARY KEY(bid, sk, side));
    """)
    c.execute("INSERT OR IGNORE INTO meta(k,v) VALUES('rev',0)")
    # one-time migration: v1 single-blob state -> parts
    if not c.execute("SELECT 1 FROM parts LIMIT 1").fetchone():
        r = c.execute("SELECT data FROM state WHERE id=1").fetchone()
        if r and r["data"]:
            try:
                D = json.loads(r["data"])
                if isinstance(D, dict) and D.get("players"):
                    for k, v in split_state(D).items():
                        c.execute("INSERT INTO parts(key,data,version,rev,updated_at) VALUES(?,?,1,1,?)",
                                  (k, json.dumps(v), now()))
                    c.execute("UPDATE meta SET v=1 WHERE k='rev'")
                    print("  migrated v1 state -> parts")
            except Exception as e:
                print("  v1 state migration skipped:", e)
    c.commit(); c.close()

def get_rev(c):
    return c.execute("SELECT v FROM meta WHERE k='rev'").fetchone()["v"]

def build_name(path, suffix=""):
    prefix = "/api/builds/"
    if not path.startswith(prefix):
        return None
    rest = path[len(prefix):]
    if suffix:
        if not rest.endswith(suffix):
            return None
        rest = rest[:-len(suffix)]
    if "/" in rest or rest == "":
        return None
    return urllib.parse.unquote(rest)

def part_key(path):
    if not path.startswith("/api/part/"):
        return None
    k = urllib.parse.unquote(path[len("/api/part/"):])
    return k if PART_RE.match(k) else None

class Handler(http.server.BaseHTTPRequestHandler):
    def _send(self, code, obj=None, ctype="application/json"):
        body = b"" if obj is None else (obj if isinstance(obj, bytes) else json.dumps(obj).encode())
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", ORIGIN)
        self.send_header("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Renown-Token")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if body:
            self.wfile.write(body)

    def _read(self):
        n = int(self.headers.get("Content-Length") or 0)
        if not n:
            return {}
        try:
            return json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            return {}

    def _authed(self, path):
        if not path.startswith("/api/") or not TOKEN:
            return True
        if hmac.compare_digest(self.headers.get("X-Renown-Token", ""), TOKEN):
            return True
        self._send(401, {"error": "unauthorized"})
        return False

    def log_message(self, *a):
        pass

    def do_OPTIONS(self):
        self._send(204)

    # ---------------- GET ----------------
    def do_GET(self):
        u = urllib.parse.urlparse(self.path); path = u.path
        if not self._authed(path):
            return
        if path in ("/", "/index.html"):
            try:
                with open(HTML, "rb") as f:
                    self._send(200, f.read(), "text/html; charset=utf-8")
            except FileNotFoundError:
                self._send(404, {"error": "settlement_board.html not found next to server.py — generate it first"})
            return
        if path == "/api/state":
            try:
                since = int(urllib.parse.parse_qs(u.query).get("since", ["0"])[0])
            except ValueError:
                since = 0
            c = db(); rev = get_rev(c)
            if since and since >= rev:
                c.close(); self._send(200, {"rev": rev, "changed": False}); return
            keys = [r["key"] for r in c.execute("SELECT key FROM parts")]
            rows = c.execute("SELECT key,data,version FROM parts WHERE rev>?", (since,)).fetchall()
            c.close()
            self._send(200, {"rev": rev, "changed": True, "keys": keys,
                             "parts": {r["key"]: {"data": json.loads(r["data"]), "version": r["version"]} for r in rows}})
            return
        m = BATTLE_RE.match(path)
        if m and not m.group(3):
            q = urllib.parse.parse_qs(u.query)
            viewer = q.get("viewer", ["-"])[0]; peek = q.get("peek", ["0"])[0] == "1"
            c = db(); rows = {r["side"]: r["tactic"] for r in c.execute(
                "SELECT side,tactic FROM battle_picks WHERE bid=? AND sk=?", (m.group(1), int(m.group(2))))}; c.close()
            both = "A" in rows and "B" in rows
            out = {"revealed": both}
            for side in ("A", "B"):
                d = {"picked": side in rows}
                opp = "B" if viewer == "A" else "A" if viewer == "B" else None
                if side in rows and (both or side == viewer or (peek and side == opp)):
                    d["tactic"] = rows[side]
                out[side] = d
            self._send(200, out); return
        if path == "/api/builds":
            c = db(); rows = c.execute("SELECT name,updated_at FROM builds ORDER BY updated_at DESC").fetchall(); c.close()
            self._send(200, {"builds": [dict(x) for x in rows]}); return
        name = build_name(path, "/snapshots")
        if name is not None:
            c = db(); rows = c.execute("SELECT id,ts FROM snapshots WHERE name=? ORDER BY ts DESC", (name,)).fetchall(); c.close()
            self._send(200, {"snapshots": [dict(x) for x in rows]}); return
        if path.startswith("/api/builds/") and "/snapshots/" in path:
            _, sid = path.rsplit("/snapshots/", 1)
            try:
                sid = int(sid)
            except ValueError:
                self._send(404, {"error": "bad snapshot id"}); return
            c = db(); r = c.execute("SELECT id,ts,data FROM snapshots WHERE id=?", (sid,)).fetchone(); c.close()
            if not r:
                self._send(404, {"error": "not found"}); return
            self._send(200, {"id": r["id"], "ts": r["ts"], "data": json.loads(r["data"])}); return
        name = build_name(path)
        if name is not None:
            c = db(); r = c.execute("SELECT data,updated_at FROM builds WHERE name=?", (name,)).fetchone(); c.close()
            if not r:
                self._send(404, {"error": "not found"}); return
            self._send(200, {"name": name, "data": json.loads(r["data"]), "updated_at": r["updated_at"]}); return
        self._send(404, {"error": "unknown route"})

    # ---------------- part write (PUT / DELETE) ----------------
    def _write_part(self, key, body, delete=False):
        base = body.get("base", 0)
        with LOCK:
            c = db()
            try:
                cur = c.execute("SELECT data,version FROM parts WHERE key=?", (key,)).fetchone()
                cur_v = cur["version"] if cur else 0
                if base != cur_v:
                    self._send(409, {"data": json.loads(cur["data"]) if cur else None, "version": cur_v}); return
                rev = get_rev(c) + 1
                c.execute("UPDATE meta SET v=? WHERE k='rev'", (rev,))
                if delete:
                    c.execute("DELETE FROM parts WHERE key=?", (key,))
                    c.commit(); self._send(200, {"rev": rev}); return
                v = cur_v + 1
                c.execute("INSERT INTO parts(key,data,version,rev,updated_at) VALUES(?,?,?,?,?) "
                          "ON CONFLICT(key) DO UPDATE SET data=excluded.data,version=excluded.version,"
                          "rev=excluded.rev,updated_at=excluded.updated_at",
                          (key, json.dumps(body.get("data")), v, rev, now()))
                c.commit(); self._send(200, {"version": v, "rev": rev})
            finally:
                c.close()

    def do_PUT(self):
        path = urllib.parse.urlparse(self.path).path
        if not self._authed(path):
            return
        body = self._read()
        key = part_key(path)
        if key:
            self._write_part(key, body); return
        m = BATTLE_RE.match(path)
        if m and m.group(3):
            bid, sk, side = m.group(1), int(m.group(2)), m.group(3)
            tac = str(body.get("tactic") or "")[:60]
            with LOCK:
                c = db()
                try:
                    n = c.execute("SELECT COUNT(*) AS n FROM battle_picks WHERE bid=? AND sk=?", (bid, sk)).fetchone()["n"]
                    if n >= 2:
                        self._send(409, {"error": "both sides locked in"}); return
                    c.execute("INSERT INTO battle_picks(bid,sk,side,tactic,ts) VALUES(?,?,?,?,?) "
                              "ON CONFLICT(bid,sk,side) DO UPDATE SET tactic=excluded.tactic,ts=excluded.ts",
                              (bid, sk, side, tac, now()))
                    c.commit(); self._send(200, {"ok": True})
                finally:
                    c.close()
            return
        name = build_name(path)
        if name is not None:
            c = db(); c.execute(
                "INSERT INTO builds(name,data,updated_at) VALUES(?,?,?) "
                "ON CONFLICT(name) DO UPDATE SET data=excluded.data,updated_at=excluded.updated_at",
                (name, json.dumps(body.get("data")), now())); c.commit(); c.close()
            self._send(200, {"ok": True, "name": name}); return
        self._send(404, {"error": "unknown route"})

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        if not self._authed(path):
            return
        body = self._read()
        name = build_name(path, "/snapshot")
        if name is not None:
            c = db(); c.execute("INSERT INTO snapshots(name,data,ts) VALUES(?,?,?)",
                                 (name, json.dumps(body.get("data")), now())); c.commit()
            sid = c.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]; c.close()
            self._send(200, {"ok": True, "id": sid}); return
        self._send(404, {"error": "unknown route"})

    def do_DELETE(self):
        path = urllib.parse.urlparse(self.path).path
        if not self._authed(path):
            return
        key = part_key(path)
        if key:
            self._write_part(key, self._read(), delete=True); return
        name = build_name(path)
        if name is not None:
            c = db(); c.execute("DELETE FROM builds WHERE name=?", (name,)); c.commit(); c.close()
            self._send(200, {"ok": True}); return
        self._send(404, {"error": "unknown route"})

class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

if __name__ == "__main__":
    init_db()
    print(f"Renown board:  http://localhost:{PORT}")
    print(f"Database:      {DB}")
    print(f"Auth:          {'token required' if TOKEN else 'open (no RENOWN_TOKEN set)'}")
    print("Ctrl-C to stop.")
    Server(("0.0.0.0", PORT), Handler).serve_forever()