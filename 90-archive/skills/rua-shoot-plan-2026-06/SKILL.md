---
name: rua-shoot-plan
description: >
  Use this skill to run a Rua Social content sprint end to end: from research intake, through the
  shoot, to delivery and handover. Triggers when the user mentions building a shoot plan, content
  plan, concepts deck, schedule, shot list, sprint plan, pre-production reissue, delivery ledger, or
  handover for a client. Also triggers on phrases like "let's plan the shoot", "build the concepts
  deck", "build the schedule", "reissue after the pre-pro call", "reconcile the delivery", or "start a
  sprint for [client]". Use it for any single stage as well as the full run. Per-asset edit guides and
  the master transcript cut are produced by the reel-edit-guide skill. This skill hands off to it at
  delivery and owns the delivery ledger and the handover.
---

# Rua Social, Content Sprint Skill

This skill runs a full content sprint for Rua Social, from the first read of a client's social
history to the handover document that closes the job out. It is built from the Skehans Free House
sprint, which is the worked example throughout. Skehans is the reference set. New clients (Fitzpatricks
Castle next) run the same spine against their own material.

Read this file fully before doing anything. Do not produce a document or summarise concepts until the
user gives an explicit go-ahead. Discussion runs first, the document is the output second.

---

## House style

These rules apply to every client-facing document and to the skill files themselves. They are not
suggestions.

- No em dashes anywhere. Use commas, brackets, colons, or restructure the sentence.
- No "it's not X, it's Y" construction, in any variant. State what something is, plainly.
- No third-person references to the client inside the client's own document. Address them directly.
- No staccato fragments (short period-fragmented sentences run together for effect).
- No marketing jargon or corporate phrasing. Write like a smart person talking to another smart person.
- Post captions are six words or fewer.
- Post copy is pulled from real lines in the footage, not written to a formula. Where there is no good
  line yet, leave a clear placeholder rather than inventing one.
- Expletives in footage and transcripts are not a problem and are not flagged.
- Standing editorial rule across all interview concepts: no politics, no religion. Anything that
  strays into either is flagged for client review before it goes near a publish decision.

When reviewing any draft, catch and fix the usual machine-writing tells without being asked: double
full stops, hedging filler, formulaic openers, and the constructions above.

---

## Terminology

Use these terms. They are the ones the client and the work are built on.

- Sprint, for the whole engagement. Not "blitz".
- Mini-series, for an episodic arc across multiple posts.
- Sub-concepts, for variations inside a single concept.
- Recurring, for a format that repeats over time.
- The View, as the only term for the space above the pub. It is named that for privacy.

---

## The sprint spine

Eight stages. They map to how the work actually runs, not to a tidy theory. A sprint can pause at any
stage, and the user may ask for one stage in isolation. Hold the order regardless: each stage assumes
the one before it is settled.

### Stage 0, Commercial (boundary, not covered here)

Proposal, scoping, and invoicing sit upstream in their own workflow. This skill starts once the
engagement is agreed. Do not fold proposals or pricing into sprint documents.

### Stage 1, Research and the concept long-list

Solo desk work. Ingest six months of the client's social history. This is mandatory. For a client with
little or no posting history, flag the gap and pull from whatever exists (competitor accounts, the
category, any brief material), but do not skip the read.

Read `references/research-analysis.md` for how to approach it and what to look for.

Come out of the analysis with two things: a findings summary, and a rough concept long-list that the
research has generated. The long-list is your own working material at this point. There is no kick-off
session and no second person in this stage. Concepts get worked properly with the client at Stage 3.

### Stage 2, Week 0 deck and presentation

Build the Week 0 deck and present it to the client. This is the first client touchpoint that carries a
document. It shows them you have studied their account, sets out what is working and what is missing,
and frames the creative direction. The Week 0 deck is built here, at the front, not bundled into a
later build stage.

Present, take the client's reaction, and move on. The rough concept territory can be aired here, but
the concept list is not locked until Stage 3.

### Stage 3, Concept review and greenlight

The working call with the client. Concepts are categorised live: green-lit, mini-series, recurring or
asset bank, or killed. This is where concepts are worked collaboratively, the client steers hard, and
weak ideas get cut.

Run it well:
- Send a pre-read 24 to 48 hours ahead so the client arrives with opinions.
- Keep the call tight. Target 90 minutes. The first Skehans greenlight ran close to two hours, which
  is the thing to improve on, not repeat.
