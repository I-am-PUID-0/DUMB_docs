---
title: Deploying on Proxmox
description: Install DUMB and its managed services natively in a Proxmox VE LXC with the Community Scripts helper, with no Docker layer.
icon: simple/proxmox
---

# Deploying DUMB on Proxmox

The recommended Proxmox layout runs DUMB and its managed services directly in
one LXC. It does **not** install Docker inside the LXC.

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

Until the script has completed LXC validation and been accepted upstream, run
the maintainer-fork build from the **Proxmox VE host shell**:

```bash
COMMUNITY_SCRIPTS_URL="https://raw.githubusercontent.com/I-am-PUID-0/ProxmoxVED/feat/dumb" \
  bash -c "$(curl -fsSL https://raw.githubusercontent.com/I-am-PUID-0/ProxmoxVED/feat/dumb/ct/dumb.sh)"
```

`COMMUNITY_SCRIPTS_URL` makes the shared Community Scripts engine fetch the
matching `install/dumb-install.sh` from the same fork and branch. Do not omit it
while using the validation build.

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
or a media server needs more resources. The amd64 path has completed the native
acceptance tests. The arm64 path is implemented but remains marked unverified
by Community Scripts until it passes the same clean Proxmox VE install, reboot,
FUSE, backup, restore, and update tests. An interactive arm64 run can opt into
testing; unattended arm64 installation remains blocked until that validation is
complete.

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

## Native LXC paths

| LXC path | Purpose |
|---|---|
| `/opt/dumb` | DUMB controller source and Python environment |
| `/config` | DUMB configuration, authentication state, snapshots, and feature state |
| `/data` | Persistent managed-service data |
| `/log` | DUMB and managed-service logs |
| `/mnt/debrid` | FUSE mounts, generated links, and symlink libraries |
| `/postgres_data` | DUMB-managed PostgreSQL cluster when enabled |
| `/etc/systemd/system/dumb.service` | Native DUMB systemd service |

These are normal LXC filesystem paths, not Docker bind mounts. DUMB preserves
its established internal paths so the same service configuration works in the
native and container-image deployments.

The helper also configures `systemd-logind` to retain IPC owned by DUMB's
managed-service UID. This is required for PostgreSQL POSIX shared memory after
temporary setup sessions end. Package-provided PostgreSQL, Plex, and Jellyfin
systemd units are masked because DUMB, not the distribution unit, supervises
those processes inside this dedicated LXC.

## Manage and update DUMB

Useful commands inside the LXC:

```bash
systemctl status dumb
journalctl -u dumb -f
systemctl restart dumb
```

Run the Community Scripts updater inside the LXC to install a newer stable DUMB
release:

```bash
update
```

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

### Plex reports port 32400 already in use during first setup

The Plex Debian package can start its own `plexmediaserver.service` while DUMB
is preparing the managed instance. The LXC helper masks that package unit so
only DUMB owns Plex and port `32400`:

```bash
systemctl is-enabled plexmediaserver.service
```

The expected result is `masked`. If an LXC created with an earlier test build
reports `enabled`, run `update` and restart DUMB before retrying Plex onboarding.

## Related pages

- [Getting Started](../getting-started/index.md)
- [Configuration](../features/configuration.md)
- [Docker deployment](docker.md)
- [Docker networking and ports](networking.md)
