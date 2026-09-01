# Rewrite contract

How reusable Rua instructions are written. Binding on every model.

This exists because the first sprint skill was a memoir of one job installed as org law. That
conflicted with rules already in this repository: keep reusable material separate from client
inputs, identify singletons as singletons, and never transfer terms, voice or devices between
clients without current evidence.

## Three rooms

**Doctrine** (`00-system/skills/`, `00-system/templates/`, this file)  
Portable method. Loaded for a matching job-type.

**Instance** (external vault via `rua vault`)  
Named facts about one engagement. Loaded only when that engagement is the job.

**Library** (`00-system/reference-map.md`)  
A pointer. Named artefacts live in the vault. Consulted on purpose through
`rua vault`. Never default context for a production chat.

**Founder record** (`20-studio/founder-context.md`)  
Read for business, hiring, pricing philosophy, music-direction questions. Not read to plan
a shoot, write a deck, or cut an interview.

## Banned in doctrine

- Living client or prospect names
- Fees, rates, invoices, proof points, lead-deck angles
- People, venues, rooms, products, or channel handles from a real job
- "The reference set," "the next client," or any named sequel
- Required reading of a file that does not exist
- A caption-length law, an editorial taboo, or a page count, unless classified below as
  every-job
- Commercial terms copied from one job as the price of the next

If a method cannot be stated without a proper noun, the method is not ready. Go back to the
human. Do not open the library to finish the sentence.

## Allowed in doctrine

Roles (the owner, the operator, the regular, the decision-maker). Job-types. Checklists.
Document hierarchy. Payment and scope rules that apply to every engagement. Build recipes
labelled as recipes.

A worked example, if any, lives in `90-archive/` or in that client's vault
record. It is not loaded unless the human asks to see how one job ran.

## Job-types

Before loading a delivery skill, name the job-type from the scope:

1. **Defined Rua-led job** (often a content sprint). Client brings the need and the last
   yes. Rua owns the creative response and a defined body of work with a finish.
2. **Pickup / execution.** Client and often the concept arrive ready-made. Finish is files.
   Do not run the sprint skill.
3. **Other.** Interview package, stills, barter, edit-only, or anything the scope names.
   Use the scope. Do not force the sprint spine.

Internal software under `30-tools/` is not a client job-type. Use
`00-system/skills/rua-ship-gate/`. Do not run the sprint skill.

Do not invent a rate card or a subcontract commercial model in these files.

## Load order for a job chat

1. What was sold, and has the payment gate been passed?
2. Job-type.
3. This client's instance record, if `rua vault search` finds it.
4. Doctrine for that job-type only.
5. A library artefact only if the human asked, or if doctrine does not cover the
   deliverable and the human agrees to open a source.
6. If a cited path is missing, stop and say so. Do not reconstruct it from another client.

## Classification applied 14 August 2026

Provisional. Overturn any mark in a later session.

### Every job

- Dates are held only after the required initial payment.
- Current evidence about this client beats precedent.
- Do not transfer commercial terms, voice, visual devices or creative concepts.
- Do not invent a quote and attribute it to a person.
- Extras are a new written agreement with price and time stated first.
- Client owns talent, access and venue prep. Flag once. Do not build a chasing apparatus.
- Missing path: report it. Do not invent the source.
- Copy written on the founder's behalf: no em dashes.
- Client-facing prose: no "it's not X, it's Y"; no staccato fragments; no marketing jargon;
  address the client in their own document; do not talk about them in the third person
  inside that document.

### This kind of job (defined Rua-led sprint)

- Research is generative. Ingest their own channel history when it exists. Flag thin
  history instead of skipping the read.
- Lenses: format versus reward, category, baseline not peaks, outliers named as outliers,
  paid or assisted stripped from the organic read, tone, frequency.
- Week 0 is the first document touchpoint.
- An early alignment list between Week 0 and greenlight is allowed. Its job is agreement,
  not specification.
- Greenlight: categorise live, kill freely, log every kill.
- Concepts deck is the source of truth. Schedule is derived. Shot list is derived.
- Creative change after approval goes back through the concepts deck, then derived docs.
- Order concepts by who must be there, lightest first.
- Types: standalone, mini-series, recurring, asset bank, sub-concepts.
- Treatment pages use the anatomy in `concept-development.md`.
- A references block (named analogue, the device it proves, verified against source) is
  allowed and undocumented in the old skill. Use it when it helps.
- Copy bank covers every concept. Placeholders where the line will only come from footage.
- Change log. Concept numbers are permanent. Killed numbers stay retired.
- Release forms issued at pre-production, not on the day.
- When a floor was sold: state floor, landed, and upside separately. Never fold upside
  into landed.
- Pending items carry a plain reason.
- Single shoot day is the default. More days only if scoped and paid.
- The HTML/PDF recipe in `document-build.md` is available. It is not a brand constitution.
  Approved client assets beat the recipe.

### One job only (stays in archive / instance)

- Any living client name, person, venue, pillar set, like-count, or "next client"
- Six-word captions as law
- No politics / no religion as a standing rule for every interview
- A nine-page people / place / voices handover as the required shape
- A 90-minute greenlight, a two-day shoot, or a specific surplus of delivered assets
- Required reading of `creative-library.md` or a `reel-edit-guide` skill

### Delete from live doctrine

- Pointers that assume those two files exist
- "Gold-standard" filenames that are not in this repository
- Any instruction to mirror a named deck rather than follow the method

## Rejection tests

A doctrine draft fails if it contains:

- a real client, prospect, or talent name
- a real fee or proof point
- "reference set" or a named sequel
- a required file that is not in the tree
- a caption-length or editorial-taboo law marked one-job-only above
- a mandatory nine-page handover
- navy and purple presented as Rua brand law

Search-replace on the archived memoir is a failed draft. Write new text.

## What this contract does not authorise

Agents, orchestration, model routing, a CRM, a marketing directory, a pickup rate card,
a music-video service line, moving the machine-local library into Git, or installing a
third-party method (agent roster, `_bmad/`, or equivalent) at the repository root.
