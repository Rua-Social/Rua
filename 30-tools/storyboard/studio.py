"""Storyboard studio: open a disk project in the browser and save every edit back to it.

A small standard-library server bound to this computer only. Disk is the record:
edits save to board.json as you work, automatic snapshots keep recent history,
and "Save version" builds the shareable HTML as a numbered version.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

import storyboard as sb

HOST = "127.0.0.1"
PORT = int(os.environ.get("STORYBOARD_PORT", "4318"))
CONFIG_DIR = Path(os.environ.get("STORYBOARD_CONFIG_DIR", Path.home() / ".config" / "rua" / "storyboard"))
SNAPSHOT_EVERY = 10 * 60  # seconds between automatic snapshots while editing
SNAPSHOTS_KEPT = 30
WRITE_LOCK = threading.Lock()
AUDIO_EXTENSIONS = {ext: mime for mime, ext in sb.AUDIO_TYPES.items()}


class StudioError(sb.ProjectError):
    def __init__(self, message: str, status: int = 400):
        super().__init__(message)
        self.status = status


# ---- recent projects -------------------------------------------------------

def project_id(path: Path) -> str:
    return hashlib.sha256(str(path).encode("utf-8")).hexdigest()[:12]


def recent_file() -> Path:
    return CONFIG_DIR / "recent.json"


def read_recent() -> list:
    try:
        data = json.loads(recent_file().read_text(encoding="utf-8"))
        return [p for p in data.get("projects", []) if isinstance(p, dict) and isinstance(p.get("path"), str)]
    except (OSError, ValueError, AttributeError):
        return []


def remember(project_path) -> tuple[str, Path]:
    """Validate a project and put it at the top of the recent list. Returns (id, project.json path)."""
    path, manifest, board, _, _ = sb.load_project(project_path)
    title = manifest.get("config", {}).get("brand") or board.get("title") or path.parent.name
    entries = [p for p in read_recent() if p["path"] != str(path)]
    entries.insert(0, {"path": str(path), "title": title, "openedAt": datetime.now(timezone.utc).isoformat(timespec="seconds")})
    sb.atomic_write(recent_file(), sb.json_text({"projects": entries[:20]}).encode("utf-8"))
    return project_id(path), path


def project_roots() -> list[Path]:
    """Where storyboards live: every connected drive's "Rua Projects" folder, or STORYBOARD_ROOTS."""
    if os.environ.get("STORYBOARD_ROOTS"):
        return [Path(p).expanduser() for p in os.environ["STORYBOARD_ROOTS"].split(os.pathsep) if p]
    roots = sorted(Path("/Volumes").glob("*/Rua Projects")) + [Path.home() / "Rua Projects"]
    return [r for r in roots if r.is_dir()]


SKIP_DIRS = {"earlier", "node_modules", "autosave", "Exports", "Footage", "Media"}


def discover(max_depth=7) -> list[dict]:
    """Find storyboard projects under the project roots. Earlier copies are not listed."""
    found = []
    for root in project_roots():
        base_depth = len(root.parts)
        for folder, dirs, files in os.walk(root):
            depth = len(Path(folder).parts) - base_depth
            dirs[:] = [] if depth >= max_depth else [d for d in dirs if not d.startswith(".") and d not in SKIP_DIRS]
            if "project.json" not in files:
                continue
            path = Path(folder) / "project.json"
            try:
                manifest = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            if not isinstance(manifest, dict) or manifest.get("version") != 1 or not manifest.get("storageKey") or not manifest.get("board"):
                continue
            parts = path.relative_to(root).parts
            job = parts[2] if len(parts) > 3 else Path(folder).parent.name
            where = " · ".join(p.split(" ", 1)[-1] if p[:2].isdigit() else p for p in parts[:2]) if len(parts) > 3 else root.parent.name
            title = (manifest.get("config") or {}).get("brand") or job
            found.append({"path": str(path.resolve()), "title": title, "job": job, "where": where, "drive": root.parent.name})
    return found


