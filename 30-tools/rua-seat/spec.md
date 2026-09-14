# Bounded, portable handoffs

The runner must preserve a task's context and outcome across harnesses, prevent
accidental duplicate execution, and stop recursive delegation within explicit
bounds. It uses a small standard-library SQLite ledger because independent
processes need atomic job claims; Markdown files cannot atomically claim a job.
Existing runtimes still execute work and maintain their own sessions.

The implementation keeps the existing runner override. Structured worker output
is optional and validated against one shipped JSON schema. Invalid, refused,
incomplete and failed results remain visible states. The coordinator owns facts,
authorization checks and the final reply. Live profile adapters point to shared
doctrine and can be backed up and restored without touching credentials.

Done is observed through the README test command: saved results survive another
CLI process; repeated IDs do not rerun; context reaches the runner; timeout,
recursion and output limits stop work; invalid structured JSON never becomes a
successful result; profile updates restore cleanly after failure.

This does not add a CRM, host a bot, migrate client records, replace runtime
sessions, provide a security sandbox or guarantee external exactly-once writes.
Session behavior is in `EXPERIENCE.md`; the terminal supplies the visual design.
