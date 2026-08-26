# rua-desk

Terminal front door for the Rua desk. The repo is the desk; Claude, Codex,
Grok, and Gemini are selectable harness seats.

## Use

```sh
rua-desk              # choose a seat interactively
rua-desk claude       # open Claude Code
rua-desk codex        # open Codex CLI
rua-desk grok         # open the Grok dashboard
rua-desk grok-one     # open one Grok session
rua-desk gemini       # open Gemini CLI
rua-desk status       # show installed seats and versions
rua-desk card         # read the operator card
rua-desk ping         # ask every installed seat for one line
rua-desk help         # show commands
```

Bare `rua-desk` prints status instead of waiting when it is used through a
pipe or another non-interactive process.

Set `RUA_REPO` if the checkout is somewhere other than `~/Rua`.

## Install

The installed command is a symlink to the versioned launcher:

```sh
mkdir -p ~/.local/bin
ln -sfn "$PWD/30-tools/rua-desk/rua-desk" ~/.local/bin/rua-desk
```

Ensure `~/.local/bin` is on `PATH`. The launcher requires the macOS-provided
Z shell. Each optional seat requires its vendor CLI (`claude`, `codex`,
`grok`, or `gemini`) and its own login. There are no package dependencies.

## Verify

```sh
python3 -m unittest discover -s 30-tools/rua-desk -p 'test_*.py'
30-tools/rua-desk/rua-desk status
```

The session contract is [EXPERIENCE.md](EXPERIENCE.md). The approved build
boundary is [spec.md](spec.md).
