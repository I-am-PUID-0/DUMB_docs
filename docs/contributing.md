---
title: Contributing
icon: lucide/git-pull-request
hide:
  - navigation
---

## Contributing to DUMB

Thanks for helping improve **Distributed Unlimited Media Bridge (DUMB)**.

Code, docs, testing feedback, and issue triage are all valuable contributions.

## Branch Strategy

- `dev` is the default collaboration branch.
- `master` is the production and release branch.
- Open normal feature and fix PRs against `dev`.
- Open PRs against `master` only for release work or approved hotfixes.

## Development Setup

Recommended: use the DUMB devcontainer:

- [.devcontainer/devcontainer.json](https://github.com/I-am-PUID-0/DUMB/blob/dev/.devcontainer/devcontainer.json)

Quick start:

1. Fork [I-am-PUID-0/DUMB](https://github.com/I-am-PUID-0/DUMB).
2. Clone your fork.
3. Open the workspace in VS Code Dev Containers.
4. Create a feature branch from `dev`.
5. Make changes and run relevant checks.
6. Open a PR to `dev`.

If you do not use Dev Containers, run with Docker using the same mounts and environment layout.

## Pull Request Guidelines

- Keep PRs focused and small when possible.
- Include a clear summary, motivation, and test notes.
- Link related issues.
- Add screenshots for UI changes.
- Update docs when behavior changes.

### Commit Format

Use Conventional Commits for PR titles and commits, for example:

- `feat(api): add new symlink repair mode`
- `fix(proxy): route iframe websocket path correctly`
- `docs: update onboarding preflight guide`

`conventional-commits.yml` validates PRs targeting both `dev` and `master`.

## Dependabot and Automation Notes

- Dependabot updates are targeted to `dev`.
- Integration testing for combined Dependabot updates runs from `dev`.
- Release automation remains pinned to `master`.

## Testing Expectations

Before opening a PR:

- Run formatters/linters relevant to changed files. For DUMB backend changes, run `make format` before `make verify`; `make verify` is check-only and does not rewrite Black formatting drift.
- Run focused tests for your change.
- Include manual verification notes when automated tests are not available.

### Service update regression suite

DUMB retains a disposable previous-version-to-latest regression matrix for service installers and updaters. It runs selected services in isolated Docker containers with fresh configuration, data, logs, mounts, and databases; it never downgrades the operator's live service data.

From the DUMB repository on a Docker-capable host:

```bash
make regression-image
make regression-service-updates REGRESSION_JOBS=2
```

Two workers are the conservative default because source builds can be CPU-, memory-, and disk-intensive. Cases run concurrently when they do not share a worker, while each service's install, update, and health checks remain ordered within that container. Use `REGRESSION_ARGS="--case <case-id>"` for focused coverage or `REGRESSION_ARGS="--include-pending --case <case-id>"` while qualifying a new matrix entry. `REGRESSION_ARGS="--use-gh-auth-token"` uses the current GitHub CLI token without printing it and avoids anonymous API limits.

The matrix lives in `scripts/service_update_regression_matrix.json`. Qualified cases run by default; pending entries document services that still need deterministic prior versions, dependency fixtures, or disposable credentials. Per-case logs and an aggregate JSON report are written under the ignored `.regression-reports/` directory. The verified install cache is retained separately so repeat runs also exercise safe cache reuse.

## Docs Contributions

Docs live in [DUMB_docs](https://github.com/I-am-PUID-0/DUMB_docs).

- Update docs when API behavior, onboarding flow, or service settings change.
- Keep examples and screenshots current.
- Prefer small, reviewable docs PRs.

## Non-Code Contributions

Even if you don't write code, there are **plenty of ways** to help!

### Star the Repo
A quick way to show support is by starring the project on GitHub:  [github.com/I-am-PUID-0/DUMB](https://github.com/I-am-PUID-0/DUMB)

### Join the Community
- Ask questions or help others in the **[DUMB Discord server](https://discord.gg/8dqKUBtbp5)**
- Boost the server if you find it helpful 
- Share your setups and improvements

### Help with Documentation
- Found a typo or confusing section in the docs? Open an issue or pull request.
- Suggestions and feedback on existing documentation are **always welcome**.

---

## Monetary Contributions?

- Sponsor the Dev through [GitHub Sponsors](https://github.com/sponsors/I-am-PUID-0)

---

## Roadmap & Feedback

If you have ideas, feature requests, or feedback:

- Create a [GitHub Issue](https://github.com/I-am-PUID-0/DUMB/issues)

- Discuss in the community before starting larger PRs

---
