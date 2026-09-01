#!/usr/bin/env python3
"""Offline boundary tests for rua vault. Synthetic fixtures only."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("rua")
REF_A = "rec-northwind-context"
REF_B = "rec-contoso-context"
LABEL_A = "Northwind Traders context"
LABEL_B = "Contoso Ltd context"
ALIAS_A = "North Wind"
PAYLOAD_A = "Northwind retainer is 111 units.\n"
PAYLOAD_B = "Contoso sprint is 222 units.\n"


class RuaVaultTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.outside = self.root / "outside"
        self.outside.mkdir()
        self.payload_a = self.outside / "northwind.md"
        self.payload_b = self.outside / "contoso.md"
        self.payload_a.write_text(PAYLOAD_A, encoding="utf-8")
        self.payload_b.write_text(PAYLOAD_B, encoding="utf-8")
        self.manifest_dir = self.outside / "config"
        self.manifest_dir.mkdir()
        self.manifest = self.manifest_dir / "manifest.json"
        self._write_manifest()
        self.env = os.environ.copy()
        self.env["RUA_VAULT_MANIFEST"] = str(self.manifest)

    def _write_manifest(self, entries=None, version=1) -> None:
        if entries is None:
            entries = [
                {
                    "ref": REF_A,
                    "label": LABEL_A,
                    "aliases": [ALIAS_A],
                    "uri": self.payload_a.resolve().as_uri(),
                    "sha256": hashlib.sha256(PAYLOAD_A.encode()).hexdigest(),
                },
                {
                    "ref": REF_B,
                    "label": LABEL_B,
                    "aliases": [],
                    "uri": self.payload_b.resolve().as_uri(),
                    "sha256": hashlib.sha256(PAYLOAD_B.encode()).hexdigest(),
                },
            ]
        self.manifest.write_text(
            json.dumps({"version": version, "entries": entries}),
            encoding="utf-8",
        )
        os.chmod(self.manifest_dir, 0o700)
        os.chmod(self.manifest, 0o600)

    def run_vault(self, *args: str, env=None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(SCRIPT), *args],
            text=True,
            capture_output=True,
            env=env or self.env,
            check=False,
        )

    def test_help_exits_zero(self) -> None:
        result = self.run_vault("vault", "--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("search", result.stdout)
        self.assertIn("get", result.stdout)

    def test_unknown_subcommand_is_invalid(self) -> None:
        result = self.run_vault("vault", "list")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("invalid command", result.stderr.lower())

    def test_missing_manifest_is_unavailable(self) -> None:
        env = {**self.env, "RUA_VAULT_MANIFEST": str(self.outside / "missing.json")}
        result = self.run_vault("vault", "search", "northwind", env=env)
        self.assertEqual(result.returncode, 3)
        self.assertEqual(result.stdout, "")
        self.assertIn("vault unavailable", result.stderr.lower())
        self.assertNotIn(str(self.outside), result.stderr)

    def test_manifest_inside_git_is_unavailable(self) -> None:
        repo = self.root / "repo"
        repo.mkdir()
        subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
        git_manifest = repo / "manifest.json"
        git_manifest.write_text(self.manifest.read_text(encoding="utf-8"), encoding="utf-8")
        os.chmod(git_manifest, 0o600)
        env = {**self.env, "RUA_VAULT_MANIFEST": str(git_manifest)}
        result = self.run_vault("vault", "search", "northwind", env=env)
        self.assertEqual(result.returncode, 3)
        self.assertEqual(result.stdout, "")

    def test_world_readable_manifest_is_unavailable(self) -> None:
        os.chmod(self.manifest, 0o644)
        result = self.run_vault("vault", "search", "northwind")
        self.assertEqual(result.returncode, 3)
        self.assertEqual(result.stdout, "")

    def test_wrong_version_is_unavailable(self) -> None:
        self._write_manifest(version=2)
        result = self.run_vault("vault", "search", "northwind")
        self.assertEqual(result.returncode, 3)

    def test_duplicate_refs_are_unavailable(self) -> None:
        entry = {
            "ref": REF_A,
            "label": LABEL_A,
            "aliases": [],
            "uri": self.payload_a.resolve().as_uri(),
            "sha256": hashlib.sha256(PAYLOAD_A.encode()).hexdigest(),
        }
        self._write_manifest(entries=[entry, dict(entry)])
        result = self.run_vault("vault", "search", "northwind")
        self.assertEqual(result.returncode, 3)

    def test_search_matches_label_case_insensitively(self) -> None:
        result = self.run_vault("vault", "search", "NORTHWIND")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, f"{REF_A}\t{LABEL_A}\n")

    def test_search_matches_alias(self) -> None:
        result = self.run_vault("vault", "search", "north wind")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(REF_A, result.stdout)

    def test_search_is_deterministic(self) -> None:
        extra = self.outside / "northwind-alt.md"
        extra.write_text("alt\n", encoding="utf-8")
        self._write_manifest(
            entries=[
                {
                    "ref": "rec-z",
                    "label": "Northwind Z",
                    "aliases": [],
                    "uri": extra.resolve().as_uri(),
                    "sha256": hashlib.sha256(b"alt\n").hexdigest(),
                },
                {
                    "ref": REF_A,
                    "label": LABEL_A,
                    "aliases": [],
                    "uri": self.payload_a.resolve().as_uri(),
                    "sha256": hashlib.sha256(PAYLOAD_A.encode()).hexdigest(),
                },
            ]
        )
        result = self.run_vault("vault", "search", "northwind")
        self.assertEqual(result.returncode, 0)
        lines = [line for line in result.stdout.splitlines() if line]
        self.assertEqual(lines[0].split("\t")[0], REF_A)
        self.assertEqual(lines[1].split("\t")[0], "rec-z")

    def test_search_does_not_read_payload(self) -> None:
        os.chmod(self.payload_a, 0)
        result = self.run_vault("vault", "search", "northwind")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(REF_A, result.stdout)
        os.chmod(self.payload_a, 0o600)

    def test_search_output_has_no_uri_or_hash(self) -> None:
        result = self.run_vault("vault", "search", "northwind")
        self.assertEqual(result.returncode, 0)
        self.assertNotIn("file://", result.stdout + result.stderr)
        self.assertNotIn("sha256", result.stdout + result.stderr)
        self.assertNotIn(PAYLOAD_A.strip(), result.stdout)

    def test_search_miss_is_missing(self) -> None:
        result = self.run_vault("vault", "search", "zzz-unknown")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("record missing", result.stderr.lower())

    def test_short_query_is_invalid(self) -> None:
        result = self.run_vault("vault", "search", "ab")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")

    def test_get_unknown_ref_is_missing(self) -> None:
        result = self.run_vault("vault", "get", "no-such-ref")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")

    def test_get_returns_payload(self) -> None:
        result = self.run_vault("vault", "get", REF_A)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, PAYLOAD_A)

    def test_json_search_and_get_schemas(self) -> None:
        search = self.run_vault("vault", "search", "--json", "northwind")
        self.assertEqual(search.returncode, 0, search.stderr)
        self.assertEqual(
            json.loads(search.stdout),
            {"matches": [{"ref": REF_A, "label": LABEL_A}]},
        )
        got = self.run_vault("vault", "get", "--json", REF_A)
        self.assertEqual(got.returncode, 0, got.stderr)
        body = json.loads(got.stdout)
        self.assertEqual(body["ref"], REF_A)
        self.assertEqual(body["label"], LABEL_A)
        self.assertEqual(body["content"], PAYLOAD_A)
        self.assertEqual(body["sha256"], hashlib.sha256(PAYLOAD_A.encode()).hexdigest())
        self.assertNotIn("uri", body)

    def test_missing_source_is_unavailable(self) -> None:
        self.payload_a.unlink()
        result = self.run_vault("vault", "get", REF_A)
        self.assertEqual(result.returncode, 4)
        self.assertEqual(result.stdout, "")
        self.assertIn("source unavailable", result.stderr.lower())
        self.assertNotIn("northwind.md", result.stderr)

    def test_source_inside_git_is_unavailable(self) -> None:
        repo = self.root / "payload-repo"
        repo.mkdir()
        subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
        inner = repo / "record.md"
        inner.write_text(PAYLOAD_A, encoding="utf-8")
        self._write_manifest(
            entries=[
                {
                    "ref": REF_A,
                    "label": LABEL_A,
                    "aliases": [],
                    "uri": inner.resolve().as_uri(),
                    "sha256": hashlib.sha256(PAYLOAD_A.encode()).hexdigest(),
                }
            ]
        )
        result = self.run_vault("vault", "get", REF_A)
        self.assertEqual(result.returncode, 4)
        self.assertEqual(result.stdout, "")

    def test_unsupported_scheme_is_unavailable(self) -> None:
        self._write_manifest(
            entries=[
                {
                    "ref": REF_A,
                    "label": LABEL_A,
                    "aliases": [],
                    "uri": "https://example.invalid/record.md",
                    "sha256": hashlib.sha256(PAYLOAD_A.encode()).hexdigest(),
                }
            ]
        )
        result = self.run_vault("vault", "get", REF_A)
        self.assertEqual(result.returncode, 4)
        self.assertEqual(result.stdout, "")

    def test_checksum_mismatch_emits_no_payload(self) -> None:
        self._write_manifest(
            entries=[
                {
                    "ref": REF_A,
                    "label": LABEL_A,
                    "aliases": [],
                    "uri": self.payload_a.resolve().as_uri(),
                    "sha256": "0" * 64,
                }
            ]
        )
        result = self.run_vault("vault", "get", REF_A)
        self.assertEqual(result.returncode, 5)
        self.assertEqual(result.stdout, "")
        self.assertIn("record invalid", result.stderr.lower())
        self.assertNotIn("111 units", result.stderr)

    def test_invalid_utf8_is_invalid(self) -> None:
        bad = self.outside / "bad.md"
        bad.write_bytes(b"\xff\xfe")
        self._write_manifest(
            entries=[
                {
                    "ref": REF_A,
                    "label": LABEL_A,
                    "aliases": [],
                    "uri": bad.resolve().as_uri(),
                    "sha256": hashlib.sha256(b"\xff\xfe").hexdigest(),
                }
            ]
        )
        result = self.run_vault("vault", "get", REF_A)
        self.assertEqual(result.returncode, 5)
        self.assertEqual(result.stdout, "")

    def test_symlink_payload_is_rejected(self) -> None:
        link = self.outside / "link.md"
        link.symlink_to(self.payload_a)
        self._write_manifest(
            entries=[
                {
                    "ref": REF_A,
                    "label": LABEL_A,
                    "aliases": [],
                    "uri": link.resolve().parent.joinpath("link.md").as_uri()
                    if False
                    else Path(os.path.join(self.outside, "link.md")).absolute().as_uri(),
                    "sha256": hashlib.sha256(PAYLOAD_A.encode()).hexdigest(),
                }
            ]
        )
        # Keep the URI pointing at the symlink path, not the resolved target.
        data = json.loads(self.manifest.read_text(encoding="utf-8"))
        data["entries"][0]["uri"] = Path(link).absolute().as_uri()
        self.manifest.write_text(json.dumps(data), encoding="utf-8")
        os.chmod(self.manifest, 0o600)
        result = self.run_vault("vault", "get", REF_A)
        self.assertEqual(result.returncode, 4)
        self.assertEqual(result.stdout, "")

    def test_default_manifest_env_override(self) -> None:
        env = {**self.env}
        env.pop("RUA_VAULT_MANIFEST", None)
        env["XDG_CONFIG_HOME"] = str(self.root / "xdg")
        result = self.run_vault("vault", "search", "northwind", env=env)
        self.assertEqual(result.returncode, 3)
        self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
