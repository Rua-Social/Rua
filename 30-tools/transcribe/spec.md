# transcribe spec

## Goal

One command that turns shoot dialogue footage into transcripts good enough
to feed the edit-guide chat, replacing the FCP closed-captions to ITT
round trip.

## Out of scope

Speaker diarization, watchers or services, per-client vocab config files,
web UI, caption burn-in, FCP import automation, and the edit-guide
generation itself (stays a chat step).

## Interface

```
transcribe <file-or-folder> [--fast] [--prompt "..." | --prompt-file f]
           [--formats srt[,txt]] [--out dir] [--language en]
```

- Default model `mlx-community/whisper-large-v3-mlx`. `--fast` switches to
  `mlx-community/whisper-large-v3-turbo`.
- `condition_on_previous_text=False` baked in. Testing showed the full
  model loops permanently on repeated speech without it.
- Default export SRT only. TXT when requested. No VTT, TSV or JSON.
- Outputs named after the input file. Folder mode iterates media files
  and skips the rest.
- Loop guard: the third identical consecutive segment onwards is dropped.
  Genuine double retakes survive; loops do not.
- Plain errors for missing ffmpeg or no media found.

## Model guidance (provisional)

Tested on two real shoot interviews (10 min and 17 min) against FCP's own
captions: large-v3 with a client-vocab prompt wins on brand names,
punctuation and coverage. Turbo is included on the strength of one clean
clip and its expected speed on long footage, but its use cases (scouting,
selects, searches) are expectations to verify, not measurements. Its
output is unpunctuated and its tails loop more. If the speed advantage
proves marginal in real use, remove `--fast`.

## Session and look

Raw CLI, inherited host. No EXPERIENCE.md, no DESIGN.md (html-to-pdf
precedent).

## Done

- README's exact command runs in-session on real footage and produces an
  SRT matching the tested quality bar: full coverage, no phantom tail,
  brand names right when primed.
- `pytest` green for the loop guard, discovery, naming and writers.
