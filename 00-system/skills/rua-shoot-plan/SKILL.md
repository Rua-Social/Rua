---
name: rua-shoot-plan
description: >
  Use this skill for a defined Rua-led content sprint: research through shoot to
  handover. Trigger on shoot plan, concepts deck, schedule, shot list, pre-production
  reissue, coming home from a shoot, delivery ledger, or handover for a sprint that
  has been scoped and gated. Do not use it for pickup, shoot-only, edit-only, or any
  job where Rua is executing a supplied concept. Confirm job-type before loading the
  stages. Ingest (folder of dialogue selects to local SRTs) still runs on pickup
  via `30-tools/transcribe/`; this skill is not required for that step.
---

# Defined Rua-led content sprint

This skill runs one job-type: a defined sprint Rua originates and leads. The client
brings the business need and the last yes. Rua owns the creative response and the
production of a defined body of work with a clear finish.

It is not the default for every Rua job. If the scope is pickup, shoot-only,
edit-only, or another bounded package, stop. Use the scope of work. Do not run
these stages.

Read this file fully before producing a document. Use the conversation to
establish the requested output. A request to build or update it supplies the
go-ahead; do not ask for the same approval again.

Read `00-system/rewrite-contract.md` if you are about to add a rule, an example,
or a name.

---

## House style (client-facing and skill text)

Read `00-system/communication.md` and apply the current client's brief.
Post copy comes from real footage lines. Leave a placeholder where no good line
exists; never invent a quote or transfer another client's editorial rules.

---

## Terminology

- **Sprint**, for this whole engagement.
- **Mini-series**, for an episodic arc across multiple posts.
- **Sub-concepts**, for variations inside a single concept.
- **Recurring**, for a format that repeats over time.

Do not import venue nicknames or client vocabulary from another job. Use the
words this client uses.

---

## Before Stage 1

Confirm, from the human or from `rua vault` for this engagement:

- The job-type is a defined Rua-led sprint.
- Responsibilities, finish point and commercial terms are agreed.
- The payment gate in `20-studio/sales/README.md` has been passed, or the human
  has explicitly said this is still pre-commitment thinking and no date is held.

If a job-shaped proposal exists for this engagement, read it as sales intent.
A starting list, if any, enters as an alignment list (Stage 2b) and is
green-lit or killed at Stage 3. Research still runs. Week 0 is still the
first delivery document after the gate.

If those are unclear, ask. Do not start a Week 0 deck to invent a sprint.

Cutting sits in `reel-edit-guide`, after Stage 7b has SRTs on disk.
The handover sits in Stage 8, after the cuts exist. Do not merge those
two documents. Do not open `reel-edit-guide` to skip ingest.

---

## The sprint path

A default path, not a moral spine. A sprint can pause at any stage. The human
may ask for one stage in isolation. Hold the order unless they override it:
each stage assumes the one before it is settled.

### Stage 0, Commercial (boundary)

Proposal, scoping and invoicing sit in `20-studio/sales/` and
`00-system/templates/scope-of-work.md`. This skill starts once the engagement
is agreed. Do not fold proposals or pricing into sprint documents.

### Stage 1, Research and the concept long-list

Solo desk work. Ingest the client's own recent social history. This is
mandatory when history exists. For thin or missing history, flag the gap and
pull from whatever exists (category, competitors, the brief). Do not skip the
read and jump to ideas.

When the instance or brief has a channel handle, run a channel pull before
you write findings. Instagram is the first automated pull: last six months
via xpoz. Other channels use the same file shape when a pull exists for
them. Read `references/research-analysis.md`.

A findings summary that claims to have read an account, with no pull file,
is a failed Stage 1. If xpoz fails, still write the file and mark `gap`.
Do not invent posts, counts, or a format split from memory.

Come out with two things: a findings summary, and a rough concept long-list.
The long-list is working material. Concepts are worked with the client at
Stage 3.

A push on those ideas, or a critique of concepts already written, calls
`rua-creative-direction` lane A and returns here. Findings come first. The
pass does not open the film skill, and it does not run before the findings
exist unless he explicitly skips the read.

### Stage 2, Week 0 deck and presentation

