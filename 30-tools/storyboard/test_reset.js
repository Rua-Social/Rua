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

function sliceFunction(startMarker, endMarker) {
  const from = source.indexOf(startMarker), to = source.indexOf(endMarker, from);
  assert.ok(from >= 0 && to > from, `Production code must contain ${startMarker}`);
  return source.slice(from, to);
}

function startupAndCleanupRules() {
  const context = { STORAGE_KEY: 'film', initial: { title: 'Home Away From Home' } };
  vm.createContext(context);
  vm.runInContext("const KEPT_PREFIX=STORAGE_KEY+':kept:';" + sliceFunction('  function startupChoice(', '  async function keepCopy(') + sliceFunction('  function isOldCopy(', '  async function clearOldCopies(') + ';this.startupChoice=startupChoice;this.isOldCopy=isOldCopy;', context);
  const { startupChoice, isOldCopy } = context;
  const same = { sourceRevision: 'r2', edited: true };
  assert.deepEqual({ ...startupChoice(null, 'r2') }, { load: null, keep: false });
  assert.equal(startupChoice(same, 'r2').load, same, 'Edits on this file version reopen');
  const edited = startupChoice({ sourceRevision: 'r1', edited: true }, 'r2');
  assert.equal(edited.load, null, 'A rebuilt file opens on its own board');
  assert.equal(edited.keep, true, 'Earlier edits are kept aside, not lost');
  assert.equal(startupChoice({ sourceRevision: 'r1', edited: false }, 'r2').keep, false, 'An untouched old copy is not kept');
  assert.equal(startupChoice({ sourceRevision: 'r1' }, 'r2').keep, true, 'Saves from before edit tracking count as edited');
  assert.equal(startupChoice({ sourceRevision: 'r1' }, '').load.sourceRevision, 'r1', 'Unbuilt pages keep the old behaviour');
  assert.equal(isOldCopy('film', { title: 'Home Away From Home' }), false, "This file's own save is never cleared");
  assert.equal(isOldCopy('film:kept:r1', { title: 'Anything' }), true);
  assert.equal(isOldCopy('film-oct21', { title: 'Home Away From Home' }), true);
  assert.equal(isOldCopy('other-film', { title: 'Another film' }), false, "Another project's save is left alone");
  assert.equal(isOldCopy('film-oct21:audio', null), false);
  assert.equal(isOldCopy('film:kept:r1:1730000000000-abc123', { title: 'Anything' }), true, 'Every kept copy of this file is cleared');
  assert.equal(isOldCopy('home-away-shared-1730000000000-abc123', { title: 'Home Away From Home' }), false, 'A complete-project file keeps its own live save');
  assert.equal(isOldCopy('other-film:kept:r1:1730000000000-abc123', { title: 'Home Away From Home' }), false, "Another file's kept edits are left alone");
}

// Kept copies never overwrite each other, and opening one makes it this page's save with its soundtrack.
async function keptCopyFlow() {
  const store = new Map();
  const audioEvents = [];
  const el = () => ({ hidden: true, textContent: '' });
  const nodes = { 'kept-notice': el(), 'kept-text': el() };
  const context = {
    STORAGE_KEY: 'film', initial: { title: 'Film', sourceRevision: 'r2', shots: [{ title: 'File panel' }] },
    state: null, sequenceFilter: 'A', statusFilter: 'B', Date, Math, JSON,
    dbGet: async key => store.has(key) ? JSON.parse(JSON.stringify(store.get(key))) : null,
    dbPut: async (value, key) => { store.set(key, value); return true; },
    dbDelete: async key => { store.delete(key); return true; },
    dbKeys: async () => [...store.keys()],
    dbWrite: async value => { store.set('film', value); return true; },
    validateImport: value => JSON.parse(JSON.stringify(value)),
    localStorage: { setItem: () => {} },
    $: id => nodes[id],
    renderAll: () => {}, toast: () => {},
    scheduleSave: () => { context.state.edited = true; store.set('film', context.state); },
    attachAudio: async (blob, name) => { audioEvents.push(name); store.set('film:audio', { blob, name }); return true; },
    clearAudio: async () => { audioEvents.push('cleared'); return true; },
  };
  vm.createContext(context);
  vm.runInContext("const KEPT_PREFIX=STORAGE_KEY+':kept:';" + sliceFunction('  async function keepCopy(', '  async function downloadKeptCopies(') + ';this.keepCopy=keepCopy;this.keptCopies=keptCopies;this.openKeptCopy=openKeptCopy;', context);

  store.set('film:audio', { blob: { size: 3 }, name: 'track-a.wav' });
  await context.keepCopy({ sourceRevision: 'r1', edited: true, shots: [{ title: 'Edits A' }] });
  await new Promise(resolve => setTimeout(resolve, 2));
  store.set('film:audio', { blob: { size: 3 }, name: 'track-b.wav' });
  await context.keepCopy({ sourceRevision: 'r1', edited: true, shots: [{ title: 'Edits B' }] });
  const kept = await context.keptCopies();
  assert.equal(kept.length, 2, 'A second set of edits on the same version keeps the first');
  assert.equal(kept[0].value.shots[0].title, 'Edits B', 'Newest kept copy first');

  context.state = { ...context.initial, edited: true, shots: [{ title: 'Edits made on this page' }] };
  await context.openKeptCopy();
  assert.equal(context.state.shots[0].title, 'Edits B');
  assert.equal(store.get('film').sourceRevision, 'r2', "Opened edits become this file's save, so a reload keeps them");
  assert.deepEqual(audioEvents, ['track-b.wav'], 'The kept soundtrack comes back with the edits');
  const after = await context.keptCopies();
  assert.equal(after.length, 2, 'The opened copy leaves the list; the edits it replaced are kept aside');
  assert.ok(after.some(c => c.value.shots[0].title === 'Edits made on this page'));
  assert.ok(after.some(c => c.value.shots[0].title === 'Edits A'));
  assert.equal(nodes['kept-notice'].hidden, false);
}

(async () => {
  startupAndCleanupRules();
  await keptCopyFlow();
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
  console.log('Reset recovery: 5 scenarios passed (track, no music, backup failure, two audio-write failures). Startup and cleanup rules passed.');
})().catch(error => { console.error(error); process.exitCode = 1; });
