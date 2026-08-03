---
title: Rclone Streaming Optimizer
description: Benchmark bounded rclone VFS profiles through NzbDAV and its live Usenet providers, compare startup and streaming performance, and explicitly apply or roll back a recommendation.
icon: lucide/gauge
---

# Rclone Streaming Optimizer

The rclone streaming optimizer measures how an **NzbDAV-backed DUMB-managed rclone instance** behaves on the current deployment. It accounts for the combined effects of the provider, network, CPU, memory, cache storage, NzbDAV, and rclone instead of assuming one flag set is right for every server.

The optimizer is currently limited to NzbDAV. It appears on the specific **rclone service page**, not as an NzbDAV configuration tool. When an associated test is active, the NzbDAV service page shows a link to that rclone job.

## What the test actually reads

Each candidate uses this path:

```text
DUMB-managed Arr instance -> active NzbDAV category
  -> production rclone mount/content/<category> (metadata discovery only)
  -> safe mount-relative read path
  -> optimizer reader
  -> isolated read-only rclone shadow mount
  -> NzbDAV WebDAV
  -> NzbDAV's configured Usenet provider(s)
```

The shadow mount uses the same rclone remote/configuration as the production mount, but has its own mount path, VFS cache directory, and loopback RC port. It does not stop the production mount, purge its cache, or reuse its cache for candidate reads.

DUMB uses the production mount only for bounded directory metadata discovery.
It does not measure file reads there because that would reuse the production VFS
cache and make candidate comparisons unreliable. Each category entry is resolved
to a safe mount-relative read path and opened on every isolated shadow mount. For
a regular entry this can be `content/radarr-nzbdav/example.mkv`; a symlink-backed
entry can resolve to its mount-internal backing path while the UI retains the
friendly category path.

These are **real provider reads**. They can consume provider traffic and are subject to provider connection, automation, and acceptable-use policies.

!!! warning "Stop media activity before testing"

    Stop Plex, Jellyfin, Emby, and any other media server before starting the
    optimizer. Wait until NzbDAV is idle with no active imports, library
    ingestion, or unrelated reads. In particular, do not benchmark while NzbDAV
    is importing an entire existing library.

    Playback, media-library scans, imports, and other reads compete for the same
    provider connections, bandwidth, CPU, memory, cache storage, and disks. This
    can distort startup and throughput measurements, produce an unsuitable
    recommendation, and add unnecessary load against the configured providers.

## Measurements

For every candidate and selected file, DUMB records:

- file-open time;
- time to first byte;
- time to fill the configured startup buffer (32 MiB by default);
- early/sequential throughput;
- seek latency near the end of the file;
- rclone process memory, CPU, cache use, and RC statistics; and
- NzbDAV active reads, bytes, errors, provider latency, retries, circuit state, failover data, and stream-trace count when the maintained NzbDAV API supplies them.

Failed or unavailable files remain visible in the report but are excluded from performance scoring. The recommendation score favors startup time and first-byte latency while also considering seek latency, throughput, resource use, and excluded/error samples.

The report distinguishes **trace capture unavailable** from **no matching retained
trace**. If NzbDAV tracing cannot be enabled, rclone performance measurements can
still complete, but provider-level event correlation is explicitly marked
unavailable instead of being presented as a path-matching result.

### Reading NzbDAV provider evidence

The four summary values in each expanded provider-evidence panel come from the
NzbDAV overview window captured after that candidate. They are not isolated to
the candidate and can include unrelated NzbDAV traffic. Candidate-specific
evidence appears in the matched retained stream traces below them. This is one
reason the media server and NzbDAV should be idle during testing.

| Field | Meaning |
|---|---|
| Provider p50 | Median provider-fetch latency in NzbDAV's overview window; half of observed provider fetches completed at or below this duration |
| Provider p95 | 95th-percentile provider-fetch latency; 95% completed at or below this duration and the slowest 5% took longer |
| Errors/min | NzbDAV's recent error rate per minute across the overview window, including any unrelated activity |
| Throttle events | NzbDAV in-flight article throttle events reported by the overview snapshot |
| Providers | Provider nicknames recorded in a candidate-matched retained stream session |
| Retries | Sum of retry counts in the matched session's retained events |
| Bytes | Bytes served recorded by retained events in that matched trace |
| Provider wait | Cumulative retained-event time spent waiting on provider work |
| Connection wait | Cumulative retained-event time spent acquiring a provider connection |