def resolve(ident: str) -> Path:
    # Only listed projects can be served: recent ones, or ones found on the drives. The browser never supplies a path.
    for entry in read_recent() + discover():
        if project_id(Path(entry["path"])) == ident:
            return Path(entry["path"])
    raise StudioError("That project could not be found. Is its drive connected? Go back to the Storyboard home page.", 404)


def listing() -> dict:
    recent = {p["path"]: p for p in read_recent()}
    found = {p["path"]: p for p in discover()}
    projects = []
    for path in dict.fromkeys(list(recent) + list(found)):
        entry = {**found.get(path, {}), **{k: v for k, v in recent.get(path, {}).items() if k == "openedAt"}}
        entry.setdefault("title", recent.get(path, {}).get("title") or Path(path).parent.name)
        entry.update(id=project_id(Path(path)), exists=Path(path).is_file())
        entry.pop("path", None)
        projects.append(entry)
    # Recently opened first, newest at the top; then everything else alphabetically.
    projects.sort(key=lambda p: p["title"].lower())
    projects = sorted([p for p in projects if p.get("openedAt")], key=lambda p: p["openedAt"], reverse=True) + [p for p in projects if not p.get("openedAt")]
    return {"projects": projects, "roots": [str(r) for r in project_roots()]}


# ---- disk operations -------------------------------------------------------

def revision(path: Path) -> str:
    manifest = sb.read_json(path)
    digest = hashlib.sha256((path.read_bytes()))
    digest.update(sb.member(path.parent, manifest.get("board"), "board").read_bytes())
    return digest.hexdigest()[:16]


def archive_dir(path: Path, manifest) -> Path:
    if isinstance(manifest.get("earlier"), str) and manifest["earlier"]:
        return (path.parent / manifest["earlier"]).resolve()
    out = sb.output_path(path, manifest)
    return (out.parent if out else path.parent.parent) / "earlier"


def snapshot_dir(path: Path, manifest) -> Path:
    return archive_dir(path, manifest) / "autosave"


def snapshots(path: Path, manifest) -> list[Path]:
    folder = snapshot_dir(path, manifest)
    return sorted(folder.glob("*.json"), reverse=True) if folder.is_dir() else []


