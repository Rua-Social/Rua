# 30-tools

Deterministic software projects — code, not AI agents. Each tool is a normal
buildable/runnable codebase in its own subdirectory with its own README and
dependency manifest. A tool may later be called by a skill or agent, but it
lives here as software first.

What exists today:

- `animation-renderer/` — one job's outro render.
- `html-to-pdf/` — print an HTML deck to A4 PDF with local Chrome.
- `desk-bridge/` — Telegram seat for the Rua desk. Phone in, Grok on this Mac out.

Changes to a tool, or a new tool, run `00-system/skills/rua-ship-gate/`.
A human session earns `EXPERIENCE.md`. Pixels Rua owns earn
`DESIGN.md`. Both are written in the `tools` room under the
ship gate.
