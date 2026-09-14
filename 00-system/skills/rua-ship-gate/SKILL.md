---
name: rua-ship-gate
description: >
  Use when implementing, fixing, building or shipping software in this
  repository. Carry an authorized request through proportionate planning,
  implementation and verification. Use short specs for complex changes and
  update experience or design contracts when affected.
---

# Software ship gate

Follow the user's requested scope and finish point. An explicit build or fix
request authorizes the ordinary reversible work needed to produce a concrete,
reviewable result. User instructions and existing authorization take precedence
over this skill. Read `AGENTS.md` and the rewrite contract when changing doctrine.

## 1. Establish the result

Identify the goal, what completion looks like and how to observe it. Resolve
routine choices from the brief. Ask only when missing information materially
changes the outcome or an action needs authorization. Continue independent work.

For a small, bounded change, the request and a brief implementation note suffice.
For a change with multiple interacting parts, a new interface or meaningful data
consequences, write a short `30-tools/<tool>/spec.md`: goal, relevant boundaries,
expected behaviour and verification. Writing a spec is authorized preparation;
it does not create a separate approval checkpoint.

## 2. Describe affected behaviour

When a change affects how a person uses the tool, create or update
`EXPERIENCE.md` in that tool using `00-system/templates/experience.md`.
Describe the user, actual and proposed states, useful messages and how they know
it worked. Label proposed behaviour clearly; do not describe it as already live.

When Rua controls and changes the visual design, create or update `DESIGN.md`
using `00-system/templates/design.md`. Inherited Telegram or CLI chrome does not
need a separate design document. Existing client-deck recipes are not brand law.

Keep these files proportionate and linked from the README or spec. Skip a new
contract when the change does not affect what it would describe. Update an
existing affected contract in the same change as the implementation.

## 3. Implement within authorization

Proceed with reversible implementation, necessary dependencies and interfaces
within the requested scope. Explain a new dependency or abstraction in terms of
the problem it solves and its material tradeoff. Follow environment permissions.

For a destructive or irreversible action, a material expansion of scope, or an
external action not already authorized, prepare the concrete result and ask for
the missing authorization before that action. A new spec, dependency, interface
or appearance alone does not require asking again. Keep unapproved proposals
separate from claims about deployed behaviour.

Carry authorized work to completion. Record incidental concerns without letting
them derail the request; address dependencies necessary to make the result work.

## 4. Diagnose and verify

Fix the layer responsible for a failure: the intended goal, the specification,
the user experience or the implementation. Keep documentation and code consistent.

Run the relevant build, test or command documented in the tool README or spec.
Choose checks that exercise changed behaviour and the places failure matters.
Walk affected user states and inspect changed visuals when applicable. Use
independent review in proportion to the consequences and the requested workflow.

After relevant checks pass, broaden or repeat them only when a new change,
failure or unresolved concern warrants it. Do not claim an unrun check passed.

## 5. Report the observed result

State what changed, why and how it was verified. Distinguish implemented, tested,
merged and deployed states. If execution is unavailable, say ready for verification
and identify the remaining check. Claim shipped only when the requested delivery
step and its relevant verification actually succeeded.
