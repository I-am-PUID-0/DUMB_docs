# Automatic frontend media refreshes

The [refresh workflow](../../.github/workflows/refresh-frontend-media.yml) checks
application sources every six hours, after changes to media tooling or channel
metadata on `master`, and through **Actions → Refresh frontend documentation
media → Run workflow**. Choose `release`, `dev`, or both. Use **force** to recapture
unchanged commits after a visual review identifies an improvement.

The workflow opens or updates one review PR. It does not approve or merge that
PR, publish Pages, create a release, or send an announcement. Accepted media goes
through the existing documentation release and publication process.

## Source selection

| Channel | Backend | Frontend |
| --- | --- | --- |
| Release | The stable backend recorded in `docs-versions.json`, or the next stable release admitted by the existing reviewed promotion checks | The latest published stable frontend release |
| Development | The current immutable commit of DUMB's `dev` branch | The current immutable commit of the frontend's `dev` branch |

Every selection records full commit hashes and package versions. A release tag
that moves, disagrees with its package version, or has not passed the reviewed
promotion checks stops the refresh. Development media does not silently advance
the reviewed prose pins. The site identifies the actual captured versions and
explains when development examples use newer application source than the prose.

For a newly published, reviewed backend release, the media PR includes the
verified `docs-versions.json` promotion and matching release captures together.
This avoids publishing new release prose alongside old backend screenshots.

The committed `frontend-media.json` catalog points to accepted packages and their
exact capture plans. Ordinary documentation builds validate those committed
sources offline. They do not chase a moving upstream branch while rebuilding an
immutable documentation release.

## Capture and acceptance

The capture catalog lists the actual screens, associated guides, required
backend capabilities, immutable frontend source prerequisites, stills and clips.
Light and dark appearance are captured separately. The backend's capability
endpoint is parsed as source data; no backend application code is executed.
Unknown runtime capability expressions remain unresolved, and a scenario that
needs one blocks the plan. A source-verified absent feature is recorded as
unavailable. A failed selector is a capture failure.

The real Nuxt frontend is built from its selected commit with the frozen
dependency lockfile. HTTP and WebSocket examples stay in the isolated fixture.
Embedded Sonarr uses a real disposable application pinned by image digest and
application version, with no library or provider accounts. Its cleanup checks the
exact task identity and removes only that temporary instance. Runtime origins and
demo state are not published.

The capture manifest records example and simulated operations separately from
measured observations. A visible review screen is not evidence that an actual
installation, provider connection, backup, migration or playback succeeded.

The workflow packages only complete coverage. It verifies all planned scenarios
and both themes, required still/clip kinds, source identities, file signatures,
sizes and hashes. Missing controls, unexpected requests, partial local captures,
changed source commits, or a changed documentation head stop the PR update.
The homepage showcase is regenerated from the same accepted screen package.

Capture tooling, catalog, example dataset and native-application pins are
fingerprinted. Changes to them trigger captures even when application commits
stay the same. Asset directories also include a digest of the finished package
manifests: a forced recapture with different output gets a new URL. Earlier asset
revisions remain available.

## Review and failures

The PR body lists the exact backend and frontend versions and commits for each
changed channel. Review the homepage showcase, interface gallery and affected
guide figures before merging. Check readable labels, truthful example-data
captions, version availability, clip pacing and media controls. Automated checks
establish source and coverage contracts; they do not replace visual review.

A failed refresh leaves the accepted catalog and media untouched. Inspect the
failed Actions step and capture-manifest artifact, repair the fixture or scenario
for the selected source, and rerun the workflow. Never mark a failed selector as
an unavailable feature to make a run pass. A source/head race requires a new
selection and capture; an older artifact must not be applied to newer inputs.

The proposal job downloads each selected channel by its exact artifact name into
`proposals/release` or `proposals/dev`. Keep those destinations explicit: the
download action extracts a single matching artifact directly at its target path,
while multiple pattern matches can introduce artifact-name subdirectories.
Each selected channel must contain its own `plan.json`, `frontend/` and
`showcase/` before validation. Failed or unselected channels are not substituted.

The capture job has read-only repository permissions and no release credential.
A separate job starts from the trusted documentation commit, validates downloaded
data without executing generated scripts, and uses the existing release
credential only to create the scoped media PR. No application repository is
modified.

For local iteration and the capture/package commands, see the
[capture instructions](README.md). Partial captures are useful for review but
cannot replace an accepted channel package.
