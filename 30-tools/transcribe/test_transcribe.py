"""Unit tests for transcribe. No model download or GPU needed."""

import pytest

from transcribe import (
    collapse_loops,
    find_media,
    srt_timestamp,
    write_srt,
    write_txt,
)


def _segment(text, start=0.0, end=1.0):
    return {"text": text, "start": start, "end": end}


class TestFindMedia:
    def test_single_media_file(self, tmp_path):
        clip = tmp_path / "interview.mp4"
        clip.touch()
        assert find_media(clip) == [clip]

    def test_folder_iterates_media_sorted_and_skips_rest(self, tmp_path):
        for name in ["b.wav", "a.mp4", "notes.txt", "c.MOV"]:
            (tmp_path / name).touch()
        found = find_media(tmp_path)
        assert [p.name for p in found] == ["a.mp4", "b.wav", "c.MOV"]

    def test_folder_skips_appledouble_sidecar_wavs(self, tmp_path):
        (tmp_path / "interview.wav").touch()
        (tmp_path / "._interview.wav").touch()
        found = find_media(tmp_path)
        assert [p.name for p in found] == ["interview.wav"]

    def test_non_media_file_rejected(self, tmp_path):
        notes = tmp_path / "notes.txt"
        notes.touch()
        with pytest.raises(ValueError, match="not a media file"):
            find_media(notes)

    def test_empty_folder_rejected(self, tmp_path):
        with pytest.raises(ValueError, match="no media files"):
            find_media(tmp_path)

    def test_missing_path_rejected(self, tmp_path):
        with pytest.raises(ValueError, match="no such file or folder"):
            find_media(tmp_path / "nope.mp4")


class TestCollapseLoops:
    def test_loop_collapses_after_second_repeat(self):
        segments = [_segment("Much better?", start=i, end=i + 1) for i in range(14)]
        kept, dropped = collapse_loops(segments)
        assert [s["text"] for s in kept] == ["Much better?", "Much better?"]
        assert dropped == 12

    def test_genuine_double_retake_survives(self):
        segments = [
            _segment("We also have these lovely pendant lights from Umage."),
            _segment("We also have these lovely pendant lights from Umage."),
        ]
        kept, dropped = collapse_loops(segments)
        assert len(kept) == 2
        assert dropped == 0

    def test_non_consecutive_repeats_all_kept(self):
        segments = [
            _segment("same line"),
            _segment("different line"),
            _segment("same line"),
            _segment("different line"),
            _segment("same line"),
        ]
        kept, dropped = collapse_loops(segments)
        assert len(kept) == 5
        assert dropped == 0

    def test_matching_ignores_case_and_whitespace(self):
        segments = [
            _segment("Tape."),
            _segment("tape."),
            _segment("  Tape.  "),
            _segment("TAPE."),
        ]
        kept, dropped = collapse_loops(segments)
        assert len(kept) == 2
        assert dropped == 2

    def test_empty_text_segments_do_not_form_runs(self):
        segments = [_segment(""), _segment(""), _segment("")]
        kept, dropped = collapse_loops(segments)
        assert len(kept) == 3
        assert dropped == 0


class TestSrtTimestamp:
    def test_zero(self):
        assert srt_timestamp(0) == "00:00:00,000"

    def test_millis_rounding(self):
        assert srt_timestamp(601.44) == "00:10:01,440"

    def test_hours(self):
        assert srt_timestamp(3661.5) == "01:01:01,500"


class TestWriters:
    def test_write_srt_numbers_and_separates_blocks(self, tmp_path):
        out = tmp_path / "clip.srt"
        write_srt(
            [
                _segment("First line.", 0.0, 1.5),
                _segment("Second line.", 1.5, 3.0),
            ],
            out,
        )
        assert out.read_text() == (
            "1\n00:00:00,000 --> 00:00:01,500\nFirst line.\n"
            "\n"
            "2\n00:00:01,500 --> 00:00:03,000\nSecond line.\n"
        )

    def test_write_txt_one_segment_per_line(self, tmp_path):
        out = tmp_path / "clip.txt"
        write_txt([_segment("First line."), _segment("Second line.")], out)
        assert out.read_text() == "First line.\nSecond line.\n"
