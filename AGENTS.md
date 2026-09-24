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

## How work moves

Carry the request through research, recommendations, execution and proportionate
review. Agents resolve reversible choices within the brief and bring material
creative or commercial decisions to the founder when they remain unresolved.
The active coordinator owns completion, including delegated work and the final
answer. Role ownership lives in `00-system/working-roles.md`; read it before
dividing work. Any capable model can fill a role.

## Working rules

Read `00-system/communication.md` for replies, copy and reviews.
User instructions take precedence over skill guidelines. Carry forward scope,
choices and authorization from the conversation. A request to create, fix or
implement authorizes the ordinary work needed to complete it. Prepare the
concrete result before asking for any remaining approval. Ask only when missing
information materially changes the outcome or an action needs authorization.
Continue independent work while that answer is pending.

Infer the job class from available context. Ask only when uncertainty affects
the work. Use the requested deliverable and finish point; a skill's full workflow
does not require extra deliverables. An explicit review-only request permits
inspection and findings, with no file writes, implementation or commits.

For current Gmail, Calendar or Drive facts, use the connected Workspace tools.
Discover available tools before declaring access unavailable. Prefer those tools
to Mac Mail or Calendar. Local notes can provide context but cannot establish
current mailbox or calendar state. If a tool fails, report the attempted lookup
and the gap. Desk or Telegram access must be verified in the current environment;
a past working connection is not proof of present access. Sending messages needs
explicit authorization; a lookup or draft request does not provide it.

Report actions as completed only when a tool result confirms completion. Label
proposals, attempts, pending work and unknown facts accurately. Verify changes
in proportion to their consequences; stop repeating checks once relevant checks
pass unless new evidence warrants more work. Delegate bounded independent work
when it can save time or improve quality and tools support it. Claim
independent review only after another reviewer has actually returned findings.

For a requested review, use `00-system/skills/rua-review/SKILL.md`.
For a studio status extraction, use `00-system/status-extraction.md`.
For a pickup memo, use `00-system/templates/pickup-memo.md`.

## Start of a chat

Infer the class before loading doctrine. Keep internal routing out of the reply
unless it helps explain a material scope decision.

- **Client job:** load order in `00-system/rewrite-contract.md`.
  Doctrine for a defined sprint is `00-system/skills/rua-shoot-plan/`.
  A concept push calls `rua-creative-direction` lane A from inside the
  sprint and returns there. Pickup uses the scope of work. Do not load
  the sprint skill.
- **Cinematic film:** `00-system/skills/rua-treatment/`. Treatment, script,
  storyboard, or visual aid, and only the stage he asked for. A pressure
  pass calls `rua-creative-direction` lane B from inside this skill and
  returns here. Do not load the sprint skill to produce it.
- **Tool / software:** `00-system/skills/rua-ship-gate/`.
- **Sales:** `20-studio/sales/README.md` and
  `00-system/templates/scope-of-work.md`. No delivery skill.
- **Founder / direction:** `20-studio/founder-context.md`.
- **Founder todo:** `20-studio/todo.md` and
  `00-system/skills/rua-todo/`. Not `lists.md`.
- **Other:** use the stated scope; ask if a material boundary remains unclear.

If the class remains unclear and changes the deliverable, ask. Do not start a
sprint document or a tool change to invent the job.

## Three rooms

Reusable instruction and named work are not the same thing.

- **Doctrine** (`00-system/skills/`, `00-system/templates/`,
  `00-system/rewrite-contract.md`): portable method. No living client names,
  fees, people, venues, proof points, or "next client."
- **Instance**: named facts about one engagement live outside Git.
  Load only through `rua vault search` then `rua vault get` when that
  engagement is the job. `10-clients/` is a marker, not a record.
- **Library** (`00-system/reference-map.md`):
  a pointer. Named artefacts live in the vault. Consult on purpose
  through `rua vault`. Never default context for a production chat.

The founder record (`20-studio/founder-context.md`) is read for business,
hiring, pricing philosophy or music-direction questions. It is not read to
plan a shoot, write a deck, or cut an interview.

How to write doctrine: `00-system/rewrite-contract.md`.

## Current file

When the engagement's instance record has a file index, that index names the current file. Offload is scratch. Scratch and an older dated copy are not current when the index names a different file.

A refinement or update writes the new current version into the working location that index already names. Rewrite the file index so it names the new version. Keep the previous current file and take it off the current list. Move that previous set out of the working location and keep it on the same job. If the instance record names a place for earlier versions, use that place. Otherwise use one earlier-versions folder outside the working location. The working location then holds only the files the index lists as current. A new offload folder is not the working location for that deliverable.

When the index lists more than one form of the same deliverable as current, update those forms together.

The working location named in the instance record is where that deliverable is written. The capture-only note in `20-studio/storage.md` does not move it.

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
and what tradeoff matters for this task. Skip this for routine filesystem
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
