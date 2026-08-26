#!/usr/bin/env python3
"""transcribe: turn shoot dialogue footage into transcripts for edit guides.

Wraps mlx-whisper with the settings the shoot workflow tested:
large-v3 by default, turbo with --fast, no conditioning on previous text
(permanent repetition loops without it), SRT by default, and a guard that
collapses runs of identical segments.
"""

from __future__ import annotations

import argparse
import shutil
import sys
import time
from pathlib import Path

MEDIA_EXTENSIONS = {".mp4", ".mov", ".m4v", ".m4a", ".wav", ".mp3", ".aac"}

DEFAULT_MODEL = "mlx-community/whisper-large-v3-mlx"
FAST_MODEL = "mlx-community/whisper-large-v3-turbo"


def find_media(target: Path) -> list[Path]:
    """Resolve the input argument to a sorted list of media files."""
    if target.is_file():
        if target.suffix.lower() not in MEDIA_EXTENSIONS:
            raise ValueError(f"not a media file: {target.name}")
        return [target]
    if target.is_dir():
        files = sorted(
            p for p in target.iterdir()
            if p.is_file() and p.suffix.lower() in MEDIA_EXTENSIONS
        )
        if not files:
            raise ValueError(f"no media files in {target}")
        return files
    raise ValueError(f"no such file or folder: {target}")


def collapse_loops(segments: list[dict], min_run: int = 3) -> tuple[list[dict], int]:
    """Drop the min_run-th identical consecutive segment onwards.

    Whisper loops on messy audio (direction chatter, silence tails) and
    emits the same line repeatedly. Genuine double retakes survive; loops
    do not. Returns (kept segments, dropped count).
    """
    kept: list[dict] = []
    dropped = 0
    last_key = None
    run_length = 0
    for segment in segments:
        key = " ".join(segment["text"].split()).lower()
        if key and key == last_key:
            run_length += 1
            if run_length >= min_run:
                dropped += 1
                continue
        else:
            last_key = key
            run_length = 1
        kept.append(segment)
    return kept, dropped


def srt_timestamp(seconds: float) -> str:
    ms = round(seconds * 1000)
    hours, rem = divmod(ms, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    secs, millis = divmod(rem, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def write_srt(segments: list[dict], path: Path) -> None:
    blocks = []
    for index, segment in enumerate(segments, 1):
        blocks.append(
            f"{index}\n"
            f"{srt_timestamp(segment['start'])} --> {srt_timestamp(segment['end'])}\n"
            f"{segment['text'].strip()}\n"
        )
    path.write_text("\n".join(blocks), encoding="utf-8")


def write_txt(segments: list[dict], path: Path) -> None:
    text = "\n".join(segment["text"].strip() for segment in segments)
    path.write_text(text + "\n", encoding="utf-8")


def transcribe_file(
    audio_path: Path,
    model: str,
    prompt: str | None,
    language: str,
) -> tuple[list[dict], int]:
    """Run the model and apply the loop guard. Returns (segments, dropped)."""
    import mlx_whisper  # deferred: --help and unit tests must not need mlx

    result = mlx_whisper.transcribe(
        str(audio_path),
        path_or_hf_repo=model,
        language=language,
        initial_prompt=prompt,
        condition_on_previous_text=False,
        verbose=False,
    )
    segments = [s for s in result["segments"] if s["text"].strip()]
    return collapse_loops(segments)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="transcribe",
        description="Transcribe shoot dialogue footage for edit guides.",
    )
    parser.add_argument("input", type=Path, help="media file or folder of media files")
    parser.add_argument(
        "--fast",
        action="store_true",
        help="use large-v3-turbo: quicker, but unpunctuated and loop-prone. "
        "For scouting and searches, never for quotes (provisional, see spec.md).",
    )
    primer = parser.add_mutually_exclusive_group()
    primer.add_argument("--prompt", help="one sentence of client vocabulary")
    primer.add_argument("--prompt-file", type=Path, help="file holding the vocabulary primer")
    parser.add_argument("--formats", default="srt", help="comma-separated: srt,txt (default srt)")
    parser.add_argument("--out", type=Path, help="output folder (default: alongside the input)")
    parser.add_argument("--language", default="en")
    args = parser.parse_args(argv)

    if shutil.which("ffmpeg") is None:
        sys.exit("error: ffmpeg not found on PATH (brew install ffmpeg)")

    formats = {f.strip() for f in args.formats.split(",")}
    unknown = formats - {"srt", "txt"}
    if unknown:
        sys.exit(f"error: unknown format(s): {', '.join(sorted(unknown))} (choose from srt, txt)")

    prompt = args.prompt
    if args.prompt_file:
        prompt = args.prompt_file.read_text(encoding="utf-8").strip()

    try:
        media = find_media(args.input)
    except ValueError as error:
        sys.exit(f"error: {error}")

    model = FAST_MODEL if args.fast else DEFAULT_MODEL
    for path in media:
        out_dir = args.out or path.parent
        out_dir.mkdir(parents=True, exist_ok=True)
        print(f"transcribing {path.name} ({model.rsplit('/', 1)[-1]})", flush=True)
        started = time.monotonic()
        segments, dropped = transcribe_file(path, model, prompt, args.language)
        outputs = []
        if "srt" in formats:
            outputs.append(out_dir / f"{path.stem}.srt")
            write_srt(segments, outputs[-1])
        if "txt" in formats:
            outputs.append(out_dir / f"{path.stem}.txt")
            write_txt(segments, outputs[-1])
        elapsed = time.monotonic() - started
        note = f", collapsed {dropped} looped segment(s)" if dropped else ""
        print(f"  {len(segments)} segments in {elapsed:.0f}s{note}")
        for output in outputs:
            print(f"  -> {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
