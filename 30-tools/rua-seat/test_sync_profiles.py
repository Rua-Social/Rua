import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import sync_profiles as sync


class ProfileSyncTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name).resolve()
        self.repo, self.home = root / "repo", root / "hermes"
        self.repo.mkdir()
        self.home.mkdir(mode=0o700)
        for name in (*sync.SOURCES, "30-tools/rua-seat/README.md"):
            path = self.repo / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("Canonical instructions\n")
        for name in sync.TARGETS:
            path = self.home / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"Original {name}\n")
        self.config = self.home / "config.yaml"
        self.config.write_text("runtime: existing\n")

    def test_dry_run_leaves_all_files_untouched(self):
        before = sync.snapshot(self.home)
        result = sync.run(self.repo, self.home)
        self.assertEqual(len(result["changed"]), 7)
        self.assertEqual(sync.snapshot(self.home), before)
        self.assertFalse((self.home / ".rua-soul-backups").exists())

    def test_apply_and_restore_preserve_original_content_and_permissions(self):
        before = sync.snapshot(self.home)
        result = sync.run(self.repo, self.home, apply=True)
        backup = Path(result["backup"])
        self.assertEqual(backup.stat().st_mode & 0o777, 0o700)
        self.assertEqual((backup / "0.soul").stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.config.read_text(), "runtime: existing\n")
        self.assertIn("canonical role table", (self.home / "SOUL.md").read_text())
        self.assertEqual(sync.run(self.repo, self.home, apply=True)["changed"], [])
        sync.run(self.repo, self.home, apply=True, restore=backup)
        self.assertEqual(sync.snapshot(self.home), before)

    def test_restore_refuses_later_edits(self):
        result = sync.run(self.repo, self.home, apply=True)
        (self.home / "SOUL.md").write_text("User's later change\n")
        with self.assertRaisesRegex(ValueError, "subsequent edits"):
            sync.run(self.repo, self.home, apply=True, restore=Path(result["backup"]))

    def test_missing_or_symlink_target_refuses_before_any_write(self):
        target = self.home / sync.TARGETS[-1]
        target.unlink()
        before = (self.home / "SOUL.md").read_bytes()
        with self.assertRaises(OSError):
            sync.run(self.repo, self.home, apply=True)
        target.symlink_to(self.config)
        with self.assertRaisesRegex(ValueError, "Symlink"):
            sync.run(self.repo, self.home, apply=True)
        self.assertEqual((self.home / "SOUL.md").read_bytes(), before)

    def test_refuses_git_backups(self):
        (self.home / ".git").mkdir()
        with self.assertRaisesRegex(ValueError, "Git"):
            sync.run(self.repo, self.home, apply=True)

    def test_restore_refuses_modified_backup(self):
        result = sync.run(self.repo, self.home, apply=True)
        backup = Path(result["backup"])
        (backup / "0.soul").write_text("changed")
        with self.assertRaisesRegex(ValueError, "manifest"):
            sync.run(self.repo, self.home, apply=True, restore=backup)

    def test_partial_failure_rolls_back(self):
        before = sync.snapshot(self.home)
        original = sync.atomic_write
        failed = [False]

        def fail_once(path, data, mode):
            if path == self.home / sync.TARGETS[2] and not failed[0]:
                failed[0] = True
                raise OSError("synthetic write failure")
            original(path, data, mode)

        with patch.object(sync, "atomic_write", side_effect=fail_once):
            with self.assertRaisesRegex(RuntimeError, "recovery backup"):
                sync.run(self.repo, self.home, apply=True)
        self.assertEqual(sync.snapshot(self.home), before)
        self.assertFalse((self.home / ".rua-soul-sync.lock").exists())


if __name__ == "__main__":
    unittest.main()
