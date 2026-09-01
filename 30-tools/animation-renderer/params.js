/* ------------------------------------------------------------------
   ECOPLEX SKY OUTRO - all tunable values live here.
   Edit this file, refresh the browser, capture when happy.
   Read by both index.html (preview) and capture.js (render).
------------------------------------------------------------------ */

const PARAMS = {

  // ---- OUTPUT ----------------------------------------------------
  width:    1080,   // 9:16 vertical 4K. Use 3840 x 2160 for landscape.
  height:   1920,
  fps:      25,     // 25 for Ireland/PAL. Match your FCP timeline.
  duration: 9,     // seconds. Loop is seamless as long as every
                    // blob "cycles" value below is a whole number.

  // ---- BRAND COLOURS (from the brand book) -------------------
  colours: {
    white:  '255, 255, 255',   // #FFFFFF  PANTONE WHITE
    yellow: '255, 246, 40',    // #FFF628  ELECTRIC YELLOW / PANTONE 3945 C
    blue:   '0, 240, 250',     // #00F0FA  ELECTRIC BLUE  / PANTONE 305 U
  },

  // ---- COLOUR SAFETY ---------------------------------------------
  // Electric Blue at full strength sits at 94.5% of the Rec.709 chroma
  // ceiling. Encoder overshoot on a hard edge pushes it illegal.
  // Capping peak alpha at 0.90 keeps the composite at ~85% and gives
  // headroom. Run `npm run check` after changing this.
  // Set to 1.0 to use the raw brand colour and accept the risk.
  blueAlphaCap: 0.90,

  // ---- DITHER ----------------------------------------------------
  // Applied in the shader, immediately before the one and only
  // quantisation to 8 bits. This is the thing that actually kills
  // banding, because it decorrelates the quantisation error instead of
  // masking it after the fact.
  // Amplitude in code values, measured as the widest run of identical
  // pixels on a centre scanline after the ProRes round trip through
  // tv-range YUV — which is where the delivered file actually lives:
  //
  //     0     66 / 112    bands badly
  //     1      9 /  28    fine in memory, falls apart on encode
  //     2      5 /   9
  //   2.5      5 /   6    <-- here
  //     3      2 /   5    better still, but you start to see the grain
  //
  // 1.0 is the textbook amount for a straight 8-bit quantisation. It isn't
  // enough here because the full-range RGB to tv-range YUV conversion
  // squeezes 256 levels into 219, and that rounding collapses about a sixth
  // of the dithered pairs back together again.
  dither: 2.5,

  // ---- GRAIN -----------------------------------------------------
  // Added at encode time by ffmpeg. Leave this at 0.
  //
  // It was originally here to fight banding, on the reasoning that grain
  // gives the platform encoder something to hold onto. Measured, it does
  // the opposite: grain is incompressible, so at a fixed CRF the encoder
  // spends its bitrate on noise and starves the gradient. Banding in the
  // H.264, as widest flat run H/V:
  //
  //   crf 18, no grain     1.2 MB    15 / 41
  //   crf 18, grain 2      2.3 MB    14 / 48   worse, and twice the size
  //   crf 18, grain 4      5.0 MB     9 / 24   still worse than crf 14
  //   crf 14, no grain     2.3 MB     6 / 11   <-- same size as grain 2
  //
  // Spending those same bytes on a lower CRF beats spending them on
  // noise, every time. Grain is a look choice now, not a fix.
  grain: 0,

  // Quality of the H.264. Lower = bigger and better. This is both the
  // review copy and the file you upload.
  //
  // Two things push it lower than you'd expect. The shader's dither is a
  // low-amplitude high-frequency signal, which is exactly what a lossy
  // encoder discards first — so a master that measures clean can still band
  // on a phone. And Instagram and TikTok re-encode from your file, so a
  // starved source gives their transcoder nothing to hold onto; 5-10Mbps is
  // the usual advice for 1080x1920.
  //
  //   crf 14   2.6 MB   2.4 Mbps   banding  8 / 18
  //   crf 10  12.4 MB  11.5 Mbps   banding  6 / 15   <-- both boxes ticked
  //   crf  8  25.1 MB  23.4 Mbps   banding  6 /  9
  //
  // Note -minrate does nothing here. x264 treats VBV as a ceiling and never
  // a floor, so CRF is the only lever that actually moves the bitrate.
  reviewCrf: 10,

  // Basename for the files in out/
  name: 'brand-sky-outro',

  // ---- BLOBS -----------------------------------------------------
  // Brand sequence is WHITE > YELLOW > BLUE. Keep that order.
  // All positions/sizes are fractions of the WIDTH.
  //   cx, cy    centre position
  //   radius    size of the falloff
  //   alpha     peak opacity at centre
  //   ampX/ampY how far it drifts
  //   cycles    WHOLE NUMBER. drifts per loop. keeps the loop seamless.
  //   phase     radians. offsets timing so blobs never sync up.
  //   scaleAmp  how much it breathes in and out
  blobs: [
    { colour: 'white',  cx: 0.22, cy: 0.30, radius: 0.85, alpha: 0.95,
      ampX: 0.05, ampY: 0.06, cycles: 4, phase: 0.00, scaleAmp: 0.10 },

    { colour: 'yellow', cx: 0.64, cy: 2, radius: 0.92, alpha: 1.00,
      ampX: 0.07, ampY: 0.05, cycles: 1, phase: 1.90, scaleAmp: 0.09 },

    { colour: 'blue',   cx: 0.74, cy: 1.1, radius: 0.95, alpha: 1.00,
      ampX: 0.06, ampY: 0.07, cycles: 2, phase: 3.40, scaleAmp: 0.12 },

    { colour: 'blue',   cx: 0.88, cy: 0.95, radius: 0.50, alpha: 0.55,
      ampX: 0.08, ampY: 0.06, cycles: 2, phase: 0.80, scaleAmp: 0.14 },
  ],

  // How many keyframes are sampled along each sine drift.
  // Higher = smoother motion, slower to set up. 48 is plenty.
  keyframeResolution: 48,
};

if (typeof module !== 'undefined') module.exports = PARAMS;
