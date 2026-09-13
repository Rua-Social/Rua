# Sales: the upstream commercial workflow

This is the Stage 0 boundary referenced by the sprint skill
(`00-system/skills/rua-shoot-plan/SKILL.md`): proposal, scoping and
invoicing sit here, upstream of any delivery workflow. It applies to any
bounded engagement Rua legitimately accepts, whatever shape it takes.

## The workflow

1. **Initial discussion and pre-commitment thinking.** Calls, research,
   direction-building and concept thinking may happen deliberately here.
   This is Rua choosing to command the problem before committing, not
   contracted production. Contracted production has not begun until the
   payment gate at step 4 is passed.

2. **Agree responsibilities, scope and commercial terms** using the
   scope-of-work template (`00-system/templates/scope-of-work.md`). The
   filled copy lives in that engagement's vault record with the brief.

3. **Invoice the required initial payment** under the terms stated in the
   scope of work.

4. **Payment gate.** Concept work may run ahead of payment to win
   commitment: proposals, concept decks and catch-ups are deliberate
   pre-commitment investment, not work to withhold out of fear the
   client will run the concepts alone. What the gate locks is the
   engagement itself: dates are held, crew and shoot days are booked,
   and production spend starts only when the required initial payment
   is received. If the initial payment goes quiet, chase it on a dated
   thread. It does not drift while the work continues.

5. **Create or activate the client engagement record** outside Git
   and retrieve it with `rua vault`. Use the folders the job needs.
   Do not force a six-phase sprint tree onto pickup or a tight package.

6. **Hand confirmed production into the appropriate delivery workflow.**
   For a defined Rua-led content sprint, that is the shoot-plan skill,
   which picks up from its Stage 1. If the scope is execution-only
   (pickup, shoot-only, edit-only, raw drop), do not run the sprint skill.
   Deliver against the scope.

7. **Record any scope change explicitly before the extra work happens**,
   per the exceptions section of the scope of work: agreed in writing with
   price and timeline impact stated.

8. **Complete delivery and collect the remaining payment** under the agreed
   terms.

### Job-shaped proposal

After a real conversation, Stage 0 may produce a job-shaped proposal: how
this engagement would run. It is optional. The generic offer, Week 0, the
concepts deck, and the scope of work remain separate objects.

If one is written:

- Label it a proposal, on the cover and in the footer.
- Carry the payment gate on the document. Dates are held only when the
  required initial payment is received.
- Keep anything that cannot be forwarded to the economic buyer out of the
  shareable file. Cover notes sit beside the pack, not in it.
- Days, if shown, are indicative. The scope names the deliverables.
- A starting list, if any, stays unlocked until the scope.
- When a job-shaped pack exists, the generic offer is the second
  attachment, and only if they ask.

If they go: fill the scope of work from the proposal. Production does not
start from the PDF. Then follow step 6.

The current working offer (three retainers plus a project) is
`ways-to-work.pdf`, built from `ways-to-work.html`. It is a leave-behind.
The one-page send is `pricing.pdf`, built from `pricing.html`. Same facts.
The room version is `ways-to-work-present.pptx`, a 16:9 present cut of
the same facts. After a number changes, rebuild with
`cd 20-studio/sales && npm install && npm run build`. It is not a rate card written into this workflow,
and it does not cover subcontract or pickup work. Change the numbers in
the HTML (`ways-to-work.html` and `pricing.html`) and reprint both
when the offer changes.

### Still open

Do not treat the present cut as finished infrastructure. It is one
worked example. Follow-up, in this order:

1. **The ask.** After an HTML deck is printed, if it will be walked in
   a room (this offer, Week 0, concepts), ask whether a 16:9 present
   cut is needed. Default no for schedule, shot list, and handover.
   The ask is not yet in `document-build.md` or the sprint stages.
2. **A second present cut** before any shared compiler. Week 0 or a
   concepts review is the trigger. Until then, copy facts by hand.
   `ways-to-work.html` and `ways-to-work-present.js` can drift. Change
   both when a number changes.
3. **Do not** flatten a PDF into slides. **Do not** add Drive upload
   until dragging the PPTX onto Drive is actually painful.

This README describes the workflow that exists. It is not a CRM, pipeline
tracker, proposal library or rate card. Add structure here only when
repeated friction earns it. Do not invent a commercial model for
subcontract work in this file.


### Sales preparation and review

When asked to prepare an ICP, messaging and outreach sequence, use the current
business direction in `20-studio/founder-context.md` and the supplied market
and prospect evidence. State the buyer, relevant need, supporting proof,
message, sequence and likely objections. Mark unsupported claims and unresolved
commercial choices for the founder. Apply `00-system/communication.md`.

When a sales team loop is explicitly requested, divide bounded work among
available workers: evidence and buyer fit, messaging and sequence, then review
of objections and unsupported claims. Use `00-system/working-roles.md` for
handoffs. Run a revision against returned findings. Stop when the requested
outputs are coherent and supported, or when a specific missing fact or founder
decision prevents completion. Report that dependency instead of cycling without
new evidence. If workers are unavailable, disclose that and do the supported
preparation directly. Sending outreach requires explicit authorization.
