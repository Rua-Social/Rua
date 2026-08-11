#!/usr/bin/env bash
set -euo pipefail

# Pull settings out of params.js so there's one source of truth
FPS=$(node -p "require('./params.js').fps")
GRAIN=$(node -p "require('./params.js').grain")

mkdir -p out

if [ "$GRAIN" -gt 0 ]; then
  # Grain is added here rather than baked into the PNGs. It dithers the
  # gradient so 8-bit banding doesn't survive into the platform re-encode.
  VF="noise=alls=${GRAIN}:allf=t+u"
else
  VF="null"
fi

# Rec.709 tagging on every output. Without this FCP can guess wrong and
# your cyan shifts.
TAG="-color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv"

echo "==> ProRes 422 HQ master"
ffmpeg -y -framerate "$FPS" -i frames/frame_%05d.png \
  -vf "$VF" \
  -c:v prores_ks -profile:v 3 -pix_fmt yuv422p10le \
  $TAG \
  out/ecoplex-outro_ProResHQ.mov

echo "==> H.264 review copy"
ffmpeg -y -framerate "$FPS" -i frames/frame_%05d.png \
  -vf "$VF" \
  -c:v libx264 -crf 16 -preset slow -pix_fmt yuv420p \
  $TAG -movflags +faststart \
  out/ecoplex-outro_h264.mp4

echo
echo "Done:"
ls -lh out/
echo
echo "ProRes goes in the FCP timeline. H.264 is for sending round for approval."
