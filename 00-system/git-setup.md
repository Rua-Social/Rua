# Git setup

One-time setup for this repository. The remote gate is on. The hook is per
machine.

Doctrine: `00-system/skills/rua-git-flow/`.

## 1. Local hook (per machine)

Blocks a direct push to `main` from this machine. When a push includes
`30-tools/html-to-pdf`, `30-tools/rua-desk`, `30-tools/rua-vault` or `30-tools/rua-seat`, it also runs
`00-system/check-tools.sh`.

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

## 2. Branch protection (on)

Applied. Confirm with `GET repos/Rua-Social/Rua/branches/main/protection`.
A 404 means it has been removed.

Admins are included (`enforce_admins` true). Merge commits onto `main` are
off; squash or rebase. No required status checks: GitHub Actions `tools.yml`
does not yet run the unittest commands these tools document, and a required
always-green check is worse than none. Updating that workflow file needs a
`gh` token with the `workflow` scope.

```sh
gh api -X PUT repos/Rua-Social/Rua/branches/main/protection \
  -H "Accept: application/vnd.github+json" \
  --input - <<'JSON'
{
  "required_status_checks": null,
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "required_approving_review_count": 0
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_linear_history": true
}
JSON
```

What each choice means, and why:

| Setting | Value | Why |
|---|---|---|
| `required_approving_review_count` | `0` | Self-merge stays legal. The PR is still required, and the diff still gets read. That is the point, not a second signature |
| `enforce_admins` | `true` | Both people who can push are admins. False would bind neither of them |
| `allow_force_pushes` | `false` | `main` history cannot be rewritten |
| `allow_deletions` | `false` | `main` cannot be deleted |
| `required_linear_history` | `true` | No merge commits. Squash or rebase |
| `required_status_checks` | `null` | Do not require a check that does not test |

Repo merge buttons: squash and rebase on, merge commit off, delete branch on merge.

## 3. Archive the superseded repo

`Rua-Social/governanca` was created and last pushed on 10 August, sixteen
minutes apart. It is named "The Governance layer". That method was consulted
and not installed here. Leaving it live implies a second source of truth.

```sh
gh api -X PATCH repos/Rua-Social/governanca -F archived=true
```

Archiving is reversible and keeps the history readable.
