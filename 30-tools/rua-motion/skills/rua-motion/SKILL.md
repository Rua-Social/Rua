---
name: rua-motion
description: Design and refine code-driven motion graphics in the local Rua Motion studio, using a job’s fonts, colour roles and transcript cues, then render ProRes files for Final Cut.
---

The tool is at `~/Rua/30-tools/rua-motion`; the default job root is
`~/rua-motion-jobs`. The local studio is `http://127.0.0.1:4317` when started
with `npm run dev`. Use this skill for requests to create, restyle or render
motion graphics. Keep ordinary video editing and stock sourcing separate.

Read the selected job’s `project.json`, plus the tool’s `SPEC.md` and
`public/model.js` for the current catalogue. Preserve user edits. If a browser
session is active, use the API’s revision check when saving; otherwise write
the complete JSON atomically. The studio watches project files and reloads.

Translate creative direction into a specific visual change: composition,
line breaks, type scale, entrance/exit movement, pace, spacing and contrast.
The browser direction bar only supports a small deterministic vocabulary;
you are the conversational creative layer. Do not describe its presets as AI.
Keep brand facts and on-screen wording in the job. Templates consume colour
roles and slots. Font files are local to each job; do not silently replace a
missing brand font. Preserve timeline drop points and entrance cues unless
changing the timing is part of the request.

`settings.pace` changes transition duration, not entrance times. `energy`
changes movement amplitude. `scale` changes composition/type size. `scrim`
controls the dark backdrop on supported overlays. Background is transparent,
surface or gradient. Gradient blob cycles must be integers to preserve loops.

New clients: create a project through `POST /api/projects` with `{name}`, then
supply colours and font files. Inspect supplied brand material and record the
reason for proposed roles in the job’s optional `brand.evidence`. Present
uncertain brand choices as proposals. The studio currently extracts rough
palettes from uploaded logos; it does not autonomously interpret brand PDFs,
websites or videos. Any such interpretation is your work with the relevant
available tools, followed by a concrete palette the user can inspect.

SRT/VTT/iTT import is `POST /api/transcript` with `{text,extension}`. Caption
cues are phrase-level. Plain text times are estimates. Never claim exact word
alignment from phrase captions. FCPXML import is not implemented; use SRT or
iTT exported from Final Cut. Keep each graphic’s `dropPoint` in edit seconds,
and slot entrance times relative to that graphic.

For bespoke compositions, keep client-specific work in the job folder.
The initial engine supports the built-in catalogue only; extending it requires
an explicit renderer change. Do not claim an arbitrary job-side HTML file is
renderable before implementing and testing that support. Promote a new layout
into `public/templates` only after removing all client facts; run `npm run check`.

Before delivery, inspect useful frames over footage and at the requested
aspect ratio. Run meaningful tests after renderer changes. Export through
`npm run render -- <project-id> [graphic-id …]` with the server running, or use
the studio Export action. Read the returned verification reports, including
warnings; do not equate a successful encoder exit with a passing delivery.
Masters are ProRes 4444 for overlays and ProRes 422 HQ for full frame. H.264
reviews are opaque. Outputs are versioned under the job’s `renders/` folder.
Report the usable files and material limitations briefly.
