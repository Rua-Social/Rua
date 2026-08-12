# Operating instructions for Claude in this repo

## What this repo is

The single monorepo for Rua: Rua Social / Rua Studio, client work, internal
tools, reusable skills, and Papa Rua. Large media, camera originals, exports,
and archive material live outside Git in Drive/local storage — this repo is
for structured knowledge, instructions, skills, and code.

## The core rule: build the minimum abstraction the work actually needs

Do not create agents, orchestration, model routing, or extra structure
because they might be useful eventually. Match the abstraction to what's
actually repeating:

- Repeated procedure → **Skill** (a `SKILL.md` under `00-system/skills/`)
- Deterministic functionality → **Tool** (a proper software project under
  `30-tools/`)
- Independently delegatable AI task → **Agent**
- Repeated handoff between multiple workers → **Orchestration**
- Different tasks demonstrably benefit from different models → **Model
  routing**

Do not create empty `agents/`, `orchestration/`, `models/`, `pipelines/`, or
`specs/` directories ahead of need. If you're about to propose one of these
and the trigger condition above isn't met yet, don't — flag the friction
instead and let the user decide when it's real.

## Founder and business intent

Before work on business direction, commercial model, positioning, growth,
prioritisation, hiring or outsourcing, or any decision where what Rua
optimises for changes the answer, read `20-studio/founder-context.md` first.
Do not assume conventional agency growth or revenue maximisation. Do not read
it for routine production, code or file tasks unless founder/business intent
materially affects the decision.

## When introducing something genuinely new

If you introduce a new Git convention, skill, agent, dependency, test, API,
or orchestration layer, briefly explain: what it is, why it's needed here,
and why the alternative would be worse. Skip this for routine filesystem
operations (moving a file, creating a normal directory) — only explain when
the concept itself is new.

## Structure

- `00-system/` — skills and templates that apply across the org
- `10-clients/<client>/` — one directory per client, phased subfolders
  (brief → research → plan → production → post → delivery)
- `20-studio/` — Rua Social / Rua Studio's own sales, marketing, operations,
  brand
- `30-tools/<tool>/` — deterministic software projects, each a normal
  buildable/runnable codebase with its own README
- `40-papa-rua/` — releases, content, live, business. Stays in this monorepo
  unless a concrete reason emerges (separate collaborators, permissions,
  deployment, or substantial independent development) to split it out
- `90-archive/` — completed or inactive material kept for reference

## Media and Git

Never commit large media (camera originals, renders, exports, masters).
`.gitignore` excludes common media extensions and build-output directories
(`out/`, `dist/`, `frames/`, etc.) by default. If a small reference asset
(e.g. a brand logo under a few hundred KB) genuinely belongs in the repo,
that's fine — just don't let it become the default.
