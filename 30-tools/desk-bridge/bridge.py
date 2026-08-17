#!/usr/bin/env python3
"""Telegram seat for the Rua desk. Stdlib only."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

REPO = Path(os.environ.get("RUA_REPO", Path.home() / "Rua"))
SECRETS = Path.home() / ".grok" / "secrets" / "desk-bridge.env"
ELEVEN_SECRETS = Path.home() / ".grok" / "secrets" / "elevenlabs.env"
STATE_DIR = Path.home() / ".grok" / "desk-bridge"
SESSION_FILE = STATE_DIR / "session_id"
OFFSET_FILE = STATE_DIR / "offset"
LAST_ERROR_FILE = STATE_DIR / "last_error"
LAST_RUN_FILE = STATE_DIR / "last_run"
PLIST_PATH = Path.home() / "Library" / "LaunchAgents" / "com.rua.desk-bridge.plist"
LABEL = "com.rua.desk-bridge"
TG_LIMIT = 3900
GROK_TIMEOUT = 15 * 60
PHONE_EFFORT = "medium"
PHONE_MAX_TURNS = 24
SESSION_BYTES = 400_000
VOICE_MAX_BYTES = 20 * 1024 * 1024
SCRIBE_URL = "https://api.elevenlabs.io/v1/speech-to-text"
SCRIBE_MODEL = "scribe_v2"
DESK_RULES = """You are the Rua desk conductor, reached by Telegram while the founder is on the go.
Read 20-studio/desk.md and AGENTS.md when the class of work needs them.
Name the class to yourself before loading doctrine. Do not invent work.
Do the work. Do not narrate loading, searching, or thinking.
Telegram gets one short result: what happened, where it is, what they need.
Before that reply, read 30-tools/desk-bridge/EXPERIENCE.md Voice and tone.
Do not contradict that file.
No markdown tables. No class label in the chat. No process talk.
A line starting with Voice note: is a spoken message. Treat it as the ask.
Do not ask them to sit down at the Mac unless the machine itself is the blocker.
Mail, calendar, and Drive are Grok Space connectors. This phone seat does not have them.
Do not use Mail.app, Calendar.app, icalBuddy, Chrome, or local mail CLIs as a stand-in.
If the ask needs those, stop. Reply with exactly: Google isn't on this phone seat. Parked on the desk list.
Write the miss under Desk → Blocked in 20-studio/lists.md. Still answer from local files if those help.
"""


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
    env.update(load_env(ELEVEN_SECRETS))
    return env


def write_user_id(user_id: str, path: Path = SECRETS) -> None:
    text = path.read_text() if path.is_file() else ""
    if re.search(r"^export TELEGRAM_USER_ID=.*$", text, re.M):
        text = re.sub(
            r"^export TELEGRAM_USER_ID=.*$",
            f"export TELEGRAM_USER_ID={user_id}",
            text,
            count=1,
            flags=re.M,
        )
    else:
        if text and not text.endswith("\n"):
            text += "\n"
        text += f"export TELEGRAM_USER_ID={user_id}\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


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
        if kind == "text":
            saw_event = True
            bit = ev.get("data") or ""
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
    if not saw_end:
        raise RuntimeError("grok stream incomplete")
    text = "".join(last_block).strip()
    if not text and not saw_tool:
        text = "".join(all_text).strip()
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


def should_drop_session(session_id: str, limit: int = SESSION_BYTES) -> bool:
    if not session_id:
        return False
    hist = session_history_path(session_id)
    if hist is None:
        return True
    return session_is_heavy(session_id, limit)


def ensure_state() -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def read_text(path: Path) -> str:
    try:
        return path.read_text().strip()
    except FileNotFoundError:
        return ""


def write_text(path: Path, value: str) -> None:
    ensure_state()
    path.write_text(value)


def grok_bin() -> str:
    found = shutil.which("grok")
    if found:
        return found
    fallback = Path.home() / ".grok" / "bin" / "grok"
    if fallback.is_file():
        return str(fallback)
    return "grok"


def api(token: str, method: str, payload: dict | None = None, timeout: int = 70) -> dict:
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")
        raise RuntimeError(f"telegram {method} HTTP {exc.code}: {body[:300]}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"telegram {method} failed: {exc.reason}") from exc


def download_bytes(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"download HTTP {exc.code}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        reason = getattr(exc, "reason", exc)
        raise RuntimeError(f"download failed: {reason}") from exc


def send(token: str, chat_id: int, text: str) -> None:
    for part in chunk_text(text):
        api(token, "sendMessage", {"chat_id": chat_id, "text": part})


def react(token: str, chat_id: int, message_id: int | None, emoji: str = "👀") -> None:
    if not message_id:
        return
    try:
        api(
            token,
            "setMessageReaction",
            {
                "chat_id": chat_id,
                "message_id": message_id,
                "reaction": [{"type": "emoji", "emoji": emoji}],
            },
        )
    except RuntimeError:
        pass


def typing_pulse(token: str, chat_id: int, stop: threading.Event) -> None:
    while not stop.wait(4):
        try:
            api(token, "sendChatAction", {"chat_id": chat_id, "action": "typing"})
        except RuntimeError:
            return


def help_text() -> str:
    return (
        "Rua desk on Telegram.\n"
        "/help — this\n"
        "/new — fresh Grok session\n"
        "/status — session and pairing\n"
        "Text or a voice note goes to the desk."
    )


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
    return env


def run_grok(prompt: str, new_session: bool = False) -> str:
    ensure_state()
    session_id = "" if new_session else read_text(SESSION_FILE)
    reset = False
    if session_id and should_drop_session(session_id):
        session_id = ""
        SESSION_FILE.unlink(missing_ok=True)
        reset = True
    cmd = [
        grok_bin(),
        "-p",
        prompt,
        "--cwd",
        str(REPO),
        "--output-format",
        "streaming-json",
        "--yolo",
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
    started = time.time()
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=GROK_TIMEOUT,
            env=grok_env(),
            cwd=str(REPO),
        )
    except subprocess.TimeoutExpired:
        write_text(LAST_ERROR_FILE, "grok timed out")
        return with_reset(reset, "The desk timed out. Send it again or try a smaller ask.")
    except FileNotFoundError:
        write_text(LAST_ERROR_FILE, "grok not on PATH")
        return with_reset(reset, "grok is not installed on this Mac.")

    stdout = (proc.stdout or "").strip()
    if proc.returncode != 0:
        err = (proc.stderr or stdout or f"exit {proc.returncode}")[-800:]
        write_text(LAST_ERROR_FILE, err)
        return with_reset(reset, PHONE_FAIL)

    try:
        text, new_id = phone_text_from_stream(stdout)
    except RuntimeError as exc:
        write_text(LAST_ERROR_FILE, str(exc))
        return with_reset(reset, PHONE_FAIL)

    if new_id:
        write_text(SESSION_FILE, new_id)
    LAST_ERROR_FILE.unlink(missing_ok=True)
    write_text(
        LAST_RUN_FILE,
        json.dumps(
            {
                "seconds": round(time.time() - started, 1),
                "effort": PHONE_EFFORT,
                "fresh": not bool(session_id),
            }
        ),
    )
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


def transcribe_voice(blob: bytes, filename: str, mime: str, api_key: str) -> str:
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
        with urllib.request.urlopen(req, timeout=90) as resp:
            data = json.loads(resp.read().decode())
        if not isinstance(data, dict):
            raise RuntimeError("scribe returned a non-object")
        text = (data.get("text") or "").strip()
    except urllib.error.HTTPError as exc:
        err = exc.read().decode(errors="replace")[:240]
        raise RuntimeError(f"scribe HTTP {exc.code}: {err}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"scribe failed: {exc.reason}") from exc
    except (json.JSONDecodeError, UnicodeDecodeError, AttributeError) as exc:
        raise RuntimeError(f"scribe bad response: {exc}") from exc
    if not text:
        raise RuntimeError("scribe returned empty text")
    return text


def telegram_file(token: str, file_id: str) -> tuple[bytes, str]:
    meta = api(token, "getFile", {"file_id": file_id})
    result = meta.get("result") or {}
    size = int(result.get("file_size") or 0)
    if size > VOICE_MAX_BYTES:
        raise RuntimeError("voice note is too large")
    path = result.get("file_path") or ""
    if not path:
        raise RuntimeError("telegram getFile had no path")
    url = f"https://api.telegram.org/file/bot{token}/{path}"
    blob = download_bytes(url)
    if len(blob) > VOICE_MAX_BYTES:
        raise RuntimeError("voice note is too large")
    name = Path(path).name or "voice.ogg"
    return blob, name


def handle_prompt(token: str, chat_id: int, message_id: int | None, prompt: str) -> None:
    stripped = prompt.strip()
    low = stripped.lower()
    if low in {"/start", "/help"}:
        send(token, chat_id, help_text())
        return
    if low == "/new":
        SESSION_FILE.unlink(missing_ok=True)
        send(token, chat_id, "New session. Next message starts fresh.")
        return
    if low == "/status":
        env = load_secrets()
        last = read_text(LAST_RUN_FILE)
        send(
            token,
            chat_id,
            "\n".join(
                [
                    f"repo: {REPO}",
                    f"user: {env.get('TELEGRAM_USER_ID') or '(unpaired)'}",
                    f"session: {read_text(SESSION_FILE) or '(none)'}",
                    f"effort: {PHONE_EFFORT}",
                    f"last run: {last or 'none'}",
                    f"last error: {read_text(LAST_ERROR_FILE) or 'none'}",
                ]
            ),
        )
        return
    react(token, chat_id, message_id)
    stop = threading.Event()
    pulse = threading.Thread(target=typing_pulse, args=(token, chat_id, stop), daemon=True)
    try:
        api(token, "sendChatAction", {"chat_id": chat_id, "action": "typing"})
    except RuntimeError:
        pass
    pulse.start()
    try:
        reply = run_grok(stripped)
    finally:
        stop.set()
    send(token, chat_id, reply)


def handle_voice(token: str, chat_id: int, message_id: int | None, voice: dict) -> None:
    key = (load_secrets().get("ELEVENLABS_API_KEY") or "").strip()
    if not key:
        send(token, chat_id, "Voice is wired. ElevenLabs key is missing.")
        return
    file_id = voice.get("file_id") or ""
    if not file_id:
        send(token, chat_id, "That voice note had no file.")
        return
    try:
        api(token, "sendChatAction", {"chat_id": chat_id, "action": "typing"})
        blob, name = telegram_file(token, file_id)
        text = transcribe_voice(blob, name, voice.get("mime_type") or "audio/ogg", key)
    except RuntimeError as exc:
        write_text(LAST_ERROR_FILE, str(exc))
        send(token, chat_id, "Couldn't transcribe that. Try again or type it.")
        return
    handle_prompt(token, chat_id, message_id, f"Voice note: {text}")


def is_private_dm(chat: dict) -> bool:
    return chat.get("type") == "private"


def pair_status(env: dict[str, str], user_id: int) -> str:
    paired = (env.get("TELEGRAM_USER_ID") or "").strip()
    if not paired:
        write_user_id(str(user_id), SECRETS)
        return "claimed"
    if paired == str(user_id):
        return "ok"
    return "foreign"


def allowed(env: dict[str, str], user_id: int) -> bool:
    return pair_status(env, user_id) != "foreign"


def poll_loop(token: str) -> None:
    ensure_state()
    offset = int(read_text(OFFSET_FILE) or "0")
    while True:
        try:
            data = api(
                token,
                "getUpdates",
                {"timeout": 50, "offset": offset, "allowed_updates": ["message"]},
                timeout=70,
            )
        except Exception as exc:  # noqa: BLE001 — stay up
            write_text(LAST_ERROR_FILE, str(exc))
            time.sleep(5)
            continue
        for upd in data.get("result") or []:
            next_offset = int(upd["update_id"]) + 1
            try:
                msg = upd.get("message") or {}
                chat = msg.get("chat") or {}
                user = msg.get("from") or {}
                chat_id = chat.get("id")
                user_id = user.get("id")
                message_id = msg.get("message_id")
                text = msg.get("text")
                voice = msg.get("voice")
                if chat_id is None or user_id is None:
                    continue
                if not is_private_dm(chat):
                    continue
                env = load_secrets()
                status = pair_status(env, int(user_id))
                if status == "foreign":
                    send(token, int(chat_id), "This desk is paired to someone else.")
                    continue
                if status == "claimed":
                    send(token, int(chat_id), "Paired. This desk answers you.")
                try:
                    if text:
                        handle_prompt(token, int(chat_id), message_id, text)
                    elif voice:
                        handle_voice(token, int(chat_id), message_id, voice)
                    else:
                        send(token, int(chat_id), "Text or a voice note.")
                except Exception as exc:  # noqa: BLE001 — keep the loop up
                    write_text(LAST_ERROR_FILE, str(exc))
                    try:
                        send(token, int(chat_id), PHONE_FAIL)
                    except RuntimeError:
                        pass
            finally:
                offset = next_offset
                write_text(OFFSET_FILE, str(offset))


def cmd_check() -> int:
    env = load_secrets()
    token = (env.get("TELEGRAM_BOT_TOKEN") or "").strip()
    if not token:
        print(f"missing TELEGRAM_BOT_TOKEN in {SECRETS}")
        return 1
    me = api(token, "getMe", timeout=20)
    if not me.get("ok"):
        print("telegram getMe failed")
        return 1
    username = (me.get("result") or {}).get("username")
    print(f"telegram ok  @{username}")
    user = (env.get("TELEGRAM_USER_ID") or "").strip()
    print(f"paired user  {user or '(will pair on first DM)'}")
    eleven = (env.get("ELEVENLABS_API_KEY") or "").strip()
    print(f"scribe       {'ok' if eleven else 'missing ELEVENLABS_API_KEY'}")
    grok = grok_bin()
    if not shutil.which(grok) and not Path(grok).is_file():
        print("grok missing")
        return 1
    ver = subprocess.run([grok, "--version"], capture_output=True, text=True, timeout=20)
    line = (ver.stdout or ver.stderr or "").strip().splitlines()
    print(f"grok ok      {line[0] if line else grok}")
    print(f"repo         {REPO}")
    print("check ok")
    return 0


def plist_body() -> str:
    script = REPO / "30-tools" / "desk-bridge" / "bridge.py"
    log = STATE_DIR / "bridge.log"
    err = STATE_DIR / "bridge.err"
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
    PLIST_PATH.parent.mkdir(parents=True, exist_ok=True)
    PLIST_PATH.write_text(plist_body())
    subprocess.run(["launchctl", "unload", str(PLIST_PATH)], capture_output=True)
    loaded = subprocess.run(["launchctl", "load", str(PLIST_PATH)], capture_output=True, text=True)
    if loaded.returncode != 0:
        print((loaded.stderr or loaded.stdout or "launchctl load failed").strip())
        return 1
    print(f"installed {PLIST_PATH}")
    print("DM @Rua_desk_bot on Telegram.")
    return 0


def cmd_uninstall() -> int:
    subprocess.run(["launchctl", "unload", str(PLIST_PATH)], capture_output=True)
    if PLIST_PATH.exists():
        PLIST_PATH.unlink()
    print("uninstalled")
    return 0


def main(argv: list[str]) -> int:
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
        env = load_secrets()
        token = (env.get("TELEGRAM_BOT_TOKEN") or "").strip()
        if not token:
            print(f"missing TELEGRAM_BOT_TOKEN in {SECRETS}", file=sys.stderr)
            return 1
        poll_loop(token)
        return 0
    print(f"unknown arg: {arg}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
