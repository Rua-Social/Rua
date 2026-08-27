#!/usr/bin/env python3
"""Offline boundary tests for the Telegram desk bridge."""

from __future__ import annotations

import io
import json
import os
import subprocess
import tempfile
import threading
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest import mock

import bridge


GOOGLE_REPLY = "Google isn't on this phone seat. Parked on the desk list."
FRESH_TODO = date.today().isoformat()
QUEUE_REPLY = "Hold that. Still on the last one."
SETUP_REPLY = "Set TELEGRAM_USER_ID before starting the desk."


def file_mode(path: Path) -> int:
    return path.stat().st_mode & 0o777


def update(
    update_id: int = 10,
    *,
    user_id: int = 42,
    chat_id: int = 420,
    chat_type: str = "private",
    text: str | None = "do the thing",
    voice: dict | None = None,
) -> dict:
    message: dict = {
        "message_id": update_id + 100,
        "chat": {"id": chat_id, "type": chat_type},
        "from": {"id": user_id},
    }
    if text is not None:
        message["text"] = text
    if voice is not None:
        message["voice"] = voice
    return {"update_id": update_id, "message": message}


class RuntimeCase(unittest.TestCase):
    """Point every mutable bridge path at one disposable directory."""

    def setUp(self):
        super().setUp()
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.repo = self.root / "Rua"
        self.repo.mkdir()
        (self.repo / "20-studio").mkdir()
        self.lists = self.repo / "20-studio" / "lists.md"
        self.lists.write_text("# Lists\n\n## Desk\n\n### Blocked\n")
        self.state = self.root / ".grok" / "desk-bridge"
        self.secrets = self.root / ".grok" / "secrets" / "desk-bridge.env"
        self.eleven = self.root / ".grok" / "secrets" / "elevenlabs.env"
        self.plist = self.root / "Library" / "LaunchAgents" / "com.rua.desk-bridge.plist"
        paths = {
            "REPO": self.repo,
            "STATE_DIR": self.state,
            "SESSION_FILE": self.state / "session_id",
            "SESSION_META_FILE": self.state / "session.json",
            "ENGINE_STATE_FILE": self.state / "engine_state.json",
            "ENGINE_OVERRIDE_FILE": self.state / "engine_override",
            "OFFSET_FILE": self.state / "offset",
            "INBOX_FILE": self.state / "inbox.json",
            "LAST_ERROR_FILE": self.state / "last_error",
            "LAST_RUN_FILE": self.state / "last_run",
            "OUTBOX_FILE": self.state / "outbox.json",
            "METRICS_FILE": self.state / "metrics.jsonl",
            "RUN_LOCK_FILE": self.state / "run.lock",
            "BRIDGE_LOG_FILE": self.state / "bridge.log",
            "BRIDGE_ERR_FILE": self.state / "bridge.err",
            "SECRETS": self.secrets,
            "ELEVEN_SECRETS": self.eleven,
            "PLIST_PATH": self.plist,
            "LISTS_FILE": self.lists,
            "DESK_LIST_FILE": self.lists,
        }
        for name, value in paths.items():
            patcher = mock.patch.object(bridge, name, value, create=True)
            patcher.start()
            self.addCleanup(patcher.stop)

    def write_owner_secrets(self, owner: str = "42") -> None:
        self.secrets.parent.mkdir(parents=True, exist_ok=True)
        self.secrets.write_text(
            "export TELEGRAM_BOT_TOKEN=token\n"
            f"export TELEGRAM_USER_ID={owner}\n"
        )


class PipeProcess:
    """Popen double with selectable stdout and no child process."""

    def __init__(
        self,
        schedule: list[tuple[float, str]] | None = None,
        *,
        keep_open: float = 0.0,
        returncode: int = 0,
        stderr: str = "",
    ):
        read_fd, self._write_fd = os.pipe()
        self.stdout = os.fdopen(read_fd, "r", encoding="utf-8", buffering=1)
        self.stderr = io.StringIO(stderr)
        self._planned_returncode = returncode
        self.returncode: int | None = None
        self.terminated = False
        self.killed = False
        self._stop = threading.Event()
        self._done = threading.Event()
        self.args = ["grok"]
        self.pid = 12345
        self._thread = threading.Thread(
            target=self._write,
            args=(schedule or [], keep_open),
            daemon=True,
        )
        self._thread.start()

    def _write(self, schedule: list[tuple[float, str]], keep_open: float) -> None:
        try:
            for delay, line in schedule:
                if self._stop.wait(delay):
                    break
                try:
                    os.write(self._write_fd, line.encode())
                except (BrokenPipeError, OSError):
                    break
            self._stop.wait(keep_open)
        finally:
            try:
                os.close(self._write_fd)
            except OSError:
                pass
            if self.returncode is None:
                self.returncode = -15 if self.terminated else self._planned_returncode
            self._done.set()

    def poll(self):
        return self.returncode if self._done.is_set() else None

    def wait(self, timeout=None):
        if not self._done.wait(timeout):
            raise subprocess.TimeoutExpired(self.args, timeout)
        return self.returncode

    def terminate(self):
        self.terminated = True
        self._stop.set()

    def kill(self):
        self.killed = True
        self.terminated = True
        self._stop.set()

    def communicate(self, timeout=None):
        self.wait(timeout)
        return self.stdout.read(), self.stderr.read()

    def close(self):
        self._stop.set()
        self._done.wait(0.5)
        try:
            self.stdout.close()
        except OSError:
            pass


def success_stream(
    text: str = "Done.",
    *,
    session_id: str = "fresh-session",
    effort: str = "medium",
    prompt_tokens: int = 1200,
) -> list[tuple[float, str]]:
    return [
        (0.0, json.dumps({
            "type": "session", "sessionId": session_id,
            "model": "grok-4.6-build", "effort": effort,
        }) + "\n"),
        (0.0, json.dumps({
            "type": "usage", "data": {
                "prompt_tokens": prompt_tokens,
                "cached_prompt_tokens": 100,
                "completion_tokens": 12,
                "reasoning_tokens": 4,
            },
        }) + "\n"),
        (0.0, json.dumps({"type": "text", "data": text}) + "\n"),
        (0.0, json.dumps({
            "type": "end", "sessionId": session_id,
            "model": "grok-4.6-build", "effort": effort,
        }) + "\n"),
    ]


class ChunkTest(unittest.TestCase):
    def test_short(self):
        self.assertEqual(bridge.chunk_text("hi"), ["hi"])

    def test_empty(self):
        self.assertEqual(bridge.chunk_text("  "), ["(empty reply)"])

    def test_splits_long_without_losing_words(self):
        body = ("word " * 2000).strip()
        parts = bridge.chunk_text(body, limit=80)
        self.assertGreater(len(parts), 1)
        self.assertEqual(" ".join(parts), body)
        self.assertTrue(all(len(part) <= 80 for part in parts))


class EnvAndOwnerTest(RuntimeCase):
    def test_load_env_preserves_explicit_blank(self):
        self.secrets.parent.mkdir(parents=True)
        self.secrets.write_text(
            "export TELEGRAM_BOT_TOKEN=abc\nexport TELEGRAM_USER_ID=\n"
        )
        env = bridge.load_env(self.secrets)
        self.assertEqual(env["TELEGRAM_BOT_TOKEN"], "abc")
        self.assertEqual(env["TELEGRAM_USER_ID"], "")

    def test_elevenlabs_file_cannot_override_telegram_owner_or_token(self):
        self.write_owner_secrets("42")
        self.eleven.write_text(
            "export ELEVENLABS_API_KEY=voice-key\n"
            "export TELEGRAM_BOT_TOKEN=wrong-token\n"
            "export TELEGRAM_USER_ID=7\n"
        )
        env = bridge.load_secrets()
        self.assertEqual(env["TELEGRAM_BOT_TOKEN"], "token")
        self.assertEqual(env["TELEGRAM_USER_ID"], "42")
        self.assertEqual(env["ELEVENLABS_API_KEY"], "voice-key")

    def test_grok_env_loads_sibling_secret_files_without_bot_token(self):
        self.write_owner_secrets("42")
        (self.secrets.parent / "xpoz.env").write_text(
            "export XPOZ_API_KEY=test-xpoz-key\n"
        )
        (self.secrets.parent / "moonshot.env").write_text(
            "export MOONSHOT_API_KEY=test-moonshot-key\n"
        )
        with mock.patch.dict(
            os.environ,
            {"XPOZ_API_KEY": "", "MOONSHOT_API_KEY": ""},
            clear=False,
        ):
            env = bridge.grok_env()
        self.assertEqual(env.get("XPOZ_API_KEY"), "test-xpoz-key")
        self.assertEqual(env.get("MOONSHOT_API_KEY"), "test-moonshot-key")
        self.assertNotEqual(env.get("TELEGRAM_BOT_TOKEN"), "token")
        self.assertEqual(env.get(bridge.GATEWAY_TOOLS_ENV), "1")
        self.assertEqual(env.get(bridge.MANAGED_MCPS_ENV), "1")

    def test_auto_engine_order_normalizes_aliases_and_duplicates(self):
        self.write_owner_secrets("42")
        with self.secrets.open("a") as handle:
            handle.write(
                "export DESK_ENGINE=auto\n"
                "export DESK_ENGINE_ORDER=anthropic,openai,grok,claude\n"
            )
        self.assertEqual(bridge.configured_engine(), "auto")
        self.assertEqual(bridge.engine_order(), ["claude", "codex", "grok"])

    def test_configured_owner_strips_and_returns_id(self):
        self.assertEqual(bridge.configured_owner({"TELEGRAM_USER_ID": " 42 "}), "42")

    def test_configured_owner_rejects_blank_with_setup_sentence(self):
        with self.assertRaisesRegex(ValueError, SETUP_REPLY):
            bridge.configured_owner({"TELEGRAM_USER_ID": "  "})

    def test_blank_owner_never_auto_pairs(self):
        self.write_owner_secrets("")
        original = self.secrets.read_text()
        with self.assertRaisesRegex(ValueError, SETUP_REPLY):
            bridge.pair_status(bridge.load_secrets(), 99)
        self.assertEqual(self.secrets.read_text(), original)

    def test_run_refuses_blank_owner_before_polling(self):
        with mock.patch.object(
            bridge, "load_secrets",
            return_value={"TELEGRAM_BOT_TOKEN": "token", "TELEGRAM_USER_ID": ""},
        ), mock.patch.object(bridge, "poll_loop") as poll, mock.patch.object(
            bridge.sys, "stderr", new_callable=io.StringIO
        ) as stderr:
            result = bridge.main(["bridge.py", "--run"])
        self.assertEqual(result, 1)
        poll.assert_not_called()
        self.assertIn(SETUP_REPLY, stderr.getvalue())

    def test_second_runtime_cannot_take_the_singleton_lock(self):
        first = bridge.acquire_run_lock()
        self.addCleanup(os.close, first)
        with self.assertRaisesRegex(RuntimeError, "already running"):
            bridge.acquire_run_lock()


