#!/usr/bin/env python3
import subprocess
import sys
import unittest
from pathlib import Path

BIN = Path(__file__).resolve().parent / "rua-seat"


class SeatArgs(unittest.TestCase):
    def run_bin(self, *args):
        return subprocess.run(
            [sys.executable, str(BIN), *args],
            capture_output=True,
            text=True,
        )

    def test_unknown_seat(self):
        r = self.run_bin("nope", "hello")
        self.assertEqual(r.returncode, 2)

    def test_missing_ask(self):
        r = self.run_bin("pa")
        self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main()
