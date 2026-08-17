# Safe HTML-to-PDF export

## Goal

Export an HTML deck without risking the source file or the last valid PDF.

## Out of scope

Deck authoring, visual redesign, screenshot QA, new rendering engines, and new
dependencies.

## Done

The CLI rejects identical input and output files, renders through unique
temporary files, preserves relative assets for fallback copies, sanity-checks
the finished PDF (with a strict parse when `pypdf` is available), and only then
atomically replaces the requested output. Failure paths leave existing files
untouched and remove their temporary files.

## Observe

Run the standard-library test suite, then export the documented fixture to
`/tmp/rua-sample-deck.pdf` and confirm it is a two-page A4 PDF with the expected
cover.
