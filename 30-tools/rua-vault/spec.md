# rua-vault

## Goal

A seat that needs one client record on purpose runs `rua vault search`
then `rua vault get`. The command returns the checksum-verified
external record. Casual repo search never finds the record.
Larger registered text records can be read deliberately in sections, and an
operator can check source health without printing client details.

- `rehash <REF>` recomputes sha256 from the record file and patches the manifest atomically.
  No-op if the hash is already current. Use after editing a record directly.
- `tidy <PATH>` scans a directory for versioned file clusters (suffix `-v3`, `_v3`, `-3`, `_3`),
  prints keep/stale groups, and with `--delete` removes the stale iterations. Dry-run by default.
  `--json` for machine-readable output.
- `current <REF>` reads one verified record, parses its single `current` block, and exits 0
  only when every listed file is in the named working directory and that directory has no
  unlisted `.html`, `.pdf`, `.md`, or `.txt` file. Failure reports a reason code and no path.

## Out of scope

- Bulk migration of remaining client files
- Git history rewrite
- Identity, auth, MCP, vector search, or a database
- Ambient scanning, empty-query listing, or disk fallback
- T7-specific paths or brands
- Binary documents or recursive directory reads

## Done

- Git holds only generic resolver code and doctrine.
- Names, aliases, URIs, checksums, and payloads live in an external
  manifest and external files.
- `search` matches manifest metadata only.
- `get` uses one file descriptor, verifies the full sha256 and UTF-8 content,
  then prints at most 1 MiB of text. Default source limit is 1 MiB; explicit
  `--max-bytes` permits up to 16 MiB. `--lines START:END` returns an inclusive
  1-based range after full verification. Mutually exclusive `--chars START:END`
  supports Unicode character ranges when one line exceeds the output ceiling.
  Invalid or excessive ranges fail with
  no content, and JSON identifies the requested range and full source hash.
- `check [REF]` verifies records within the 16 MiB ceiling and emits only refs,
  status and reason codes. Large verified records are marked as requiring an
  explicit limit and slice. Any record failure exits 4 after the check report;
  an invalid manifest exits 3 before any report.
- Payloads require owner read permission and no group or other permissions.
- Missing, insecure, Git-resident, malformed, unsupported, or
  checksum-failed retrievals fail closed with empty stdout. The explicit health
  command may report a failure's ref and reason, never its label, path or content.
- Tests use only temporary synthetic fixtures.

## Observe

```sh
python3 -m unittest discover -s 30-tools/rua-vault -p 'test_*.py'
```

Then, only when an external vault is configured outside Git, search a
named client and get the exact verified record. A generic pricing
query against the repo must not surface that record.

See `EXPERIENCE.md` for the human CLI session.
