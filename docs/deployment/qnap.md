---
title: Deploy with QNAP
icon: simple/qnap
---

# Deploy with QNAP Container Station

QNAP Container Station can create a Docker Compose application from YAML. The
labels can vary slightly by Container Station/QTS version, but the official flow
is **Create** → **Create Application** → paste and validate the Compose YAML.

## Prerequisites

- A QNAP model/architecture supported by the DUMB image (`amd64` or `arm64`)
- Container Station installed and current
- Shared folders for persistent DUMB data
- A QNAP user UID/GID with read/write access to those folders
- FUSE device/capability support if the selected workflow creates FUSE mounts

See QNAP's
[Creating an Application](https://docs.qnap.com/operating-system/qne-network/1.0.x/en-us/container-creation-1A95801A.html#creating-an-application)
instructions for the Compose application workflow.

## Prepare the shared folders

Create a DUMB directory under a persistent share, with these subdirectories:

```text
/share/Container/DUMB/
├── config/
├── data/
├── log/
└── mnt/debrid/
```

Your QNAP share name can differ. Use its absolute host path in the Compose file
and grant the selected `PUID:PGID` ownership or read/write access.

## Create the application

1. Download or copy the current
   [DUMB Compose file](https://github.com/I-am-PUID-0/DUMB/blob/master/docker-compose.yml).
2. In Container Station, open **Create** → **Create Application**.
3. Name the application `dumb` and paste the YAML.
4. Replace `/home/username/docker/DUMB` with `/share/Container/DUMB` (or your
   actual share path).
5. Set `TZ`, `PUID`, and `PGID`.
6. Validate the YAML and create the application.

The persistent mounts should be:

```yaml
volumes:
  - /share/Container/DUMB/config:/config
  - /share/Container/DUMB/log:/log
  - /share/Container/DUMB/data:/data
  - /share/Container/DUMB/mnt/debrid:/mnt/debrid
```

The maintained Compose file publishes the DUMB frontend on `3005`. Open
`http://<qnap-address>:3005` after the application becomes healthy.

## FUSE and external consumers

The maintained Compose file requests `/dev/fuse`, `SYS_ADMIN`, and an unconfined
AppArmor profile. Keep those entries for workflows that mount with rclone/FUSE.
Availability depends on the QNAP kernel and Container Station version; if the
application rejects them, check the QNAP host before removing the settings.

When another container must see a DUMB-created submount, use `:rshared` on the
DUMB `/mnt/debrid` bind and `:rslave` on the consumer bind. If Container Station
cannot preserve those propagation modes, use an all-in-one DUMB workflow or a
workflow based on ordinary files/symlinks instead of assuming external FUSE
mounts will propagate.

## Update and recover

- Pull `iampuid0/dumb:latest`, then recreate/redeploy the application.
- Preserve `/share/Container/DUMB/config`, `data`, `log`, and `mnt/debrid`.
- Use Container Station logs first; then review [Troubleshooting](../faq/dumb.md)
  and [Service ports](../reference/ports.md).

Do not publish backend port `8000` for normal use. The frontend proxies the API
under `http://<qnap-address>:3005/api`.
