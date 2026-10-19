#!/usr/bin/env python3
"""Papa Rua barber promo: cut, grade, caption, freeze-frame ending. Dialogue only, no music."""
import json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SRC = "/Users/darraghhoare/Downloads/IMG_1467.MOV"
OUT_DIR = "/Users/darraghhoare/Downloads/papa-rua-barber-promo"
WORK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "work")
FPS = 24
# Instagram's caption font (Instagram Sans) is proprietary; Poppins is the closest free match
FONT_CAP = "/Library/Fonts/Poppins-SemiBold.ttf"

# Crops in the autorotated 2160x3840 frame; face sits around (870, 2030)
CROPS = {
    "W": "1964:3492:100:284",
    "M": "1440:2560:250:955",
    "T": "1080:1920:330:1262",
}
GRADE = "eq=contrast=1.07:saturation=0.86:gamma=0.98,vignette=angle=PI/5.5"

SHOTS = [
    (24.47, 26.92, "T", [(24.47, 25.85, "I'm playing a gig tonight, actually,"),
                         (25.85, 26.92, "so I need to look fresh.")]),
    (34.55, 38.94, "W", [(34.55, 36.95, "We're doing the National Concert Hall tonight, so..."),
                         (36.95, 37.50, "The Concert Hall?"),
                         (37.50, 38.94, "Yeah, yeah. Believe it or not.")]),
    (45.97, 48.23, "T", [(45.97, 48.23, "Last time I was there was with Phil Coulter, actually.")]),
    (98.50, 102.36, "W", [(98.50, 102.36, "It's part of, like, a showcase gig.")]),
    (105.61, 107.34, "T", [(105.61, 107.34, "Artist development programme.")]),
    (170.55, 174.90, "M", [(170.55, 172.70, "We're all the same hopeless people"),
                           (172.70, 174.90, "trying to make our dreams come true.")]),
    (174.90, 177.22, "W", [(175.45, 177.22, "Not hopeless. It's actually the opposite.")]),
    (225.76, 229.43, "M", [(225.76, 227.95, "Would you let me do a little gig in here?"),
                           (227.95, 229.43, "Absolutely.")]),
    (609.60, 614.44, "T", [(609.60, 612.50, "It's just gonna be a very different kind of show"),
                           (612.50, 614.44, "in the National Concert Hall. Friends and family.")]),
    (1254.43, 1256.59, "M", [(1254.43, 1255.92, "I'm looking forward to tonight now."),
                             (1255.92, 1256.59, "Feeling good.")]),
]
# Freeze-frame ending: plain hold on the last frame with the goodbye audio under it
END_AUDIO = (1361.14, 1366.48)
END_DUR = 5.34
END_CAPS = [(1361.21, 1364.21, "Happy days. See you later."),
            (1364.25, 1365.00, "Have a good one.")]
END_TEXT = "Tonight at the National Concert Hall"  # top-of-frame overlay on the freeze


def snap(t):
    return round(t * FPS) / FPS


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"FAILED: {' '.join(cmd)}\n{r.stderr[-3000:]}")


ENC_V = ["-c:v", "libx264", "-crf", "12", "-preset", "veryfast", "-pix_fmt", "yuv420p",
         "-r", str(FPS), "-video_track_timescale", "24000"]
ENC_A = ["-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2"]


def render_shot(i, a, b, crop):
    out = os.path.join(WORK, f"shot{i:02d}.mov")
    d = b - a
    n = round(d * FPS)  # exact frame count; audio trimmed to the same length (2000 samples per frame)
    vf = (f"crop={CROPS[crop]},scale=1080:1920:flags=lanczos,setsar=1,fps={FPS},{GRADE},format=yuv420p,"
          f"trim=end_frame={n},setpts=PTS-STARTPTS")
    af = (f"aresample=48000,atrim=end_sample={n * 2000},asetpts=PTS-STARTPTS,"
          f"afade=t=in:d=0.04,afade=t=out:st={n / FPS - 0.05:.4f}:d=0.05")
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.4f}", "-i", SRC, "-t", f"{d + 0.5:.4f}",
         "-vf", vf, "-af", af, *ENC_V, *ENC_A, out])
    return out


