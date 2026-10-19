# Rua Motion — standalone studio

The tool lives here. Jobs live outside it, initially in `~/rua-motion-jobs`.
Jobs are never written into the Rua repository. Client reference copies stay
outside it.

## Job contract (v1)

`project.json` contains an ID, name, output size, rational frame rate, brand,
graphics, transcript and optional preview footage. `brand/` holds supplied
fonts and artwork; `renders/` holds versioned delivery bundles.

Brand roles: accent, secondary, highlight, alert, surface, text, ink, muted.
Fonts have a family plus local file/weight/style records. Graphics never
substitute missing uploaded fonts. File paths are relative to the job.

A graphic has ID, template, label, duration in seconds, timeline drop point,
slots (text and entrance time), and settings: energy (0–1), pace (0.5–2),
scale (0.65–1.3), scrim (0–0.8), and background (transparent/surface/gradient).
Template-specific settings include swap time, exit time and gradient blobs.
Times are relative to the graphic; drop points are relative to the edit.

## Template contract

Templates consume roles and slots only. Build after local fonts load. Every
frame is seekable without a clock, including WebGL loops. Landscape legacy
layouts preserve the originals; portrait and square layouts reflow. The
catalogue includes kinetic replacement, relationship, process, quote,
outcomes, lower third, gradient, chapter, statistic and call to action.

## Studio

Local Node server, buildless browser UI, shared deterministic composition
module for preview and export. Editable fields, motion controls, palette,
local fonts, logo, graphic catalogue, exact frame scrubbing, safe areas,
footage preview, SRT/VTT/iTT import and cue-to-graphic creation. Plain text
transcripts have explicitly estimated timing. Direction presets apply
transparent deterministic changes; freeform creative work uses the agent
workflow and live project-file reload, without an API key in the browser.

## Delivery

Bundled Puppeteer Chromium; PNG frames piped to one ffmpeg process. Overlay
master is ProRes 4444 with alpha; full frame is ProRes 422 HQ. H.264 review
is opaque. Both use explicit Rec.709 filter tagging. Each bundle includes
poster, contact sheet, job snapshot, timing manifest and decoded-file report.
Rendering snapshots a saved job, prevents concurrent exports, reports progress,
supports cancellation, and preserves previous exports.

Extend the existing measured verification algorithms: delivered metadata,
frame count, sampled code values, alpha, gradient loop join and banding.
Preflight checks dimensions, fonts, text length, reading time, contrast,
spelling candidates and overflow. Reports distinguish measurements from
heuristics. No unconditional “safe to deliver” claim.

## Completion checks

Open both reference engines. Migrate both original jobs outside the tool.
Check render determinism, template purity, import timing, persistence, asset
containment and exports. Inspect the studio and representative graphic frames.
Render real alpha and full-frame samples and probe their delivered files.
