# Rua

Rua is the master organisation. This repository is the single Git monorepo
for everything structured under it: Rua Social / Rua Studio, client work,
internal tools, reusable AI skills, and Papa Rua.

Large media — camera originals, exports, renders, archive material — stays
out of Git, in Drive or local storage. This repo holds structured knowledge,
instructions, skills, and code.

## Structure

```
00-system/      Doctrine, templates, rewrite contract, library index
10-clients/     Marker only. Named records are retrieved with rua vault
20-studio/      Founder context, sales workflow, and desk note
30-tools/       Deterministic software projects (e.g. animation-renderer)
40-papa-rua/    Papa Rua releases, content, live, business
90-archive/     Completed / inactive material kept for reference
```

Each numbered directory and most subdirectories have their own `README.md`
explaining what belongs there.

## Vocabulary

These terms are used consistently across this repo:

- **PROJECT** — a bounded thing being built or operated (a client campaign,
  a tool, a release)
- **REPOSITORY** — this Git-tracked home for the organisation's projects
- **README** — explains what something is, how it's structured, how to use it
- **AGENTS.md** — shared operating instructions for every model
- **CLAUDE.md** — Claude-specific load order and library rules
- **SKILL** — a reusable procedure (e.g. `rua-shoot-plan`, `rua-ship-gate`)
- **TOOL** — deterministic software/code (e.g. the animation renderer)
- **DOCTRINE** — portable method, no living client names
- **INSTANCE** — named facts about one engagement
- **LIBRARY** — index of real artefacts, most of them outside Git
- **AGENT** — a bounded AI worker (not created ahead of need)
- **ORCHESTRATION** — coordination between multiple agents (not created
  ahead of need)
- **MODEL ROUTING** — choosing a model for a specific task (not created
  ahead of need)

See [AGENTS.md](AGENTS.md) for the rule on when each of these gets created.
See [00-system/rewrite-contract.md](00-system/rewrite-contract.md) for how
doctrine is written.

## Status

This is a starting schema, not fixed architecture. Structure grows from real
friction, not anticipation.
