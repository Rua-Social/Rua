# rua-vault

Deliberate retrieval of one external client record. The Git checkout
never holds names, paths, fees, or payloads.

## Commands

```sh
rua vault search [--json] QUERY
rua vault get [--json] REF
rua vault get [--json] --max-bytes BYTES --lines START:END REF
rua vault get [--json] --max-bytes BYTES --chars START:END REF
rua vault check [--json] [REF]
```

`search` matches labels and aliases in the **external** manifest only.
`get` reads the file through one descriptor, checks the complete sha256 and
UTF-8 content, then prints text. The default source limit and maximum returned
text are 1 MiB (1,048,576 bytes). A larger source requires an explicit
`--max-bytes` limit, up to 16 MiB (16,777,216 bytes), and a `--lines START:END`
range whose returned text fits 1 MiB. Lines are inclusive and start at 1;
out-of-range requests fail rather than silently shortening the result. A small
record can also be sliced. JSON results retain the full source hash and add a
`lines` object for slices. For a single very long line, use `--chars START:END`
instead; this selects inclusive 1-based Unicode characters and returns `chars`
metadata. A request cannot combine the two selectors. JSON escaping can increase the serialized size.

`check` verifies the configured records, or one supplied ref, with the 16 MiB
read ceiling. It prints only `ref`, `status`, and a reason code: no labels,
paths, content, or hashes. `ok / verified` means ordinary retrieval works;
`ok / requires_explicit_limit_and_slice` means the record can be retrieved in
sections. Missing, insecure, Git-resident, oversized, corrupt, or invalid UTF-8
sources are errors. A check of multiple records continues after a failed record.
This is an explicit health operation, not a discovery command for client names.

Exit codes remain 0 success, 1 missing record, 2 invalid command, 3 unavailable
manifest, 4 unavailable source or output too large, 5 invalid record. A health
check with any record errors exits 4 and still emits its metadata-only results.
An unreadable or invalid manifest fails before any results are printed.

## Config

Default manifest:

```text
${XDG_CONFIG_HOME:-~/.config}/rua/vault/manifest.json
```

Override: `RUA_VAULT_MANIFEST`. Directory mode `0700`, file mode `0600`.
Manifests and payloads inside a Git worktree are refused.
Payloads must be readable by their owner with no group or other permissions.

Version 1 supports `file://` only. There is no list command and no
fallback search of the disk.

The vault limits accidental retrieval and verifies file integrity. It does not
isolate files from another process running as the same local user.

## Install

```sh
ln -sfn "$PWD/30-tools/rua-vault/rua" ~/.local/bin/rua
```

## Observe

```sh
python3 -m unittest discover -s 30-tools/rua-vault -p 'test_*.py'
```

See `spec.md` and `EXPERIENCE.md`.
