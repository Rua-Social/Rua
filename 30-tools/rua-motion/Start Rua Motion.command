#!/bin/zsh
cd "$(dirname "$0")" || exit 1
if curl --silent --fail http://127.0.0.1:4317/api/projects >/dev/null; then
  open http://127.0.0.1:4317
  exit 0
fi
(sleep 2; open http://127.0.0.1:4317) &
npm run dev
