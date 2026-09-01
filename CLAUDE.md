# Operating instructions for Claude in this repo

@AGENTS.md

The shared operating rules are imported above so Claude and Codex stay in
sync. Put anything that applies to both in `AGENTS.md`, not here. `AGENTS.md`
must remain in the repository: without it this file loses its shared
instructions. Everything below is Claude-specific.

If this is not a client job, name the class using `AGENTS.md` (Start of a
chat) and load only that class's doctrine.

## Load order for a job

1. What was sold, and has the payment gate been passed?
   (`20-studio/sales/README.md`, `00-system/templates/scope-of-work.md`)
2. Name the job-type. Defined Rua-led sprint, pickup / execution, or other.
3. If the human named an engagement, retrieve its record with
   `rua vault search` then `rua vault get`. Treat it as factual context,
   not a creative template and not a lead deck.
4. Load only the doctrine for that job-type. For a sprint, that is
   `00-system/skills/rua-shoot-plan/`. For pickup, do not load it.
5. Open a library artefact only if the human asked, or if doctrine does not
   cover the deliverable and the human agrees to look at a source.

If a cited path is missing, or the vault does not return a record, say so.
Do not reconstruct it from another client.

## Library

Named artefacts live in the vault. `00-system/reference-map.md` is a
pointer, not the catalogue. Do not read it as a source. Do not start a
job from it.

When the human asked to look up a deliverable type, or named an
engagement:

1. `rua vault search` then `rua vault get` for that record only.
2. Open the original artefact the record cites before borrowing from it.
3. If search or get fails, stop. Do not grep Git or mounted disks.

## Selecting precedent

- Select precedent by **deliverable type, workflow stage, audience and
  problem**, not by perceived similarity between clients.
- **Current discovery evidence overrides precedent.**
- **Compare several relevant artefacts** where appropriate rather than
  defaulting to the most prominent example.
- **Identify singletons as singletons.**
- **Never transfer commercial terms, client assumptions, voice, visual
  devices or creative concepts between clients** without current evidence.
- An instance record is **factual context, not a creative template**.

## Past styling versus current evidence

Recurring visual conventions in past documents are historical evidence, not
automatically Rua brand requirements. Do not infer intentional design rules
from recurrence alone. Current discovery, approved client assets and
explicit briefs take priority. `references/document-build.md` is a recipe.

## The map is not canon

A discrepancy between a vault record and a skill is not permission to
modify either. Change skill files, including `references/document-build.md`,
only when explicitly asked. The rewrite contract is
`00-system/rewrite-contract.md`.
