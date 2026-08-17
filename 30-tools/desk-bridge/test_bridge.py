#!/usr/bin/env python3
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import bridge


class ChunkTest(unittest.TestCase):
    def test_short(self):
        self.assertEqual(bridge.chunk_text("hi"), ["hi"])

    def test_empty(self):
        self.assertEqual(bridge.chunk_text("  "), ["(empty reply)"])

    def test_splits_long(self):
        body = ("word " * 2000).strip()
        parts = bridge.chunk_text(body, limit=80)
        self.assertGreater(len(parts), 1)
        self.assertEqual(" ".join(parts), body)
        self.assertTrue(all(len(p) <= 80 for p in parts))


class EnvTest(unittest.TestCase):
    def test_load_and_pair(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "desk-bridge.env"
            path.write_text("export TELEGRAM_BOT_TOKEN=abc\nexport TELEGRAM_USER_ID=\n")
            env = bridge.load_env(path)
            self.assertEqual(env["TELEGRAM_BOT_TOKEN"], "abc")
            self.assertEqual(env["TELEGRAM_USER_ID"], "")
            bridge.write_user_id("42", path)
            env = bridge.load_env(path)
            self.assertEqual(env["TELEGRAM_USER_ID"], "42")
            self.assertEqual(env["TELEGRAM_BOT_TOKEN"], "abc")


class PhoneTextTest(unittest.TestCase):
    def test_drops_process_talk(self):
        stream = "\n".join(
            [
                '{"type":"text","data":"Sales. Loading founder context...\\n"}',
                '{"type":"tool_call","toolCallId":"1","toolName":"read_file"}',
                '{"type":"text","data":"One-pager is in the chat."}',
                '{"type":"end","sessionId":"abc"}',
            ]
        )
        text, sid = bridge.phone_text_from_stream(stream)
        self.assertEqual(text, "One-pager is in the chat.")
        self.assertEqual(sid, "abc")

    def test_joins_final_chunks(self):
        stream = "\n".join(
            [
                '{"type":"tool_call","toolCallId":"1"}',
                '{"type":"text","data":"Sent. "}',
                '{"type":"text","data":"PDF is in the chat."}',
                '{"type":"end","sessionId":"z"}',
            ]
        )
        text, sid = bridge.phone_text_from_stream(stream)
        self.assertEqual(text, "Sent. PDF is in the chat.")
        self.assertEqual(sid, "z")

    def test_legacy_json(self):
        text, sid = bridge.phone_text_from_stream(
            '{"text":"hi","sessionId":"s1"}'
        )
        self.assertEqual(text, "hi")
        self.assertEqual(sid, "s1")

    def test_error_event(self):
        with self.assertRaises(RuntimeError):
            bridge.phone_text_from_stream('{"type":"error","message":"nope"}')

    def test_no_fallback_after_tool(self):
        stream = "\n".join(
            [
                '{"type":"text","data":"I will inspect it"}',
                '{"type":"tool_call","toolCallId":"1"}',
                '{"type":"end","sessionId":"s"}',
            ]
        )
        text, sid = bridge.phone_text_from_stream(stream)
        self.assertEqual(text, "")
        self.assertEqual(sid, "s")

    def test_incomplete_stream(self):
        stream = '{"type":"text","data":"partial"}'
        with self.assertRaises(RuntimeError):
            bridge.phone_text_from_stream(stream)


class SessionHeavyTest(unittest.TestCase):
    def test_heavy_when_history_big(self):
        with tempfile.TemporaryDirectory() as tmp:
            hist = Path(tmp) / "cwd" / "sid-1" / "chat_history.jsonl"
            hist.parent.mkdir(parents=True)
            hist.write_bytes(b"x" * 500)
            with mock.patch.object(bridge, "session_history_path", return_value=hist):
                self.assertTrue(bridge.session_is_heavy("sid-1", limit=100))
                self.assertFalse(bridge.session_is_heavy("sid-1", limit=10_000))

    def test_missing_is_not_heavy(self):
        with mock.patch.object(bridge, "session_history_path", return_value=None):
            self.assertFalse(bridge.session_is_heavy("missing"))

    def test_drop_stale_missing_history(self):
        with mock.patch.object(bridge, "session_history_path", return_value=None):
            self.assertTrue(bridge.should_drop_session("stale-id"))
            self.assertFalse(bridge.should_drop_session(""))


class PairAndChatTest(unittest.TestCase):
    def test_private_dm_only(self):
        self.assertTrue(bridge.is_private_dm({"type": "private"}))
        self.assertFalse(bridge.is_private_dm({"type": "group"}))
        self.assertFalse(bridge.is_private_dm({"type": "supergroup"}))
        self.assertFalse(bridge.is_private_dm({}))

    def test_pair_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "desk-bridge.env"
            path.write_text("export TELEGRAM_BOT_TOKEN=abc\nexport TELEGRAM_USER_ID=\n")
            with mock.patch.object(bridge, "SECRETS", path):
                env = bridge.load_env(path)
                self.assertEqual(bridge.pair_status(env, 7), "claimed")
                env = bridge.load_env(path)
                self.assertEqual(bridge.pair_status(env, 7), "ok")
                self.assertEqual(bridge.pair_status(env, 8), "foreign")
                self.assertFalse(bridge.allowed(env, 8))
                self.assertTrue(bridge.allowed(env, 7))


class DeskRulesTest(unittest.TestCase):
    def test_google_miss_is_plain(self):
        rules = bridge.DESK_RULES
        self.assertIn("Mail.app", rules)
        self.assertIn(
            "Google isn't on this phone seat. Parked on the desk list.",
            rules,
        )
        self.assertIn("20-studio/lists.md", rules)


class ResetLineTest(unittest.TestCase):
    def test_prefix(self):
        self.assertEqual(bridge.with_reset(False, "hi"), "hi")
        self.assertTrue(
            bridge.with_reset(True, "hi").startswith(
                "Session reset. The last one was too big or gone."
            )
        )


class MultipartTest(unittest.TestCase):
    def test_contains_model_and_file(self):
        body, bound = bridge.multipart(
            {"model_id": "scribe_v2"},
            "voice.ogg",
            b"OGGDATA",
            "audio/ogg",
        )
        self.assertIn(bound.encode(), body)
        self.assertIn(b"scribe_v2", body)
        self.assertIn(b"OGGDATA", body)
        self.assertIn(b"voice.ogg", body)


if __name__ == "__main__":
    unittest.main()
