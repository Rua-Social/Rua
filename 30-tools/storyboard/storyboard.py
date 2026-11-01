#!/usr/bin/env python3
"""Build and recover a browser storyboard from an external project folder."""

from __future__ import annotations

import argparse
import base64
import copy
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
import math
import mimetypes
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import uuid

SOURCE = Path(__file__).resolve().parent / "src"
MISSING = object()
IMAGE_TYPES = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp"}
AUDIO_TYPES = {
    "audio/mpeg": ".mp3", "audio/mp3": ".mp3", "audio/wav": ".wav",
    "audio/x-wav": ".wav", "audio/wave": ".wav", "audio/mp4": ".m4a",
    "audio/x-m4a": ".m4a", "audio/aac": ".aac", "audio/ogg": ".ogg",
    "audio/webm": ".webm", "audio/flac": ".flac",
}


class ProjectError(ValueError):
    """An actionable project error, without a traceback in the CLI."""


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"), parse_constant=lambda v: (_ for _ in ()).throw(ValueError(v)))
    except (OSError, ValueError) as exc:
        raise ProjectError(f"Cannot read valid JSON from {path}: {exc}") from exc


def json_text(value) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def embedded_json(value) -> str:
    # Escaping '<' protects script end tags, HTML comments and all case variants.
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False).replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")


def member(root: Path, value, label: str, *, must_exist=True) -> Path:
    if not isinstance(value, str) or not value.strip() or Path(value).is_absolute():
        raise ProjectError(f"{label} must be a relative path inside the project folder.")
    path = (root / value).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ProjectError(f"{label} points outside the project folder.")
    if must_exist and not path.is_file():
        raise ProjectError(f"Missing {label}: {path}")
    return path


def positive_number(value, label: str, lower=.2, upper=600):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not lower <= value <= upper:
        raise ProjectError(f"{label} must be a finite number between {lower} and {upper}.")


def decode_data_url(value, allowed: dict, label: str):
    if not isinstance(value, str):
        raise ProjectError(f"{label} must be a base64 data URL.")
    match = re.fullmatch(r"data:([^;,]+);base64,([A-Za-z0-9+/=]+)", value)
    if not match or match[1].lower() not in allowed:
        raise ProjectError(f"{label} has an unsupported media type or encoding.")
    try:
        data = base64.b64decode(match[2], validate=True)
    except ValueError as exc:
        raise ProjectError(f"{label} has invalid base64 data.") from exc
    if not data:
        raise ProjectError(f"{label} is empty.")
    return data, allowed[match[1].lower()]


def data_url(path: Path, allowed: dict, label: str) -> str:
    mime = mimetypes.guess_type(path.name)[0]
    if mime not in allowed:
        raise ProjectError(f"{label} has an unsupported file type: {path.suffix}")
    data = path.read_bytes()
    if not data:
        raise ProjectError(f"{label} is empty: {path}")
    return f"data:{mime};base64," + base64.b64encode(data).decode("ascii")


def validate_board(board):
    if not isinstance(board, dict):
        raise ProjectError("Board must be a JSON object.")
    sequences, shots = board.get("sequences"), board.get("shots")
    if not isinstance(sequences, list) or not 1 <= len(sequences) <= 20:
        raise ProjectError("Board needs between 1 and 20 sequences.")
    if not isinstance(shots, list) or not 1 <= len(shots) <= 250:
        raise ProjectError("Board needs between 1 and 250 panels.")
    sequence_ids = set()
    for seq in sequences:
        ident = seq.get("id") if isinstance(seq, dict) else None
        if not isinstance(ident, str) or not ident.strip() or ident in sequence_ids:
            raise ProjectError("Each sequence needs a unique non-empty text ID.")
        sequence_ids.add(ident)
    shot_ids = set()
    for shot in shots:
        ident = shot.get("id") if isinstance(shot, dict) else None
        if not isinstance(ident, str) or not ident.strip() or ident in shot_ids:
            raise ProjectError("Each panel needs a unique non-empty text ID.")
        shot_ids.add(ident)
        if shot.get("sequence") not in sequence_ids:
            raise ProjectError(f"Panel {ident} refers to an unknown sequence.")
        positive_number(shot.get("duration"), f"Panel {ident} duration")
        for key in ("title", "framing", "action", "camera", "sound", "transition", "continuity", "decision", "provenance", "notes", "endTitle", "endSubtitle"):
            if shot.get(key) is not None and (not isinstance(shot[key], str) or len(shot[key]) > 30000):
                raise ProjectError(f"Panel {ident} has an invalid {key} field.")
        image_index = shot.get("imageIndex", -1)
        if isinstance(image_index, bool) or not isinstance(image_index, int) or not -1 <= image_index <= 31:
            raise ProjectError(f"Panel {ident} imageIndex must be -1 or an atlas slot from 0 to 31.")
        if shot.get("customImage") and shot.get("customImagePath"):
            raise ProjectError(f"Panel {ident} has both customImage and customImagePath; keep only one.")
        if shot.get("customImage"):
            decode_data_url(shot["customImage"], IMAGE_TYPES, f"Panel {ident} image")
    for key in ("decisions", "references", "workflow", "glossary"):
        if key in board and (not isinstance(board[key], list) or len(board[key]) > 200):
            raise ProjectError(f"Board {key} must be a list with at most 200 entries.")


