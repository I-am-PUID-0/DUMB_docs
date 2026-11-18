---
title: Deploying on Proxmox
description: Install DUMB and its managed services natively in a Proxmox VE LXC with the Community Scripts helper, with no Docker layer.
icon: simple/proxmox
---

# Deploying DUMB on Proxmox

The native helper runs DUMB and its managed services directly in one LXC, without a Docker layer. The helper currently uses the maintainer validation branch described below.

This keeps the normal DUMB topology simple:

```text
Proxmox host
└── DUMB LXC
    ├── DUMB API and frontend
    ├── rclone / Decypharr / InfiniDysk
    ├── Arr applications
    └── Plex / Jellyfin / Emby
```

Because every consumer is in the same LXC, DUMB-created FUSE mounts only need
to exist inside that LXC. No mount propagation back to the Proxmox host is
required.

## Install the validation build

While the helper is awaiting upstream acceptance, run the maintainer-fork build from the **Proxmox VE host shell**:

```bash
COMMUNITY_SCRIPTS_URL="https://raw.githubusercontent.com/I-am-PUID-0/ProxmoxVED/feat/dumb" \
  bash -c "$(curl -fsSL https://raw.githubusercontent.com/I-am-PUID-0/ProxmoxVED/feat/dumb/ct/dumb.sh)"
```

`COMMUNITY_SCRIPTS_URL` makes the shared Community Scripts engine fetch the
matching `install/dumb-install.sh` from the same fork and branch. Do not omit it
while using the validation build.

The default controller source is the latest stable DUMB release. For an
advanced test installation, set **DUMB Controller Branch** in the script
generator's app settings or pass `var_dumb_branch` from the host shell. For
example, this installs the current `dev` branch:

```bash
var_dumb_branch=dev \
COMMUNITY_SCRIPTS_URL="https://raw.githubusercontent.com/I-am-PUID-0/ProxmoxVED/feat/dumb" \
  bash -c "$(curl -fsSL https://raw.githubusercontent.com/I-am-PUID-0/ProxmoxVED/feat/dumb/ct/dumb.sh)"
```

Any valid branch in `I-am-PUID-0/DUMB` can be selected. Branch heads are
mutable development targets and may be less stable than a published release;
the same candidate validation and controller rollback protections still apply.
Take an independent backup first: controller rollback restores `/opt/dumb`, but
it does not reverse configuration migrations or application-state changes under
`/config` or `/data`.

!!! warning "Validation build"

    This branch is for controlled testing before the upstream pull request. Use
    a new LXC, keep independent backups, and report the DUMB version plus the
    relevant `journalctl -u dumb` output when a test fails.

After the script is validated, submitted to `community-scripts/ProxmoxVED`, and
promoted into `community-scripts/ProxmoxVE`, the production command will become:

```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/community-scripts/ProxmoxVE/main/ct/dumb.sh)"
```

The default installation creates an unprivileged Debian 13 LXC with:

- 4 vCPU;
- 8 GiB RAM;
- 40 GiB disk;
- FUSE enabled for rclone and other DUMB-managed mounts;
- optional Intel/AMD GPU device passthrough; and
- DUMB plus its required runtimes installed directly on the guest OS.

Use **Advanced Settings** when a large stack, source builds, the install cache,
or a media server needs more resources. Both amd64 and arm64 have completed the
recorded native acceptance tests with DUMB 2.21.0: clean Proxmox VE installation,
controller update and rollback, reboot, FUSE namespace isolation, and stopped
backup/restore. That qualification applies to the tested versions; it does not establish every later application update or GPU path.

When installation finishes, open:

```text
http://<DUMB-LXC-IP>:3005
```

The frontend can take several minutes to appear on first boot while DUMB
installs its initial managed services. Follow progress inside the LXC with:

```bash
journalctl -u dumb -f
```

Then continue with [Getting Started](../getting-started/index.md).

## .NET repository checks

