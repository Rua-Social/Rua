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


def load_project(project_path: str | Path, *, manifest=MISSING, board=MISSING):
    """Load and validate a project, or proposed changes before they replace disk data."""
    path = Path(project_path).expanduser().resolve()
    if path.is_dir():
        path /= "project.json"
    if manifest is MISSING:
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
    if board is MISSING:
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


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:48] or "version"


def read_versions(project_dir: Path) -> list:
    path = project_dir / "versions.json"
    if not path.exists():
        return []
    data = read_json(path)
    entries = data.get("versions") if isinstance(data, dict) else None
    if not isinstance(entries, list) or any(not isinstance(e, dict) or not isinstance(e.get("n"), int) for e in entries):
        raise ProjectError(f"{path} must contain a versions list with numbered entries.")
    return entries


def versions_for_page(entries: list) -> list:
    # Only the newest entry is the current file; an earlier entry without a kept file has no link.
    page = []
    for index, entry in enumerate(entries):
        item = {"n": entry["n"], "label": entry.get("label", ""), "date": str(entry.get("builtAt", ""))[:10]}
        if index == len(entries) - 1:
            item["current"] = True
        elif entry.get("file"):
            item["href"] = Path(entry["file"]).as_uri()
        page.append(item)
    return page


# Browser bookkeeping that never changes what the board is.
VOLATILE_KEYS = ("sourceRevision", "savedAt", "exportedAt", "edited", "keptAt")


def source_revision(board, assets, audio, config) -> str:
    revision_board = {key: value for key, value in board.items() if key not in VOLATILE_KEYS}
    return hashlib.sha256(json_text({"board": revision_board, "assets": assets, "audio": audio, "config": config}).encode()).hexdigest()


