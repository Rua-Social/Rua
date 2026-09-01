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

If a cited path is missing, report that. Do not reconstruct it from another
client or from a map description.

## The reference map

`00-system/reference-map.md` is a library index of past documents. Most of
the sources it cites are machine-local and outside Git. It is not a design
canon and it is not how a job starts.

Do not read it in full by default. Do not import it here. Do not start
ordinary client work at Part D.

When the human is asking about the library, or has agreed you may look up a
deliverable type:

1. Check whether an exact-client instance record exists via `rua vault`.
   Read it only when it matches the current client.
2. Use Part D of the map to find candidate artefacts.
3. Read the relevant Part A or B record.
4. Open the original cited artefact before relying on or borrowing from it.

**Open the original before borrowing from it.** The map describes what a
document does and where it sits. Never reproduce wording, a structure or a
component solely from the map's description.

If a cited path no longer resolves, report that instead of reconstructing
the source from the map.

Supporting evidence for how the map was built lives in
`00-system/reference-audit/2026-08-14/`.

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

Some cited sources have no usable text layer and must be rendered to page
images rather than text-extracted. The map identifies these sources
individually.

## The map is evidence, not canon

A discrepancy between the map and a skill is not permission to modify
either. Change skill files, including `references/document-build.md`, only
when explicitly asked. The rewrite contract is `00-system/rewrite-contract.md`.
