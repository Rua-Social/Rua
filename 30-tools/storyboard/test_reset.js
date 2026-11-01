#!/usr/bin/env node
'use strict';

// Exercise the production reset control flow without a browser or media encoder.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const source = fs.readFileSync(path.join(__dirname, 'src/app.js'), 'utf8');
const start = source.indexOf('  async function restoreOriginalBoard(){');
const end = source.indexOf('  function renderPrintBoard(){', start);
assert.ok(start >= 0 && end > start, 'Production reset function must be found');
const resetSource = source.slice(start, end);

async function scenario({ fileMusic = true, backupOK = true, audioOK = true } = {}) {
  const trackA = { size: 12, track: 'browser A' };
  const trackB = { size: 12, track: 'file B' };
  const previous = { sourceRevision: 'browser-revision', shots: [{ title: 'Edited panel' }] };
  const initial = { sourceRevision: 'file-revision', shots: [{ title: 'File panel' }] };
  const button = { disabled: false };
  const events = [];
  let backup, warning = '', storedAudio = trackA;
  const context = {
    initial, state: previous, resetInProgress: false,
    tempAudioBlob: trackA, tempAudioName: 'track-a.wav',
    sequenceFilter: 'A', statusFilter: 'Approved',
    window: { confirm: () => true, STORYBOARD_AUDIO: fileMusic ? { data: 'bundled-B', name: 'track-b.wav' } : null },
    $: id => { assert.equal(id, 'reset-board'); return button; },
    clone: value => JSON.parse(JSON.stringify(value)),
    lockBackground: locked => events.push(locked ? 'lock' : 'unlock'),
    embeddedAudioBlob: data => { assert.equal(data, 'bundled-B'); return trackB; },
    exportHTML: async includeAudio => {
      assert.equal(includeAudio, true, 'Reset must back up music as well as board data');
      assert.equal(button.disabled, true, 'Block repeated resets during backup');
      events.push('backup');
      backup = { state: context.clone(context.state), track: context.tempAudioBlob };
      return backupOK;
    },
    attachAudio: async (blob, name, persist) => {
      events.push(persist ? 'persist-track' : 'restore-session-track');
      context.tempAudioBlob = blob; context.tempAudioName = name;
      if (persist && audioOK) storedAudio = blob;
      return persist ? audioOK : true;
    },
    clearAudio: async () => {
      events.push('persist-no-music'); context.tempAudioBlob = null; context.tempAudioName = '';
      if (audioOK) storedAudio = null;
      return audioOK;
    },
    releaseAudio: () => { context.tempAudioBlob = null; context.tempAudioName = ''; },
    updateAudioLabel: () => {},
    showAudioWarning: message => { warning = message; },
    renderAll: () => events.push('render'),
    scheduleSave: () => events.push('save-board'),
    toast: () => {},
  };
  vm.createContext(context);
  vm.runInContext(resetSource, context, { filename: 'production-reset.js' });
  await context.restoreOriginalBoard();
  assert.equal(context.resetInProgress, false);
  assert.equal(button.disabled, false);
  assert.equal(events.at(-1), 'unlock');
  assert.deepEqual(backup.state, previous);
  assert.equal(backup.track, trackA, 'Backup must contain the previous browser track');
  return { context, previous, initial, trackA, trackB, events, warning, storedAudio };
}

(async () => {
  for (const fileMusic of [true, false]) {
    const r = await scenario({ fileMusic });
    assert.deepEqual(r.context.state, r.initial);
    assert.equal(r.context.tempAudioBlob, fileMusic ? r.trackB : null);
    assert.equal(r.storedAudio, fileMusic ? r.trackB : null);
    assert.equal(r.context.sequenceFilter, 'all');
    assert.equal(r.context.statusFilter, 'all');
    assert.deepEqual(r.events, ['lock', 'backup', fileMusic ? 'persist-track' : 'persist-no-music', 'render', 'save-board', 'unlock']);
    assert.equal(r.warning, '');
  }
  const failedBackup = await scenario({ backupOK: false });
  assert.equal(failedBackup.context.state, failedBackup.previous);
  assert.equal(failedBackup.context.tempAudioBlob, failedBackup.trackA);
  assert.equal(failedBackup.storedAudio, failedBackup.trackA);
  assert.deepEqual(failedBackup.events, ['lock', 'backup', 'unlock']);
  for (const fileMusic of [true, false]) {
    const r = await scenario({ fileMusic, audioOK: false });
    assert.equal(r.context.state, r.previous, 'Failed audio write must retain the old board revision');
    assert.equal(r.context.tempAudioBlob, r.trackA);
    assert.equal(r.storedAudio, r.trackA);
    assert.ok(!r.events.includes('save-board'));
    assert.match(r.warning, /Restore stopped.*could not save/);
    assert.equal(r.events.at(-2), 'restore-session-track');
  }
  console.log('Reset recovery: 5 scenarios passed (track, no music, backup failure, two audio-write failures).');
})().catch(error => { console.error(error); process.exitCode = 1; });
