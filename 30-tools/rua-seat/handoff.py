"""Provider-neutral handoff storage and result validation. No model SDK required."""
from __future__ import annotations

import json
import os
from pathlib import Path
import sqlite3
import stat
import time

SCHEMA_PATH = Path(__file__).resolve().with_name("result.schema.json")
SCHEMA = json.loads(SCHEMA_PATH.read_text())
MAX_OUTPUT = 1024 * 1024
MAX_DEPTH = 3
MAX_RUNS = 12


def validate(value, schema=SCHEMA):
    """Validate the deliberately small subset used by the shipped schema.

    The JSON schema is authoritative, including required keys and enums.
    Unsupported schema keywords/types fail closed instead of being ignored.
    """
    allowed = {"type", "properties", "required", "additionalProperties", "items", "enum"}
    if set(schema) - allowed:
        raise ValueError("Unsupported result schema keyword")
    kind = schema["type"]
    if kind == "object":
        if not isinstance(value, dict):
            raise ValueError("Expected object")
        if set(value) != set(schema["required"]) or schema["additionalProperties"] is not False:
            raise ValueError("Unexpected or missing result fields")
        for key, item in value.items():
            validate(item, schema["properties"][key])
    elif kind == "array":
        if not isinstance(value, list):
            raise ValueError("Expected array")
        for item in value:
            validate(item, schema["items"])
    elif kind == "string":
        if not isinstance(value, str):
            raise ValueError("Expected string")
    else:
        raise ValueError("Unsupported result schema type")
    if "enum" in schema and value not in schema["enum"]:
        raise ValueError("Invalid result status")


def parse_result(raw):
    def unique_keys(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate result field")
            result[key] = value
        return result

    result = json.loads(raw, object_pairs_hook=unique_keys)
    validate(result)
    if not result["summary"].strip():
        raise ValueError("Result summary is empty")
    if result["status"] == "completed" and result["blockers"]:
        raise ValueError("Completed result contains blockers")
    if result["status"] in ("blocked", "refused", "incomplete") and not result["blockers"]:
        raise ValueError("Unfinished result needs a reason")
    return result


def load_context(path):
    if path is None:
        return {"project_ref": None, "source_refs": [], "accepted_decisions": [], "authorization": ""}
    if path.stat().st_size > 65536:
        raise ValueError("Context file exceeds 64 KiB")
    value = json.loads(path.read_text())
    expected = {"project_ref", "source_refs", "accepted_decisions", "authorization"}
    if not isinstance(value, dict) or set(value) != expected:
        raise ValueError("Context must contain project_ref, source_refs, accepted_decisions, authorization")
    if value["project_ref"] is not None and not isinstance(value["project_ref"], str):
        raise ValueError("Invalid project reference")
    if not isinstance(value["authorization"], str):
        raise ValueError("Invalid authorization context")
    for key in ("source_refs", "accepted_decisions"):
        if not isinstance(value[key], list) or any(not isinstance(x, str) for x in value[key]):
            raise ValueError("Context references and decisions must be string arrays")
    return value


class Ledger:
    def __init__(self):
        default = Path(os.environ.get("XDG_STATE_HOME", str(Path.home() / ".local/state"))) / "rua/handoffs"
        directory = Path(os.environ.get("RUA_HANDOFF_DIR", str(default))).expanduser()
        # Client-bearing execution records never belong in Git.
        resolved = directory.resolve()
        if any((p / ".git").exists() for p in (resolved, *resolved.parents)):
            raise ValueError("Handoff storage must be outside Git")
        if directory.is_symlink():
            raise ValueError("Handoff storage must not be a symlink")
        directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        info = directory.stat()
        if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) & 0o077:
            raise ValueError("Handoff directory must be owner-only (0700)")
        self.directory = directory.resolve()
        db = directory / "jobs.sqlite3"
        if db.is_symlink():
            raise ValueError("Handoff database must not be a symlink")
        fd = os.open(db, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        try:
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) & 0o077:
                raise ValueError("Handoff database must be an owner-only regular file")
        finally:
            os.close(fd)
        self.db = sqlite3.connect(db, timeout=10)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, root TEXT NOT NULL, record TEXT NOT NULL)")
        self.db.commit()

    def get(self, job_id):
        row = self.db.execute("SELECT record FROM jobs WHERE id=?", (job_id,)).fetchone()
        return json.loads(row[0]) if row else None

    def start(self, record):
        self.db.execute("BEGIN IMMEDIATE")
        try:
            existing = self.get(record["job_id"])
            if existing:
                if existing["request"] != record["request"] or existing["owner"] != record["owner"]:
                    raise ValueError("Job ID already belongs to a different request")
                self.db.commit()
                return existing
            count = self.db.execute("SELECT COUNT(*) FROM jobs WHERE root=?", (record["root_id"],)).fetchone()[0]
            if count >= MAX_RUNS:
                raise ValueError("Handoff tree reached its run limit")
            self.db.execute("INSERT INTO jobs VALUES (?, ?, ?)", (record["job_id"], record["root_id"], json.dumps(record)))
            self.db.commit()
            return None
        except BaseException:
            self.db.rollback()
            raise

    def finish(self, record):
        record["finished_at"] = time.time()
        self.db.execute("UPDATE jobs SET record=? WHERE id=?", (json.dumps(record), record["job_id"]))
        self.db.commit()

    def close(self):
        self.db.close()
