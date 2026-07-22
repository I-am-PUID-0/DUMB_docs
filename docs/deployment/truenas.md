---
title: Deploy with TrueNAS
icon: simple/truenas
---

# Deploy with TrueNAS SCALE

TrueNAS SCALE 24.10 and later use Docker for Apps and can deploy a custom
application from Docker Compose YAML. Older 24.04 and earlier releases use the
archived Kubernetes app model and are not covered by this Compose procedure.

## Prerequisites

- TrueNAS SCALE 24.10 or later with an Apps pool selected
- Datasets/directories for DUMB's persistent storage
- Dataset ACLs that permit the selected `PUID:PGID` to read and write
- FUSE device/capability support if the selected workflow uses rclone/FUSE

TrueNAS documents the current editor under
[Install Custom App via YAML](https://www.truenas.com/docs/scale/apps/installcustomappscreens/#add-custom-app-screen).

## Create datasets and directories

Create a dedicated dataset such as `tank/apps/dumb`, then create:

```text
/mnt/tank/apps/dumb/
├── config/
├── data/
├── log/
└── mnt/debrid/
```

Use your actual pool/dataset name. Host-path datasets are easier to back up and
inspect than hidden app-managed volumes. Set ACLs/ownership for the UID/GID DUMB
will run as; the TrueNAS `apps` user's default IDs are not automatically the
right IDs for DUMB.

## Install via YAML

1. Open **Apps** → **Discover Apps**.
2. Use the menu beside **Custom App** and choose **Install via YAML**.
3. Name the app `dumb`.
4. Paste the current
   [DUMB Compose file](https://github.com/I-am-PUID-0/DUMB/blob/master/docker-compose.yml).
5. Replace `/home/username/docker/DUMB` with `/mnt/tank/apps/dumb`.
6. Set `TZ`, `PUID`, and `PGID`, then save the app.

The storage section should resemble:

```yaml
volumes:
  - /mnt/tank/apps/dumb/config:/config
  - /mnt/tank/apps/dumb/log:/log
  - /mnt/tank/apps/dumb/data:/data
  - /mnt/tank/apps/dumb/mnt/debrid:/mnt/debrid
```

Open `http://<truenas-address>:3005` after the workload starts. The frontend
proxies DUMB's API under `/api`; do not expose native backend port `8000` unless
you deliberately change its bind address, enable authentication, and restrict
network access.

## FUSE and external media servers

The maintained Compose file includes `/dev/fuse`, `SYS_ADMIN`, and an unconfined
AppArmor profile. Keep them for mount-producing workflows. Remove `/dev/dri`
only if that device is absent and no configured service needs it.

If another TrueNAS App must see submounts created by DUMB, use `:rshared` on
DUMB's `/mnt/debrid` host bind and a compatible slave propagation mode in the
consumer. TrueNAS performs only basic YAML validation, so verify the effective
container mounts after deployment rather than assuming the UI accepted every
Compose option.

## Updates and backups

- Edit/redeploy the custom app to adopt Compose changes and pull a new image.
- Back up `config` and service data under `data`; preserve the chosen workflow's
  library/link state under `mnt/debrid` where applicable.
- Dataset snapshots are useful, but database-aware logical backups are still
  required for PostgreSQL portability. See [PostgreSQL FAQ](../faq/postgres.md).

Continue with [Getting Started](../getting-started/index.md).