class RoutingTest(RuntimeCase):
    def test_private_dm_only(self):
        self.assertTrue(bridge.is_private_dm({"type": "private"}))
        self.assertFalse(bridge.is_private_dm({"type": "group"}))
        self.assertFalse(bridge.is_private_dm({"type": "supergroup"}))
        self.assertFalse(bridge.is_private_dm({}))

    def test_owner_message_is_enqueued(self):
        enqueue = mock.Mock(return_value=0)
        with mock.patch.object(
            bridge, "load_secrets", return_value={"TELEGRAM_USER_ID": "42"}
        ), mock.patch.object(bridge, "send") as send:
            next_offset = bridge.handle_update("token", update(), enqueue)
        self.assertEqual(next_offset, 11)
        enqueue.assert_called_once()
        job = enqueue.call_args.args[0]
        self.assertEqual(job["chat_id"], 420)
        self.assertEqual(job["text"], "do the thing")
        send.assert_not_called()

    def test_foreign_dm_gets_plain_refusal_and_is_not_enqueued(self):
        enqueue = mock.Mock()
        with mock.patch.object(
            bridge, "load_secrets", return_value={"TELEGRAM_USER_ID": "42"}
        ), mock.patch.object(bridge, "send") as send:
            next_offset = bridge.handle_update(
                "token", update(user_id=7, chat_id=700), enqueue
            )
        self.assertEqual(next_offset, 11)
        enqueue.assert_not_called()
        send.assert_called_once_with(
            "token",
            700,
            "This desk is paired to another Telegram account.",
            timeout=5,
        )

    def test_group_is_silent_even_when_sent_by_owner(self):
        enqueue = mock.Mock()
        with mock.patch.object(
            bridge, "load_secrets", return_value={"TELEGRAM_USER_ID": "42"}
        ), mock.patch.object(bridge, "send") as send:
            next_offset = bridge.handle_update(
                "token", update(chat_type="group"), enqueue
            )
        self.assertEqual(next_offset, 11)
        enqueue.assert_not_called()
        send.assert_not_called()

    def test_second_ask_is_acknowledged_as_queued(self):
        enqueue = mock.Mock(return_value=1)
        with mock.patch.object(
            bridge, "load_secrets", return_value={"TELEGRAM_USER_ID": "42"}
        ), mock.patch.object(bridge, "send") as send:
            next_offset = bridge.handle_update("token", update(), enqueue)
        self.assertEqual(next_offset, 11)
        send.assert_called_once_with("token", 420, QUEUE_REPLY, timeout=5)

    def test_enqueue_failure_is_raised_so_poller_retries_same_offset(self):
        enqueue = mock.Mock(side_effect=RuntimeError("queue broke"))
        with mock.patch.object(
            bridge, "load_secrets", return_value={"TELEGRAM_USER_ID": "42"}
        ), mock.patch.object(bridge, "send"):
            with self.assertRaisesRegex(RuntimeError, "queue broke"):
                bridge.handle_update("token", update(), enqueue)

    def test_malformed_stored_offset_recovers_to_zero(self):
        self.state.mkdir(parents=True)
        bridge.OFFSET_FILE.write_text("definitely-not-an-int")
        self.assertEqual(bridge.read_offset(), 0)

    def test_poller_persists_offset_after_durable_enqueue(self):
        class StopPolling(BaseException):
            pass

        coordinator = mock.Mock()
        coordinator.enqueue.return_value = 0
        with mock.patch.object(
            bridge, "load_secrets", return_value={"TELEGRAM_USER_ID": "42"}
        ), mock.patch.object(
            bridge, "WorkCoordinator", return_value=coordinator
        ), mock.patch.object(
            bridge, "deliver_outbox", return_value=True
        ), mock.patch.object(
            bridge,
            "api",
            side_effect=[{"result": [update()]}, StopPolling()],
        ):
            with self.assertRaises(StopPolling):
                bridge.poll_loop("token")
        self.assertEqual(bridge.read_offset(), 11)

    def test_poller_does_not_advance_offset_when_enqueue_fails(self):
        class StopPolling(BaseException):
            pass

        bridge.write_text(bridge.OFFSET_FILE, "5")
        coordinator = mock.Mock()
        coordinator.enqueue.side_effect = RuntimeError("queue broke")
        with mock.patch.object(
            bridge, "load_secrets", return_value={"TELEGRAM_USER_ID": "42"}
        ), mock.patch.object(
            bridge, "WorkCoordinator", return_value=coordinator
        ), mock.patch.object(
            bridge, "deliver_outbox", return_value=True
        ), mock.patch.object(
            bridge,
            "api",
            side_effect=[{"result": [update()]}, StopPolling()],
        ):
            with self.assertRaises(StopPolling):
                bridge.poll_loop("token")
        self.assertEqual(bridge.read_offset(), 5)

    def test_poller_does_not_overwrite_last_error_with_getupdates_timeout(self):
        class StopPolling(BaseException):
            pass

        bridge.write_text(bridge.LAST_ERROR_FILE, "grok max_turns_reached")
        coordinator = mock.Mock()
        with mock.patch.object(
            bridge, "load_secrets", return_value={"TELEGRAM_USER_ID": "42"}
        ), mock.patch.object(
            bridge, "WorkCoordinator", return_value=coordinator
        ), mock.patch.object(
            bridge, "deliver_outbox", return_value=True
        ), mock.patch.object(
            bridge,
            "api",
            side_effect=[
                RuntimeError("telegram getUpdates timed out"),
                StopPolling(),
            ],
        ):
            with self.assertRaises(StopPolling):
                bridge.poll_loop("token")
        self.assertEqual(bridge.read_text(bridge.LAST_ERROR_FILE), "grok max_turns_reached")


class QueuePersistenceTest(RuntimeCase):
    def test_depth_includes_a_job_after_the_worker_has_taken_it(self):
        coordinator = bridge.WorkCoordinator("token")
        coordinator.jobs.put({"id": 10})
        coordinator.jobs.get_nowait()
        self.assertEqual(coordinator.jobs.qsize(), 0)
        self.assertEqual(coordinator.depth(), 1)
        coordinator.jobs.task_done()
        self.assertEqual(coordinator.depth(), 0)

    def test_replayed_update_id_is_not_put_in_memory_twice(self):
        coordinator = bridge.WorkCoordinator("token")
        job = {
            "id": 10,
            "chat_id": 420,
            "message_id": 110,
            "text": "do the thing",
            "voice": None,
            "enqueued_at": 1.0,
        }
        coordinator.enqueue(job)
        coordinator.enqueue(job)
        self.assertEqual(len(bridge.inbox_items()), 1)
        self.assertEqual(coordinator.jobs.qsize(), 1)

    def test_offset_is_durable_before_job_is_exposed_to_worker(self):
        class StopPolling(BaseException):
            pass

        worker_done = threading.Event()
        offsets_seen_by_worker: list[int] = []

        def finish_immediately(_token, _job, delivery_notify=None):
            del delivery_notify
            offsets_seen_by_worker.append(bridge.read_offset())
            worker_done.set()

        def metric_barrier(event):
            # Force the current enqueue->metric->offset ordering to expose its
            # crash window deterministically instead of relying on a race.
            if event.get("stage") == "pickup":
                worker_done.wait(0.3)

        with mock.patch.object(
            bridge, "load_secrets", return_value={"TELEGRAM_USER_ID": "42"}
        ), mock.patch.object(
            bridge, "deliver_outbox", return_value=True
        ), mock.patch.object(
            bridge, "process_work_item", side_effect=finish_immediately
        ), mock.patch.object(
            bridge, "append_metric", side_effect=metric_barrier
        ), mock.patch.object(
            bridge,
            "api",
            side_effect=[{"result": [update()]}, StopPolling()],
        ):
            with self.assertRaises(StopPolling):
                bridge.poll_loop("token")
        self.assertTrue(worker_done.wait(0.5))
        self.assertEqual(offsets_seen_by_worker, [11])