def caption_png(text, path, centre_y=1330):
    W, H = 1080, 1920
    font = ImageFont.truetype(FONT_CAP, 56)
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if font.getlength(test) <= 800 or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    if len(lines) == 2:  # balance two-line captions so no word is left on its own
        best = min(range(1, len(words)),
                   key=lambda k: max(font.getlength(" ".join(words[:k])), font.getlength(" ".join(words[k:]))))
        lines = [" ".join(words[:best]), " ".join(words[best:])]
    lh = 74
    top = centre_y - (len(lines) * lh) // 2
    txt = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dt, ds = ImageDraw.Draw(txt), ImageDraw.Draw(shadow)
    for n, line in enumerate(lines):
        x = (W - font.getlength(line)) / 2
        y = top + n * lh
        ds.text((x, y + 2), line, font=font, fill=(0, 0, 0, 170))
        dt.text((x, y), line, font=font, fill=(255, 255, 255, 255))
    out = Image.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(5)), txt)
    out.save(path)


def end_freeze(last_shot):
    # clone the last decoded frame of the final shot so format and colour tags match exactly
    out = os.path.join(WORK, "endfreeze.mov")
    a = snap(END_AUDIO[0])
    n = round(END_DUR * FPS)
    fc = (f"[0:v]reverse,trim=end_frame=1,setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop={n - 1},"
          f"fps={FPS},setsar=1,format=yuv420p[v];"
          f"[1:a]aresample=48000,afade=t=in:d=0.04,afade=t=out:st={END_DUR - 0.6:.4f}:d=0.6[a]")
    run(["ffmpeg", "-v", "error", "-y", "-sseof", "-0.25", "-i", last_shot,
         "-ss", f"{a:.4f}", "-t", f"{n / FPS:.4f}", "-i", SRC,
         "-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-frames:v", str(n),
         "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
         *ENC_V, *ENC_A, out])
    return out


def final(base, caps, total, out_path):
    inputs = ["-reinit_filter", "0", "-i", base]
    for c in caps:
        inputs += ["-i", c["png"]]
    chain, prev = [], "[0:v]"
    for k, c in enumerate(caps):
        lbl = f"[c{k}]"
        chain.append(f"{prev}[{1 + k}:v]overlay=0:0:enable='between(t,{c['t0']:.4f},{c['t1']:.4f})'{lbl}")
        prev = lbl
    chain.append(f"{prev}noise=alls=3:allf=t,format=yuv420p[v]")
    afc = ["[0:a]highpass=f=90,afftdn=nr=6,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]"]
    fc = ";".join(chain + afc)
    run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", fc,
         "-map", "[v]", "-map", "[a]", "-t", f"{total:.4f}",
         "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-profile:v", "high",
         "-maxrate", "20M", "-bufsize", "40M", "-pix_fmt", "yuv420p", "-r", str(FPS),
         "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-movflags", "+faststart", out_path])


def main():
    os.makedirs(WORK, exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)
    parts, caps, t = [], [], 0.0
    for i, (a, b, crop, lines) in enumerate(SHOTS, 1):
        a, b = snap(a), snap(b)
        print(f"shot {i:02d} {crop} {a:.3f}-{b:.3f} -> out {t:.3f}", flush=True)
        parts.append(render_shot(i, a, b, crop))
        for k, (s0, s1, text) in enumerate(lines):
            png = os.path.join(WORK, f"cap{i:02d}_{k}.png")
            caption_png(text, png)
            t0 = t + max(snap(s0), a) - a
            t1 = t + min(snap(s1), b) - a
            caps.append({"png": png, "t0": t0, "t1": t1 - 0.001, "text": text})
        t += b - a
    end_start = t
    parts.append(end_freeze(parts[-1]))
    total = end_start + round(END_DUR * FPS) / FPS
    a0 = snap(END_AUDIO[0])
    for k, (s0, s1, text) in enumerate(END_CAPS):
        png = os.path.join(WORK, f"cap_end_{k}.png")
        caption_png(text, png)
        caps.append({"png": png, "t0": end_start + snap(s0) - a0, "t1": end_start + snap(s1) - a0, "text": text})
    png = os.path.join(WORK, "cap_end_text.png")
    caption_png(END_TEXT, png, centre_y=380)
    caps.append({"png": png, "t0": end_start, "t1": total, "text": END_TEXT})
    with open(os.path.join(WORK, "list.txt"), "w") as f:
        for p in parts:
            f.write(f"file '{p}'\n")
    base = os.path.join(WORK, "base.mov")
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(WORK, "list.txt"), "-c", "copy", base])
    json.dump({"end_start": end_start, "total": total, "caps": caps}, open(os.path.join(WORK, "timeline.json"), "w"), indent=1)
    print(f"freeze at {end_start:.3f}, total {total:.3f}", flush=True)
    final(base, caps, total, os.path.join(OUT_DIR, "papa-rua-barber-promo.mp4"))
    print("rendered captioned", flush=True)
    final(base, [], total, os.path.join(OUT_DIR, "papa-rua-barber-promo-clean.mp4"))
    print("rendered clean", flush=True)


if __name__ == "__main__":
    main()
