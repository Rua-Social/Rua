---
name: rua-git-flow
description: >
  Use this skill for any change that will be committed to this repository.
  Trigger on commit, push, branch, merge, open a PR, or "ship this".
  Work on a branch, land through a pull request, keep main releasable.
  Applies to doctrine, client records, tools and studio files alike.
  Does not apply to a local scratch file that will never be committed.
---

# Git flow

How work reaches `main` in this repository.

Provisional. Overturn this file when the flow itself is wrong.

This is instruction-following on the client. The hard stops are the local
hook, when installed, and branch protection on the remote, which is on.
Setup is `00-system/git-setup.md`. If this file and the remote disagree,
the remote is correct.

Read `00-system/rewrite-contract.md` before adding a rule here.

## The rule

`main` is always releasable. Work happens on a branch. Branches land through
a pull request.

That is the whole rule. Everything below is threshold and mechanics.

## Threshold: when a branch is required

A branch and a PR are required when the change:

- touches more than one file, or
- changes a tool under `30-tools/`, or
- changes doctrine in `00-system/`, or
- was written mostly by a model rather than typed by the human.

That last one matters most. A model can produce a correct-looking fifteen-file
change in one turn. The PR is where that gets read before it becomes history.

Direct to `main` is fine for: a typo, a README line, a todo line, a date. If
you are unsure, branch. The cost of an unnecessary branch is thirty seconds.

## Branch names

`<type>/<short-slug>`

`feat/`, `fix/`, `docs/`, `chore/`, `refactor/`.

Slug is two to four words, hyphenated, describing the change and not the file.
`fix/desk-bridge-timeout`, not `fix/update-py`.

## Commits

Subject line in the imperative, under 72 characters. Body only when the change
needs a reason that the diff does not show.

No attribution trailers. No model names. No "generated with".

## The pull request

Body answers three questions. Two sentences each is plenty.

```
What changed
Why
How it was checked
```

"How it was checked" is not optional and "looks right" is not an answer. For a
tool, name the command that ran. For doctrine, name the rule in the rewrite
contract it complies with. For a client record, name the source of the facts.

Self-merge is fine. You are one person. The value is the diff review, not a
second signature.

## Issues

GitHub issues are for deferred repo work that is not a founder next-action.
The founder list is `20-studio/todo.md`, capped at seven by `rua-todo`. A
full list means close one. Do not park overflow as an issue.

If an issue exists for the work, close it from the PR body with `Closes #N`.

## What never lands

- Large media. See `AGENTS.md`, Media and Git.
- Secrets, tokens, client credentials, or a `.env` with real values.
- A client's personal data in a commit message.
- A generated `out/`, `dist/` or `frames/` directory.

## When the gate is wrong

If this flow is blocking real work, say so and change this file in a PR. Do not
route around it silently. A gate that gets bypassed without a record is worse
than no gate, because it stops describing what actually happens.