class GoogleMissTest(RuntimeCase):
    def test_card_answerable_asks_reach_grok(self):
        # No input gate: asks the instance card or todo can answer are desk
        # asks. The Google sentence is Grok's call, never a regex's.
        asks = [
            "what did I send to Tommy today",
            "what was the last doc I sent Tommy",
            "last file I sent him",
            "when is my call with Tommy",
            "check my gmail",
            "What's on my Google Calendar tomorrow?",
        ]
        for ask in asks:
            with self.subTest(ask=ask), mock.patch.object(
                bridge, "run_grok", return_value="Draft 4 on Tommy's thread."
            ) as run_grok:
                reply = bridge.handle_prompt("token", 420, 7, ask)
            run_grok.assert_called_once()
            self.assertEqual(reply, "Draft 4 on Tommy's thread.")
            self.assertNotIn(GOOGLE_REPLY, reply)

    def test_google_ask_is_parked_idempotently(self):
        ask = "Find the latest client deck in Drive"
        bridge.park_google_ask(ask)
        once = self.lists.read_text()
        bridge.park_google_ask(ask)
        twice = self.lists.read_text()
        self.assertEqual(twice, once)
        self.assertEqual(
            twice.count("phone Google request blocked by desk-bridge"), 1
        )
        self.assertNotIn(ask, twice)

    def test_pocket_brief_reads_todo_and_client_status(self):
        todo = self.repo / "20-studio" / "todo.md"
        todo.write_text(
            f"# Todo\n\n## Open\n\n- {FRESH_TODO} Send the Fitzpatrick reply.\n"
        )
        self.lists.write_text(
            "# Lists\n\n## Founder\n\n### Do\n\n- Diary leak that must not brief.\n"
        )
        clients = self.repo / "10-clients" / "fitzpatrick-castle"
        clients.mkdir(parents=True)
        (clients / "README.md").write_text(
            "# Instance\n\n**Status:** deposit waiting\n\n"
            "Latest client document: `draft4.pdf`\n"
        )
        brief = bridge.pocket_brief(self.repo / "10-clients")
        self.assertIn("Do: Send the Fitzpatrick reply.", brief)
        self.assertNotIn("Diary leak", brief)
        self.assertNotIn("Next:", brief)
        self.assertIn("fitzpatrick castle: deposit waiting", brief)
        self.assertIn("draft4.pdf", brief)

    def test_brief_command_does_not_start_grok(self):
        (self.repo / "20-studio" / "todo.md").write_text(
            f"# Todo\n\n## Open\n\n- {FRESH_TODO} Send the reply.\n"
        )
        with mock.patch.object(bridge, "run_grok") as run_grok:
            reply = bridge.handle_prompt("token", 420, 7, "brief")
        run_grok.assert_not_called()
        self.assertIn("Do: Send the reply.", reply)

    def test_todo_command_does_not_start_grok(self):
        (self.repo / "20-studio" / "todo.md").write_text(
            f"# Todo\n\n## Open\n\n- {FRESH_TODO} Send the reply.\n"
        )
        with mock.patch.object(bridge, "run_grok") as run_grok:
            reply = bridge.handle_prompt("token", 420, 7, "todo")
        run_grok.assert_not_called()
        self.assertIn("- Send the reply.", reply)
        self.assertNotIn("Do:", reply)
        self.assertNotIn(FRESH_TODO, reply)
        self.assertTrue(reply.endswith("Text the action to close it."))

    def test_format_open_todo_prints_action_not_date(self):
        todo = self.repo / "20-studio" / "todo.md"
        todo.write_text(
            f"# Todo\n\n## Open\n\n- {FRESH_TODO} Send the reply.\n"
        )
        reply = bridge.format_open_todo(today=date.today())
        self.assertEqual(
            reply,
            "- Send the reply.\nText the action to close it.",
        )
        self.assertNotIn(FRESH_TODO, reply)

    def test_format_open_todo_empty_stays_nothing_open(self):
        todo = self.repo / "20-studio" / "todo.md"
        todo.write_text("# Todo\n\n## Open\n")
        self.assertEqual(bridge.format_open_todo(), "Nothing open.")

    def test_format_open_todo_keeps_stale_prefix(self):
        todo = self.repo / "20-studio" / "todo.md"
        todo.write_text(
            "# Todo\n\n## Open\n\n- 2026-08-01 Chase the old deposit.\n"
        )
        reply = bridge.format_open_todo(today=date(2026, 8, 18))
        self.assertEqual(
            reply,
            "- STALE Chase the old deposit.\nText the action to close it.",
        )
        self.assertNotIn("2026-08-01", reply)

    def test_format_open_todo_full_then_bullets_then_close(self):
        todo = self.repo / "20-studio" / "todo.md"
        todo.write_text(
            "# Todo\n\n## Open\n\n"
            + "".join(f"- {FRESH_TODO} Send pack {index}.\n" for index in range(7))
        )
        reply = bridge.format_open_todo(today=date.today())
        self.assertTrue(reply.startswith("Todo is full. Close one.\n"))
        self.assertIn("- Send pack 0.", reply)
        self.assertTrue(reply.endswith("Text the action to close it."))
        self.assertNotIn(FRESH_TODO, reply)

    def test_named_send_ask_reaches_grok(self):
        ask = "what did I send to Tommy today"
        with mock.patch.object(
            bridge, "run_grok", return_value="Draft 4 on Tommy's thread."
        ) as run_grok:
            reply = bridge.handle_prompt("token", 420, 7, ask)
        run_grok.assert_called_once()
        self.assertEqual(reply, "Draft 4 on Tommy's thread.")
        self.assertNotIn(GOOGLE_REPLY, reply)

    def test_missing_tools_sentence_is_not_a_parked_google_miss(self):
        with mock.patch.object(bridge, "park_google_ask") as park:
            reply = bridge.google_miss_finish(bridge.PHONE_GOOGLE_MISSING)
        park.assert_not_called()
        self.assertEqual(reply, bridge.PHONE_GOOGLE_MISSING)

    def test_quoted_google_sentence_is_not_a_miss(self):
        (self.repo / "20-studio" / "todo.md").write_text(
            "# Todo\n\n## Open\n\n- 2026-08-18 Chase the Fitzpatrick deposit.\n"
        )
        with mock.patch.object(
            bridge,
            "run_grok",
            return_value=(
                "The rule is: Google isn't on this phone seat. "
                "Parked on the desk list. So I checked the card first."
            ),
        ):
            reply = bridge.handle_prompt("token", 420, 7, "how do you handle mail")
        self.assertNotIn(
            "phone Google request blocked", self.lists.read_text()
        )
        self.assertNotIn("Do:", reply)

    def test_voice_brainstorm_never_closes_the_list(self):
        todo = self.repo / "20-studio" / "todo.md"
        done = self.repo / "20-studio" / "todo-done.md"
        todo.write_text(
            "# Todo\n\n## Open\n\n- 2026-08-18 Chase the Fitzpatrick deposit.\n"
        )
        done.write_text("# Todo done\n\n")
        with mock.patch.object(
            bridge,
            "run_grok",
            return_value="Think it through.\nLIST+ Done | Fitzpatrick deposit",
        ):
            reply = bridge.handle_prompt(
                "token",
                420,
                7,
                "Voice note: brainstorm the deposit angle",
                from_voice=True,
            )
        self.assertEqual(
            reply,
            "Think it through.\n\nVoice can't close the list. Text it if it landed.",
        )
        self.assertIn("Chase the Fitzpatrick deposit.", todo.read_text())
        self.assertNotIn("Fitzpatrick", done.read_text())

    def test_google_miss_comes_back_from_grok_with_brief_and_park(self):
        (self.repo / "20-studio" / "todo.md").write_text(
            f"# Todo\n\n## Open\n\n- {FRESH_TODO} Chase the Fitzpatrick deposit.\n"
        )
        with mock.patch.object(
            bridge, "run_grok", return_value=GOOGLE_REPLY
        ) as run_grok:
            reply = bridge.handle_prompt("token", 420, 7, "Read my latest Gmail")
            again = bridge.handle_prompt("token", 420, 7, "Read my latest Gmail")
        run_grok.assert_called()
        self.assertTrue(reply.startswith(GOOGLE_REPLY))
        self.assertIn("Do: Chase the Fitzpatrick deposit.", reply)
        self.assertIn("Do: Chase the Fitzpatrick deposit.", again)
        self.assertEqual(
            self.lists.read_text().count(
                "phone Google request blocked by desk-bridge"
            ),
            1,
        )

    def test_pocket_brief_ranks_gated_do_over_softer_line(self):
        (self.repo / "20-studio" / "todo.md").write_text(
            "# Todo\n\n## Open\n\n"
            f"- {FRESH_TODO} Think about Papa Rua colours.\n"
            f"- {FRESH_TODO} Chase the Fitzpatrick deposit on a dated thread.\n"
        )
        idle = self.repo / "10-clients" / "aaa-idle"
        idle.mkdir(parents=True)
        (idle / "README.md").write_text("# Instance\n\n**Status:** delivered\n")
        hot = self.repo / "10-clients" / "zzz-hot"
        hot.mkdir(parents=True)
        (hot / "README.md").write_text(
            "# Instance\n\n**Status:** proposal drafted, not sent\n\n"
            "Latest client document: `pack.pdf`\n"
        )
        brief = bridge.pocket_brief(self.repo / "10-clients")
        self.assertIn("Do: Chase the Fitzpatrick deposit", brief)
        self.assertNotIn("Papa Rua", brief)
        self.assertNotIn("cannot see Gmail", brief)
        self.assertIn("zzz hot: proposal drafted, not sent", brief)
        self.assertNotIn("aaa idle", brief)

    def test_pocket_brief_ranks_stale_gated_do_over_fresh_craft(self):
        old = (date.today() - timedelta(days=8)).isoformat()
        (self.repo / "20-studio" / "todo.md").write_text(
            "# Todo\n\n## Open\n\n"
            f"- {FRESH_TODO} Do Deirdre Duffy's edits\n"
            f"- {old} Chase the Fitzpatrick deposit on a dated thread.\n"
        )
        brief = bridge.pocket_brief(self.repo / "10-clients")
        self.assertIn("Do: STALE Chase the Fitzpatrick deposit", brief)
        self.assertNotIn("Deirdre", brief)
        self.assertNotIn("STALE: Chase the Fitzpatrick deposit", brief)

    def test_desk_ask_writes_todo_and_hides_trailers(self):
        todo = self.repo / "20-studio" / "todo.md"
        done = self.repo / "20-studio" / "todo-done.md"
        todo.write_text(
            "# Todo\n\n## Open\n\n- 2026-08-18 chase the Fitzpatrick deposit\n"
        )
        done.write_text("# Todo done\n\n")
        with mock.patch.object(
            bridge,
            "run_grok",
            return_value=(
                "Drafted the chase note.\n"
                "LIST+ Do | send the Ecoplex pack\n"
                "LIST+ Done | chase the Fitzpatrick deposit"
            ),
        ):
            reply = bridge.handle_prompt(
                "token", 420, 7, "chase tommy on the deposit"
            )
        self.assertEqual(reply, "Drafted the chase note.")
        self.assertNotIn("LIST+", reply)
        open_text = todo.read_text()
        self.assertIn("send the Ecoplex pack", open_text)
        self.assertNotIn("chase the Fitzpatrick deposit", open_text)
        self.assertIn("chase the Fitzpatrick deposit", done.read_text())
        self.assertNotIn("send the Ecoplex pack", self.lists.read_text())

    def test_list_write_does_not_duplicate_the_same_line(self):
        todo = self.repo / "20-studio" / "todo.md"
        todo.write_text(
            "# Todo\n\n## Open\n\n- 2026-08-18 chase the Fitzpatrick deposit\n"
        )
        reply = bridge.persist_desk_writes(
            "Still that.\nLIST+ Do | chase the Fitzpatrick deposit"
        )
        self.assertEqual(reply, "Still that.\n\nAlready on the list.")
        self.assertEqual(
            todo.read_text().count("chase the Fitzpatrick deposit"), 1
        )

    def test_todo_rejects_junk_and_caps_open_list(self):
        todo = self.repo / "20-studio" / "todo.md"
        todo.write_text("# Todo\n\n## Open\n")
        self.assertEqual(bridge.add_open_todo("phone cannot see Gmail"), "junk")
        self.assertNotIn("Gmail", todo.read_text())
        for index in range(7):
            self.assertEqual(bridge.add_open_todo(f"Send pack {index}"), "")
        self.assertEqual(bridge.add_open_todo("Send pack extra"), "full")
        self.assertEqual(bridge.add_open_todo("Send pack 0"), "dup")
        self.assertEqual(todo.read_text().count("Send pack"), 7)

    def test_close_todo_refuses_junk_even_when_it_matches(self):
        todo = self.repo / "20-studio" / "todo.md"
        done = self.repo / "20-studio" / "todo-done.md"
        todo.write_text(
            "# Todo\n\n## Open\n\n- 2026-08-18 Chase the gmail invoice.\n"
        )
        done.write_text("# Todo done\n\n")
        self.assertFalse(bridge.close_todo("gmail"))
        self.assertIn("Chase the gmail invoice.", todo.read_text())
        self.assertNotIn("gmail", done.read_text())

    def test_voice_ask_never_closes_the_list(self):
        todo = self.repo / "20-studio" / "todo.md"
        done = self.repo / "20-studio" / "todo-done.md"
        todo.write_text(
            "# Todo\n\n## Open\n\n- 2026-08-18 Chase the Fitzpatrick deposit.\n"
        )
        done.write_text("# Todo done\n\n")
        with mock.patch.object(
            bridge,
            "run_grok",
            return_value="Sent it.\nLIST+ Done | Fitzpatrick deposit",
        ):
            reply = bridge.handle_prompt(
                "token", 420, 7, "Voice note: the deposit went", from_voice=True
            )
        self.assertEqual(
            reply,
            "Sent it.\n\nVoice can't close the list. Text it if it landed.",
        )
        self.assertIn("Chase the Fitzpatrick deposit.", todo.read_text())
        self.assertNotIn("Fitzpatrick", done.read_text())

    def test_voice_ask_only_adds_an_explicit_do_line(self):
        todo = self.repo / "20-studio" / "todo.md"
        todo.write_text("# Todo\n\n## Open\n")
        with mock.patch.object(
            bridge,
            "run_grok",
            return_value="Noted.\nLIST+ Do | Send the Ecoplex nudge",
        ):
            reply = bridge.handle_prompt(
                "token", 420, 7,
                "Voice note: Add one todo: Send the Ecoplex nudge",
                from_voice=True,
            )
        self.assertEqual(reply, "Noted.")
        self.assertIn("Send the Ecoplex nudge", todo.read_text())

    def test_voice_ask_does_not_infer_a_do_line(self):
        todo = self.repo / "20-studio" / "todo.md"
        todo.write_text("# Todo\n\n## Open\n")
        with mock.patch.object(
            bridge,
            "run_grok",
            return_value="Noted.\nLIST+ Do | Send the Ecoplex nudge",
        ):
            reply = bridge.handle_prompt(
                "token", 420, 7, "Voice note: nudge ecoplex", from_voice=True
            )
        self.assertIn("Voice did not add a todo", reply)
        self.assertNotIn("Send the Ecoplex nudge", todo.read_text())

    def test_refused_do_trailers_say_so_on_the_phone(self):
        todo = self.repo / "20-studio" / "todo.md"
        todo.write_text(
            "# Todo\n\n## Open\n\n"
            + "".join(f"- 2026-08-18 Send pack {index}.\n" for index in range(7))
        )
        with mock.patch.object(
            bridge,
            "run_grok",
            return_value=(
                "Ok.\n"
                "LIST+ Do | Send pack extra\n"
                "LIST+ Do | phone cannot see gmail"
            ),
        ):
            reply = bridge.handle_prompt("token", 420, 7, "one more thing")
        self.assertEqual(
            reply, "Ok.\n\nTodo is full. Close one.\nNot a todo line."
        )
        self.assertNotIn("Send pack extra", todo.read_text())
        self.assertNotIn("gmail", todo.read_text())

    def test_todo_marks_stale_after_seven_days(self):
        todo = self.repo / "20-studio" / "todo.md"
        todo.write_text(
            "# Todo\n\n## Open\n\n- 2026-08-01 Chase the old deposit.\n"
        )
        items = bridge.regulate_todo(today=date(2026, 8, 18))
        self.assertTrue(items[0][1])
        self.assertIn("STALE Chase the old deposit", todo.read_text())

    def test_list_write_keeps_only_two_trailers(self):
        cleaned, writes = bridge.extract_list_writes(
            "Ok.\n"
            "LIST+ Do | one\n"
            "LIST+ Done | two\n"
            "LIST+ Moving | three\n"
        )
        self.assertEqual(cleaned, "Ok.")
        self.assertEqual(
            writes, [("Do", "one"), ("Done", "two")]
        )


