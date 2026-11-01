/* Local storyboard movie export workspace. No files leave this browser. */
(() => {
  'use strict';
  const clone = value => JSON.parse(JSON.stringify(value));
  const finite = (value, fallback = 0) => Number.isFinite(Number(value)) ? Number(value) : fallback;
  const bound = (value, min, max) => Math.max(min, Math.min(max, value));
  const stamp = value => {
    const n = Math.max(0, finite(value));
    return `${String(Math.floor(n / 60)).padStart(2, '0')}:${(n % 60).toFixed(1).padStart(4, '0')}`;
  };
  const fileSize = bytes => bytes >= 1e9 ? `${(bytes / 1e9).toFixed(2)} GB` : `${(bytes / 1e6).toFixed(1)} MB`;
  const round = value => Math.round(value * 100) / 100;
  const safeName = value => (String(value).replace(/[\\/:*?"<>|\u0000-\u001f]/g, '-').replace(/\.(mp4|webm)$/i, '').trim().slice(0, 120) || 'Storyboard');

  const defaultFilename = () => safeName((window.STORYBOARD_CONFIG?.exportPrefix || 'Rua')+'-Timed-Storyboard');

  window.StoryboardVideoExport = {
    init(bridge) {
      const previous = document.getElementById('video-export-dialog');
      if (previous) previous.remove();
      const dialog = document.createElement('section');
      dialog.id = 'video-export-dialog';
      dialog.className = 've-dialog';
      dialog.hidden = true;
      dialog.setAttribute('role', 'dialog');
      dialog.setAttribute('aria-modal', 'true');
      dialog.setAttribute('aria-labelledby', 've-title');
      dialog.innerHTML = `
        <div class="ve-window">
          <header class="ve-header">
            <div class="ve-header-title"><span class="ve-mark" aria-hidden="true">↗</span><div><p class="ve-eyebrow">DIRECTOR’S WORKSPACE</p><h2 id="ve-title">Export timed board</h2></div></div>
            <button class="ve-icon" id="ve-close" aria-label="Close video export">×</button>
          </header>
          <div class="ve-body">
            <div class="ve-viewer-column">
              <div class="ve-preview-head"><span>OUTPUT PREVIEW</span><span id="ve-output-badge">16:9 · 1080p · 25 fps</span></div>
              <div class="ve-canvas-wrap"><canvas id="ve-canvas" width="1280" height="720" aria-label="Video output preview"></canvas><div class="ve-preparing" id="ve-preparing" role="status"><span class="ve-spinner" aria-hidden="true"></span><span id="ve-preparing-text">Preparing your board…</span></div></div>
              <div class="ve-transport"><button id="ve-play" class="ve-play" aria-label="Play export preview" disabled>▶</button><output id="ve-time">00:00.0</output><input id="ve-scrub" aria-label="Preview position in seconds" type="range" min="0" max="90" step="0.05" value="0" disabled><span id="ve-total">01:30.0</span></div>
              <div class="ve-preview-description"><span id="ve-preview-panel">All current panels · current order</span><span>16:9 master</span></div>
              <section class="ve-music" aria-labelledby="ve-music-title">
                <div class="ve-section-top"><div><p class="ve-eyebrow">SOUNDTRACK</p><h3 id="ve-music-title">Shape the music.</h3></div><label class="ve-switch"><input id="ve-audio-enabled" type="checkbox"><span>Include in video</span></label></div>
                <div class="ve-track-row"><div class="ve-track-icon" aria-hidden="true">♫</div><div class="ve-track-info"><strong id="ve-track-name">No music attached</strong><span id="ve-track-detail">Choose a local audio file to score the timed board.</span></div><button id="ve-pick-audio" class="ve-button">Choose music</button><button id="ve-clear-audio" class="ve-icon ve-small-icon" aria-label="Remove music" hidden>×</button></div>
                <input id="ve-audio-file" type="file" accept="audio/*,.wav,.mp3,.m4a,.aac,.aif,.aiff,.ogg,.flac" hidden>
                <div id="ve-music-editor" hidden>
                  <div class="ve-waveform-wrap"><canvas id="ve-waveform" width="1000" height="100" role="img" aria-label="Audio waveform with selected source region"></canvas><div class="ve-waveform-labels"><span>0:00</span><span id="ve-source-length">—</span></div></div>
                  <div class="ve-audio-timing ve-field-grid">
                    <label>Source in <span>sec</span><input id="ve-trim-in" type="number" min="0" step="0.1" value="0" inputmode="decimal"></label>
                    <label>Source out <span>sec</span><input id="ve-trim-out" type="number" min="0" step="0.1" value="0" inputmode="decimal"></label>
                    <label>Starts in board <span>sec</span><input id="ve-audio-offset" type="number" min="0" step="0.1" value="3" inputmode="decimal"></label>
                  </div>
                  <div class="ve-board-mix" aria-label="Soundtrack placement in the board"><div class="ve-mix-track"><div id="ve-mix-region"></div></div><div><span>BOARD</span><span id="ve-mix-label">—</span></div></div>
                  <div class="ve-field-grid ve-mix-controls"><label>Level <span>dB</span><div class="ve-level-control"><input id="ve-gain" type="range" min="-60" max="0" step="1" value="0" aria-label="Music level in decibels"><output id="ve-gain-output">0 dB</output></div></label><label>Fade in <span>sec</span><input id="ve-fade-in" type="number" min="0" step="0.1" value="0" inputmode="decimal"></label><label>Fade out <span>sec</span><input id="ve-fade-out" type="number" min="0" step="0.1" value="0" inputmode="decimal"></label></div>
                  <p class="ve-help">Source in/out chooses a section of the track. “Starts in board” places it against the picture. Fades apply to the portion heard in the film.</p>
                </div>
                <p class="ve-local-note">Enabled music is included in the video. “Save complete project” also bundles the track for moving your editable board.</p>
              </section>
              <div class="ve-result" id="ve-result" hidden>
                <div><span class="ve-success-mark" aria-hidden="true">✓</span><div><strong>Video ready</strong><p id="ve-result-detail"></p></div></div>
                <div class="ve-result-actions"><button id="ve-review-result" class="ve-button">Review export</button><a id="ve-download" class="ve-button ve-primary" download>Save video ↓</a></div>
                <video id="ve-result-video" controls playsinline preload="metadata" hidden aria-label="Completed video export"></video>
              </div>
            </div>
            <aside class="ve-inspector" aria-label="Video export settings">
              <div class="ve-inspector-heading"><p class="ve-eyebrow">DELIVERY</p><h3>Video settings</h3></div>
              <fieldset id="ve-settings-fields"><legend class="sr-only">Video delivery settings</legend>
                <label class="ve-field">File name<input id="ve-filename" type="text" maxlength="120" value="Storyboard" autocomplete="off" spellcheck="false"><span class="ve-field-note" id="ve-file-extension">.mp4</span></label>
                <label class="ve-field">Format<select id="ve-format"></select></label>
                <p class="ve-help ve-format-help" id="ve-format-help"></p>
                <div class="ve-field-grid ve-video-grid"><label>Resolution<select id="ve-resolution"><option value="1920">1920 × 1080 · HD</option><option value="1280">1280 × 720 · HD</option><option value="3840">3840 × 2160 · 4K</option></select></label><label>Frame rate target<select id="ve-fps"><option value="24">24 fps</option><option value="25" selected>25 fps</option><option value="30">30 fps</option></select></label></div>
                <p class="ve-help" id="ve-upscale-note">Storyboard artwork is upscaled to your output size; export resolution does not add image detail.</p>
                <label class="ve-field">Quality<select id="ve-quality"><option value="balanced" selected>Balanced · review copy</option><option value="high">High · presentation copy</option><option value="compact">Compact · easier sharing</option><option value="custom">Custom bitrate</option></select></label>
                <div class="ve-field-grid ve-video-grid"><label>Video target <span>Mbps</span><input id="ve-bitrate" type="number" min="1" max="100" step="0.5" value="16" inputmode="decimal"></label><label>Audio target<select id="ve-audio-bitrate"><option value="128">128 kbps</option><option value="192" selected>192 kbps</option><option value="256">256 kbps</option></select></label></div>
                <div class="ve-setting-divider"></div>
                <label class="ve-field">Picture layout<select id="ve-layout"><option value="review">Review board · frame + direction</option><option value="frames">Clean frames · full picture</option></select></label>
                <label class="ve-check"><input id="ve-burnin" type="checkbox" checked><span>Show panel number and timecode</span></label>
                <p class="ve-help">On-screen titles stay in both layouts. Clean frames removes the direction notes.</p>
              </fieldset>
              <dl class="ve-delivery-summary"><div><dt>Duration</dt><dd id="ve-duration-summary">—</dd></div><div><dt>Panels</dt><dd id="ve-panel-summary">—</dd></div><div><dt>Estimated size</dt><dd id="ve-size-summary">—</dd></div><div><dt>Audio</dt><dd id="ve-audio-summary">No music</dd></div></dl>
              <p class="ve-help">Frame rate and bitrates are targets for the browser encoder; actual output can vary.</p>
              <p class="ve-render-note"><span aria-hidden="true">◷</span> Export runs at the film’s pace. Keep this tab visible until it finishes.</p>
              <div class="ve-errors" id="ve-errors" role="alert" hidden></div>
            </aside>
          </div>
          <footer class="ve-footer"><div class="ve-status-area"><div class="ve-status-line"><strong id="ve-status" role="status" aria-live="polite">Preparing export…</strong><span id="ve-status-time"></span></div><progress id="ve-progress" max="1" value="0" hidden aria-label="Video export progress"></progress><p id="ve-status-note">All current panels and their timings are included.</p></div><div class="ve-footer-actions"><button id="ve-cancel" class="ve-button" hidden>Cancel export</button><button id="ve-export" class="ve-button ve-primary" disabled>Export video <span aria-hidden="true">↗</span></button></div></footer>
        </div>`;
      document.body.append(dialog);
      const $ = id => dialog.querySelector(`#${id}`);
      dialog.querySelector('.ve-header .ve-eyebrow').textContent = String(window.STORYBOARD_CONFIG?.brand || 'Rua').toUpperCase()+' · DIRECTOR’S WORKSPACE';
      const engine = window.StoryboardVideoEngine;
      let project = null, board = null, audioFile = null, formats = [], settings = null;
      let preparing = false, encoding = false, open = false, prepareToken = 0, fatalError = '';
      let controller = null, cancelReason = '', resultURL = '', audioURL = '', previewAudio = null;
      let playTime = 0, playing = false, playOrigin = 0, playFrame = 0, lastFocus = null, rafAudioError = false;
      const inputIDs = ['ve-format', 've-resolution', 've-fps', 've-bitrate', 've-audio-bitrate', 've-layout', 've-burnin', 've-audio-enabled', 've-trim-in', 've-trim-out', 've-audio-offset', 've-gain', 've-fade-in', 've-fade-out', 've-filename'];

      function defaults(saved) {
        const value = saved || {};
        const width = [1280, 1920, 3840].includes(Number(value.width)) ? Number(value.width) : 1920;
        return {
          width, height: width * 9 / 16, fps: [24, 25, 30].includes(Number(value.fps)) ? Number(value.fps) : 25,
          videoMbps: bound(finite(value.videoMbps, 16), 1, 100), audioKbps: [128, 192, 256].includes(Number(value.audioKbps)) ? Number(value.audioKbps) : 192,
          formatId: formats.some(f => f.id === value.formatId) ? value.formatId : (formats[0]?.id || ''),
          layout: value.layout === 'frames' ? 'frames' : 'review', burnIn: value.burnIn !== false,
          filename: safeName(value.filename || defaultFilename()), quality: ['balanced', 'high', 'compact', 'custom'].includes(value.quality) ? value.quality : 'balanced',
          audio: { enabled: value.audio?.enabled !== false, trimIn: Math.max(0, finite(value.audio?.trimIn)), trimOut: value.audio?.trimOut == null ? null : Math.max(0, finite(value.audio.trimOut)), offset: Math.max(0, finite(value.audio?.offset, finite(board?.audioStartSeconds, 3))), gainDb: bound(finite(value.audio?.gainDb), -60, 0), fadeIn: Math.max(0, finite(value.audio?.fadeIn)), fadeOut: Math.max(0, finite(value.audio?.fadeOut)) }
        };
      }

      function setFields(value) {
        const values = { 've-format': value.formatId, 've-resolution': value.width, 've-fps': value.fps, 've-bitrate': value.videoMbps, 've-audio-bitrate': value.audioKbps, 've-layout': value.layout, 've-filename': value.filename, 've-quality': value.quality, 've-trim-in': value.audio.trimIn, 've-trim-out': value.audio.trimOut == null ? (project ? round(project.audioDuration) : 0) : value.audio.trimOut, 've-audio-offset': value.audio.offset, 've-gain': value.audio.gainDb, 've-fade-in': value.audio.fadeIn, 've-fade-out': value.audio.fadeOut };
        for (const [id, val] of Object.entries(values)) $(id).value = val;
        $('ve-burnin').checked = value.burnIn;
        $('ve-audio-enabled').checked = value.audio.enabled && !!audioFile;
      }

      function readFields() {
        const num = id => $(id).value === '' ? NaN : Number($(id).value);
        const width = num('ve-resolution');
        return { width, height: width * 9 / 16, fps: num('ve-fps'), videoMbps: num('ve-bitrate'), audioKbps: num('ve-audio-bitrate'), formatId: $('ve-format').value, layout: $('ve-layout').value, burnIn: $('ve-burnin').checked, filename: $('ve-filename').value, quality: $('ve-quality').value,
          audio: { enabled: $('ve-audio-enabled').checked && !!audioFile, trimIn: num('ve-trim-in'), trimOut: num('ve-trim-out'), offset: num('ve-audio-offset'), gainDb: num('ve-gain'), fadeIn: num('ve-fade-in'), fadeOut: num('ve-fade-out') } };
      }

      function audibleSpan(value) {
        if (!project || !value.audio.enabled) return 0;
        return Math.max(0, Math.min(value.audio.trimOut - value.audio.trimIn, project.duration - value.audio.offset));
      }

      function validation(value) {
        const errors = [];
        if (fatalError) errors.push(fatalError);
        if (!formats.length) errors.push('This browser cannot record a supported video format. Open the board in an up-to-date desktop browser to export.');
        if (!project || preparing) return errors;
        if (!formats.some(f => f.id === value.formatId)) errors.push('Choose an available video format.');
        if (!value.filename.trim()) errors.push('Enter a file name.');
        if (!Number.isFinite(value.videoMbps) || value.videoMbps < 1 || value.videoMbps > 100) errors.push('Video bitrate must be between 1 and 100 Mbps.');
        if (value.audio.enabled) {
          const a = value.audio;
          if (!Number.isFinite(a.trimIn) || a.trimIn < 0 || a.trimIn >= project.audioDuration) errors.push('Source in must be within the audio file.');
          if (!Number.isFinite(a.trimOut) || a.trimOut <= a.trimIn || a.trimOut > project.audioDuration + 0.03) errors.push('Source out must follow source in and stay within the audio file.');
          if (!Number.isFinite(a.offset) || a.offset < 0 || a.offset >= project.duration) errors.push('Music must start between 0 and the end of the board.');
          const span = audibleSpan(value);
          if (!Number.isFinite(a.fadeIn) || !Number.isFinite(a.fadeOut) || a.fadeIn < 0 || a.fadeOut < 0) errors.push('Fade durations must be zero or greater.');
          else if (a.fadeIn + a.fadeOut > span + 0.01) errors.push(`Combined fades cannot exceed the ${stamp(span)} of music heard in the board.`);
        }
        return errors;
      }

      function setStatus(main, note = '', timing = '') {
        $('ve-status').textContent = main;
        $('ve-status-note').textContent = note;
        $('ve-status-time').textContent = timing;
      }

      function refresh(persist = true) {
        settings = readFields();
        const errors = validation(settings);
        const format = formats.find(f => f.id === settings.formatId);
        $('ve-errors').hidden = !errors.length;
        $('ve-errors').replaceChildren(...errors.map(message => { const p = document.createElement('p'); p.textContent = message; return p; }));
        $('ve-export').disabled = !project || preparing || encoding || !!errors.length;
        $('ve-play').disabled = !project || preparing || encoding || !!errors.length;
        $('ve-scrub').disabled = !project || preparing || encoding;
        $('ve-audio-enabled').disabled = !audioFile || preparing || encoding;
        $('ve-audio-bitrate').disabled = !settings.audio.enabled || encoding;
        $('ve-gain-output').textContent = `${settings.audio.gainDb} dB`;
        $('ve-file-extension').textContent = format ? `.${format.extension}` : '';
        $('ve-output-badge').textContent = `16:9 · ${settings.height}p · ${settings.fps} fps`;
        $('ve-format-help').textContent = format?.extension === 'mp4' ? 'MP4 is available in this browser. Encoding uses the browser’s supported H.264 / audio combination.' : formats.length ? (formats.some(f=>f.extension==='mp4') ? 'WebM uses VP8 or VP9 video with Opus audio. Choose MP4 above for an H.264 / AAC delivery.' : 'WebM is the available browser format. For an MP4 delivery, open this board in a browser that offers MP4 export.') : '';
        $('ve-upscale-note').textContent = settings.width === 3840 ? '4K output · upscaled artwork. Output resolution adds pixels but cannot add detail to the supplied artwork.' : 'Storyboard artwork is upscaled to your output size; export resolution does not add image detail.';
        $('ve-duration-summary').textContent = project ? stamp(project.duration) : '—';
        $('ve-panel-summary').textContent = board ? `${board.shots.length} · current order` : '—';
        $('ve-size-summary').textContent = project && Number.isFinite(settings.videoMbps) ? `≈ ${fileSize(project.duration * (settings.videoMbps * 1e6 + (settings.audio.enabled ? settings.audioKbps * 1e3 : 0)) / 8)}` : '—';
        $('ve-audio-summary').textContent = settings.audio.enabled ? `${stamp(audibleSpan(settings))} · ${settings.audioKbps} kbps target` : 'No music';
        $('ve-music-editor').classList.toggle('ve-muted', !settings.audio.enabled);
        if (!preparing && !encoding) setStatus(errors.length ? 'Check the highlighted settings' : 'Ready to export', project ? `All ${board.shots.length} panels · ${stamp(project.duration)} · ${format?.label || 'choose a format'}` : '');
        if (persist && resultURL) $('ve-status-note').textContent='Settings changed. Export again to apply them; Save video still downloads the previous render.';
        if (project) {
          $('ve-scrub').max = project.duration;
          $('ve-total').textContent = stamp(project.duration);
          drawWaveform();
          const a = settings.audio, span = audibleSpan(settings);
          $('ve-mix-region').style.left = `${bound(finite(a.offset / project.duration * 100), 0, 100)}%`;
          $('ve-mix-region').style.width = `${bound(finite(span / project.duration * 100), 0, 100)}%`;
          $('ve-mix-region').style.opacity = settings.audio.enabled ? 1 : 0.3;
          $('ve-mix-label').textContent = settings.audio.enabled ? `${stamp(a.offset)} → ${stamp(a.offset + span)} · ${stamp(span)} heard` : 'Soundtrack excluded';
          if (persist && !errors.length) bridge.saveSettings?.(clone(settings));
          drawPreview();
        }
      }

      function drawWaveform() {
        if (!project) return;
        const canvas = $('ve-waveform'), ctx = canvas.getContext('2d'), peaks = project.waveform || [];
        const w = canvas.width, h = canvas.height, duration = project.audioDuration || 1;
        const start = bound(finite(settings.audio.trimIn / duration), 0, 1), end = bound(finite(settings.audio.trimOut / duration), 0, 1);
        ctx.clearRect(0, 0, w, h);
        ctx.fillStyle = '#1c2220'; ctx.fillRect(0, 0, w, h);
        ctx.fillStyle = settings.audio.enabled ? '#b5aa7b22' : '#ffffff06'; ctx.fillRect(start * w, 0, (end - start) * w, h);
        const gap = w / Math.max(1, peaks.length);
        peaks.forEach((peak, i) => {
          const x = i / peaks.length, height = Math.max(2, finite(peak) * (h - 20));
          ctx.fillStyle = x >= start && x <= end && settings.audio.enabled ? '#c5b685' : '#59615c';
          ctx.fillRect(i * gap, (h - height) / 2, Math.max(1, gap - 1.5), height);
        });
        ctx.fillStyle = '#e9ddb8';
        for (const x of [start, end]) { ctx.fillRect(x * (w - 2), 0, 2, h); ctx.fillRect(Math.min(w - 8, x * w - 3), 0, 8, 8); }
        if (playing && settings.audio.enabled) {
          const sourceTime = playTime - settings.audio.offset + settings.audio.trimIn;
          if (sourceTime >= settings.audio.trimIn && sourceTime <= settings.audio.trimOut) { ctx.fillStyle = '#fff'; ctx.fillRect(sourceTime / duration * w, 0, 2, h); }
        }
        canvas.setAttribute('aria-label', `Source waveform. Selected ${stamp(settings.audio.trimIn)} to ${stamp(settings.audio.trimOut)} of ${stamp(project.audioDuration)}.`);
      }

      function drawPreview() {
        if (!project || !settings) return;
        try { project.draw($('ve-canvas'), Math.min(playTime, Math.max(0, project.duration - 0.001)), settings); }
        catch (error) { fatalError = `The preview could not be drawn: ${error.message || 'unknown error'}`; }
        $('ve-time').textContent = stamp(playTime);
        $('ve-scrub').value = playTime;
        let cursor = 0, index = board.shots.length - 1;
        for (let i = 0; i < board.shots.length; i++) { cursor += finite(board.shots[i].duration, 3); if (playTime < cursor) { index = i; break; } }
        const shot = board.shots[index];
        $('ve-preview-panel').textContent = shot ? `${shot.id || index + 1} · ${shot.title || 'Untitled panel'}` : 'Current board';
      }

      function stopPreview() {
        playing = false;
        cancelAnimationFrame(playFrame);
        previewAudio?.pause();
        $('ve-play').textContent = '▶';
        $('ve-play').setAttribute('aria-label', 'Play export preview');
      }

      function audioAt(time, seek = false) {
        if (!previewAudio || !project || !settings) return;
        const a = settings.audio, elapsed = time - a.offset, span = audibleSpan(settings);
        if (!a.enabled || elapsed < 0 || elapsed >= span) { previewAudio.pause(); return; }
        const sourceTime = a.trimIn + elapsed;
        if (seek || Math.abs(previewAudio.currentTime - sourceTime) > 0.3) previewAudio.currentTime = sourceTime;
        let envelope = 1;
        if (a.fadeIn > 0) envelope = Math.min(envelope, elapsed / a.fadeIn);
        if (a.fadeOut > 0) envelope = Math.min(envelope, (span - elapsed) / a.fadeOut);
        previewAudio.volume = bound(Math.pow(10, a.gainDb / 20) * envelope, 0, 1);
        if (playing && previewAudio.paused) previewAudio.play().catch(error => {
          if (!playing || rafAudioError) return;
          rafAudioError = true; stopPreview();
          setStatus('Music preview could not play', error.message || 'Choose the track again or check the audio file.');
        });
      }

      function previewTick() {
        if (!playing || !project) return;
        playTime = Math.min(project.duration, (performance.now() - playOrigin) / 1000);
        drawPreview(); audioAt(playTime); drawWaveform();
        if (playTime >= project.duration) { stopPreview(); return; }
        playFrame = requestAnimationFrame(previewTick);
      }

      function playPreview() {
        if (playing) { stopPreview(); return; }
        if (!project || encoding || preparing || validation(readFields()).length) return;
        $('ve-result-video').pause();
        if (playTime >= project.duration - 0.02) playTime = 0;
        playing = true; rafAudioError = false; playOrigin = performance.now() - playTime * 1000;
        $('ve-play').textContent = 'Ⅱ'; $('ve-play').setAttribute('aria-label', 'Pause export preview');
        audioAt(playTime, true); previewTick();
      }

      function releaseAudio() {
        previewAudio?.pause();
        if (previewAudio) { previewAudio.removeAttribute('src'); previewAudio.load(); }
        previewAudio = null;
        if (audioURL) URL.revokeObjectURL(audioURL);
        audioURL = '';
      }

      function showTrack() {
        $('ve-track-name').textContent = audioFile?.name || 'No music attached';
        $('ve-track-name').title = audioFile?.name || '';
        $('ve-track-detail').textContent = audioFile ? `${project ? `${stamp(project.audioDuration)} · ` : ''}${fileSize(audioFile.blob.size)} · local audio` : 'Choose a local audio file to score the timed board.';
        $('ve-pick-audio').textContent = audioFile ? 'Replace music' : 'Choose music';
        $('ve-clear-audio').hidden = !audioFile;
        $('ve-music-editor').hidden = !audioFile;
        $('ve-source-length').textContent = project ? stamp(project.audioDuration) : '—';
        $('ve-trim-in').max = $('ve-trim-out').max = project?.audioDuration || 0;
        $('ve-audio-offset').max = project?.duration || 0;
      }

      function updateBusy() {
        $('ve-close').disabled = encoding;
        $('ve-pick-audio').disabled = encoding || preparing;
        $('ve-clear-audio').disabled = encoding || preparing;
        $('ve-settings-fields').disabled = encoding;
        for (const input of dialog.querySelectorAll('.ve-music input')) input.disabled = encoding || preparing;
        $('ve-cancel').hidden = !encoding;
        $('ve-progress').hidden = !encoding;
        $('ve-preparing').hidden = !preparing;
        $('ve-export').innerHTML = encoding ? 'Exporting…' : 'Export video <span aria-hidden="true">↗</span>';
        dialog.setAttribute('aria-busy', preparing || encoding ? 'true' : 'false');
      }

      async function prepare(resetTrim = false) {
        const token = ++prepareToken;
        stopPreview(); releaseAudio();
        project?.dispose(); project = null;
        preparing = true; fatalError = '';
        const pendingSettings=clone(settings);
        updateBusy(); showTrack(); refresh(false);settings=pendingSettings;
        setStatus('Preparing export…', audioFile ? 'Loading the frames and reading your soundtrack.' : 'Loading the current storyboard frames.');
        try {
          if (!engine) throw new Error('The video export engine is missing. Open the complete updated HTML file.');
          const next = await engine.prepare(clone(board), bridge.assets, audioFile?.blob || null);
          if (token !== prepareToken || !open) { next.dispose(); return; }
          project = next;
          if (audioFile) {
            audioURL = URL.createObjectURL(audioFile.blob);
            previewAudio = new Audio(audioURL); previewAudio.preload = 'auto';
            if (resetTrim) { settings.audio.trimIn = 0; settings.audio.trimOut = round(project.audioDuration); settings.audio.fadeIn = 0; settings.audio.fadeOut = 0; settings.audio.enabled = true; }
            else if (settings.audio.trimOut == null || settings.audio.trimOut === 0) settings.audio.trimOut = round(project.audioDuration);
          }
          playTime = Math.min(playTime, project.duration);
          setFields(settings);
        } catch (error) {
          if (token !== prepareToken || !open) return;
          fatalError = error.message || 'The board could not be prepared for export.';
        } finally {
          if (token === prepareToken && open) { preparing = false; updateBusy(); showTrack(); refresh(); }
        }
      }

      function applyQuality() {
        const quality = $('ve-quality').value;
        if (quality === 'custom') return;
        const values = { 1280: { compact: 4, balanced: 8, high: 12 }, 1920: { compact: 8, balanced: 16, high: 28 }, 3840: { compact: 24, balanced: 45, high: 65 } };
        $('ve-bitrate').value = values[$('ve-resolution').value][quality];
        $('ve-audio-bitrate').value = quality === 'compact' ? 128 : quality === 'high' ? 256 : 192;
      }

      function cancelExport(reason = '') {
        if (!encoding || !controller) return;
        cancelReason = reason;
        controller.abort();
        $('ve-cancel').disabled = true;
        setStatus('Stopping export…', 'The unfinished recording will be discarded.');
      }

      async function exportVideo() {
        refresh();
        if (!project || encoding || preparing || validation(settings).length) return;
        stopPreview(); $('ve-result-video').pause();
        settings.filename = safeName(settings.filename); $('ve-filename').value = settings.filename;
        bridge.saveSettings?.(clone(settings));
        encoding = true; cancelReason = ''; controller = new AbortController();
        $('ve-cancel').disabled = false; $('ve-result').hidden = true;
        $('ve-result-video').hidden = true; $('ve-result-video').removeAttribute('src');
        if (resultURL) { URL.revokeObjectURL(resultURL); resultURL = ''; }
        updateBusy(); refresh(false); $('ve-progress').value = 0;
        $('ve-cancel').focus();
        setStatus('Exporting video…', 'Keep this tab visible. You can cancel at any time.', `00:00 / ${stamp(project.duration)}`);
        try {
          const result = await project.export(clone(settings), {
            signal: controller.signal,
            onProgress(value) {
              $('ve-progress').value = bound(finite(value.progress), 0, 1);
              playTime = Math.min(project.duration, finite(value.elapsed)); drawPreview();
              setStatus(`Exporting video · ${Math.round(bound(finite(value.progress), 0, 1) * 100)}%`, value.message || 'Keep this tab visible until the export finishes.', `${stamp(value.elapsed)} / ${stamp(project.duration)}`);
            }
          });
          if (controller.signal.aborted) throw new DOMException('Export cancelled', 'AbortError');
          resultURL = URL.createObjectURL(result.blob);
          $('ve-download').href = resultURL;
          $('ve-download').download = `${settings.filename}.${result.extension}`;
          $('ve-result-video').src = resultURL;
          $('ve-result-detail').textContent = `${result.extension.toUpperCase()} · ${settings.width} × ${settings.height} · ${settings.fps} fps · ${fileSize(result.blob.size)}`;
          $('ve-result').hidden = false;
          encoding = false; updateBusy(); refresh(false);
          setStatus('Your video is ready', 'Save the file, or review the exported picture and soundtrack first.');
          $('ve-download').focus();
          bridge.toast?.('Video ready — choose Save video to download.');
        } catch (error) {
          encoding = false; updateBusy(); refresh(false);
          if (controller.signal.aborted || error.name === 'AbortError') setStatus('Export cancelled', cancelReason || 'No partial video was saved. Your settings are still here.');
          else setStatus('Export could not finish', error.message || 'Try a lower resolution or another available format.');
          $('ve-export').focus();
        } finally { controller = null; }
      }

      async function changeMusic(file) {
        if (!file || encoding || preparing) return;
        stopPreview();
        try {
          await bridge.setAudio(file, file.name);
          audioFile = { blob: file, name: file.name };
          settings = readFields(); settings.audio.enabled = true;
          await prepare(true);
        } catch (error) { setStatus('Music could not be attached', error.message || 'Choose a supported audio file.'); }
      }

      async function clearMusic() {
        if (encoding || preparing) return;
        stopPreview();
        try {
          await bridge.clearAudio(); audioFile = null; settings = readFields(); settings.audio.enabled = false;
          await prepare();
        } catch (error) { setStatus('Music could not be removed', error.message || 'Try again.'); }
      }

      async function openDialog() {
        if (open) return;
        lastFocus = document.activeElement; bridge.pausePresentation?.();
        board = clone(bridge.getBoard()); audioFile = bridge.getAudio();
        formats = engine?.getFormats() || [];
        $('ve-format').replaceChildren(...formats.map(format => { const option = document.createElement('option'); option.value = format.id; option.textContent = format.label; return option; }));
        settings = defaults(bridge.getSettings?.());
        setFields(settings); playTime = 0; fatalError = '';
        open = true; dialog.hidden = false;dialog.querySelector('.ve-body').scrollTop=0;
        bridge.onOpen?.();
        $('ve-close').focus();
        await prepare();
      }

      function closeDialog() {
        if (!open || encoding) return;
        stopPreview(); $('ve-result-video').pause(); releaseAudio();
        prepareToken++; project?.dispose(); project = null; preparing = false;
        open = false; dialog.hidden = true; bridge.onClose?.();
        if (lastFocus?.isConnected && !lastFocus.closest('[hidden]')) lastFocus.focus();
      }

      $('ve-close').addEventListener('click', closeDialog);
      $('ve-play').addEventListener('click', playPreview);
      $('ve-export').addEventListener('click', exportVideo);
      $('ve-cancel').addEventListener('click', () => cancelExport());
      $('ve-pick-audio').addEventListener('click', () => $('ve-audio-file').click());
      $('ve-audio-file').addEventListener('change', event => { const file = event.target.files[0]; event.target.value = ''; changeMusic(file); });
      $('ve-clear-audio').addEventListener('click', clearMusic);
      $('ve-review-result').addEventListener('click', () => { stopPreview(); $('ve-result-video').hidden = !$('ve-result-video').hidden; $('ve-review-result').textContent = $('ve-result-video').hidden ? 'Review export' : 'Hide review'; if ($('ve-result-video').hidden) $('ve-result-video').pause(); });
      $('ve-result-video').addEventListener('play', stopPreview);
      $('ve-scrub').addEventListener('input', () => { playTime = Number($('ve-scrub').value); playOrigin = performance.now() - playTime * 1000; drawPreview(); audioAt(playTime, true); drawWaveform(); });
      $('ve-quality').addEventListener('change', () => { stopPreview(); applyQuality(); refresh(); });
      for (const id of inputIDs) $(id).addEventListener('input', () => {
        stopPreview();
        if (id === 've-bitrate') $('ve-quality').value = 'custom';
        if (id === 've-resolution') applyQuality();
        refresh();
      });
      $('ve-filename').addEventListener('change', () => { if ($('ve-filename').value.trim()) $('ve-filename').value = safeName($('ve-filename').value); refresh(); });
      document.addEventListener('keydown', event => {
        if (!open) return;
        if (event.key === 'Escape') { event.preventDefault(); event.stopImmediatePropagation(); if (encoding) cancelExport(); else closeDialog(); return; }
        if (event.key === 'Tab') {
          const focusable = [...dialog.querySelectorAll('button:not(:disabled),a[href],input:not(:disabled),select:not(:disabled),video[controls]')].filter(element => !element.closest('[hidden]') && element.getClientRects().length);
          const first = focusable[0], last = focusable[focusable.length - 1];
          if (event.shiftKey && (document.activeElement === first || !dialog.contains(document.activeElement))) { event.preventDefault(); last?.focus(); }
          else if (!event.shiftKey && (document.activeElement === last || !dialog.contains(document.activeElement))) { event.preventDefault(); first?.focus(); }
        }
        const editing = /INPUT|SELECT|TEXTAREA|BUTTON|A|VIDEO/.test(event.target.tagName);
        if (event.code === 'Space' && !editing) { event.preventDefault(); event.stopPropagation(); playPreview(); }
      }, true);
      document.addEventListener('visibilitychange', () => { if (document.hidden && open) { stopPreview(); if (encoding) cancelExport('The tab became hidden, so the export stopped to avoid missing frames. Keep this tab visible and export again.'); } });
      window.addEventListener('beforeunload', () => { if (resultURL) URL.revokeObjectURL(resultURL); releaseAudio(); });
      return { open: openDialog, close: closeDialog };
    }
  };
})();