def render_page(manifest, board, assets, audio, versions, *, source=SOURCE, studio=None) -> str:
    """Assemble the single-file editor page. `studio` is set only when served by `storyboard open`."""
    source = Path(source)
    html = (source / "index.html").read_text(encoding="utf-8")
    values = [("STORYBOARD_STORAGE_KEY", manifest["storageKey"]), ("STORYBOARD_CONFIG", copy.deepcopy(manifest.get("config", {}))),
              ("STORYBOARD_DATA", board), ("STORYBOARD_AUDIO", audio), ("STORYBOARD_VERSIONS", versions)]
    if studio is not None:
        values.append(("STORYBOARD_STUDIO", studio))
    replacements = {
        '<script src="storyboard-data.js"></script>': '<script>' + ''.join(f"window.{key}={embedded_json(value)};" for key, value in values) + '</script>',
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
    return html


def output_path(path: Path, manifest) -> Path | None:
    value = manifest.get("output")
    if not isinstance(value, str) or not value.strip():
        return None
    destination = Path(value).expanduser()
    return (destination if destination.is_absolute() else path.parent / destination).resolve()


def free_name(path: Path) -> Path:
    candidate, count = path, 2
    while candidate.exists():
        candidate = path.with_name(f"{path.stem}-{count}{path.suffix}")
        count += 1
    return candidate


def build(project_path: str | Path, output: str | Path | None = None, *, source=SOURCE, label: str | None = None):
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
    config = copy.deepcopy(manifest.get("config", {}))
    for key in VOLATILE_KEYS:
        board.pop(key, None)
    board["sourceRevision"] = source_revision(board, assets, audio, config)
    # Versions are tracked for the project's own output, including --output naming that same file.
    tracked = output is None or destination == output_path(path, manifest)
    entries = copy.deepcopy(read_versions(path.parent)) if tracked else []
    last = entries[-1] if entries else None
    new_version = tracked and (last is None or last.get("sourceRevision") != board["sourceRevision"])
    archive_dir = (path.parent / manifest["earlier"]).resolve() if isinstance(manifest.get("earlier"), str) and manifest["earlier"] else destination.parent / "earlier"
    archive_target = None
    if new_version:
        prefix = slug(str(config.get("exportPrefix") or path.parent.name))
        if last is None and destination.is_file():
            stamp = datetime.fromtimestamp(destination.stat().st_mtime, timezone.utc)
            last = {"n": 1, "label": "Earlier build", "builtAt": stamp.isoformat(timespec="seconds"), "sourceRevision": None}
            entries.append(last)
        if last is not None and destination.is_file():
            archive_target = free_name(archive_dir / f"{str(last.get('builtAt', ''))[:10]}_{prefix}-v{last['n']:02d}-{slug(last.get('label', ''))}.html")
            last["file"] = str(archive_target)
        entries.append({"n": (last["n"] + 1) if last else 1, "label": label or "Untitled",
                        "builtAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                        "sourceRevision": board["sourceRevision"], "panels": len(board["shots"]),
                        "seconds": sum(s["duration"] for s in board["shots"]), "music": audio["name"] if audio else None})
    elif tracked and label:
        last["label"] = label
    html = render_page(manifest, board, assets, audio, versions_for_page(entries) if tracked else None, source=source)
    archive = None
    if destination.exists():
        if not destination.is_file():
            raise ProjectError(f"Output is not a file: {destination}")
        if destination.read_bytes() == html.encode("utf-8"):
            return destination, None, summary(board, audio) + " / output already current"
        # Every replaced output is archived. A new version gets its numbered name; a rebuild of the
        # same board (editor or label change only) still keeps the previous HTML under a dated name.
        archive_dir.mkdir(parents=True, exist_ok=True)
        archive = archive_target or backup_name(destination, archive_dir)
        shutil.copy2(destination, archive)
    atomic_write(destination, html.encode("utf-8"))
    report = summary(board, audio)
    if tracked:
        atomic_write(path.parent / "versions.json", json_text({"versions": entries}).encode("utf-8"))
        report += f" / version {entries[-1]['n']}: {entries[-1].get('label', '')}"
    return destination, archive, report


def list_versions(project_path) -> str:
    path, _, _, _, _ = load_project(project_path)
    entries = read_versions(path.parent)
    if not entries:
        return "No versions recorded yet. The next build starts the list."
    lines = []
    for entry in reversed(entries):
        where = "current file" if entry is entries[-1] else entry.get("file") or "file not kept"
        lines.append(f"v{entry['n']:<3} {str(entry.get('builtAt', ''))[:16].replace('T', ' ')}  {entry.get('label', '')}\n      {where}")
    return "\n".join(lines)


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
    pattern = re.compile(r"window\.(STORYBOARD_(?:STORAGE_KEY|CONFIG|DATA|ASSETS|AUDIO|VERSIONS))\s*=\s*")
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
    build_cmd.add_argument("--output", help="override project.output (a review copy; not recorded as a version)")
    build_cmd.add_argument("--label", help="name this version, for example \"wreath added\"")
    import_cmd = sub.add_parser("import", help="save a browser export back into the disk project with a backup")
    import_cmd.add_argument("snapshot", help="complete-project HTML or JSON export")
    import_cmd.add_argument("--project", required=True)
    import_cmd.add_argument("--expected-panels", type=int, help="refuse an unexpected panel count")
    import_cmd.add_argument("--clear-audio", action="store_true", help="explicitly remove the project's soundtrack")
    save_cmd = sub.add_parser("save", help="import a browser export, then build it as a new named version")
    save_cmd.add_argument("snapshot", help="complete-project HTML or JSON export")
    save_cmd.add_argument("--project", required=True)
    save_cmd.add_argument("--label", required=True, help="name this version")
    save_cmd.add_argument("--expected-panels", type=int, help="refuse an unexpected panel count")
    versions_cmd = sub.add_parser("versions", help="list the project's numbered versions and where each file is")
    versions_cmd.add_argument("project")
    open_cmd = sub.add_parser("open", help="open the Storyboard app in the browser; edits save to the project on disk")
    open_cmd.add_argument("project", nargs="?", help="project.json to open (omit for the home page)")
    serve_cmd = sub.add_parser("serve", help="run the Storyboard app server in this terminal")
    serve_cmd.add_argument("--port", type=int, default=None)
    args = parser.parse_args(argv)
    if args.command in ("open", "serve"):
        import studio
        try:
            if args.command == "serve":
                studio.serve(args.port or studio.PORT)
            else:
                print(f"Storyboard is open at {studio.open_studio(args.project)}")
            return 0
        except (ProjectError, studio.sb.ProjectError) as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
    try:
        if args.command == "check":
            path, _, board, _, audio = load_project(args.project)
            print(f"Verified {path}\n{summary(board, audio)}")
        elif args.command == "build":
            path, backup, report = build(args.project, args.output, label=args.label)
            print(f"Built {path}\n{report}")
            if backup:
                print(f"Previous output: {backup}")
        elif args.command == "versions":
            print(list_versions(args.project))
        elif args.command == "save":
            backup, report = import_snapshot(args.snapshot, args.project, expected_panels=args.expected_panels)
            path, previous, built = build(args.project, label=args.label)
            print(f"Imported {Path(args.snapshot).name}\n{report}\nPrevious project: {backup}\nBuilt {path}\n{built}")
            if previous:
                print(f"Previous output: {previous}")
        else:
            backup, report = import_snapshot(args.snapshot, args.project, clear_audio=args.clear_audio, expected_panels=args.expected_panels)
            print(f"Imported into {Path(args.project).resolve()}\n{report}\nPrevious project: {backup}\nRun build to update the standalone HTML.")
    except (ProjectError, OSError, ValueError) as exc:
        print(f"Storyboard: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