class SecureStateTest(RuntimeCase):
    def test_atomic_write_creates_owner_only_parent_and_file(self):
        path = self.state / "nested" / "state"
        bridge.ensure_private_dir(path.parent)
        bridge.atomic_write_text(path, "one", mode=0o600)
        self.assertEqual(path.read_text(), "one")
        self.assertEqual(file_mode(path.parent), 0o700)
        self.assertEqual(file_mode(path), 0o600)

    def test_atomic_replacement_preserves_owner_only_mode(self):
        path = self.state / "value"
        path.parent.mkdir(parents=True)
        path.write_text("old")
        path.chmod(0o644)
        bridge.atomic_write_text(path, "new", mode=0o600)
        self.assertEqual(path.read_text(), "new")
        self.assertEqual(file_mode(path), 0o600)

    def test_failed_atomic_replace_preserves_previous_value(self):
        path = self.state / "value"
        bridge.atomic_write_text(path, "old")
        with mock.patch.object(bridge.os, "replace", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                bridge.atomic_write_text(path, "new")
        self.assertEqual(path.read_text(), "old")

    def test_write_text_uses_secure_atomic_write(self):
        path = self.state / "last_run"
        bridge.write_text(path, "ok")
        self.assertEqual(path.read_text(), "ok")
        self.assertEqual(file_mode(path), 0o600)
        self.assertEqual(file_mode(self.state), 0o700)


class TelegramBoundaryTest(unittest.TestCase):
    def test_raw_timeout_is_normalized(self):
        with mock.patch.object(
            bridge.urllib.request, "urlopen", side_effect=TimeoutError("timed out")
        ):
            with self.assertRaisesRegex(RuntimeError, "telegram getMe.*timed out"):
                bridge.api("token", "getMe", timeout=1)

    def test_reaction_is_best_effort_for_raw_timeout(self):
        with mock.patch.object(
            bridge.urllib.request, "urlopen", side_effect=TimeoutError("timed out")
        ):
            bridge.react("token", 2, 3)

    def test_typing_pulse_is_best_effort_for_raw_timeout(self):
        with mock.patch.object(
            bridge.urllib.request, "urlopen", side_effect=TimeoutError("timed out")
        ):
            bridge.typing_pulse("token", 2, threading.Event())

    def test_absolute_http_deadline_beats_a_trickling_response(self):
        release = threading.Event()

        class SlowResponse:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def read(self, _limit=-1):
                release.wait(1)
                return b"done"

        started = bridge.time.monotonic()
        try:
            with mock.patch.object(
                bridge.urllib.request, "urlopen", return_value=SlowResponse()
            ):
                with self.assertRaisesRegex(TimeoutError, "phone request deadline"):
                    bridge.fetch_url_bytes(
                        bridge.urllib.request.Request("https://example.invalid"),
                        timeout=1,
                        deadline=bridge.time.monotonic() + 0.03,
                    )
            self.assertLess(bridge.time.monotonic() - started, 0.3)
        finally:
            release.set()


class FeedbackTimingTest(RuntimeCase):
    def test_slow_reaction_does_not_delay_grok_start(self):
        release_reaction = threading.Event()
        grok_started = threading.Event()

        def slow_feedback(*_args, **_kwargs):
            release_reaction.wait(1)

        def fake_grok(_prompt, new_session=False, deadline=None):
            del new_session, deadline
            grok_started.set()
            return "Done."

        errors: list[BaseException] = []

        def invoke():
            try:
                bridge.process_work_item(
                    "token",
                    {
                        "id": 1,
                        "chat_id": 420,
                        "message_id": 7,
                        "text": "local task",
                        "voice": None,
                    },
                )
            except BaseException as exc:  # pragma: no cover - reported below
                errors.append(exc)

        with mock.patch.object(
            bridge, "feedback_pulse", side_effect=slow_feedback
        ), mock.patch.object(
            bridge, "run_grok", side_effect=fake_grok
        ), mock.patch.object(bridge, "enqueue_outbox"), mock.patch.object(
            bridge, "deliver_outbox", return_value=True
        ):
            worker = threading.Thread(target=invoke)
            worker.start()
            self.assertTrue(
                grok_started.wait(0.4),
                "Grok stayed behind a best-effort Telegram reaction",
            )
            release_reaction.set()
            worker.join(1)
        self.assertFalse(worker.is_alive())
        self.assertEqual(errors, [])


class PhoneTextTest(unittest.TestCase):
    def test_grok_1_0_4_stream_fixture(self):
        stream = "\n".join([
            '{"type":"available_commands","tools":[],"commands":[]}',
            '{"type":"thought","data":"Answer briefly."}',
            '{"type":"text","data":"OK"}',
            '{"type":"usage","usage":{"input_tokens":20,"cache_read_input_tokens":10,"output_tokens":1}}',
            '{"type":"end","stopReason":"end_turn","sessionId":"live-shape"}',
        ])
        self.assertEqual(
            bridge.phone_text_from_stream(stream), ("OK", "live-shape")
        )

    def test_codex_stream_fixture(self):
        stream = "\n".join([
            '{"type":"thread.started","thread_id":"codex-thread"}',
            '{"type":"turn.started"}',
            '{"type":"item.completed","item":{"type":"agent_message","text":"Done."}}',
            '{"type":"turn.completed","usage":{"input_tokens":20,"output_tokens":2}}',
        ])
        self.assertEqual(
            bridge.phone_text_from_stream(stream), ("Done.", "codex-thread")
        )

    def test_drops_process_talk_before_last_tool(self):
        stream = "\n".join([
            '{"type":"text","data":"Sales. Loading founder context...\\n"}',
            '{"type":"tool_call","toolCallId":"1","toolName":"read_file"}',
            '{"type":"text","data":"One-pager is in the chat."}',
            '{"type":"end","sessionId":"abc"}',
        ])
        text, session_id = bridge.phone_text_from_stream(stream)
        self.assertEqual(text, "One-pager is in the chat.")
        self.assertEqual(session_id, "abc")

    def test_joins_final_chunks(self):
        stream = "\n".join([
            '{"type":"tool_call","toolCallId":"1"}',
            '{"type":"text","data":"Sent. "}',
            '{"type":"text","data":"PDF is in the chat."}',
            '{"type":"end","sessionId":"z"}',
        ])
        text, session_id = bridge.phone_text_from_stream(stream)
        self.assertEqual(text, "Sent. PDF is in the chat.")
        self.assertEqual(session_id, "z")

    def test_legacy_json(self):
        text, session_id = bridge.phone_text_from_stream(
            '{"text":"hi","sessionId":"s1"}'
        )
        self.assertEqual(text, "hi")
        self.assertEqual(session_id, "s1")

    def test_error_event(self):
        with self.assertRaises(RuntimeError):
            bridge.phone_text_from_stream('{"type":"error","message":"nope"}')

    def test_no_fallback_after_tool(self):
        stream = "\n".join([
            '{"type":"text","data":"I will inspect it"}',
            '{"type":"tool_call","toolCallId":"1"}',
            '{"type":"end","sessionId":"s"}',
        ])
        text, session_id = bridge.phone_text_from_stream(stream)
        self.assertEqual(text, "")
        self.assertEqual(session_id, "s")

    def test_incomplete_stream_with_text_is_kept(self):
        text, session_id = bridge.phone_text_from_stream(
            '{"type":"text","data":"partial"}'
        )
        self.assertEqual(text, "partial")
        self.assertEqual(session_id, "")

    def test_incomplete_stream_without_text_raises(self):
        with self.assertRaises(RuntimeError):
            bridge.phone_text_from_stream('{"type":"tool_call","toolCallId":"1"}')


class SessionResetTest(RuntimeCase):
    def make_history(self, size: int = 10) -> Path:
        history = self.root / "sessions" / "sid" / "chat_history.jsonl"
        history.parent.mkdir(parents=True)
        history.write_bytes(b"x" * size)
        return history

    def test_heavy_when_history_file_is_over_byte_fallback(self):
        history = self.make_history(500)
        with mock.patch.object(bridge, "session_history_path", return_value=history):
            self.assertTrue(bridge.session_is_heavy("sid", limit=100))
            self.assertFalse(bridge.session_is_heavy("sid", limit=10_000))

    def test_missing_history_drops_existing_session(self):
        with mock.patch.object(bridge, "session_history_path", return_value=None):
            self.assertTrue(bridge.should_drop_session("stale-id"))
            self.assertFalse(bridge.should_drop_session(""))

    def test_wrong_effective_effort_drops_session(self):
        history = self.make_history()
        with mock.patch.object(
            bridge, "session_history_path", return_value=history
        ), mock.patch.object(
            bridge, "session_metadata",
            return_value={
                "effort": "xhigh",
                "prompt_tokens": 10,
                "history_bytes": 10,
            },
        ):
            self.assertTrue(bridge.should_drop_session("sid"))

    def test_claude_engine_does_not_drop_for_missing_grok_history(self):
        with mock.patch.object(bridge, "desk_engine", return_value="claude"):
            self.assertEqual(bridge.session_reset_reason("claude-sid"), "")

    def test_codex_engine_does_not_drop_for_missing_grok_history(self):
        with mock.patch.object(bridge, "desk_engine", return_value="codex"):
            self.assertEqual(bridge.session_reset_reason("codex-sid"), "")

    def test_prompt_token_total_does_not_drop_a_live_session(self):
        history = self.make_history()
        with mock.patch.object(
            bridge, "session_history_path", return_value=history
        ), mock.patch.object(
            bridge, "session_metadata",
            return_value={
                "effort": "medium",
                "prompt_tokens": 250_000,
                "history_bytes": 10,
            },
        ):
            self.assertFalse(bridge.should_drop_session("sid"))
            self.assertEqual(bridge.session_reset_reason("sid"), "")

    def test_matching_session_under_budget_is_kept(self):
        history = self.make_history()
        with mock.patch.object(
            bridge, "SESSION_PROMPT_TOKENS", 100, create=True
        ), mock.patch.object(
            bridge, "session_history_path", return_value=history
        ), mock.patch.object(
            bridge, "session_metadata",
            return_value={
                "effort": "medium",
                "prompt_tokens": 99,
                "history_bytes": 10,
            },
        ):
            self.assertFalse(bridge.should_drop_session("sid"))

    def test_history_observed_effort_wins_over_stale_saved_metadata(self):
        history = self.root / "sessions" / "sid" / "chat_history.jsonl"
        history.parent.mkdir(parents=True)
        history.write_text(
            json.dumps(
                {
                    "type": "assistant",
                    "model_id": "grok-4.6-build",
                    "reasoning_effort": "xhigh",
                }
            )
            + "\n"
        )
        bridge.write_json(
            bridge.SESSION_META_FILE,
            {
                "session_id": "sid",
                "model": "grok-4.6-build",
                "effort": "medium",
                "prompt_tokens": 10,
            },
        )
        with mock.patch.object(bridge, "session_history_path", return_value=history):
            metadata = bridge.session_metadata("sid")
            self.assertEqual(metadata["effort"], "xhigh")
            self.assertTrue(bridge.should_drop_session("sid"))


class StreamSchemaTest(unittest.TestCase):
    def fresh_meta(self) -> dict:
        return {
            "first_event_seconds": None,
            "tool_events": 0,
            "model": "",
            "effort": "",
            "prompt_tokens": 0,
            "output_tokens": 0,
            "reasoning_tokens": 0,
        }

    def test_tool_call_update_counts_as_meaningful_progress(self):
        event = {"type": "tool_call_update", "toolCallId": "one"}
        self.assertTrue(bridge._meaningful_stream_event(event))

    def test_cached_input_is_included_in_session_prompt_budget(self):
        meta = self.fresh_meta()
        bridge._update_stream_meta(
            {
                "type": "usage",
                "data": {
                    "input_tokens": 1_000,
                    "cache_read_input_tokens": 79_000,
                },
            },
            meta,
        )
        self.assertEqual(meta["prompt_tokens"], 80_000)

    def test_current_usage_envelope_is_parsed(self):
        meta = self.fresh_meta()
        bridge._update_stream_meta(
            {
                "type": "usage",
                "usage": {
                    "input_tokens": 1_000,
                    "cache_read_input_tokens": 2_000,
                    "output_tokens": 12,
                    "reasoning_tokens": 4,
                },
            },
            meta,
        )
        self.assertEqual(meta["prompt_tokens"], 3_000)
        self.assertEqual(meta["output_tokens"], 12)
        self.assertEqual(meta["reasoning_tokens"], 4)

    def test_claude_tool_use_event_counts_as_live_capability(self):
        meta = self.fresh_meta()
        bridge._update_stream_meta(
            {
                "type": "assistant",
                "message": {
                    "content": [{"type": "tool_use", "name": "mcp__claude_ai_Gmail__search_threads"}]
                },
            },
            meta,
        )
        self.assertEqual(meta["tool_events"], 1)

    def test_live_google_prompt_forces_workspace_lookup(self):
        with mock.patch.dict(os.environ, {"DESK_GOOGLE": "live"}):
            prompt = bridge.live_google_prompt("What was my latest Gmail?")
        self.assertIn("LIVE WORKSPACE REQUIREMENT", prompt)
        self.assertIn("must call the connected Gmail, Calendar, or Drive tool", prompt)
        self.assertIn("Europe/Dublin", prompt)
        self.assertRegex(prompt, r"Current local time: \d{4}-\d{2}-\d{2}")


class GrokStreamingTest(RuntimeCase):
    def run_with_process(
        self,
        process: PipeProcess,
        *,
        first: float = 0.04,
        idle: float = 0.06,
        total: float = 0.12,
        drop_session: bool = False,
    ) -> tuple[str, mock.Mock]:
        self.addCleanup(process.close)
        popen = mock.Mock(return_value=process)
        with mock.patch.object(bridge.subprocess, "Popen", popen), mock.patch.object(
            bridge, "GROK_FIRST_EVENT_TIMEOUT", first, create=True
        ), mock.patch.object(
            bridge, "GROK_IDLE_TIMEOUT", idle, create=True
        ), mock.patch.object(bridge, "GROK_TIMEOUT", total), mock.patch.object(
            bridge, "should_drop_session", return_value=drop_session
        ):
            reply = bridge.run_grok("a private prompt")
        return reply, popen

    def test_empty_engine_reply_gets_a_plain_sentence(self):
        stream = [
            (0.0, json.dumps({
                "type": "session", "sessionId": "s1",
                "model": "grok-4.6-build", "effort": "medium",
            }) + "\n"),
            (0.0, json.dumps({"type": "end", "sessionId": "s1"}) + "\n"),
        ]
        process = PipeProcess(stream)
        reply, _ = self.run_with_process(process)
        self.assertEqual(reply, "The desk came back with nothing. Send it again.")
        self.assertIn("no reply text", bridge.read_text(bridge.LAST_ERROR_FILE))

    def test_live_google_answer_without_tool_event_is_rejected(self):
        process = PipeProcess(success_stream("Stale answer."))
        self.addCleanup(process.close)
        with mock.patch.dict(os.environ, {"DESK_GOOGLE": "live"}), mock.patch.object(
            bridge.subprocess, "Popen", return_value=process
        ):
            with self.assertRaises(bridge.EngineUnavailable) as caught:
                bridge.run_engine_once("What was my latest Gmail?", "claude")
        self.assertEqual(caught.exception.reason, "google-tools")

    def test_streaming_success_uses_medium_ten_turn_phone_command(self):
        process = PipeProcess(success_stream())
        reply, popen = self.run_with_process(process)
        self.assertEqual(reply, "Done.")
        command = popen.call_args.args[0]
        self.assertIn("--effort", command)
        self.assertEqual(command[command.index("--effort") + 1], "medium")
        self.assertIn("--max-turns", command)
        self.assertEqual(command[command.index("--max-turns") + 1], "10")
        self.assertEqual(bridge.read_text(bridge.SESSION_FILE), "fresh-session")

    def test_first_event_timeout_returns_provider_busy_sentence(self):
        process = PipeProcess([], keep_open=0.5)
        reply, _ = self.run_with_process(process, first=0.02, idle=0.2, total=0.3)
        self.assertEqual(reply, "Grok is busy. Try again in a minute.")
        self.assertTrue(process.terminated or process.killed)

    def test_capacity_retry_event_fails_fast_before_any_tool(self):
        process = PipeProcess(
            [
                (
                    0.0,
                    json.dumps(
                        {
                            "type": "retrying",
                            "reason": "model currently at capacity",
                            "retry_state": {"attempt": 1},
                        }
                    )
                    + "\n",
                )
            ],
            keep_open=0.5,
        )
        reply, _ = self.run_with_process(process, first=0.2, idle=0.2, total=0.3)
        self.assertEqual(reply, "Grok is busy. Try again in a minute.")
        self.assertTrue(process.terminated or process.killed)

    def test_usage_limit_after_tool_returns_error_without_safe_fallback(self):
        process = PipeProcess(
            [
                (0.0, '{"type":"tool_call","toolCallId":"write-one"}\n'),
                (0.0, '{"type":"error","message":"usage limit reached"}\n'),
            ],
            returncode=1,
        )
        self.addCleanup(process.close)
        with mock.patch.object(
            bridge.subprocess, "Popen", return_value=process
        ), mock.patch.object(
            bridge, "GROK_FIRST_EVENT_TIMEOUT", 0.05
        ), mock.patch.object(
            bridge, "GROK_IDLE_TIMEOUT", 0.05
        ), mock.patch.object(bridge, "GROK_TIMEOUT", 0.2):
            reply = bridge.run_engine_once("do it", "grok")
        self.assertEqual(reply, bridge.PHONE_FAIL)

    def test_usage_limit_before_tool_allows_safe_fallback(self):
        process = PipeProcess(
            [(0.0, '{"type":"error","message":"usage limit reached"}\n')],
            returncode=1,
        )
        self.addCleanup(process.close)
        with mock.patch.object(
            bridge.subprocess, "Popen", return_value=process
        ), mock.patch.object(
            bridge, "GROK_FIRST_EVENT_TIMEOUT", 0.05
        ), mock.patch.object(
            bridge, "GROK_IDLE_TIMEOUT", 0.05
        ), mock.patch.object(bridge, "GROK_TIMEOUT", 0.2):
            with self.assertRaises(bridge.EngineUnavailable) as caught:
                bridge.run_engine_once("do it", "grok")
        self.assertEqual(caught.exception.reason, "limit")

    def test_idle_timeout_after_first_event_returns_desk_timeout(self):
        process = PipeProcess(
            [(0.0, '{"type":"text","data":"partial"}\n')], keep_open=0.5
        )
        reply, _ = self.run_with_process(process, first=0.05, idle=0.02, total=0.3)
        self.assertEqual(reply, "The desk timed out. Send it again or try a smaller ask.")
        self.assertTrue(process.terminated or process.killed)

    def test_total_timeout_wins_while_events_keep_arriving(self):
        events = [
            (0.008, json.dumps({"type": "text", "data": "."}) + "\n")
            for _ in range(20)
        ]
        process = PipeProcess(events, keep_open=0.2)
        reply, _ = self.run_with_process(
            process, first=0.03, idle=0.03, total=0.055
        )
        self.assertEqual(reply, "The desk timed out. Send it again or try a smaller ask.")
        self.assertTrue(process.terminated or process.killed)

    def test_reset_session_runs_fresh_and_says_so(self):
        bridge.atomic_write_text(bridge.SESSION_FILE, "old-session")
        process = PipeProcess(success_stream("Fresh answer."))
        reply, popen = self.run_with_process(process, drop_session=True)
        command = popen.call_args.args[0]
        self.assertNotIn("--resume", command)
        self.assertTrue(
            reply.startswith("Session reset. The last one was too big or gone.")
        )
        self.assertTrue(reply.endswith("Fresh answer."))

    def test_max_turns_with_text_is_delivered_despite_nonzero_exit(self):
        session_id = "max-turns-session"
        events = [
            (0.0, json.dumps({
                "type": "session", "sessionId": session_id,
                "model": "grok-4.6-build", "effort": "medium",
            }) + "\n"),
            (0.0, json.dumps({"type": "text", "data": "Here is the short answer."}) + "\n"),
            (0.0, json.dumps({
                "type": "turn_ended",
                "outcome": "cancelled",
                "cancellation_context": {"reason": "max_turns_reached", "limit": 10},
            }) + "\n"),
        ]
        process = PipeProcess(events, returncode=1)
        reply, _ = self.run_with_process(process)
        self.assertEqual(reply, "Here is the short answer.")
        self.assertEqual(bridge.read_text(bridge.LAST_ERROR_FILE), "grok max_turns_reached")

    def test_nonzero_exit_without_text_keeps_fail_sentence(self):
        process = PipeProcess(
            [(0.0, '{"type":"session","sessionId":"x"}\n')],
            returncode=1,
            stderr="boom",
        )
        reply, _ = self.run_with_process(process)
        self.assertEqual(reply, "Desk hit an error. /status")
        self.assertEqual(bridge.read_text(bridge.LAST_ERROR_FILE), "boom")

    def test_phone_grok_launch_attaches_gateway_google_tools(self):
        cmd = bridge.desk_command("hello", "")
        self.assertEqual(cmd[0], bridge.grok_bin())
        self.assertIn("-p", cmd)
        self.assertIn("hello", cmd)
        self.assertIn("--yolo", cmd)
        self.assertIn("--output-format", cmd)
        self.assertIn("streaming-json", cmd)
        self.assertIn(bridge.DESK_RULES, cmd)
        self.assertNotIn("--leader", cmd)
        env = bridge.grok_env()
        self.assertEqual(env[bridge.GATEWAY_TOOLS_ENV], "1")
        self.assertEqual(env[bridge.MANAGED_MCPS_ENV], "1")

    def test_claude_engine_builds_claude_print_command(self):
        with mock.patch.object(bridge, "desk_engine", return_value="claude"):
            cmd = bridge.desk_command("hello", "")
        self.assertEqual(cmd[0], bridge.claude_bin())
        self.assertIn("-p", cmd)
        self.assertIn("--append-system-prompt", cmd)
        self.assertNotIn(bridge.grok_bin(), cmd)

    def test_codex_engine_builds_unattended_json_command(self):
        cmd = bridge.desk_command("hello", "", engine="codex")
        self.assertEqual(cmd[:2], [bridge.codex_bin(), "exec"])
        self.assertIn("--json", cmd)
        self.assertIn("--approve-for-me", cmd)
        self.assertIn('model_reasoning_effort="medium"', cmd)
        self.assertIn(bridge.DESK_RULES, cmd[-1])

    def test_codex_tool_event_is_counted_before_provider_error(self):
        meta = {
            "first_event_seconds": None,
            "tool_events": 0,
            "model": "",
            "effort": "",
            "prompt_tokens": 0,
            "output_tokens": 0,
            "reasoning_tokens": 0,
        }
        bridge._update_stream_meta(
            {
                "type": "item.completed",
                "item": {"type": "file_change", "changes": []},
            },
            meta,
        )
        self.assertEqual(meta["tool_events"], 1)

    def test_claude_result_event_is_the_phone_text(self):
        stream = "\n".join([
            '{"type":"assistant","message":{"content":[{"type":"text","text":"Hi."}]}}',
            '{"type":"result","result":"Parked.","session_id":"claude-sid"}',
        ])
        text, session_id = bridge.phone_text_from_stream(stream)
        self.assertEqual(text, "Parked.")
        self.assertEqual(session_id, "claude-sid")

    def test_metrics_do_not_store_prompt_content(self):
        private_prompt = "private words that must not enter metrics"
        process = PipeProcess(success_stream())
        self.addCleanup(process.close)
        with mock.patch.object(
            bridge.subprocess, "Popen", return_value=process
        ), mock.patch.object(bridge, "should_drop_session", return_value=False):
            self.assertEqual(bridge.run_grok(private_prompt), "Done.")
        metrics = bridge.METRICS_FILE.read_text()
        self.assertNotIn(private_prompt, metrics)
        self.assertEqual(file_mode(bridge.METRICS_FILE), 0o600)
        events = [json.loads(line) for line in metrics.splitlines() if line.strip()]
        completed = [
            event
            for event in events
            if event.get("stage") == "grok" and event.get("outcome") == "ok"
        ]
        self.assertEqual(len(completed), 1)
        self.assertIn("first_event_seconds", completed[0])
        self.assertEqual(completed[0]["prompt_tokens"], 1200)


class AutoFallbackTest(RuntimeCase):
    def setUp(self):
        super().setUp()
        self.write_owner_secrets("42")
        with self.secrets.open("a") as handle:
            handle.write(
                "export DESK_ENGINE=auto\n"
                "export DESK_ENGINE_ORDER=claude,codex,grok\n"
            )

    def test_usage_limit_falls_through_and_sticks_to_working_engine(self):
        with mock.patch.object(
            bridge,
            "run_engine_once",
            side_effect=[bridge.EngineUnavailable("claude", "limit"), "Done."],
        ) as run:
            reply = bridge.run_grok("private ask")
        self.assertEqual(
            reply, "Using Codex — Claude hit its limit.\n\nDone."
        )
        self.assertEqual([call.args[1] for call in run.call_args_list], ["claude", "codex"])
        self.assertTrue(run.call_args_list[0].kwargs["new_session"])
        self.assertTrue(run.call_args_list[1].kwargs["new_session"])
        state = bridge.engine_state()
        self.assertEqual(state["active"], "codex")
        self.assertIn("claude", state["unavailable"])
        self.assertNotIn("private ask", bridge.ENGINE_STATE_FILE.read_text())

    def test_cooling_engine_is_skipped_then_rejoins_after_expiry(self):
        bridge.mark_engine_unavailable("claude", "limit", now=1000)
        bridge.mark_engine_active("codex", now=1000)
        self.assertEqual(bridge.engine_candidates(now=1001), ["codex", "grok"])
        self.assertEqual(
            bridge.engine_candidates(now=1000 + bridge.ENGINE_COOLDOWN_SECONDS + 1),
            ["claude", "codex", "grok"],
        )

    def test_failed_preferred_probe_restores_fallback_session(self):
        bridge.write_text(bridge.SESSION_FILE, "codex-session")
        bridge.write_json(
            bridge.SESSION_META_FILE,
            {"session_id": "codex-session", "engine": "codex", "effort": "medium"},
        )
        bridge.mark_engine_active("codex")
        with mock.patch.object(
            bridge,
            "run_engine_once",
            side_effect=[bridge.EngineUnavailable("claude", "limit"), "Continued."],
        ) as run:
            reply = bridge.run_grok("follow-up")
        self.assertTrue(run.call_args_list[0].kwargs["new_session"])
        self.assertFalse(run.call_args_list[1].kwargs["new_session"])
        self.assertEqual(bridge.read_text(bridge.SESSION_FILE), "codex-session")
        self.assertTrue(reply.endswith("Continued."))

    def test_all_unavailable_has_one_plain_sentence(self):
        failures = [
            bridge.EngineUnavailable("claude", "limit"),
            bridge.EngineUnavailable("codex", "limit"),
            bridge.EngineUnavailable("grok", "limit"),
        ]
        with mock.patch.object(
            bridge, "run_engine_once", side_effect=failures
        ) as run:
            self.assertEqual(bridge.run_grok("ask"), bridge.PHONE_ALL_ENGINES)
        self.assertEqual(run.call_count, 3)

    def test_failure_after_tool_does_not_try_another_engine(self):
        with mock.patch.object(
            bridge, "run_engine_once", return_value=bridge.PHONE_FAIL
        ) as run:
            self.assertEqual(bridge.run_grok("do it"), bridge.PHONE_FAIL)
        run.assert_called_once()
        self.assertEqual(bridge.engine_state()["active"], "claude")

    def test_status_shows_mode_active_and_cooldown(self):
        bridge.mark_engine_unavailable("claude", "limit")
        bridge.mark_engine_active("codex")
        reply = bridge.handle_prompt("token", 420, 1, "/status")
        self.assertIn("engine: auto", reply)
        self.assertIn("active: codex", reply)
        self.assertRegex(reply, r"unavailable: claude \d+m")


class OutboxTest(RuntimeCase):
    def test_enqueue_is_idempotent_by_source_id_and_owner_only(self):
        bridge.enqueue_outbox("update:7", 420, "Completed result")
        bridge.enqueue_outbox("update:7", 420, "Completed result")
        data = json.loads(bridge.OUTBOX_FILE.read_text())
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["chat_id"], 420)
        self.assertEqual(data[0]["parts"], ["Completed result"])
        self.assertEqual(file_mode(bridge.OUTBOX_FILE), 0o600)

    def test_failed_delivery_stays_pending_then_retries(self):
        bridge.enqueue_outbox("update:7", 420, "Completed result")
        with mock.patch.object(
            bridge, "api", side_effect=RuntimeError("telegram unavailable")
        ) as failed_send:
            self.assertFalse(bridge.deliver_outbox("token"))
        failed_send.assert_called_once_with(
            "token",
            "sendMessage",
            {"chat_id": 420, "text": "Completed result"},
            timeout=bridge.TG_SEND_TIMEOUT,
        )
        self.assertTrue(bridge.OUTBOX_FILE.exists())
        with mock.patch.object(bridge, "api") as successful_send:
            self.assertTrue(bridge.deliver_outbox("token"))
        successful_send.assert_called_once_with(
            "token",
            "sendMessage",
            {"chat_id": 420, "text": "Completed result"},
            timeout=bridge.TG_SEND_TIMEOUT,
        )
        if bridge.OUTBOX_FILE.exists():
            self.assertEqual(json.loads(bridge.OUTBOX_FILE.read_text()), [])

    def test_partial_chunk_retry_does_not_resend_delivered_part(self):
        text = ("first " * 800) + "final"
        bridge.enqueue_outbox("update:8", 420, text)
        saved = json.loads(bridge.OUTBOX_FILE.read_text())
        self.assertGreater(len(saved[0]["parts"]), 1)
        first_part, second_part = saved[0]["parts"][:2]
        with mock.patch.object(
            bridge,
            "api",
            side_effect=[{"ok": True}, RuntimeError("telegram unavailable")],
        ) as first_attempt:
            self.assertFalse(bridge.deliver_outbox("token"))
        self.assertEqual(first_attempt.call_count, 2)
        pending = json.loads(bridge.OUTBOX_FILE.read_text())
        self.assertEqual(pending[0]["next_part"], 1)
        with mock.patch.object(bridge, "api", return_value={"ok": True}) as retry:
            self.assertTrue(bridge.deliver_outbox("token"))
        sent_texts = [call.args[2]["text"] for call in retry.call_args_list]
        self.assertNotIn(first_part, sent_texts)
        self.assertIn(second_part, sent_texts)

    def test_retry_does_not_rerun_grok(self):
        job = {
            "id": 7,
            "chat_id": 420,
            "message_id": 70,
            "text": "do it",
            "voice": None,
        }
        with mock.patch.object(
            bridge, "feedback_pulse"
        ), mock.patch.object(
            bridge, "run_grok", return_value="Completed result"
        ) as run_grok, mock.patch.object(
            bridge, "api", side_effect=RuntimeError("telegram unavailable")
        ):
            bridge.process_work_item("token", job)
        run_grok.assert_called_once()
        self.assertEqual(run_grok.call_args.args, ("do it",))
        self.assertIsInstance(run_grok.call_args.kwargs.get("deadline"), float)
        self.assertTrue(bridge.OUTBOX_FILE.exists())
        with mock.patch.object(bridge, "api") as send:
            self.assertTrue(bridge.deliver_outbox("token"))
        send.assert_called_once_with(
            "token",
            "sendMessage",
            {"chat_id": 420, "text": "Completed result"},
            timeout=bridge.TG_SEND_TIMEOUT,
        )
        run_grok.assert_called_once()

    def test_completed_inbox_job_is_retired_before_delivery(self):
        job = {
            "id": 10,
            "chat_id": 420,
            "message_id": 110,
            "text": "do it",
            "voice": None,
            "enqueued_at": bridge.time.time(),
        }
        bridge.persist_inbox_job(job)
        bridge.mark_inbox_job(10, "running")

        def inspect_delivery(_token):
            self.assertEqual(bridge.inbox_items(), [])
            self.assertEqual(bridge.pending_outbox_count(), 1)
            return True

        with mock.patch.object(bridge, "feedback_pulse"), mock.patch.object(
            bridge, "run_grok", return_value="Done"
        ), mock.patch.object(
            bridge, "deliver_outbox", side_effect=inspect_delivery
        ):
            bridge.process_work_item("token", job)

    def test_live_worker_only_wakes_delivery_thread(self):
        job = {
            "id": 11,
            "chat_id": 420,
            "message_id": 111,
            "text": "do it",
            "voice": None,
            "enqueued_at": bridge.time.time(),
        }
        notify = mock.Mock()
        with mock.patch.object(bridge, "feedback_pulse"), mock.patch.object(
            bridge, "run_grok", return_value="Done"
        ), mock.patch.object(
            bridge, "deliver_outbox", side_effect=AssertionError("must be asynchronous")
        ):
            bridge.process_work_item("token", job, delivery_notify=notify)
        notify.assert_called_once_with()
        self.assertEqual(bridge.pending_outbox_count(), 1)

    def test_recovery_offset_is_never_written_backward(self):
        bridge.write_text(bridge.OFFSET_FILE, "20")
        self.assertEqual(bridge.advance_offset(11), 20)
        self.assertEqual(bridge.read_offset(), 20)


