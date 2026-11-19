# Capture the released DUMB frontend

These scripts photograph and record the actual packaged dmbdb frontend. A
loopback fixture supplies public example data; no DUMB backend, provider account,
media library or installation is contacted. The current baseline is frontend
`v1.91.0`, commit `66c90b93ea35abe546c07cbf643dc00a184bbd7f`.

## Build an isolated source archive

Use the frontend's development container as its normal development user. Keep
the active checkout, controllers, `.nuxt`, `.output`, dependencies and staged
work untouched. Verify the published release tag resolves to the full commit
above before building; the capture runner checks package versions but does not
independently verify the remote tag.

Make this scripts directory available inside that container, then archive the
verified source into a new task directory. For example, from the frontend checkout:

```bash
capture_root=$(mktemp -d /tmp/dumb-docs-media.XXXXXX)
mkdir "$capture_root/frontend"
git archive --format=tar 66c90b93ea35abe546c07cbf643dc00a184bbd7f |
  tar -xf - -C "$capture_root/frontend"
cd "$capture_root/frontend"
corepack pnpm install --frozen-lockfile --store-dir "$capture_root/pnpm-store"
env -i PATH="$PATH" NODE_ENV=production CI=1 COREPACK_ENABLE_DOWNLOAD_PROMPT=0 \
  DMB_API_URL=http://127.0.0.1:9 DUMB_API_URL=http://127.0.0.1:9 \
  DMB_TRAEFIK_URL=http://127.0.0.1:9 DUMB_TRAEFIK_URL=http://127.0.0.1:9 \
  corepack pnpm build
```

Use the archive's declared Node and package-manager versions. If Corepack is not
available, invoke that exact pnpm version directly. Do not reuse the active
checkout's dependencies, copy `.env` files, or run its devcontainer setup command.
The isolated build must produce `.output/server/index.mjs` and package version
`1.91.0`.

## Capture and review

With `runner_dir` set to the location of these scripts inside the container:

```bash
node "$runner_dir/capture.mjs" \
  --frontend-root "$capture_root/frontend" \
  --out "$capture_root/captures"
```

The runner loads Playwright and `ws` from the isolated frozen install and starts
only its own frontend and fixture on random loopback ports. It explicitly sets
both `DMB_` and `DUMB_` API/Traefik targets in a minimal child environment. The
browser uses a fresh profile, a fixed example clock, a 1280×800 viewport and
local assets. Unplanned API operations, external traffic, HTTP errors and browser
errors make the manifest incomplete. Supported UI preference saves affect only
the in-memory fixture. Cleanup closes its browser and servers, then waits for its
own frontend child to exit.

The recordings add a visible pointer, a yellow outline around the next control
and a short click pulse. These recording-only cues identify existing controls;
they do not add application controls or change the frontend. Tools menus remain
open for 2.5 seconds, the next menu choice is highlighted for 1.6 seconds before
selection, and results remain visible for at least 2.2 seconds. The manifest
records chapter labels, timing and pacing. Still images omit these cues.

Review every still and all six complete WebM recordings before packaging. Confirm
the controls and text are readable, filters and version checks behave as shown,
and no private identifiers or unrelated application content appear. The
walkthroughs filter/pause logs, check/review an update, switch appearance, and
review dependencies, configuration and auto-restart guardrails. The latter three
leave configuration and service state unchanged. No walkthrough installs an
update. Example progress is not evidence of a completed real operation.

## Package the approved captures

ImageMagick `convert` needs WebP support. Run:

```bash
node "$runner_dir/package.mjs" \
  --captures "$capture_root/captures" \
  --out "$capture_root/packaged"
```

Packaging rejects incomplete/error-bearing manifests and mismatched source
identity. It converts twelve selected PNG frames to quality-90 WebP without
resizing, checks the resulting dimensions, and copies the original short WebMs:

