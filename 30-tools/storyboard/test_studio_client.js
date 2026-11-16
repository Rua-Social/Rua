#!/usr/bin/env node
'use strict';

// Exercise save/restore races using the production client and controlled requests.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, 'src/app.js'), 'utf8');
function section(from, to) {
  const start = source.indexOf(from), end = source.indexOf(to, start);
  assert.ok(start >= 0 && end > start);
  return source.slice(start, end);
}
const production = section('  function studioRequest(', '  async function renderStudioVersions(')
  + section('  function persistAudio(', '  async function attachAudio(');
const response = (data = {}, status = 200) => ({ ok: status < 400, status, json: async () => data });
function deferred() {
  let resolve;
  const promise = new Promise(done => { resolve = done; });
  return { promise, resolve };
}
const tick = () => new Promise(setImmediate);
function scenario(handle) {
  const requests = [], messages = [], nodes = {};
  const context = {
    STUDIO: { api: '/api/project' }, studioRev: 'r1', studioQueue: Promise.resolve(),
    studioDirty: false, studioBlocked: false, studioSaveFailed: false,
    studioTransition: false, pendingEdits: 0, activeModal: null,
    studioAudioDirty: false, studioAudioPending: 0, studioAudioRevision: 0,
    audioSaveChain: Promise.resolve(true), saveRevision: 0, saveTimer: null,
    state: { title: 'Current edits' }, clearTimeout,
    window: { prompt: () => 'First version', confirm: () => true },
    document: { body: { inert: false, setAttribute: () => {} } },
    location: { reload: () => { context.reloaded = true; } },
    $: id => nodes[id] || (nodes[id] = {}),
    toast: message => messages.push(message),
    showStorageWarning: message => messages.push(message),
    showAudioWarning: message => messages.push(message),
    setSaveLabel: label => { context.label = label; },
    renderStudioVersions: async () => {},
    fetch: async (url, options) => {
      const request = { url, ...options };
      requests.push(request);
      return handle ? handle(request) : response({ rev: 'r2', report: 'version saved' });
    },
  };
  vm.createContext(context);
  vm.runInContext(production, context);
  return { context, requests, messages };
}

(async () => {
  // Once Restore starts, no second transition or asynchronous edit can overwrite it.
  const restoring = deferred();
  const restore = scenario(request => request.url.endsWith('/restore')
    ? restoring.promise : response({ rev: 'r2' }));
  restore.context.studioDirty = true;
  const operation = restore.context.studioRestore({ version: 1 }, 'version one');
  await tick();
  assert.equal(restore.context.document.body.inert, true);
  assert.deepEqual(restore.requests.map(r => r.method), ['PUT', 'POST']);
  await restore.context.studioRestore({ version: 2 }, 'version two');
  await restore.context.studioSaveVersion();
  let lateEdit = false;
  await restore.context.pendingEdit(async () => { lateEdit = true; })();
  assert.equal(lateEdit, false);
  assert.equal(restore.requests.length, 2);
  restoring.resolve(response({ rev: 'r3' }));
  await operation;
  assert.equal(restore.context.reloaded, true);
  assert.equal(restore.context.studioDirty, false);
  assert.equal(restore.context.document.body.inert, true, 'Keep editing locked until reload');

  // A file decode already in flight must finish before a transition may start.
  const importing = deferred(), busy = scenario();
  const edit = busy.context.pendingEdit(() => importing.promise)();
  await busy.context.studioRestore({ version: 1 }, 'version one');
  await busy.context.studioSaveVersion();
  assert.equal(busy.requests.length, 0);
  importing.resolve();
  await edit;
  await busy.context.studioSaveVersion();
  assert.equal(busy.requests.length, 1);
  assert.equal(busy.context.document.body.inert, false);

  // Export preparation can still be settling trim settings after audio was saved.
  const exporting = scenario();
  exporting.context.activeModal = 'export';
  await exporting.context.studioSaveVersion();
  await exporting.context.studioRestore({ version: 1 }, 'version one');
  assert.equal(exporting.requests.length, 0);

  // A failed soundtrack write must block both operations, retaining the session track.
  const audio = scenario(request => request.url.includes('/audio')
    ? response({ error: 'Unsupported audio type' }, 400) : response({ rev: 'r2' }));
  assert.equal(await audio.context.persistAudio({ blob: {}, name: 'track.aiff' }), false);
  await audio.context.studioSaveVersion();
  await audio.context.studioRestore({ version: 1 }, 'version one');
  assert.equal(audio.requests.length, 1);
  assert.equal(audio.context.studioAudioDirty, true);
  assert.equal(audio.context.label, 'Music not saved');
  assert.equal(audio.context.document.body.inert, false);
  assert.ok(audio.messages.some(message => /music change has not saved/.test(message)));
  assert.ok(!audio.context.reloaded);

  // Wait for an outstanding soundtrack request before building a version.
  const writingAudio = deferred();
  const waiting = scenario(request => request.url.includes('/audio')
    ? writingAudio.promise : response({ rev: 'r3', report: 'version saved' }));
  const savingTrack = waiting.context.persistAudio({ blob: {}, name: 'track.wav' });
  const savingVersion = waiting.context.studioSaveVersion();
  await tick();
  assert.equal(waiting.requests.length, 1);
  writingAudio.resolve(response({ rev: 'r2' }));
  await Promise.all([savingTrack, savingVersion]);
  assert.equal(waiting.requests.length, 2);
  assert.equal(waiting.requests[1].headers['X-Storyboard-Rev'], 'r2');
  assert.equal(waiting.context.studioAudioDirty, false);

  // Failures unlock the page and keep the unsaved status visible.
  const failed = scenario(() => response({ error: 'Drive unavailable' }, 500));
  failed.context.studioDirty = true;
  await failed.context.studioRestore({ version: 1 }, 'version one');
  assert.equal(failed.context.document.body.inert, false);
  assert.equal(failed.context.studioDirty, true);
  assert.equal(failed.context.label, 'Not saved');
  assert.ok(!failed.context.reloaded);

  console.log('Studio client: restore locking, pending imports, failed/pending audio and failed saves passed.');
})().catch(error => { console.error(error); process.exitCode = 1; });
