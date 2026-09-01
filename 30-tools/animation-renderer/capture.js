const puppeteer = require('puppeteer');
const fs   = require('fs');
const path = require('path');
const P    = require('./params.js');

const TOTAL  = Math.round(P.fps * P.duration);
const OUTDIR = path.join(__dirname, 'frames');

(async () => {
  // Clear old frames so a shorter render can't leave stale files behind
  if (fs.existsSync(OUTDIR)) fs.rmSync(OUTDIR, { recursive: true });
  fs.mkdirSync(OUTDIR);

  const browser = await puppeteer.launch({
    args: ['--force-color-profile=srgb', '--disable-lcd-text'],
  });
  const page = await browser.newPage();

  // Viewport matches output exactly, so the preview scale resolves to 1
  await page.setViewport({
    width: P.width,
    height: P.height,
    deviceScaleFactor: 1,
  });

  await page.goto('file://' + path.join(__dirname, 'index.html'),
                  { waitUntil: 'networkidle0' });

  await page.evaluate(() => document.getAnimations().forEach(a => a.pause()));

  console.log(`Capturing ${TOTAL} frames at ${P.width}x${P.height} @ ${P.fps}fps`);

  for (let i = 0; i < TOTAL; i++) {
    const ms = (i / P.fps) * 1000;
    await page.evaluate(t => {
      document.getAnimations().forEach(a => { a.currentTime = t; });
    }, ms);

    await page.screenshot({
      path: path.join(OUTDIR, `frame_${String(i).padStart(5, '0')}.png`),
      captureBeyondViewport: false,
    });

    if (i % 10 === 0 || i === TOTAL - 1) {
      process.stdout.write(`\r  ${i + 1}/${TOTAL}`);
    }
  }

  console.log('\nFrames written to ./frames');
  await browser.close();
})();
