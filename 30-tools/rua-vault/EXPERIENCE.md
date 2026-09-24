# EXPERIENCE.md

How a human session behaves. Not how it looks. Not the build spec.

## Foundation

CLI on this Mac. Founder or any AI seat with the same command.

## Information architecture

| Surface | Reached from | Purpose |
| --- | --- | --- |
| `rua vault search QUERY` | terminal | Find an opaque ref from an external label or alias |
| `rua vault get REF` | terminal | Print one verified record |
| `rua vault get --max-bytes BYTES --lines START:END REF` | terminal | Read a verified section of a larger record |
| `rua vault check [REF]` | terminal | Check source health without client labels or content |
| `rua vault rehash REF` | terminal | Recompute sha256 and patch the manifest after editing a record |
| `rua vault tidy PATH [--delete]` | terminal | Show (and optionally remove) stale versioned files in an offload folder |
| `rua vault current REF` | terminal | Exit 0 when the record's `current` block and the working directory name the same deliverable files |

## Voice and tone

| Do | Don't |
| --- | --- |
| Name the failure class | Print paths, URIs, or payload on error |
| Keep retrieval stdout empty on failure; health reports contain only refs and reasons | Guess a closest match |

## State patterns

| State | What they see or hear | Gap |
| --- | --- | --- |
| Worked search | One `ref` and `label` per line | |
| Worked get | Exact record text | |
| No match | stderr: record missing. exit 1 | |
| Bad command | stderr: invalid command. exit 2 | |
| Vault unavailable | stderr: vault unavailable. exit 3 | |
| Source unavailable | stderr: source unavailable. exit 4 | |
| Unverified | stderr: record invalid. exit 5 | |
| Source over chosen limit | stderr: Record exceeds read limit. Use --max-bytes and --lines. exit 4 | |
| Selected text over 1 MiB | stderr: Output exceeds 1 MiB. Use a smaller --lines or --chars range. exit 4 | |
| Character range outside the record | stderr: Character range is outside the record. exit 2 | |
| Range outside the record | stderr: Line range is outside the record. exit 2 | |
| Healthy record | ref, ok, verified | |
| Healthy large record | ref, ok, requires_explicit_limit_and_slice | |
| Failed health check | ref, error, reason code; stderr: Vault check found inaccessible records. exit 4 |
| Current files agree | ref, ok, agree | |
| Current files disagree | ref, error, reason code; stderr: Current files disagree. exit 4. No path | |
| Current block missing | stderr: Record invalid. exit 5. No path | |

## Interaction primitives

Allowed: explicit `search`, `get`, and metadata-only `check` reports. Banned:
list-all client discovery, empty search query,
repo grep of the vault, fallback to Desktop or Downloads.

## Accessibility floor

Every failure is one plain sentence.

## Rejected

- A repo-side client map — because names and paths are payload.
- Silent fallback when storage is missing — because a guessed fee is worse than no fee.

## Success and what not to optimize

Success: they asked for one named record and received that exact text.
For a slice, success is the exact selected lines after verifying the whole record.

Do not optimize: enumerating every client.

## Key flows

### Flow 1 — Deliberate retrieval (founder, named client)

1. `rua vault search "<name>"`
2. Copy the printed ref.
3. `rua vault get <ref>`
4. **Worked:** stdout is the record, nothing else.
5. Failure: vault unavailable, record missing, or record invalid.

### Flow 2 — Casual query must not leak

1. Search the Git repo for a generic term such as pricing.
2. **Worked:** no client names, fees, or vault paths appear from the vault.
3. Failure: a README or test fixture still lists a live client.

### Flow 3 — Large text record

1. Find the ref through deliberate search.
2. `rua vault check <ref>` reports `requires_explicit_limit_and_slice`.
3. `rua vault get --max-bytes 16777216 --lines 1:20 <ref>`.
4. **Worked:** the selected lines arrive only after the full source verifies.
5. An invalid line range or a section over 1 MiB returns no content; request a
   valid smaller range. If one line is too large, use `--chars 1:10000` instead
   to select Unicode characters. A checksum failure requires repairing the source or
   manifest through the ordinary record maintenance process, never bypassing it.

### Flow 4 — Operator health check

1. `rua vault check --json`.
2. **Worked:** every row contains a ref, status and reason, without client labels.
3. A bad source does not hide the health of the other records; exit 4 signals
   that at least one needs attention. Missing or insecure manifest: exit 3,
   no results. This operation reads source text for verification but never prints it.
