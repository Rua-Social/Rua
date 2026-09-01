---
name: rua-shoot-plan
description: >
  Use this skill for a defined Rua-led content sprint: research through shoot to
  handover. Trigger on shoot plan, concepts deck, schedule, shot list, pre-production
  reissue, delivery ledger, or handover for a sprint that has been scoped and gated.
  Do not use it for pickup, shoot-only, edit-only, or any job where Rua is executing
  a supplied concept. Confirm job-type before loading the stages.
---

# Defined Rua-led content sprint

This skill runs one job-type: a defined sprint Rua originates and leads. The client
brings the business need and the last yes. Rua owns the creative response and the
production of a defined body of work with a clear finish.

It is not the default for every Rua job. If the scope is pickup, shoot-only,
edit-only, or another bounded package, stop. Use the scope of work. Do not run
these stages.

Read this file fully before producing a document. Discussion first. The document
is the output second. Wait for an explicit go-ahead before building.

Read `00-system/rewrite-contract.md` if you are about to add a rule, an example,
or a name.

---

## House style (client-facing and skill text)

- No em dashes. Use commas, brackets, colons, or restructure.
- No "it's not X, it's Y" construction, in any variant. State what something is.
- No third-person references to the client inside the client's own document.
  Address them directly.
- No staccato fragments.
- No marketing jargon. Write like a smart person talking to another smart person.
- Post copy is pulled from real lines in the footage. Where there is no good line
  yet, leave a placeholder. Never invent a quote and attribute it to a person.
- Caption length, editorial taboos, and tone laws come from this client's brief
  and research, not from a previous job.

When reviewing a draft, fix machine-writing tells without being asked: double
full stops, hedging filler, formulaic openers, and the constructions above.

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

Confirm, from the human or from `10-clients/<slug>/`:

- The job-type is a defined Rua-led sprint.
- Responsibilities, finish point and commercial terms are agreed.
- The payment gate in `20-studio/sales/README.md` has been passed, or the human
  has explicitly said this is still pre-commitment thinking and no date is held.

If a job-shaped proposal exists for this engagement, read it as sales intent.
A starting list, if any, enters as an alignment list (Stage 2b) and is
green-lit or killed at Stage 3. Research still runs. Week 0 is still the
first delivery document after the gate.

If those are unclear, ask. Do not start a Week 0 deck to invent a sprint.

Cutting, grade and per-asset edit guides are outside this skill. Do not hand off
to a skill that is not in this repository. When the footage is in, take the
human's instruction for how the cuts will be made. Then come back here for the
ledger and the handover.

The default ingest from footage to edit guide: put the dialogue selects in a
folder per shoot day or block and run `30-tools/transcribe/` on it, with a
`--prompt` sentence built from this client's names, brands and venues. B-roll
and exteriors are not transcribed. The SRT files go into the edit-guide chat
with the concepts deck. Model choice and options live in the tool's README.
Mapping lines to concepts and choosing takes stays a human chat step;
transcription is the deterministic part.

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

Come out with an agreed list. Wait for an explicit go-ahead before building
the deck.

### Stage 4, Concepts deck and iteration

Build the concepts deck. Read `references/concept-development.md` and
`references/document-build.md`.

The concepts deck is the single source of truth for the sprint. One page per
concept, a copy bank with no gaps, a change log before sign-off.

Multiple dated iterations are normal. The latest dated file is canonical.
Iteration can happen async.

### Stage 5, Pre-production and the reissue loop

A pre-production call locks logistics and the schedule shape. It almost always
also surfaces creative changes. Those do not get patched into the schedule.

Creative changes flow back through the concepts deck first. Read
`references/reissue-protocol.md`.

Issue a simple staff release template to the client here, so it is ready
before the schedule goes out.

### Stage 6, Schedule and shot list

Both derive from the latest concepts deck. Client-facing schedule: block cards,
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
   location, next. Stage 8.

Build instructions for HTML decks are in `references/document-build.md`.
That file is a recipe. Approved client assets beat it.

---

## Document hierarchy and the reissue rule

- The concepts deck is the single source of truth.
- The schedule is derived from the concepts deck.
- The shot list is derived from the schedule.

Any creative change after the concepts deck is approved flows into a new dated
concepts iteration first, and only then rebuilds the schedule and shot list.
Never patch a creative correction into the schedule directly.

---

## Versioning, change log, concept numbering

**Versioning.** Ship a new dated file. Do not overwrite. Pattern:
`[client]_[doctype]_[mmmYYYY]` or `[client]_[doctype]_[ddmmyy]` for same-month
reissues. The latest dated file is canonical.

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

There is no creative library in this repository. Do not invent one. Do not
read `90-archive/skills/rua-shoot-plan-2026-06/` unless the human asks for
the historical extraction.
