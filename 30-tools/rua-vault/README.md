# rua-vault

Deliberate retrieval of one external client record. The Git checkout
never holds names, paths, fees, or payloads.

## Commands

```sh
rua vault search [--json] QUERY
rua vault get [--json] REF
```

`search` matches labels and aliases in the **external** manifest only.
`get` reads the file once, checks sha256, then prints UTF-8 text.

## Config

Default manifest:

```text
${XDG_CONFIG_HOME:-~/.config}/rua/vault/manifest.json
```

Override: `RUA_VAULT_MANIFEST`. Directory mode `0700`, file mode `0600`.
Manifests and payloads inside a Git worktree are refused.

Version 1 supports `file://` only. There is no list command and no
fallback search of the disk.

## Install

```sh
ln -sfn "$PWD/30-tools/rua-vault/rua" ~/.local/bin/rua
```

## Observe

```sh
python3 -m unittest discover -s 30-tools/rua-vault -p 'test_*.py'
```

See `spec.md` and `EXPERIENCE.md`.
