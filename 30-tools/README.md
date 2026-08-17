# 30-tools

Deterministic software projects — code, not AI agents. Each tool is a normal
buildable/runnable codebase in its own subdirectory with its own README and
dependency manifest. A tool may later be called by a skill or agent, but it
lives here as software first.

What exists today:

- `animation-renderer/` — one job's outro render.
- `html-to-pdf/` — print an HTML deck to A4 PDF with local Chrome.

Changes to a tool, or a new tool, run `00-system/skills/rua-ship-gate/`.
