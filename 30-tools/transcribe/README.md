# transcribe

Turn shoot dialogue footage into transcripts for the edit-guide chat.
Local mlx-whisper on this Mac. Two models: `whisper-large-v3` (edit
guide) and `--fast` turbo (scout only). Do not send this audio to a
cloud STT.

Tested on two real shoot interviews (10 min and 17 min) against FCP's own
captions. Whisper won on brand names, punctuation and coverage.

## Requires

- macOS on Apple Silicon
- ffmpeg (`brew install ffmpeg`)
- python3 (the system one is fine)

## Install

```
cd 30-tools/transcribe
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

The first run downloads the model (about 3GB) into
`~/.cache/huggingface`, shared with anything else that uses it later.

## Use

```
.venv/bin/python transcribe.py "/path/to/clip.mp4" \
  --prompt "Kitchen design interview with the designer. Brand and client names here."
```

- Input is one file or a folder. A folder is iterated sorted, media files
  only (`mp4 mov m4v m4a wav mp3 aac`), everything else skipped.
- Default output is one `.srt` per input, alongside the input. `--out dir`
  redirects. `--formats srt,txt` adds a prose `.txt`.
- `--prompt` primes names and vocabulary (brands, people, venues). Worth
  doing per client: it fixed every brand miss in testing.
- `--language en` is the default.

## Model choice

Default is `whisper-large-v3`: punctuated, sentence-level segments,
brand-accurate when primed. Use it for anything that feeds the edit guide,
a copy bank or captions.

`--fast` uses `whisper-large-v3-turbo`. Measured on the ship run
(10-minute clip, M-series): v3 took 50s, turbo 13s. The speed is real,
but output is unpunctuated, and in the same run turbo rendered a primed
brand name phonetically anyway ("deckton") while v3 landed the primed
spelling. Use it for scouting, selects and "what did they say about X"
searches on long footage, never for quotes or the edit guide.

## What it always does

- Runs with `condition_on_previous_text=False`. Without it the full model
  can loop permanently on repeated speech and lose the rest of the clip.
- Collapses remaining loops: the third identical consecutive segment
  onwards is dropped. Genuine double retakes survive. The drop count is
  printed per file.

## Formats

- `srt` (default): text with timecodes, readable by the edit-guide chat
  and importable into FCP as captions.
- `txt` (on request): prose for quoting into a copy bank.
- VTT, TSV and JSON are deliberately not produced.

## Errors

- `ffmpeg not found on PATH`: install ffmpeg.
- `no media files in ...`: the folder has nothing whisper can read.

## Test

```
.venv/bin/python -m pytest test_transcribe.py
```