The first client touchpoint that carries a document. It shows you have studied
their account, sets out what is working and what is missing, and frames a
direction. Build it here, at the front.

Present, take the reaction, and move on. Rough concept territory can be aired.
The list is not locked until Stage 3.

### Stage 2b, Alignment list (optional)

An early concept list sent to get buy-in before the greenlight call. Purpose is
agreement, not specification. Use it when the gap between Week 0 and greenlight
is long, when the client needs to arrive already oriented, or when a
job-shaped proposal already carried a starting list. Do not treat it as the
concepts deck.

### Stage 3, Concept review and greenlight

The working call. Concepts are categorised live: green-lit, mini-series,
recurring or asset bank, or killed. The client steers. Weak ideas get cut.

Run it well:

- Send a pre-read 24 to 48 hours ahead so they arrive with opinions. Skip the
  pre-read only if the human says this client must see the work live first.
- Keep the call tight. If it starts to sprawl, park remaining items rather
  than exhausting the room.
- Kill anything that does not work and replace it with something that does.
- Log every kill so it carries into the change log.

Come out with an agreed list. Build the deck when requested; carry forward any go-ahead already given.

### Stage 4, Concepts deck and iteration

Build the concepts deck. Read `references/concept-development.md` and
`references/document-build.md`.

The concepts deck is the single source of truth for the sprint. One page per
concept, a copy bank with no gaps, a change log before sign-off.

Multiple dated iterations are normal. The current file is the one the
instance file index names. Follow Current file in `AGENTS.md`.
Iteration can happen async.

### Stage 5, Pre-production and the reissue loop

A pre-production call locks logistics and the schedule shape. It almost always
also surfaces creative changes. Record them against the approved concepts.

Creative changes normally flow through the concepts deck first. The schedule-only
exception below applies when the human chooses it. Read
`references/reissue-protocol.md`.

Issue a simple staff release template to the client here, so it is ready
before the schedule goes out.

### Stage 6, Schedule and shot list

Use the concepts deck the instance file index names as current. When the human requests schedule-only
hygiene without a new deck, skip Stage 4 and use the last approved concepts plus
the current brief. Record the sources and any authorized changes in the schedule
change log. Do not invent missing creative decisions; ask only about details that
block an accurate schedule. Produce only the requested outputs.

Client-facing schedule: block cards,
flag boxes, consolidated action list, question sets for talent. Internal shot
list: capture reference by block, conservative floor. The client never sees
the shot list.

Talent, venue preparation and on-shoot logistics are the client's to own.
Surface them once. If a named subject does not materialise, the concept runs
with whoever is available or it drops, and the drop goes in the change log.

### Stage 7, Shoot

Single day is the default. More days only when the scope and the price say so.
Later days, if scoped, run as solo pickup: B-roll, exteriors, anything that
did not land. No client coordination is required on a solo pickup day.

### Stage 7b, Coming home (ingest)

The unit of work is the dialogue-selects folder for that day or block.
This is the automation that is in place. Transcription is deterministic.
Mapping is not.

1. Name the folder. One shoot day or block. Not one clip. Not a slice of
   a long interview. If the folder is missing, ask. Do not substitute.
2. Run `30-tools/transcribe/` on that folder. Local mlx-whisper,
   `whisper-large-v3`. `--fast` is scout-only and does not feed a guide.
   Do not send shoot dialogue to a cloud STT. Skip AppleDouble `._` files.
3. `--prompt` is one sentence of this client's names, brands and venues.
   B-roll and exteriors stay out of the folder.
4. Write the SRT set to the vault offload for this job. Never Desktop.
   Never Git.
5. Stop. Put the SRT set in the chat with the latest concepts deck.
   Mapping lines to concepts, choosing takes, and writing the edit guide
   is the next human step. `reel-edit-guide` starts there.

Forbidden: picking the smallest clip to prove Whisper works; writing a
deck or PDF before the folder has SRTs; treating an export still as
ingest when the camera original exists; folding the SRT dump into a
handover.

### Stage 8, Delivery and closeout

After the cuts exist, build the delivery ledger and the handover. Read
`references/delivery-closeout.md`.

