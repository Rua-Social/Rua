# rua-seat

Run one other Rua seat with a deadline and a durable result. A mention in chat
is not a handoff. This uses the configured runtime; it does not replace its
session, inference or tool implementation.

```sh
rua-seat pa "what is new in the inbox"
rua-seat --structured --json reader "digest this source and cite the evidence"
```

Seats: desk, pa, reader, maker, checker, flags.

## Binding

No runner ships by default. The binding is per-machine configuration, not
doctrine; the doctrine is: the other role actually ran and returned. Set
`RUA_SEAT_RUNNER`, a shell-like template that must include `{ask}`:

```sh
export RUA_SEAT_RUNNER='codex exec --sandbox read-only {ask}'
rua-seat pa "what is new in the inbox"
```

Other installed harnesses take a plain prompt the same way, e.g. `claude -p
{ask}`, `gemini -p {ask}`, `grok -p {ask}`. Each has its own sandbox,
approval and permission flags (`codex exec`'s default sandbox is
`workspace-write`, not read-only); put the ones a seat needs directly in its
template. A read-only binding can answer for `reader` or `checker` but
cannot fill `maker`, which has to write.

Include `{seat}` too when the runner has a native profile or session concept
to bind to:

```sh
export RUA_SEAT_RUNNER='other-runner --profile rua-{seat} --prompt {ask}'
```

`{ask}` is required and must occupy exactly one argument; `{seat}` is
optional. Either way, the seat's role, scope and source pointers travel in
the prompt itself (see `role_preamble` in `rua-seat`), so no runner-side
profile is assumed — every seat currently shares the one configured runner
and its credentials. The runner is invoked as an argument array, never
through a shell, with stdin closed so a runner that otherwise waits on piped
input cannot hang the call. Adapters must preserve the inherited
`RUA_HANDOFF_*` environment for nested work.

## Shared handoff record

Every invocation records its job ID, parent/root IDs, owner, request, timestamps,
status, bounded stdout/stderr and optional validated result. Storage defaults to
`${XDG_STATE_HOME:-~/.local/state}/rua/handoffs/jobs.sqlite3`. Override its directory
with `RUA_HANDOFF_DIR`. The directory and database must be owner-only and outside
Git. The record can contain private task inputs and output; do not commit or
publish it. Records are retained until deliberately removed by the operator.

This is the portable handoff record, not a second client or chat database.
The configured runner continues to own its own runtime sessions. Another
runner can read the same job without reconstructing a previous model's
conversation.

```sh
rua-seat --structured --json --job-id draft-pass-1 --context /outside-git/context.json maker "draft the approved deliverable"
rua-seat --show draft-pass-1
```

An explicit job ID prevents duplicate execution: repeated identical requests
return the saved result; a different request or owner is rejected. Running or
unfinished records never trigger an automatic retry. If a process disappeared or
its deadline elapsed without a recorded outcome, inspection reports `unconfirmed`.
Check any side effects before deliberately starting a new job with a new ID.
This does not promise exactly-once effects across arbitrary external services.

The optional context file has exactly these fields:

```json
{
  "project_ref": null,
  "source_refs": [],
  "accepted_decisions": [],
  "authorization": ""
}
```

Use stable references and the user's actual decisions. Nested calls inherit
context unless explicitly supplied another context file. Authorization here is
recorded context, not a security capability: the runtime and tools must enforce
access. Supplying a sentence cannot grant permission to send, delete or publish.

## Structured results and the final reply

`result.schema.json` is the canonical worker result schema. `--structured`
requires `status`, `summary`, `findings`, `sources`, `artifacts` and `blockers`.
No extra fields are accepted. Sources carry `reference` and `locator`.
`completed` cannot contain blockers; unfinished states require a reason.
Schema validity does not prove factual correctness, authorization or that a
referenced artifact exists. The coordinator checks the evidence before reporting
the requested work complete.

In structured mode the adapter receives `RUA_SEAT_RESULT_SCHEMA` pointing at the
schema. An API-backed adapter should use its provider's native schema-constrained
generation where available; see, for example, the
[OpenAI structured-output guide](https://developers.openai.com/api/docs/guides/structured-outputs)
for `text.format`. This CLI does not call any provider's API directly or claim
native schema support for a configured runner: the schema travels in the prompt,
and the CLI validates the returned JSON regardless of which runner produced it.
Invalid output is saved as `invalid_output`, never silently repaired or retried.

Plain structured output shows only the summary, artifact references and pending
reasons. `--json` and `--show` expose the complete private record for another
agent or application. The final coordinator composes a human reply using
`00-system/communication.md`; internal findings and transcripts stay in the job
record. Legacy plain runs keep stdout but report `returned`, not verified task
completion.

## Bounds and failure

Default wall deadline: 600 seconds; `--timeout` accepts up to 3600. Descendants
inherit the earliest deadline. Repeated seats in the same ancestry and more than
three levels are refused; each root permits at most twelve recorded runs.
Combined captured output is limited to 1 MiB. These are limits for cooperating
runners, not a sandbox against code that discards the environment or daemonizes.
Ctrl-C/SIGTERM cancels the runner process group; timeout does likewise. Nested
wrappers propagate cancellation to their own runners. Abrupt SIGKILL can leave
work unconfirmed and requires inspection.

Exit codes: 0 for a returned plain run or a structured completed result; 2 for
invalid input/configuration; 4 for failed, blocked, refused, incomplete, cancelled,
timed-out, oversized, unconfirmed or invalid-output results. No automatic retry
can duplicate a send or overwrite. `--show` prints JSON even for unfinished jobs.

## Install

```sh
ln -sfn "$PWD/30-tools/rua-seat/rua-seat" ~/.local/bin/rua-seat
```

`rua` remains the vault CLI. The shipped binary name is `rua-seat`. Call it as:

```sh
rua-seat pa "the ask"
```

## Observe

```sh
python3 -m unittest discover -s 30-tools/rua-seat -p 'test_*.py'
```

See `spec.md` and `EXPERIENCE.md`. Tests use synthetic runners and private
temporary stores; they make no model calls or external sends.
