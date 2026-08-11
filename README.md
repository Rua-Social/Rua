# Rua

Rua is the master organisation. This repository is the single Git monorepo
for everything structured under it: Rua Social / Rua Studio, client work,
internal tools, reusable AI skills, and Papa Rua.

Large media — camera originals, exports, renders, archive material — stays
out of Git, in Drive or local storage. This repo holds structured knowledge,
instructions, skills, and code.

## Structure

```
00-system/      Cross-cutting operating layer: skills, templates
10-clients/     Client work, one directory per client
20-studio/      Rua Social / Rua Studio itself: sales, marketing, ops, brand
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
- **CLAUDE.md** — operating instructions for Claude inside a given part of
  the repo
- **SKILL** — a reusable procedure/capability (e.g. `rua-shoot-plan`)
- **TOOL** — deterministic software/code (e.g. the animation renderer)
- **AGENT** — a bounded AI worker with a specific responsibility/context/tools
- **ORCHESTRATION** — coordination between multiple agents/processes
- **MODEL ROUTING** — choosing Claude/Gemini/GPT/Kimi for a specific task

See [CLAUDE.md](CLAUDE.md) for the rule on when each of these gets created.

## Status

This is a starting schema, not fixed architecture. Structure grows from real
friction, not anticipation — see CLAUDE.md.
