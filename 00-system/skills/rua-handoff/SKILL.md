---
name: rua-handoff
description: >
  Hand work to another Rua seat and wait for what they said. Use when
  desk, telegram, or any seat would tag pa, reader, maker, checker, or
  flags. Trigger on hand off, delegate, ask the PA, ask the reader.
---

# Handoff

A mention in chat is not a handoff. The other seat has to run and return.

On this machine:

```sh
rua-seat pa "what is new in the inbox"
rua-seat reader "digest this source, findings only"
rua-seat maker "draft to this decision"
rua-seat checker "grade this draft, do not rewrite"
rua-seat flags "fact-check this draft against the vault"
rua-seat desk "vault search Dental"
```

Wait for stdout. Then quote the useful lines to the founder.

If a vault card or the founder names a path (`/Volumes/T7/...`), `ls` it.
The fetch seat can read that disk when it is mounted. Run the command
before saying you cannot access it.

If `rua-seat` is missing, the same job is:

```sh
hermes -p rua-pa chat -q "the ask"
```

Do not tell the founder you asked someone until that command finished.

PA asks are read-only unless the founder already said send, book, or delete.

Voice notes mis-hear names. Search the vault with the heard phrase, the
words stuck together, and a distinctive chunk (plex, eco, dental, fitz)
before saying there is no record.
