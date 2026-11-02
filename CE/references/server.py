#!/usr/bin/env python3
"""
Renown settlement-board server  —  stdlib only, no pip installs.

Serves the lobby (main menu) and settlement_board.html, and persists state to SQLite.

Games (v3):
  * Every game is its own SQLite file, games/<id>.db, opened per request; an idle game costs nothing
    but its file. "main" is the original single game (RENOWN_DB), kept for old links.
  * A game lives under /g/<id>/: the board at /g/<id>/, its API at /g/<id>/api/... (routes below).
    Plain /api/... (no /g/ prefix) is the main game.
  * games/lobby.db lists the games (name, seats, Duke PIN hash, created, last active, archived).

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
    RENOWN_DUKE_PIN=<pin> python server.py   # PIN for the Duke (admin) on the board (unset = open)
    RENOWN_ORIGIN=https://board.example.com  # lock CORS (default *)

API (JSON):
    GET    /                                   -> the lobby (main menu)
    GET    /api/games[?all=1]                  -> {games:[{id,name,seats,players,claimed,started,turn,live,last_active,pin,archived}]}
    POST   /api/games          {name,seats,pin}-> {id}
    POST   /api/games/<id>/archive {archived,pin} -> {ok}   (needs that game's Duke PIN when it has one)
    GET    /g/<id>/                            -> the board for game <id>
    GET    /g/<id>/api/game                    -> {id,name,seats}
  Game routes (prefix /g/<id>, or none for the main game):
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

Chat — kept out of shared state; recipients filtered here, never on the client:
    GET    /api/chat?since=<id>              -> {me:{pid,name,duke}, msgs:[...]}  (visible to the caller only)
    POST   /api/chat  {scope, to?, text}     -> {ok, id} | 400 {error}
           scope "all"      everyone (spectators may post here only)
           scope "whisper"  to=<pid>|"duke"  sender + that player (stored by pid: delivered once claimed)
           scope "alliance" sender + every player allied to them (Military/Defensive Alliance or same
                            Suzerain household), resolved at send time from shared.diplo
    DELETE /api/chat                         -> Duke only: clear the log
    Identity: X-Renown-Dev + X-Renown-Key (device secret, registered on first use); the sender/viewer
    is the player whose board claim names that device. The Duke (X-Renown-Pin, or X-Renown-Duke:1
    when no PIN is set) sees every message.
"""
import http.server, socketserver, json, os, sqlite3, urllib.parse, datetime, threading, hmac, re, hashlib, secrets, time

HERE   = os.path.dirname(os.path.abspath(__file__))
HTML   = os.path.join(HERE, "settlement_board.html")
DB     = os.environ.get("RENOWN_DB", os.path.join(HERE, "renown.db"))
PORT   = int(os.environ.get("PORT", "8000"))
TOKEN  = os.environ.get("RENOWN_TOKEN", "")
ADMIN_PIN = os.environ.get("RENOWN_DUKE_PIN", os.environ.get("RENOWN_ADMIN_PIN", ""))   # unlocks the Duke (admin) on the board; unset = open
ORIGIN = os.environ.get("RENOWN_ORIGIN", "*")
LOBBY_HTML = os.path.join(HERE, "lobby.html")
GAMES_DIR  = os.environ.get("RENOWN_GAMES", os.path.join(HERE, "games"))
LOBBY_DB   = os.path.join(GAMES_DIR, "lobby.db")
MAIN_GAME  = "main"                                                # the original single game (RENOWN_DB)
GAME_RE    = re.compile(r"^/g/([a-z0-9-]{1,40})(/.*)?$")
LIVE_SECS  = 90                                                    # a game polled this recently is "live"
SEATS_MAX  = 7

LOCAL_KEYS = {"active", "view", "theme", "shape", "pursuitView"}   # per-browser UI, never shared
BATTLE_RE = re.compile(r"^/api/battle/([A-Za-z0-9_-]{1,40})/(\d{1,4})(?:/([AB]))?$")
PART_RE = re.compile(r"^(shared|board:[A-Za-z0-9_-]{1,40})$")
DEV_RE = re.compile(r"^[A-Za-z0-9_-]{4,64}$")
CHAT_MAX_LEN = 500       # characters per message
CHAT_BACKLOG = 200       # messages returned on a full (since=0) load
CTX = threading.local()                                            # per request: .gid (one thread per request)
LOCKS, LOCKS_GUARD = {}, threading.Lock()                          # one write lock per game
SEEN = {}                                                          # gid -> time of its last request (live dot)
INITED = set()                                                     # games whose tables exist this run

