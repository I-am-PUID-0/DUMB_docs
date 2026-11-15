# DUMB documentation

Source for [dumbarr.com](https://dumbarr.com), covering the DUMB backend and
dmbdb dashboard. The documentation uses [Zensical](https://zensical.org/).

## Preview and verify

Use the repository's development container, or Python 3.11 or newer with Poetry:

```bash
poetry install --no-root
poetry run python scripts/build_docs.py
poetry run python scripts/audit_seo.py site
poetry run python scripts/audit_seo.py site/dev --development
poetry run python scripts/audit_reader_paths.py site
poetry run python -m unittest discover -s tests
poetry run python -m http.server 8000 --directory site
```

Open `http://localhost:8000`. The preview includes both channels and the shared
header selector. `poetry run zensical serve` is useful for writing, but previews
the development source alone; it does not assemble both channels.

## Release and development channels

The public root contains the latest released DUMB documentation. `/dev/` contains
the development documentation. Both use the same theme, navigation and reviewed
Markdown sources in `docs/`. See [documentation versions](docs/reference/doc-versions.md)
for the user-facing explanation.

`docs-versions.json` records the released backend version and immutable source
commit, the documentation snapshot commit, and the backend/frontend commits
covered by the development review. Keep these separate from this repository's
own package version. The release build reads its frozen docs
directly from Git, without switching branches or changing the index.
Navigation, theme configuration, templates, styles, and scripts stay shared and
current. Navigation is filtered to pages available in each channel, so a menu
improvement reaches stable readers without advertising unshipped features.

- Set `development_only: true` in front matter for a guide whose feature has not
  shipped. The release build substitutes a short availability page and omits it
  from navigation; old links still resolve.
- In mixed pages, enclose complete development sections in
  `<!-- dev:start -->` and `<!-- dev:end -->`. Use `<!-- release:start -->` and
  `<!-- release:end -->` for release-specific alternatives. Markers must be paired
  and must not nest. Keep code fences and HTML containers inside the same block.
- Check actual tagged backend code before describing behavior as released.
  A newer dashboard cannot add a backend capability to an older image.
- After reviewing new development behavior, advance `dev.version`, `dev.source`,
  and `dev.frontend_source` together with the relevant documentation. These
  commits are the reviewed candidate, rather than a claim that every later
  change to the development branches has been reviewed.

The workflow checks DUMB's latest stable release every six hours, on docs pushes,
and when manually dispatched. When its version matches the reviewed candidate
and its source contains the reviewed backend commit, `scripts/sync_release.py`
proposes a release snapshot pointing to the current documentation commit. It
also checks that a published stable dashboard release contains the reviewed
frontend commit. The frontend has its own version number. This checks that the
compatible dashboard is available; existing images can still contain older
bundled frontends until they are updated.
The validation workflow promotes the candidate's development sections, builds
and audits both channels, then records only the verified version metadata.
That commit enters the normal docs release process; it does not publish Pages.
The metadata step uses the existing `RELEASE_PLEASE_TOKEN` credential because
the default branch requires pull requests and permits administrator bypass.
It verifies the publisher's repository permission even when no promotion is
needed. Build jobs keep their read-only Actions token. GitHub supplies the
authenticated actor's commit identity; local author settings are not changed.
A non-forced ref update and head checks reject concurrent changes.

An unexpected release version, moved tag, incompatible ancestry, or failed build
stops promotion. Review the changed source and candidate, then run the workflow
again. A release is never inferred from a branch name or a frontend version.

For a correction to an already frozen stable guide, place a reviewed replacement
at `release-overrides/<release-version>/<path-relative-to-docs>`, for example
`release-overrides/2.23.0/features/authentication.md`. Only existing Markdown
pages can be replaced. Overrides apply before channel filtering, only to that
exact release, and cannot add navigation, routes, scripts, or assets. Update the
development guide too when the correction applies there. A new release snapshot
does not inherit overrides intended for an older version.

The build creates channel metadata and a page inventory for the selector. It
retains the current path when switching channels and falls back to the target
homepage if no equivalent page exists. Search stays within the selected channel.

## Writing and publishing

See [contributing](docs/contributing.md) and the concise
[writing guide](.cursor/rules/docs-rules/RULE.md). Preserve existing URLs and add
compatibility links when splitting a long guide. Use reserved examples and keep
credentials and deployment state out of Git.

Pull requests and pushes to `master` build and audit both channels. Public
publication follows a **DUMB_docs release**, with its own version number:

1. Write conventional commits, such as `docs: explain a setup task` or
   `fix(docs): correct a control label`. The Python release strategy includes
   documentation changes as releasable work.
2. Release Please maintains a generated release PR with the package version,
   release manifest and `CHANGELOG.md`. `automate_docs_release.py` accepts only
   that same-repository generated PR, a current base, and those three files.
   It checks that the changes contain only the version bump and a prepended
   changelog section, then waits for the current-head docs gate and all three
   CodeQL checks. Queued/rerunning checks prevent merging; it rechecks the head
   and base immediately before a head-pinned merge.
3. The existing administrator release actor merges that exact head. This narrow
   automation uses the repository's existing bypass because its owner-authored
   version PR cannot approve itself. It does not weaken branch rules, approve
   arbitrary PRs or automatically merge content/dependency changes.
4. Release Please creates the GitHub release and immutable tag. Its published
   event dispatches `publish-release.yml` on `master`, preserving the Pages
   environment's existing branch policy. The workflow verifies the latest
   published stable docs release, checks out its **resolved commit**, and builds
   with `--release-tag`. It never runs backend promotion in that checkout.
5. Both channels are audited again. Package version, manifest, tag, clean source,
   HTML footer/meta and channel JSON must agree. Pages and DUMB's legacy
   `gh-pages` mirror receive the same validated artifact. Both publication steps
   recheck that the tag has not moved or been superseded. Newer unreleased master
   commits do not prevent deployment of the latest published release.

The footer shows **Documentation release X.Y.Z**, its release notes and source
commit in both channels. The header continues to show the **DUMB backend**
release/development version. Dedicated `dumb-docs-*` metadata, the nested
`documentation` object in each `channel.json`, and both `llms` exports expose
the same documentation artifact identity without changing channel versions.
Local builds and PR previews say **Documentation preview (unreleased)**; a
package version alone never establishes that a build is a published release.

Release Please and publication reconcile every six hours and can be run
manually. To retry publication, run **Publish documentation release** from
`master` and leave `release_tag` blank to select the latest release, or supply
that exact tag. Older tags, prereleases, moved tags and releases outside master
ancestry are refused. The existing release credential drives downstream events;
default-token events alone are insufficient for this unattended chain.
Documentation publishing does not publish a DUMB image.

### Discord release announcements

New stable docs releases request a Discord announcement after both Pages and
the legacy mirror deploy successfully. The workflow uses the existing
`DISCORD_WEBHOOK_URL` secret and the original release-role mention, stored in
the `DISCORD_RELEASE_MENTION` repository secret. Release notes come from the
verified GitHub release; long notes are shortened with a link to the full text.

Scheduled rebuilds and ordinary manual publication do not post messages. For a
delivery retry, run **Publish documentation release** with the exact latest tag
and `announce_release` enabled. A confirmed delivery is skipped on repeat runs.
The release actor keeps a pending/sent receipt in the
`DOCS_DISCORD_ANNOUNCEMENT` repository variable. A pending receipt blocks blind
retries after a timeout or failure to record delivery; inspect the workflow and
Discord channel before resolving it. Webhook credentials and Discord response
contents stay out of logs and Git.

Release pages retain their public URLs. Development pages are `noindex, follow`
with their own canonical URLs, and release-unavailable pages stay out of search
and the release sitemap. The generated audit checks metadata, structured data,
fragments, image references, and the complete release sitemap. Each channel also
exports `llms.txt` and `llms-full.txt` from its filtered content.

Geek mode is a browser preference that opens native technical-detail sections.
It never removes documentation from the page or changes which channel is read.
The normal guide must stand alone as a complete frontend task: where to click,
what to enter, how to save, and how to check the result. Geek sections add
internals and alternative API, CLI, environment, or manual configuration methods.
Do not hide normal dashboard actions, essential warnings, support links, or
deployment choices merely because a page also contains technical reference.
The reader-path audit checks platform discovery, visible frontend workflows,
separate technical diagrams, and support links outside Geek sections in both
channels. It complements source-based editorial review of each procedure.
Enabled sections have green panels and a visible mode indicator. Amber channel
labels and Dev badges identify additions beyond the frozen release docs;
already promoted blocks do not retain an unreleased label. A new guide is
distinguished from an explicitly development-only feature.

Channel filtering repairs only table row continuations split by removed markers.
The generated audit rejects raw Markdown table rows outside tables/code. Shared
CSS and JavaScript receive content-hashed URLs so browser caches pick up UI fixes.
