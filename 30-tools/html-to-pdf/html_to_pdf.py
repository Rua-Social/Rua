#!/usr/bin/env python3
"""Print an HTML deck to A4 PDF using the Chrome already on this machine."""

from __future__ import annotations

import argparse
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.parse import quote

PRINT_CSS = """
@page { size: A4; margin: 0; }
html, body { margin: 0; }
* { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
"""


def find_chrome() -> str:
    candidates = [
        os.environ.get("CHROME_BIN"),
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary",
        shutil.which("google-chrome"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
        shutil.which("chrome"),
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file() and os.access(candidate, os.X_OK):
            return candidate
    sys.exit("html-to-pdf: Chrome or Chromium not found. Install Chrome or set CHROME_BIN.")


def inject_print_css(src: Path, dest: Path) -> None:
    html = src.read_text(encoding="utf-8")
    snippet = f'<style id="rua-print">{PRINT_CSS}</style>'
    if "</head>" in html:
        html = html.replace("</head>", snippet + "\n</head>", 1)
    else:
        html = snippet + html
    dest.write_text(html, encoding="utf-8")


def file_url(path: Path) -> str:
    return "file://" + quote(str(path.resolve()), safe="/:")


def wait_for_pdf(path: Path, proc: subprocess.Popen[bytes], timeout: float) -> None:
    deadline = time.time() + timeout
    last_size = -1
    stable = 0
    while time.time() < deadline:
        if path.is_file():
            size = path.stat().st_size
            if size > 100 and size == last_size:
                stable += 1
                if stable >= 3:
                    return
            else:
                stable = 0
            last_size = size
        if proc.poll() is not None:
            if path.is_file() and path.stat().st_size > 100:
                return
            err = ""
            if proc.stderr is not None:
                err = proc.stderr.read().decode("utf-8", errors="replace")
            extra = f"\n{err.strip()}" if err.strip() else ""
            sys.exit(
                f"html-to-pdf: Chrome exited {proc.returncode} without writing {path}.{extra}"
            )
        time.sleep(0.15)
    if path.is_file() and path.stat().st_size > 100:
        return
    sys.exit(f"html-to-pdf: timed out waiting for {path}")


def kill_chrome(proc: subprocess.Popen[bytes]) -> None:
    if proc.poll() is not None:
        return
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        proc.wait(timeout=3)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            return
        proc.wait(timeout=3)


def print_copy_path(src: Path) -> Path:
    dest = src.with_name(f"{src.stem}.__print__.html")
    try:
        inject_print_css(src, dest)
        return dest
    except OSError:
        fallback = Path(tempfile.mkdtemp(prefix="rua-html-to-pdf-src-")) / src.name
        inject_print_css(src, fallback)
        return fallback


def page_count(pdf: Path) -> int | None:
    try:
        from pypdf import PdfReader
    except ImportError:
        return None
    return len(PdfReader(str(pdf)).pages)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Print an HTML deck to A4 PDF with local Chrome. No Playwright."
    )
    parser.add_argument("html", type=Path, help="source HTML deck")
    parser.add_argument(
        "pdf",
        type=Path,
        nargs="?",
        help="output path (default: same name as the HTML, .pdf)",
    )
    parser.add_argument(
        "--wait-ms",
        type=int,
        default=8000,
        help="Chrome virtual-time budget so webfonts can load (default: 8000)",
    )
    args = parser.parse_args()

    src = args.html.expanduser().resolve()
    if not src.is_file():
        sys.exit(f"html-to-pdf: no such file: {src}")

    out = args.pdf.expanduser().resolve() if args.pdf else src.with_suffix(".pdf")
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()

    chrome = find_chrome()
    print_html = print_copy_path(src)
    profile = Path(tempfile.mkdtemp(prefix="rua-html-to-pdf-"))
    proc: subprocess.Popen[bytes] | None = None
    try:
        cmd = [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-extensions",
            "--hide-scrollbars",
            "--no-pdf-header-footer",
            f"--virtual-time-budget={args.wait_ms}",
            f"--timeout={args.wait_ms + 15000}",
            f"--user-data-dir={profile}",
            f"--crash-dumps-dir={profile / 'crashes'}",
            f"--print-to-pdf={out}",
            file_url(print_html),
        ]
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            start_new_session=True,
        )
        wait_for_pdf(out, proc, timeout=(args.wait_ms / 1000.0) + 20)
    finally:
        if proc is not None:
            kill_chrome(proc)
        if print_html.exists() and print_html != src:
            print_html.unlink()
        shutil.rmtree(profile, ignore_errors=True)

    data = out.read_bytes()
    if not data.startswith(b"%PDF"):
        sys.exit(f"html-to-pdf: {out} is not a PDF")

    pages = page_count(out)
    if pages is not None:
        print(f"wrote {out} ({out.stat().st_size} bytes, {pages} pages)")
    else:
        print(f"wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
