#!/usr/bin/env python3
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

BIN = Path(__file__).resolve().parent / "rua-seat"


class SeatArgs(unittest.TestCase):
    def run_bin(self, *args, env=None):
        return subprocess.run(
            [sys.executable, str(BIN), *args],
            capture_output=True,
            text=True,
            env=env,
        )

    def test_unknown_seat(self):
        r = self.run_bin("nope", "hello")
        self.assertEqual(r.returncode, 2)

    def test_missing_ask(self):
        r = self.run_bin("pa")
        self.assertEqual(r.returncode, 2)

    def test_default_requires_hermes_on_path(self):
        env = os.environ.copy()
        env.pop("RUA_SEAT_RUNNER", None)
        env["PATH"] = "/usr/bin:/bin"
        r = self.run_bin("pa", "hello", env=env)
        self.assertEqual(r.returncode, 4)
        self.assertIn("hermes not on PATH", r.stderr)

    def test_runner_override_runs_template(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out.txt"
            runner = Path(tmp) / "fake-runner"
            runner.write_text(
                "#!/bin/sh\n"
                "printf '%s\\n' \"$@\" > \"$RUA_SEAT_TEST_OUT\"\n",
                encoding="utf-8",
            )
            runner.chmod(0o755)
            env = os.environ.copy()
            env["PATH"] = f"{tmp}:{env.get('PATH', '')}"
            env["RUA_SEAT_TEST_OUT"] = str(out)
            env["RUA_SEAT_RUNNER"] = f"fake-runner --profile rua-{{seat}} -- {{ask}}"
            r = self.run_bin("pa", "what is new", env=env)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(
                out.read_text(encoding="utf-8").splitlines(),
                ["--profile", "rua-pa", "--", "what is new"],
            )

    def test_runner_override_requires_ask_placeholder(self):
        env = os.environ.copy()
        env["RUA_SEAT_RUNNER"] = "echo only-{seat}"
        r = self.run_bin("pa", "hello", env=env)
        self.assertEqual(r.returncode, 2)
        self.assertIn("must include {ask}", r.stderr)


if __name__ == "__main__":
    unittest.main()