| Output | Captured source |
| --- | --- |
| `dashboard.webp` | `dashboard.png` |
| `service-controls.webp` | `service-controls.png` |
| `service-logs.webp` | `service-logs-poster.png` |
| `updates.webp` | `updates-check-poster.png` |
| `appearance.webp` | `appearance-poster.png` |
| `metrics.webp` | `metrics.png` |
| `embedded-ui-settings.webp` | `embedded-ui-settings.png` |
| `disabled-services.webp` | `disabled-services.png` |
| `about.webp` | `about.png` |
| `configuration.webp` | `configuration-poster.png` |
| `dependencies.webp` | `dependencies-poster.png` |
| `auto-restart.webp` | `auto-restart-poster.png` |
| `service-logs.webm` | `service-logs.webm` |
| `updates.webm` | `updates-check.webm` |
| `appearance.webm` | `appearance.webm` |
| `configuration.webm` | `configuration.webm` |
| `dependencies.webm` | `dependencies.webm` |
| `auto-restart.webm` | `auto-restart.webm` |

The Metrics view contains synthetic system/history measurements. The disabled
services image shows the sidebar's **Show Disabled** option and a filtered
example Tautulli entry; it does not enable that service. Embedded UI settings are
shown without enabling or embedding another application. About shows independent
DUMB and frontend versions. Newer setup, migration and backup flows are outside
this released frontend capture set.

The clean package manifest records the frontend repository/tag/full commit,
example-data scope, viewport, theme, route, actions, byte size and SHA-256 for
each file. Runtime duration inspection and any deliberate video trimming remain
separate review steps; rerun packaging from the reviewed capture set after a
change so hashes describe the actual published bytes.

After review, copy the package to
`docs/assets/images/guides/frontend/v1.91.0/tour-2/`. Keep the earlier media paths
unchanged so updated walkthroughs have a distinct URL. Use the stills as video posters and
show native playback controls; avoid autoplay. Captions should identify the
released frontend version and example responses. Keep the raw captures until
review and publication are complete, then clean only the task-owned directory.

## Build the homepage overview

`overview-scenes.json` defines the caption text, chapter order and timing of the
114-second visual tour. Its application scenes use the reviewed capture package
at normal speed. Introductory cards explain the workflow and deployment choices;
they are illustrations rather than application screens.

The frontend container also needs FFmpeg with `ffprobe` and the `libx264`
encoder, plus ImageMagick WebP support. Run the composer against the reviewed
package and the existing public DUMB logo:

```bash
node "$runner_dir/overview.mjs" \
  --frontend-root "$capture_root/frontend" \
  --media "$capture_root/packaged" \
  --logo "$capture_root/logo.png" \
  --out "$capture_root/overview"
```

Review every chapter and the transitions. Check that menus and selected actions
stay readable, the captions match the visible actions, and essential controls
are not cropped. The composer verifies the input hashes and records the actual
clip ranges. It emits a silent H.264 MP4 with captions in the picture, an image
poster, optional English captions and chapter tracks, and a provenance manifest.
It checks duration, dimensions, absence of audio, the 25 MB size limit and the
MP4's fast-start layout. See the [FFmpeg MP4 documentation](https://ffmpeg.org/ffmpeg-formats.html#mov_002c-mp4_002c-ismv)
for the encoding container.

Publish only `dumb-overview.mp4`, `poster.webp`, `captions.vtt`, `chapters.vtt` and
`manifest.json` under a new `docs/assets/images/guides/overview/<revision>/`
directory. Keep the raw recording out of Git. Update the homepage transcript,
chapter times and video metadata together when scenes change. The SEO audit
checks the homepage's `VideoObject` against its real source, poster and anchor.

The stable sharing link is `https://dumbarr.com/#overview`. A repository README
can link a poster to that page, while the homepage can move to a later revision:

```markdown
[![Watch the captioned DUMB overview](https://dumbarr.com/assets/images/guides/overview/v1/poster.webp)](https://dumbarr.com/#overview)
```
