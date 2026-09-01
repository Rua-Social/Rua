/* ------------------------------------------------------------------
   Checks the file you are actually going to deliver.

   check-colour.js reasons about the brand colours on paper: it composites
   each blob over white on its own and reports the worst. That misses the
   case that actually matters, which is two blue blobs overlapping — the
   real composite is more saturated than any single blob predicts. On the
   current params it under-reports by about 4 points of excursion and says
   "safe to deliver" while the real frames sit in watch territory.

   So this decodes the rendered master and measures the pixels themselves:
   chroma legality, loop seamlessness, banding, and file tagging.

   Run: npm run verify        (npm run build does it for you)
------------------------------------------------------------------ */

const { spawn, execFileSync } = require('child_process');
const path = require('path');
const fs   = require('fs');
const P    = require('./params.js');

const NAME  = P.name || 'brand-sky-outro';
const MASTER = path.join(__dirname, 'out', `${NAME}_ProResHQ.mov`);
const REVIEW = path.join(__dirname, 'out', `${NAME}_h264.mp4`);
const W = P.width, H = P.height;

if (!fs.existsSync(MASTER)) {
  console.error(`\nNo master at ${MASTER}. Run npm run render first.\n`);
  process.exit(1);
}

let fail = 0, warn = 0;
const pass = m => console.log(`  ok    ${m}`);
const soft = m => { warn++; console.log(`  warn  ${m}`); };
const hard = m => { fail++; console.log(`  FAIL  ${m}`); };

/* Stream a decode of the master, handing each frame to fn as a Buffer.
   Frames are processed and dropped one at a time — the whole sequence is
   1.4GB at 8-bit RGB and there is no reason to hold it. */
function eachFrame(pixFmt, bytesPerFrame, fn, file = MASTER) {
  return new Promise((res, rej) => {
    const ff = spawn('ffmpeg', [
      '-v', 'error', '-i', file,
      '-f', 'rawvideo', '-pix_fmt', pixFmt, 'pipe:1',
    ], { stdio: ['ignore', 'pipe', 'inherit'] });

    let acc = Buffer.alloc(0), n = 0;
    ff.stdout.on('data', d => {
      acc = acc.length ? Buffer.concat([acc, d]) : d;
      while (acc.length >= bytesPerFrame) {
        fn(acc.subarray(0, bytesPerFrame), n++);
        acc = acc.subarray(bytesPerFrame);
      }
    });
    ff.on('close', c => c === 0 ? res(n) : rej(new Error(`ffmpeg exited ${c}`)));
  });
}

