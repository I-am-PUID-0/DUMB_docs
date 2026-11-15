---
title: Contributing
description: Choose the right DUMB repository and branch, reproduce a problem, run the relevant checks, and submit a focused code or documentation change.
icon: lucide/git-pull-request
---

# Contributing

You can help with code, documentation, reproducible bug reports, or testing a proposed fix. Start with the repository that owns the behavior.

## Choose how to help

- **Report a problem:** use the steps below to describe what happened and share relevant, redacted logs.
- **Improve a guide:** report a confusing instruction or submit a documentation correction.
- **Help another user:** join the [community discussion](https://discord.gg/8dqKUBtbp5).
- **Support the DUMB maintainer:** use [GitHub Sponsors](https://github.com/sponsors/I-am-PUID-0). Integrated applications have their own maintainer links in the service guides.

## Report a problem

Include the DUMB image/version, relevant application version, what you expected, what happened, and the smallest steps that reproduce it. For UI issues, include the browser and a screenshot if useful.

Use logs exported through DUMB where possible. Review logs, configuration, screenshots, and URLs for credentials and personal information before attaching them. Do not upload a whole configuration directory or database to a public issue.

- [Backend issues](https://github.com/I-am-PUID-0/DUMB/issues)
- [Dashboard issues](https://github.com/nicocapalbo/dmbdb/issues)
- [Documentation issues](https://github.com/I-am-PUID-0/DUMB_docs/issues)
- [Community discussion](https://discord.gg/8dqKUBtbp5)

<details class="geek-details" markdown="1">
<summary>Geek contribution guide: repositories, branches, development and validation</summary>

## Choose a repository and branch

| Change | Repository | Normal pull request target |
|---|---|---|
| Backend API, service installation, process lifecycle, container image | [DUMB](https://github.com/I-am-PUID-0/DUMB) | `dev` |
| Dashboard, onboarding UI, embedded proxy, browser behavior | [dmbdb](https://github.com/nicocapalbo/dmbdb) | `dev` |
| This documentation site | [DUMB_docs](https://github.com/I-am-PUID-0/DUMB_docs) | `master` |

DUMB's release branch is `master`; dmbdb's release branch is `main`. Normal fixes and features go to `dev`. Release work and approved hotfixes may target the release branch.

A change can span repositories. An API change may need a dashboard capability check and a docs update; a dashboard workflow change may need revised user instructions.

## Develop and validate

Use the selected repository's devcontainer and checked-in instructions. For the backend, fork the repo, create a feature branch from `dev`, and run focused tests while iterating.

Before opening a backend pull request:

```bash
make format
make verify
```

`make format` applies formatting; `make verify` checks metadata, the lockfile, formatting, lint, syntax, tests, and security. Run it in a disposable development environment rather than against a live media library.

For the dashboard, use the pinned package manager, a frozen lockfile installation, the relevant test scripts, and a production build. Embedded routing changes need the repository's browser checks as well.

For docs, use the [repository README](https://github.com/I-am-PUID-0/DUMB_docs#readme) for the current build and validation commands. Check both release and development output when changing channel-specific content.

### Service installer and updater regressions

DUMB includes a disposable previous-version-to-latest matrix. It gives each selected case fresh configuration, data, logs, mounts, and databases rather than downgrading an operator's installation.

From a Docker-capable development host:

```bash
make regression-image
make regression-service-updates REGRESSION_JOBS=2
```

Two workers are the default because source builds can be resource-intensive. To focus a run, pass `REGRESSION_ARGS="--case <case-id>"`; use `--include-pending` while qualifying a pending entry. `--use-gh-auth-token` uses the current GitHub CLI token without printing it.

The matrix is `scripts/service_update_regression_matrix.json`. Qualified entries run by default. Pending entries still need prior versions, dependency fixtures, or disposable credentials. Reports go to ignored `.regression-reports/`; the separate verified install cache is retained for reuse checks.

## Submit a pull request

Describe the concrete problem, the resulting behavior, and how you tested it. Link related issues, include screenshots for UI changes, and update user docs when behavior changes. Keep unrelated cleanup separate.

Use Conventional Commit titles, for example:

- `fix(proxy): preserve embedded service WebSocket routing`
- `feat(api): expose symlink comparison results`
- `docs: clarify first-run provider setup`

Distinguish automated checks from any manual or operational testing that remains. For dependency updates, inspect the changed versions and the affected runtime path as well as the build result.

For a larger feature, discuss the proposed behavior in an issue or the community before building it.

</details>
