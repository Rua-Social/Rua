#!/bin/sh
# Run the documented tests for tools that have them.
# animation-renderer has no test command and is not listed.
set -e
root=$(git rev-parse --show-toplevel)
echo "check-tools: html-to-pdf" >&2
python3 -m unittest discover -s "$root/30-tools/html-to-pdf" -p 'test_*.py'
echo "check-tools: desk-bridge" >&2
python3 "$root/30-tools/desk-bridge/test_bridge.py"
echo "check-tools: rua-desk" >&2
python3 -m unittest discover -s "$root/30-tools/rua-desk" -p 'test_*.py'
echo "check-tools: rua-vault" >&2
python3 -m unittest discover -s "$root/30-tools/rua-vault" -p 'test_*.py'
echo "check-tools: ok" >&2
