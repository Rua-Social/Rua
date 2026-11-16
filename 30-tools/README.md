# 30-tools

Deterministic software projects — code, not AI agents. Each tool is a normal
buildable/runnable codebase in its own subdirectory with its own README and
dependency manifest. A tool may later be called by a skill or agent, but it
lives here as software first.

What exists today:

- `animation-renderer/` — one job's outro render.
- `html-to-pdf/` — print an HTML deck to A4 PDF with local Chrome.
- `rua-desk/` — engine-neutral terminal front door for the Rua repository.
- `transcribe/` — shoot dialogue footage to transcripts for the edit-guide chat.
- `rua-vault/` — deliberate retrieval of one external client record.
- `rua-seat/` — run one other seat and print what they said. A mention is not a handoff.
- `rua-motion/` — local motion graphics studio. Renders branded overlays and title cards for Final Cut.
- [`storyboard/`](storyboard/README.md) — editable timed boards, portable project saves and video export. Source code lives here; project data and media are located through the engagement's vault record.

## Open the tools

Run `30-tools/install-apps.sh` once (and again after moving the repository).
It makes **Storyboard** and **Rua Motion** apps in `~/Applications/Rua`. Open
them from Spotlight or keep them in the Dock. Each starts its tool in the
background if needed and opens it in the browser. Logs go to
`~/Library/Logs/Rua/`.

Changes to a tool, or a new tool, run `00-system/skills/rua-ship-gate/`.
A human session earns `EXPERIENCE.md`. Pixels Rua owns earn
`DESIGN.md`. Both are written in the `tools` room under the
ship gate.