## Content selection

Open the NzbDAV-backed rclone service and select **Rclone Optimizer**. DUMB first
reuses the same Arr-to-NzbDAV category derivation used during integration setup.
Only enabled Radarr, Sonarr, Lidarr, and Whisparr instances whose `core_service`
includes `nzbdav` contribute categories. For example, a Radarr instance named
`NzbDAV` produces `radarr-nzbdav`.

The configured rclone instance supplies the user-defined mount base through
`mount_dir` plus `mount_name`. DUMB scans only
`<mount>/content/<active-category>`, reports missing/empty categories in the
panel, and suggests a small, stratified set:

- recently modified content, which is more likely to be warm;
- older content, which is more likely to be cold;
- a large/high-bitrate candidate; and
- a typical file near the middle of the observed set.

These files are representative automatic suggestions, not mandatory choices.
They are pinned to the top of the picker and labeled with the selection reason,
such as **Recent / likely warm**, **Older / likely cold**, **Largest /
high-bandwidth candidate**, or **Typical / median-age candidate**. Keep the
automatic set, replace it with your own files, or mix automatic and manual
choices up to the eight-file limit. **Restore automatic selection** returns to
the suggested starting set after manual changes.

Age is only a **cache-likelihood heuristic**. It does not prove whether an article is cached by NzbDAV or a provider. The report keeps recent/likely-warm and older/likely-cold startup results separate, while NzbDAV's live metrics and stream traces explain what happened during the reads.

You can replace the automatic selection with any listed media files. Select between one and eight files. The scan is intentionally bounded by file count and time so discovering content does not recursively enumerate an unlimited remote library. No `/mnt/debrid/...` mount path or category name is hard-coded into the optimizer.

## Candidate matrix

The optimizer does not try every possible rclone flag permutation. That would consume excessive time and provider traffic while producing noisy results. Instead, it tests known-shape profiles:

| Depth | Profiles | Purpose |
|---|---:|---|
| Quick | 2 | Current tuning with the cache ceiling enforced, and one balanced alternative |
| Standard | 4 | Bounded current tuning, balanced, lower-memory, and fast-start profiles |
| Thorough | 6 | Standard profiles plus high-throughput and large-chunk variants |

The report deliberately separates the settings into four roles:

| Role | Values | Meaning |
|---|---|---|
| Actually varied | `--buffer-size`, `--vfs-read-chunk-size`, `--vfs-read-chunk-size-limit`, `--vfs-read-ahead` | Streaming-oriented dimensions that differ across predefined alternative profiles and drive the bundle comparison |
| Fixed test constraints | `--vfs-cache-max-size`, bandwidth, memory, free disk, duration, and concurrency | Deployment-specific safety/resource boundaries held constant across every candidate; these are not tuned |
| Bundled assumptions | `--vfs-cache-mode`, `--vfs-cache-max-age`, `--dir-cache-time` | Profile assumptions changed together rather than independently; a winning profile does not prove any one of these values is optimal |
| Preserved | Every other existing user flag | Passed into each shadow command unchanged and not evaluated, except for the temporary isolation/safety plumbing described below |

The UI shows the complete optimizer-relevant effective settings for **every**
candidate, including current-to-tested changes and the role of each value. The
winning recommendation is therefore a **bundle recommendation**, not a claim
that every displayed setting was individually optimized.

Preserved flags are outside the optimizer's intended streaming dimensions and
normally should not determine this comparison. However, an unusual custom
rclone flag can still change runtime behavior and must be reviewed manually.
Their values are intentionally omitted from public job reports because rclone
commands can contain credentials or other private values. The remote source,
provider credentials, filtering, and user behavior flags remain preserved, and
the production mount command is not modified during testing.
The shadow process necessarily substitutes its temporary mount path and cache
directory, binds a loopback RC endpoint without production RC credentials,
forces read-only behavior and a test log level, and optionally adds the fixed
bandwidth ceiling. Those isolation controls are not candidate tuning dimensions.

In particular, `--dir-cache-time` governs directory metadata refresh and should
not determine media-byte throughput once a file is open.
`--vfs-cache-max-age` primarily governs retention of inactive cached data between
reads. `--vfs-cache-mode` establishes VFS behavior and can matter, but is tested
only as a bundled prerequisite. The UI explains the expected streaming relevance
of each displayed flag; these statements describe expected scope, not a guarantee
that arbitrary custom combinations can never influence playback.