def load_project(project_path: str | Path):
    path = Path(project_path).expanduser().resolve()
    if path.is_dir():
        path /= "project.json"
    manifest = read_json(path)
    if not isinstance(manifest, dict) or manifest.get("version") != 1:
        raise ProjectError("Project manifest must contain version: 1.")
    if not isinstance(manifest.get("storageKey"), str) or not manifest["storageKey"].strip():
        raise ProjectError("Project needs a stable non-empty storageKey.")
    config = manifest.get("config", {})
    if not isinstance(config, dict):
        raise ProjectError("Project config must be an object.")
    for key in ("brand", "strapline", "eyebrow", "footer", "exportPrefix", "databaseName"):
        if key in config and not isinstance(config[key], str):
            raise ProjectError(f"Project config.{key} must be text.")
    for key in ("runtimeMin", "runtimeMax"):
        if key in config:
            positive_number(config[key], f"Project config.{key}", lower=0, upper=150000)
    if config.get("runtimeMin", 0) > config.get("runtimeMax", 150000):
        raise ProjectError("Project runtimeMin exceeds runtimeMax.")
    board_path = member(path.parent, manifest.get("board"), "board")
    board = read_json(board_path)
    validate_board(board)
    assets = manifest.get("assets", {})
    if not isinstance(assets, dict) or any(not isinstance(k, str) for k in assets):
        raise ProjectError("Project assets must map text keys to relative image paths.")
    embedded_assets = {key: data_url(member(path.parent, value, f"asset {key}"), IMAGE_TYPES, f"asset {key}") for key, value in assets.items()}
    embedded_board = copy.deepcopy(board)
    for shot in embedded_board["shots"]:
        if shot.get("customImagePath"):
            shot["customImage"] = data_url(member(path.parent, shot.pop("customImagePath"), f"panel {shot['id']} image"), IMAGE_TYPES, f"panel {shot['id']} image")
        if not shot.get("customImage") and shot.get("imageIndex", -1) >= 0:
            key = "board-" + chr(ord("a") + shot["imageIndex"] // 8)
            if key not in assets:
                raise ProjectError(f"Panel {shot['id']} requires the {key} atlas.")
    audio = manifest.get("audio")
    embedded_audio = None
    if audio is not None:
        if not isinstance(audio, dict) or not isinstance(audio.get("name"), str) or not audio["name"].strip():
            raise ProjectError("Project audio must be null or an object with path and name.")
        audio_path = member(path.parent, audio.get("path"), "audio")
        embedded_audio = {"name": audio["name"], "data": data_url(audio_path, AUDIO_TYPES, "audio")}
    return path, manifest, embedded_board, embedded_assets, embedded_audio


def summary(board, audio):
    return f"{len(board['shots'])} panels / {sum(s['duration'] for s in board['shots']):g} seconds / music: {audio['name'] if audio else 'not bundled'}"


def atomic_write(path: Path, data: bytes):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix="." + path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def backup_name(path: Path, directory: Path) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    return directory / f"{path.stem}-{stamp}-{uuid.uuid4().hex[:6]}{path.suffix if path.is_file() else ''}"


def build(project_path: str | Path, output: str | Path | None = None, *, source=SOURCE):
    path, manifest, board, assets, audio = load_project(project_path)
    destination = output if output is not None else manifest.get("output")
    if not isinstance(destination, (str, Path)) or not str(destination).strip():
        raise ProjectError("Supply --output or an output path in project.json.")
    destination = Path(destination).expanduser()
    if not destination.is_absolute():
        destination = (path.parent / destination) if output is None else (Path.cwd() / destination)
    destination = destination.resolve()
    if destination.suffix.lower() != ".html":
        raise ProjectError("Build output must have an .html extension.")
    if destination.is_relative_to(path.parent) or destination.is_relative_to(Path(source).resolve()):
        raise ProjectError("Build output must be outside the project source folder and editor source folder.")
    source = Path(source)
    html = (source / "index.html").read_text(encoding="utf-8")
    config = copy.deepcopy(manifest.get("config", {}))
    revision_board = {key: value for key, value in board.items() if key not in ("sourceRevision", "savedAt", "exportedAt")}
    board["sourceRevision"] = hashlib.sha256(json_text({"board": revision_board, "assets": assets, "audio": audio, "config": config}).encode()).hexdigest()
    replacements = {
        '<script src="storyboard-data.js"></script>': '<script>' + ''.join(f"window.{key}={embedded_json(value)};" for key, value in [("STORYBOARD_STORAGE_KEY", manifest["storageKey"]), ("STORYBOARD_CONFIG", config), ("STORYBOARD_DATA", board), ("STORYBOARD_AUDIO", audio)]) + '</script>',
        '<script src="assets-data.js"></script>': '<script>window.STORYBOARD_ASSETS=' + embedded_json(assets) + ';</script>',
    }
    for name in ("styles", "video-export"):
        replacements[f'<link rel="stylesheet" href="{name}.css">'] = '<style>' + (source / f"{name}.css").read_text(encoding="utf-8") + '</style>'
    for name in ("video-engine", "video-export", "app"):
        script = (source / f"{name}.js").read_text(encoding="utf-8")
        script = re.sub(r"</script", r"<\\/script", script, flags=re.IGNORECASE)
        replacements[f'<script src="{name}.js"></script>'] = f'<script data-storyboard-{name}>' + script + '</script>'
    for marker, replacement in replacements.items():
        if html.count(marker) != 1:
            raise ProjectError(f"Editor template must contain exactly one {marker}")
        html = html.replace(marker, replacement)
    archive = None
    if destination.exists():
        if not destination.is_file():
            raise ProjectError(f"Output is not a file: {destination}")
        if destination.read_bytes() == html.encode("utf-8"):
            return destination, None, summary(board, audio) + " / output already current"
        earlier = manifest.get("earlier")
        archive_dir = (path.parent / earlier).resolve() if isinstance(earlier, str) and earlier else destination.parent / "earlier"
        archive_dir.mkdir(parents=True, exist_ok=True)
        archive = backup_name(destination, archive_dir)
        shutil.copy2(destination, archive)
    atomic_write(destination, html.encode("utf-8"))
    return destination, archive, summary(board, audio)


class ScriptReader(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.scripts = []
        self.current = None

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            self.current = []

    def handle_data(self, data):
        if self.current is not None:
            self.current.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self.current is not None:
            self.scripts.append("".join(self.current))
            self.current = None


def parse_snapshot(snapshot_path: str | Path):
    path = Path(snapshot_path)
    raw = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json" or raw.lstrip().startswith("{"):
        board = json.loads(raw)
        if isinstance(board, dict) and "project" in board:
            board = board["project"]
        validate_board(board)
        return board, None, MISSING
    parser = ScriptReader()
    parser.feed(raw)
    assignments = {}
    pattern = re.compile(r"window\.(STORYBOARD_(?:STORAGE_KEY|CONFIG|DATA|ASSETS|AUDIO))\s*=\s*")
    decoder = json.JSONDecoder()
    for script in parser.scripts:
        rest = script.strip()
        if not pattern.match(rest):
            continue
        while rest:
            match = pattern.match(rest)
            if not match:
                raise ProjectError("Snapshot data script contains non-JSON code; use Save complete project.")
            try:
                value, end = decoder.raw_decode(rest[match.end():])
            except ValueError as exc:
                raise ProjectError("Snapshot has invalid embedded project JSON.") from exc
            name = match[1]
            if name in assignments:
                raise ProjectError(f"Snapshot contains duplicate {name} data.")
            assignments[name] = value
            rest = rest[match.end() + end:].lstrip()
            if rest.startswith(";"):
                rest = rest[1:].lstrip()
            elif rest:
                raise ProjectError("Snapshot data needs a semicolon between JSON assignments.")
    if "STORYBOARD_DATA" not in assignments:
        raise ProjectError("No embedded storyboard found. Choose the complete-project HTML or exported JSON.")
    board = assignments["STORYBOARD_DATA"]
    validate_board(board)
    assets = assignments.get("STORYBOARD_ASSETS")
    if assets is not None and not isinstance(assets, dict):
        raise ProjectError("Snapshot assets must be an object.")
    return board, assets, assignments.get("STORYBOARD_AUDIO", MISSING)


def write_media(stage: Path, data, allowed, folder: str, label: str):
    payload, extension = decode_data_url(data, allowed, label)
    relative = f"{folder}/{hashlib.sha256(payload).hexdigest()}{extension}"
    target = stage / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(payload)
    return relative


def import_snapshot(snapshot_path, project_path, *, clear_audio=False, expected_panels=None):
    path, manifest, _, _, _ = load_project(project_path)
    board, assets, audio = parse_snapshot(snapshot_path)
    if expected_panels is not None and len(board["shots"]) != expected_panels:
        raise ProjectError(f"Snapshot has {len(board['shots'])} panels; expected {expected_panels}. Project was not changed.")
    root = path.parent
    if path.name != "project.json":
        raise ProjectError("Import requires the project manifest to be named project.json.")
    if any(item.is_symlink() for item in root.rglob("*")):
        raise ProjectError("Import cannot safely back up a project containing symlinks.")
    archive_dir = root.parent / "earlier"
    if archive_dir.resolve().is_relative_to(root):
        raise ProjectError("The earlier-versions folder cannot be inside the project source folder.")
    staging = Path(tempfile.mkdtemp(prefix=".storyboard-import-", dir=root.parent))
    backup = None
    audio_note = "existing music preserved (snapshot contains no soundtrack)"
    try:
        shutil.copytree(root, staging, dirs_exist_ok=True)
        updated = copy.deepcopy(manifest)
        if assets is not None:
            for key, data in assets.items():
                if not isinstance(key, str):
                    raise ProjectError("Snapshot asset keys must be text.")
                updated.setdefault("assets", {})[key] = write_media(staging, data, IMAGE_TYPES, "assets/imported", f"Asset {key}")
        for shot in board["shots"]:
            if shot.get("customImagePath"):
                raise ProjectError("Browser snapshots must embed replacement images, not reference local paths.")
            if shot.get("customImage"):
                shot["customImagePath"] = write_media(staging, shot.pop("customImage"), IMAGE_TYPES, "assets/imported", f"Panel {shot['id']} image")
        if clear_audio:
            updated["audio"] = None
            audio_note = "music cleared by --clear-audio"
        elif audio is not MISSING and audio is not None:
            if not isinstance(audio, dict) or not isinstance(audio.get("name"), str) or not audio["name"].strip():
                raise ProjectError("Snapshot audio needs a name and embedded data.")
            updated["audio"] = {"name": audio["name"], "path": write_media(staging, audio.get("data"), AUDIO_TYPES, "audio/imported", "Soundtrack")}
            audio_note = "snapshot soundtrack imported"
        # Identity/config remain with this project, not the exported snapshot's new browser key.
        updated["lastImport"] = {"at": datetime.now(timezone.utc).isoformat(), "snapshot": Path(snapshot_path).name, "sha256": hashlib.sha256(Path(snapshot_path).read_bytes()).hexdigest()}
        member(staging, updated["board"], "board").write_text(json_text(board), encoding="utf-8")
        (staging / path.name).write_text(json_text(updated), encoding="utf-8")
        _, _, verified_board, _, verified_audio = load_project(staging / path.name)
        archive_dir.mkdir(parents=True, exist_ok=True)
        backup = backup_name(root, archive_dir)
        shutil.copytree(root, backup)
        # Rename the validated directory as one unit; leave a complete recovery copy.
        displaced = root.parent / ("." + root.name + "-replaced-" + uuid.uuid4().hex)
        os.replace(root, displaced)
        try:
            os.replace(staging, root)
        except BaseException:
            os.replace(displaced, root)
            raise
        shutil.rmtree(displaced)
        return backup, summary(verified_board, verified_audio) + " / " + audio_note
    finally:
        if staging.exists():
            shutil.rmtree(staging)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="rua storyboard", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    check_cmd = sub.add_parser("check", help="validate project data, image paths and soundtrack")
    check_cmd.add_argument("project", help="external project.json or project directory")
    build_cmd = sub.add_parser("build", help="build a standalone HTML; back up an existing output")
    build_cmd.add_argument("project")
    build_cmd.add_argument("--output", help="override project.output")
    import_cmd = sub.add_parser("import", help="save a browser export back into the disk project with a backup")
    import_cmd.add_argument("snapshot", help="complete-project HTML or JSON export")
    import_cmd.add_argument("--project", required=True)
    import_cmd.add_argument("--expected-panels", type=int, help="refuse an unexpected panel count")
    import_cmd.add_argument("--clear-audio", action="store_true", help="explicitly remove the project's soundtrack")
    args = parser.parse_args(argv)
    try:
        if args.command == "check":
            path, _, board, _, audio = load_project(args.project)
            print(f"Verified {path}\n{summary(board, audio)}")
        elif args.command == "build":
            path, backup, report = build(args.project, args.output)
            print(f"Built {path}\n{report}")
            if backup:
                print(f"Previous output: {backup}")
        else:
            backup, report = import_snapshot(args.snapshot, args.project, clear_audio=args.clear_audio, expected_panels=args.expected_panels)
            print(f"Imported into {Path(args.project).resolve()}\n{report}\nPrevious project: {backup}\nRun build to update the standalone HTML.")
    except (ProjectError, OSError, ValueError) as exc:
        print(f"Storyboard: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
