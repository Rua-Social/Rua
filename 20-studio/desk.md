# The Rua desk

Use the harness that has the capabilities the task needs. The shared contract
is `AGENTS.md`, with role ownership in `00-system/working-roles.md`. The active
coordinator carries the request to completion across any delegated work.

## Entry points and capability checks

- `rua-desk` selects an installed desktop harness. Usage and status checks:
  `30-tools/rua-desk/README.md`.
- `rua-seat` invokes a role through its configured runner. Binding and handoff
  mechanics: `30-tools/rua-seat/README.md`.
- `rua vault` retrieves authorized named client records. Usage:
  `30-tools/rua-vault/README.md`.

Discover connected tools and inspect current status before making access claims.
Installed software, an old successful session or a shared launcher does not prove
that another harness has the same tools or conversation. Current Gmail, Calendar
and Drive facts come from connected Workspace tools. Local notes supply context.

Provider and model choices belong in runner configuration. Choose them from
current availability and task needs. Add a tool, integration or coordination
mechanism when repeated friction justifies it, using the proportionality rule in
`AGENTS.md`. A repository shares instructions and artefacts; execution results
still need an actual handoff and return.

## Context and continuity

Infer the job class and load its relevant doctrine. Keep named client facts and
large exports outside Git, accessed through the vault and referenced storage.
Carry the objective, accepted decisions, authorization, owned paths and unfinished
work when changing seats. Follow `00-system/skills/rua-handoff/SKILL.md`.

Parallel workers need separate path ownership or worktrees. The coordinator
reconciles their results and writes one answer appropriate to the request.

## Phone replies

Verify the live Telegram gateway and its available tools before using it. The
archived desk bridge is historical code and is not an instruction to start it.
Changing this document does not deploy or reconfigure the live phone runtime.

Treat a transcribed voice note as the ask. Infer whether it requests an action,
an idea capture, brainstorming, intake or a lookup. Do not turn every thought
into a todo. Follow the action-record rules in `00-system/skills/rua-todo/`.

Apply `00-system/communication.md`. Keep file-hunting, role routing and internal
process off-screen. Send a short result: what happened, where the useful output
is and any essential next step. Use ordinary paragraphs; omit tables, file trees
and raw worker transcripts unless the user requests them. When a file was actually
sent, say it is in the chat. Preserve material uncertainty without a studio log.

Examples of the intended shape, only when the underlying action is verified:

- "Added it to your list for Friday."
- "The draft is attached. The opening uses your interview line; the final call to
  action still needs your choice."
- "The calendar lookup failed, so I couldn't verify that time. The draft is ready."

## History

Earlier model experiments, incidents and operating prescriptions are preserved
in `90-archive/desk-operating-note-20260914.md`. Consult that record for a specific
historical question; current capability checks and shared instructions govern work.
