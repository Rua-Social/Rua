#!/usr/bin/env python3
"""Print an HTML deck to A4 PDF using the Chrome already on this machine."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.parse import quote, urljoin

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


def inject_print_css_with_base(src: Path, dest: Path) -> None:
    """Write a print copy whose relative URLs still resolve from ``src``."""
    html = src.read_text(encoding="utf-8")
    base_pattern = re.compile(
        r"(<base\b[^>]*\bhref\s*=\s*)(?:(['\"])(.*?)\2|([^\s>]+))",
        flags=re.IGNORECASE | re.DOTALL,
    )
    masked = re.sub(
        r"<!--.*?-->|<script\b[^>]*>.*?</script\s*>|<style\b[^>]*>.*?</style\s*>",
        lambda match: " " * len(match.group(0)),
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    existing_base = base_pattern.search(masked)
    if existing_base:
        href = existing_base.group(3) or existing_base.group(4)
        resolved = urljoin(file_url(src), href)
        replacement = existing_base.group(1) + f'"{resolved}"'
        html = html[: existing_base.start()] + replacement + html[existing_base.end() :]
        base = ""
    else:
        # Use the original document URL, not merely its directory. Relative
        # assets still resolve correctly and fragment/query-only references
        # retain the source filename semantics.
        base = f'<base href="{file_url(src)}">\n'
    snippet = f'{base}<style id="rua-print">{PRINT_CSS}</style>'
    head = re.search(r"<head(?:\s[^>]*)?>", html, flags=re.IGNORECASE)
    if head:
        html = html[: head.end()] + "\n" + snippet + html[head.end() :]
    elif re.search(r"</head\s*>", html, flags=re.IGNORECASE):
        html = re.sub(
            r"</head\s*>",
            snippet + "\n</head>",
            html,
            count=1,
            flags=re.IGNORECASE,
        )
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
        returncode = proc.poll()
        if returncode is not None:
            if returncode == 0 and path.is_file() and path.stat().st_size > 100:
                return
            err = ""
            if proc.stderr is not None:
                err = proc.stderr.read().decode("utf-8", errors="replace")
            extra = f"\n{err.strip()}" if err.strip() else ""
            sys.exit(
                f"html-to-pdf: Chrome exited {returncode} without a successful export of {path}.{extra}"
            )
        if path.is_file():
            size = path.stat().st_size
            if size > 100 and size == last_size:
                stable += 1
                if stable >= 3:
                    return
            else:
                stable = 0
            last_size = size
        time.sleep(0.15)
    sys.exit(f"html-to-pdf: timed out waiting for {path}")


def kill_chrome(proc: subprocess.Popen[bytes]) -> None:
    try:
        initial = proc.poll()
        if initial is not None:
            if initial != 0:
                raise RuntimeError(f"Chrome exited {initial}; refusing to publish its PDF")
        else:
            try:
                os.killpg(proc.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                try:
                    proc.wait(timeout=3)
                except subprocess.TimeoutExpired as exc:
                    raise RuntimeError("Chrome did not stop after SIGKILL") from exc
        final = proc.poll()
        if final is not None and final not in (0, -signal.SIGTERM, -signal.SIGKILL):
            raise RuntimeError(f"Chrome exited {final}; refusing to publish its PDF")
        if final is None:
            raise RuntimeError("Chrome is still running; refusing to publish its PDF")
    except OSError as exc:
        raise RuntimeError(f"could not stop Chrome: {exc}") from exc
    finally:
        if proc.stderr is not None:
            try:
                proc.stderr.close()
            except OSError:
                pass


def print_copy_path(src: Path, fallback_dir: Path) -> Path:
    """Create a collision-safe print copy, falling back outside ``src.parent``."""
    try:
        fd, name = tempfile.mkstemp(
            prefix=f".{src.stem}.",
            suffix=".__print__.html",
            dir=src.parent,
        )
        os.close(fd)
    except OSError:
        fallback = fallback_dir / "source.__print__.html"
        inject_print_css_with_base(src, fallback)
        return fallback

    dest = Path(name)
    try:
        inject_print_css(src, dest)
        return dest
    except OSError:
        try:
            dest.unlink(missing_ok=True)
        except OSError:
            pass
        fallback = fallback_dir / "source.__print__.html"
        inject_print_css_with_base(src, fallback)
        return fallback
    except Exception:
        # The tempfile belongs to this invocation even when decoding or HTML
        # preparation fails before the outer cleanup learns its path.
        try:
            dest.unlink(missing_ok=True)
        except OSError:
            pass
        raise


def paths_refer_to_same_file(src: Path, out: Path) -> bool:
    if src == out:
        return True
    try:
        return out.exists() and os.path.samefile(src, out)
    except OSError:
        return False


def validate_pdf(pdf: Path) -> bytes:
    """Sanity-check structure, plus a strict parse when pypdf is installed."""
    try:
        data = pdf.read_bytes()
    except OSError as exc:
        raise ValueError(f"could not read generated PDF: {exc}") from exc

    if len(data) <= 100:
        raise ValueError("generated PDF is unexpectedly small")
    if re.match(rb"%PDF-[12]\.\d", data) is None:
        raise ValueError("generated file has no valid PDF header")
    if re.search(rb"/Type\s*/Page(?:\s|[/>])", data) is None:
        raise ValueError("generated PDF contains no page object")

    tail = data[-2048:].rstrip()
    if not tail.endswith(b"%%EOF"):
        raise ValueError("generated PDF has no final EOF marker")
    startxref = list(re.finditer(rb"startxref\s+(\d+)\s+%%EOF", tail))
    if not startxref:
        raise ValueError("generated PDF has no final cross-reference pointer")
    offset = int(startxref[-1].group(1))
    if offset >= len(data):
        raise ValueError("generated PDF has an invalid cross-reference pointer")
    target = data[offset : offset + 64].lstrip()
    if target.startswith(b"xref"):
        final_section = data[offset:]
        trailer = re.search(rb"\btrailer\s*<<(.{1,4096}?)>>", final_section, re.DOTALL)
        if trailer is None or re.search(rb"/Root\s+\d+\s+\d+\s+R\b", trailer.group(1)) is None:
            raise ValueError("generated PDF has no rooted cross-reference trailer")
    else:
        xref_stream = re.match(
            rb"\d+\s+\d+\s+obj\s*<<(.{1,4096}?)>>\s*stream\b",
            data[offset : offset + 8192],
            re.DOTALL,
        )
        if xref_stream is None:
            raise ValueError("generated PDF cross-reference pointer has no valid target")
        dictionary = xref_stream.group(1)
        for marker in (rb"/Type\s*/XRef\b", rb"/Root\s+\d+\s+\d+\s+R\b", rb"/W\s*\["):
            if re.search(marker, dictionary) is None:
                raise ValueError("generated PDF has an invalid cross-reference stream")

    parsed_pages = page_count(pdf, require_valid=True)
    if parsed_pages is not None and parsed_pages < 1:
        raise ValueError("generated PDF contains no readable pages")
    return data


def page_count(pdf: Path, require_valid: bool = False) -> int | None:
    try:
        from pypdf import PdfReader
    except ImportError:
        return None
    try:
        with pdf.open("rb") as stream:
            return len(PdfReader(stream, strict=True).pages)
    except Exception as exc:
        if require_valid:
            raise ValueError(f"generated PDF failed strict parsing: {exc}") from exc
        return None


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Print an HTML deck to A4 PDF with local Chrome. No Playwright."
    )
    parser.add_argument("html", type=Path, nargs="?", help="source HTML deck")
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
    parser.add_argument(
        "--print-chrome",
        action="store_true",
        help="print resolved Chrome path and exit",
    )
    args = parser.parse_args()

    if args.print_chrome:
        print(find_chrome())
        sys.exit(0)
    if not args.html:
        parser.error("the following arguments are required: html")

    src = args.html.expanduser().resolve()
    if not src.is_file():
        sys.exit(f"html-to-pdf: no such file: {src}")

    out = args.pdf.expanduser().resolve() if args.pdf else src.with_suffix(".pdf")
    if paths_refer_to_same_file(src, out):
        sys.exit("html-to-pdf: source HTML and output PDF must be different files")

    out.parent.mkdir(parents=True, exist_ok=True)

    chrome = find_chrome()
    work_dir = Path(tempfile.mkdtemp(prefix=".rua-html-to-pdf-", dir=out.parent))
    print_html: Path | None = None
    temp_pdf = work_dir / "render.pdf"
    profile = work_dir / "profile"
    proc: subprocess.Popen[bytes] | None = None
    try:
        print_html = print_copy_path(src, work_dir)
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
            f"--print-to-pdf={temp_pdf}",
            file_url(print_html),
        ]
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            start_new_session=True,
        )
        wait_for_pdf(temp_pdf, proc, timeout=(args.wait_ms / 1000.0) + 20)
        kill_chrome(proc)
        proc = None

        try:
            validate_pdf(temp_pdf)
        except ValueError as exc:
            sys.exit(f"html-to-pdf: {exc}")
        pdf_fd = os.open(temp_pdf, os.O_RDONLY)
        try:
            os.fsync(pdf_fd)
        finally:
            os.close(pdf_fd)
        os.replace(temp_pdf, out)
        try:
            parent_fd = os.open(out.parent, os.O_RDONLY)
            try:
                os.fsync(parent_fd)
            finally:
                os.close(parent_fd)
        except OSError:
            # The atomic publish has already succeeded; a filesystem that
            # rejects directory fsync must not turn that success into a false
            # failure after the previous destination is gone.
            pass
    finally:
        if proc is not None:
            try:
                kill_chrome(proc)
            except Exception:
                # The success path already refuses to publish until Chrome is
                # confirmed stopped. Cleanup must still run while an earlier
                # failure is propagating.
                pass
            finally:
                if proc.stderr is not None:
                    try:
                        proc.stderr.close()
                    except OSError:
                        pass
        try:
            if print_html is not None:
                try:
                    print_html.unlink(missing_ok=True)
                except OSError:
                    pass
        finally:
            shutil.rmtree(work_dir, ignore_errors=True)

    pages = page_count(out)
    if pages is not None:
        print(f"wrote {out} ({out.stat().st_size} bytes, {pages} pages)")
    else:
        print(f"wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
