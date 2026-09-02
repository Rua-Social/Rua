# rua-seat

Run one other Rua seat and print what they said. A mention in chat is not a handoff.

```sh
rua seat pa "what is new in the inbox"
rua seat reader "digest this URL, neutral findings only"
```

Seats: desk, pa, reader, maker, checker, flags.

On this machine the command calls `hermes -p rua-<seat> chat -q`. That is a harness binding, not doctrine. The doctrine is: the other role actually ran and returned.

## Install

```sh
ln -sfn "$PWD/30-tools/rua-seat/rua-seat" ~/.local/bin/rua-seat
```

`rua` remains the vault CLI. This is a second command: `rua-seat` or `rua seat` if you wrap it. The shipped binary name is `rua-seat`. Call it as:

```sh
rua-seat pa "the ask"
```

## Observe

```sh
python3 -m unittest discover -s 30-tools/rua-seat -p 'test_*.py'
```
