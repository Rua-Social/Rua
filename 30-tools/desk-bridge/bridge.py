#!/usr/bin/env python3
"""Telegram seat for the Rua desk. Stdlib only."""

from __future__ import annotations

import json
import os
import fcntl
import queue
import re
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path

REPO = Path(os.environ.get("RUA_REPO", Path.home() / "Rua"))
SECRETS = Path.home() / ".grok" / "secrets" / "desk-bridge.env"
ELEVEN_SECRETS = Path.home() / ".grok" / "secrets" / "elevenlabs.env"
STATE_DIR = Path.home() / ".grok" / "desk-bridge"
SESSION_FILE = STATE_DIR / "session_id"
OFFSET_FILE = STATE_DIR / "offset"
LAST_ERROR_FILE = STATE_DIR / "last_error"
LAST_RUN_FILE = STATE_DIR / "last_run"
SESSION_META_FILE = STATE_DIR / "session_meta.json"
INBOX_FILE = STATE_DIR / "inbox.json"
OUTBOX_FILE = STATE_DIR / "outbox.json"
METRICS_FILE = STATE_DIR / "metrics.jsonl"
RUN_LOCK_FILE = STATE_DIR / "run.lock"
BRIDGE_LOG_FILE = STATE_DIR / "bridge.log"
BRIDGE_ERR_FILE = STATE_DIR / "bridge.err"
PLIST_PATH = Path.home() / "Library" / "LaunchAgents" / "com.rua.desk-bridge.plist"
LABEL = "com.rua.desk-bridge"
TG_LIMIT = 3900
TG_ACTION_TIMEOUT = 5
TG_SEND_TIMEOUT = 20
GROK_FIRST_EVENT_TIMEOUT = 60
GROK_IDLE_TIMEOUT = 120
GROK_TIMEOUT = 5 * 60
PHONE_REQUEST_TIMEOUT = 5 * 60
PHONE_EFFORT = "medium"
PHONE_MAX_TURNS = 10
SESSION_BYTES = 300_000
SESSION_PROMPT_TOKENS = 80_000
VOICE_MAX_BYTES = 20 * 1024 * 1024
SCRIBE_URL = "https://api.elevenlabs.io/v1/speech-to-text"
SCRIBE_MODEL = "scribe_v2"
PHONE_BUSY = "Grok is busy. Try again in a minute."
PHONE_TIMEOUT = "The desk timed out. Send it again or try a smaller ask."
PHONE_QUEUE = "Hold that. Still on the last one."
PHONE_GOOGLE = "Google isn't on this phone seat. Parked on the desk list."
OWNER_SETUP = "Set TELEGRAM_USER_ID before starting the desk."
STATE_LOCK = threading.RLock()
DELIVERY_LOCK = threading.Lock()
ACTIVE_PROCESS_LOCK = threading.RLock()
ACTIVE_GROK_PROCESS: subprocess.Popen | None = None
RUN_LOCK_FD: int | None = None
DESK_RULES = """You are the Rua desk conductor, reached by Telegram while the founder is on the go.
Read 20-studio/desk.md and AGENTS.md when the class of work needs them.
Name the class to yourself before loading doctrine. Do not invent work.
Do the work. Do not narrate loading, searching, or thinking.
Filter like a chief of staff. Escalate what would blindside the founder. Handle the ask. Park niceties.
The founder todo is 20-studio/todo.md. Read it when the ask needs the list. Do not write todos to lists.md, desk.md, client READMEs, or chat.
If the founder commits to a concrete action or reports one done, end with at most two lines:
LIST+ Do | one short action
LIST+ Done | what landed
Allowed headings: Do, Done, Moving, Blocked, Waiting on the desk.
Do and Done go to todo.md. Moving and Blocked stay on the desk diary.
Do not invent work. Do not edit those files yourself. The bridge writes them and hides the trailers.
LIST+ Done only on a typed ask. A voice note cannot close the list: say it landed and that a text closes it.
Telegram gets one short result: what happened, where it is, what they need.
No markdown tables. No class label in the chat. No process talk.
A line starting with Voice note: is a spoken message. Treat it as the ask.
Instagram and TikTok links in the message are intake, not decoration. Capture them, do the asked work, reply with what landed and where.
A client-facing document is written for the person who will sit with it and the person it is for. No internal paths, no steal-language, no studio process, no names they did not put in the room. References they sent appear as the thing itself: a still they recognise, then a link.
Do not ask them to sit down at the Mac unless the machine itself is the blocker.
This bridge sends text only. If work creates a file, name its repo path; do not claim it is attached.
Named clients: read 10-clients/<slug>/ first. That record is the pocket card. Todo is 20-studio/todo.md. Answer from those files.
Do not hunt Drive or Gmail for a fact the instance already has. lists.md is a diary. Do not brief a stale diary line over the instance or the founder.
If the founder corrects a desk fact, believe them and emit LIST+ Done or Moving.
Mail, calendar, and Drive live on dashboard Grok, not this phone process.
Do not use Mail.app, Calendar.app, icalBuddy, Chrome, or local mail CLIs as a stand-in.
Only if the files do not have the fact, and the ask is live mail, calendar, or Drive, reply with exactly this sentence and nothing else: Google isn't on this phone seat. Parked on the desk list. The bridge appends the pocket card and parks the miss. Do not lead with that sentence when the card or the todo already answers.
Hold a craft conversation if he asked for a hold. Do not write the deck or the concept list unless he asked for the file.
Do not spawn subagents or call another model from this phone seat.
If a tool fails auth or 401s, try it once, then answer with what you have. Do not burn the turn budget retrying.
A message that starts with park, backlog, or idea is a capture the bridge already handled. Do not re-park it.
"""


class GrokFirstEventTimeout(RuntimeError):
    """Grok produced no meaningful streamed event before the phone deadline."""


class GrokIdleTimeout(RuntimeError):
    """Grok stopped producing meaningful streamed events during a run."""


class GrokTotalTimeout(RuntimeError):
    """Grok exceeded the whole phone budget."""


class GrokProviderBusy(RuntimeError):
    """Grok reported provider capacity before doing any work."""


def load_env(path: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    if not path.is_file():
        return env
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :]
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        env[key.strip()] = value.strip().strip("'\"")
    return env


def load_secrets() -> dict[str, str]:
    env = load_env(SECRETS)
    eleven = load_env(ELEVEN_SECRETS)
    if "ELEVENLABS_API_KEY" in eleven:
        env["ELEVENLABS_API_KEY"] = eleven["ELEVENLABS_API_KEY"]
    return env


def configured_owner(env: dict[str, str]) -> str:
    owner = (env.get("TELEGRAM_USER_ID") or "").strip()
    if not owner:
        raise ValueError(OWNER_SETUP)
    if not owner.isdigit():
        raise ValueError("TELEGRAM_USER_ID must be a numeric Telegram user id.")
    return owner


def ensure_private_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(path, 0o700)


