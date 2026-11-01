import base64
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import storyboard as sb


PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aX1sAAAAASUVORK5CYII=')


class ProjectTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.root = self.base / 'project'
        self.root.mkdir()
        (self.root / 'assets').mkdir()
        (self.root / 'assets/frame.png').write_bytes(PNG)
        self.board = {'title': 'A café </ScRiPt> scene', 'sequences': [{'id': 'A', 'title': 'Arrival'}],
                      'shots': [{'id': 'S01', 'sequence': 'A', 'duration': 3, 'title': 'The door', 'imageIndex': 0}],
                      'decisions': [], 'references': [], 'workflow': [], 'glossary': []}
        self.manifest = {'version': 1, 'storageKey': 'test-project', 'config': {'brand': 'Test', 'databaseName': 'test-db'},
                         'board': 'board.json', 'assets': {'board-a': 'assets/frame.png'}, 'audio': None,
                         'output': '../working/board.html', 'earlier': '../earlier'}
        self.write_source()

    def write_source(self):
        (self.root / 'board.json').write_text(sb.json_text(self.board))
        (self.root / 'project.json').write_text(sb.json_text(self.manifest))

    def snapshot(self, board=None, audio=sb.MISSING):
        pairs = [('STORYBOARD_DATA', board or self.board), ('STORYBOARD_ASSETS', {'board-a': 'data:image/png;base64,' + base64.b64encode(PNG).decode()})]
        if audio is not sb.MISSING:
            pairs.append(('STORYBOARD_AUDIO', audio))
        path = self.base / 'snapshot.html'
        path.write_text('<!doctype html><script>' + ''.join(f'window.{k}={sb.embedded_json(v)};' for k, v in pairs) + '</script>')
        return path

    def test_portable_build_and_script_text_roundtrip(self):
        out, backup, report = sb.build(self.root)
        self.assertIsNone(backup)
        self.assertIn('1 panels / 3 seconds', report)
        built, assets, audio = sb.parse_snapshot(out)
        self.assertEqual(built['title'], self.board['title'])
        self.assertEqual(sb.decode_data_url(assets['board-a'], sb.IMAGE_TYPES, 'frame')[0], PNG)
        self.assertIsNone(audio)
        self.assertEqual(len(built['sourceRevision']), 64)
        self.assertNotIn('<script src=', out.read_text())
        self.assertNotIn('<link rel="stylesheet"', out.read_text())

    def test_build_archives_previous_and_is_deterministic(self):
        out, _, _ = sb.build(self.root)
        first = out.read_bytes()
        self.assertIsNone(sb.build(self.root)[1])
        self.board['shots'][0]['duration'] = 4
        self.write_source()
        _, backup, _ = sb.build(self.root)
        self.assertEqual(backup.parent, self.base / 'earlier')
        self.assertEqual(backup.read_bytes(), first)
        self.assertNotEqual(out.read_bytes(), first)

    def test_invalid_source_does_not_replace_existing_output(self):
        out, _, _ = sb.build(self.root)
        original = out.read_bytes()
        self.board['shots'][0]['duration'] = float('nan')
        (self.root / 'board.json').write_text(json.dumps(self.board))
        with self.assertRaises(sb.ProjectError):
            sb.build(self.root)
        self.assertEqual(out.read_bytes(), original)

    def test_import_recovers_frames_music_settings_and_keeps_backup(self):
        edited = copy.deepcopy(self.board)
        edited['shots'][0]['title'] = 'Édit </script> preserved'
        edited['shots'][0]['customImage'] = 'data:image/png;base64,' + base64.b64encode(PNG).decode()
        edited['videoExportSettings'] = {'width': 1280, 'audio': {'trimIn': 2, 'offset': 3}}
        audio_bytes = b'RIFF-test-audio'
        snapshot = self.snapshot(edited, {'name': 'track.wav', 'data': 'data:audio/wav;base64,' + base64.b64encode(audio_bytes).decode()})
        before = (self.root / 'board.json').read_bytes()
        backup, report = sb.import_snapshot(snapshot, self.root, expected_panels=1)
        self.assertEqual((backup / 'board.json').read_bytes(), before)
        on_disk = sb.read_json(self.root / 'board.json')
        self.assertNotIn('customImage', on_disk['shots'][0])
        self.assertEqual((self.root / on_disk['shots'][0]['customImagePath']).read_bytes(), PNG)
        project = sb.read_json(self.root / 'project.json')
        self.assertEqual(project['storageKey'], 'test-project')
        self.assertEqual((self.root / project['audio']['path']).read_bytes(), audio_bytes)
        out, _, _ = sb.build(self.root)
        restored, _, audio = sb.parse_snapshot(out)
        self.assertEqual(restored['videoExportSettings'], edited['videoExportSettings'])
        self.assertEqual(restored['shots'][0]['title'], edited['shots'][0]['title'])
        self.assertEqual(audio['name'], 'track.wav')

    def test_json_and_review_import_preserve_music_until_explicit_clear(self):
        (self.root / 'track.mp3').write_bytes(b'original music')
        self.manifest['audio'] = {'path': 'track.mp3', 'name': 'track.mp3'}
        self.write_source()
        snapshot = self.base / 'snapshot.json'
        snapshot.write_text(sb.json_text(self.board))
        sb.import_snapshot(snapshot, self.root)
        self.assertEqual(sb.load_project(self.root)[4]['name'], 'track.mp3')
        review = self.snapshot(audio=None)
        sb.import_snapshot(review, self.root)
        self.assertEqual(sb.load_project(self.root)[4]['name'], 'track.mp3')
        sb.import_snapshot(review, self.root, clear_audio=True)
        self.assertIsNone(sb.load_project(self.root)[4])

    def test_import_rejects_wrong_panel_count_and_executable_data(self):
        original = (self.root / 'board.json').read_bytes()
        snapshot = self.snapshot()
        with self.assertRaises(sb.ProjectError):
            sb.import_snapshot(snapshot, self.root, expected_panels=32)
        snapshot.write_text('<script>window.STORYBOARD_DATA=alert("execute");</script>')
        with self.assertRaises(sb.ProjectError):
            sb.import_snapshot(snapshot, self.root)
        self.assertEqual((self.root / 'board.json').read_bytes(), original)

    def test_missing_asset_and_escape_path_rejected(self):
        self.manifest['assets']['board-a'] = '../outside.png'
        (self.base / 'outside.png').write_bytes(PNG)
        self.write_source()
        with self.assertRaises(sb.ProjectError):
            sb.load_project(self.root)
        self.manifest['assets']['board-a'] = 'assets/missing.png'
        self.write_source()
        with self.assertRaises(sb.ProjectError):
            sb.load_project(self.root)

    def test_import_rolls_back_failed_directory_install(self):
        original = (self.root / 'board.json').read_bytes()
        snapshot = self.snapshot()
        replace = sb.os.replace
        def fail_staged_install(src, dst):
            if Path(src).name.startswith('.storyboard-import-'):
                raise OSError('simulated install failure')
            return replace(src, dst)
        with patch.object(sb.os, 'replace', side_effect=fail_staged_install):
            with self.assertRaises(OSError):
                sb.import_snapshot(snapshot, self.root)
        self.assertEqual((self.root / 'board.json').read_bytes(), original)

    def test_project_named_earlier_cannot_recursively_copy_itself(self):
        snapshot = self.snapshot()
        renamed = self.root.parent / 'earlier'
        self.root.rename(renamed)
        with self.assertRaisesRegex(sb.ProjectError, 'earlier-versions folder'):
            sb.import_snapshot(snapshot, renamed)
        self.assertEqual(sb.read_json(renamed / 'board.json'), self.board)

    def test_revision_tracks_branding_not_save_timestamp(self):
        out, _, _ = sb.build(self.root)
        first = sb.parse_snapshot(out)[0]['sourceRevision']
        self.board.update(savedAt=1234, sourceRevision='old')
        self.write_source()
        sb.build(self.root)
        self.assertEqual(sb.parse_snapshot(out)[0]['sourceRevision'], first)
        self.manifest['config']['brand'] = 'New brand'
        self.write_source()
        sb.build(self.root)
        self.assertNotEqual(sb.parse_snapshot(out)[0]['sourceRevision'], first)


if __name__ == '__main__':
    unittest.main()
