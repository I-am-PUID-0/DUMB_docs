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
own package version. The release build reads its frozen docs and navigation
directly from Git, without switching branches or changing the index.
Theme configuration, templates, styles, and scripts stay shared and current;
the snapshot freezes prose and navigation rather than obsolete build settings.

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
The workflow
promotes the candidate's development sections, builds and audits both channels,
then records only the verified version metadata and publishes the artifact.
GitHub supplies the automation commit identity; local author settings are not
changed. A non-forced ref update and head checks reject concurrent changes.

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

Pull requests build and audit both channels. Pushes to `master` publish the
verified artifact to GitHub Pages and mirror it to DUMB's existing `gh-pages`
branch. Documentation publishing does not publish a DUMB image.

Release pages retain their public URLs. Development pages are `noindex, follow`
with their own canonical URLs, and release-unavailable pages stay out of search
and the release sitemap. The generated audit checks metadata, structured data,
fragments, image references, and the complete release sitemap. Each channel also
exports `llms.txt` and `llms-full.txt` from its filtered content.

Geek mode is a browser preference that opens native technical-detail sections.
It never removes documentation from the page or changes which channel is read.