If a floor was sold, the handover opens with floor, landed, and upside as
separate numbers. Then what was made, anything still waiting on the client,
suggested copy lifted from the footage, where it lives, and what is next.

Match the handover to what was sold. A light handover (caption, tag, location)
is correct when that is the finish. Do not pad it into a nine-page narrative
because a previous sprint used one.

---

## The deliverables

Six documents across a full sprint, in three groups. Do not collapse them into
each other. A paused or narrower sprint may stop before all six exist.

**Planning, client-facing**

1. **Week 0 deck.** Research and direction. Stage 2.
2. **Concepts deck.** Treatments, copy bank, change log. Source of truth.
   Stage 4.
3. **Shoot schedule.** Block-by-block day plan, flags, action list, questions.
   Stage 6.

**Planning, internal**

4. **Shot list.** Capture reference, equipment, audio, conservative floor.
   Markdown. Stage 6.

**Pre-production utility**

5. **Release form template.** Issued at Stage 5.

**Delivery, client-facing**

6. **Handover.** Ledger if a floor was sold, made assets, pending items, copy,
   location, next. Stage 8. Built after the cuts exist.

The edit guide is an internal cut list. It is not one of these six. It is
owned by `reel-edit-guide`, after Stage 7b. Do not ship it to the client
as if it were the handover.

Build instructions for HTML decks are in `references/document-build.md`.
That file is a recipe. Approved client assets beat it.

---

## Document hierarchy and the reissue rule

- The concepts deck is the single source of truth.
- The schedule derives from approved concepts, with the current brief supplying
  authorized changes for an explicit schedule-only update.
- The shot list is derived from the schedule.

Creative changes normally enter a dated concepts iteration before the schedule
and shot list are rebuilt. For an explicit schedule-only request, the last
approved concepts and current brief govern the update. Record each authorized
change and its source in the schedule; do not silently treat the old deck as
updated. This exception does not authorize new creative decisions.

---

## Versioning, change log, concept numbering

**Versioning.** Follow Current file in `AGENTS.md`. The current file is the
one the instance file index names. A refinement writes the new current set
into the working location that index already names, rewrites the index so it
names that set, and keeps the previous file. The previous file is no longer
listed as current. Move it out of the working location. If the instance
record names a place for earlier versions, use that place. Otherwise use one
earlier-versions folder outside the working location. Forms the index lists
together for one deliverable move together. A refinement does not create a new offload folder for that
deliverable. Before the pass is finished, run `rua vault current REF`.
Exit 0 means the working location and the `current` block agree. Any other
exit means the pass is not finished. Pattern:
`[client]_[doctype]_[mmmYYYY]` or `[client]_[doctype]_[ddmmyy]` for same-month
reissues. Stage 7b still writes the SRT set to the vault offload for this job.

**Change log.** Every concepts deck and schedule carries one near the end,
before sign-off. Date, concept number or numbers, one line on what changed
and why.

**Concept numbering.** Numbers last for the life of the project. A killed
number is retired, not reused. A later replacement takes the next free
number. This keeps shot lists, schedules and conversation stable.

---

## Adapting

What changes: the research inputs, who will go on camera and how comfortable
they are, the pillars this research produces, document scale, copy voice
(match what is good, lift what is flat), and whether the shoot is one day
or more.

What stays: the path above, the six deliverable types when the sprint is
run in full, the hierarchy and reissue rule, the channel-pull gate at
Stage 1, tier logic, copy bank, change log and numbering, talent and
logistics sitting with the client, research driving concepts.

What does not stay: another client's pillars, editorial taboos, caption
laws, surplus, page count, or look.

---

## Reference files

- `references/research-analysis.md`
- `references/concept-development.md`
- `references/document-build.md` (recipe, not a brand system)
- `references/reissue-protocol.md`
- `references/delivery-closeout.md`

There is no creative library in this repository. Do not invent one. A craft
pass uses `rua-creative-direction` and returns here. Outside skills are a
shelf, not a second sprint. Do not read
`90-archive/skills/rua-shoot-plan-2026-06/` unless the human asks for the
historical extraction.
