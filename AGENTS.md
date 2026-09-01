# Operating instructions for every model in this repo

## What this repo is

The single monorepo for Rua: Rua Social / Rua Studio, client work, internal
tools, reusable skills, and Papa Rua. Large media, camera originals, exports,
and archive material live outside Git in Drive/local storage. This repo is
for structured knowledge, instructions, skills, and code.

## The core rule: build the minimum abstraction the work actually needs

Do not create agents, orchestration, model routing, or extra structure
because they might be useful eventually. Match the abstraction to what is
actually repeating:

- Repeated procedure → **Skill** (a `SKILL.md` under `00-system/skills/`)
- Deterministic functionality → **Tool** (a proper software project under
  `30-tools/`)
- Independently delegatable AI task → **Agent**
- Repeated handoff between multiple workers → **Orchestration**
- Different tasks demonstrably benefit from different models → **Model
  routing**

Do not create empty `agents/`, `orchestration/`, `models/`, `pipelines/`, or
`specs/` directories ahead of need. If you are about to propose one of these
and the trigger condition above is not met yet, do not. Flag the friction
instead and let the user decide when it is real.

This is an evidence and proportionality principle, not a preference for
nothing being built. Do not use it to protect a memoir of one job sitting
in a skill file. Do not use it to block a proportionate improvement that
is genuinely justified.

## Start of a chat

Name the class before loading doctrine.

- **Client job:** load order in `00-system/rewrite-contract.md`.
  Doctrine for a defined sprint is `00-system/skills/rua-shoot-plan/`.
  Pickup uses the scope of work. Do not load the sprint skill.
- **Tool / software:** `00-system/skills/rua-ship-gate/`.
- **Sales:** `20-studio/sales/README.md` and
  `00-system/templates/scope-of-work.md`. No delivery skill.
- **Founder / direction:** `20-studio/founder-context.md`.
- **Founder todo:** `20-studio/todo.md` and
  `00-system/skills/rua-todo/`. Not `lists.md`.
- **Other:** ask. Do not invent a class.

If the class is unclear, ask. Do not start a sprint document or a
tool change to invent the job.

## Three rooms

Reusable instruction and named work are not the same thing.

- **Doctrine** (`00-system/skills/`, `00-system/templates/`,
  `00-system/rewrite-contract.md`): portable method. No living client names,
  fees, people, venues, proof points, or "next client."
- **Instance**: named facts about one engagement live outside Git.
  Load only through `rua vault search` then `rua vault get` when that
  engagement is the job. `10-clients/` is a marker, not a record.
- **Library** (`00-system/reference-map.md`, `00-system/reference-audit/`):
  an index of real artefacts, most of them outside Git. Consult on purpose.
  Never default context for a production chat.

The founder record (`20-studio/founder-context.md`) is read for business,
hiring, pricing philosophy or music-direction questions. It is not read to
plan a shoot, write a deck, or cut an interview.

How to write doctrine: `00-system/rewrite-contract.md`.

## Founder and business intent

Before work on business direction, commercial model, positioning, growth,
prioritisation, hiring or outsourcing, or any decision where what Rua
optimises for changes the answer, read `20-studio/founder-context.md` first.
Do not assume conventional agency growth or revenue maximisation. Do not
read it for routine production, code or file tasks unless founder/business
intent materially affects the decision.

Rua encounters at least two kinds of work: defined Rua-led jobs, and
pickup / execution where the client and often the concept come from
elsewhere. The scope-of-work template covers both. The sprint skill covers
only the first. Do not invent a commercial model or rate card for the
second in these files.

## When introducing something genuinely new

If you introduce a new Git convention, skill, agent, dependency, test, API,
or orchestration layer, briefly explain: what it is, why it is needed here,
and why the alternative would be worse. Skip this for routine filesystem
operations. Only explain when the concept itself is new.

## Git

`main` is always releasable. Work happens on a branch and lands through a pull
request. Doctrine is `00-system/skills/rua-git-flow/`.

Branch when the change touches more than one file, changes a tool or doctrine,
or was written mostly by a model. Direct to `main` is for a typo or a date.

The remote requires a pull request onto `main`. Admins are included. If this
file and the remote disagree, the remote is correct.

Pre-cleanup Git history is not in this repository. It is a vault
artefact. See `00-system/git-history.md`.

## Structure

- `00-system/` — skills, templates, rewrite contract, library index
- `10-clients/` — marker only. Live client records are external and
  opened through `rua vault`
- `20-studio/` — Rua Social / Rua Studio itself. What exists today: founder
  context, the sales workflow, and the desk note
- `30-tools/<tool>/` — deterministic software projects, each a normal
  buildable/runnable codebase with its own README
- `40-papa-rua/` — releases, content, live, business. Stays in this
  monorepo unless a concrete reason emerges to split it out
- `90-archive/` — completed or inactive material kept for reference

## Media and Git

Never commit large media (camera originals, renders, exports, masters).
`.gitignore` excludes common media extensions and build-output directories
(`out/`, `dist/`, `frames/`, etc.) by default. If a small reference asset
(e.g. a brand logo under a few hundred KB) genuinely belongs in the repo,
that is fine. Do not let it become the default.
