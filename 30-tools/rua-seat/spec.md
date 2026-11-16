# Bounded, portable handoffs

The runner must preserve a task's context and outcome across harnesses, prevent
accidental duplicate execution, and stop recursive delegation within explicit
bounds. It uses a small standard-library SQLite ledger because independent
processes need atomic job claims; Markdown files cannot atomically claim a job.
Existing runtimes still execute work and maintain their own sessions.

The implementation requires an explicit runner binding; no CLI is privileged by
default, so the tool stays model-agnostic across machines and harnesses. The
seat's role, scope and source pointers travel in the prompt itself rather than
in a runner-side profile, so any runner that takes a plain prompt can fill a
seat. Structured worker output is optional and validated against one shipped
JSON schema. Invalid, refused, incomplete and failed results remain visible
states. The coordinator owns facts, authorization checks and the final reply.

Done is observed through the README test command: saved results survive another
CLI process; repeated IDs do not rerun; context reaches the runner; timeout,
recursion and output limits stop work; invalid structured JSON never becomes a
successful result; an unconfigured runner fails clearly rather than falling
back to one CLI.

This does not add a CRM, host a bot, migrate client records, replace runtime
sessions, provide a security sandbox or guarantee external exactly-once writes.
Session behavior is in `EXPERIENCE.md`; the terminal supplies the visual design.
