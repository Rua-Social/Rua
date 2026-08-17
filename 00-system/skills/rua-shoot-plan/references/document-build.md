# Document build

HTML-to-PDF recipe for sprint documents: fonts, a default palette, page model,
CSS for each document type, and the export / QA steps.

This is a build recipe. It is not a Rua brand constitution. It descended from
one session style that reproduced cleanly across chats. Recurrence is not a
design decision.

When the client has approved assets (logo, type, colour), those win. Do not
restyle a job into navy and purple because this file exists. Adjust the
recipe, including the look, when the job requires it. Do not treat "adjust
copy, not the system" as a rule.

---

## Recipe at a glance

- **Headlines:** Instrument Serif, italic. Used for cover titles, h1, h2.
- **Body:** DM Sans. Everything else.
- **Default palette (night):** dark navy `#1a1a2e`, purple `#7c3aed`, with a
  light purple, stone, and neutral greys. Amber is reserved for flags.
- **Page model:** A4 portrait. Each page is a fixed-height `.page` div that
  hard-breaks after itself.
- **Format:** built as a single HTML file, exported to PDF.

This palette is the current default for sprint documents when no client
system has been supplied.

---

## Fonts

Load Instrument Serif and DM Sans. The reliable path is a Google Fonts link in the head:

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Instrument+Serif:ital@0;1&display=swap" rel="stylesheet">
```

If the build environment blocks Google Fonts, download the TTF files from their GitHub raw sources and
embed them with `@font-face` (file paths or base64). Either way, give the PDF export a few seconds to
load the fonts before rendering (see the PDF recipe below), or headlines fall back to Georgia and the
deck looks wrong.

---

## Base CSS (shared by all HTML decks)

Every deck starts from this. The concepts deck and the schedule deck both build on it.

```css
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
@page { size: A4; margin: 0; }
* { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
:root {
  --night: #1a1a2e; --purple: #7c3aed; --purple-light: #f3f0ff;
  --stone: #4a4a68; --body: #2d2d3f; --muted: #71717a;
  --border: #e4e4e7; --bg: #fafafa;
  --serif: 'Instrument Serif', Georgia, serif;
  --sans: 'DM Sans', system-ui, sans-serif;
}
body { font-family: var(--sans); background: var(--bg); color: var(--body); font-size: 15px; line-height: 1.6; }
.page { width: 210mm; height: 297mm; margin: 0 auto; background: white; position: relative; display: flex; flex-direction: column; overflow: hidden; page-break-after: always; break-after: page; }
.page:last-child { page-break-after: auto; break-after: auto; }
@media print { body { margin: 0; } .page { margin: 0; box-shadow: none; } }

/* COVER */
.cover { background: var(--night); color: white; padding: 64px 56px; min-height: 297mm; display: flex; flex-direction: column; justify-content: space-between; }
.cover-agency { font-size: 11px; font-weight: 500; letter-spacing: 0.18em; text-transform: uppercase; color: rgba(255,255,255,0.5); }
.cover-main { flex: 1; display: flex; flex-direction: column; justify-content: center; padding: 60px 0 40px; }
.cover-label { font-size: 10px; font-weight: 500; letter-spacing: 0.15em; text-transform: uppercase; color: var(--purple); margin-bottom: 20px; }
.cover-title { font-family: var(--serif); font-style: italic; font-size: 58px; line-height: 1.1; color: white; margin-bottom: 24px; max-width: 520px; }
.cover-bar { width: 80px; height: 4px; background: var(--purple); margin-bottom: 28px; }
.cover-sub { font-size: 15px; color: rgba(255,255,255,0.55); max-width: 420px; line-height: 1.7; }
.cover-meta { display: grid; grid-template-columns: 1fr 1fr; gap: 24px 40px; padding-top: 48px; border-top: 1px solid rgba(255,255,255,0.1); }
.cover-meta-item label { display: block; font-size: 9px; font-weight: 500; letter-spacing: 0.15em; text-transform: uppercase; color: rgba(255,255,255,0.35); margin-bottom: 4px; }
.cover-meta-item span { font-size: 14px; color: rgba(255,255,255,0.8); }

/* INTERIOR PAGES */
.page-header { display: flex; justify-content: space-between; align-items: center; padding: 18px 56px; border-bottom: 1px solid var(--border); }
.page-header-agency { font-size: 10px; font-weight: 500; letter-spacing: 0.15em; text-transform: uppercase; color: var(--muted); }
.page-header-title { font-size: 10px; color: var(--muted); }
.page-content { flex: 1; padding: 36px 56px 36px; }
.page-footer { margin-top: auto; padding: 14px 56px; border-top: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; }
.page-footer span { font-size: 10px; color: var(--muted); }

/* TYPOGRAPHY */
.section-label { font-size: 9px; font-weight: 500; letter-spacing: 0.18em; text-transform: uppercase; color: var(--purple); margin-bottom: 10px; }
h1 { font-family: var(--serif); font-style: italic; font-size: 36px; line-height: 1.15; color: var(--night); margin-bottom: 18px; }
h2 { font-family: var(--serif); font-style: italic; font-size: 26px; line-height: 1.2; color: var(--night); margin-bottom: 10px; }
h3 { font-size: 9px; font-weight: 500; color: var(--stone); margin-bottom: 6px; letter-spacing: 0.12em; text-transform: uppercase; }
p { margin-bottom: 12px; color: var(--body); font-size: 13px; line-height: 1.65; }
p:last-child { margin-bottom: 0; }
```

---

## Week 0 deck

The research and direction document, presented at Stage 2. Uses the base CSS plus the box and table
components below (shared with the concepts deck). Page order:

- Cover (creative title for the sprint, not the literal file name).
- Findings pages: the format split, the baseline, the pillars, the outliers, each on the page where it
  earns its space. Use insight and neutral boxes to carry the key reads.
- A direction page that frames where the concepts are heading.
- Sign-off with Rua Social contact details.

---

## Concepts deck

The single source of truth, built at Stage 4. Page order:

- Cover with a creative title.
- Overview table, ordered by tier.
- One page per concept: tier banner, section label, badges, title, description, insight box, logistics
  grid, shot list where applicable, question list where applicable, caption or format note. Episode
  cards for a mini-series, locked shots for an asset bank.
- Copy bank: every concept, on-screen text and post copy, no gaps.
- Change log, before the sign-off.
- Sign-off with Rua Social contact details.

Concepts deck component CSS (add to the base):

```css
/* TIER BANNER */
.tier-banner { background: var(--night); margin: -36px -56px 28px; padding: 14px 56px; display: flex; align-items: baseline; gap: 16px; }
.tier-banner-label { font-size: 9px; font-weight: 500; letter-spacing: 0.18em; text-transform: uppercase; color: var(--purple); }
.tier-banner-title { font-size: 13px; font-weight: 500; color: white; }
.tier-banner-note { font-size: 11.5px; color: rgba(255,255,255,0.45); margin-left: auto; }

/* BADGES */
.concept-badges { display: flex; align-items: center; gap: 7px; margin-bottom: 11px; flex-wrap: wrap; }
.badge { font-size: 9px; font-weight: 500; letter-spacing: 0.11em; text-transform: uppercase; padding: 3px 8px; border-radius: 3px; display: inline-block; }
.badge-num { color: var(--muted); border: 1px solid var(--border); background: white; }
.badge-green { color: #065f46; background: #d1fae5; border: 1px solid #6ee7b7; }
.badge-amber { color: #92400e; background: #fef3c7; border: 1px solid #fcd34d; }
.badge-series { color: var(--purple); background: var(--purple-light); border: 1px solid #c4b5fd; }
.badge-elevated { color: #5b21b6; background: #ede9fe; border: 1px solid #a78bfa; }
.badge-recurring { color: var(--stone); background: var(--bg); border: 1px solid var(--border); }

/* BOXES */
.insight-box { background: var(--purple-light); border-left: 3px solid var(--purple); padding: 12px 16px; margin: 12px 0; border-radius: 0 4px 4px 0; }
.insight-box .box-label { font-size: 9px; font-weight: 500; letter-spacing: 0.14em; text-transform: uppercase; color: var(--purple); margin-bottom: 4px; display: block; }
.insight-box p { font-size: 12px; color: var(--stone); margin: 0; line-height: 1.6; }
.neutral-box { background: var(--bg); border-left: 3px solid var(--stone); padding: 12px 16px; margin: 12px 0; border-radius: 0 4px 4px 0; }
.neutral-box .box-label { font-size: 9px; font-weight: 500; letter-spacing: 0.14em; text-transform: uppercase; color: var(--stone); margin-bottom: 4px; display: block; }
.neutral-box p { font-size: 12px; color: var(--stone); margin: 0; line-height: 1.6; }
.warning-box { background: #fef3c7; border-left: 3px solid #f59e0b; padding: 12px 16px; margin: 12px 0; border-radius: 0 4px 4px 0; }
.warning-box .box-label { font-size: 9px; font-weight: 500; letter-spacing: 0.14em; text-transform: uppercase; color: #92400e; margin-bottom: 4px; display: block; }
.warning-box p { font-size: 12px; color: #78350f; margin: 0; line-height: 1.6; }

/* LOGISTICS GRID */
.logistics-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0; margin: 11px 0; border: 1px solid var(--border); border-radius: 6px; overflow: hidden; }
.logistics-cell { padding: 11px 13px; border-right: 1px solid var(--border); }
.logistics-cell:last-child { border-right: none; }
.logistics-cell .lc-label { font-size: 9px; font-weight: 500; letter-spacing: 0.12em; text-transform: uppercase; color: var(--muted); margin-bottom: 5px; display: block; }
.logistics-cell p { font-size: 11.5px; color: var(--body); margin: 0; line-height: 1.5; }

/* EPISODE CARDS */
.episode-grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 11px; margin: 12px 0; }
.episode-grid-4 { display: grid; grid-template-columns: 1fr 1fr; gap: 11px; margin: 12px 0; }
.episode-card { border: 1px solid var(--border); border-radius: 6px; padding: 11px 13px; }
.episode-card .ep-num { font-size: 9px; font-weight: 500; letter-spacing: 0.12em; text-transform: uppercase; color: var(--purple); margin-bottom: 3px; display: block; }
.episode-card .ep-title { font-size: 12px; font-weight: 500; color: var(--night); margin-bottom: 5px; display: block; }
.episode-card p { font-size: 11.5px; color: var(--stone); margin: 0 0 4px; line-height: 1.45; }
.episode-card p:last-child { margin: 0; }

/* LISTS */
.q-list { list-style: none; padding: 0; margin: 8px 0; }
.q-list li { font-size: 12.5px; color: var(--body); padding: 5px 0 5px 15px; border-bottom: 1px solid var(--border); position: relative; line-height: 1.5; }
.q-list li:last-child { border-bottom: none; }
.q-list li::before { content: ''; position: absolute; left: 0; top: 12px; width: 5px; height: 5px; background: var(--purple); border-radius: 50%; }
.shot-list { list-style: none; padding: 0; margin: 8px 0; }
.shot-list li { display: flex; gap: 11px; padding: 7px 0; border-bottom: 1px solid var(--border); font-size: 12.5px; color: var(--body); line-height: 1.5; }
.shot-list li:last-child { border-bottom: none; }
.shot-num { font-size: 10px; font-weight: 500; color: var(--purple); min-width: 22px; padding-top: 2px; flex-shrink: 0; }
.shot-detail { flex: 1; }
.shot-detail strong { color: var(--night); }

/* SUB-CONCEPTS */
.sub-concepts { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 12px 0; }
.sub-concept-card { border: 1px solid var(--border); border-radius: 6px; padding: 12px 14px; }
.sub-concept-card .sc-label { font-size: 9px; font-weight: 500; letter-spacing: 0.12em; text-transform: uppercase; color: var(--purple); margin-bottom: 4px; display: block; }
.sub-concept-card .sc-title { font-size: 13px; font-weight: 500; color: var(--night); margin-bottom: 7px; display: block; }
.sub-concept-card p { font-size: 11.5px; color: var(--stone); margin-bottom: 5px; line-height: 1.45; }

/* OVERVIEW TABLE */
.overview-table { width: 100%; border-collapse: collapse; font-size: 11.5px; margin: 8px 0; }
.overview-table th { text-align: left; padding: 6px 10px; font-size: 9px; font-weight: 500; letter-spacing: 0.12em; text-transform: uppercase; color: white; background: var(--night); }
.overview-table td { padding: 5px 10px; border-bottom: 1px solid var(--border); vertical-align: middle; }
.tier-row td { background: var(--bg); padding: 4px 10px; }
.tier-row-label { font-size: 9px; font-weight: 500; letter-spacing: 0.14em; text-transform: uppercase; color: var(--night); }
.ov-num { font-size: 10px; font-weight: 500; color: var(--muted); }
.ov-title { font-weight: 500; color: var(--night); display: block; font-size: 12px; }
.ov-sub { font-size: 10.5px; color: var(--muted); display: block; }
.who-pill { font-size: 9px; font-weight: 500; color: var(--stone); background: white; border: 1px solid var(--border); padding: 2px 7px; border-radius: 3px; white-space: nowrap; }

/* COPY BANK */
.copy-bank-table { width: 100%; border-collapse: collapse; font-size: 12px; margin: 10px 0; }
.copy-bank-table th { background: var(--night); color: white; padding: 8px 12px; text-align: left; font-size: 9px; font-weight: 500; letter-spacing: 0.12em; text-transform: uppercase; }
.copy-bank-table td { padding: 9px 12px; border-bottom: 1px solid var(--border); vertical-align: top; line-height: 1.55; font-size: 11.5px; }
.copy-bank-table tr:nth-child(even) td { background: var(--bg); }
.cb-concept { font-weight: 500; color: var(--night); display: block; margin-bottom: 2px; font-size: 12px; }
.cb-onscreen { color: var(--purple); font-style: italic; font-size: 11px; margin-bottom: 5px; display: block; }
.cb-none { color: var(--muted); font-size: 11px; font-style: italic; }
.caption-tag { display: inline-block; font-size: 9px; font-weight: 500; letter-spacing: 0.1em; text-transform: uppercase; padding: 2px 7px; border-radius: 3px; background: #fef9c3; color: #713f12; border: 1px solid #fde047; margin-left: 6px; vertical-align: middle; }
```

---

## Shoot schedule

The operational day plan, built at Stage 6. Page order:

- Cover (same page recipe as the concepts deck). Mark a draft clearly in the cover if the shoot date
  is not yet confirmed.
- Timetable pages: one block card per block, with a dark header (time and title), a body describing
  what is captured and who is needed, and an amber flag box for anything the client must organise.
- Questions page: every interview question set in one place, so the client can share them with talent.
- Action list page: a numbered table of everything flagged, a quick reference grid of the day, the
  logistics, and the sign-off.
- Change log, before the sign-off.

The schedule adds an amber palette to the root and these components on top of the base:

```css
:root {
  --amber-bg: #fef3c7; --amber-text: #92400e; --amber-border: #fcd34d;
}

/* BLOCK CARDS */
.block-card { border: 1px solid var(--border); border-radius: 6px; margin-bottom: 16px; overflow: hidden; }
.block-header { background: var(--night); padding: 10px 16px; display: flex; align-items: baseline; gap: 14px; }
.block-time { font-size: 12px; font-weight: 500; color: var(--purple); white-space: nowrap; }
.block-title { font-size: 13px; font-weight: 500; color: white; }
.block-body { padding: 14px 16px; }
.block-body p { font-size: 12.5px; line-height: 1.6; margin-bottom: 8px; }
.block-who { font-size: 11px; color: var(--stone); margin-top: 8px; padding-top: 8px; border-top: 1px solid var(--border); }

/* FLAG BOXES */
.flag-box { background: var(--amber-bg); border-left: 3px solid #f59e0b; padding: 10px 14px; margin-top: 10px; border-radius: 0 4px 4px 0; }
.flag-label { font-size: 9px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: var(--amber-text); margin-bottom: 3px; display: block; }
.flag-box p { font-size: 11.5px; color: #78350f; margin: 0; line-height: 1.5; }

/* ACTION TABLE */
.action-table { width: 100%; border-collapse: collapse; font-size: 12px; margin: 10px 0; }
.action-table th { text-align: left; padding: 7px 10px; font-size: 9px; font-weight: 500; letter-spacing: 0.12em; text-transform: uppercase; color: white; background: var(--night); }
.action-table td { padding: 6px 10px; border-bottom: 1px solid var(--border); vertical-align: middle; font-size: 12px; }
.action-num { font-weight: 700; color: var(--purple); min-width: 24px; }

/* QUICK REF GRID */
.qr-grid { width: 100%; border-collapse: collapse; font-size: 12px; margin: 10px 0; }
.qr-grid td { padding: 5px 10px; border-bottom: 1px solid var(--border); }
.qr-grid td:first-child { font-weight: 500; color: var(--purple); width: 140px; background: var(--purple-light); }
```

Every block that requires something from the client gets a flag box. Consolidate all flags into the
numbered action list on the final page. For a multi-day shoot, give Day 2 and later their own block
section, marked as solo pickup.

---

## Shot list (markdown, internal)

Not a deck. Plain markdown, internal. The client never sees it. Structure:

- Block headers matching the schedule's time windows.
- Per block: a shot table (shot ID, description and framing, detail), then equipment and audio notes.
- Shot IDs are concept number plus shot or episode number (for example 003.01, 008.E2).
- Question sets for voiced concepts, with production notes the client does not need ("don't direct",
  "follow at distance", "cannot be staged").
- A capture summary table at the end (block, concept, shots or outputs) and a single conservative floor
  line for total distinct captures.
- An equipment day pack and audio kit quick reference, plus which concepts need voiced audio and which
  need none.

---

## Handover (delivery)

Built at Stage 8. Its structure and the delivery ledger are covered in
`references/delivery-closeout.md`. It uses the same base CSS plus a handful of delivery-specific
components documented there.

---

## PDF conversion

Export every HTML deck with the local printer. It uses the Chrome already on
this machine. Do not use Grok's Playwright or Chrome Headless tools.

```bash
python3 30-tools/html-to-pdf/html_to_pdf.py /absolute/path/to/deck.html
```

That writes `deck.pdf` next to the HTML. Pass a second argument to choose the
output path. Raise `--wait-ms` if headlines fall back to Georgia.

Each page div must use `height: 297mm` (not `min-height`) with `page-break-after: always`, or pages
drift and content bleeds across breaks.

If this deck will be walked in a room, ask whether a 16:9 present cut is
needed. That is a separate file, organised for presenting, not the PDF
dropped into PowerPoint. The first example is
`20-studio/sales/ways-to-work-present.js`. Open work and the order to
do it live in `20-studio/sales/README.md` under **Still open**. Do not
build a compiler until a second present cut exists.

---

## QA pagination before delivery

Render the PDF to images and inspect each page rather than eyeballing the HTML. Use `pdf2image`
(`convert_from_path`) and screenshot individual `.page` elements. Check for:

- Orphan paragraphs and stranded headings at the foot of a page.
- Boxes or cards split across a page break.
- Footer overflow or content running under the footer.
- Cover title wrapping badly or fonts falling back to Georgia (a sign the font wait was too short).

Fix and re-export until clean.
