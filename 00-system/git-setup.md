# Git setup

One-time setup for this repository. Run once, per machine for the hook, once
globally for branch protection.

Doctrine: `00-system/skills/rua-git-flow/`.

## 1. Local hook (per machine)

Blocks a direct push to `main` from this machine.

```sh
git config core.hooksPath .githooks
```

That is the whole install. The hook is committed at `.githooks/pre-push`.

Bypass once, deliberately and visibly:

```sh
git push --no-verify
```

A hook lives on one machine and protects you from habit, not from intent. It is
not enforcement. Step 2 is.

## 2. Branch protection (once, needs admin)

This is the only layer that actually enforces anything. GitHub refuses the push
regardless of client, machine, model, or tool-approval setting.

```sh
gh api -X PUT "repos/Rua-Social/Rua/branches/main/protection" \
  -H "Accept: application/vnd.github+json" \
  -F "required_pull_request_reviews[required_approving_review_count]=0" \
  -F "required_pull_request_reviews[dismiss_stale_reviews]=true" \
  -F "enforce_admins=false" \
  -F "required_status_checks[strict]=true" \
  -F "required_status_checks[contexts][]=" \
  -F "restrictions=" \
  -F "allow_force_pushes=false" \
  -F "allow_deletions=false" \
  -F "required_linear_history=true"
```

What each choice means, and why:

| Setting | Value | Why |
|---|---|---|
| `required_approving_review_count` | `0` | One person. Self-merge stays legal. The PR is still required, and the diff still gets read. That is the point, not a second signature |
| `enforce_admins` | `false` | A deliberate escape hatch while the flow beds in. Set `true` once it feels natural |
| `allow_force_pushes` | `false` | `main` history cannot be rewritten |
| `allow_deletions` | `false` | `main` cannot be deleted |
| `required_linear_history` | `true` | No merge commits. History stays readable |

## 3. Archive the superseded repo

`Rua-Social/governanca` was created and last pushed on 10 August, sixteen
minutes apart. It is named "The Governance layer" and that concept now lives in
`00-system/`. Leaving it live implies a second source of truth.

```sh
gh api -X PATCH repos/Rua-Social/governanca -F archived=true
```

Archiving is reversible and keeps the history readable.
