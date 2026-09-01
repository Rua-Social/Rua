# EXPERIENCE.md

How a human session behaves. Not how it looks. Not the build spec.

## Foundation

CLI on this Mac. Founder or any AI seat with the same command.

## Information architecture

| Surface | Reached from | Purpose |
| --- | --- | --- |
| `rua vault search QUERY` | terminal | Find an opaque ref from an external label or alias |
| `rua vault get REF` | terminal | Print one verified record |

## Voice and tone

| Do | Don't |
| --- | --- |
| Name the failure class | Print paths, URIs, or payload on error |
| Stay silent on stdout when failing | Guess a closest match |

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

## Interaction primitives

Allowed: explicit `search` and `get`. Banned: list-all, empty query,
repo grep of the vault, fallback to Desktop or Downloads.

## Accessibility floor

Every failure is one plain sentence.

## Rejected

- A repo-side client map — because names and paths are payload.
- Silent fallback when storage is missing — because a guessed fee is worse than no fee.

## Success and what not to optimize

Success: they asked for one named record and received that exact text.

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
