# Brand Sky Outro

Animated brand gradient background for a testimonial outro card.
Text is overlaid separately in Final Cut Pro. This renders background only.

Colours are the Sky gradient from the brand book, in brand sequence:
White `#FFFFFF` into Electric Yellow `#FFF628` into Electric Blue `#00F0FA`.

---

## One-time setup

```bash
cd 30-tools/animation-renderer
npm install          # pulls puppeteer, downloads a Chromium, takes a minute
brew install ffmpeg  # skip if you already have it
```

---

## The loop you'll actually use

**1. Start the preview**

```bash
npm run dev
```

Then open **http://localhost:5173** in your browser.

Leave that terminal tab running the whole time you're working. Ctrl+C stops it.

**2. Tweak**

Put your editor and the browser side by side. Open `params.js`, change a
number, save.

**The browser reloads itself.** No refreshing, no clicking back and forth.
Save and watch it change.

Everything adjustable is in `params.js` and commented.

**3. Render**

```bash
npm run build
```

About a minute for 9 seconds at 1080x1920. It renders, then checks its own
output and tells you whether it's safe to send.

**Output lands in `out/`:**

| File | Use |
|---|---|
| `brand-sky-outro_ProResHQ.mov` | The one that goes in the FCP timeline |
| `brand-sky-outro_h264.mp4` | Review copy |

---

## All the commands, in one place

| Command | Does |
|---|---|
| `npm run dev` | Live preview at localhost:5173, reloads on save |
| `npm run render` | Renders both output files. About a minute |
| `npm run verify` | Measures the rendered files and passes or fails them |
| `npm run build` | render, then verify |

---

## What to tweak, and what it does

All in `params.js`.

| Want | Change |
|---|---|
| More or less blue | The `alpha` on the blue blobs, or their `radius` |
| Slower drift | Raise `duration` |
| More visible movement | Raise `ampX` / `ampY` on a blob |
| More breathing | Raise `scaleAmp` |
| Different loop length | `duration`. Keep every `cycles` a whole number |
| Landscape instead | `width: 3840, height: 2160` |
| Softer overall | Drop the `alpha` values |
| Reposition a blob | `cx` / `cy`. Both are fractions of the WIDTH |

**The one rule: `cycles` must be a whole number on every blob.** That's what
makes the loop seamless. A blob on `cycles: 1` completes one drift per loop,
`cycles: 2` completes two. Anything fractional and you get a visible jump at
the loop point. `npm run render` refuses to start if you break this, and
`npm run verify` measures the loop join afterwards to confirm.

Different `cycles` and `phase` values per blob mean they never sync up, which
is what stops it reading as a mechanical loop.

---

## What `npm run verify` is checking

It decodes the files you're about to deliver and measures them. Four things:

**Chroma legality.** Reads the actual Y/Cb/Cr code values out of the ProRes
master. See below for why this matters and why it replaced the old
parameter-based check.

**The loop.** Compares the last frame back to the first and reports it as a
ratio against a normal frame-to-frame step. 1.0 means the join is
indistinguishable from any other frame. Above about 1.3 and you'd see it.

**Banding.** Measures the widest run of identical pixels along a centre
scanline. On a smooth gradient those runs are quantisation steps, and once
they get wide enough to see, that's a band. It checks the H.264 as well as
the master, because they fail differently — see below.

**Tagging.** Confirms both files came out tagged Rec.709. This is not
paranoia, it's a bug that actually bit: `-color_trc bt709` is silently
ignored when the input frames carry their own colour tag, and the previous
version of this project was shipping files tagged sRGB while believing they
were Rec.709.

---

## Why colour safety matters here

Electric Blue `#00F0FA` is legal in Rec.709, but only just, and the problem
is delivery. Instagram and TikTok re-encode hard, and encoders ring on
saturated edges. Push a saturated cyan past the chroma ceiling on a hard
edge against white and you get smearing or blocking.

`blueAlphaCap` in params.js caps the blue's peak opacity to keep headroom.

**The catch, and the reason `verify.js` exists.** The old `check-colour.js`
composited each blob over white *on its own*. But two blue blobs overlap, and
the real composite is more saturated than any single blob predicts. On the
current params it reported 85.0% and said "safe to deliver" — the actual
rendered frames measure **89.5%**. It wasn't wrong so much as blind to the
one case that matters.

Measured on the real frames, across the whole loop:

| `blueAlphaCap` | worst excursion | peak blue pixel | |
|---|---|---|---|
| 0.90 | 89.3% | `#0DF0F9` | current — tight |
| 0.85 | 86.6% | `#14F0F9` | tight |
| 0.80 | 84.2% | `#1BF1F9` | headroom |
| 0.75 | 81.9% | `#21F1F9` | headroom |

`0.80` is the first value with real headroom, and `#1BF1F9` against
`#0DF0F9` is not a difference you'd pick out of a lineup. It's a brand call
rather than a technical one, so it's been left at `0.90` — but if a client
ever reports smeary edges on a story, this table is the fix.

