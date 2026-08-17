# Scan notes

## Method

Metadata-first. Filename, parent path, extension, logical size and dates only.

- Pruned `find -P -xdev` traversal on all six included roots.
- Explicit filename-only Spotlight queries (`kMDItemFSName == '*term*'c`) as a cross-check
  on indexed roots. **No bare `mdfind` content search was run at any point.**
- 786 unique Spotlight name hits were used purely to confirm scan-root coverage, not as a
  content channel.

Nothing was opened, rendered, extracted, executed, OCR'd, transcribed or previewed. No file
was hashed. No archive was expanded. No macro or embedded script ran. No network request was
made. No cloud placeholder was materialised. Nothing was moved, renamed, deleted or modified,
and no source file's metadata was touched (`stat` and `lstat` only; no `atime` update on APFS
with the default `noatime`-equivalent behaviour, and no writes of any kind).

## Repository state

`git status --short` before the audit: `?? AGENTS.md`
`git status --short` after the audit: `?? AGENTS.md`

Identical. `AGENTS.md` remains untracked and untouched. No file in `~/Rua` was edited,
staged or committed. The Papa Rua migration was not advanced.

All audit output is confined to `/tmp/rua-shoot-reference-audit-20260814T011246/` (mode 0700).

## Coverage confidence

A control sweep for hits **outside** the six scan roots returned only Motion Templates
(172), Library/Application Support (67), Final Cut Backups (29), Final Cut Cache (10),
sample libraries, and the Rua repo itself. No planning or reference documents were found
outside the chosen roots. The root selection was adequate.

## Exclusions applied

- `/Volumes/Macintosh HD` — symlink to `/`, aliases the system root.
- `/Volumes/LUMIX` — camera card. Shallow root check run as instructed: **zero files at the
  root**, so no clearly named planning or reference documents. Not traversed.
- System, recovery and preboot volumes; no Time Machine or backup volume was mounted.
- Mail, Messages, Photos libraries, browser data, Keychains, Trash.
- Caches, application bundles, `.git`, `node_modules`, build outputs, package internals.
- Final Cut libraries (`.fcpbundle` ×8 on T7 alone), Logic projects (`.logicx` ×20+ in
  iCloud), Original Media, Transcoded Media, Proxies, Render Files.
- Application payloads (CrystalDiskMark, Cam2Rec, fonnts.com downloads, Spitfire, Splice)
  were traversed but dropped at ranking as noise.
- No personal financial, medical, legal or credential material was encountered in the
  filename metadata. Nothing of that kind is in the candidate set.

## Errors and access

Zero permission errors. The traversal error log is empty. All six roots were fully readable.

## Unindexed roots

`/Volumes/T7` reports `Error: unknown indexing state` from `mdutil`. Treated as unindexed;
covered by traversal only, with no Spotlight cross-check available. If something is filed
there under a name none of the priority terms would catch, this audit would not have found it.

`/Volumes/LUMIX` has Spotlight indexing disabled (excluded anyway).

## Possible cloud placeholders

248 of 1,187 candidates (21%) report a logical size with zero allocated blocks and are
recorded as `"availability": "placeholder"`. Almost all are in iCloud Drive. None were
forced to download. If any is selected for the visual-review pass it will need to be
materialised first, which is a decision for Darragh, not this audit.

Every rank-1 and rank-2 candidate is `local`. Nothing on the critical path is a placeholder.

## Interpretation corrections applied after the first report

Three corrections were issued by Darragh and are now binding on how this audit's output is read.

1. **File size is not evidence of visual progress, sophistication or quality.** Sizes are
   recorded as a change signal only. Any size-based remark is a prompt to look, not a finding.
2. **The filename search cannot prove that moodboards, storyboards or visual references are
   absent.** It only shows that none is *separately named*. Visual reference material may sit
   inside generically named decks. This is an open question for the content review.
3. **A missing named HTML source is a source-recovery gap, not proof that no editable source
   exists.** Drive, email, another machine or a prior chat session were outside this audit's
   reach.

Additionally: `shot list skehans 29052601.pdf` is surviving historical shot-list material and
is included in the visual-review sample. It is not an exemplar. The `~/Downloads` finding is
recorded as an observation only and is explicitly **not** a migration task.

## Uncertainties, stated plainly

1. **Duplicate detection is inferential.** Files were not hashed, so "probable duplicate"
   means equal size plus equal normalised name. It could be wrong. Nothing was discarded on
   that basis.
2. **exFAT dates are weak.** On both T7 volumes birth time is unreliable and often equals
   modified time. Downloads folder dates reflect *download* time, not authorship: several
   Otel meeting notes from February carry a March modified date because that is when they
   were pulled down. Chronology from this root should not be trusted without checking.
3. **Format inference from size is inference only, and size proves nothing about quality.**
   Whether `shot list skehans 29052601.pdf` (7.81 MB) is image-bearing is a question for the
   content review, not a conclusion from metadata.
4. **`~/Downloads` is doing the work of a document store.** 636 of 1,187 candidates and
   effectively every recovered sprint deliverable live there, alongside 757 top-level
   entries of unrelated material. There is no organised project archive for these documents.
   This is a real operational risk and it is why version history is patchy.
5. **Provenance is ambiguous for some items.** `The Studio Brand Colour Guide.pdf` is filed
   under a client folder but may be Rua's, the client's, or a third party's. It is marked
   ambiguous rather than assigned.
6. **Two loose copies of the skill exist outside Git** (`~/Downloads/rua-shoot-plan/` and
   `rua-shoot-plan 2/`). Their contents were not compared with the repository version. They
   may have diverged.
7. **The 79 `skehans_ig_*.png` files** are all stamped 22–23 March 2026 with dates in their
   filenames running September 2025 to January 2026. Treated as research screen captures.
   That reading is from the naming pattern alone.
8. **Rank 5 (438 items) has not been reviewed by eye.** It is a holding bucket, kept intact
   rather than deleted, but should be assumed to contain both noise and a small number of
   mis-ranked items.
