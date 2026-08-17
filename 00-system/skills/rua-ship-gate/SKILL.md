---
name: rua-ship-gate
description: >
  Use this skill when shipping or changing software in this repository
  (anything under 30-tools/, or a new tool). Trigger on implement, fix,
  ship, build, or change a tool. Compress intent, take the smallest safe
  path, write EXPERIENCE.md when a human holds the thing and DESIGN.md
  when Rua owns the pixels, treat an explicit fix/build request as
  one-shot approval, draft specs in chat, and do not call it shipped
  until the relevant command has run successfully. Do not use it for
  client sprints, pickup, sales, or founder-direction questions.
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

Session and look are part of this gate. They are not a separate
room or a named agent.

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

Name whether a human will hold the result, and whether Rua owns the
pixels. Inherit the host (Telegram, a CLI, a print page) unless this
change is the look.

### 2. Choose the smallest safe path

**One-shot** when all of these hold:

- one concern
- no new dependency
- no new public interface
- no new host, service, or chat surface
- the way a human runs the tool does not change
- the look does not change
- the goal fits in one sentence
- blast radius is local and the change is reversible
- the change is not destructive to data, credentials, or authentication

A small destructive or auth change is not a one-shot.
A silent change to pairing, waiting, voice, errors, or session-drop
on a living seat is not a one-shot.

**Spec path** otherwise. Draft the spec in chat. Do not write `spec.md`
until that draft is approved. After approval, persist it at
`30-tools/<tool>/spec.md`. Do not create a `specs/` directory at the
repository root.

A spec states: the goal, what is out of scope, what "done" looks like,
and how it will be observed (a command, a page, a file). Keep it short.

When a human holds the thing, the spec also names: who (often the
founder), the form-factor, the states that must have a plain
sentence, the moment they know it worked, and one thing not to
optimize. Persist the session contract at
`30-tools/<tool>/EXPERIENCE.md`. Shape:
`00-system/templates/experience.md`. Ask. Do not invent journeys,
microcopy, or states the product does not have.

When Rua owns the pixels, persist the look at
`30-tools/<tool>/DESIGN.md`. Shape: `00-system/templates/design.md`.
Tokens plus why each exists and where it is not used. Do not write
DESIGN.md for a host we inherit (Telegram chrome, a raw CLI, a
system font dump). Client-deck navy and purple are not brand law.

Skip both files when the change does not touch the session or the
look. html-to-pdf and a one-job renderer usually skip. A phone seat
does not.

If `EXPERIENCE.md` or `DESIGN.md` already exists, a change that
touches what they govern updates them in the same change. A file
nobody reads is dead. `spec.md` and the tool README must point at
the ones that exist.

### 3. Approval

- An explicit request to fix, build, implement, or ship a change that
  qualifies as a one-shot is the go-ahead. Do not ask for a second go.
- A spec, a session or look contract, a risky change, a new dependency
  or public interface, or any expansion of the agreed scope needs its
  own go after the draft is shown.

Do not write implementation files before the relevant go-ahead.

### 4. Implement against the approved goal or spec

Do not expand scope while writing. If the work reveals a second concern,
stop and return to step 1 for that concern.

Do not contradict `EXPERIENCE.md` or `DESIGN.md` in the code. If the
code must change the session or the look, change the file first.

### 5. Diagnose at the right layer

When the result is wrong, say which layer failed:

- **Intent:** the goal was the wrong thing
- **Spec:** the goal was right and the spec was weak
- **Experience:** the spec was right and the session or look was wrong
- **Implementation:** the contracts were right and the code missed them

Fix that layer. Do not patch a lower layer to compensate for a higher one.
Do not patch code to hide a missing state sentence.

### 6. Before it is shipped

- The exact relevant run, build, or test command from the tool's README
  or the approved spec has been executed in this session and succeeded.
  Report the command and the result.
- If a human holds the thing, walk the states in `EXPERIENCE.md`.
  A state with no sentence is not shipped.
- If Rua owns the pixels, the look in `DESIGN.md` is what shipped.
- If you could not run it, call the work **ready for verification**,
  name the command, and do not call it shipped.
- You have walked the two to five spots where being wrong costs the most.
- Incidental findings are listed and parked. They are not this change.

## Adapting

What changes: the tool, the commands in its README, how "run it" is
observed, and the session or look files when those apply.

What stays: the six steps, implementation files only after the relevant
go-ahead, layer diagnosis (including Experience when a human holds
it), an observed successful run before "shipped", and no third-party
method at the repository root unless the rewrite contract later
authorises it.