- Kill anything that does not work and replace it with something that does.
- Log every kill in conversation so it carries into the deck change log later.

Come out with an agreed concept list. Say so clearly and wait for an explicit go-ahead before building.

### Stage 4, Concepts deck and iteration cycles

Build the concepts deck. Read `references/concept-development.md` for concept types, tier logic, and
the anatomy of a full treatment, and `references/document-build.md` for the design system and page
structure.

The concepts deck is the single source of truth for the sprint. One page per concept, copy bank
covering every asset with no gaps, change log before the sign-off.

Expect multiple iterations. Skehans ran four dated versions (March, April, May, and a 25 May reissue
off the back of pre-production). Multiple iterations are normal, not a sign of drift. The latest dated
file is canonical. Iteration can happen async between calls, not only in meetings.

### Stage 5, Pre-production and the reissue loop

Before the shoot, a pre-production call locks the day's logistics and the schedule shape. It almost
always also surfaces creative changes: refined questions, swapped or added talent, named locations,
copy adjustments. These do not get patched straight into the schedule.

Creative changes flow back through the concepts deck first. Read `references/reissue-protocol.md` for
the full loop. In short: pre-pro call, then audit the changes against the current concepts deck, then
a new dated concepts iteration, then the schedule, then the shot list. The schedule is derived from the
concepts deck and is never the home for a creative correction.

Release forms are adopted at this stage. Issue the simple staff release template to the client here, so
it is ready before the schedule goes out rather than scrambled for later.

### Stage 6, Schedule and shot list

Both documents derive from the latest concepts deck. Build the client-facing schedule (block cards,
amber flag boxes, consolidated action list, question sets for sharing with talent) and the internal
shot list (capture reference by block, conservative floor count). Read `references/document-build.md`
for both.

Talent, venue preparation, and on-shoot logistics are the client's to own. Surface them once: as flag
boxes in the schedule and a short named-subjects list sent alongside it. Do not build a chasing
apparatus around them. If a named subject does not materialise on the day, the concept runs with
whoever is available or it drops, and the drop goes in the change log. Hold the line lightly, not with
a countdown.

### Stage 7, Shoot

Single day is the default. Multi-day is budget-dependent and used when scope or travel warrants it
(Skehans ran two days). Day 2 and any later day run as solo pickup: B-roll bank, exteriors, and
anything that did not land on Day 1. No client coordination is needed on a solo pickup day.

### Stage 8, Delivery and closeout

Per-asset edit guides and the master transcript cut are produced with the **reel-edit-guide** skill,
not here. Switch to that skill for the cutting once the footage is in.

Once the cuts exist, come back to this skill for the two delivery artifacts: the delivery ledger and
the handover. Read `references/delivery-closeout.md`. The handover opens with the ledger (conservative
floor planned, what landed, and the upside if masters get clipped into individual assets), then what
was made, the status of anything still waiting on client input, suggested copy lifted from the footage,
and where it all lives plus what comes next.

---

## The deliverables

Six documents across the sprint, in three groups. Each has a different audience. Do not collapse them
into each other.

**Planning, client-facing:**
1. **Week 0 deck.** Research and direction. HTML built in the house style, exported to PDF. Stage 2.
2. **Concepts deck.** Creative treatments, copy bank, change log. HTML to PDF. The single source of
   truth. Stage 4.
3. **Shoot schedule.** Block-by-block day plan, flag boxes, action list, question sets. HTML to PDF.
   Stage 6.

**Planning, internal (Darragh only):**
4. **Shot list.** Capture reference by block, equipment and audio notes, capture summary, conservative
   floor. Markdown. The client never sees it. Stage 6.

**Pre-production utility:**
5. **Release form template.** Simple staff permission form, issued to the client at pre-production.
   Stage 5.

**Delivery, client-facing:**
6. **Handover.** Opens with the delivery ledger, then the made assets, pending items, suggested copy,
   and where it lives plus what is next. HTML to PDF. Stage 8.

Full build instructions, CSS, and page structure for every document are in
`references/document-build.md`. Delivery-specific structure is in `references/delivery-closeout.md`.

---

## Document hierarchy and the reissue rule

The order of authority is fixed:

- The concepts deck is the single source of truth.
- The schedule is derived from the concepts deck.
- The shot list is derived from the schedule.

