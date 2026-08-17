---
name: rua-ship-gate
description: >
  Use this skill when shipping or changing software in this repository
  (anything under 30-tools/, or a new tool). Trigger on implement, fix,
  ship, build, or change a tool. Compress intent, take the smallest safe
  path, treat an explicit fix/build request as one-shot approval, draft
  specs in chat, and do not call it shipped until the relevant command
  has run successfully. Do not use it for client sprints, pickup, sales,
  or founder-direction questions.
---

# Software ship gate

Quality gate for code in this repository. Discussion first.
Implementation files second.

Provisional. Overturn this file when the gate itself is wrong.

This is instruction-following, not a hard stop. A harness may still
write files if tool approval is set to always-allow. Use Ask or Plan
mode when you want the product to block.

Read `00-system/rewrite-contract.md` if you are about to add a rule,
an example, or a name. That contract does not authorise installing a
third-party method, agent roster, or extra output tree at the
repository root. Do not add one to satisfy this skill.

## When this applies

- Changing an existing project under `30-tools/`
- Adding a new tool under `30-tools/`
- Any other software change in this repository that will be run or shipped

If the work is a defined Rua-led sprint, stop. Use `rua-shoot-plan`.
If the work is pickup or another client package, use the scope of work.
If the work is sales, use `20-studio/sales/README.md`.

## The gate

### 1. Compress intent

Restate the request as one goal. Name anything that is out of scope.
If a second project is hiding in the request, split it and do one.

### 2. Choose the smallest safe path

**One-shot** when all of these hold:

- one concern
- no new dependency
- no new public interface
- no new host, service, or chat surface
- the way a human runs the tool does not change
- the goal fits in one sentence
- blast radius is local and the change is reversible
- the change is not destructive to data, credentials, or authentication

A small destructive or auth change is not a one-shot.

**Spec path** otherwise. Draft the spec in chat. Do not write `spec.md`
until that draft is approved. After approval, persist it at
`30-tools/<tool>/spec.md`. Do not create a `specs/` directory at the
repository root.

A spec states: the goal, what is out of scope, what "done" looks like,
and how it will be observed (a command, a page, a file). Keep it short.

### 3. Approval

- An explicit request to fix, build, implement, or ship a change that
  qualifies as a one-shot is the go-ahead. Do not ask for a second go.
- A spec, a risky change, a new dependency or public interface, or any
  expansion of the agreed scope needs its own go after the draft is
  shown.

Do not write implementation files before the relevant go-ahead.

### 4. Implement against the approved goal or spec

Do not expand scope while writing. If the work reveals a second concern,
stop and return to step 1 for that concern.

### 5. Diagnose at the right layer

When the result is wrong, say which layer failed:

- **Intent:** the goal was the wrong thing
- **Spec:** the goal was right and the spec was weak
- **Implementation:** the spec was right and the code missed it

Fix that layer. Do not patch a lower layer to compensate for a higher one.

### 6. Before it is shipped

- The exact relevant run, build, or test command from the tool's README
  or the approved spec has been executed in this session and succeeded.
  Report the command and the result.
- If you could not run it, call the work **ready for verification**,
  name the command, and do not call it shipped.
- You have walked the two to five spots where being wrong costs the most.
- Incidental findings are listed and parked. They are not this change.

## Adapting

What changes: the tool, the commands in its README, how "run it" is
observed.

What stays: the six steps, implementation files only after the relevant
go-ahead, layer diagnosis, an observed successful run before "shipped",
and no third-party method at the repository root unless the rewrite
contract later authorises it.
