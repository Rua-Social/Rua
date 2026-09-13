#!/usr/bin/env python3
"""Offline boundary tests for the Rua Desk terminal launcher."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("rua-desk")


class RuaDeskTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "Rua"
        self.bin = self.root / "bin"
        (self.repo / "20-studio").mkdir(parents=True)
        self.bin.mkdir()
        (self.repo / "20-studio" / "desk.md").write_text(
            "# Test operator card\n", encoding="utf-8"
        )
        for seat in ("claude", "codex", "grok", "gemini"):
            fake = self.bin / seat
            fake.write_text(
                "#!/bin/sh\n"
                "if [ \"${1:-}\" = \"--version\" ]; then\n"
                f"  echo '{seat} test-version'\n"
                "  exit 0\n"
                "fi\n"
                f"printf 'FAKE {seat} PWD=%s ARGS=%s\\n' \"$PWD\" \"$*\"\n",
                encoding="utf-8",
            )
            fake.chmod(0o755)

        self.env = os.environ.copy()
        self.env.update(
            {
                "PATH": f"{self.bin}:{self.env['PATH']}",
                "RUA_REPO": str(self.repo),
                "PAGER": "cat",
            }
        )

    def run_desk(
        self, *args: str, input_text: str | None = None, env: dict[str, str] | None = None
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(SCRIPT), *args],
            input=input_text,
            text=True,
            capture_output=True,
            env=env or self.env,
            check=False,
        )

    def test_bare_noninteractive_call_prints_status_without_waiting(self) -> None:
        result = self.run_desk()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f"Rua desk  {self.repo}", result.stdout)
        self.assertIn("claude test-version", result.stdout)
        self.assertIn("The repo is the desk.", result.stdout)
        self.assertNotIn("Choose a seat [", result.stdout)

    def test_every_direct_seat_starts_in_repo(self) -> None:
        expected_args = {
            "claude": "",
            "codex": "",
            "grok": "dashboard",
            "gemini": "",
        }
        for seat, args in expected_args.items():
            with self.subTest(seat=seat):
                result = self.run_desk(seat)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(f"Opening {seat.title()} at {self.repo}", result.stdout)
                self.assertIn(
                    f"FAKE {seat} PWD={self.repo} ARGS={args}", result.stdout
                )

    def test_grok_one_opens_single_session(self) -> None:
        result = self.run_desk("grok-one")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f"Opening one Grok session at {self.repo}", result.stdout)
        self.assertIn(f"FAKE grok PWD={self.repo} ARGS=", result.stdout)

    def test_interactive_number_selects_seat(self) -> None:
        env = {**self.env, "RUA_DESK_INTERACTIVE": "1"}
        result = self.run_desk(input_text="2\n", env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Rua desk  choose a seat", result.stdout)
        self.assertIn(f"Opening Codex at {self.repo}", result.stdout)
        self.assertIn(f"FAKE codex PWD={self.repo} ARGS=", result.stdout)

    def test_interactive_name_selects_seat(self) -> None:
        env = {**self.env, "RUA_DESK_INTERACTIVE": "1"}
        result = self.run_desk(input_text="claude\n", env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f"Opening Claude at {self.repo}", result.stdout)

    def test_invalid_selection_returns_to_prompt(self) -> None:
        env = {**self.env, "RUA_DESK_INTERACTIVE": "1"}
        result = self.run_desk(input_text="nope\nq\n", env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Choose 1-4, a seat name, s, c, or q.", result.stdout)
        self.assertIn("Desk closed.", result.stdout)
        self.assertEqual(result.stdout.count("Choose a seat ["), 2)
        self.assertNotIn("choice=", result.stdout)

    def test_status_then_quit_does_not_leak_shell_state(self) -> None:
        env = {**self.env, "RUA_DESK_INTERACTIVE": "1"}
        result = self.run_desk(input_text="s\nq\n", env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f"Rua desk  {self.repo}", result.stdout)
        self.assertIn("Desk closed.", result.stdout)
        self.assertNotIn("choice=", result.stdout)

    def test_card_uses_operator_note(self) -> None:
        result = self.run_desk("card")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("# Test operator card", result.stdout)

    def test_missing_seat_is_plain_and_actionable(self) -> None:
        missing_bin = self.root / "missing-bin"
        missing_bin.mkdir()
        env = {**self.env, "PATH": str(missing_bin)}
        result = self.run_desk("gemini", env=env)
        self.assertEqual(result.returncode, 127)
        self.assertEqual(
            result.stderr.strip(), "Gemini is not installed or not on PATH."
        )

    def test_unknown_command_prints_help(self) -> None:
        result = self.run_desk("other")
        self.assertEqual(result.returncode, 2)
        self.assertIn("Unknown Rua desk command: other", result.stderr)
        self.assertIn("rua-desk claude", result.stderr)
        self.assertIn("rua-desk codex", result.stderr)
        self.assertIn("rua-desk grok", result.stderr)
        self.assertIn("rua-desk gemini", result.stderr)


    def test_doctor_passes_with_agents_and_symlinks(self) -> None:
        (self.repo / "AGENTS.md").write_text("# test\n", encoding="utf-8")
        skills = self.repo / "00-system" / "skills" / "rua-todo"
        skills.mkdir(parents=True)
        (skills / "SKILL.md").write_text("# skill\n", encoding="utf-8")
        grok = self.repo / ".grok" / "skills"
        grok.mkdir(parents=True)
        (grok / "rua-todo").symlink_to("../../00-system/skills/rua-todo")
        # Point hooksPath at a path inside the temp repo without touching user gitconfig globally:
        # doctor reads git config for the repo; set local config in the temp repo.
        subprocess.run(
            ["git", "init"],
            cwd=self.repo,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "core.hooksPath", ".githooks"],
            cwd=self.repo,
            check=True,
            capture_output=True,
        )
        (self.repo / ".githooks").mkdir(exist_ok=True)
        # Fake rua / rua-seat on PATH
        for name in ("rua", "rua-seat"):
            fake = self.bin / name
            fake.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            fake.chmod(0o755)
        result = self.run_desk("doctor")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS  AGENTS.md present", result.stdout)
        self.assertIn("PASS  symlink rua-todo", result.stdout)
        self.assertIn("Doctor ok", result.stdout)

    def test_doctor_fails_without_agents(self) -> None:
        result = self.run_desk("doctor")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("FAIL  AGENTS.md missing", result.stdout)
        self.assertIn("Doctor failed.", result.stdout)

    def test_help_lists_doctor(self) -> None:
        result = self.run_desk("help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("rua-desk doctor", result.stdout)

    def test_missing_repo_is_plain_and_actionable(self) -> None:
        missing = self.root / "missing"
        env = {**self.env, "RUA_REPO": str(missing)}
        result = self.run_desk("status", env=env)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(
            result.stderr.strip(),
            f"Rua repo not found at {missing}. Set RUA_REPO to the checkout.",
        )


if __name__ == "__main__":
    unittest.main()