class VoiceTest(RuntimeCase):
    def test_prefetch_captures_audio_before_worker_reaches_voice(self):
        with mock.patch.object(
            bridge, "telegram_file", return_value=(b"voice", "voice.ogg")
        ):
            bridge.update_voice_record("voice-9", status="queued")
            bridge.prefetch_voice("token", "voice-9", {"file_id": "file"})
        record = json.loads((self.state / "voice" / "voice-9.json").read_text())
        self.assertEqual(record["status"], "downloaded")
        self.assertTrue((self.state / "voice" / record["audio_file"]).is_file())

    def test_malformed_telegram_size_is_a_capture_error(self):
        with mock.patch.object(
            bridge, "api", return_value={"result": {"file_size": "wat", "file_path": "voice.ogg"}}
        ):
            with self.assertRaises(bridge.VoiceCaptureError):
                bridge.telegram_file("token", "file")

    def test_oversized_voice_has_plain_boundary_sentence(self):
        with mock.patch.object(
            bridge, "load_secrets", return_value={"ELEVENLABS_API_KEY": "key"}
        ), mock.patch.object(
            bridge, "telegram_file", side_effect=bridge.VoiceTooLarge("voice note is too large")
        ):
            self.assertEqual(
                bridge.handle_voice("token", 420, 7, {"file_id": "file"}),
                "That voice note is too large. Send it in two parts.",
            )

    def test_intake_only_voice_is_saved_without_running_engine(self):
        with mock.patch.object(
            bridge, "load_secrets", return_value={"ELEVENLABS_API_KEY": "key"}
        ), mock.patch.object(
            bridge, "telegram_file", return_value=(b"voice", "voice.ogg")
        ), mock.patch.object(
            bridge, "transcribe_voice",
            return_value="Save this as intake. No action yet. Meeting notes about the launch.",
        ), mock.patch.object(bridge, "handle_prompt") as handle_prompt:
            reply = bridge.handle_voice("token", 420, 7, {"file_id": "file"})
        self.assertIn("Voice saved. No actions added.", reply)
        handle_prompt.assert_not_called()
        record = json.loads(next((self.state / "voice").glob("*.json")).read_text())
        self.assertEqual(record["status"], "held")

    def test_saved_receipt_is_emitted_after_transcript_persistence(self):
        saved = mock.Mock()
        with mock.patch.object(
            bridge, "load_secrets", return_value={"ELEVENLABS_API_KEY": "key"}
        ), mock.patch.object(
            bridge, "telegram_file", return_value=(b"voice", "voice.ogg")
        ), mock.patch.object(
            bridge, "transcribe_voice", return_value="book the room"
        ), mock.patch.object(bridge, "handle_prompt", return_value="Done"):
            reply = bridge.handle_voice(
                "token", 420, 7, {"file_id": "file"}, saved_notify=saved
            )
        self.assertEqual(reply, "Done")
        saved.assert_called_once_with(bridge.VOICE_SAVED_WORKING)
        record = json.loads(next((self.state / "voice").glob("*.json")).read_text())
        self.assertEqual(record["status"], "completed")

    def test_cancelled_voice_never_starts_engine_after_capture(self):
        with mock.patch.object(
            bridge, "load_secrets", return_value={"ELEVENLABS_API_KEY": "key"}
        ), mock.patch.object(
            bridge, "telegram_file", return_value=(b"voice", "voice.ogg")
        ), mock.patch.object(
            bridge, "transcribe_voice", return_value="launch notes"
        ), mock.patch.object(bridge, "handle_prompt") as handle_prompt:
            reply = bridge.handle_voice(
                "token", 420, 7, {"file_id": "file"}, can_start=lambda: False
            )
        self.assertIn("Voice saved. No actions added.", reply)
        handle_prompt.assert_not_called()

    def test_voice_capture_and_transcript_are_durable_before_engine(self):
        observed = {}

        def engine(*_args, **_kwargs):
            records = list((self.state / "voice").glob("*.json"))
            self.assertEqual(len(records), 1)
            record = json.loads(records[0].read_text())
            observed.update(record)
            # The engine marker is written only after this durable transcript
            # exists; its presence proves the no-replay boundary is crossed.
            self.assertEqual(record["status"], "engine-running")
            self.assertEqual(record["transcript"], "book the room")
            self.assertTrue((self.state / "voice" / record["audio_file"]).is_file())
            return "Done."

        with mock.patch.object(
            bridge, "load_secrets", return_value={"ELEVENLABS_API_KEY": "key"}
        ), mock.patch.object(
            bridge, "feedback_pulse"
        ), mock.patch.object(
            bridge, "telegram_file", return_value=(b"voice", "voice.ogg")
        ), mock.patch.object(
            bridge, "transcribe_voice", return_value="book the room"
        ), mock.patch.object(
            bridge, "run_grok", side_effect=engine
        ), mock.patch.object(bridge, "enqueue_outbox"), mock.patch.object(
            bridge, "deliver_outbox", return_value=True
        ), mock.patch.object(
            bridge, "safe_send", return_value=True
        ):
            bridge.process_work_item(
                "token",
                {
                    "id": 7,
                    "chat_id": 420,
                    "message_id": 70,
                    "text": "",
                    "voice": {"file_id": "file", "mime_type": "audio/ogg"},
                },
            )
        self.assertEqual(observed["status"], "engine-running")
        self.assertEqual(observed["transcript_length"], len("book the room"))

    def test_queued_voice_is_captured_after_request_budget(self):
        expired = bridge.time.monotonic() - 1
        with mock.patch.object(bridge, "feedback_pulse"), mock.patch.object(
            bridge, "handle_voice", return_value="saved"
        ) as handle, mock.patch.object(
            bridge, "enqueue_outbox"
        ), mock.patch.object(bridge, "deliver_outbox", return_value=True):
            bridge.process_work_item(
                "token",
                {
                    "id": 8,
                    "chat_id": 420,
                    "message_id": 80,
                    "text": "",
                    "voice": {"file_id": "file"},
                    "enqueued_at": 1.0,
                    "expires_at": expired,
                },
            )
        handle.assert_called_once()
        self.assertGreater(handle.call_args.kwargs["deadline"], bridge.time.monotonic())

    def test_waiting_pulse_covers_transcription(self):
        pulse_started = threading.Event()

        def pulse(_token, _chat_id, _message_id, stop):
            pulse_started.set()
            stop.wait(0.5)

        def transcribe(*_args, **_kwargs):
            self.assertTrue(
                pulse_started.wait(0.3),
                "typing did not begin until after voice transcription",
            )
            return "book the room"

        with mock.patch.object(
            bridge, "load_secrets", return_value={"ELEVENLABS_API_KEY": "key"}
        ), mock.patch.object(
            bridge, "feedback_pulse", side_effect=pulse
        ), mock.patch.object(
            bridge, "telegram_file", return_value=(b"voice", "voice.ogg")
        ), mock.patch.object(
            bridge, "transcribe_voice", side_effect=transcribe
        ), mock.patch.object(bridge, "handle_prompt") as handle_prompt, mock.patch.object(
            bridge, "enqueue_outbox"
        ), mock.patch.object(
            bridge, "deliver_outbox", return_value=True
        ), mock.patch.object(
            bridge, "safe_send", return_value=True
        ):
            bridge.process_work_item(
                "token",
                {
                    "id": 7,
                    "chat_id": 420,
                    "message_id": 70,
                    "text": "",
                    "voice": {"file_id": "file", "mime_type": "audio/ogg"},
                },
            )
        handle_prompt.assert_called_once_with(
            "", 0, None, "Voice note: book the room", deadline=mock.ANY, from_voice=True
        )

    def test_expired_voice_budget_never_starts_grok(self):
        with mock.patch.object(
            bridge, "load_secrets", return_value={"ELEVENLABS_API_KEY": "key"}
        ), mock.patch.object(bridge, "handle_prompt") as handle_prompt:
            reply = bridge.handle_voice(
                "token",
                420,
                7,
                {"file_id": "file", "mime_type": "audio/ogg"},
                deadline=bridge.time.monotonic() - 1,
            )
        self.assertEqual(reply, bridge.PHONE_TIMEOUT)
        handle_prompt.assert_not_called()

    def test_voice_transcription_failure_has_plain_sentence(self):
        with mock.patch.object(
            bridge, "load_secrets", return_value={"ELEVENLABS_API_KEY": "key"}
        ), mock.patch.object(
            bridge, "telegram_file", side_effect=RuntimeError("bad file")
        ):
            reply = bridge.handle_voice(
                "token", 420, 7,
                {"file_id": "file", "mime_type": "audio/ogg"},
            )
        self.assertEqual(
            reply, "Couldn't transcribe that. Try again or type it."
        )