def take_snapshot(path: Path, manifest, *, force=False) -> Path | None:
    """Keep the board and soundtrack together, at most once per interval unless forced."""
    existing = snapshots(path, manifest)
    if not force and existing and time.time() - existing[0].stat().st_mtime < SNAPSHOT_EVERY:
        return None
    board_path = sb.member(path.parent, manifest.get("board"), "board")
    folder = snapshot_dir(path, manifest)
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / (datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S.%fZ") + ".json")
    snapshot = {"snapshotVersion": 1, "board": sb.read_json(board_path),
                "audio": manifest.get("audio"), "assets": manifest.get("assets", {})}
    sb.atomic_write(target, sb.json_text(snapshot).encode("utf-8"))
    for old in snapshots(path, manifest)[SNAPSHOTS_KEPT:]:
        old.unlink()
    return target


def read_autosave(path: Path):
    snapshot = sb.read_json(path)
    if isinstance(snapshot, dict) and snapshot.get("snapshotVersion") == 1:
        if "audio" not in snapshot:
            raise StudioError("That automatic save has no soundtrack state.")
        board, audio, assets = snapshot.get("board"), snapshot["audio"], snapshot.get("assets", sb.MISSING)
    else:
        # Earlier app versions saved only the board; keep the current music for those.
        board, audio, assets = snapshot, sb.MISSING, sb.MISSING
    sb.validate_board(board)
    return board, audio, assets


def store_media(root: Path, data, allowed, folder: str, label: str) -> str:
    payload, extension = sb.decode_data_url(data, allowed, label)
    relative = f"{folder}/{hashlib.sha256(payload).hexdigest()}{extension}"
    target = root / relative
    if not target.is_file():
        target.parent.mkdir(parents=True, exist_ok=True)
        sb.atomic_write(target, payload)
    return relative


def disk_board(root: Path, board) -> dict:
    """Turn a browser board (embedded images) into the on-disk form (image files)."""
    if not isinstance(board, dict):
        raise StudioError("The board must be a JSON object.")
    board = {key: value for key, value in board.items() if key not in sb.VOLATILE_KEYS}
    for shot in board.get("shots") or []:
        if isinstance(shot, dict) and shot.get("customImage"):
            shot.pop("customImagePath", None)
            shot["customImagePath"] = store_media(root, shot.pop("customImage"), sb.IMAGE_TYPES, "assets/imported", f"Panel {shot.get('id')} image")
    sb.validate_board(board)
    return board


def write_board(path: Path, manifest, board: dict):
    target = sb.member(path.parent, manifest.get("board"), "board")
    if target.read_text(encoding="utf-8") == sb.json_text(board):
        return False
    sb.load_project(path, manifest=manifest, board=board)
    take_snapshot(path, manifest)
    sb.atomic_write(target, sb.json_text(board).encode("utf-8"))
    return True


def save_board(path: Path, base: str, board) -> str:
    with WRITE_LOCK:
        if base != revision(path):
            raise StudioError("This board was changed in another window or by another tool, so this window has stopped saving. Use Export → Editable backup to keep what is on this page, then reload to see the latest.", 409)
        manifest = sb.read_json(path)
        write_board(path, manifest, disk_board(path.parent, board))
        return revision(path)


def write_manifest(path: Path, manifest):
    sb.load_project(path, manifest=manifest)
    sb.atomic_write(path, sb.json_text(manifest).encode("utf-8"))


def save_audio(path: Path, base: str, name: str | None, data: bytes | None) -> str:
    with WRITE_LOCK:
        if base != revision(path):
            raise StudioError("This board was changed in another window. Reload before changing the music.", 409)
        previous = sb.read_json(path)
        manifest = dict(previous)
        if data is None:
            manifest["audio"] = None
        else:
            name = (name or "Soundtrack").strip()[:200] or "Soundtrack"
            extension = Path(name).suffix.lower()
            if extension not in AUDIO_EXTENSIONS:
                raise StudioError("Choose an MP3, WAV, M4A, AAC, OGG, WEBM or FLAC file.")
            if not data or len(data) > 200 * 1024 * 1024:
                raise StudioError("Choose a soundtrack smaller than 200 MB.")
            relative = f"audio/imported/{hashlib.sha256(data).hexdigest()}{extension}"
            target = path.parent / relative
            if not target.is_file():
                sb.atomic_write(target, data)
            manifest["audio"] = {"path": relative, "name": name}
        sb.load_project(path, manifest=manifest)
        if manifest != previous:
            take_snapshot(path, previous)
            write_manifest(path, manifest)
        return revision(path)


def history(path: Path) -> dict:
    manifest = sb.read_json(path)
    entries = sb.read_versions(path.parent)
    output = sb.output_path(path, manifest)
    versions = []
    for index, entry in enumerate(entries):
        current = index == len(entries) - 1
        restorable = bool(output and output.is_file()) if current else bool(entry.get("file") and Path(entry["file"]).is_file())
        versions.append({"n": entry["n"], "label": entry.get("label", ""), "date": str(entry.get("builtAt", ""))[:16].replace("T", " "),
                         "panels": entry.get("panels"), "seconds": entry.get("seconds"), "current": current, "restorable": restorable})
    autosaves = []
    for snap in snapshots(path, manifest):
        try:
            board, _, _ = read_autosave(snap)
            panels = len(board["shots"])
        except sb.ProjectError:
            continue
        stamp = datetime.fromtimestamp(snap.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        autosaves.append({"name": snap.name, "date": stamp, "panels": panels})
    return {"versions": list(reversed(versions)), "autosaves": autosaves}


def save_version(path: Path, base: str, label: str) -> dict:
    label = (label or "").strip()[:120]
    if not label:
        raise StudioError("Give this version a short name, for example \"wreath added\".")
    with WRITE_LOCK:
        if base != revision(path):
            raise StudioError("This board was changed in another window. Reload before saving a version.", 409)
        out, _, report = sb.build(path, label=label)
        return {"report": report, "file": str(out), "rev": revision(path)}


def restore(path: Path, base: str, *, version=None, autosave=None) -> str:
    with WRITE_LOCK:
        if base != revision(path):
            raise StudioError("This board was changed in another window. Reload before restoring.", 409)
        previous = sb.read_json(path)
        manifest = dict(previous)
        if autosave is not None:
            snap = snapshot_dir(path, manifest) / Path(str(autosave)).name
            if not snap.is_file() or snap.suffix != ".json":
                raise StudioError("That automatic save no longer exists.", 404)
            board, audio, assets = read_autosave(snap)
            if audio is not sb.MISSING:
                manifest["audio"] = audio
            if assets is not sb.MISSING:
                manifest["assets"] = assets
        else:
            entries = sb.read_versions(path.parent)
            match = [i for i, e in enumerate(entries) if e["n"] == version]
            if not match:
                raise StudioError("That version is not in this project's list.", 404)
            index = match[0]
            source = sb.output_path(path, manifest) if index == len(entries) - 1 else Path(entries[index].get("file") or "")
            if not source or not source.is_file():
                raise StudioError("The file for that version is no longer on disk.", 404)
            board, assets, audio = sb.parse_snapshot(source)
            board = disk_board(path.parent, board)
            if assets is not None:
                manifest["assets"] = {key: store_media(path.parent, data, sb.IMAGE_TYPES, "assets/imported", f"asset {key}")
                                      for key, data in assets.items()}
            if audio is not sb.MISSING:
                if audio is None:
                    manifest["audio"] = None
                else:
                    manifest["audio"] = {"name": audio["name"], "path": store_media(path.parent, audio.get("data"), sb.AUDIO_TYPES, "audio/imported", "Soundtrack")}
        # Read and validate the target before a forced snapshot can prune the oldest save.
        sb.load_project(path, manifest=manifest, board=board)
        take_snapshot(path, previous, force=True)
        sb.atomic_write(sb.member(path.parent, manifest.get("board"), "board"), sb.json_text(board).encode("utf-8"))
        write_manifest(path, manifest)
        return revision(path)


def page(path: Path, ident: str) -> str:
    with WRITE_LOCK:
        path, manifest, board, assets, audio = sb.load_project(path)
        rev = revision(path)
    board["sourceRevision"] = sb.source_revision(board, assets, audio, manifest.get("config", {}))
    studio = {"api": f"/api/p/{ident}", "rev": rev, "home": "/", "project": manifest.get("config", {}).get("brand") or path.parent.name}
    return sb.render_page(manifest, board, assets, audio, None, studio=studio)


def pick_project() -> str | None:
    """Fallback for a storyboard outside the usual folders: choose the job folder; the project inside is found for you."""
    script = ('tell application (path to frontmost application as text) to POSIX path of '
              '(choose folder with prompt "Choose the job folder that holds the storyboard")')
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if result.returncode != 0 or not result.stdout.strip():
        return None
    folder = Path(result.stdout.strip())
    if (folder / "project.json").is_file():
        return str(folder / "project.json")
    for candidate in sorted(folder.rglob("project.json"), key=lambda p: len(p.parts)):
        if "earlier" not in candidate.relative_to(folder).parts and len(candidate.relative_to(folder).parts) <= 5:
            return str(candidate)
    raise StudioError("No storyboard was found in that folder.")


# ---- home page -------------------------------------------------------------

HOME = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Storyboard</title><style>
:root{--paper:#f4f1ea;--ink:#1d211c;--muted:#6b7064;--line:#d9d4c7;--card:#fbfaf6;--accent:#4d6952}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--paper:#171a16;--ink:#ecebe4;--muted:#a3a89b;--line:#33382f;--card:#20241f;--accent:#93ad8f}}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.5 -apple-system,BlinkMacSystemFont,"Helvetica Neue",sans-serif}
main{max-width:720px;margin:0 auto;padding:56px 16px}h1{font-size:13px;letter-spacing:3px;text-transform:uppercase;margin:0 0 28px}
.row{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:28px}button{font:inherit;cursor:pointer;border:1px solid var(--line);background:var(--card);color:var(--ink);padding:10px 16px}
button.primary{background:var(--accent);border-color:var(--accent);color:#fff}ul{list-style:none;margin:0;padding:0;border-top:1px solid var(--line)}
li{border-bottom:1px solid var(--line)}li a{display:flex;justify-content:space-between;gap:16px;padding:16px 4px;color:inherit;text-decoration:none}li a:hover strong{text-decoration:underline}
small{color:var(--muted)}.empty{color:var(--muted);padding:16px 4px}#msg{color:var(--muted);min-height:1.5em}
.lede{color:var(--muted);margin:-12px 0 24px}li a span{display:flex;flex-direction:column}li a .meta{text-align:right}.foot{margin-top:24px}.foot button{font-size:13px}
</style></head><body><main><h1>Storyboard</h1>
<p class="lede">Choose a storyboard. Every storyboard on your connected drives is listed here.</p>
<ul id="list"><li class="empty">Looking for storyboards…</li></ul>
<p id="msg"></p>
<div class="row foot"><button id="open">Open one from another folder…</button><button id="quit">Quit Storyboard</button></div></main>
<script>
const H={'X-Storyboard':'1'};const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
async function load(){const r=await fetch('/api/projects');const {projects}=await r.json();const list=document.getElementById('list');
const sub=p=>[p.job&&p.job!==p.title?p.job:'',p.where].filter(Boolean).join(' · ');
list.innerHTML=projects.length?projects.map(p=>p.exists?`<li><a href="/p/${p.id}"><span><strong>${esc(p.title)}</strong><small>${esc(sub(p))}</small></span><small class="meta">${p.openedAt?'Opened '+esc(p.openedAt.slice(0,10)):esc(p.drive||'')}</small></a></li>`:`<li><a aria-disabled="true"><span><strong>${esc(p.title)}</strong><small>Not found · is the drive connected?</small></span></a></li>`).join(''):'<li class="empty">No storyboards found. Connect the T7 drive, or use Open one from another folder.</li>';}
document.getElementById('open').onclick=async()=>{const m=document.getElementById('msg');m.textContent='Choose the job folder in the window that opened. The storyboard inside it is found for you.';
const r=await fetch('/api/pick',{method:'POST',headers:H});const d=await r.json();if(d.id)location.href='/p/'+d.id;else m.textContent=d.error||'';};
document.getElementById('quit').onclick=async()=>{await fetch('/api/quit',{method:'POST',headers:H}).catch(()=>{});document.querySelector('main').innerHTML='<h1>Storyboard</h1><p>Storyboard has closed. Open it again from the Storyboard app.</p>';};
load();
</script></body></html>"""


# ---- HTTP ------------------------------------------------------------------

class Handler(BaseHTTPRequestHandler):
    server_version = "RuaStoryboard/1"

    def log_message(self, fmt, *args):
        sys.stderr.write("%s %s\n" % (datetime.now().strftime("%H:%M:%S"), fmt % args))

    def send(self, status, body: bytes, kind="application/json; charset=utf-8"):
        self.send_response(status)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def json(self, status, value):
        self.send(status, json.dumps(value, ensure_ascii=False).encode("utf-8"))

    def body(self, limit=300 * 1024 * 1024) -> bytes:
        length = int(self.headers.get("Content-Length") or 0)
        if length > limit:
            raise StudioError("That upload is too large.", 413)
        return self.rfile.read(length)

    def guard(self):
        host = (self.headers.get("Host") or "").split(":")[0]
        if host not in ("127.0.0.1", "localhost"):
            raise StudioError("Storyboard only answers this computer.", 403)

    def guard_write(self):
        # Pages from other sites cannot send this header without a preflight this server never approves.
        if self.headers.get("X-Storyboard") != "1":
            raise StudioError("Missing Storyboard header.", 403)

    def route(self, method):
        self.guard()
        url = urllib.parse.urlsplit(self.path)
        parts = [urllib.parse.unquote(p) for p in url.path.split("/") if p]
        query = urllib.parse.parse_qs(url.query)
        if method != "GET":
            self.guard_write()
        if method == "GET" and parts == ["health"]:
            return self.send(200, b"ok", "text/plain")
        if method == "GET" and not parts:
            return self.send(200, HOME.encode("utf-8"), "text/html; charset=utf-8")
        if method == "GET" and parts == ["api", "projects"]:
            return self.json(200, listing())
        if method == "POST" and parts == ["api", "pick"]:
            try:
                chosen = pick_project()
            except StudioError as exc:
                return self.json(200, {"error": str(exc)})
            if not chosen:
                return self.json(200, {"cancelled": True})
            try:
                ident, _ = remember(chosen)
            except sb.ProjectError as exc:
                return self.json(200, {"error": f"That file is not a storyboard project: {exc}"})
            return self.json(200, {"id": ident})
        if method == "POST" and parts == ["api", "quit"]:
            self.json(200, {"ok": True})
            threading.Thread(target=self.server.shutdown, daemon=True).start()
            return None
        if method == "GET" and len(parts) == 2 and parts[0] == "p":
            path = resolve(parts[1])
            remember(path)
            return self.send(200, page(path, parts[1]).encode("utf-8"), "text/html; charset=utf-8")
        if len(parts) == 4 and parts[:2] == ["api", "p"]:
            path, action = resolve(parts[2]), parts[3]
            base = self.headers.get("X-Storyboard-Rev", "")
            if method == "GET" and action == "history":
                return self.json(200, history(path))
            if method == "PUT" and action == "board":
                return self.json(200, {"rev": save_board(path, base, json.loads(self.body() or b"null"))})
            if method == "PUT" and action == "audio":
                return self.json(200, {"rev": save_audio(path, base, (query.get("name") or [""])[0], self.body())})
            if method == "DELETE" and action == "audio":
                return self.json(200, {"rev": save_audio(path, base, None, None)})
            if method == "POST" and action == "version":
                return self.json(200, save_version(path, base, json.loads(self.body() or b"{}").get("label", "")))
            if method == "POST" and action == "restore":
                request = json.loads(self.body() or b"{}")
                return self.json(200, {"rev": restore(path, base, version=request.get("version"), autosave=request.get("autosave"))})
        raise StudioError("Not found.", 404)

    def handle_method(self, method):
        try:
            self.route(method)
        except StudioError as exc:
            self.json(exc.status, {"error": str(exc)})
        except sb.ProjectError as exc:
            self.json(400, {"error": str(exc)})
        except (ValueError, json.JSONDecodeError) as exc:
            self.json(400, {"error": f"Could not read that request: {exc}"})
        except Exception as exc:  # keep the server alive and tell the page
            self.json(500, {"error": f"Storyboard hit an unexpected problem: {exc}"})

    def do_GET(self):
        self.handle_method("GET")

    def do_POST(self):
        self.handle_method("POST")

    def do_PUT(self):
        self.handle_method("PUT")

    def do_DELETE(self):
        self.handle_method("DELETE")


def make_server(port=PORT) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((HOST, port), Handler)


def serve(port=PORT):
    server = make_server(port)
    print(f"Storyboard · http://{HOST}:{server.server_address[1]}", flush=True)
    try:
        server.serve_forever()
    finally:
        server.server_close()


def running(port=PORT) -> bool:
    try:
        with urllib.request.urlopen(f"http://{HOST}:{port}/health", timeout=1) as response:
            return response.read() == b"ok"
    except (urllib.error.URLError, OSError):
        return False


def open_studio(project=None, port=PORT, browser=True) -> str:
    """Start the studio in the background if needed and open the home page or a project."""
    url = f"http://{HOST}:{port}/"
    if project:
        ident, _ = remember(project)
        url += f"p/{ident}"
    if not running(port):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        log = open(CONFIG_DIR / "studio.log", "ab")
        subprocess.Popen([sys.executable, str(Path(__file__).resolve().parent / "storyboard.py"), "serve", "--port", str(port)],
                         stdout=log, stderr=log, stdin=subprocess.DEVNULL, start_new_session=True)
        for _ in range(50):
            if running(port):
                break
            time.sleep(0.1)
        else:
            raise sb.ProjectError(f"Storyboard did not start. See {CONFIG_DIR / 'studio.log'}.")
    if browser:
        subprocess.run(["open", url], check=False)
    return url
