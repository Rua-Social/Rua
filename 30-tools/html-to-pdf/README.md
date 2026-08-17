# html-to-pdf

Print a Rua HTML deck to an A4 PDF using the Chrome already on this machine.

Sales collateral, Week 0, concepts, schedules and handovers are built as
HTML. Export is a local print job. Do not spend Grok Playwright or Chrome
Headless credits on it.

This prints the document. It does not make a room deck. A live
presentation is a separate 16:9 present cut, not this PDF dropped into
PowerPoint. The working offer's present file is
`20-studio/sales/ways-to-work-present.pptx`.

## Goal

`deck.html` in, A4 PDF out, same look as the browser. No Playwright, no
new dependency, no rewrite of the page model.

Out of scope: authoring the deck, QA page screenshots, WeasyPrint, reportlab.

Done: the command below writes a real PDF with the right page count and a
solid navy cover on the fixture.

## Run

```bash
python3 30-tools/html-to-pdf/html_to_pdf.py path/to/deck.html
python3 30-tools/html-to-pdf/html_to_pdf.py path/to/deck.html path/to/deck.pdf
```

Chrome is resolved in this order: `CHROME_BIN`, then the macOS Chrome app,
then `google-chrome` / `chromium` on PATH.

`--wait-ms` (default 8000) is the font-load budget. Raise it if headlines
fall back to Georgia.

## Check

```bash
python3 30-tools/html-to-pdf/html_to_pdf.py \
  30-tools/html-to-pdf/fixtures/sample-deck.html \
  /tmp/rua-sample-deck.pdf
```

Expect two A4 pages, a dark cover, and Instrument Serif on the title.

## Why this and not Playwright

The document recipe already designs for Chromium print. Grok's Playwright
and Chrome Headless tools bill for a browser session. This script calls the
Chrome you already run, then exits. Same engine, no credit burn.