class GoogleOffTest(RuntimeCase):
    def test_google_is_off_by_default(self):
        self.assertFalse(bridge.google_live_enabled())
        prompt = bridge.live_google_prompt("What was my latest Gmail?")
        self.assertEqual(prompt, "What was my latest Gmail?")

    def test_live_flag_reads_secrets_or_env(self):
        self.write_owner_secrets()
        with open(self.secrets, "a") as handle:
            handle.write("export DESK_GOOGLE=live\n")
        self.assertTrue(bridge.google_live_enabled())
        with mock.patch.dict(os.environ, {"DESK_GOOGLE": "off"}):
            self.assertFalse(bridge.google_live_enabled())

    def test_off_mode_keeps_an_answer_without_a_tool_event(self):
        process = PipeProcess(success_stream("From the card: Draft 4 is with them."))
        self.addCleanup(process.close)
        with mock.patch.object(bridge.subprocess, "Popen", return_value=process):
            reply = bridge.run_engine_once("What was my latest Gmail?", "claude")
        self.assertEqual(reply, "From the card: Draft 4 is with them.")

    def test_off_mode_desk_rules_park_current_data_asks(self):
        rules = bridge.desk_rules().lower()
        self.assertIn("this seat has no live gmail", rules)
        self.assertNotIn("live workspace requirement", rules)
        command = bridge.desk_command("Read my latest Gmail", "", engine="grok")
        self.assertIn(bridge.desk_rules(), command)