## Safety limits

The values initially shown in the optimizer are **generic starting placeholders,
not recommendations**. DUMB does not derive them from the deployment's CPU, RAM,
cache disk, ISP bandwidth, NzbDAV activity, or provider policy. Review and change
every value for the current hardware and provider before starting a job. The UI
provides a native tooltip on each control explaining its purpose.

Configure the limits before starting a job:

| Limit | Default | Behavior |
|---|---:|---|
| Maximum VFS cache | 5 GiB | Passed to each isolated candidate as `--vfs-cache-max-size` |
| Minimum free disk | 10 GiB | Checked before and during testing; reaching it stops the matrix |
| Maximum optimizer memory | 2048 MiB | Candidates over the limit are rejected and further testing stops |
| Maximum test/provider budget | 4 GiB | Shared requested-read budget, reconciled with NzbDAV's observed provider-byte delta after each profile |
| Maximum duration | 20 minutes | Shared wall-clock deadline for the job |
| Concurrent streams | 1 | May be raised to 3 only when deliberate concurrency testing is needed |
| Startup buffer target | 32 MiB | Amount read before startup time is considered satisfied |
| Bandwidth limit | Unlimited | Optional Mbps ceiling, converted to rclone's byte-rate limit |

!!! warning "VFS maximum is not a hard filesystem quota"

    `--vfs-cache-max-size` drives rclone eviction. Temporary overshoot can occur, so retain free-space headroom and use the minimum-free-disk guard.

!!! note "Provider budget can have a small final overshoot"

    The reader stops reserving bytes at the configured shared limit, and DUMB also subtracts NzbDAV's observed provider-byte delta after each profile. Rclone chunking/read-ahead and in-flight provider requests can fetch beyond the exact bytes consumed by the reader, so this is a conservative safety control rather than a provider-side quota.

Testing stops early when NzbDAV indicates a provider circuit is open or reports strong throttling/authentication/rate-limit signals. Errors, retries, and failover remain in the report. This reduces provider risk but cannot guarantee that a provider will permit benchmarking; review your provider's rules and keep concurrency/data limits conservative.

## Background jobs and notifications

The job continues in the DUMB backend when you close the panel or navigate away. The rclone service page keeps an active-job banner, and the frontend posts a completion or failure toast while it is open. If DUMB notifications are configured for the optimizer event types, the backend can also queue the completion/failure event.

If DUMB restarts during a test, the job is marked **interrupted**, the temporary mount/cache is cleaned up, and the matrix is not resumed. Start a fresh test so candidate conditions remain comparable.

Each candidate verifies that its isolated shadow mount is no longer mounted
before the result is accepted. Before a job can report **completed**, DUMB also
verifies that all job shadow mounts, the runtime directory, and the candidate
cache directory are gone. The rclone page reports those three cleanup checks. If
cleanup cannot be verified, the job fails instead of presenting a completed
recommendation, leaves the runtime path available for a later safe retry, and
retries cleanup during finalization and the next DUMB startup.

## Apply and rollback

Finishing a test creates a report and recommendation. It does **not** change rclone.

1. Review every candidate's complete settings/roles, warm/cold samples, exclusions, resources, cleanup status, and NzbDAV evidence.
2. Select **Apply recommendation**.
3. DUMB merges only the recommended optimizer flags into the saved rclone command.
4. DUMB restarts that rclone process and verifies its production mount.

The pre-apply command is stored privately in the job record. Select **Roll back** to restore it, restart rclone, and verify the mount again. If apply fails, DUMB attempts that rollback automatically.

## Provider-risk guidance

- Start with **Quick**, one stream, and a small data budget.
- Do not run repeated tests back-to-back merely to chase small score changes.
- Avoid testing while normal users are already saturating the provider or ISP connection.
- Treat retries, failover, open circuits, authorization failures, and rate-limit messages as reasons to stop and investigate.
- Do not assume older content is uncached or recent content is cached.
- Keep the report as deployment-specific evidence; another user's result is not a universal rclone preset.

## Related guides

- [rclone service](../services/dependent/rclone.md)
- [NzbDAV](../services/core/nzbdav.md)
- [Service pages](../frontend/service-pages.md)
- [Process Management API](../api/process.md#rclone-streaming-optimizer)
