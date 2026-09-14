#!/usr/bin/env python3
import os
import json
import shlex
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

BIN = Path(__file__).resolve().parent / "rua-seat"


class SeatArgs(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def run_bin(self, *args, env=None):
        env = (env or os.environ).copy()
        env["RUA_HANDOFF_DIR"] = str(Path(self.tmp.name) / "jobs")
        for key in ("RUA_HANDOFF_JOB_ID", "RUA_HANDOFF_ROOT_ID", "RUA_HANDOFF_LINEAGE", "RUA_HANDOFF_DEADLINE"):
            env.pop(key, None)
        return subprocess.run(
            [sys.executable, str(BIN), *args],
            capture_output=True,
            text=True,
            env=env,
            timeout=10,
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

    def fake_env(self, source):
        runner = Path(self.tmp.name) / "runner.py"
        runner.write_text(source)
        env = os.environ.copy()
        env["RUA_SEAT_RUNNER"] = f"{shlex.quote(sys.executable)} {shlex.quote(str(runner))} {{seat}} {{ask}}"
        return env

    def test_durable_result_can_be_read_without_runner(self):
        env = self.fake_env("print('Returned evidence')")
        result = self.run_bin("--json", "--job-id", "readback", "reader", "hello", env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads(result.stdout)
        self.assertEqual(record["status"], "returned")
        self.assertIsNone(record["result"])
        shown = self.run_bin("--show", "readback")
        self.assertEqual(json.loads(shown.stdout), record)
        db = Path(self.tmp.name) / "jobs/jobs.sqlite3"
        self.assertEqual(db.stat().st_mode & 0o777, 0o600)

    def test_duplicate_id_does_not_execute_twice(self):
        marker = str(Path(self.tmp.name) / "calls")
        env = self.fake_env(f"from pathlib import Path\np=Path({marker!r})\np.write_text(p.read_text()+'x' if p.exists() else 'x')\nprint('ok')")
        for _ in range(2):
            result = self.run_bin("--json", "--job-id", "same", "reader", "hello", env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(Path(marker).read_text(), "x")
        changed = self.run_bin("--job-id", "same", "maker", "hello", env=env)
        self.assertEqual(changed.returncode, 2)
        self.assertEqual(Path(marker).read_text(), "x")

    def test_structured_result_and_blocker_status(self):
        payload = {"status": "blocked", "summary": "Source is missing.", "findings": [],
                   "sources": [], "artifacts": [], "blockers": ["Provide the source reference."]}
        env = self.fake_env(f"print({json.dumps(payload)!r})")
        result = self.run_bin("--structured", "--json", "reader", "hello", env=env)
        record = json.loads(result.stdout)
        self.assertEqual(record["status"], "blocked")
        self.assertEqual(record["result"], payload)
        self.assertEqual(result.returncode, 4)

    def test_concurrent_duplicate_claim_runs_once(self):
        marker = Path(self.tmp.name) / "concurrent-calls"
        env = self.fake_env(f"import time\nfrom pathlib import Path\nwith Path({str(marker)!r}).open('a') as f: f.write('x')\ntime.sleep(0.3)\nprint('ok')")
        env["RUA_HANDOFF_DIR"] = str(Path(self.tmp.name) / "jobs")
        for key in ("RUA_HANDOFF_JOB_ID", "RUA_HANDOFF_ROOT_ID", "RUA_HANDOFF_LINEAGE", "RUA_HANDOFF_DEADLINE"):
            env.pop(key, None)
        command = [sys.executable, str(BIN), "--json", "--job-id", "concurrent", "reader", "hello"]
        processes = [subprocess.Popen(command, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for _ in range(2)]
        for process in processes:
            stdout, stderr = process.communicate(timeout=10)
            self.assertIn(json.loads(stdout)["status"], ("running", "returned"), stderr)
        self.assertEqual(marker.read_text(), "x")

    def test_structured_output_rejects_false_shape_and_completion(self):
        for raw in ('not json', '{"status":"completed"}',
                    json.dumps({"status": "completed", "summary": "Done", "findings": [],
                                "sources": [], "artifacts": [], "blockers": ["Not done"]})):
            with self.subTest(raw=raw):
                env = self.fake_env(f"print({raw!r})")
                result = self.run_bin("--structured", "--json", "reader", "hello", env=env)
                self.assertEqual(json.loads(result.stdout)["status"], "invalid_output")
                self.assertEqual(result.returncode, 4)

    def test_timeout_is_saved_and_never_retried(self):
        env = self.fake_env("import time\ntime.sleep(10)")
        result = self.run_bin("--timeout", "0.15", "--json", "--job-id", "timeout", "reader", "hello", env=env)
        self.assertEqual(result.returncode, 4)
        self.assertEqual(json.loads(result.stdout)["status"], "timed_out")
        shown = self.run_bin("--show", "timeout")
        self.assertEqual(json.loads(shown.stdout)["status"], "timed_out")

    def test_missing_runner_is_recorded(self):
        env = os.environ.copy()
        env["RUA_SEAT_RUNNER"] = "/nonexistent/rua-runner {seat} {ask}"
        result = self.run_bin("--json", "reader", "hello", env=env)
        self.assertEqual(result.returncode, 4)
        self.assertEqual(json.loads(result.stdout)["status"], "failed")

    def test_large_output_stops_with_bounded_capture(self):
        env = self.fake_env("import sys\nsys.stdout.write('x' * (2 * 1024 * 1024))")
        result = self.run_bin("--json", "reader", "hello", env=env)
        record = json.loads(result.stdout)
        self.assertEqual(record["status"], "output_limit")
        self.assertLessEqual(len(record["stdout"]) + len(record["stderr"]), 1024 * 1024)

    def test_recursive_seat_cycle_is_stopped(self):
        env = self.fake_env(f"import subprocess, sys\nr=subprocess.run([sys.executable, {str(BIN)!r}, 'reader', 'recursive'], capture_output=True, text=True)\nprint(r.stderr)\nsys.exit(r.returncode)")
        result = self.run_bin("--json", "reader", "hello", env=env)
        record = json.loads(result.stdout)
        self.assertEqual(record["status"], "failed")
        self.assertIn("cycle or depth limit", record["stdout"])

    def test_accepted_decisions_reach_another_runner(self):
        context = {"project_ref": "project-test", "source_refs": ["vault:test"],
                   "accepted_decisions": ["Use the approved concept"], "authorization": "Draft only"}
        path = Path(self.tmp.name) / "context.json"
        path.write_text(json.dumps(context))
        env = self.fake_env("import sys\nprint(sys.argv[-1])")
        result = self.run_bin("--json", "--context", str(path), "maker", "draft", env=env)
        record = json.loads(result.stdout)
        self.assertEqual(record["request"]["context"], context)
        self.assertIn("Use the approved concept", record["stdout"])

    def test_completed_structured_result_hides_worker_details_in_plain_output(self):
        payload = {"status": "completed", "summary": "The draft is ready.",
                   "findings": ["Internal review details"], "sources": [],
                   "artifacts": ["draft.md"], "blockers": []}
        env = self.fake_env(f"print({json.dumps(payload)!r})")
        result = self.run_bin("--structured", "maker", "draft", env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "The draft is ready.\ndraft.md\n")

    def test_reject_storage_inside_git(self):
        env = self.fake_env("print('should not run')")
        (Path(self.tmp.name) / ".git").mkdir()
        result = self.run_bin("reader", "hello", env=env)
        self.assertEqual(result.returncode, 2)
        self.assertIn("outside Git", result.stderr)

    def test_runner_override_requires_seat_placeholder(self):
        env = os.environ.copy()
        env["RUA_SEAT_RUNNER"] = "echo {ask}"
        result = self.run_bin("reader", "hello", env=env)
        self.assertEqual(result.returncode, 2)

    def test_context_rejects_missing_fields(self):
        path = Path(self.tmp.name) / "context.json"
        path.write_text('{"authorization":"do anything"}')
        result = self.run_bin("--context", str(path), "reader", "hello")
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
