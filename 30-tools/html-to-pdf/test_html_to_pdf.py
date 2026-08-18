from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


MODULE_PATH = Path(__file__).with_name("html_to_pdf.py")
SPEC = importlib.util.spec_from_file_location("rua_html_to_pdf", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
html_to_pdf = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(html_to_pdf)


FAKE_CHROME = r'''#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse


def valid_pdf():
    objects = [
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R >>\nendobj\n",
    ]
    body = b"%PDF-1.4\n"
    offsets = []
    for item in objects:
        offsets.append(len(body))
        body += item
    xref_offset = len(body)
    return (
        body
        + b"xref\n0 4\n0000000000 65535 f \n"
        + b"".join(f"{offset:010d} 00000 n \n".encode("ascii") for offset in offsets)
        + b"trailer\n<< /Size 4 /Root 1 0 R >>\n"
        + b"startxref\n"
        + str(xref_offset).encode("ascii")
        + b"\n%%EOF\n"
    )


output_arg = next(arg for arg in sys.argv if arg.startswith("--print-to-pdf="))
output = Path(output_arg.split("=", 1)[1])
source_url = sys.argv[-1]
source = Path(unquote(urlparse(source_url).path))

watch = os.environ.get("FAKE_CHROME_WATCH_OUTPUT")
expected = os.environ.get("FAKE_CHROME_EXPECTED_HEX")
if watch and expected and Path(watch).read_bytes().hex() != expected:
    print("existing output changed before render completed", file=sys.stderr)
    raise SystemExit(9)

log = os.environ.get("FAKE_CHROME_LOG")
if log:
    record = {
        "input": str(source),
        "output": str(output),
        "html": source.read_text(encoding="utf-8"),
    }
    with Path(log).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")

mode = os.environ.get("FAKE_CHROME_MODE", "valid")
if mode == "no-output":
    print("synthetic Chrome failure", file=sys.stderr)
    raise SystemExit(7)
if mode == "invalid":
    output.write_bytes(b"not a PDF" * 40)
else:
    output.write_bytes(valid_pdf())
if mode == "valid-fail":
    print("synthetic failure after writing", file=sys.stderr)
    raise SystemExit(8)
'''


def valid_pdf() -> bytes:
    objects = [
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R >>\nendobj\n",
    ]
    body = b"%PDF-1.4\n"
    offsets = []
    for item in objects:
        offsets.append(len(body))
        body += item
    xref_offset = len(body)
    return (
        body
        + b"xref\n0 4\n0000000000 65535 f \n"
        + b"".join(f"{offset:010d} 00000 n \n".encode("ascii") for offset in offsets)
        + b"trailer\n<< /Size 4 /Root 1 0 R >>\n"
        + b"startxref\n"
        + str(xref_offset).encode("ascii")
        + b"\n%%EOF\n"
    )


class HtmlToPdfSafetyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source_dir = self.root / "source"
        self.output_dir = self.root / "output"
        self.source_dir.mkdir()
        self.output_dir.mkdir()
        self.source = self.source_dir / "deck.html"
        self.source.write_text(
            '<html><head></head><body><img src="assets/logo.png"></body></html>',
            encoding="utf-8",
        )
        self.output = self.output_dir / "deck.pdf"
        self.chrome = self.root / "fake-chrome"
        self.chrome.write_text(FAKE_CHROME, encoding="utf-8")
        self.chrome.chmod(0o755)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_main(self, *args: Path | str, env: dict[str, str] | None = None) -> str:
        argv = [str(MODULE_PATH), *(str(arg) for arg in args), "--wait-ms", "0"]
        with (
            mock.patch.object(sys, "argv", argv),
            mock.patch.object(html_to_pdf, "find_chrome", return_value=str(self.chrome)),
            mock.patch.object(html_to_pdf, "page_count", return_value=None),
            mock.patch.dict(os.environ, env or {}, clear=False),
            contextlib.redirect_stdout(io.StringIO()) as stdout,
        ):
            html_to_pdf.main()
        return stdout.getvalue()

    def assert_no_temporary_files(self) -> None:
        self.assertEqual([], list(self.output_dir.glob(".rua-html-to-pdf-*")))
        self.assertEqual([], list(self.source_dir.glob(".*.__print__.html")))

    def test_rejects_identical_paths_before_mutation(self) -> None:
        original = self.source.read_bytes()
        argv = [str(MODULE_PATH), str(self.source), str(self.source)]
        with (
            mock.patch.object(sys, "argv", argv),
            mock.patch.object(
                html_to_pdf,
                "find_chrome",
                side_effect=AssertionError("Chrome lookup must not run"),
            ),
        ):
            with self.assertRaisesRegex(SystemExit, "must be different files"):
                html_to_pdf.main()
        self.assertEqual(original, self.source.read_bytes())
        self.assert_no_temporary_files()

    def test_rejects_a_hard_link_to_the_source(self) -> None:
        linked_output = self.output_dir / "linked.pdf"
        try:
            os.link(self.source, linked_output)
        except OSError as exc:
            self.skipTest(f"hard links unavailable: {exc}")
        original = self.source.read_bytes()
        with self.assertRaisesRegex(SystemExit, "must be different files"):
            self.run_main(self.source, linked_output)
        self.assertEqual(original, self.source.read_bytes())
        self.assertEqual(original, linked_output.read_bytes())

    def test_rejects_a_symlink_to_the_source(self) -> None:
        linked_output = self.output_dir / "linked.pdf"
        try:
            os.symlink(self.source, linked_output)
        except OSError as exc:
            self.skipTest(f"symlinks unavailable: {exc}")
        original = self.source.read_bytes()
        with self.assertRaisesRegex(SystemExit, "must be different files"):
            self.run_main(self.source, linked_output)
        self.assertEqual(original, self.source.read_bytes())
        self.assertTrue(linked_output.is_symlink())

    def test_missing_chrome_does_not_delete_existing_output(self) -> None:
        previous = b"last valid PDF"
        self.output.write_bytes(previous)
        argv = [str(MODULE_PATH), str(self.source), str(self.output)]
        with (
            mock.patch.object(sys, "argv", argv),
            mock.patch.object(
                html_to_pdf,
                "find_chrome",
                side_effect=SystemExit("Chrome missing"),
            ),
        ):
            with self.assertRaisesRegex(SystemExit, "Chrome missing"):
                html_to_pdf.main()
        self.assertEqual(previous, self.output.read_bytes())
        self.assert_no_temporary_files()

    def test_chrome_failure_preserves_existing_output_and_cleans_up(self) -> None:
        previous = b"last valid PDF"
        self.output.write_bytes(previous)
        with self.assertRaisesRegex(SystemExit, "synthetic Chrome failure"):
            self.run_main(
                self.source,
                self.output,
                env={"FAKE_CHROME_MODE": "no-output"},
            )
        self.assertEqual(previous, self.output.read_bytes())
        self.assert_no_temporary_files()

    def test_nonzero_chrome_exit_cannot_publish_a_valid_looking_pdf(self) -> None:
        previous = b"last valid PDF"
        self.output.write_bytes(previous)
        with self.assertRaisesRegex(SystemExit, "Chrome exited 8"):
            self.run_main(
                self.source,
                self.output,
                env={"FAKE_CHROME_MODE": "valid-fail"},
            )
        self.assertEqual(previous, self.output.read_bytes())
        self.assert_no_temporary_files()

    def test_invalid_render_preserves_existing_output_and_cleans_up(self) -> None:
        previous = b"last valid PDF"
        self.output.write_bytes(previous)
        with self.assertRaisesRegex(SystemExit, "valid PDF header"):
            self.run_main(
                self.source,
                self.output,
                env={"FAKE_CHROME_MODE": "invalid"},
            )
        self.assertEqual(previous, self.output.read_bytes())
        self.assert_no_temporary_files()

    def test_invalid_render_does_not_create_a_new_destination(self) -> None:
        with self.assertRaisesRegex(SystemExit, "valid PDF header"):
            self.run_main(
                self.source,
                self.output,
                env={"FAKE_CHROME_MODE": "invalid"},
            )
        self.assertFalse(self.output.exists())
        self.assert_no_temporary_files()

    def test_valid_render_replaces_output_only_after_validation(self) -> None:
        previous = b"last valid PDF"
        self.output.write_bytes(previous)
        stdout = self.run_main(
            self.source,
            self.output,
            env={
                "FAKE_CHROME_MODE": "valid",
                "FAKE_CHROME_WATCH_OUTPUT": str(self.output),
                "FAKE_CHROME_EXPECTED_HEX": previous.hex(),
            },
        )
        self.assertEqual(valid_pdf(), self.output.read_bytes())
        self.assertIn(f"wrote {self.output.resolve()}", stdout)
        self.assert_no_temporary_files()

    def test_failed_atomic_replace_preserves_existing_output_and_cleans_up(self) -> None:
        previous = b"last valid PDF"
        self.output.write_bytes(previous)
        with mock.patch.object(
            html_to_pdf.os,
            "replace",
            side_effect=OSError("synthetic replace failure"),
        ):
            with self.assertRaisesRegex(OSError, "synthetic replace failure"):
                self.run_main(
                    self.source,
                    self.output,
                    env={"FAKE_CHROME_MODE": "valid"},
                )
        self.assertEqual(previous, self.output.read_bytes())
        self.assert_no_temporary_files()

    def test_failed_chrome_stop_preserves_existing_output_and_still_cleans_up(self) -> None:
        previous = b"last valid PDF"
        self.output.write_bytes(previous)
        with mock.patch.object(
            html_to_pdf,
            "kill_chrome",
            side_effect=RuntimeError("synthetic stop failure"),
        ):
            with self.assertRaisesRegex(RuntimeError, "synthetic stop failure"):
                self.run_main(
                    self.source,
                    self.output,
                    env={"FAKE_CHROME_MODE": "valid"},
                )
        self.assertEqual(previous, self.output.read_bytes())
        self.assert_no_temporary_files()

    def test_unique_print_and_pdf_paths_do_not_touch_old_sidecar(self) -> None:
        old_sidecar = self.source_dir / "deck.__print__.html"
        old_sidecar.write_text("keep me", encoding="utf-8")
        log = self.root / "chrome.jsonl"
        env = {"FAKE_CHROME_MODE": "valid", "FAKE_CHROME_LOG": str(log)}

        self.run_main(self.source, self.output, env=env)
        self.run_main(self.source, self.output, env=env)

        records = [json.loads(line) for line in log.read_text().splitlines()]
        self.assertEqual(2, len(records))
        self.assertNotEqual(records[0]["input"], records[1]["input"])
        self.assertNotEqual(records[0]["output"], records[1]["output"])
        self.assertTrue(all(record["output"] != str(self.output) for record in records))
        self.assertTrue(all(not Path(record["input"]).exists() for record in records))
        self.assertTrue(all(not Path(record["output"]).exists() for record in records))
        self.assertEqual("keep me", old_sidecar.read_text(encoding="utf-8"))
        self.assert_no_temporary_files()

    def test_invalid_source_encoding_leaves_no_print_copy(self) -> None:
        self.source.write_bytes(b"\xff\xfe\x00")
        with self.assertRaises(UnicodeDecodeError):
            self.run_main(self.source, self.output)
        self.assertFalse(self.output.exists())
        self.assert_no_temporary_files()

    def test_fallback_copy_preserves_relative_asset_base_and_is_cleaned(self) -> None:
        log = self.root / "chrome.jsonl"
        env = {"FAKE_CHROME_MODE": "valid", "FAKE_CHROME_LOG": str(log)}
        with mock.patch.object(
            html_to_pdf.tempfile,
            "mkstemp",
            side_effect=PermissionError("read-only source directory"),
        ):
            self.run_main(self.source, self.output, env=env)

        record = json.loads(log.read_text().strip())
        expected_base = f'<base href="{html_to_pdf.file_url(self.source)}">'
        self.assertIn(expected_base, record["html"])
        self.assertIn('src="assets/logo.png"', record["html"])
        self.assertFalse(Path(record["input"]).exists())
        self.assert_no_temporary_files()

    def test_fallback_resolves_an_existing_relative_base_from_the_source(self) -> None:
        self.source.write_text(
            '<html><head><base href="../shared/"></head>'
            '<body><img src="logo.png"></body></html>',
            encoding="utf-8",
        )
        log = self.root / "chrome.jsonl"
        with mock.patch.object(
            html_to_pdf.tempfile,
            "mkstemp",
            side_effect=PermissionError("read-only source directory"),
        ):
            self.run_main(
                self.source,
                self.output,
                env={"FAKE_CHROME_MODE": "valid", "FAKE_CHROME_LOG": str(log)},
            )

        record = json.loads(log.read_text().strip())
        expected = f'<base href="{html_to_pdf.file_url(self.root / "shared")}/">'
        self.assertIn(expected, record["html"])
        self.assertEqual(1, record["html"].lower().count("<base "))
        self.assert_no_temporary_files()

    def test_fallback_handles_unquoted_base_and_ignores_comment_decoy(self) -> None:
        self.source.write_text(
            '<html><head><!-- <base href="wrong/"> -->'
            '<base href=../shared/></head><body></body></html>',
            encoding="utf-8",
        )
        log = self.root / "chrome.jsonl"
        with mock.patch.object(
            html_to_pdf.tempfile,
            "mkstemp",
            side_effect=PermissionError("read-only source directory"),
        ):
            self.run_main(
                self.source,
                self.output,
                env={"FAKE_CHROME_MODE": "valid", "FAKE_CHROME_LOG": str(log)},
            )

        record = json.loads(log.read_text().strip())
        expected = f'<base href="{html_to_pdf.file_url(self.root / "shared")}/">'
        self.assertIn(expected, record["html"])
        self.assertIn('<!-- <base href="wrong/"> -->', record["html"])
        self.assert_no_temporary_files()

    def test_print_chrome_flag_prints_path_and_exits_cleanly(self) -> None:
        argv = [str(MODULE_PATH), "--print-chrome"]
        with (
            mock.patch.object(sys, "argv", argv),
            mock.patch.object(html_to_pdf, "find_chrome", return_value=str(self.chrome)),
            contextlib.redirect_stdout(io.StringIO()) as stdout,
        ):
            with self.assertRaises(SystemExit) as ctx:
                html_to_pdf.main()
        self.assertEqual(0, ctx.exception.code)
        self.assertEqual(f"{self.chrome}\n", stdout.getvalue())

    def test_dependency_free_validation_rejects_structural_failures(self) -> None:
        pdf = self.root / "candidate.pdf"
        good = valid_pdf()
        self.assertEqual(good, html_to_pdf.validate_pdf(self._write(pdf, good)))

        cases = {
            "too small": b"%PDF-1.4\n%%EOF\n",
            "bad header": b"NOTPDF!!" + good[8:],
            "no page": good.replace(b"/Type /Page ", b"/Kind /Leaf ", 1),
            "no EOF": good.rsplit(b"%%EOF", 1)[0],
            "bad pointer": good.replace(
                b"startxref\n" + str(good.index(b"xref")).encode("ascii"),
                b"startxref\n999999",
            ),
            "fake xref object": good.replace(
                b"xref\n0 4\n",
                b"4 0 obj\n<< /Type /NotXRef >>\nendobj\n",
                1,
            ),
        }
        for name, data in cases.items():
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    html_to_pdf.validate_pdf(self._write(pdf, data))

    @staticmethod
    def _write(path: Path, data: bytes) -> Path:
        path.write_bytes(data)
        return path


if __name__ == "__main__":
    unittest.main()
