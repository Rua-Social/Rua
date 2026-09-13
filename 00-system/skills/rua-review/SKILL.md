---
name: rua-review
description: Review Rua files or drafts without changes, with cited findings and a verdict. Use for independent review, read-only review, or a requested pre-commit assessment.
---

# Review

Establish the requested material, criteria and output limit from the conversation.
Read the relevant source files and diff. Inspect only the material needed to
assess the request. Do not write files, implement fixes, commit, or run commands
that generate artifacts during a read-only review. A later explicit request to
implement changes ends that boundary for the newly authorized work.

Check correctness and the user's requirements first. For prose, use
`00-system/communication.md` and the current brief. Cite each actionable finding
to a file and line, or a precise passage in a document. Explain the consequence
and the smallest useful correction. Distinguish a defect from a preference.

Use the requested word or bullet limit; otherwise keep findings concise. Lead
with the verdict, then findings in consequence order. If no actionable findings
remain, say so and name any material verification gap. Do not invent issues to
fill a quota. A read-only inspection does not establish that unrun tests pass.

An independent review requires a separate reviewer who has actually inspected
the material. If acting as that reviewer, return findings to the requester. If
reviewing your own work, label it as self-review. Do not claim another reviewer
ran merely because a role or agent was proposed.
