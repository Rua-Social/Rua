# Rua Motion

A local motion design studio for building branded overlays, title cards and
animated backgrounds, then rendering files for Final Cut. It lives in the Rua
repository at `30-tools/rua-motion`. Client jobs live outside the tool and
are never written into the repository.

## Open it

```sh
cd ~/Rua/30-tools/rua-motion
npm run dev
```

Open **http://127.0.0.1:4317**. Or double-click `Start Rua Motion.command`.
The studio needs Node 22+, ffmpeg and its bundled Puppeteer Chromium. On this
Mac those dependencies are installed. For a fresh checkout:

```sh
npm install
node node_modules/puppeteer/install.mjs
```

The existing jobs are in `~/rua-motion-jobs`. To use another job root:

```sh
MOTION_JOBS_DIR=/absolute/path/to/jobs npm run dev
```

A project is a directory containing `project.json` and `brand/` assets.
Renders go into a new timestamped directory each time. The previous project
save is retained as `project.previous.json`. Fonts and client artwork are
local files, not embedded in the tool’s templates. This server binds only to
localhost; it is intended for a single editor on their own computer.

## Use it

1. Choose a project, or create one. Set its colour roles and supply the font
   files under **Brand**. A new project copies the playground palette.
2. Add a graphic from the catalogue. Edit wording, entrance times, duration
   and timeline drop point under **Content**.
3. Import SRT, VTT or iTT captions and choose a cue to make a graphic. Plain
   text is accepted with explicitly estimated timing.
4. Shape pace, movement, type scale and scrim under **Motion**. Switch between
   16:9, 9:16, 1:1 and 4:5. Space plays; arrow keys step one frame.
5. Preview an overlay against a local H.264 video. Footage uses timeline drop
   point + graphic time + optional offset. Footage is preview-only.
6. Export the selected graphic or sequence. Review the files and reports in
   the resulting bundle before using the master in your edit.

The ten templates are chapter, kinetic replacement, relationship diagram,
process flow, quote, outcomes, lower third, statistic, closing invitation and
seamless gradient. The original six reference compositions retain their
landscape layouts; other ratios reflow. Long or bespoke copy still needs
creative review. The safe-area overlay is a generic 10% title guide, not a
promise about any particular platform’s changing interface.

## Talk to it

Use the studio’s direction presets for quick changes such as “calmer”,
“bigger”, “minimal” and “more contrast”. They are local rule-based controls.
For unrestricted creative direction, use the [Rua Motion skill](skills/rua-motion/SKILL.md)
in your agent conversation. **Copy brief for your agent** includes the job
path and graphic ID. Saved project edits reload in the browser. Template and stylesheet edits also
reload an idle studio; active text edits are preserved with a refresh notice.

## Render and verify

```sh
npm run render -- <project-id>                 # entire sequence
npm run render -- <project-id> <graphic-id>    # selected graphic
npm run verify -- /absolute/path/to/render-bundle/01-graphic
npm test
npm run check
npm run test:browser
```

The renderer uses the same composition module as the preview. Every frame is
explicitly sought; animation does not depend on wall-clock capture timing.
PNG buffers stream to ffmpeg. ProRes uses a fixed quantizer of 1, which eliminated
large ringing excursions found in the detailed artwork during measured tests.
This produces larger masters than the profile’s default rate allocation. See
[FFmpeg’s ProRes encoder options](https://www.ffmpeg.org/ffmpeg-codecs.html#ProRes). Each graphic produces:

| File | Use |
| --- | --- |
| `master-4444.mov` or `master-422HQ.mov` | ProRes master; 4444 retains alpha |
| `review.mp4` | Opaque H.264 review, CRF 10; overlays flattened onto brand ink |
| `poster.png` | Representative still; overlays retain transparency |
| `manifest.json` | Exact render settings, frame count and drop point |
| `verification.json` | Measured delivery checks |

Each sequence also gets a contact sheet, timing CSV and project snapshot.
Both video files are explicitly tagged Rec.709 through `setparams` and output
tags. Screenshots originate at 8-bit precision; ProRes does not invent extra
source precision. The gradient keeps the reference single-pass float shader
and triangular dither before quantisation.

Verification extends the reference algorithms: frame counts, dimensions,
frame rate, all colour tags, alpha presence and sampled decoded signal
levels. Gradient loops additionally measure the join and centre-scanline flat
runs. Flat runs are a heuristic and intentional flat areas can trigger them.
Preflight includes supplied-font availability, cue timing, reading-rate and
palette contrast heuristics, plus a small common-misspelling list. It is not a
full proofreader or a guarantee of broadcast compliance.

## What is intentionally still limited

- Brand intake is manual roles, local fonts, logo upload and rough logo
  palette extraction. Automated PDF/site/video brand interpretation is not built.
- Captions import phrase timings; exact word alignment and FCPXML are not built.
- Footage legibility is visually reviewed; automated contrast throughout a
  video and colour-blind simulation are not built.
- No in-app LLM or voice recognition. Your coding agent is the conversational layer.
- The initial template catalogue is built in. Job-side bespoke templates need
  a future loader; a random HTML file cannot yet be selected in the studio.
- Font weight/style inference uses filenames. Rename unusually named font
  files or edit their `weight` and `style` records in `project.json`.

Final Cut Pro 12.4 is installed on this Mac. Apple documents caption export
as separate SRT/iTT files: [Export closed captions](https://support.apple.com/guide/final-cut-pro/ver245c7581b/mac).
The actual installed Final Cut export menu has not been exercised in this build.

See [SPEC.md](SPEC.md) for the job and renderer contracts. Local test
artefacts are excluded from version control. The client reference engines and
the original research handoff stay outside the repository. Do not copy client
jobs into this tool.
