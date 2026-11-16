#!/bin/zsh
# Make double-clickable Mac apps for Rua's local tools, in ~/Applications/Rua.
# Each app starts its tool in the background if needed and opens it in the browser.
# Safe to run again after moving the repository or updating Node/Python.
set -euo pipefail

TOOLS="${0:A:h}"
DEST="${RUA_APPS_DIR:-$HOME/Applications/Rua}"
PYTHON="$(command -v python3)"
NODE_DIR="$(dirname "$(command -v node)")"
LOGS="$HOME/Library/Logs/Rua"
mkdir -p "$DEST" "$LOGS"

make_app() {
  local name="$1" shell_command="$2"
  local escaped="${shell_command//\\/\\\\}"
  escaped="${escaped//\"/\\\"}"
  rm -rf "$DEST/$name.app"
  osacompile -o "$DEST/$name.app" \
    -e "try" \
    -e "do shell script \"$escaped\"" \
    -e "on error errText" \
    -e "display alert \"$name could not open\" message errText" \
    -e "end try"
  echo "Made $DEST/$name.app"
}

make_app "Storyboard" \
  "'$PYTHON' '$TOOLS/storyboard/storyboard.py' open >> '$LOGS/storyboard-open.log' 2>&1 || (tail -1 '$LOGS/storyboard-open.log' >&2; exit 1)"

make_app "Rua Motion" \
  "export PATH='$NODE_DIR':/opt/homebrew/bin:/usr/bin:/bin; \
if ! curl -sf http://127.0.0.1:4317/api/projects >/dev/null; then \
cd '$TOOLS/rua-motion' && nohup npm run dev >> '$LOGS/rua-motion.log' 2>&1 & \
for i in {1..50}; do curl -sf http://127.0.0.1:4317/api/projects >/dev/null && break; sleep 0.2; done; fi; \
curl -sf http://127.0.0.1:4317/api/projects >/dev/null || { echo 'Rua Motion did not start. See $LOGS/rua-motion.log' >&2; exit 1; }; \
open http://127.0.0.1:4317"

echo "Open them from Spotlight (Cmd+Space, type the name) or drag them from $DEST into the Dock."