Any creative change that arrives after the concepts deck is approved (most often from the
pre-production call) flows back into a new dated concepts iteration first, and only then rebuilds the
schedule and shot list. Never patch a creative correction into the schedule directly. This is the one
rule the pre-production stage exists to protect. The full audit flow is in
`references/reissue-protocol.md`.

---

## Versioning, change log, concept numbering

**Versioning.** Decks iterate. The latest dated file is canonical. Filename pattern is
`[client]_[doctype]_[mmmYYYY].html` or `[client]_[doctype]_[ddmmyy].html` for same-month reissues
(for example `skehans_concepts_april2026.html`, then `skehans_concepts_250526.html`). Ship a new dated
file rather than overwriting the previous one.

**Change log.** Every concepts deck and schedule deck carries a change log section near the end, before
the sign-off. Each entry has a date, the concept number or numbers affected, and one line on what
changed and why.

**Concept numbering.** Concepts keep their number for the life of the project. If concept 009 is
killed, the slot is retired, not reused. Later concepts keep their numbers (010 and 011 do not slide
down). The change log records the kill: "26 March: Concept 009 killed (reason). No replacement." A
later replacement idea takes the next free number, never the retired one. This keeps cross-references
in shot lists, schedules, and conversation stable.

---

## The reel-edit-guide boundary

This skill owns planning, the shoot, and delivery reconciliation (the ledger and the handover). It does
not own the cutting. Per-asset edit guides and the master transcript cut are the reel-edit-guide
skill's job. At Stage 8, hand off to reel-edit-guide for the edits, then return here for the ledger and
handover. Keep the boundary clean so neither skill duplicates the other.

---

## Adapting across clients

What changes per client: the research inputs, the people available and their comfort on camera, the
relevant pillars (a pub differs from a hotel or a gym), the number of assets and document scale, the
copy voice (match what is good, lift what is flat), and whether the shoot is single or multi-day.

What stays the same: the eight-stage spine, the six deliverables, the house style and terminology, the
Rua Social design system, the tier logic (order concepts by who needs to be there), the copy bank in
the concepts deck, the change log and concept-numbering conventions, the document hierarchy and the
reissue rule, talent and logistics sitting with the client, and the principle that research drives the
concepts.

---

## Reference files

- `references/research-analysis.md`, how to read six months of social history and what to pull from it.
- `references/concept-development.md`, concept types, tier logic, pillar thinking, full treatment
  anatomy.
- `references/document-build.md`, the full Rua Social design system, CSS for every document type, page
  components, and PDF conversion.
- `references/reissue-protocol.md`, the pre-production controlled-change loop and the release form.
- `references/delivery-closeout.md`, the delivery ledger and the handover structure.
- `references/creative-library.md`, approved case-study entries from completed sprints (worked, did not
  work, corrected). Read during Stage 1 and Stage 4. New entries require Darragh's explicit sign-off
  before they are written, so do not add to this file unprompted.

---

## Worked example: the Skehans sprint

The real cadence, for reference when pacing a new client:

- Solo research read of six months of the Skehans Instagram, ahead of any call.
- 23 March, Day 0 with the client: research presented (video beats static, roughly a 200-like
  baseline, music treated as an unplanned outlier, multi-day shoot first raised). The Week 0 deck.
- 26 March, greenlight call (ran close to two hours): concepts categorised, Reluctant Landlord killed,
  Memorabilia Walk added, pint competition and the Telegraph Hill exterior bank locked, food cut from
  ten dishes to six. First concepts deck out of this.
- April and May: further concepts iterations, partly async between calls.
- 12 May, pre-production: logistics and schedule locked, The View named, mandatory release forms
  adopted, Julius and Chai questions refined. This triggered the reissue: new concepts, then schedule,
  then shot list (the 25 May set).
- 29 to 30 May, two-day shoot, Day 2 as solo pickup.
- June, delivery: per-asset edit guides and the master cut produced via reel-edit-guide, then the
  delivery ledger and the nine-page handover produced here.

The corresponding files, as gold-standard examples to mirror rather than re-derive from the style
brief alone:

- `skehans_week0.html`, Week 0 deck (Stage 2).
- `skehans_concepts_250526.html`, concepts deck, final iteration (Stage 4).
- `skehans_schedule_250526.html`, shoot schedule (Stage 6).
- `skehans_shot_list_250526.md`, shot list (Stage 6).
- `skehans_handover_jun2026.html`, handover (Stage 8).