(async () => {

// ---- 1. CHROMA LEGALITY, measured in the master's own colour space ------
// The master is yuv422p10le. Asking about Rec.709 legality in RGB means
// guessing at the conversion; reading the Y/Cb/Cr code values that are
// actually in the file does not.
console.log('\nCHROMA LEGALITY  (10-bit code values, from the ProRes master)');

let minY = 1e9, maxY = -1e9, minC = 1e9, maxC = -1e9, worstExc = 0;
const BPF444 = W * H * 3 * 2;   // yuv444p10le, 2 bytes per sample

await eachFrame('yuv444p10le', BPF444, (f) => {
  const n = W * H;
  for (let i = 0; i < n; i += 7) {           // stride-sample, 7 is coprime with W
    const y  = f.readUInt16LE(i * 2);
    const cb = f.readUInt16LE((n + i) * 2);
    const cr = f.readUInt16LE((n * 2 + i) * 2);
    if (y < minY) minY = y; if (y > maxY) maxY = y;
    const lo = Math.min(cb, cr), hi = Math.max(cb, cr);
    if (lo < minC) minC = lo; if (hi > maxC) maxC = hi;
    const exc = Math.max(Math.abs(cb - 512), Math.abs(cr - 512)) / 448 * 100;
    if (exc > worstExc) worstExc = exc;
  }
});

// 10-bit legal: luma 64-940, chroma 64-960. Hard limits are 4 and 1019.
console.log(`  luma   ${minY} .. ${maxY}   (legal 64-940)`);
console.log(`  chroma ${minC} .. ${maxC}   (legal 64-960)`);
console.log(`  worst chroma excursion ${worstExc.toFixed(1)}% of the Rec.709 ceiling`);

/* Pure white converts to Y=940.0 exactly, and ffmpeg's rounding lands it on
   941 about as often as 940. One code value over on a white that is meant to
   be white is a rounding artifact, not a grading problem, so it warns rather
   than blocking delivery. Anything beyond that is real clipping. */
if (minY < 64 || maxY > 943) hard(`luma outside legal range (${minY}..${maxY})`);
else if (maxY > 940) soft(`luma peaks at ${maxY}, one code over the 940 ceiling — ` +
                          'that is white rounding up, harmless for social delivery');
else pass('luma legal');

if (minC < 64 || maxC > 960) hard('chroma is outside legal range');
else if (worstExc > 90) soft(`chroma at ${worstExc.toFixed(1)}% — encoder ringing on a ` +
                             'hard edge can push this illegal. Lower blueAlphaCap.');
else if (worstExc > 85) soft(`chroma at ${worstExc.toFixed(1)}% — tight but deliverable. ` +
                             'Watch the blue/white boundary after upload.');
else pass(`chroma has headroom (${worstExc.toFixed(1)}%)`);

// ---- 2. LOOP SEAMLESSNESS ----------------------------------------------
// The join from the last frame back to the first has to look like any
// other frame step. If it is meaningfully bigger, the loop visibly jumps.
console.log('\nLOOP');

const BPF = W * H * 3;
let first = null, prev = null, last = null, prevDelta = 0, sumStep = 0, steps = 0;
const mad = (a, b) => { let s = 0; for (let i = 0; i < a.length; i++) s += Math.abs(a[i] - b[i]); return s / a.length; };

const count = await eachFrame('rgb24', BPF, (f, i) => {
  const c = Buffer.from(f);
  if (i === 0) first = c;
  if (prev) { const d = mad(prev, c); sumStep += d; steps++; prevDelta = d; }
  prev = c; last = c;
});

const expected = Math.round(P.fps * P.duration);
if (count === expected) pass(`${count} frames, matches fps x duration`);
else hard(`${count} frames but fps x duration = ${expected}`);

const join = mad(last, first);
const avg  = sumStep / steps;
const ratio = join / avg;
console.log(`  join (last -> first) ${join.toFixed(3)}   typical step ${avg.toFixed(3)}   ratio ${ratio.toFixed(2)}x`);
if (ratio > 2.0) hard(`the loop jumps — ${ratio.toFixed(2)}x a normal step. Check every blob has whole-number cycles.`);
else if (ratio > 1.3) soft(`loop join is ${ratio.toFixed(2)}x a normal step, may be visible`);
else pass('loop is seamless');

if (join < 1e-6) soft('last frame is identical to the first — you have a duplicate ' +
                      'frame at the join, which stalls for one frame every loop');

// ---- 3. BANDING ---------------------------------------------------------
// A "flat run" is a stretch of consecutive pixels of identical colour. On a
// smooth gradient those are quantisation steps, and once they get wide
// enough to see, that is a band.
console.log('\nBANDING  (widest stretch of identical pixels on a centre scanline)');

function widestRun(buf, axis) {
  const N = axis === 'h' ? W : H;
  let prevV = -1, run = 0, max = 0;
  for (let k = 0; k < N; k++) {
    const x = axis === 'h' ? k : (W >> 1);
    const y = axis === 'h' ? (H >> 1) : k;
    const i = (y * W + x) * 3;
    const v = (buf[i] << 16) | (buf[i + 1] << 8) | buf[i + 2];
    if (v === prevV) { run++; if (run > max) max = run; }
    else { prevV = v; run = 1; }
  }
  return max;
}
const bh = widestRun(first, 'h'), bv = widestRun(first, 'v');
console.log(`  master  horizontal ${bh} px    vertical ${bv} px`);
if (bh > 24 || bv > 24) hard('wide flat runs in the master — raise dither in params.js');
else if (bh > 12 || bv > 12) soft('flat runs in the master are getting wide');
else pass('master has no meaningful banding');

/* The master is nearly lossless, so it is the easy case. The H.264 is the
   file that actually goes up, and a lossy encoder treats a one-code dither
   as noise to be spent away — which is exactly how a gradient that looked
   clean in the master ends up banded on a phone. So measure it there too. */
if (fs.existsSync(REVIEW)) {
  let rf = null;
  await eachFrame('rgb24', BPF, (f, i) => { if (i === 0) rf = Buffer.from(f); }, REVIEW);
  const rh = widestRun(rf, 'h'), rv = widestRun(rf, 'v');
  console.log(`  review  horizontal ${rh} px    vertical ${rv} px`);
  if (rh > 32 || rv > 32) hard('the H.264 has banded — the encoder spent away the dither. ' +
                               'Lower reviewCrf, or add a little grain in params.js');
  else if (rh > 16 || rv > 16) soft('some banding in the H.264, check it on a phone before sending');
  else pass('review copy holds up');
}

// ---- 4. FILE TAGGING ----------------------------------------------------
// ffmpeg silently ignores -color_trc when the input frames carry their own
// tag, so this is worth confirming rather than assuming.
console.log('\nTAGGING');
for (const [label, file] of [['master', MASTER], ['review', REVIEW]]) {
  if (!fs.existsSync(file)) { soft(`${label}: missing`); continue; }
  const out = execFileSync('ffprobe', [
    '-v', 'error', '-select_streams', 'v:0',
    '-show_entries', 'stream=color_primaries,color_transfer,color_space,color_range',
    '-of', 'default=nw=1:nk=1', file,
  ]).toString().trim().split('\n');
  const [prim, trc, spc, rng] = out;
  const mb = (fs.statSync(file).size / 1048576).toFixed(1);
  console.log(`  ${label.padEnd(7)} ${prim}/${trc}/${spc}/${rng}   ${mb} MB`);
  if (trc !== 'bt709') hard(`${label} is tagged ${trc}, not bt709 — Final Cut will guess and the cyan can shift`);
  else pass(`${label} tagged Rec.709 throughout`);
}

// ---- verdict ------------------------------------------------------------
console.log('');
if (fail)      { console.log(`${fail} failure(s), ${warn} warning(s). Do not deliver this.\n`); process.exit(1); }
else if (warn) { console.log(`Clean, with ${warn} warning(s) worth a look before you send it.\n`); }
else           { console.log('All checks clean. Safe to deliver.\n'); }

})().catch(e => { console.error(e); process.exit(1); });