Debian 13 has an [official Microsoft .NET feed](https://learn.microsoft.com/en-us/dotnet/core/install/linux-debian).
An updater message claiming that the feed does not exist can also come from a
failed network probe.

The DUMB install/update scripts wrap the existing Community Scripts .NET
installer with a local repository check. On Debian, this check runs before the
shared installer can remove an existing Microsoft source/keyring, retries
transient failures, and reuses a successful result for the duration of that
.NET setup invocation. Failed checks stop the update before repository changes.
The wrapper also avoids the shared probe's reversed cached success/failure
handling without modifying core or changing checks for other applications.

Use the updated DUMB helper scripts for this fix; updating only DUMB's Python
controller does not change native runtime reconciliation. No core fork or
`COMMUNITY_SCRIPTS_CORE_URL` override is required. Existing running services
remain on the previous controller if dependency reconciliation fails before
activation.

## Native LXC paths

| LXC path | Purpose |
|---|---|
| `/opt/dumb` | DUMB controller source and Python environment |
| `/config` | DUMB configuration, authentication state, snapshots, and feature state |
| `/data` | Persistent managed-service data |
| `/log` | DUMB and managed-service logs |
| `/mnt/debrid` | FUSE mounts, generated links, and symlink libraries |
| `/postgres_data` | DUMB-managed PostgreSQL cluster when enabled |
| `/zurg/config.yml`, `/zurg/plex_update.sh` | Base Zurg files copied into newly configured Zurg instances |
| `/etc/dumb/controller-source` | Root-managed stable or branch selection used by `update` |
| `/etc/systemd/system/dumb.service` | Native DUMB systemd service |

These are normal LXC filesystem paths, not Docker bind mounts. DUMB preserves
its established internal paths so the same service configuration works in the
native and container-image deployments.

The helper also configures `systemd-logind` to retain IPC owned by DUMB's
managed-service UID. This is required for PostgreSQL POSIX shared memory after
temporary setup sessions end. Package-provided PostgreSQL, Plex, and Jellyfin
systemd units are kept inactive because DUMB, not the distribution unit, supervises
those processes inside this dedicated LXC.

## GPU passthrough and Jellyfin

When GPU passthrough is enabled, the installer invokes the Community Scripts
hardware-acceleration helper to select the vendor's drivers and required Debian
repository components. The update path also reconciles drivers when updating
the controller. Intel GPU support requires the appropriate VA-API driver;
OpenCL tone mapping additionally depends on a compute runtime compatible with
the GPU generation. Installing a package does not prove either path works.

DUMB creates and maintains its own service account. Adding only the
package-created `jellyfin` account to `render`/`video` does not grant access to
DUMB's Jellyfin process. After applying the installer and controller fixes,
restart DUMB and inspect the actual Jellyfin process:

```bash
pgrep -a -f '/usr/lib/jellyfin/bin/jellyfin'
ls -ln /dev/dri/renderD*
# Replace <PID> with the Jellyfin PID shown above.
grep -E '^(Uid|Gid|Groups):' /proc/<PID>/status
```

The command should select `/usr/lib/jellyfin-ffmpeg/ffmpeg` unless a custom path
was configured. The process's primary or supplementary groups must include the
render device's numeric GID. For an unprivileged LXC, unmapped ownership must be
corrected in the Proxmox device mapping; making render nodes world-writable is
not required by DUMB.

Verify playback by forcing a transcode and checking the Jellyfin FFmpeg log for
the selected binary, QSV/VA-API codec, and successful device initialization.
Testing only as root can conceal service-user permission failures. See the
[Jellyfin service guide](../services/core/jellyfin.md#hardware-acceleration).

### Intel OpenCL tone mapping

QSV/VA-API video acceleration and OpenCL tone mapping use separate Intel
runtimes. QSV can keep working after a compute-runtime update drops support for
an older GPU. An OpenCL error such as `CL_PLATFORM_NOT_FOUND_KHR` or
`Failed to get number of OpenCL platforms: -1001` means that no OpenCL platform
was available to that process.

!!! note "Unreleased native helper correction"

    The native helper correction adds Intel's
    [legacy compute runtime](https://github.com/intel/compute-runtime/blob/master/documentation/LEGACY_PLATFORMS.md)
    alongside the current runtime for its supported Intel GPU setup path on
    amd64 Debian 13 (trixie). This includes Gen9–Gen11 GPUs recognized by that
    path; older GPU setup paths are unchanged.

    Once the corrected helper is published, run `update` inside the LXC.
    Selecting DUMB's `dev` controller branch or updating Jellyfin alone does
    not install this helper change. The helper checks OpenCL device enumeration
    and warns if no Intel GPU is found.

Check the installed compute packages and ICD registrations inside the LXC:

```bash
dpkg-query -W 'intel-opencl*' 'intel-igc*'
ls -l /etc/OpenCL/vendors/
```

Then check OpenCL as the account running DUMB's Jellyfin process, using the PID
from the earlier process check:

```bash
ps -o user=,pid=,args= -p <PID>
# Replace <service-user> with the account shown above.
runuser -u <service-user> -- clinfo -l
```

The output should list an Intel GPU platform and device. This checks runtime
loading and device access; it does not prove that Jellyfin's FFmpeg can use
OpenCL with QSV. After applying the corrected native helper, force an HDR-to-SDR
transcode with tone mapping enabled and inspect its FFmpeg log. A listed
`tonemap_opencl` filter or `opencl` hardware-acceleration type only describes
FFmpeg's compiled features.

If playback still fails, include the package versions, `clinfo` output and
Jellyfin FFmpeg error in the report.

## Manage and update DUMB

Useful commands inside the LXC:

```bash
systemctl status dumb
journalctl -u dumb -f
systemctl restart dumb
```

Run the Community Scripts updater inside the LXC to update the currently
selected DUMB source. Stable installations follow the latest published release,
while branch installations follow the current head of their saved branch:

```bash
update
```

To switch an existing LXC to `dev` or another DUMB branch, pass the branch for
one update run:

```bash
DUMB_CONTROLLER_BRANCH=dev update
```

The branch choice is saved only after the candidate starts and passes the API
health check, so later `update` runs continue following it. Return to the stable
release channel with:

```bash
DUMB_CONTROLLER_BRANCH=latest update
```

Switching back to stable can be a controller downgrade. Verify that the branch
did not introduce configuration or data changes that the stable release cannot
read before making that switch.

The updater reconciles the required native dependencies, downloads the new
controller into a candidate directory, builds its locked Python environment,
and validates it while the current controller is still running. It then backs
up `/opt/dumb`, stops DUMB only for activation, starts the candidate, and waits
for the API health check. A failed build, start, or health check automatically
restores and verifies the previous controller. An interrupted update is
recovered the next time `update` runs.

Configuration and managed application data under `/config`, `/data`,
`/postgres_data`, and `/mnt/debrid` remain outside the replaced controller
directory. The update backup is removed after the replacement passes health
verification.

Use DUMB's own Updates controls for the individual services it manages.

## Backups and FUSE

Back up at least `/config` and `/data`, plus any application-native backups
required by the services you enabled. `/mnt/debrid` normally contains live or
re-creatable mount views and should not be treated as the only copy of data.

!!! warning "Proxmox snapshot backups and FUSE"

    Proxmox [strongly advises against FUSE mounts inside an LXC](https://pve.proxmox.com/pve-docs/pct.1.html)
    because freezing the container for suspend/snapshot-mode backups can fail.
    Prefer a stopped-mode backup window after stopping DUMB, or otherwise test
    the exact backup mode and mount stack before relying on it.

## Existing Plex or Arr applications in other LXCs

An external Plex or Arr LXC cannot see `/mnt/debrid` merely because it uses the
same path name. It needs a separately designed storage boundary that exposes
both the symlink library and every target path those symlinks reference.

The helper deliberately does not add that boundary automatically. Reverse
propagation of a mount created inside an LXC depends on the host mount namespace,
LXC propagation flags, FUSE permissions, UID/GID mappings, backup behavior, and
the consumer's own mount namespace. A configuration that gets one of those
boundaries wrong can look healthy until a remount leaves Plex or an Arr app on
a stale path.

Choose one of these approaches:

1. Move the consumer into the DUMB LXC. This is the supported and simplest
   layout.
2. Mount the remote storage on the Proxmox host, then bind-mount the same
   host-managed tree into DUMB and every consumer LXC. In that layout, disable
   the duplicate DUMB-managed rclone mount and keep the same absolute paths in
   all applications.
3. Export the complete DUMB mount/link tree through a deliberately managed
   network filesystem and mount it in each consumer. Validate symlink target
   paths, permissions, disconnect/reconnect behavior, and startup ordering.
4. Build a custom `rshared`/`rslave` LXC topology only after proving mount and
   unmount propagation in both directions on the exact Proxmox/LXC version.

!!! danger "Do not add a host mount over an active `/mnt/debrid`"

    A new bind mount hides the directory that was previously at that path. If
    DUMB is already configured, stop it, take independent backups, and migrate
    the mount and symlink trees deliberately. Never attach an empty host path
    over an active deployment and assume the old files moved into it.

For a custom propagation topology, verify all of the following before allowing
an Arr import or media-server scan:

```bash
# DUMB LXC
findmnt -R /mnt/debrid
findmnt -no TARGET,PROPAGATION /mnt/debrid

# Proxmox host and every consumer LXC
findmnt -R <shared-path>
readlink <representative-symlink>
```

Test a provider remount while each consumer is running. A consumer should see
the replacement mount without retaining `Transport endpoint is not connected`.
Also confirm that consumer unmounts cannot propagate back and tear down DUMB's
producer mount.

## Troubleshooting

### The DUMB page is unavailable

Inside the LXC:

```bash
systemctl status dumb --no-pager
journalctl -u dumb -n 200 --no-pager
ss -lntp | grep -E ':(8000|3005)\b'
```

The API normally listens on port `8000`; the user-facing frontend is port
`3005`. The LXC firewall and network must allow the frontend port from your
operator workstation.

### `/dev/fuse` is missing

On the Proxmox host, inspect the generated container configuration:

```bash
pct config <CTID> | grep -E 'features|dev/fuse'
```

The Community Scripts default enables FUSE. Stop and start the LXC after fixing
its configuration; restarting only the DUMB service cannot add a missing device
to the LXC.

### A managed service cannot find a runtime

Confirm the native toolchain and controller environment:

```bash
python3.11 --version
python3.12 --version
node --version
pnpm --version
go version
dotnet --info
rclone version
/opt/dumb/venv/bin/python -m pip check
```

Run `update` to repair the DUMB controller source/environment. Service-specific
install failures remain visible in `journalctl -u dumb` and can then be retried
from the DUMB UI.

### PostgreSQL reports a missing shared-memory segment

If several PostgreSQL-backed services fail together and the journal contains
`could not open shared memory segment "/PostgreSQL..."`, verify the native LXC
safeguard:

```bash
systemd-analyze cat-config systemd/logind.conf | grep -A2 dumb.conf
```

The effective configuration must include `RemoveIPC=no`. Run `update`, then
restart DUMB, if the drop-in is absent. A healthy restart recreates the
PostgreSQL shared-memory objects and keeps them after the managed UID's setup
session closes.

### Plex fails to install or cannot create its Cache directory

Older test builds created a direct `/etc/systemd/system/plexmediaserver.service`
mask before Plex was installed. Plex's Debian package rejects that path during
its pre-install check. If the package was then repaired manually, the generated
`/plex/Plex Media Server` tree could also remain owned by the package account.

Current LXC helpers use a supported systemd drop-in with an unmet condition.
That lets the Debian package install successfully without starting its own Plex
process; DUMB remains the only process supervisor and repairs the writable tree.

```bash
test ! -e /etc/systemd/system/plexmediaserver.service
systemctl cat plexmediaserver.service | grep -F 'ConditionPathExists=/run/dumb-allow-package-services'
systemctl is-active plexmediaserver.service
```

The first command should produce no output, the second should show the condition,
and the package-owned unit should report `inactive`. For an LXC created with an
older test build, reconcile the helper and restart the DUMB controller:

```bash
update
systemctl restart dumb
```

If `dpkg` still reports an interrupted installation, complete its pending work
after `update` has removed the legacy mask:

```bash
dpkg --configure -a
apt-get -f install
```

## Related pages

- [Getting Started](../getting-started/index.md)
- [Configuration](../features/configuration.md)
- [Docker deployment](docker.md)
- [Docker networking and ports](networking.md)
