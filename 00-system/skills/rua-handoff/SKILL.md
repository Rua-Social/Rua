---
name: rua-handoff
description: >
  Delegate a bounded task to another Rua seat and use its returned result.
  Trigger on hand off, delegate, ask the PA, or work that benefits from an
  independent reader, maker, checker or factual reviewer.
---

# Handoff

Read `00-system/working-roles.md` for role ownership. The coordinator keeps
responsibility for the request and final answer while another worker runs.

State the objective, relevant sources, accepted decisions, authorized actions,
owned paths and expected result. Keep client details in the authorized external
record; share only the context needed for this task. Tell workers about concurrent
work and give each path one writer, or use isolated worktrees.

The executable is `rua-seat`. Its binding, supported invocation and handoff
mechanics are documented in `30-tools/rua-seat/README.md`.

```sh
rua-seat reader "research the supplied source and return cited findings"
rua-seat maker "draft the requested artefact within the agreed brief"
rua-seat checker "review the draft against the current brief and house style"
```

Use the requested role. If the command is unavailable, inspect the README and
available tools; do not silently substitute another role or assume a particular
harness is installed. Native collaboration tools may handle bounded delegation
when available, using the same responsibility and evidence requirements.

Wait for the actual result before claiming that the handoff or review completed.
Report a failed or timed-out run accurately. Continue independent work where
possible. A further attempt needs a reason to expect progress; repeated failure
should surface the specific gap instead of an unbounded retry loop.

Synthesize useful findings into the final answer, retaining sources and material
uncertainty. Do not paste raw worker output by default. Reconcile disagreements
against the evidence; agreement between independent reviewers is valid.

Verify a named disk or path before reporting it unavailable. Client lookup uses
`rua vault search` then `rua vault get`; try alternate transcriptions when needed.
Lookup and draft requests do not authorize sending, booking or deleting. Existing
explicit authorization carries through the handoff.