class FileSendTest(RuntimeCase):
    def make_file(self, rel: str = "20-studio/report.pdf", content: bytes = b"%PDF-fake") -> Path:
        target = self.repo / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        return target

    def test_extract_strips_trailer_and_keeps_text(self):
        text, paths = bridge.extract_file_sends(
            "Month 1 report is ready.\nFILE+ 20-studio/report.pdf"
        )
        self.assertEqual(text, "Month 1 report is ready.")
        self.assertEqual(paths, ["20-studio/report.pdf"])

    def test_extract_keeps_only_one_path(self):
        text, paths = bridge.extract_file_sends(
            "Two files.\nFILE+ a.pdf\nFILE+ b.pdf"
        )
        self.assertEqual(paths, ["a.pdf"])
        self.assertNotIn("FILE+", text)

    def test_validate_repo_relative_path(self):
        made = self.make_file()
        resolved = bridge.validate_file_send("20-studio/report.pdf")
        self.assertEqual(resolved, made.resolve())

    def test_validate_refuses_traversal_hidden_missing_and_outside(self):
        self.make_file()
        downloads = self.root / "Downloads"
        downloads.mkdir()
        (downloads / "export.pdf").write_bytes(b"data")
        with mock.patch.object(
            bridge, "file_send_roots", return_value=[self.repo, downloads]
        ):
            self.assertEqual(
                bridge.validate_file_send(str(downloads / "export.pdf")),
                (downloads / "export.pdf").resolve(),
            )
            for bad in (
                "../outside.pdf",
                "/etc/hosts",
                str(self.root / "secret" / "x.pdf"),
                "20-studio/missing.pdf",
                "20-studio",
                ".git/config",
            ):
                with self.subTest(bad=bad):
                    with self.assertRaises(ValueError):
                        bridge.validate_file_send(bad)

    def test_validate_refuses_oversize(self):
        self.make_file(content=b"x" * 16)
        with mock.patch.object(bridge, "TG_DOC_MAX_BYTES", 8, create=True):
            with self.assertRaises(ValueError):
                bridge.validate_file_send("20-studio/report.pdf")

    def test_send_document_posts_multipart_to_senddocument(self):
        doc = self.make_file()
        with mock.patch.object(
            bridge, "fetch_url_bytes", return_value=b'{"ok": true, "result": {}}'
        ) as fetch:
            bridge.send_document("token", 420, doc)
        req = fetch.call_args.args[0]
        self.assertTrue(req.full_url.endswith("/sendDocument"))
        self.assertIn(b'name="document"; filename="report.pdf"', req.data)
        self.assertIn(b'name="chat_id"', req.data)
        self.assertIn(b"%PDF-fake", req.data)

    def test_text_arrives_before_the_document(self):
        self.make_file()
        job = {
            "id": 7,
            "chat_id": 420,
            "message_id": 70,
            "text": "send me the report",
            "voice": None,
            "enqueued_at": bridge.time.time(),
        }
        calls = []

        def fake_api(token, method, payload, timeout=None):
            calls.append(("text", payload.get("text")))
            return {"ok": True}

        with mock.patch.object(bridge, "feedback_pulse"), mock.patch.object(
            bridge,
            "run_grok",
            return_value="Here it is.\nFILE+ 20-studio/report.pdf",
        ), mock.patch.object(bridge, "api", side_effect=fake_api), mock.patch.object(
            bridge, "send_document", side_effect=lambda *a: calls.append(("doc", a[2]))
        ) as send_document:
            bridge.process_work_item("token", job)
        self.assertEqual(calls[0], ("text", "Here it is."))
        self.assertEqual(calls[1][0], "doc")
        self.assertEqual(calls[1][1].name, "report.pdf")
        send_document.assert_called_once()
        self.assertEqual(bridge.read_json(bridge.OUTBOX_FILE, []), [])

    def test_document_failure_retries_then_falls_back_with_mac_path(self):
        self.make_file()
        bridge.enqueue_document(7, 420, bridge.validate_file_send("20-studio/report.pdf"))
        with mock.patch.object(
            bridge, "send_document", side_effect=RuntimeError("telegram down")
        ) as send_document, mock.patch.object(
            bridge, "api", return_value={"ok": True}
        ) as api_mock:
            self.assertFalse(bridge.deliver_outbox("token"))
            self.assertFalse(bridge.deliver_outbox("token"))
            self.assertTrue(bridge.deliver_outbox("token"))
        self.assertEqual(send_document.call_count, bridge.DOC_MAX_ATTEMPTS)
        fallback = api_mock.call_args.args[2]["text"]
        self.assertTrue(fallback.startswith("That file didn't send."))
        self.assertIn("report.pdf", fallback)
        self.assertEqual(bridge.read_json(bridge.OUTBOX_FILE, []), [])

    def test_invalid_file_gets_a_plain_refusal_and_no_document(self):
        job = {
            "id": 7,
            "chat_id": 420,
            "message_id": 70,
            "text": "send me the secrets",
            "voice": None,
            "enqueued_at": bridge.time.time(),
        }
        with mock.patch.object(bridge, "feedback_pulse"), mock.patch.object(
            bridge, "run_grok", return_value="Found it.\nFILE+ ../../.grok/secrets/desk-bridge.env"
        ), mock.patch.object(bridge, "api", return_value={"ok": True}) as api_mock, mock.patch.object(
            bridge, "send_document"
        ) as send_document:
            bridge.process_work_item("token", job)
        send_document.assert_not_called()
        sent = [call.args[2]["text"] for call in api_mock.call_args_list]
        self.assertEqual(len(sent), 1)
        self.assertIn("Can't send that file from the phone seat.", sent[0])
        self.assertNotIn("FILE+", sent[0])

    def test_restart_resumes_pending_document_without_resending_text(self):
        made = self.make_file()
        bridge.enqueue_document(7, 420, made)
        with mock.patch.object(bridge, "api") as api_mock, mock.patch.object(
            bridge, "send_document"
        ) as send_document:
            self.assertTrue(bridge.deliver_outbox("token"))
        api_mock.assert_not_called()
        send_document.assert_called_once()
        self.assertEqual(send_document.call_args.args[2], made.resolve())
        self.assertEqual(bridge.read_json(bridge.OUTBOX_FILE, []), [])

    def test_instant_command_never_leaks_a_file_trailer(self):
        enqueue = mock.Mock()
        with mock.patch.object(
            bridge, "load_secrets", return_value={"TELEGRAM_USER_ID": "42"}
        ), mock.patch.object(
            bridge, "run_grok", return_value="Quick think.\nFILE+ 20-studio/report.pdf"
        ), mock.patch.object(bridge, "send") as send:
            bridge.handle_update("token", update(text="/brainstorm send me x"), enqueue)
        send.assert_called_once()
        self.assertEqual(send.call_args.args[2], "Quick think.")


class MultipartTest(unittest.TestCase):
    def test_contains_model_and_file(self):
        body, boundary = bridge.multipart(
            {"model_id": "scribe_v2"}, "voice.ogg", b"OGGDATA", "audio/ogg"
        )
        self.assertIn(boundary.encode(), body)
        self.assertIn(b"scribe_v2", body)
        self.assertIn(b"OGGDATA", body)
        self.assertIn(b"voice.ogg", body)


class RulesTest(unittest.TestCase):
    def test_phone_rules_are_embedded_without_per_ask_experience_read(self):
        self.assertIn(GOOGLE_REPLY, bridge.DESK_RULES)
        self.assertNotIn(
            "read 30-tools/desk-bridge/experience.md", bridge.DESK_RULES.lower()
        )
        self.assertNotIn(bridge.PHONE_GOOGLE_MISSING, bridge.DESK_RULES)
        self.assertEqual(bridge.PHONE_GOOGLE_MISSING.count("\n"), 0)
        self.assertNotIn("/mcps", bridge.PHONE_GOOGLE_MISSING)

    def test_phone_rules_filter_intake_and_client_facing(self):
        rules = bridge.DESK_RULES.lower()
        self.assertIn("filter like a chief of staff", rules)
        self.assertIn("list+ do |", rules)
        self.assertIn("20-studio/todo.md", rules)
        self.assertIn("do not write todos to lists.md", rules)
        self.assertIn("10-clients/<slug>/", rules)
        self.assertIn("file+ <path>", rules)
        self.assertNotIn(bridge.PHONE_GOOGLE_MISSING.lower(), rules)
        self.assertIn("a voice note cannot close the list", rules)
        self.assertIn("instagram and tiktok links", rules)
        self.assertIn("client-facing", rules)
        self.assertIn("still they recognise", rules)

    def test_phone_rules_default_off_parks_current_data_asks(self):
        rules = bridge.DESK_RULES.lower()
        self.assertIn("this seat has no live gmail, calendar, or drive", rules)
        self.assertIn(
            "reply with exactly this sentence and nothing else: " + GOOGLE_REPLY.lower(),
            rules,
        )
        self.assertNotIn("search_tool", rules)
        self.assertNotIn("use_tool", rules)
        self.assertEqual(bridge.DESK_RULES, bridge.desk_rules())

    def test_phone_rules_live_google_variant_keeps_workspace_semantics(self):
        with mock.patch.dict(os.environ, {"DESK_GOOGLE": "live"}):
            rules = bridge.desk_rules()
        low = rules.lower()
        self.assertIn("search_tool", low)
        self.assertIn("use_tool", low)
        self.assertIn("never reply with: google isn't on this phone seat", low)
        self.assertIn("do not send them to /mcps", low)
        self.assertIn("preserve human relationship language", low)
        self.assertIn('"directly to" means the entity appears in to', low)
        self.assertIn("latest means the individual message timestamp", low)
        self.assertIn("keep multi-entity asks multi-entity", low)
        self.assertIn("relative time in europe/dublin", low)
        self.assertIn('"follow up" means draft only', low)
        self.assertIn("never mutate workspace as a side effect of a lookup", low)
        self.assertIn("evidence that contradicts a connector result", low)
        self.assertIn('do not repeat an older card or connector result as "latest"', low)
        self.assertNotIn(
            "reply with exactly this sentence and nothing else: " + GOOGLE_REPLY.lower(),
            low,
        )

    def test_reset_prefix(self):
        self.assertEqual(bridge.with_reset(False, "hi"), "hi")
        self.assertTrue(
            bridge.with_reset(True, "hi").startswith(
                "Session reset. The last one was too big or gone."
            )
        )


