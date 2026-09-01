/* ------------------------------------------------------------------
   Capture and encode in a single pass.

   The old path was: screenshot 225 PNGs to disk (540MB), then run ffmpeg
   over that folder twice, once per output. That decodes every PNG twice
   and writes half a gigabyte you immediately throw away.

   Here Chrome's PNG buffers go straight down ffmpeg's stdin, and one
   ffmpeg invocation emits both the ProRes master and the H.264 review
   copy from that single decode. Nothing touches the disk but the outputs.

   Run: npm run render
------------------------------------------------------------------ */

const puppeteer = require('puppeteer');
const { spawn }  = require('child_process');
const path = require('path');
const fs   = require('fs');
const P    = require('./params.js');

const TOTAL = Math.round(P.fps * P.duration);
const OUT   = path.join(__dirname, 'out');
const NAME  = P.name || 'brand-sky-outro';

if (Math.abs(P.fps * P.duration - TOTAL) > 1e-9) {
  console.error(`\nfps x duration = ${P.fps * P.duration}, which is not a whole`);
  console.error('number of frames. The loop cannot be seamless. Fix params.js.\n');
  process.exit(1);
}
for (const b of P.blobs) {
  if (!Number.isInteger(b.cycles)) {
    console.error(`\nblob "${b.colour}" has cycles: ${b.cycles}, which is not a whole`);
    console.error('number. The loop will jump. Fix params.js.\n');
    process.exit(1);
  }
}

const grain = P.grain > 0 ? `noise=alls=${P.grain}:allf=t+u` : null;

/* Two things ffmpeg gets wrong if you let it:

   1. The PNGs carry an sRGB transfer tag, and in ffmpeg 7+ that frame-level
      tag beats the -color_trc option on the output, so you silently get a
      file tagged iec61966-2-1 no matter what you asked for. setparams is
      what actually overrides it. Verify with:
        ffprobe -show_entries stream=color_transfer out/<file>
   2. Untagged, Final Cut guesses, and a near-limit cyan is exactly the
      colour that shifts when it guesses wrong. */
const setparams =
  'setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv';

/* Tempting to add an explicit
     scale=in_range=full:out_range=tv:...:sws_dither=ed
   here to name the conversion rather than let ffmpeg infer it. Measured, it
   makes things worse: the outputs then convert twice (once in the filter,
   once again for the encoder's -pix_fmt) and banding in the H.264 went from
   18px to 97px. Let ffmpeg do the single conversion it was going to do. */
const chain = [setparams, grain].filter(Boolean).join(',');
const TAG = ('-color_primaries bt709 -color_trc bt709 ' +
             '-colorspace bt709 -color_range tv').split(' ');

const args = [
  '-y', '-hide_banner', '-loglevel', 'error', '-stats',
  '-f', 'image2pipe', '-c:v', 'png', '-framerate', String(P.fps), '-i', 'pipe:0',
  '-filter_complex', `[0:v]${chain},split=2[m][r]`,

  // ProRes 422 HQ master — this is the one that goes in the FCP timeline
  '-map', '[m]', '-c:v', 'prores_ks', '-profile:v', '3',
  '-pix_fmt', 'yuv422p10le', ...TAG,
  path.join(OUT, `${NAME}_ProResHQ.mov`),

  /* H.264 — for sending round, and for the actual platform upload.

     CRF alone gives a ~1-2 Mbps file here, because a smooth gradient is
     genuinely cheap to encode and CRF is doing its job. But this file gets
     handed to Instagram's and TikTok's transcoder, which re-encodes from
     whatever it is given, and a starved source leaves it nothing to work
     from — the first thing it discards is the low-amplitude high-frequency
     dither holding the gradient together.

     The way to spend more bytes is a lower CRF, not -minrate. Measured,
     -minrate/-maxrate/-bufsize alongside -crf changed the output by exactly
     nothing: 2.4Mbps with or without. x264 treats VBV as a ceiling, never a
     floor, so the only real lever is the quality target itself. */
  '-map', '[r]', '-c:v', 'libx264', '-crf', String(P.reviewCrf ?? 10),
  '-preset', 'slow', '-profile:v', 'high', '-level', '4.0',
  '-g', String(P.fps * 2), '-keyint_min', String(P.fps),
  '-pix_fmt', 'yuv420p', ...TAG,
  '-movflags', '+faststart',
  path.join(OUT, `${NAME}_h264.mp4`),
];

(async () => {
  fs.mkdirSync(OUT, { recursive: true });

  const browser = await puppeteer.launch({
    args: [
      '--force-color-profile=srgb',
      '--disable-lcd-text',
      '--use-gl=angle',
      '--enable-unsafe-swiftshader',   // lets it run headless without a GPU
    ],
  });
  const page = await browser.newPage();
  await page.setViewport({
    width: P.width, height: P.height, deviceScaleFactor: 1,
  });

  const errors = [];
  page.on('pageerror', e => errors.push(e.message));

  await page.goto('file://' + path.join(__dirname, 'index-gl.html'),
                  { waitUntil: 'networkidle0' });

  if (errors.length) {
    console.error('\nThe page threw before it could render:\n  ' +
                  errors.join('\n  ') + '\n');
    await browser.close();
    process.exit(1);
  }

  // Stop the preview loop. From here every frame is drawn on demand, so
  // what lands in the file is a pure function of the frame index — no
  // clock, nothing that can drift or drop a frame under load.
  await page.evaluate(() => window.stopPreview());

  const ff = spawn('ffmpeg', args, { stdio: ['pipe', 'inherit', 'inherit'] });
  const done = new Promise((res, rej) => {
    ff.on('close', c => c === 0 ? res() : rej(new Error(`ffmpeg exited ${c}`)));
    ff.on('error', rej);
  });
  ff.stdin.on('error', () => {});   // ffmpeg dying first would raise EPIPE

  console.log(`\nRendering ${TOTAL} frames at ${P.width}x${P.height} @ ${P.fps}fps`);
  const t0 = Date.now();

  for (let i = 0; i < TOTAL; i++) {
    await page.evaluate(n => window.drawFrame(n), i);
    const buf = await page.screenshot({ captureBeyondViewport: false });

    if (!ff.stdin.write(buf)) {
      await new Promise(r => ff.stdin.once('drain', r));   // respect backpressure
    }

    if (i % 5 === 0 || i === TOTAL - 1) {
      const el = (Date.now() - t0) / 1000;
      const eta = el / (i + 1) * (TOTAL - i - 1);
      process.stdout.write(
        `\r  ${i + 1}/${TOTAL}  ${(el / (i + 1)).toFixed(2)}s/frame  ` +
        `eta ${Math.round(eta)}s   `);
    }
  }

  ff.stdin.end();
  console.log('\n  encoding...');
  await done;
  await browser.close();

  console.log(`\nDone in ${Math.round((Date.now() - t0) / 1000)}s\n`);
  for (const f of fs.readdirSync(OUT)) {
    const s = fs.statSync(path.join(OUT, f));
    console.log(`  ${(s.size / 1048576).toFixed(1).padStart(7)} MB  ${f}`);
  }
  console.log('');
})().catch(e => { console.error(e); process.exit(1); });
