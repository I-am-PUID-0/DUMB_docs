---
title: Contributing
icon: lucide/git-pull-request
hide:
  - navigation
---

## Contributing to DUMB

Thanks for helping improve **Debrid Unlimited Media Bridge (DUMB)**.

Code, docs, testing feedback, and issue triage are all valuable contributions.

## Branch Strategy

- `dev` is the default collaboration branch.
- `master` is the production and release branch.
- Open normal feature and fix PRs against `dev`.
- Open PRs against `master` only for release work or approved hotfixes.

## Development Setup

Recommended: use the DUMB devcontainer:

- [.devcontainer/devcontainer.json](https://github.com/I-am-PUID-0/DUMB/tree/master/.devcontainer/devcontainer.json)

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

- Run formatters/linters relevant to changed files.
- Run focused tests for your change.
- Include manual verification notes when automated tests are not available.

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

