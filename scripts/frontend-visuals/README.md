# Capture the actual DUMB frontend

The capture runner renders the full packaged Nuxt application. It does not
recreate screens in HTML or replace application components. An isolated,
in-memory HTTP/WebSocket fixture supplies public example responses. The embedded
Sonarr example uses the actual application from the pinned official image.

[Capture catalog](./capture-catalog.json) lists screens, routes, feature guides,
required source files and backend capability gates.
[Example data](./dataset.json) contains no operator configuration or credentials.
[Automation](./AUTOMATION.md) explains source discovery, refresh PRs and publishing.

## Source and coverage contract

Each run requires an immutable plan containing independent frontend and backend
repository, commit, version and release/development identities. Release examples
use released sources. Development examples use committed development sources;
they are never relabeled as a release or an uncommitted working tree. Media
source pins are separate from prose review pins in the documentation builder.

The runner checks source and compiled package versions, validates the canonical
plan hash and catalog/data hashes, and records the plan fingerprints.
The caller must verify source refs and archive their exact commits before
building. Use each project's development container and declared Node/pnpm
versions. Keep active checkouts, controllers, generated outputs, dependencies
and staged work untouched.

The catalog covers the dashboard, individual/global logs, service controls,
configuration, updates, dependencies, recovery settings, Metrics, every Settings
section, sign-in/account setup, AI provider forms, all onboarding stages, retained
connection tasks and actual embedded Sonarr. Source-supported differences are
discovered from the selected archive and verified backend capabilities. The
empty `pages/home.vue` artifact is excluded: it contains no user-facing feature.

Coverage distinguishes:

- **Captured:** the actual packaged screen rendered and produced expected files.
- **Unavailable:** the immutable frontend lacks the route/section, or its verified
  backend does not advertise the required capability/protocol.
- **Blocked:** a selector, example API contract, prerequisite or browser request
  failed. A blocked required screen prevents publication.

A selected-scenario probe can complete while full planned coverage remains
incomplete. Automation requires the full required scenario/theme matrix.

## Build an isolated frontend

Archive the plan's verified frontend commit into a fresh task directory. Do not
copy an operator `.env` file or reuse active checkout builds/dependencies.

```bash
capture_root=$(mktemp -d /tmp/dumb-docs-media.XXXXXX)
mkdir "$capture_root/frontend"
git archive --format=tar "$frontend_commit" |
  tar -xf - -C "$capture_root/frontend"
cd "$capture_root/frontend"
corepack pnpm install --frozen-lockfile --store-dir "$capture_root/pnpm-store"
env -i PATH="$PATH" NODE_ENV=production CI=1 COREPACK_ENABLE_DOWNLOAD_PROMPT=0 \
  DMB_API_URL=http://127.0.0.1:9 DUMB_API_URL=http://127.0.0.1:9 \
  DMB_TRAEFIK_URL=http://127.0.0.1:9 DUMB_TRAEFIK_URL=http://127.0.0.1:9 \
  corepack pnpm build
```

Use the immutable backend source to generate the plan with the refresh helper;
do not execute a live backend to obtain configuration or customer data.

## Capture and review

Make this directory available in the frontend container. The pinned Sonarr demo
launcher supplies a temporary empty library on loopback; retain its public image
digest and observed version in the plan. Its runtime origin is an argument only
and is omitted from published manifests.

```bash
node "$runner_dir/capture.mjs" \
  --plan "$capture_root/plan.json" \
  --frontend-root "$capture_root/frontend" \
  --out "$capture_root/captures" \
  --embedded-sonarr-origin http://127.0.0.1:18989/sonarr
```

For a small iteration, add selections such as:

```bash
--scenarios dashboard,metrics,onboarding-review,embedded-sonarr --themes dark
```

The browser has a fresh profile, a fixed starting calendar time that advances
normally, a 1280×800 viewport and actual light/dark application themes. Both
`DMB_` and `DUMB_` API/Traefik targets point only to the task fixture. Unknown API
operations, malformed requests, external traffic, unplanned HTTP errors and
browser errors make the manifest incomplete.

Allowed writes are restricted to harmless in-memory UI preferences, an example
update check, setup-plan reads, and scoped in-memory onboarding simulations.
No application installation, update, service control, acquisition, provider
call, migration or real backup is performed. Simulated progress, result and error
views are labeled examples and are not operational validation. Review shows
selected apps, supporting dependencies, an example existing external app, and
remaining unverified connection tasks.

Metrics uses numeric CPU, memory and task-owned process counters sampled inside
the capture container. It does not inspect operator process command lines,
addresses or identifiers. Other service identities and API fields remain public
examples. Primary Metrics captures turn History off through the real control;
seconds of measurements are never stretched into hours of invented history.

Recording-only pointer, highlight and click cues identify existing controls.
Tools menus remain open for 2.5 seconds, choices are highlighted for 1.6 seconds,
and results remain visible for at least 2.2 seconds. Still navigation uses shorter
waits, and still images omit the cues. The manifest records chapters and pacing.

Review all frames and complete videos. Check readable text, actual action
results, expected light/dark appearance, representative coverage and absence of
private identifiers. Local failure evidence is written under `diagnostics/`
(final route, page/frame text, recent request paths and screenshots); it is never
included in the package. Cleanup closes only the runner's browser, frontend
child, fixture and measurement sampler.

Run focused transport/provenance regressions before an expensive capture:

```bash
node --test "$runner_dir/capture.test.mjs"
```

## Package approved captures

ImageMagick `convert` needs WebP support. Package only a reviewed capture set:

```bash
node "$runner_dir/package.mjs" \
  --plan "$capture_root/plan.json" \
  --captures "$capture_root/captures" \
  --out "$capture_root/packaged"
```

A local-only probe can use `--scope partial`; its incomplete coverage flag remains
in the package and prevents automatic publication. The packager validates source
identity, planned coverage, raw inventory and recorded file hashes. It converts
PNGs to quality-90 WebP without resizing and copies original WebMs.

Schema-2 files use `dark/<scenario>.webp` and `light/<scenario>.webp`, with matching
WebM names/posters where the catalog calls for a recording. The package manifest
records actual capture time, source identities, native application attestation,
measurement provenance, example-operation scope, routes/actions, coverage,
dimensions, byte sizes and SHA-256 hashes. It never contains the runtime Sonarr
origin or operator credentials.

Automation stages versioned packages below
`docs/assets/images/guides/frontend/channels/<channel>/<backend-sha12>-<frontend-sha12>/`.
It updates the shared media catalog in a reviewed PR. Use native playback
controls and posters rather than autoplay. Keep raw captures through visual
review and publication, then clean only task-owned directories. Earlier
schema-1 packages remain readable for reproducing original released media.
