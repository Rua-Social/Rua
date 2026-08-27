# rua-desk

## Goal

Running `rua-desk` in a terminal opens an engine-neutral chooser and
launches the selected AI harness from the Rua repository. The repository,
`AGENTS.md`, skills, and files on disk are the desk; no harness is the desk
itself.

## Out of scope

- Model routing or an `auto` mode for interactive terminal work.
- A shared session across harnesses.
- Making harness-specific features available in every harness.
- New agents, orchestration, APIs, dependencies, or graphical surfaces.
- Changing the Telegram desk-bridge engine selection.

## Done

- Bare `rua-desk` presents Claude, Codex, Grok, Gemini, and Kimi Code as
  selectable seats when attached to a terminal.
- Direct commands remain available: `claude`, `codex`, `grok`, `gemini`,
  `kimi`, and Grok's `grok-one` single-session mode.
- `status`, `card`, `ping`, and `help` remain available.
- Every harness starts with the Rua repository as its working directory.
- A missing harness, missing repository, invalid selection, and unknown
  command each produce a plain, actionable sentence.
- The versioned launcher lives in this project and the installed
  `~/.local/bin/rua-desk` resolves to it.
- `20-studio/desk.md` describes the repository as the desk and separates
  shared behaviour from harness-specific behaviour.

## Observe

```sh
python3 -m unittest discover -s 30-tools/rua-desk -p 'test_*.py'
30-tools/rua-desk/rua-desk status
readlink ~/.local/bin/rua-desk
```

Then run bare `rua-desk`, choose an installed seat, and confirm its opening
message names `/Users/darraghhoare/Rua` before the harness takes over.
