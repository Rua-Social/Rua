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
        self.payload_a.chmod(0o600)
        self.payload_b.chmod(0o600)
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
        bad.chmod(0o600)
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

    def replace_payload(self, content: bytes) -> None:
        self.payload_a.write_bytes(content)
        data = json.loads(self.manifest.read_text())
        data["entries"][0]["sha256"] = hashlib.sha256(content).hexdigest()
        self._write_manifest(entries=data["entries"])

    def assert_private_failure(self, result, code) -> None:
        self.assertEqual(result.returncode, code, result.stderr)
        self.assertEqual(result.stdout, "")
        for private in [LABEL_A, str(self.outside), "111 units", "Traceback"]:
            self.assertNotIn(private, result.stderr)

    def test_large_record_requires_explicit_limit_and_small_output(self) -> None:
        content = ("é" * 100 + "\n").encode() * 6000
        self.replace_payload(content)
        self.assert_private_failure(self.run_vault("vault", "get", REF_A), 4)
        self.assert_private_failure(self.run_vault("vault", "get", REF_A,
                                    "--max-bytes", "2097152"), 4)
        self.assert_private_failure(self.run_vault("vault", "get", REF_A,
                                    "--lines", "1:2"), 4)
        sliced = self.run_vault("vault", "get", REF_A, "--max-bytes", "2097152",
                                "--lines", "2:3", "--json")
        self.assertEqual(sliced.returncode, 0, sliced.stderr)
        result = json.loads(sliced.stdout)
        self.assertEqual(result["content"], ("é" * 100 + "\n") * 2)
        self.assertEqual(result["sha256"], hashlib.sha256(content).hexdigest())
        self.assertEqual(result["lines"], {"start": 2, "end": 3})

    def test_slice_checks_hash_of_unreturned_content(self) -> None:
        self.replace_payload(b"first\nsecond\n")
        self.payload_a.write_bytes(b"first\nchanged\n")
        self.assert_private_failure(self.run_vault("vault", "get", REF_A,
                                    "--lines", "1:1"), 5)

    def test_slice_checks_utf8_of_unreturned_content(self) -> None:
        self.replace_payload(b"first\n\xff\n")
        self.assert_private_failure(self.run_vault("vault", "get", REF_A,
                                    "--lines", "1:1"), 5)

    def test_line_bounds_and_final_unterminated_line(self) -> None:
        self.replace_payload(b"first\nsecond")
        result = self.run_vault("vault", "get", REF_A, "--lines", "2:2")
        self.assertEqual(result.stdout, "second")
        self.assertEqual(result.returncode, 0)
        for value in ["0:1", "2:1", "1:3", "1", "-1:2", "a:b", "1:2:3"]:
            with self.subTest(value=value):
                self.assert_private_failure(self.run_vault("vault", "get", REF_A,
                                            "--lines=" + value), 2)

    def test_record_limit_has_hard_ceiling(self) -> None:
        for value in ["0", "-1", "16777217", "not-a-number"]:
            with self.subTest(value=value):
                self.assert_private_failure(self.run_vault("vault", "get", REF_A,
                                            "--max-bytes", value), 2)
        self.replace_payload(b"x" * (16777216 + 1))
        self.assert_private_failure(self.run_vault("vault", "get", REF_A,
                                    "--max-bytes", "16777216", "--lines", "1:1"), 4)
        checked = self.run_vault("vault", "check", REF_A, "--json")
        self.assertEqual(checked.returncode, 4)
        self.assertEqual(json.loads(checked.stdout)["records"][0]["reason"], "read_limit_exceeded")

    def test_selected_output_has_byte_ceiling(self) -> None:
        self.replace_payload(("é" * 600000 + "\nsmall\n").encode())
        result = self.run_vault("vault", "get", REF_A, "--max-bytes", "2097152",
                                "--lines", "1:1")
        self.assert_private_failure(result, 4)

    def test_character_slice_retrieves_a_large_single_line_without_splitting_utf8(self) -> None:
        self.replace_payload(("é" * 600000).encode())
        result = self.run_vault("vault", "get", REF_A, "--max-bytes", "2097152",
                                "--chars", "599999:600000", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        body = json.loads(result.stdout)
        self.assertEqual(body["content"], "éé")
        self.assertEqual(body["chars"], {"start": 599999, "end": 600000})
        self.assertNotIn("lines", body)
        for args in [("--chars", "600000:600001"), ("--chars", "0:1"),
                     ("--chars", "1:1", "--lines", "1:1")]:
            self.assert_private_failure(self.run_vault("vault", "get", REF_A,
                                        "--max-bytes", "2097152", *args), 2)

    def test_private_payload_permissions_required(self) -> None:
        for mode in [0o644, 0o640, 0o000]:
            with self.subTest(mode=mode):
                self.payload_a.chmod(mode)
                self.assert_private_failure(self.run_vault("vault", "get", REF_A), 4)
        self.payload_a.chmod(0o600)

    def test_health_reports_only_refs_status_and_reason(self) -> None:
        result = self.run_vault("vault", "check", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {"records": [
            {"ref": REF_A, "status": "ok", "reason": "verified"},
            {"ref": REF_B, "status": "ok", "reason": "verified"},
        ]})
        self.payload_a.unlink()
        result = self.run_vault("vault", "check", "--json")
        self.assertEqual(result.returncode, 4)
        rows = json.loads(result.stdout)["records"]
        self.assertEqual(rows[0]["reason"], "missing_or_unreadable")
        self.assertEqual(rows[1]["status"], "ok")
        for private in [LABEL_A, LABEL_B, str(self.outside), PAYLOAD_A.strip(), "sha256"]:
            self.assertNotIn(private, result.stdout + result.stderr)

    def test_health_notes_large_record_and_checks_hash(self) -> None:
        self.replace_payload(b"record\n" * 180000)
        result = self.run_vault("vault", "check", REF_A, "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["records"], [
            {"ref": REF_A, "status": "ok", "reason": "requires_explicit_limit_and_slice"}
        ])
        with self.payload_a.open("ab") as stream:
            stream.write(b"changed")
        result = self.run_vault("vault", "check", REF_A)
        self.assertEqual(result.returncode, 4)
        self.assertEqual(result.stdout, f"{REF_A}\terror\trecord_invalid\n")

    def test_health_missing_ref_or_manifest(self) -> None:
        self.assert_private_failure(self.run_vault("vault", "check", "absent"), 1)
        self.manifest.chmod(0o644)
        self.assert_private_failure(self.run_vault("vault", "check"), 3)

    def test_uri_through_symlink_parent_cannot_enter_git(self) -> None:
        repo = self.root / "repo"
        repo.mkdir()
        (repo / ".git").mkdir()
        payload = repo / "hidden.md"
        payload.write_text(PAYLOAD_A)
        payload.chmod(0o600)
        link = self.outside / "link"
        link.symlink_to(repo, target_is_directory=True)
        data = json.loads(self.manifest.read_text())
        data["entries"][0]["uri"] = (link / "hidden.md").as_uri()
        self._write_manifest(entries=data["entries"])
        self.assert_private_failure(self.run_vault("vault", "get", REF_A,
                                    "--max-bytes", "16777216", "--lines", "1:1"), 4)
        result = self.run_vault("vault", "check", REF_A, "--json")
        self.assertEqual(result.returncode, 4)
        self.assertEqual(json.loads(result.stdout)["records"][0]["reason"], "inside_git")

    def test_bad_uri_is_metadata_safe(self) -> None:
        for uri in ["file:relative", "file:///some%00file", "file://[broken/", "file:///a?query"]:
            data = json.loads(self.manifest.read_text())
            data["entries"][0]["uri"] = uri
            self._write_manifest(entries=data["entries"])
            self.assert_private_failure(self.run_vault("vault", "get", REF_A), 4)


class RuaVaultRehashTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.outside = self.root / "outside"
        self.outside.mkdir()
        self.payload = self.outside / "northwind.md"
        self.payload.write_text("original content\n", encoding="utf-8")
        self.payload.chmod(0o600)
        self.manifest_dir = self.outside / "config"
        self.manifest_dir.mkdir()
        self.manifest_dir.chmod(0o700)
        self.manifest = self.manifest_dir / "manifest.json"
        self.sha_original = hashlib.sha256(b"original content\n").hexdigest()
        self._write_manifest(self.sha_original)
        self.env = os.environ.copy()
        self.env["RUA_VAULT_MANIFEST"] = str(self.manifest)

    def _write_manifest(self, sha: str) -> None:
        data = {
            "version": 1,
            "entries": [{
                "ref": "rec-northwind-context",
                "label": "Northwind",
                "aliases": [],
                "uri": self.payload.resolve().as_uri(),
                "sha256": sha,
            }],
        }
        self.manifest.write_text(json.dumps(data, indent=2), encoding="utf-8")
        self.manifest.chmod(0o600)

    def run_cmd(self, *args) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["python3", str(SCRIPT), *args],
            capture_output=True, text=True, env=self.env,
        )

    def test_rehash_already_current(self) -> None:
        result = self.run_cmd("vault", "rehash", "rec-northwind-context")
        self.assertEqual(result.returncode, 0)
        self.assertIn("already current", result.stdout)

    def test_rehash_updates_stale_sha(self) -> None:
        # Write new content to the file, manifest still has old SHA.
        new_content = "updated content\n"
        self.payload.write_text(new_content, encoding="utf-8")
        self.payload.chmod(0o600)
        result = self.run_cmd("vault", "rehash", "rec-northwind-context")
        self.assertEqual(result.returncode, 0)
        self.assertIn("updated", result.stdout)
        # Manifest should now have the new SHA.
        data = json.loads(self.manifest.read_text())
        new_sha = hashlib.sha256(new_content.encode()).hexdigest()
        self.assertEqual(data["entries"][0]["sha256"], new_sha)

    def test_rehash_missing_ref(self) -> None:
        result = self.run_cmd("vault", "rehash", "rec-does-not-exist")
        self.assertEqual(result.returncode, 1)

    def test_rehash_invalid_ref_characters(self) -> None:
        result = self.run_cmd("vault", "rehash", "bad ref!")
        self.assertEqual(result.returncode, 2)


class RuaVaultTidyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.scan = Path(self.temp.name) / "offload"
        self.scan.mkdir()

    def _touch(self, *names: str) -> None:
        for name in names:
            p = self.scan / name
            p.write_text("x")

    def run_cmd(self, *args) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["python3", str(SCRIPT), *args],
            capture_output=True, text=True,
        )

    def test_tidy_no_clusters(self) -> None:
        self._touch("report.pdf", "notes.md")
        result = self.run_cmd("vault", "tidy", str(self.scan))
        self.assertEqual(result.returncode, 0)
        self.assertIn("No version clusters", result.stdout)

    def test_tidy_identifies_stale_versions(self) -> None:
        self._touch("doc-v1.pdf", "doc-v2.pdf", "doc-v3.pdf")
        result = self.run_cmd("vault", "tidy", str(self.scan))
        self.assertEqual(result.returncode, 0)
        self.assertIn("keep    doc-v3.pdf", result.stdout)
        self.assertIn("doc-v1.pdf", result.stdout)
        self.assertIn("doc-v2.pdf", result.stdout)
        # Dry-run: files must still be present.
        self.assertTrue((self.scan / "doc-v1.pdf").exists())

    def test_tidy_delete_removes_stale(self) -> None:
        self._touch("doc-v1.pdf", "doc-v2.pdf", "doc-v3.pdf")
        result = self.run_cmd("vault", "tidy", str(self.scan), "--delete")
        self.assertEqual(result.returncode, 0)
        self.assertFalse((self.scan / "doc-v1.pdf").exists())
        self.assertFalse((self.scan / "doc-v2.pdf").exists())
        self.assertTrue((self.scan / "doc-v3.pdf").exists())

    def test_tidy_json_output(self) -> None:
        self._touch("brief-v1.html", "brief-v2.html")
        result = self.run_cmd("vault", "tidy", str(self.scan), "--json")
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertEqual(len(data["clusters"]), 1)
        self.assertEqual(data["clusters"][0]["keep"], "brief-v2.html")
        self.assertEqual(data["clusters"][0]["stale"], ["brief-v1.html"])

    def test_tidy_v_prefix_and_plain_number(self) -> None:
        self._touch("plan-v3.md", "plan-v4.md", "plan-5.md")
        result = self.run_cmd("vault", "tidy", str(self.scan), "--json")
        self.assertEqual(result.returncode, 0)
        # plan-v3/v4 form one group; plan-5 uses plain number and is separate.
        data = json.loads(result.stdout)
        all_stale = [s for c in data["clusters"] for s in c["stale"]]
        self.assertIn("plan-v3.md", all_stale)

    def test_tidy_invalid_path(self) -> None:
        result = self.run_cmd("vault", "tidy", "/nonexistent/path")
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
