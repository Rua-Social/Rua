# rua-vault

## Goal

A seat that needs one client record on purpose runs `rua vault search`
then `rua vault get`. The command returns the checksum-verified
external record. Casual repo search never finds the record.

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
- `get` reads once, verifies sha256, then prints UTF-8 content.
- Missing, insecure, Git-resident, malformed, unsupported, or
  checksum-failed sources fail closed with empty stdout.
- Tests use only temporary synthetic fixtures.

## Observe

```sh
python3 -m unittest discover -s 30-tools/rua-vault -p 'test_*.py'
```

Then, only when an external vault is configured outside Git, search a
named client and get the exact verified record. A generic pricing
query against the repo must not surface that record.

See `EXPERIENCE.md` for the human CLI session.