def gid():
    return getattr(CTX, "gid", MAIN_GAME)

def game_path(g):
    return DB if g == MAIN_GAME else os.path.join(GAMES_DIR, g + ".db")

def game_lock():
    with LOCKS_GUARD:
        return LOCKS.setdefault(gid(), threading.Lock())

def db():
    """Connection to the current request's game; creates its tables on first touch."""
    g = gid()
    if g not in INITED:
        with LOCKS_GUARD:
            if g not in INITED:
                init_db(game_path(g)); INITED.add(g)
    c = sqlite3.connect(game_path(g), timeout=10); c.row_factory = sqlite3.Row; return c

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

def init_db(path):
    c = sqlite3.connect(path, timeout=10); c.row_factory = sqlite3.Row
    c.executescript("""
      CREATE TABLE IF NOT EXISTS state(id INTEGER PRIMARY KEY CHECK(id=1), data TEXT, updated_at TEXT);
      CREATE TABLE IF NOT EXISTS parts(key TEXT PRIMARY KEY, data TEXT, version INTEGER, rev INTEGER, updated_at TEXT);
      CREATE TABLE IF NOT EXISTS meta(k TEXT PRIMARY KEY, v INTEGER);
      CREATE TABLE IF NOT EXISTS builds(name TEXT PRIMARY KEY, data TEXT, updated_at TEXT);
      CREATE TABLE IF NOT EXISTS snapshots(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, data TEXT, ts TEXT);
      CREATE TABLE IF NOT EXISTS battle_picks(bid TEXT, sk INTEGER, side TEXT, tactic TEXT, ts TEXT,
                                              PRIMARY KEY(bid, sk, side));
      CREATE TABLE IF NOT EXISTS devices(dev TEXT PRIMARY KEY, key_hash TEXT, ts TEXT);
      CREATE TABLE IF NOT EXISTS chat(id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, dev TEXT, pid TEXT,
                                      name TEXT, color TEXT, scope TEXT, to_pid TEXT, to_name TEXT,
                                      recips TEXT, text TEXT);
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

# ---------------- lobby ----------------
def lobby():
    os.makedirs(GAMES_DIR, exist_ok=True)
    c = sqlite3.connect(LOBBY_DB, timeout=10); c.row_factory = sqlite3.Row; return c

def init_lobby():
    c = lobby()
    c.execute("""CREATE TABLE IF NOT EXISTS games(id TEXT PRIMARY KEY, name TEXT, seats INTEGER, pin_hash TEXT,
                                              created TEXT, last_active TEXT, archived INTEGER DEFAULT 0)""")
    if os.path.exists(DB) and not c.execute("SELECT 1 FROM games WHERE id=?", (MAIN_GAME,)).fetchone():
        c.execute("INSERT INTO games(id,name,seats,pin_hash,created,last_active) VALUES(?,?,?,?,?,?)",
                  (MAIN_GAME, "Main game", 0, "", now(), now()))
    c.commit(); c.close()

def game_row(g):
    c = lobby(); r = c.execute("SELECT * FROM games WHERE id=?", (g,)).fetchone(); c.close()
    return dict(r) if r else None

def pin_hash(pin):
    return hashlib.sha256(("renown:" + pin).encode()).hexdigest() if pin else ""

def duke_pin_set():
    """True when the current game needs a Duke PIN (its own, or RENOWN_DUKE_PIN for the main game)."""
    r = game_row(gid()) or {}
    return bool(r.get("pin_hash") or (gid() == MAIN_GAME and ADMIN_PIN))

def duke_pin_ok(pin, g=None):
    r = game_row(g or gid()) or {}
    if r.get("pin_hash"):
        return hmac.compare_digest(pin_hash(pin), r["pin_hash"])
    if (g or gid()) == MAIN_GAME and ADMIN_PIN:
        return hmac.compare_digest(pin, ADMIN_PIN)
    return True

def touch(write=False):
    """Mark the current game seen; on writes also store last_active in the lobby."""
    SEEN[gid()] = time.time()
    if write:
        c = lobby(); c.execute("UPDATE games SET last_active=? WHERE id=?", (now(), gid())); c.commit(); c.close()

def slug(name):
    s = re.sub(r"[^a-z0-9]+", "-", (name or "").lower()).strip("-")[:24].strip("-")
    return (s or "game") + "-" + secrets.token_hex(2)

def game_summary(r):
    """Lobby row + what the game's own file says (players, claims, started, turn)."""
    out = {k: r[k] for k in ("id", "name", "seats", "created", "last_active")}
    out["archived"] = bool(r["archived"]); out["pin"] = bool(r["pin_hash"] or (r["id"] == MAIN_GAME and ADMIN_PIN))
    seen = SEEN.get(r["id"])
    out["live"] = bool(seen and time.time() - seen < LIVE_SECS)
    out.update(players=0, claimed=0, started=False, turn=0)
    path = game_path(r["id"])
    if os.path.exists(path):
        try:
            c = sqlite3.connect(path, timeout=5); c.row_factory = sqlite3.Row
            sh = c.execute("SELECT data FROM parts WHERE key='shared'").fetchone()
            sh = json.loads(sh["data"]) if sh else {}
            out["players"] = len(sh.get("roster") or {})
            out["started"] = bool(sh.get("started"))
            out["turn"] = int((sh.get("tbl") or {}).get("turn") or 1) if sh else 0
            for b in c.execute("SELECT data FROM parts WHERE key LIKE 'board:%'"):
                if (json.loads(b["data"]) or {}).get("claim"):
                    out["claimed"] += 1
            c.close()
        except Exception:
            pass
    return out

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

# ---------------- chat helpers ----------------
def load_part(c, key):
    r = c.execute("SELECT data FROM parts WHERE key=?", (key,)).fetchone()
    try:
        return json.loads(r["data"]) if r else None
    except Exception:
        return None

def roster(c):
    return ((load_part(c, "shared") or {}).get("roster")) or {}

def claimed_pid(c, dev):
    """pid of the player whose board claim names this device, else None."""
    for r in c.execute("SELECT key,data FROM parts WHERE key LIKE 'board:%'"):
        try:
            cl = (json.loads(r["data"]) or {}).get("claim") or {}
        except Exception:
            continue
        if cl.get("dev") == dev:
            return r["key"][len("board:"):]
    return None

def top_suz(diplo, pid):
    """Mirrors topSuz() in the board: follow the Suzerain chain to its top."""
    sz, cur = diplo.get("suzerain") or {}, str(pid)
    for _ in range(16):
        nxt = sz.get(cur)
        if not nxt:
            break
        cur = str(nxt)
    return cur

def same_alliance(diplo, a, b):
    """Mirrors sameAlliance() in the board: same Suzerain household, or tops share an Alliance group."""
    a, b = str(a), str(b)
    if a == b:
        return False
    ra, rb = top_suz(diplo, a), top_suz(diplo, b)
    if ra == rb:
        return True
    g = (diplo.get("member") or {}).get(ra)
    return bool(g) and g == (diplo.get("member") or {}).get(rb)

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
        self.send_header("Access-Control-Allow-Headers",
                         "Content-Type, X-Renown-Token, X-Renown-Dev, X-Renown-Key, X-Renown-Pin, X-Renown-Duke")
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

    def _redirect(self, to):
        self.send_response(302); self.send_header("Location", to); self.send_header("Content-Length", "0"); self.end_headers()

    def _route(self, method):
        """Pick the game for this request and strip its /g/<id> prefix from self.path.
        Returns False when the request was answered here (lobby, redirect, unknown game, auth)."""
        u = urllib.parse.urlparse(self.path); path = u.path
        CTX.gid = MAIN_GAME
        m = GAME_RE.match(path)
        if m:
            g, rest = m.group(1), m.group(2)
            if rest is None:
                self._redirect(path + "/" + ("?" + u.query if u.query else "")); return False
            if not game_row(g) and not (g == MAIN_GAME and os.path.exists(DB)):
                self._send(404, {"error": "no such game"}); return False
            CTX.gid = g
            self.path = rest + ("?" + u.query if u.query else "")
            path = rest
        elif path in ("/", "/index.html", "/lobby") and method == "GET":
            self._file(LOBBY_HTML, "lobby.html not found next to server.py"); return False
        elif path == "/api/games" or path.startswith("/api/games/"):
            if self._authed(path):
                self._lobby_api(method, path, u)
            return False
        if not self._authed(path):
            return False
        if path.startswith("/api/"):
            touch(write=method != "GET")
        return True

    def _file(self, fn, missing):
        try:
            with open(fn, "rb") as f:
                self._send(200, f.read(), "text/html; charset=utf-8")
        except FileNotFoundError:
            self._send(404, {"error": missing})

    def _lobby_api(self, method, path, u):
        if method == "GET" and path == "/api/games":
            show_all = urllib.parse.parse_qs(u.query).get("all", ["0"])[0] == "1"
            c = lobby(); rows = c.execute("SELECT * FROM games ORDER BY last_active DESC").fetchall(); c.close()
            self._send(200, {"games": [game_summary(r) for r in rows if show_all or not r["archived"]]}); return
        if method == "POST" and path == "/api/games":
            body = self._read()
            name = re.sub(r"[\x00-\x1f\x7f]", "", str(body.get("name") or "")).strip()[:60] or "New game"
            try:
                seats = max(1, min(SEATS_MAX, int(body.get("seats") or 1)))
            except (TypeError, ValueError):
                seats = 1
            pin = str(body.get("pin") or "")[:64]
            c = lobby()
            g = slug(name)
            while c.execute("SELECT 1 FROM games WHERE id=?", (g,)).fetchone():
                g = slug(name)
            c.execute("INSERT INTO games(id,name,seats,pin_hash,created,last_active) VALUES(?,?,?,?,?,?)",
                      (g, name, seats, pin_hash(pin), now(), now()))
            c.commit(); c.close()
            self._send(200, {"id": g}); return
        m = re.match(r"^/api/games/([a-z0-9-]{1,40})/archive$", path)
        if method == "POST" and m:
            body = self._read(); g = m.group(1)
            if not game_row(g):
                self._send(404, {"error": "no such game"}); return
            if not duke_pin_ok(str(body.get("pin") or ""), g):
                self._send(403, {"error": "Duke PIN required"}); return
            c = lobby(); c.execute("UPDATE games SET archived=? WHERE id=?", (1 if body.get("archived", True) else 0, g))
            c.commit(); c.close()
            self._send(200, {"ok": True}); return
        if method == "OPTIONS":
            self._send(204); return
        self._send(404, {"error": "unknown route"})

    # ---------------- chat ----------------
    def _who(self, c):
        """Verify the device secret (registered on first use) -> {dev, pid, name, color, duke}; None after an error reply."""
        dev, key = self.headers.get("X-Renown-Dev", ""), self.headers.get("X-Renown-Key", "")
        if not DEV_RE.match(dev) or not (16 <= len(key) <= 128):
            self._send(400, {"error": "missing device identity"}); return None
        h = hashlib.sha256(key.encode()).hexdigest()
        with game_lock():
            r = c.execute("SELECT key_hash FROM devices WHERE dev=?", (dev,)).fetchone()
            if r is None:
                c.execute("INSERT INTO devices(dev,key_hash,ts) VALUES(?,?,?)", (dev, h, now())); c.commit()
            elif not hmac.compare_digest(r["key_hash"], h):
                self._send(403, {"error": "device key mismatch"}); return None
        pin = self.headers.get("X-Renown-Pin", "")
        duke = duke_pin_ok(pin) if duke_pin_set() else self.headers.get("X-Renown-Duke") == "1"
        pid = claimed_pid(c, dev)
        ro = roster(c).get(pid) or {} if pid else {}
        name = ro.get("name") if pid else ("Duke" if duke else "Spectator " + dev[:4])
        return {"dev": dev, "pid": pid, "name": name or "?", "color": ro.get("color") or "", "duke": duke}

    def _chat_get(self, u):
        try:
            since = int(urllib.parse.parse_qs(u.query).get("since", ["0"])[0])
        except ValueError:
            since = 0
        c = db()
        try:
            me = self._who(c)
            if not me:
                return
            out = []
            last = c.execute("SELECT COALESCE(MAX(id),0) AS m FROM chat").fetchone()["m"]
            for r in c.execute("SELECT * FROM chat WHERE id>? AND id<=? ORDER BY id", (since, last)):
                rec = json.loads(r["recips"]) if r["recips"] else []
                vis = (r["scope"] == "all" or me["duke"] or r["dev"] == me["dev"]
                       or (me["pid"] is not None and (r["pid"] == me["pid"] or me["pid"] in rec)))
                if vis:
                    out.append({"id": r["id"], "ts": r["ts"], "pid": r["pid"], "name": r["name"], "color": r["color"],
                                "scope": r["scope"], "to": r["to_pid"], "toName": r["to_name"], "text": r["text"],
                                "mine": r["dev"] == me["dev"]})
            self._send(200, {"me": {k: me[k] for k in ("pid", "name", "duke")}, "last": last,
                             "msgs": out[-CHAT_BACKLOG:] if not since else out})
        finally:
            c.close()

    def _chat_post(self, body):
        c = db()
        try:
            me = self._who(c)
            if not me:
                return
            text = re.sub(r"[\x00-\x08\x0b-\x1f\x7f]", "", str(body.get("text") or "")).strip()[:CHAT_MAX_LEN]
            scope = body.get("scope") or "all"
            if not text:
                self._send(400, {"error": "empty message"}); return
            if scope not in ("all", "whisper", "alliance"):
                self._send(400, {"error": "unknown scope"}); return
            if scope != "all" and not me["pid"] and not me["duke"]:
                self._send(400, {"error": "spectators can post to All only"}); return
            to_pid = to_name = None; recips = []
            ro = roster(c)
            if scope == "whisper":
                to_pid = str(body.get("to") or "")
                if to_pid == "duke":
                    to_name = "Duke"
                elif to_pid in ro:
                    to_name = ro[to_pid].get("name") or "?"
                else:
                    self._send(400, {"error": "no such player"}); return
                if to_pid == me["pid"]:
                    self._send(400, {"error": "can't whisper yourself"}); return
                recips = [to_pid]
            elif scope == "alliance":
                if not me["pid"]:
                    self._send(400, {"error": "claim a player to use alliance chat"}); return
                diplo = (load_part(c, "shared") or {}).get("diplo") or {}
                recips = [q for q in ro if same_alliance(diplo, me["pid"], q)]
                if not recips:
                    self._send(400, {"error": "not in an alliance"}); return
            with game_lock():
                cur = c.execute("INSERT INTO chat(ts,dev,pid,name,color,scope,to_pid,to_name,recips,text) "
                                "VALUES(?,?,?,?,?,?,?,?,?,?)",
                                (now(), me["dev"], me["pid"], me["name"], me["color"], scope, to_pid, to_name,
                                 json.dumps(recips) if recips else None, text))
                c.commit()
            self._send(200, {"ok": True, "id": cur.lastrowid})
        finally:
            c.close()

    def _chat_clear(self):
        c = db()
        try:
            me = self._who(c)
            if not me:
                return
            if not me["duke"]:
                self._send(403, {"error": "Duke only"}); return
            with game_lock():
                c.execute("DELETE FROM chat"); c.commit()
            self._send(200, {"ok": True})
        finally:
            c.close()

    def do_OPTIONS(self):
        self._send(204)

    # ---------------- GET ----------------
    def do_GET(self):
        if not self._route("GET"):
            return
        u = urllib.parse.urlparse(self.path); path = u.path
        if path in ("/", "/index.html"):
            self._file(HTML, "settlement_board.html not found next to server.py — generate it first"); return
        if path == "/api/game":
            r = game_row(gid()) or {}
            self._send(200, {"id": gid(), "name": r.get("name") or gid(), "seats": r.get("seats") or 0}); return
        if path == "/api/chat":
            self._chat_get(u); return
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
        with game_lock():
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
        if not self._route("PUT"):
            return
        path = urllib.parse.urlparse(self.path).path
        body = self._read()
        key = part_key(path)
        if key:
            self._write_part(key, body); return
        m = BATTLE_RE.match(path)
        if m and m.group(3):
            bid, sk, side = m.group(1), int(m.group(2)), m.group(3)
            tac = str(body.get("tactic") or "")[:60]
            with game_lock():
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
        if not self._route("POST"):
            return
        path = urllib.parse.urlparse(self.path).path
        body = self._read()
        if path == "/api/chat":
            self._chat_post(body); return
        if path == "/api/admin":                     # {"pin": "..."} -> {"ok": bool, "open": bool}
            if not duke_pin_set():
                self._send(200, {"ok": True, "open": True}); return
            ok = duke_pin_ok(str(body.get("pin", "")))
            self._send(200 if ok else 403, {"ok": ok, "open": False}); return
        name = build_name(path, "/snapshot")
        if name is not None:
            c = db(); c.execute("INSERT INTO snapshots(name,data,ts) VALUES(?,?,?)",
                                 (name, json.dumps(body.get("data")), now())); c.commit()
            sid = c.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]; c.close()
            self._send(200, {"ok": True, "id": sid}); return
        self._send(404, {"error": "unknown route"})

    def do_DELETE(self):
        if not self._route("DELETE"):
            return
        path = urllib.parse.urlparse(self.path).path
        if path == "/api/chat":
            self._chat_clear(); return
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
    init_lobby()
    print(f"Renown board:  http://localhost:{PORT}")
    print(f"Main game:     {DB}")
    print(f"Games:         {GAMES_DIR}  (lobby at /)")
    print(f"Auth:          {'token required' if TOKEN else 'open (no RENOWN_TOKEN set)'}")
    print(f"Duke (main):   {'PIN required' if ADMIN_PIN else 'open (no RENOWN_DUKE_PIN set)'}; other games set their own PIN")
    print("Ctrl-C to stop.")
    Server(("0.0.0.0", PORT), Handler).serve_forever()