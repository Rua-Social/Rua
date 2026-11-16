import base64
import http.client
import json
import os
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

import storyboard as sb
import studio


PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aX1sAAAAASUVORK5CYII=')
PNG_URL = 'data:image/png;base64,' + base64.b64encode(PNG).decode()


class StudioTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.root = self.base / 'project'
        (self.root / 'assets').mkdir(parents=True)
        (self.root / 'assets/frame.png').write_bytes(PNG)
        self.board = {'title': 'Test film', 'sequences': [{'id': 'A', 'title': 'Arrival'}],
                      'shots': [{'id': 'S01', 'sequence': 'A', 'duration': 3, 'title': 'The door', 'imageIndex': 0}]}
        manifest = {'version': 1, 'storageKey': 'test', 'config': {'brand': 'Test film'}, 'board': 'board.json',
                    'assets': {'board-a': 'assets/frame.png'}, 'audio': None, 'output': '../working/board.html', 'earlier': '../earlier'}
        (self.root / 'board.json').write_text(sb.json_text(self.board))
        (self.root / 'project.json').write_text(sb.json_text(manifest))
        config = patch.object(studio, 'CONFIG_DIR', self.base / 'config')
        config.start()
        self.addCleanup(config.stop)
        self.ident, self.project = studio.remember(self.root)
        self.server = studio.make_server(0)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)
        self.port = self.server.server_address[1]

    def call(self, method, path, body=None, rev=None, headers=None, host=None):
        conn = http.client.HTTPConnection('127.0.0.1', self.port, timeout=10)
        sent = {'X-Storyboard': '1', **({'X-Storyboard-Rev': rev} if rev is not None else {}), **(headers or {})}
        if host:
            sent['Host'] = host
        if isinstance(body, (dict, list)):
            body = json.dumps(body).encode()
            sent['Content-Type'] = 'application/json'
        conn.request(method, path, body=body, headers=sent)
        response = conn.getresponse()
        data = response.read()
        conn.close()
        try:
            return response.status, json.loads(data)
        except ValueError:
            return response.status, data.decode('utf-8', 'replace')

    def rev(self):
        return studio.revision(self.project)

    def edited(self, title, image=False):
        board = json.loads(json.dumps(self.board))
        board['shots'][0]['title'] = title
        board.update(sourceRevision='x', savedAt=1, edited=True)
        if image:
            board['shots'][0]['customImage'] = PNG_URL
        return board

    def test_page_opens_from_disk_with_studio_settings(self):
        status, html = self.call('GET', f'/p/{self.ident}')
        self.assertEqual(status, 200)
        self.assertIn('window.STORYBOARD_STUDIO=', html)
        self.assertIn(f'"rev":"{self.rev()}"', html)
        status, home = self.call('GET', '/api/projects')
        self.assertEqual(home['projects'][0]['title'], 'Test film')

    def test_edits_save_to_disk_and_images_become_files(self):
        status, result = self.call('PUT', f'/api/p/{self.ident}/board', self.edited('Saved to disk', image=True), rev=self.rev())
        self.assertEqual(status, 200, result)
        saved = sb.read_json(self.root / 'board.json')
        self.assertEqual(saved['shots'][0]['title'], 'Saved to disk')
        self.assertNotIn('customImage', saved['shots'][0])
        self.assertTrue((self.root / saved['shots'][0]['customImagePath']).is_file())
        for key in sb.VOLATILE_KEYS:
            self.assertNotIn(key, saved)
        self.assertEqual(result['rev'], self.rev())

    def test_a_stale_window_cannot_overwrite_newer_work(self):
        old = self.rev()
        self.call('PUT', f'/api/p/{self.ident}/board', self.edited('Window one'), rev=old)
        status, result = self.call('PUT', f'/api/p/{self.ident}/board', self.edited('Window two'), rev=old)
        self.assertEqual(status, 409)
        self.assertIn('another window', result['error'])
        self.assertEqual(sb.read_json(self.root / 'board.json')['shots'][0]['title'], 'Window one')

    def test_invalid_board_is_refused_and_disk_is_unchanged(self):
        before = (self.root / 'board.json').read_text()
        status, _ = self.call('PUT', f'/api/p/{self.ident}/board', {'shots': []}, rev=self.rev())
        self.assertEqual(status, 400)
        self.assertEqual((self.root / 'board.json').read_text(), before)

    def test_automatic_snapshots_are_spaced_and_capped(self):
        os.utime(self.root / 'board.json', (1, 1))
        self.call('PUT', f'/api/p/{self.ident}/board', self.edited('One'), rev=self.rev())
        self.call('PUT', f'/api/p/{self.ident}/board', self.edited('Two'), rev=self.rev())
        manifest = sb.read_json(self.project)
        snaps = studio.snapshots(self.project, manifest)
        self.assertEqual(len(snaps), 1, 'Only one snapshot inside ten minutes')
        self.assertEqual(studio.read_autosave(snaps[0])[0]['shots'][0]['title'], 'The door', 'The snapshot holds the board before the session')
        self.assertGreater(snaps[0].stat().st_mtime, 1, 'Snapshots use creation time, not the old board modification time')
        with patch.object(studio, 'SNAPSHOTS_KEPT', 3):
            for _ in range(5):
                studio.take_snapshot(self.project, manifest, force=True)
            self.assertEqual(len(studio.snapshots(self.project, manifest)), 3)

    def test_save_version_builds_the_shareable_file_and_restore_goes_back(self):
        status, first = self.call('POST', f'/api/p/{self.ident}/version', {'label': 'First cut'}, rev=self.rev())
        self.assertEqual(status, 200, first)
        self.assertTrue((self.base / 'working/board.html').is_file())
        self.call('PUT', f'/api/p/{self.ident}/board', self.edited('Second idea'), rev=self.rev())
        status, second = self.call('POST', f'/api/p/{self.ident}/version', {'label': 'Second idea'}, rev=self.rev())
        self.assertIn('version 2', second['report'])
        status, history = self.call('GET', f'/api/p/{self.ident}/history')
        self.assertEqual([v['n'] for v in history['versions']], [2, 1])
        self.assertTrue(all(v['restorable'] for v in history['versions']))
        status, result = self.call('POST', f'/api/p/{self.ident}/restore', {'version': 1}, rev=self.rev())
        self.assertEqual(status, 200, result)
        self.assertEqual(sb.read_json(self.root / 'board.json')['shots'][0]['title'], 'The door')
        manifest = sb.read_json(self.project)
        kept = [studio.read_autosave(s)[0]['shots'][0]['title'] for s in studio.snapshots(self.project, manifest)]
        self.assertIn('Second idea', kept, 'What you had is kept before a restore')

    def test_restore_an_automatic_save(self):
        self.call('PUT', f'/api/p/{self.ident}/board', self.edited('Later'), rev=self.rev())
        status, history = self.call('GET', f'/api/p/{self.ident}/history')
        name = history['autosaves'][0]['name']
        status, _ = self.call('POST', f'/api/p/{self.ident}/restore', {'autosave': '../../' + name}, rev=self.rev())
        self.assertEqual(status, 200)
        self.assertEqual(sb.read_json(self.root / 'board.json')['shots'][0]['title'], 'The door')

    def test_music_saves_into_the_project_and_can_be_removed(self):
        status, _ = self.call('PUT', f'/api/p/{self.ident}/audio?name=Temp%20track.mp3', b'ID3fakeaudio', rev=self.rev(), headers={'Content-Type': 'audio/mpeg'})
        self.assertEqual(status, 200)
        manifest = sb.read_json(self.project)
        self.assertEqual(manifest['audio']['name'], 'Temp track.mp3')
        self.assertTrue((self.root / manifest['audio']['path']).is_file())
        status, _ = self.call('DELETE', f'/api/p/{self.ident}/audio', rev=self.rev())
        self.assertIsNone(sb.read_json(self.project)['audio'])

    def test_invalid_image_dependencies_cannot_replace_the_board(self):
        before = (self.root / 'board.json').read_bytes()
        rev = self.rev()
        (self.root / 'assets/empty.png').write_bytes(b'')
        (self.root / 'assets/unsupported.txt').write_text('not an image')
        for change in ({'imageIndex': 8}, {'customImagePath': 'assets/missing.png'},
                       {'customImagePath': 'assets/empty.png'}, {'customImagePath': 'assets/unsupported.txt'}):
            with self.subTest(change=change):
                candidate = self.edited('Should never reach disk')
                candidate['shots'][0].update(change)
                status, result = self.call('PUT', f'/api/p/{self.ident}/board', candidate, rev=rev)
                self.assertEqual(status, 400, result)
                self.assertEqual((self.root / 'board.json').read_bytes(), before)
                self.assertEqual(self.rev(), rev)
                self.assertEqual(studio.history(self.project)['autosaves'], [])

    def test_audio_only_changes_keep_recoverable_snapshots(self):
        with patch.object(studio, 'SNAPSHOT_EVERY', 0):
            status, result = self.call('PUT', f'/api/p/{self.ident}/audio?name=track-a.mp3', b'ID3trackA', rev=self.rev())
            self.assertEqual(status, 200, result)
            status, result = self.call('DELETE', f'/api/p/{self.ident}/audio', rev=self.rev())
            self.assertEqual(status, 200, result)
        history = studio.history(self.project)['autosaves']
        self.assertEqual(len(history), 2)
        status, result = self.call('POST', f'/api/p/{self.ident}/restore', {'autosave': history[0]['name']}, rev=self.rev())
        self.assertEqual(status, 200, result)
        self.assertEqual(sb.read_json(self.project)['audio']['name'], 'track-a.mp3')
        status, result = self.call('POST', f'/api/p/{self.ident}/restore', {'autosave': history[1]['name']}, rev=self.rev())
        self.assertEqual(status, 200, result)
        self.assertIsNone(sb.read_json(self.project)['audio'], 'A snapshot also records deliberate silence')

    def test_restore_and_undo_preserve_board_soundtrack_and_atlas(self):
        self.call('PUT', f'/api/p/{self.ident}/audio?name=track-a.mp3', b'ID3trackA', rev=self.rev())
        status, result = self.call('POST', f'/api/p/{self.ident}/version', {'label': 'First cut'}, rev=self.rev())
        self.assertEqual(status, 200, result)
        # The newer work has another panel, soundtrack and atlas, but is not yet a named version.
        self.call('PUT', f'/api/p/{self.ident}/board', self.edited('Later'), rev=self.rev())
        self.call('PUT', f'/api/p/{self.ident}/audio?name=track-b.mp3', b'ID3trackB', rev=self.rev())
        later_atlas = PNG + b'new atlas'
        (self.root / 'assets/frame.png').write_bytes(later_atlas)
        status, result = self.call('POST', f'/api/p/{self.ident}/restore', {'version': 1}, rev=self.rev())
        self.assertEqual(status, 200, result)
        manifest = sb.read_json(self.project)
        self.assertEqual(sb.read_json(self.root / 'board.json')['shots'][0]['title'], 'The door')
        self.assertEqual((self.root / manifest['audio']['path']).read_bytes(), b'ID3trackA')
        self.assertEqual((self.root / manifest['assets']['board-a']).read_bytes(), PNG)
        undo = studio.history(self.project)['autosaves'][0]['name']
        status, result = self.call('POST', f'/api/p/{self.ident}/restore', {'autosave': undo}, rev=self.rev())
        self.assertEqual(status, 200, result)
        manifest = sb.read_json(self.project)
        self.assertEqual(sb.read_json(self.root / 'board.json')['shots'][0]['title'], 'Later')
        self.assertEqual((self.root / manifest['audio']['path']).read_bytes(), b'ID3trackB')
        self.assertEqual((self.root / manifest['assets']['board-a']).read_bytes(), later_atlas)

    def test_restore_oldest_snapshot_at_retention_limit(self):
        manifest = sb.read_json(self.project)
        with patch.object(studio, 'SNAPSHOTS_KEPT', 3):
            for title in ('Oldest', 'Middle', 'Newest'):
                self.call('PUT', f'/api/p/{self.ident}/board', self.edited(title), rev=self.rev())
                studio.take_snapshot(self.project, manifest, force=True)
            oldest = studio.snapshots(self.project, manifest)[-1]
            self.assertEqual(studio.read_autosave(oldest)[0]['shots'][0]['title'], 'Oldest')
            status, result = self.call('POST', f'/api/p/{self.ident}/restore', {'autosave': oldest.name}, rev=self.rev())
            self.assertEqual(status, 200, result)
            self.assertEqual(sb.read_json(self.root / 'board.json')['shots'][0]['title'], 'Oldest')
            self.assertEqual(len(studio.snapshots(self.project, manifest)), 3)

    def test_failed_restore_preserves_current_files_and_snapshot_history(self):
        manifest = sb.read_json(self.project)
        with patch.object(studio, 'SNAPSHOTS_KEPT', 3):
            for _ in range(3):
                studio.take_snapshot(self.project, manifest, force=True)
            latest = studio.snapshots(self.project, manifest)[0]
            broken = sb.read_json(latest)
            broken['board']['shots'][0]['customImagePath'] = 'assets/missing.png'
            latest.write_text(sb.json_text(broken))
            before = {p.name: p.read_bytes() for p in studio.snapshots(self.project, manifest)}
            board_before = (self.root / 'board.json').read_bytes()
            manifest_before = self.project.read_bytes()
            rev = self.rev()
            for request in ({'autosave': latest.name}, {'version': 999}):
                status, result = self.call('POST', f'/api/p/{self.ident}/restore', request, rev=rev)
                self.assertIn(status, (400, 404), result)
                self.assertEqual((self.root / 'board.json').read_bytes(), board_before)
                self.assertEqual(self.project.read_bytes(), manifest_before)
                self.assertEqual({p.name: p.read_bytes() for p in studio.snapshots(self.project, manifest)}, before)

    def test_legacy_board_only_snapshot_keeps_current_music_and_assets(self):
        self.call('PUT', f'/api/p/{self.ident}/audio?name=current.mp3', b'ID3current', rev=self.rev())
        self.call('PUT', f'/api/p/{self.ident}/board', self.edited('Later'), rev=self.rev())
        manifest = sb.read_json(self.project)
        legacy = studio.snapshot_dir(self.project, manifest) / '2000-01-01T00-00-00.000000Z.json'
        legacy.write_text(sb.json_text(self.board))
        status, result = self.call('POST', f'/api/p/{self.ident}/restore', {'autosave': legacy.name}, rev=self.rev())
        self.assertEqual(status, 200, result)
        self.assertEqual(sb.read_json(self.root / 'board.json')['shots'][0]['title'], 'The door')
        restored = sb.read_json(self.project)
        self.assertEqual(restored['audio'], manifest['audio'])
        self.assertEqual(restored['assets'], manifest['assets'])

    def test_storyboards_on_the_drive_are_listed_without_choosing_a_file(self):
        drive = self.base / 'Rua Projects'
        job = drive / '01 Live' / 'Direct' / 'New Client' / '00 Record' / 'storyboard'
        old = drive / '01 Live' / 'Direct' / 'New Client' / '00 Record' / 'earlier' / 'copy'
        for folder in (job, old):
            folder.mkdir(parents=True)
            for name in ('board.json', 'project.json'):
                (folder / name).write_bytes((self.root / name).read_bytes())
            (folder / 'assets').mkdir()
            (folder / 'assets/frame.png').write_bytes(PNG)
        with patch.dict(os.environ, {'STORYBOARD_ROOTS': str(drive)}):
            status, home = self.call('GET', '/api/projects')
            listed = [p for p in home['projects'] if p.get('job') == 'New Client']
            self.assertEqual(len(listed), 1, 'Earlier copies are not listed')
            self.assertEqual(listed[0]['where'], 'Live · Direct')
            status, html = self.call('GET', f"/p/{listed[0]['id']}")
            self.assertEqual(status, 200, 'A listed project opens directly')

    def test_requests_from_other_sites_are_refused(self):
        status, _ = self.call('GET', f'/p/{self.ident}', host='evil.example')
        self.assertEqual(status, 403)
        conn = http.client.HTTPConnection('127.0.0.1', self.port, timeout=10)
        conn.request('PUT', f'/api/p/{self.ident}/board', body=b'{}', headers={'Content-Type': 'application/json'})
        self.assertEqual(conn.getresponse().status, 403, 'Writes need the Storyboard header')
        conn.close()
        status, _ = self.call('GET', '/p/000000000000')
        self.assertEqual(status, 404, 'Only projects on the recent list are served')


if __name__ == '__main__':
    unittest.main()