class CommandReplyTest(RuntimeCase):
    def test_status_reports_effective_effort_queue_and_pending_delivery(self):
        bridge.write_text(bridge.SESSION_FILE, "sid")
        bridge.write_text(bridge.LAST_RUN_FILE, '{"seconds":1.2}')
        bridge.enqueue_outbox("pending", 420, "held")
        with mock.patch.object(
            bridge,
            "load_secrets",
            return_value={"TELEGRAM_USER_ID": "42"},
        ), mock.patch.object(
            bridge,
            "session_metadata",
            return_value={"effort": "medium", "model": "grok-4.6-build"},
        ), mock.patch.object(bridge, "current_queue_depth", return_value=2), mock.patch.object(
            bridge, "run_grok"
        ) as run_grok:
            reply = bridge.handle_prompt("token", 420, 7, "/status")
        run_grok.assert_not_called()
        self.assertIn("owner: 42", reply)
        self.assertIn("effort: medium", reply)
        self.assertIn("engine: grok", reply)
        self.assertIn("queue: 2", reply)
        self.assertIn("pending: 1", reply)
        self.assertIn("last run: 1s", reply)
        self.assertIn("last error:", reply)
        self.assertIn("next:", reply)
        self.assertNotIn("{", reply)

    def test_status_typo_is_status(self):
        with mock.patch.object(
            bridge, "load_secrets", return_value={"TELEGRAM_USER_ID": "42"}
        ), mock.patch.object(bridge, "run_grok") as run_grok:
            reply = bridge.handle_prompt("token", 420, 7, "/statua")
        run_grok.assert_not_called()
        self.assertIn("owner: 42", reply)
        self.assertIn("last run: none", reply)
        self.assertIn("next:", reply)

    def test_bare_status_word_is_status(self):
        with mock.patch.object(
            bridge, "load_secrets", return_value={"TELEGRAM_USER_ID": "42"}
        ), mock.patch.object(bridge, "run_grok") as run_grok:
            reply = bridge.handle_prompt("token", 420, 7, "status")
        run_grok.assert_not_called()
        self.assertIn("owner: 42", reply)

    def test_park_appends_ideas_without_grok(self):
        self.lists.write_text("# Lists\n\n## Founder\n\n### Do\n")
        with mock.patch.object(bridge, "run_grok") as run_grok:
            reply = bridge.handle_prompt(
                "token", 420, 7, "Voice note: park buy more ND filters"
            )
        run_grok.assert_not_called()
        self.assertEqual(reply, "On the list.")
        self.assertIn("buy more ND filters", self.lists.read_text())
        self.assertIn("### Ideas", self.lists.read_text())

    def test_park_without_payload_asks(self):
        with mock.patch.object(bridge, "run_grok") as run_grok:
            reply = bridge.handle_prompt("token", 420, 7, "/park")
        run_grok.assert_not_called()
        self.assertEqual(reply, "Say what to park.")

    def test_slash_capture_keeps_its_payload(self):
        self.lists.write_text("# Lists\n\n## Founder\n\n### Do\n")
        with mock.patch.object(bridge, "run_grok") as run_grok:
            reply = bridge.handle_prompt("token", 420, 7, "/park buy ND filters")
        run_grok.assert_not_called()
        self.assertEqual(reply, "On the list.")
        self.assertIn("buy ND filters", self.lists.read_text())

    def test_slash_idea_with_payload_captures(self):
        self.lists.write_text("# Lists\n\n## Founder\n\n### Do\n")
        with mock.patch.object(bridge, "run_grok") as run_grok:
            reply = bridge.handle_prompt(
                "token", 420, 7, "/idea fix the landing page"
            )
        run_grok.assert_not_called()
        self.assertEqual(reply, "Sent to the desk.")
        self.assertIn("fix the landing page", self.lists.read_text())

    def test_slash_brainstorm_with_payload_reaches_grok(self):
        with mock.patch.object(
            bridge, "run_grok", return_value="Roof at dusk, one face."
        ) as run_grok:
            reply = bridge.handle_prompt("token", 420, 7, "/brainstorm dusk idea")
        run_grok.assert_called_once()
        self.assertEqual(reply, "Roof at dusk, one face.")

    def test_non_capture_slash_with_payload_is_still_help(self):
        with mock.patch.object(bridge, "run_grok") as run_grok:
            reply = bridge.handle_prompt("token", 420, 7, "/todo please")
        run_grok.assert_not_called()
        self.assertEqual(reply, bridge.help_text())

    def test_brainstorm_is_a_short_grok_ask(self):
        with mock.patch.object(
            bridge, "run_grok", return_value="Roof at dusk, one face."
        ) as run_grok:
            reply = bridge.handle_prompt(
                "token", 420, 7, "brainstorm dusk shoot from the roof"
            )
        run_grok.assert_called_once()
        self.assertIn("Brainstorm briefly", run_grok.call_args.args[0])
        self.assertEqual(reply, "Roof at dusk, one face.")

    def test_parking_is_not_a_park_capture(self):
        self.assertIsNone(bridge.parse_capture("parking is tight tomorrow")[0])

    def test_long_idea_writes_a_desk_file(self):
        self.lists.write_text("# Lists\n\n## Founder\n\n")
        ideas = self.repo / "20-studio" / "ideas"
        body = "What if month-1 solar is only faces and never a leaflet. " * 8
        with mock.patch.object(bridge, "run_grok") as run_grok:
            reply = bridge.capture_idea(body, self.lists, ideas)
        run_grok.assert_not_called()
        self.assertTrue(reply.startswith("Sent to the desk. 20-studio/ideas/"))
        written = list(ideas.glob("*.md"))
        self.assertEqual(len(written), 1)
        self.assertIn("faces", written[0].read_text())
        self.assertIn("brainstorm 20-studio/ideas/", self.lists.read_text())

    def test_unknown_slash_command_is_help_not_grok(self):
        with mock.patch.object(bridge, "run_grok") as run_grok:
            reply = bridge.handle_prompt("token", 420, 7, "/statux")
        run_grok.assert_not_called()
        self.assertIn("/status", reply)

    def test_new_drops_session_and_metadata(self):
        bridge.write_text(bridge.SESSION_FILE, "sid")
        bridge.write_json(bridge.SESSION_META_FILE, {"session_id": "sid"})
        with mock.patch.object(bridge, "run_grok") as run_grok:
            reply = bridge.handle_prompt("token", 420, 7, "/new")
        self.assertEqual(reply, "New session. Next message starts fresh.")
        self.assertFalse(bridge.SESSION_FILE.exists())
        self.assertFalse(bridge.SESSION_META_FILE.exists())
        run_grok.assert_not_called()

    def test_engine_switches_persist_and_start_a_fresh_session_without_grok(self):
        for engine in ("auto", "claude", "codex", "grok"):
            with self.subTest(engine=engine):
                bridge.write_text(bridge.SESSION_FILE, "sid")
                bridge.write_json(
                    bridge.SESSION_META_FILE,
                    {"session_id": "sid", "engine": "grok"},
                )
                with mock.patch.object(bridge, "run_grok") as run_grok:
                    reply = bridge.handle_prompt(
                        "token", 420, 7, f"/engine {engine}"
                    )
                self.assertEqual(
                    reply,
                    f"Engine set to {engine}. Next message starts fresh.",
                )
                self.assertEqual(
                    bridge.read_text(bridge.ENGINE_OVERRIDE_FILE), engine
                )
                self.assertEqual(bridge.configured_engine(), engine)
                self.assertFalse(bridge.SESSION_FILE.exists())
                self.assertFalse(bridge.SESSION_META_FILE.exists())
                run_grok.assert_not_called()

    def test_bare_or_invalid_engine_command_is_usage_only(self):
        for command in ("/engine", "/engine llama", "/engine claude extra"):
            with self.subTest(command=command):
                bridge.write_text(bridge.ENGINE_OVERRIDE_FILE, "codex")
                bridge.write_text(bridge.SESSION_FILE, "sid")
                bridge.write_json(
                    bridge.SESSION_META_FILE,
                    {"session_id": "sid", "engine": "codex"},
                )
                bridge.write_json(
                    bridge.ENGINE_STATE_FILE,
                    {
                        "active": "codex",
                        "unavailable": {
                            "claude": {"until": 9999999999, "reason": "limit"}
                        },
                    },
                )
                before = {
                    path: path.read_bytes()
                    for path in (
                        bridge.ENGINE_OVERRIDE_FILE,
                        bridge.SESSION_FILE,
                        bridge.SESSION_META_FILE,
                        bridge.ENGINE_STATE_FILE,
                    )
                }
                with mock.patch.object(bridge, "run_grok") as run_grok:
                    reply = bridge.handle_prompt("token", 420, 7, command)
                self.assertEqual(reply, "Use /engine auto|claude|codex|grok")
                self.assertEqual(
                    {path: path.read_bytes() for path in before}, before
                )
                run_grok.assert_not_called()

    def test_new_leaves_engine_override_unchanged(self):
        bridge.write_text(bridge.ENGINE_OVERRIDE_FILE, "claude")
        bridge.write_text(bridge.SESSION_FILE, "sid")
        bridge.write_json(bridge.SESSION_META_FILE, {"session_id": "sid"})
        bridge.handle_prompt("token", 420, 7, "/new")
        self.assertEqual(bridge.read_text(bridge.ENGINE_OVERRIDE_FILE), "claude")

    def test_status_reflects_runtime_engine_override(self):
        bridge.write_text(bridge.ENGINE_OVERRIDE_FILE, "codex")
        with mock.patch.object(
            bridge, "load_secrets", return_value={"TELEGRAM_USER_ID": "42"}
        ), mock.patch.object(bridge, "run_grok") as run_grok:
            reply = bridge.handle_prompt("token", 420, 7, "/status")
        self.assertIn("engine: codex", reply)
        run_grok.assert_not_called()

    def test_engine_override_is_owner_only_state(self):
        bridge.handle_prompt("token", 420, 7, "/engine claude")
        self.assertEqual(file_mode(bridge.ENGINE_OVERRIDE_FILE), 0o600)
        self.assertEqual(file_mode(bridge.ENGINE_OVERRIDE_FILE.parent), 0o700)

    def test_switching_to_auto_clears_fallback_cooldowns(self):
        bridge.write_json(
            bridge.ENGINE_STATE_FILE,
            {
                "active": "codex",
                "unavailable": {
                    "claude": {"until": 9999999999, "reason": "limit"},
                    "grok": {"until": 9999999999, "reason": "capacity"},
                },
            },
        )
        bridge.handle_prompt("token", 420, 7, "/engine auto")
        state = bridge.engine_state(now=1)
        self.assertEqual(state["unavailable"], {})
        self.assertFalse(state["active"])

    def test_status_command_is_not_enqueued(self):
        enqueue = mock.Mock()
        with mock.patch.object(
            bridge, "load_secrets", return_value={"TELEGRAM_USER_ID": "42"}
        ), mock.patch.object(bridge, "send") as send:
            bridge.handle_update(
                "token", update(text="/status"), enqueue
            )
        enqueue.assert_not_called()
        send.assert_called_once()
        self.assertIn("effort:", send.call_args.args[2])

    def test_engine_switch_is_instant_and_cancels_queued_asks(self):
        coordinator = bridge.WorkCoordinator("token")
        coordinator.enqueue(
            {
                "id": 10,
                "chat_id": 420,
                "message_id": 110,
                "text": "queued ask",
                "voice": None,
                "enqueued_at": 1.0,
            }
        )
        enqueue = mock.Mock()
        self.assertTrue(bridge.is_instant_command("/engine claude"))
        with mock.patch.object(
            bridge, "load_secrets", return_value={"TELEGRAM_USER_ID": "42"}
        ), mock.patch.object(
            bridge, "WORK_COORDINATOR", coordinator, create=True
        ), mock.patch.object(bridge, "send") as send, mock.patch.object(
            bridge, "run_grok"
        ) as run_grok:
            next_offset = bridge.handle_update(
                "token", update(text="/engine claude"), enqueue
            )
        self.assertEqual(next_offset, 11)
        enqueue.assert_not_called()
        self.assertEqual(coordinator.depth(), 0)
        self.assertEqual(bridge.inbox_items(), [])
        send.assert_called_once_with(
            "token",
            420,
            "Engine set to claude. Next message starts fresh.",
            timeout=5,
        )
        run_grok.assert_not_called()

    def test_new_cancels_queued_asks(self):
        coordinator = bridge.WorkCoordinator("token")
        job = {
            "id": 10,
            "chat_id": 420,
            "message_id": 110,
            "text": "do the thing",
            "voice": None,
            "enqueued_at": 1.0,
        }
        coordinator.enqueue(job)
        self.assertEqual(coordinator.depth(), 1)
        drained = coordinator.cancel_pending()
        self.assertEqual(drained, 1)
        self.assertEqual(coordinator.depth(), 0)
        self.assertEqual(len(bridge.inbox_items()), 0)


class CommandFailureTest(RuntimeCase):
    def test_check_rejects_missing_owner_without_traceback(self):
        with mock.patch.object(
            bridge, "load_secrets",
            return_value={"TELEGRAM_BOT_TOKEN": "token", "TELEGRAM_USER_ID": ""},
        ), mock.patch.object(bridge, "api", return_value={"ok": True}), mock.patch.object(
            bridge, "grok_bin", return_value="/fake/grok"
        ), mock.patch.object(bridge.shutil, "which", return_value="/fake/grok"), mock.patch.object(
            bridge.subprocess, "run",
            return_value=mock.Mock(returncode=0, stdout="grok 1", stderr=""),
        ), mock.patch("builtins.print") as output:
            self.assertEqual(bridge.cmd_check(), 1)
        self.assertIn(SETUP_REPLY, "\n".join(str(call) for call in output.call_args_list))

    def test_check_normalizes_telegram_failure_to_nonzero(self):
        with mock.patch.object(
            bridge, "load_secrets",
            return_value={"TELEGRAM_BOT_TOKEN": "token", "TELEGRAM_USER_ID": "42"},
        ), mock.patch.object(
            bridge, "api", side_effect=RuntimeError("telegram unavailable")
        ), mock.patch("builtins.print"):
            self.assertEqual(bridge.cmd_check(), 1)

    def test_successful_check_hardens_secret_files(self):
        self.write_owner_secrets()
        self.eleven.write_text("export ELEVENLABS_API_KEY=key\n")
        self.secrets.parent.chmod(0o755)
        self.secrets.chmod(0o644)
        self.eleven.chmod(0o644)
        with mock.patch.object(
            bridge, "api",
            return_value={"ok": True, "result": {"username": "Rua_desk_bot"}},
        ), mock.patch.object(bridge, "grok_bin", return_value="/fake/grok"), mock.patch.object(
            bridge.shutil, "which", return_value="/fake/grok"
        ), mock.patch.object(
            bridge.subprocess, "run",
            return_value=mock.Mock(returncode=0, stdout="grok 1", stderr=""),
        ):
            self.assertEqual(bridge.cmd_check(), 0)
        self.assertEqual(file_mode(self.secrets.parent), 0o700)
        self.assertEqual(file_mode(self.secrets), 0o600)
        self.assertEqual(file_mode(self.eleven), 0o600)

    def test_install_precreates_owner_only_logs(self):
        loaded = mock.Mock(returncode=0, stdout="", stderr="")
        with mock.patch.object(bridge, "cmd_check", return_value=0), mock.patch.object(
            bridge.subprocess, "run", return_value=loaded
        ):
            self.assertEqual(bridge.cmd_install(), 0)
        self.assertEqual(file_mode(self.state), 0o700)
        self.assertEqual(file_mode(self.state / "bridge.log"), 0o600)
        self.assertEqual(file_mode(self.state / "bridge.err"), 0o600)

    def test_failed_reinstall_restores_and_reloads_previous_plist(self):
        self.plist.parent.mkdir(parents=True)
        self.plist.write_text("old plist", encoding="utf-8")
        ok = mock.Mock(returncode=0, stdout="", stderr="")
        failed = mock.Mock(returncode=1, stdout="", stderr="new load failed")
        with mock.patch.object(bridge, "cmd_check", return_value=0), mock.patch.object(
            bridge.subprocess,
            "run",
            side_effect=[ok, ok, failed, ok],
        ), mock.patch("builtins.print"):
            self.assertEqual(bridge.cmd_install(), 1)
        self.assertEqual(self.plist.read_text(encoding="utf-8"), "old plist")

    def test_uninstall_failure_is_reported_and_keeps_plist(self):
        self.plist.parent.mkdir(parents=True)
        self.plist.write_text("plist")
        with mock.patch.object(
            bridge.subprocess, "run", side_effect=OSError("launchctl missing")
        ), mock.patch("builtins.print"):
            self.assertEqual(bridge.cmd_uninstall(), 1)
        self.assertTrue(self.plist.exists())


if __name__ == "__main__":
    unittest.main()