def atomic_write_text(path: Path, value: str, mode: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if mode is None:
        try:
            mode = path.stat().st_mode & 0o777
        except FileNotFoundError:
            mode = 0o600
    fd, raw_tmp = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    tmp = Path(raw_tmp)
    try:
        os.fchmod(fd, mode)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(value)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
        os.chmod(path, mode)
        parent_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(parent_fd)
        finally:
            os.close(parent_fd)
    except Exception:
        try:
            os.close(fd)
        except OSError:
            pass
        tmp.unlink(missing_ok=True)
        raise


def ensure_runtime_permissions() -> None:
    ensure_private_dir(STATE_DIR)
    ensure_private_dir(SECRETS.parent)
    for path in (SECRETS, ELEVEN_SECRETS):
        if path.is_file():
            os.chmod(path, 0o600)
    for path in STATE_DIR.iterdir():
        if path.is_file():
            os.chmod(path, 0o600)


def append_metric(event: dict) -> None:
    ensure_state()
    record = {"ts": round(time.time(), 3), **event}
    payload = (json.dumps(record, separators=(",", ":")) + "\n").encode()
    with STATE_LOCK:
        fd = os.open(METRICS_FILE, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
        try:
            os.fchmod(fd, 0o600)
            view = memoryview(payload)
            while view:
                view = view[os.write(fd, view) :]
        finally:
            os.close(fd)


def chunk_text(text: str, limit: int = TG_LIMIT) -> list[str]:
    text = (text or "").strip() or "(empty reply)"
    if len(text) <= limit:
        return [text]
    chunks: list[str] = []
    rest = text
    while rest:
        if len(rest) <= limit:
            chunks.append(rest)
            break
        cut = rest.rfind("\n", 0, limit)
        if cut < limit // 2:
            cut = rest.rfind(" ", 0, limit)
        if cut < limit // 2:
            cut = limit
        chunks.append(rest[:cut].rstrip())
        rest = rest[cut:].lstrip()
    return chunks


PHONE_FAIL = "Desk hit an error. /status"
STATUS_COMMANDS = {"/status", "/statua", "/stat", "status", "statua", "stat"}
BRIEF_COMMANDS = {"/brief", "brief"}
TODO_COMMANDS = {"/todo", "todo"}
CAPTURE_PREFIXES = (
    ("/park ", "park"),
    ("park this ", "park"),
    ("park ", "park"),
    ("/backlog ", "park"),
    ("backlog ", "park"),
    ("/idea ", "idea"),
    ("idea ", "idea"),
    ("/brainstorm ", "brainstorm"),
    ("brainstorm ", "brainstorm"),
)
CAPTURE_BARE = {
    "/park": "park",
    "park": "park",
    "/backlog": "park",
    "backlog": "park",
    "/idea": "idea",
    "idea": "idea",
    "/brainstorm": "brainstorm",
    "brainstorm": "brainstorm",
}
KNOWN_SLASH = {"/start", "/help", "/new", "/brief", "/todo", "/park", "/idea", "/backlog", "/brainstorm"} | {
    cmd for cmd in STATUS_COMMANDS if cmd.startswith("/")
}
CAPTURE_SLASH = {cmd for cmd in CAPTURE_BARE if cmd.startswith("/")}
IDEA_INLINE_LIMIT = 200


def is_status_command(text: str) -> bool:
    return text.strip().lower() in STATUS_COMMANDS


def is_brief_command(text: str) -> bool:
    return text.strip().lower() in BRIEF_COMMANDS


def is_todo_command(text: str) -> bool:
    return text.strip().lower() in TODO_COMMANDS


def spoken_text(text: str) -> str:
    raw = (text or "").strip()
    if raw.lower().startswith("voice note:"):
        raw = raw.split(":", 1)[1].strip()
    return raw


def parse_capture(text: str) -> tuple[str, str] | tuple[None, str]:
    raw = spoken_text(text)
    low = raw.lower()
    bare = CAPTURE_BARE.get(low)
    if bare:
        return bare, ""
    for prefix, kind in CAPTURE_PREFIXES:
        if low.startswith(prefix):
            return kind, raw[len(prefix) :].strip()
    return None, raw


def is_instant_command(text: str) -> bool:
    low = spoken_text(text).lower()
    if not low:
        return False
    if is_status_command(low) or is_brief_command(low) or is_todo_command(low):
        return True
    kind, _ = parse_capture(text)
    if kind in {"park", "idea"}:
        return True
    if low.startswith("/"):
        return True
    return False


def format_last_run(raw: str) -> str:
    if not raw:
        return "none"
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return raw
    if not isinstance(data, dict):
        return raw
    seconds = data.get("seconds")
    first = data.get("first_event_seconds")
    tools = data.get("tool_events")
    reset = data.get("reset_reason")
    bits: list[str] = []
    if isinstance(seconds, (int, float)):
        bits.append(f"{round(seconds)}s")
    if isinstance(first, (int, float)):
        bits.append(f"first {round(first)}s")
    if isinstance(tools, int):
        bits.append(f"{tools} tools")
    if reset:
        bits.append("reset")
    return ", ".join(bits) if bits else "ok"


def format_next_session(session_id: str) -> str:
    if not session_id:
        return "fresh"
    reason = session_reset_reason(session_id)
    if not reason:
        return "keep"
    return f"reset ({reason})"


def phone_text_from_stream(stdout: str) -> tuple[str, str]:
    """Last assistant text after the last tool call, plus session id."""
    last_block: list[str] = []
    all_text: list[str] = []
    session_id = ""
    saw_event = False
    saw_tool = False
    saw_end = False
    for raw in (stdout or "").splitlines():
        line = raw.strip()
        if not line or not line.startswith("{"):
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        kind = ev.get("type")
        if kind == "result":
            saw_event = True
            saw_end = True
            session_id = ev.get("session_id") or ev.get("sessionId") or session_id
            result = ev.get("result")
            if isinstance(result, str) and result.strip():
                last_block = [result]
                all_text.append(result)
        elif kind == "assistant":
            saw_event = True
            message = ev.get("message") or {}
            for block in message.get("content") or []:
                if isinstance(block, dict) and block.get("type") == "text":
                    bit = block.get("text") or ""
                    if bit:
                        last_block.append(bit)
                        all_text.append(bit)
        elif kind == "text":
            saw_event = True
            bit = ev.get("data") or ev.get("text") or ""
            if bit:
                last_block.append(bit)
                all_text.append(bit)
        elif kind == "tool_call":
            saw_event = True
            saw_tool = True
            last_block = []
        elif kind == "end":
            saw_event = True
            saw_end = True
            session_id = ev.get("sessionId") or session_id
        elif kind == "error":
            msg = ev.get("message") or "grok stream error"
            raise RuntimeError(msg)
    if not saw_event:
        try:
            data = json.loads(stdout)
        except json.JSONDecodeError:
            return ((stdout or "").strip(), "")
        if isinstance(data, dict):
            if data.get("type") == "error":
                raise RuntimeError(data.get("message") or "grok error")
            return ((data.get("text") or "").strip(), data.get("sessionId") or "")
    text = "".join(last_block).strip()
    if not text and not saw_tool:
        text = "".join(all_text).strip()
    if not saw_end and not text:
        raise RuntimeError("grok stream incomplete")
    return (text, session_id)


def session_history_path(session_id: str) -> Path | None:
    if not session_id:
        return None
    root = Path.home() / ".grok" / "sessions"
    if not root.is_dir():
        return None
    for child in root.iterdir():
        hist = child / session_id / "chat_history.jsonl"
        if hist.is_file():
            return hist
    return None


def session_is_heavy(session_id: str, limit: int = SESSION_BYTES) -> bool:
    hist = session_history_path(session_id)
    if hist is None:
        return False
    try:
        return hist.stat().st_size > limit
    except OSError:
        return False


def session_metadata(session_id: str) -> dict:
    metadata = {
        "session_id": session_id,
        "model": "",
        "effort": "",
        "prompt_tokens": 0,
        "history_bytes": 0,
    }
    hist = session_history_path(session_id)
    if hist is None:
        return metadata
    try:
        metadata["history_bytes"] = hist.stat().st_size
        with hist.open(encoding="utf-8") as handle:
            for raw in handle:
                try:
                    item = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                if item.get("type") != "assistant":
                    continue
                metadata["model"] = item.get("model_id") or metadata["model"]
                metadata["effort"] = item.get("reasoning_effort") or metadata["effort"]
    except OSError:
        return metadata
    saved = read_json(SESSION_META_FILE, {})
    if isinstance(saved, dict) and saved.get("session_id") == session_id:
        try:
            metadata["prompt_tokens"] = int(saved.get("prompt_tokens") or 0)
        except (TypeError, ValueError):
            metadata["prompt_tokens"] = 0
        # History is the authority for effective settings. The sidecar exists
        # mainly because token usage is not present in chat_history.jsonl.
        metadata["model"] = metadata["model"] or saved.get("model") or ""
        metadata["effort"] = metadata["effort"] or saved.get("effort") or ""
    return metadata


def session_reset_reason(session_id: str, limit: int = SESSION_BYTES) -> str:
    if not session_id:
        return ""
    saved = read_json(SESSION_META_FILE, {})
    if isinstance(saved, dict) and saved.get("engine") and saved.get("engine") != desk_engine():
        return "wrong-engine"
    if desk_engine() == "claude":
        if isinstance(saved, dict) and saved.get("effort") and saved.get("effort") != PHONE_EFFORT:
            return "wrong-effort"
        return ""
    hist = session_history_path(session_id)
    if hist is None:
        return "missing"
    meta = session_metadata(session_id)
    if meta["history_bytes"] > limit:
        return "history-bytes"
    # Prompt-token totals include the MCP catalog. A normal success is
    # already over 80k; resetting on that number makes every follow-up
    # forget. Byte cap and wrong-effort stay.
    if meta["effort"] and meta["effort"] != PHONE_EFFORT:
        return "wrong-effort"
    return ""


def should_drop_session(session_id: str, limit: int = SESSION_BYTES) -> bool:
    return bool(session_reset_reason(session_id, limit))


def ensure_state() -> None:
    ensure_private_dir(STATE_DIR)


def read_text(path: Path) -> str:
    try:
        return path.read_text().strip()
    except FileNotFoundError:
        return ""


def write_text(path: Path, value: str) -> None:
    ensure_state()
    atomic_write_text(path, value, mode=0o600)


def read_offset() -> int:
    raw = read_text(OFFSET_FILE)
    if not raw:
        return 0
    try:
        value = int(raw)
    except ValueError:
        write_text(LAST_ERROR_FILE, "invalid Telegram offset reset to 0")
        return 0
    return max(0, value)


def advance_offset(next_offset: int) -> int:
    """Durably move the Telegram high-water mark forward, never backward."""
    with STATE_LOCK:
        current = read_offset()
        value = max(current, int(next_offset))
        if value != current:
            write_text(OFFSET_FILE, str(value))
        return value


def read_json(path: Path, fallback):
    raw = read_text(path)
    if not raw:
        return fallback
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        write_text(LAST_ERROR_FILE, f"invalid state file: {path.name}")
        return fallback


def write_json(path: Path, value) -> None:
    write_text(path, json.dumps(value, separators=(",", ":")))


def grok_bin() -> str:
    found = shutil.which("grok")
    if found:
        return found
    fallback = Path.home() / ".grok" / "bin" / "grok"
    if fallback.is_file():
        return str(fallback)
    return "grok"


def claude_bin() -> str:
    found = shutil.which("claude")
    if found:
        return found
    fallback = Path.home() / ".local" / "bin" / "claude"
    if fallback.is_file():
        return str(fallback)
    return "claude"


def desk_engine() -> str:
    raw = (
        os.environ.get("DESK_ENGINE")
        or load_secrets().get("DESK_ENGINE")
        or "grok"
    )
    engine = raw.strip().lower()
    if engine in {"claude", "claude-code", "anthropic"}:
        return "claude"
    return "grok"


def desk_command(prompt: str, session_id: str) -> list[str]:
    if desk_engine() == "claude":
        cmd = [
            claude_bin(),
            "-p",
            prompt,
            "--output-format",
            "stream-json",
            "--verbose",
            "--dangerously-skip-permissions",
            "--effort",
            PHONE_EFFORT,
            "--append-system-prompt",
            DESK_RULES,
        ]
        if session_id:
            cmd.extend(["--resume", session_id])
        return cmd
    cmd = [
        grok_bin(),
        "-p",
        prompt,
        "--cwd",
        str(REPO),
        "--output-format",
        "streaming-json",
        "--yolo",
        "--no-subagents",
        "--no-plan",
        "--rules",
        DESK_RULES,
        "--no-auto-update",
        "--effort",
        PHONE_EFFORT,
        "--max-turns",
        str(PHONE_MAX_TURNS),
    ]
    if session_id:
        cmd.extend(["--resume", session_id])
    return cmd


def api(
    token: str,
    method: str,
    payload: dict | None = None,
    timeout: float = 70,
    deadline: float | None = None,
) -> dict:
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        body = fetch_url_bytes(req, timeout, deadline=deadline, max_bytes=2 * 1024 * 1024)
        return json.loads(body.decode())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")
        raise RuntimeError(f"telegram {method} HTTP {exc.code}: {body[:300]}") from exc
    except (TimeoutError, socket.timeout) as exc:
        raise RuntimeError(f"telegram {method} timed out") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"telegram {method} failed: {exc.reason}") from exc


def download_bytes(
    url: str,
    timeout: float = 60,
    deadline: float | None = None,
    max_bytes: int | None = None,
) -> bytes:
    req = urllib.request.Request(url)
    try:
        return fetch_url_bytes(req, timeout, deadline=deadline, max_bytes=max_bytes)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"download HTTP {exc.code}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        reason = getattr(exc, "reason", exc)
        raise RuntimeError(f"download failed: {reason}") from exc


def bounded_timeout(deadline: float | None, cap: float) -> float:
    if deadline is None:
        return cap
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise TimeoutError("phone request deadline")
    return max(0.05, min(cap, remaining))


def fetch_url_bytes(
    request: urllib.request.Request,
    timeout: float,
    deadline: float | None = None,
    max_bytes: int | None = None,
) -> bytes:
    """Read one HTTP response without letting trickle traffic beat a deadline."""

    def fetch() -> bytes:
        socket_timeout = bounded_timeout(deadline, timeout)
        with urllib.request.urlopen(request, timeout=socket_timeout) as response:
            limit = -1 if max_bytes is None else max_bytes + 1
            return response.read(limit)

    if deadline is None:
        data = fetch()
    else:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("phone request deadline")
        result: queue.Queue = queue.Queue(maxsize=1)

        def run_fetch() -> None:
            try:
                result.put((True, fetch()))
            except BaseException as exc:  # pass HTTP errors back to the caller
                result.put((False, exc))

        threading.Thread(target=run_fetch, daemon=True).start()
        try:
            ok, value = result.get(timeout=remaining)
        except queue.Empty as exc:
            raise TimeoutError("phone request deadline") from exc
        if not ok:
            raise value
        data = value

    if max_bytes is not None and len(data) > max_bytes:
        raise RuntimeError("HTTP response is too large")
    return data


def send(token: str, chat_id: int, text: str, timeout: float = TG_SEND_TIMEOUT) -> None:
    for part in chunk_text(text):
        api(token, "sendMessage", {"chat_id": chat_id, "text": part}, timeout=timeout)


def safe_send(
    token: str, chat_id: int, text: str, timeout: float = TG_ACTION_TIMEOUT
) -> bool:
    try:
        send(token, chat_id, text, timeout=timeout)
        return True
    except RuntimeError as exc:
        write_text(LAST_ERROR_FILE, str(exc))
        return False


def enqueue_outbox(source_id: int | str, chat_id: int, text: str) -> None:
    item_id = str(source_id)
    with STATE_LOCK:
        current = read_json(OUTBOX_FILE, [])
        if not isinstance(current, list):
            current = []
        if any(str(item.get("id")) == item_id for item in current if isinstance(item, dict)):
            return
        current.append(
            {
                "id": item_id,
                "chat_id": int(chat_id),
                "parts": chunk_text(text),
                "next_part": 0,
                "created_at": round(time.time(), 3),
            }
        )
        write_json(OUTBOX_FILE, current)


def inbox_items() -> list[dict]:
    current = read_json(INBOX_FILE, [])
    if not isinstance(current, list):
        return []
    return [item for item in current if isinstance(item, dict)]


def persist_inbox_job(job: dict) -> bool:
    with STATE_LOCK:
        current = inbox_items()
        item_id = str(job["id"])
        if any(str(item.get("id")) == item_id for item in current):
            return False
        current.append({**job, "status": "queued"})
        write_json(INBOX_FILE, current)
        return True


def mark_inbox_job(source_id: int | str, status: str) -> None:
    with STATE_LOCK:
        current = inbox_items()
        for item in current:
            if str(item.get("id")) == str(source_id):
                item["status"] = status
                write_json(INBOX_FILE, current)
                return


def remove_inbox_job(source_id: int | str) -> None:
    with STATE_LOCK:
        current = inbox_items()
        remaining = [item for item in current if str(item.get("id")) != str(source_id)]
        write_json(INBOX_FILE, remaining)


def pending_outbox_count() -> int:
    current = read_json(OUTBOX_FILE, [])
    return len(current) if isinstance(current, list) else 0


def deliver_outbox(token: str) -> bool:
    # Only one sender claims the outbox, but state writes remain available to
    # the poller and worker while Telegram is slow or unreachable.
    with DELIVERY_LOCK:
        while True:
            with STATE_LOCK:
                current = read_json(OUTBOX_FILE, [])
                if not isinstance(current, list):
                    current = []
                while current and not isinstance(current[0], dict):
                    current.pop(0)
                    write_json(OUTBOX_FILE, current)
                if not current:
                    return True
                item = dict(current[0])
                parts = item.get("parts") or []
                try:
                    index = int(item.get("next_part") or 0)
                    chat_id = int(item["chat_id"])
                except (KeyError, TypeError, ValueError) as exc:
                    write_text(LAST_ERROR_FILE, f"outbox delivery: {exc}")
                    return False
                if index >= len(parts):
                    current.pop(0)
                    write_json(OUTBOX_FILE, current)
                    append_metric({"stage": "delivery", "outcome": "ok"})
                    continue
                part = str(parts[index])

            try:
                api(
                    token,
                    "sendMessage",
                    {"chat_id": chat_id, "text": part},
                    timeout=TG_SEND_TIMEOUT,
                )
            except RuntimeError as exc:
                write_text(LAST_ERROR_FILE, f"outbox delivery: {exc}")
                append_metric(
                    {
                        "stage": "delivery",
                        "outcome": "pending",
                        "pending": pending_outbox_count(),
                    }
                )
                return False

            with STATE_LOCK:
                current = read_json(OUTBOX_FILE, [])
                if not isinstance(current, list) or not current:
                    continue
                head = current[0]
                if not isinstance(head, dict) or str(head.get("id")) != str(item.get("id")):
                    continue
                if int(head.get("next_part") or 0) == index:
                    head["next_part"] = index + 1
                    write_json(OUTBOX_FILE, current)


class OutboxDeliverer:
    """One retrying sender so Telegram I/O never blocks pickup or Grok work."""

    def __init__(self, token: str):
        self.token = token
        self.wake = threading.Event()
        self.worker = threading.Thread(target=self._run, daemon=True)

    def start(self) -> None:
        self.worker.start()

    def notify(self) -> None:
        self.wake.set()

    def _run(self) -> None:
        while True:
            self.wake.wait()
            self.wake.clear()
            try:
                while pending_outbox_count():
                    if deliver_outbox(self.token):
                        break
                    # Retry transient delivery failures without holding up the
                    # poller or the sole work queue.
                    self.wake.wait(5)
                    self.wake.clear()
            except Exception as exc:
                try:
                    write_text(LAST_ERROR_FILE, f"delivery worker: {exc}")
                except Exception:
                    pass
                self.wake.wait(5)
                self.wake.set()


def react(
    token: str, chat_id: int, message_id: int | None, emoji: str = "👀"
) -> bool:
    if not message_id:
        return False
    try:
        api(
            token,
            "setMessageReaction",
            {
                "chat_id": chat_id,
                "message_id": message_id,
                "reaction": [{"type": "emoji", "emoji": emoji}],
            },
            timeout=TG_ACTION_TIMEOUT,
        )
        return True
    except RuntimeError:
        return False


def typing_pulse(token: str, chat_id: int, stop: threading.Event) -> None:
    while not stop.is_set():
        try:
            api(
                token,
                "sendChatAction",
                {"chat_id": chat_id, "action": "typing"},
                timeout=TG_ACTION_TIMEOUT,
            )
        except (RuntimeError, TimeoutError):
            return
        if stop.wait(4):
            return


def feedback_pulse(
    token: str, chat_id: int, message_id: int | None, stop: threading.Event
) -> None:
    started = time.monotonic()
    reaction_ok = react(token, chat_id, message_id)
    typing_ok = False
    if not stop.is_set():
        try:
            api(
                token,
                "sendChatAction",
                {"chat_id": chat_id, "action": "typing"},
                timeout=TG_ACTION_TIMEOUT,
            )
            typing_ok = True
        except (RuntimeError, TimeoutError):
            typing_ok = False
    append_metric(
        {
            "stage": "acknowledgement",
            "outcome": "ok" if reaction_ok or typing_ok else "missed",
            "reaction": reaction_ok,
            "typing": typing_ok,
            "seconds": round(time.monotonic() - started, 3),
        }
    )
    if not typing_ok:
        return
    while not stop.wait(4):
        try:
            api(
                token,
                "sendChatAction",
                {"chat_id": chat_id, "action": "typing"},
                timeout=TG_ACTION_TIMEOUT,
            )
        except (RuntimeError, TimeoutError):
            return


def help_text() -> str:
    return (
        "Rua desk on Telegram.\n"
        "/help — this\n"
        "/new — drop the chat and the queue. Does not restart the Mac.\n"
        "/status — desk state\n"
        "/brief — walking brief from the todo\n"
        "/todo — open actions only\n"
        "/park — drop a line on the list\n"
        "/idea — send a thought to the desk\n"
        "Text or a voice note goes to the desk.\n"
        "This desk is yours. Another Grok window is not a second owner."
    )


LIST_WRITE_RE = re.compile(
    r"^LIST\+\s+(.+?)\s*\|\s*(.+)$",
    re.I,
)
LIST_WRITE_HEADINGS = {
    "do": "Do",
    "done": "Done",
    "moving": "Moving",
    "blocked": "Blocked",
    "waiting": "Waiting on the desk",
    "waiting on": "Waiting on the desk",
    "waiting on the desk": "Waiting on the desk",
}
DESK_LIST_HEADINGS = frozenset({"Blocked", "Moving", "Done"})
FOUNDER_LIST_HEADINGS = frozenset({"Do", "Ideas", "Planned", "Waiting on the desk"})
MAX_LIST_WRITES = 2
GATE_RE = re.compile(
    r"\b(deposit|send|chase|unpaid|lock|due|today|invoice|pack|follow-?up|reply|dated|gate)\b",
    re.I,
)
NEEDS_HIM_RE = re.compile(
    r"\b(chase|send|reply|decide|deposit|pack|follow-?up|founder)\b",
    re.I,
)
CLIENT_MOVE_RE = re.compile(
    r"\b(not sent|unpaid|deposit|send|draft|waiting|with them)\b",
    re.I,
)
TODO_LINE_RE = re.compile(
    r"^- (\d{4}-\d{2}-\d{2})(?: (STALE))? (.+)$"
)
TODO_JUNK_RE = re.compile(
    r"phone cannot|gmail|calendar|drive|kimi|launchd|desk-bridge|"
    r"cos slice|getupdates|mail\.app|lists\.md",
    re.I,
)
TODO_OPEN_CAP = 7
TODO_STALE_DAYS = 7
TODO_ACK_DUP = "Already on the list."
TODO_ACK_FULL = "Todo is full. Close one."
TODO_ACK_JUNK = "Not a todo line."
TODO_ACK_VOICE_DONE = "Voice can't close the list. Text it if it landed."
TODO_HEADER = (
    "# Todo\n\n"
    "Open actions only. Not a diary. Not ideas. Not desk incidents.\n"
    "Any seat that needs the list reads this file. Closed lines live in\n"
    "`20-studio/todo-done.md`. Cap 7. After 7 days a line is marked STALE.\n"
    "Do not write todos anywhere else. Skill: `00-system/skills/rua-todo/`.\n\n"
    "## Open\n"
)
TODO_DONE_HEADER = (
    "# Todo done\n\n"
    "Closed founder actions. Not the open list. Do not brief from here.\n"
)


def section_bullets(text: str, heading: str, limit: int = 2) -> list[str]:
    marker = f"### {heading}\n"
    start = text.find(marker)
    if start < 0:
        return []
    rest = text[start + len(marker) :]
    nxt = rest.find("\n### ")
    if nxt < 0:
        nxt = rest.find("\n## ")
    if nxt >= 0:
        rest = rest[:nxt]
    found: list[str] = []
    skip_needles = (
        "cannot see Gmail",
        "Phone hung",
        "CoS slice",
        "phone Google request",
    )
    for line in rest.splitlines():
        line = line.strip()
        if not line.startswith("- "):
            continue
        bullet = line[2:].strip().replace("**", "")
        if any(needle in bullet for needle in skip_needles):
            continue
        if len(bullet) > 140:
            cut = bullet.rfind(" ", 0, 140)
            bullet = bullet[: cut if cut > 40 else 140].rstrip() + "…"
        found.append(bullet)
        if len(found) >= limit:
            break
    return found


def client_cards(root: Path | None = None, limit: int = 3) -> list[str]:
    base = root or (REPO / "10-clients")
    if not base.is_dir():
        return []
    cards: list[str] = []
    for child in sorted(base.iterdir()):
        if not child.is_dir() or child.name.startswith("."):
            continue
        readme = child / "README.md"
        if not readme.is_file():
            continue
        try:
            body = readme.read_text(encoding="utf-8")[:4000]
        except OSError:
            continue
        status = ""
        last = ""
        for line in body.splitlines():
            if line.startswith("**Status:**"):
                status = line.split(":**", 1)[-1].strip().strip("*").strip()
            if "Latest client document:" in line:
                last = line.split(":", 1)[-1].strip().strip("`")
        name = child.name.replace("-", " ")
        bit = name
        if status:
            bit += f": {status}"
        if last:
            bit += f". Last file {last}"
        if bit != name:
            cards.append(bit)
        if len(cards) >= limit:
            break
    return cards


def _score_gate(bullet: str) -> int:
    score = 0
    if GATE_RE.search(bullet):
        score += 3
    if re.search(r"\b\d{1,2}\s+[A-Za-z]{3,}\b", bullet):
        score += 1
    return score


def _score_needs_him(bullet: str) -> int:
    if NEEDS_HIM_RE.search(bullet):
        return _score_gate(bullet) + 2
    return _score_gate(bullet)


def _score_client(card: str) -> int:
    score = 0
    if CLIENT_MOVE_RE.search(card):
        score += 3
    low = card.lower()
    if "not sent" in low or "unpaid" in low:
        score += 2
    if "delivered" in low:
        score -= 2
    return score


def _pick_ranked(items: list[str], score_fn) -> str | None:
    if not items:
        return None
    ranked = sorted(
        ((score_fn(item), index, item) for index, item in enumerate(items)),
        key=lambda row: (-row[0], row[1]),
    )
    return ranked[0][2]


def todo_file(path: Path | None = None) -> Path:
    return path or (REPO / "20-studio" / "todo.md")


def todo_done_file(path: Path | None = None) -> Path:
    return path or (REPO / "20-studio" / "todo-done.md")


def parse_todo_items(text: str) -> list[tuple[date, bool, str]]:
    marker = "## Open\n"
    start = text.find(marker)
    body = text[start + len(marker) :] if start >= 0 else text
    nxt = body.find("\n## ")
    if nxt >= 0:
        body = body[:nxt]
    items: list[tuple[date, bool, str]] = []
    for line in body.splitlines():
        match = TODO_LINE_RE.match(line.strip())
        if not match:
            continue
        try:
            added = datetime.strptime(match.group(1), "%Y-%m-%d").date()
        except ValueError:
            continue
        stale = match.group(2) == "STALE"
        items.append((added, stale, match.group(3).strip()))
    return items


def format_todo_line(added: date, stale: bool, text: str) -> str:
    mark = "STALE " if stale else ""
    return f"- {added.isoformat()} {mark}{text}".rstrip()


def write_todo_open(
    items: list[tuple[date, bool, str]], path: Path | None = None
) -> None:
    body = TODO_HEADER
    if items:
        body += "\n" + "\n".join(
            format_todo_line(added, stale, text) for added, stale, text in items
        ) + "\n"
    atomic_write_text(todo_file(path), body)


def load_todo(path: Path | None = None) -> list[tuple[date, bool, str]]:
    target = todo_file(path)
    try:
        text = target.read_text(encoding="utf-8")
    except FileNotFoundError:
        return []
    return parse_todo_items(text)


def regulate_todo(
    path: Path | None = None, today: date | None = None
) -> list[tuple[date, bool, str]]:
    now = today or date.today()
    cutoff = now - timedelta(days=TODO_STALE_DAYS)
    items = []
    changed = False
    for added, stale, text in load_todo(path):
        should_stale = added <= cutoff
        if should_stale and not stale:
            changed = True
        items.append((added, should_stale, text))
    if changed or not todo_file(path).is_file():
        write_todo_open(items, path)
    return items


def is_todo_junk(text: str) -> bool:
    return bool(TODO_JUNK_RE.search(text or ""))


def todo_has(items: list[tuple[date, bool, str]], text: str) -> bool:
    needle = normalize_list_bullet(text)
    if not needle:
        return False
    return any(
        needle == normalize_list_bullet(existing)
        or needle in normalize_list_bullet(existing)
        or normalize_list_bullet(existing) in needle
        for _, _, existing in items
    )


def add_open_todo(
    text: str,
    path: Path | None = None,
    today: date | None = None,
) -> str:
    """Empty string when the line landed, else the refusal reason."""
    body = (text or "").strip()
    if not body or is_todo_junk(body):
        return "junk"
    items = regulate_todo(path, today=today)
    if todo_has(items, body):
        return "dup"
    if len(items) >= TODO_OPEN_CAP:
        return "full"
    items.append((today or date.today(), False, body))
    write_todo_open(items, path)
    return ""


def close_todo(
    text: str,
    path: Path | None = None,
    done_path: Path | None = None,
    today: date | None = None,
) -> bool:
    body = (text or "").strip()
    if not body or is_todo_junk(body):
        return False
    items = regulate_todo(path, today=today)
    kept: list[tuple[date, bool, str]] = []
    closed: tuple[date, bool, str] | None = None
    for item in items:
        if closed is None and (
            todo_has([item], body) or todo_has([(item[0], item[1], body)], item[2])
        ):
            closed = item
            continue
        kept.append(item)
    if closed is None:
        closed = (today or date.today(), False, body)
    else:
        write_todo_open(kept, path)
    dest = todo_done_file(done_path)
    try:
        current = dest.read_text(encoding="utf-8")
    except FileNotFoundError:
        current = TODO_DONE_HEADER + "\n"
    if current.strip() == TODO_DONE_HEADER.strip():
        current = TODO_DONE_HEADER + "\n"
    stamp = (today or date.today()).isoformat()
    line = f"- {closed[0].isoformat()} → {stamp} {closed[2]}\n"
    if normalize_list_bullet(closed[2]) in normalize_list_bullet(current):
        return True
    if not current.endswith("\n"):
        current += "\n"
    atomic_write_text(dest, current + line)
    return True


def format_open_todo(path: Path | None = None, today: date | None = None) -> str:
    items = regulate_todo(path, today=today)
    lines: list[str] = []
    if len(items) >= TODO_OPEN_CAP:
        lines.append("Todo is full. Close one.")
    if not items:
        return "Nothing open."
    for added, stale, text in items:
        lines.append(format_todo_line(added, stale, text))
    return "\n".join(lines)


def pocket_brief(
    clients_root: Path | None = None,
    todo_path: Path | None = None,
) -> str:
    items = regulate_todo(todo_path)
    lines: list[str] = []
    if len(items) >= TODO_OPEN_CAP:
        lines.append("Todo is full. Close one.")
    stale = [item for item in items if item[1]]
    fresh = [item for item in items if not item[1]]
    if stale:
        lines.append(f"STALE: {stale[0][2]}")
    picked = _pick_ranked([item[2] for item in fresh], _score_gate)
    if picked:
        lines.append(f"Do: {picked}")
    elif fresh:
        lines.append(f"Do: {fresh[0][2]}")
    card = _pick_ranked(client_cards(clients_root, limit=8), _score_client)
    if card:
        lines.append(card)
    return "\n".join(lines[:5])


def google_miss_finish(text: str) -> str:
    """A real Google miss comes back from Grok as the EXPERIENCE sentence.
    The bridge parks it once and appends the pocket brief. The sentence
    quoted inside a longer reply is not a miss."""
    if not text.strip().startswith(PHONE_GOOGLE):
        return text
    park_google_ask("")
    brief = pocket_brief()
    return f"{text}\n\n{brief}" if brief else text


def ensure_list_heading(text: str, heading: str) -> str:
    marker = f"### {heading}\n"
    if marker in text:
        return text
    parent = "## Desk\n" if heading in DESK_LIST_HEADINGS else "## Founder\n"
    if parent in text:
        return text.replace(parent, parent + "\n" + marker + "\n", 1)
    other = "## Founder\n" if parent == "## Desk\n" else "## Desk\n"
    if other in text and parent == "## Desk\n":
        return text.replace(other, parent + "\n" + marker + "\n" + other, 1)
    return text.rstrip() + f"\n\n{parent}\n\n{marker}\n"


def normalize_list_bullet(text: str) -> str:
    cleaned = text.strip().lower()
    cleaned = re.sub(r"^\d{1,2}\s+[a-z]{3,}\s+[—-]\s+", "", cleaned)
    return re.sub(r"\s+", " ", cleaned)


def heading_has_bullet(text: str, heading: str, bullet: str) -> bool:
    needle = normalize_list_bullet(bullet)
    if not needle:
        return False
    return any(
        needle == normalize_list_bullet(existing)
        or needle in normalize_list_bullet(existing)
        or normalize_list_bullet(existing) in needle
        for existing in section_bullets(text, heading, 40)
    )


def extract_list_writes(text: str) -> tuple[str, list[tuple[str, str]]]:
    kept: list[str] = []
    writes: list[tuple[str, str]] = []
    for line in (text or "").splitlines():
        match = LIST_WRITE_RE.match(line.strip())
        if not match:
            kept.append(line)
            continue
        heading = LIST_WRITE_HEADINGS.get(match.group(1).strip().lower())
        body = match.group(2).strip()
        if heading and body and len(writes) < MAX_LIST_WRITES:
            writes.append((heading, body))
    cleaned = "\n".join(kept).strip()
    return cleaned, writes


TODO_ACKS = {
    "dup": TODO_ACK_DUP,
    "full": TODO_ACK_FULL,
    "junk": TODO_ACK_JUNK,
}


def persist_desk_writes(
    text: str,
    path: Path | None = None,
    todo_path: Path | None = None,
    done_path: Path | None = None,
    allow_done: bool = True,
) -> str:
    cleaned, writes = extract_list_writes(text)
    if not writes:
        return cleaned or text
    target = path or (REPO / "20-studio" / "lists.md")
    try:
        current = target.read_text(encoding="utf-8")
    except FileNotFoundError:
        current = "# Lists\n\n"
    applied: list[str] = []
    acks: list[str] = []
    for heading, body in writes:
        if heading == "Do":
            reason = add_open_todo(body, todo_path)
            if reason:
                acks.append(TODO_ACKS[reason])
            else:
                applied.append(heading)
            continue
        if heading == "Done":
            if not allow_done:
                acks.append(TODO_ACK_VOICE_DONE)
                continue
            if close_todo(body, todo_path, done_path):
                applied.append(heading)
            else:
                acks.append(TODO_ACK_JUNK)
            continue
        if heading_has_bullet(current, heading, body):
            continue
        append_list_bullet(heading, body, target)
        try:
            current = target.read_text(encoding="utf-8")
        except FileNotFoundError:
            current = ""
        applied.append(heading)
    if applied:
        append_metric(
            {
                "stage": "list-write",
                "outcome": "ok",
                "count": len(applied),
                "headings": applied,
            }
        )
    reply = cleaned or "(no text)"
    if acks:
        reply += "\n\n" + "\n".join(dict.fromkeys(acks))
    return reply


def append_list_bullet(
    heading: str, bullet: str, path: Path | None = None
) -> None:
    target = path or (REPO / "20-studio" / "lists.md")
    try:
        text = target.read_text(encoding="utf-8")
    except FileNotFoundError:
        text = "# Lists\n\n## Founder\n\n"
    text = ensure_list_heading(text, heading)
    stamp = time.strftime("%d %b").lstrip("0")
    line = f"- {stamp} — {bullet}\n"
    marker = f"### {heading}\n"
    text = text.replace(marker, marker + "\n" + line, 1)
    atomic_write_text(target, text)


def idea_filename(when: float | None = None) -> str:
    stamp = time.strftime("%Y-%m-%d-%H%M", time.localtime(when or time.time()))
    return f"{stamp}.md"


def capture_park(body: str, lists_path: Path | None = None) -> str:
    if not body:
        return "Say what to park."
    append_list_bullet("Ideas", body, lists_path)
    return "On the list."


def capture_idea(
    body: str,
    lists_path: Path | None = None,
    ideas_dir: Path | None = None,
) -> str:
    if not body:
        return "Say the idea."
    dest = ideas_dir or (REPO / "20-studio" / "ideas")
    if len(body) <= IDEA_INLINE_LIMIT:
        append_list_bullet("Ideas", body, lists_path)
        return "Sent to the desk."
    dest.mkdir(parents=True, exist_ok=True)
    name = idea_filename()
    path = dest / name
    suffix = 2
    while path.exists():
        path = dest / f"{name[:-3]}-{suffix}.md"
        suffix += 1
    atomic_write_text(
        path,
        f"# Idea\n\n{time.strftime('%d %b %Y %H:%M')}\n\n{body}\n",
        mode=0o600,
    )
    rel = f"20-studio/ideas/{name}"
    append_list_bullet("Ideas", f"brainstorm {rel}", lists_path)
    return f"Sent to the desk. {rel}"


def park_google_ask(prompt: str, path: Path | None = None) -> bool:
    del prompt  # Never persist phone message contents in the desk list.
    target = path or (REPO / "20-studio" / "lists.md")
    marker = "phone Google request blocked by desk-bridge"
    try:
        text = target.read_text(encoding="utf-8")
    except FileNotFoundError:
        return False
    if marker in text:
        return False
    heading = "### Blocked\n"
    if heading not in text:
        return False
    stamp = time.strftime("%d %b").lstrip("0")
    line = f"\n- {stamp} — {marker}. Gmail, Calendar, and Drive remain dashboard-only."
    updated = text.replace(heading, heading + line + "\n", 1)
    atomic_write_text(target, updated)
    return True


def grok_env() -> dict[str, str]:
    env = os.environ.copy()
    home = str(Path.home())
    path_bits = [
        f"{home}/.grok/bin",
        f"{home}/.local/bin",
        "/opt/homebrew/bin",
        "/usr/local/bin",
        env.get("PATH", ""),
    ]
    env["PATH"] = ":".join(path_bits)
    env["GROK_DISABLE_AUTOUPDATER"] = "1"
    # Launchd does not inherit the interactive shell. Phone grok still
    # needs the same MCP keys the dashboard already uses.
    secrets_dir = SECRETS.parent
    for name in ("xpoz.env", "moonshot.env"):
        for key, value in load_env(secrets_dir / name).items():
            if key and value and not env.get(key):
                env[key] = value
    return env


def _pipe_reader(pipe, name: str, output: queue.Queue) -> None:
    try:
        if pipe is not None:
            while True:
                line = pipe.readline()
                if line == "":
                    break
                output.put((name, line))
    finally:
        output.put((f"{name}_eof", ""))


def _event_kind(event: dict) -> str:
    kind = str(event.get("type") or "")
    if kind:
        return kind.lower()
    update = ((event.get("params") or {}).get("update") or {})
    return str(update.get("type") or update.get("sessionUpdate") or "").lower()


def _event_text(event: dict) -> str:
    values = [
        event.get("message"),
        event.get("reason"),
        event.get("error"),
        ((event.get("params") or {}).get("update") or {}).get("reason"),
    ]
    return " ".join(str(value) for value in values if value).lower()


def _usage_value(data: dict, *names: str) -> int:
    for name in names:
        value = data.get(name)
        if value is None:
            continue
        try:
            return int(value)
        except (TypeError, ValueError):
            continue
    return 0


def _update_stream_meta(event: dict, meta: dict) -> None:
    kind = _event_kind(event)
    if (
        kind in {"tool_call", "tool_call_update", "tool_started"}
        or "toolcall" in kind
    ):
        meta["tool_events"] += 1
    update = ((event.get("params") or {}).get("update") or {})
    for container in (
        event,
        event.get("data") or {},
        event.get("usage") or {},
        update,
        update.get("usage") or {} if isinstance(update, dict) else {},
    ):
        if not isinstance(container, dict):
            continue
        meta["model"] = (
            container.get("model_id")
            or container.get("model")
            or meta.get("model", "")
        )
        meta["effort"] = (
            container.get("reasoning_effort")
            or container.get("effort")
            or meta.get("effort", "")
        )
        reported_prompt = _usage_value(container, "prompt_tokens", "promptTokens")
        uncached_input = _usage_value(container, "input_tokens", "inputTokens")
        cached = _usage_value(
            container,
            "cache_read_input_tokens",
            "cacheReadInputTokens",
            "cached_prompt_tokens",
            "cachedPromptTokens",
        )
        cache_write = _usage_value(
            container,
            "cache_creation_input_tokens",
            "cacheCreationInputTokens",
        )
        effective_prompt = reported_prompt or (uncached_input + cached + cache_write)
        if effective_prompt:
            meta["prompt_tokens"] = max(
                meta["prompt_tokens"], effective_prompt
            )
        output = _usage_value(
            container, "completion_tokens", "output_tokens", "outputTokens", "completionTokens"
        )
        if output:
            meta["output_tokens"] = max(meta["output_tokens"], output)
        reasoning = _usage_value(container, "reasoning_tokens", "reasoningTokens")
        if reasoning:
            meta["reasoning_tokens"] = max(meta["reasoning_tokens"], reasoning)


def _meaningful_stream_event(event: dict) -> bool:
    kind = _event_kind(event)
    return bool(
        kind
        and (
            kind in {
                "text",
                "tool_call",
                "tool_call_update",
                "end",
                "error",
                "usage",
                "thinking",
                "thought",
                "reasoning",
                "retrying",
                "result",
                "assistant",
                "system",
            }
            or "toolcall" in kind
            or "assistant" in kind
            or "agent_message" in kind
            or "agent_thought" in kind
            or "turn_completed" in kind
            or "usage" in kind
        )
    )


def _max_turns_event(event: dict) -> bool:
    kind = _event_kind(event)
    if kind not in {"turn_ended", "turnended"} and "turn_ended" not in kind:
        return False
    contexts = [
        event.get("cancellation_context") or {},
        ((event.get("params") or {}).get("update") or {}).get("cancellation_context")
        or {},
    ]
    return any(
        isinstance(ctx, dict) and ctx.get("reason") == "max_turns_reached"
        for ctx in contexts
    )


def _provider_busy_event(event: dict) -> bool:
    text = _event_text(event)
    return any(
        phrase in text
        for phrase in (
            "currently at capacity",
            "provider capacity",
            "service unavailable",
            "rate limit",
            "overloaded",
            "usage limit",
            "out of extra usage",
            "credit balance",
        )
    )


def terminate_process(proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        return
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except (AttributeError, OSError, ProcessLookupError):
        try:
            proc.terminate()
        except (AttributeError, OSError):
            return
    try:
        proc.wait(timeout=2)
        return
    except (subprocess.TimeoutExpired, AttributeError):
        pass
    # A provider can ignore TERM.  Escalate so a timed-out --yolo child
    # cannot continue doing work after the bridge has abandoned the request.
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except (AttributeError, OSError, ProcessLookupError):
        try:
            proc.kill()
        except (AttributeError, OSError):
            return
    try:
        proc.wait(timeout=2)
    except (subprocess.TimeoutExpired, AttributeError):
        pass


def set_active_grok_process(proc: subprocess.Popen | None) -> None:
    global ACTIVE_GROK_PROCESS
    with ACTIVE_PROCESS_LOCK:
        ACTIVE_GROK_PROCESS = proc


def stop_active_grok_process() -> None:
    with ACTIVE_PROCESS_LOCK:
        proc = ACTIVE_GROK_PROCESS
    if proc is not None:
        terminate_process(proc)


def handle_shutdown(signum, _frame) -> None:
    stop_active_grok_process()
    raise SystemExit(128 + signum)


def acquire_run_lock() -> int:
    ensure_state()
    fd = os.open(RUN_LOCK_FILE, os.O_RDWR | os.O_CREAT, 0o600)
    os.fchmod(fd, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except (BlockingIOError, OSError) as exc:
        os.close(fd)
        raise RuntimeError("desk-bridge is already running") from exc
    return fd


def stream_grok_process(
    proc: subprocess.Popen, total_timeout: float | None = None
) -> tuple[str, str, dict]:
    output: queue.Queue = queue.Queue()
    stdout_lines: list[str] = []
    stderr_lines: list[str] = []
    stdout_done = False
    stderr_done = False
    started = time.monotonic()
    total_limit = GROK_TIMEOUT if total_timeout is None else max(0.0, total_timeout)
    last_meaningful: float | None = None
    meta = {
        "first_event_seconds": None,
        "tool_events": 0,
        "model": "",
        "effort": "",
        "prompt_tokens": 0,
        "output_tokens": 0,
        "reasoning_tokens": 0,
        "max_turns": False,
    }
    for pipe, name in ((proc.stdout, "stdout"), (proc.stderr, "stderr")):
        threading.Thread(
            target=_pipe_reader, args=(pipe, name, output), daemon=True
        ).start()

    while not (stdout_done and stderr_done and proc.poll() is not None):
        now = time.monotonic()
        if now - started >= total_limit:
            terminate_process(proc)
            raise GrokTotalTimeout("grok total timeout")
        if last_meaningful is None:
            remaining = min(GROK_FIRST_EVENT_TIMEOUT, total_limit) - (now - started)
            if remaining <= 0:
                terminate_process(proc)
                raise GrokFirstEventTimeout("grok first event timeout")
        else:
            remaining = GROK_IDLE_TIMEOUT - (now - last_meaningful)
            if remaining <= 0:
                terminate_process(proc)
                raise GrokIdleTimeout("grok idle timeout")
        timeout = max(0.01, min(0.5, remaining, total_limit - (now - started)))
        try:
            source, line = output.get(timeout=timeout)
        except queue.Empty:
            if proc.poll() is not None and stdout_done and stderr_done:
                break
            continue
        if source == "stdout_eof":
            stdout_done = True
            continue
        if source == "stderr_eof":
            stderr_done = True
            continue
        if source == "stderr":
            stderr_lines.append(line)
            if len(stderr_lines) > 200:
                stderr_lines = stderr_lines[-200:]
            continue
        stdout_lines.append(line)
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        _update_stream_meta(event, meta)
        if _max_turns_event(event):
            meta["max_turns"] = True
        if _provider_busy_event(event) and meta["tool_events"] == 0:
            terminate_process(proc)
            raise GrokProviderBusy("grok provider capacity")
        if _meaningful_stream_event(event):
            last_meaningful = time.monotonic()
            if meta["first_event_seconds"] is None:
                meta["first_event_seconds"] = round(last_meaningful - started, 3)

    try:
        proc.wait(timeout=2)
    except subprocess.TimeoutExpired:
        terminate_process(proc)
    return "".join(stdout_lines), "".join(stderr_lines), meta


def run_grok(
    prompt: str, new_session: bool = False, deadline: float | None = None
) -> str:
    ensure_state()
    session_id = "" if new_session else read_text(SESSION_FILE)
    reset = False
    reset_reason = session_reset_reason(session_id)
    if session_id and reset_reason:
        session_id = ""
        SESSION_FILE.unlink(missing_ok=True)
        reset = True
    cmd = desk_command(prompt, session_id)
    started = time.monotonic()
    try:
        total_timeout = bounded_timeout(deadline, GROK_TIMEOUT)
    except TimeoutError:
        return with_reset(reset, PHONE_TIMEOUT)
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            env=grok_env(),
            cwd=str(REPO),
            start_new_session=True,
        )
    except FileNotFoundError:
        write_text(LAST_ERROR_FILE, f"{desk_engine()} not on PATH")
        missing = (
            "claude is not installed on this Mac."
            if desk_engine() == "claude"
            else "grok is not installed on this Mac."
        )
        return with_reset(reset, missing)

    set_active_grok_process(proc)
    try:
        try:
            total_timeout = min(total_timeout, bounded_timeout(deadline, total_timeout))
        except TimeoutError:
            terminate_process(proc)
            raise GrokTotalTimeout("grok total timeout")
        stdout, stderr, meta = stream_grok_process(proc, total_timeout=total_timeout)
    except (GrokFirstEventTimeout, GrokProviderBusy) as exc:
        SESSION_FILE.unlink(missing_ok=True)
        write_text(LAST_ERROR_FILE, str(exc))
        append_metric(
            {
                "stage": "grok",
                "outcome": "provider-busy",
                "seconds": round(time.monotonic() - started, 3),
                "fresh": not bool(session_id),
            }
        )
        return with_reset(reset, PHONE_BUSY)
    except (GrokIdleTimeout, GrokTotalTimeout) as exc:
        SESSION_FILE.unlink(missing_ok=True)
        write_text(LAST_ERROR_FILE, str(exc))
        append_metric(
            {
                "stage": "grok",
                "outcome": "timeout",
                "seconds": round(time.monotonic() - started, 3),
                "fresh": not bool(session_id),
            }
        )
        return with_reset(reset, PHONE_TIMEOUT)
    finally:
        if proc.poll() is None:
            terminate_process(proc)
        set_active_grok_process(None)

    stdout = (stdout or "").strip()
    try:
        text, new_id = phone_text_from_stream(stdout)
    except RuntimeError as exc:
        text, new_id = "", ""
        if proc.returncode == 0:
            write_text(LAST_ERROR_FILE, str(exc))
            return with_reset(reset, PHONE_FAIL)

    if proc.returncode != 0 and not text:
        err = (stderr or stdout or f"exit {proc.returncode}")[-800:]
        write_text(LAST_ERROR_FILE, err)
        append_metric(
            {
                "stage": "grok",
                "outcome": "error",
                "seconds": round(time.monotonic() - started, 3),
                "exit": proc.returncode,
            }
        )
        return with_reset(reset, PHONE_FAIL)

    keep_error = False
    if proc.returncode != 0 and meta.get("max_turns"):
        write_text(LAST_ERROR_FILE, "grok max_turns_reached")
        keep_error = True

    effective_effort = meta.get("effort") or PHONE_EFFORT
    effective_model = meta.get("model") or ""
    if new_id:
        observed = session_metadata(new_id)
        effective_effort = meta.get("effort") or observed.get("effort") or PHONE_EFFORT
        effective_model = meta.get("model") or observed.get("model") or ""
        if effective_effort == PHONE_EFFORT:
            write_text(SESSION_FILE, new_id)
        else:
            SESSION_FILE.unlink(missing_ok=True)
        write_json(
            SESSION_META_FILE,
            {
                "session_id": new_id,
                "engine": desk_engine(),
                "model": effective_model,
                "effort": effective_effort,
                "prompt_tokens": meta.get("prompt_tokens") or 0,
            },
        )
    if not keep_error:
        LAST_ERROR_FILE.unlink(missing_ok=True)
    elapsed = round(time.monotonic() - started, 3)
    run_record = {
        "seconds": elapsed,
        "first_event_seconds": meta.get("first_event_seconds"),
        "effort": effective_effort if new_id else (meta.get("effort") or PHONE_EFFORT),
        "model": effective_model if new_id else (meta.get("model") or ""),
        "prompt_tokens": meta.get("prompt_tokens") or 0,
        "output_tokens": meta.get("output_tokens") or 0,
        "reasoning_tokens": meta.get("reasoning_tokens") or 0,
        "tool_events": meta.get("tool_events") or 0,
        "fresh": not bool(session_id),
        "reset_reason": reset_reason,
    }
    write_text(
        LAST_RUN_FILE,
        json.dumps(run_record, separators=(",", ":")),
    )
    append_metric({"stage": "grok", "outcome": "ok", **run_record})
    return with_reset(reset, text or "(no text)")


def with_reset(reset: bool, text: str) -> str:
    if not reset:
        return text
    return "Session reset. The last one was too big or gone.\n\n" + text


def multipart(fields: dict[str, str], filename: str, blob: bytes, ctype: str) -> tuple[bytes, str]:
    bound = "----rua" + uuid.uuid4().hex
    parts: list[bytes] = []
    for name, value in fields.items():
        parts.append(
            (
                f"--{bound}\r\n"
                f'Content-Disposition: form-data; name="{name}"\r\n\r\n'
                f"{value}\r\n"
            ).encode()
        )
    parts.append(
        (
            f"--{bound}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
            f"Content-Type: {ctype}\r\n\r\n"
        ).encode()
        + blob
        + b"\r\n"
    )
    parts.append(f"--{bound}--\r\n".encode())
    return b"".join(parts), bound


def transcribe_voice(
    blob: bytes,
    filename: str,
    mime: str,
    api_key: str,
    timeout: float = 90,
    deadline: float | None = None,
) -> str:
    body, bound = multipart(
        {"model_id": SCRIBE_MODEL, "tag_audio_events": "false"},
        filename,
        blob,
        mime or "application/octet-stream",
    )
    req = urllib.request.Request(
        SCRIBE_URL,
        data=body,
        headers={
            "xi-api-key": api_key,
            "Content-Type": f"multipart/form-data; boundary={bound}",
        },
        method="POST",
    )
    try:
        response = fetch_url_bytes(
            req,
            timeout,
            deadline=deadline,
            max_bytes=2 * 1024 * 1024,
        )
        data = json.loads(response.decode())
        if not isinstance(data, dict):
            raise RuntimeError("scribe returned a non-object")
        text = (data.get("text") or "").strip()
    except urllib.error.HTTPError as exc:
        err = exc.read().decode(errors="replace")[:240]
        raise RuntimeError(f"scribe HTTP {exc.code}: {err}") from exc
    except (TimeoutError, socket.timeout) as exc:
        raise RuntimeError("scribe timed out") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"scribe failed: {exc.reason}") from exc
    except (json.JSONDecodeError, UnicodeDecodeError, AttributeError) as exc:
        raise RuntimeError(f"scribe bad response: {exc}") from exc
    if not text:
        raise RuntimeError("scribe returned empty text")
    return text


def telegram_file(
    token: str, file_id: str, deadline: float | None = None
) -> tuple[bytes, str]:
    meta = api(
        token,
        "getFile",
        {"file_id": file_id},
        timeout=bounded_timeout(deadline, 70),
        deadline=deadline,
    )
    result = meta.get("result") or {}
    size = int(result.get("file_size") or 0)
    if size > VOICE_MAX_BYTES:
        raise RuntimeError("voice note is too large")
    path = result.get("file_path") or ""
    if not path:
        raise RuntimeError("telegram getFile had no path")
    url = f"https://api.telegram.org/file/bot{token}/{path}"
    blob = download_bytes(
        url,
        timeout=bounded_timeout(deadline, 60),
        deadline=deadline,
        max_bytes=VOICE_MAX_BYTES,
    )
    if len(blob) > VOICE_MAX_BYTES:
        raise RuntimeError("voice note is too large")
    name = Path(path).name or "voice.ogg"
    return blob, name


def current_queue_depth() -> int:
    coordinator = globals().get("WORK_COORDINATOR")
    return coordinator.depth() if coordinator is not None else 0


def handle_prompt(
    token: str,
    chat_id: int,
    message_id: int | None,
    prompt: str,
    deadline: float | None = None,
    from_voice: bool = False,
) -> str:
    del token, chat_id, message_id
    stripped = prompt.strip()
    low = stripped.lower()
    if low in {"/start", "/help"}:
        return help_text()
    if low.startswith("/") and low not in KNOWN_SLASH:
        # Capture commands keep their payload: "/park buy filters" captures.
        if low.split()[0] not in CAPTURE_SLASH:
            return help_text()
    if low == "/new":
        SESSION_FILE.unlink(missing_ok=True)
        SESSION_META_FILE.unlink(missing_ok=True)
        return "New session. Next message starts fresh."
    if is_status_command(low):
        env = load_secrets()
        session_id = read_text(SESSION_FILE)
        meta = session_metadata(session_id) if session_id else {}
        owner = (env.get("TELEGRAM_USER_ID") or "").strip()
        return "\n".join(
            [
                f"owner: {owner or '(missing)'}",
                f"session: {'set' if session_id else 'none'}",
                f"effort: {meta.get('effort') or PHONE_EFFORT}",
                f"queue: {current_queue_depth()}",
                f"pending: {pending_outbox_count()}",
                f"engine: {desk_engine()}",
                f"last run: {format_last_run(read_text(LAST_RUN_FILE))}",
                f"last error: {read_text(LAST_ERROR_FILE) or 'none'}",
                f"next: {format_next_session(session_id)}",
            ]
        )
    if is_brief_command(low):
        return pocket_brief() or "Nothing open."
    if is_todo_command(low):
        return format_open_todo()
    kind, body = parse_capture(stripped)
    if kind == "park":
        return capture_park(body)
    if kind == "idea":
        return capture_idea(body)
    if kind == "brainstorm":
        if not body:
            return "Say the idea."
        return google_miss_finish(
            persist_desk_writes(
                run_grok(
                    "Brainstorm briefly. One short result. No deck. No table.\n\n"
                    + body,
                    deadline=deadline,
                ),
                allow_done=not from_voice,
            )
        )
    return google_miss_finish(
        persist_desk_writes(
            run_grok(stripped, deadline=deadline),
            allow_done=not from_voice,
        )
    )


def handle_voice(
    token: str,
    chat_id: int,
    message_id: int | None,
    voice: dict,
    deadline: float | None = None,
) -> str:
    del chat_id, message_id
    key = (load_secrets().get("ELEVENLABS_API_KEY") or "").strip()
    if not key:
        return "Voice is wired. ElevenLabs key is missing."
    file_id = voice.get("file_id") or ""
    if not file_id:
        return "That voice note had no file."
    started = time.monotonic()
    try:
        blob, name = telegram_file(token, file_id, deadline=deadline)
        downloaded = time.monotonic()
        text = transcribe_voice(
            blob,
            name,
            voice.get("mime_type") or "audio/ogg",
            key,
            timeout=bounded_timeout(deadline, 90),
            deadline=deadline,
        )
    except (RuntimeError, TimeoutError) as exc:
        write_text(LAST_ERROR_FILE, str(exc))
        deadline_hit = deadline is not None and time.monotonic() >= deadline
        append_metric(
            {
                "stage": "voice",
                "outcome": "timeout" if deadline_hit else "error",
                "seconds": round(time.monotonic() - started, 3),
            }
        )
        if deadline_hit or isinstance(exc, TimeoutError):
            return PHONE_TIMEOUT
        return "Couldn't transcribe that. Try again or type it."
    append_metric(
        {
            "stage": "voice",
            "outcome": "ok",
            "download_seconds": round(downloaded - started, 3),
            "transcribe_seconds": round(time.monotonic() - downloaded, 3),
        }
    )
    if deadline is not None and time.monotonic() >= deadline:
        return PHONE_TIMEOUT
    return handle_prompt(
        "", 0, None, f"Voice note: {text}", deadline=deadline, from_voice=True
    )


def is_private_dm(chat: dict) -> bool:
    return chat.get("type") == "private"


def pair_status(env: dict[str, str], user_id: int) -> str:
    paired = configured_owner(env)
    if paired == str(user_id):
        return "ok"
    return "foreign"


def allowed(env: dict[str, str], user_id: int) -> bool:
    return pair_status(env, user_id) == "ok"


class WorkCoordinator:
    def __init__(self, token: str, delivery_notify=None):
        self.token = token
        self.delivery_notify = delivery_notify
        self.jobs: queue.Queue = queue.Queue()
        self.lock = threading.Lock()
        self.epoch = 0
        for item in inbox_items():
            try:
                next_offset = int(item["id"]) + 1
                chat_id = int(item["chat_id"])
            except (KeyError, TypeError, ValueError):
                write_text(LAST_ERROR_FILE, "invalid queued Telegram update discarded")
                remove_inbox_job(item.get("id"))
                continue
            # A crash may occur after the durable inbox write but before the
            # offset write. Repair that boundary before recovered work runs.
            advance_offset(next_offset)
            if item.get("status") == "running":
                enqueue_outbox(item.get("id", time.time_ns()), chat_id, PHONE_FAIL)
                remove_inbox_job(item.get("id"))
                write_text(LAST_ERROR_FILE, "uncertain interrupted job was not replayed")
                continue
            item.pop("status", None)
            self.jobs.put(item)
        self.worker = threading.Thread(target=self._run, daemon=True)

    def start(self) -> None:
        self.worker.start()

    def enqueue(self, job: dict) -> int:
        with self.lock:
            position = self.depth()
            next_offset = int(job["id"]) + 1
            if next_offset <= read_offset():
                return position
            if not persist_inbox_job(job):
                return position
            # Work must never be visible to the worker before Telegram's
            # high-water mark is durable. Otherwise a crash can replay a
            # completed command and duplicate its side effects.
            advance_offset(next_offset)
            self.jobs.put(job)
            return position

    def cancel_pending(self) -> int:
        with self.lock:
            self.epoch += 1
            drained = 0
            while True:
                try:
                    job = self.jobs.get_nowait()
                except queue.Empty:
                    break
                remove_inbox_job(job.get("id"))
                try:
                    self.jobs.task_done()
                except (ValueError, RuntimeError):
                    pass
                drained += 1
            stop_active_grok_process()
            return drained

    def depth(self) -> int:
        # unfinished_tasks covers queued and currently running work without
        # the jobs.get() -> active-flag race of a separate counter.
        with self.jobs.all_tasks_done:
            return self.jobs.unfinished_tasks

    def _run(self) -> None:
        while True:
            job = self.jobs.get()
            try:
                mark_inbox_job(job.get("id"), "running")
                if self.delivery_notify is None:
                    process_work_item(self.token, job)
                else:
                    process_work_item(
                        self.token, job, delivery_notify=self.delivery_notify
                    )
            except Exception as exc:  # noqa: BLE001 — keep the worker alive
                try:
                    write_text(LAST_ERROR_FILE, f"worker: {exc}")
                except Exception:
                    pass
                try:
                    enqueue_outbox(
                        job.get("id", time.time_ns()), int(job["chat_id"]), PHONE_FAIL
                    )
                    if self.delivery_notify is None:
                        deliver_outbox(self.token)
                    else:
                        self.delivery_notify()
                except Exception:
                    pass
            finally:
                try:
                    remove_inbox_job(job.get("id"))
                except Exception:
                    pass
                try:
                    self.jobs.task_done()
                except (ValueError, RuntimeError):
                    pass


WORK_COORDINATOR: WorkCoordinator | None = None
OUTBOX_DELIVERER: OutboxDeliverer | None = None


def process_work_item(token: str, job: dict, delivery_notify=None) -> None:
    started = time.monotonic()
    # The five-minute budget starts when Telegram accepts the ask, including
    # any queue wait, so a busy bridge cannot silently extend the contract.
    expires_at = float(job.get("expires_at") or (
        float(job.get("enqueued_at") or time.time()) + PHONE_REQUEST_TIMEOUT
    ))
    deadline = started + max(0.0, expires_at - time.time())
    queue_seconds = round(
        max(0.0, time.time() - float(job.get("enqueued_at") or time.time())), 3
    )
    chat_id = int(job["chat_id"])
    message_id = job.get("message_id")
    text = job.get("text") or ""
    voice = job.get("voice")
    command = is_instant_command(text)
    epoch = 0
    coordinator = globals().get("WORK_COORDINATOR")
    if coordinator is not None:
        epoch = coordinator.epoch
    stop = threading.Event()
    pulse: threading.Thread | None = None
    expired = time.monotonic() >= deadline and not command
    if not command and not expired:
        pulse = threading.Thread(
            target=feedback_pulse,
            args=(token, chat_id, message_id, stop),
            daemon=True,
        )
        pulse.start()
    try:
        if expired:
            reply = PHONE_TIMEOUT
            kind = "expired"
        elif text:
            reply = handle_prompt(token, chat_id, message_id, text, deadline=deadline)
            kind = "text"
        elif voice:
            reply = handle_voice(token, chat_id, message_id, voice, deadline=deadline)
            kind = "voice"
        else:
            reply = "Text or a voice note."
            kind = "unsupported"
    finally:
        stop.set()
        if pulse is not None:
            pulse.join(timeout=0.05)
    if coordinator is not None and coordinator.epoch != epoch:
        remove_inbox_job(job["id"])
        return
    enqueue_outbox(job["id"], chat_id, reply)
    # Once the result is durable, the work is complete. Retire the inbox job
    # before delivery so a crash after Telegram accepts the reply cannot cause
    # recovery to append a false generic failure.
    remove_inbox_job(job["id"])
    if delivery_notify is None:
        delivered = deliver_outbox(token)
        outcome = "delivered" if delivered else "pending-delivery"
    else:
        delivery_notify()
        outcome = "delivery-queued"
    append_metric(
        {
            "stage": "request",
            "outcome": outcome,
            "kind": kind,
            "queue_seconds": queue_seconds,
            "total_seconds": round(time.monotonic() - started, 3),
        }
    )


def handle_update(token: str, update: dict, enqueue) -> int:
    update_id = int(update.get("update_id") or 0)
    next_offset = update_id + 1
    msg = update.get("message") or {}
    chat = msg.get("chat") or {}
    user = msg.get("from") or {}
    chat_id = chat.get("id")
    user_id = user.get("id")
    if chat_id is None or user_id is None:
        return next_offset
    if not is_private_dm(chat):
        return next_offset
    env = load_secrets()
    try:
        status = pair_status(env, int(user_id))
    except ValueError as exc:
        write_text(LAST_ERROR_FILE, str(exc))
        return next_offset
    if status == "foreign":
        safe_send(
            token,
            int(chat_id),
            "This desk is paired to another Telegram account.",
        )
        return next_offset
    text = msg.get("text")
    voice = msg.get("voice")
    if not text and not voice:
        safe_send(token, int(chat_id), "Text or a voice note.")
        return next_offset
    if text and is_instant_command(text):
        if text.strip().lower() == "/new":
            coordinator = globals().get("WORK_COORDINATOR")
            if coordinator is not None:
                coordinator.cancel_pending()
        reply = handle_prompt(
            token, int(chat_id), msg.get("message_id"), text
        )
        safe_send(token, int(chat_id), reply)
        append_metric(
            {
                "stage": "pickup",
                "outcome": "accepted",
                "kind": "text",
                "pickup_seconds": None,
                "queue_position": 0,
                "queue_ack": None,
            }
        )
        return next_offset
    job = {
        "id": update_id,
        "chat_id": int(chat_id),
        "message_id": msg.get("message_id"),
        "text": text or "",
        "voice": voice,
        "enqueued_at": time.time(),
        "expires_at": time.time() + PHONE_REQUEST_TIMEOUT,
    }
    message_date = msg.get("date")
    pickup_seconds = None
    if isinstance(message_date, (int, float)):
        pickup_seconds = round(max(0.0, time.time() - float(message_date)), 3)
    position = int(enqueue(job))
    acknowledged = None
    if position >= 1:
        acknowledged = safe_send(token, int(chat_id), PHONE_QUEUE)
    append_metric(
        {
            "stage": "pickup",
            "outcome": "queued" if position >= 1 else "accepted",
            "kind": "voice" if voice else "text",
            "pickup_seconds": pickup_seconds,
            "queue_position": position,
            "queue_ack": acknowledged,
        }
    )
    return next_offset


def poll_loop(token: str) -> None:
    global OUTBOX_DELIVERER, WORK_COORDINATOR
    ensure_runtime_permissions()
    configured_owner(load_secrets())
    OUTBOX_DELIVERER = OutboxDeliverer(token)
    OUTBOX_DELIVERER.start()
    WORK_COORDINATOR = WorkCoordinator(token, OUTBOX_DELIVERER.notify)
    # Recovery can repair the durable high-water mark from queued work.
    offset = read_offset()
    WORK_COORDINATOR.start()
    OUTBOX_DELIVERER.notify()
    while True:
        try:
            data = api(
                token,
                "getUpdates",
                {"timeout": 50, "offset": offset, "allowed_updates": ["message"]},
                timeout=70,
            )
        except Exception as exc:  # noqa: BLE001 — stay up
            # Long-poll idle timeout is expected. Do not overwrite a real desk miss.
            if str(exc) != "telegram getUpdates timed out":
                write_text(LAST_ERROR_FILE, str(exc))
            time.sleep(5)
            continue
        for upd in data.get("result") or []:
            try:
                next_offset = handle_update(token, upd, WORK_COORDINATOR.enqueue)
                offset = advance_offset(next_offset)
            except Exception as exc:  # noqa: BLE001 — retry this update after restart
                write_text(LAST_ERROR_FILE, f"update {upd.get('update_id')}: {exc}")
                break


def cmd_check() -> int:
    ensure_runtime_permissions()
    env = load_secrets()
    token = (env.get("TELEGRAM_BOT_TOKEN") or "").strip()
    if not token:
        print(f"missing TELEGRAM_BOT_TOKEN in {SECRETS}")
        return 1
    try:
        owner = configured_owner(env)
    except ValueError as exc:
        print(str(exc))
        return 1
    try:
        me = api(token, "getMe", timeout=20)
    except RuntimeError as exc:
        print(str(exc))
        return 1
    if not me.get("ok"):
        print("telegram getMe failed")
        return 1
    username = (me.get("result") or {}).get("username")
    print(f"telegram ok  @{username}")
    print(f"owner user   {owner}")
    eleven = (env.get("ELEVENLABS_API_KEY") or "").strip()
    print(f"scribe       {'ok' if eleven else 'missing ELEVENLABS_API_KEY'}")
    grok = grok_bin()
    if not shutil.which(grok) and not Path(grok).is_file():
        print("grok missing")
        return 1
    try:
        ver = subprocess.run([grok, "--version"], capture_output=True, text=True, timeout=20)
    except (subprocess.TimeoutExpired, OSError) as exc:
        print(f"grok version failed: {exc}")
        return 1
    if ver.returncode != 0:
        print((ver.stderr or ver.stdout or "grok --version failed").strip())
        return 1
    line = (ver.stdout or ver.stderr or "").strip().splitlines()
    print(f"grok ok      {line[0] if line else grok}")
    engine = desk_engine()
    print(f"engine      {engine}")
    if engine == "claude":
        claude = claude_bin()
        if not shutil.which(claude) and not Path(claude).is_file():
            print("claude missing")
            return 1
        print(f"claude ok    {claude}")
    print(f"repo         {REPO}")
    if not grok_env().get("XPOZ_API_KEY"):
        print("xpoz         missing XPOZ_API_KEY (phone MCP will 401)")
    else:
        print("xpoz         ok")
    print("check ok")
    return 0


def plist_body() -> str:
    script = REPO / "30-tools" / "desk-bridge" / "bridge.py"
    log = BRIDGE_LOG_FILE
    err = BRIDGE_ERR_FILE
    path = ":".join(
        [
            str(Path.home() / ".grok" / "bin"),
            str(Path.home() / ".local/bin"),
            "/opt/homebrew/bin",
            "/usr/local/bin",
            "/usr/bin",
            "/bin",
        ]
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>{LABEL}</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/caffeinate</string>
    <string>-i</string>
    <string>-s</string>
    <string>/usr/bin/python3</string>
    <string>{script}</string>
    <string>--run</string>
  </array>
  <key>WorkingDirectory</key>
  <string>{REPO}</string>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>Umask</key>
  <integer>63</integer>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key>
    <string>{path}</string>
    <key>HOME</key>
    <string>{Path.home()}</string>
    <key>RUA_REPO</key>
    <string>{REPO}</string>
  </dict>
  <key>StandardOutPath</key>
  <string>{log}</string>
  <key>StandardErrorPath</key>
  <string>{err}</string>
</dict>
</plist>
"""


def cmd_install() -> int:
    if cmd_check() != 0:
        return 1
    ensure_state()
    for path in (BRIDGE_LOG_FILE, BRIDGE_ERR_FILE):
        if path.exists():
            os.chmod(path, 0o600)
        else:
            atomic_write_text(path, "", mode=0o600)
    try:
        loaded_before = launchd_loaded()
    except OSError as exc:
        print(f"launchctl check failed: {exc}")
        return 1
    previous_plist = None
    if PLIST_PATH.is_file():
        previous_plist = PLIST_PATH.read_text(encoding="utf-8")
    PLIST_PATH.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_text(PLIST_PATH, plist_body(), mode=0o600)
    if loaded_before:
        try:
            unloaded = subprocess.run(
                ["launchctl", "unload", str(PLIST_PATH)],
                capture_output=True,
                text=True,
            )
        except OSError as exc:
            restore_plist(previous_plist)
            print(f"launchctl unload failed: {exc}")
            return 1
        if unloaded.returncode != 0:
            restore_plist(previous_plist)
            print((unloaded.stderr or unloaded.stdout or "launchctl unload failed").strip())
            return 1
    try:
        loaded = subprocess.run(
            ["launchctl", "load", str(PLIST_PATH)], capture_output=True, text=True
        )
    except OSError as exc:
        rollback_install(previous_plist, loaded_before)
        print(f"launchctl load failed: {exc}")
        return 1
    if loaded.returncode != 0:
        rollback_install(previous_plist, loaded_before)
        print((loaded.stderr or loaded.stdout or "launchctl load failed").strip())
        return 1
    try:
        healthy = launchd_loaded()
    except OSError as exc:
        healthy = False
        health_error = str(exc)
    else:
        health_error = "job not present after launchctl load"
    if not healthy:
        try:
            subprocess.run(
                ["launchctl", "unload", str(PLIST_PATH)],
                capture_output=True,
                text=True,
            )
        except OSError:
            pass
        rollback_install(previous_plist, loaded_before)
        print(f"launchctl health check failed: {health_error}")
        return 1
    print(f"installed {PLIST_PATH}")
    print("DM @Rua_desk_bot on Telegram.")
    return 0


def restore_plist(previous: str | None) -> None:
    if previous is None:
        PLIST_PATH.unlink(missing_ok=True)
    else:
        atomic_write_text(PLIST_PATH, previous, mode=0o600)


def rollback_install(previous: str | None, loaded_before: bool) -> bool:
    restore_plist(previous)
    if not loaded_before or previous is None:
        return True
    try:
        restored = subprocess.run(
            ["launchctl", "load", str(PLIST_PATH)], capture_output=True, text=True
        )
    except OSError:
        return False
    return restored.returncode == 0


def launchd_loaded() -> bool:
    target = f"gui/{os.getuid()}/{LABEL}"
    result = subprocess.run(["launchctl", "print", target], capture_output=True)
    return result.returncode == 0


def cmd_uninstall() -> int:
    if PLIST_PATH.exists():
        try:
            loaded = launchd_loaded()
        except OSError as exc:
            print(f"launchctl check failed: {exc}")
            return 1
    else:
        loaded = False
    if loaded:
        try:
            unloaded = subprocess.run(
                ["launchctl", "unload", str(PLIST_PATH)],
                capture_output=True,
                text=True,
            )
        except OSError as exc:
            print(f"launchctl unload failed: {exc}")
            return 1
        if unloaded.returncode != 0:
            print((unloaded.stderr or unloaded.stdout or "launchctl unload failed").strip())
            return 1
    if PLIST_PATH.exists():
        PLIST_PATH.unlink()
    print("uninstalled")
    return 0


def main(argv: list[str]) -> int:
    global RUN_LOCK_FD
    arg = argv[1] if len(argv) > 1 else "--help"
    if arg in {"-h", "--help"}:
        print("usage: bridge.py --check | --install | --uninstall | --run")
        return 0
    if arg == "--check":
        return cmd_check()
    if arg == "--install":
        return cmd_install()
    if arg == "--uninstall":
        return cmd_uninstall()
    if arg == "--run":
        ensure_runtime_permissions()
        env = load_secrets()
        token = (env.get("TELEGRAM_BOT_TOKEN") or "").strip()
        if not token:
            print(f"missing TELEGRAM_BOT_TOKEN in {SECRETS}", file=sys.stderr)
            return 1
        try:
            configured_owner(env)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        try:
            RUN_LOCK_FD = acquire_run_lock()
        except RuntimeError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        signal.signal(signal.SIGTERM, handle_shutdown)
        signal.signal(signal.SIGINT, handle_shutdown)
        poll_loop(token)
        return 0
    print(f"unknown arg: {arg}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