`check-colour.js` is still there and still runs, if you want the
per-parameter view before committing to a render.

---

## Why the gradient is drawn in WebGL

`index-gl.html` computes the whole picture in one shader pass.
`index.html` is the original, which stacked four translucent divs and let
the browser composite them. Both are kept; the GL one is what renders.

Two reasons it changed.

**Banding.** Every stacked div lands in an 8-bit buffer before the next one
blends over it, so quantisation error compounds four times. The shader does
the whole composite in float and quantises exactly once, with a dither
applied immediately before that single quantisation. Widest flat run on a
centre scanline, which is the thing you see as a band:

| | horizontal | vertical |
|---|---|---|
| CSS divs | 10 px | 13 px |
| WebGL, dither off | 65 px | 100 px |
| WebGL, dither on | 5 px | 6 px |

(Dither off is *worse* than CSS because Chrome dithers its own gradients.
The win is the dither, not the shader — the shader is what makes it
possible to dither at the right moment.)

The dither is triangular, not uniform, and that distinction is worth one
sentence: triangular noise makes the quantisation error the same size
wherever the signal sits between two code values, whereas uniform noise
makes it collapse to nothing exactly on a code value and peak between them.
On a slowly drifting gradient, uniform dither visibly pulses as the picture
crosses code boundaries. Triangular doesn't.

**A hard edge that shouldn't have been there.** `radial-gradient(circle, …)`
sizes its stops to the box's *farthest corner*, but `border-radius: 50%`
clips the div at half its width — a factor of √2 earlier. So each blob's
falloff was being chopped off while still at about 5% opacity, leaving a
faint hard-edged ring. It measures as a 3-code-value step where neighbouring
pixels differ by 0.63. The shader runs the falloff to zero as intended.

---

## Why grain is off now

It used to be on at `8`, on the reasoning that grain dithers the gradient and
gives the platform encoder something to hold onto. Measured, it does the
opposite. Grain is incompressible, so at a fixed CRF the encoder spends its
bitrate on noise and starves the gradient:

| | size | banding H / V |
|---|---|---|
| crf 18, no grain | 1.2 MB | 15 / 41 |
| crf 18, grain 2 | 2.3 MB | 14 / 48 |
| crf 18, grain 4 | 5.0 MB | 9 / 24 |
| **crf 14, no grain** | **2.3 MB** | **6 / 11** |

Same bytes, spent on a lower CRF instead of on noise, and the banding is four
times better. `grain` is a look choice now, not a fix.

There's a related trap worth knowing about. The master measures clean, but
the H.264 is the file that actually goes up, and a lossy encoder throws away
low-amplitude high-frequency signal first — which is exactly what dither is.
A gradient that's perfect in the master can still band on a phone. That's why
`verify` checks both files.

## Why the H.264 is 15MB and not 2MB

`reviewCrf` is 10, which is lower than you'd choose for a file this simple.
Instagram and TikTok re-encode everything you give them, and they re-encode
from your file rather than your intentions — hand their transcoder a starved
2Mbps gradient and it has nothing to hold onto. The usual advice for
1080x1920 is 5-10Mbps. crf 10 lands around 11.

The obvious way to do that is a bitrate floor, and it does not work: adding
`-minrate 8M -maxrate 12M -bufsize 24M` alongside `-crf` changed the output
by *exactly nothing*, byte for byte. x264 treats VBV as a ceiling and never
a floor. CRF is the only lever that moves it.

---

## Before you send it

- [ ] `npm run build` comes back clean
- [ ] Watch the loop point. Play the h264 twice through and look for a jump
- [ ] Test upload. Post the h264 to a private TikTok and a private IG story,
      then watch it back on a phone. This is the only test that actually
      counts, everything above is just stacking the odds
- [ ] Check text contrast. The background sits bright throughout (luma never
      drops below about 720 of 940), so black text holds and white text
      disappears. Black is in the brand palette
- [ ] Confirm frame rate matches your FCP timeline. Currently 25

---

## Notes

- Frame rate is 25 for Ireland. Change `fps` in params.js if the rest of the
  edit is 24.
- Nothing is written to disk except the two output files. Chrome's frames go
  straight down ffmpeg's stdin, and one ffmpeg pass emits both outputs. The
  old path wrote 225 PNGs (~190MB) and then decoded them twice, once per
  output, which is most of why it used to take 20-40 minutes.
- The old `frames/` folder is no longer used or written to. Safe to delete.
- `capture.js` and `encode.sh` are the old two-stage path, kept as
  `npm run build:legacy` in case you need to compare against it.
- Puppeteer screenshots are 8-bit, so the 10-bit ProRes carries no more
  precision than the 8-bit source — the dither is what makes that acceptable
  rather than the bit depth.
- ProRes is tagged Rec.709 explicitly, via a `setparams` filter rather than
  the `-color_trc` flag, because the flag doesn't work here.
