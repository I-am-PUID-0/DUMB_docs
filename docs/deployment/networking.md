---
title: Docker networking and ports
description: Choose between Docker bridge port publishing and host networking for DUMB, with Compose examples, security tradeoffs, and WSL considerations.
icon: lucide/network
---

# Docker Networking and Ports

Docker controls how applications inside the DUMB container become reachable
from the Docker host and other devices. Choose one of the following Compose
configurations.

| | Selected port publishing | Host networking |
|---|---|---|
| Compose setting | `ports:` | `network_mode: host` |
| Exposed listeners | Only listed ports | All non-loopback listeners |
| Host-to-container port translation | Supported | Not available |
| Docker network isolation | Retained | Removed |
| Best for | Most installations | Direct access to many service ports |

!!! note "WSL users"

    On WSL, the Docker host is the Linux distribution running inside WSL.
    Complete the [WSL mirrored networking configuration](wsl.md#mirrored-mode-networking)
    before using the Windows machine's IPv4 address to access DUMB.

## Option 1: Publish Selected Ports (Recommended)

The maintained DUMB Compose file uses Docker's normal bridge networking and
publishes only the DUMB Frontend:

```yaml
services:
  DUMB:
    ports:
      - "3005:3005"
```

Open the dashboard at:

```text
http://localhost:3005
http://<docker-host-ip>:3005
```

Add another mapping for each service that must be accessed directly. For
example:

```yaml
services:
  DUMB:
    ports:
      - "3005:3005" # DUMB Frontend and API gateway
      - "7878:7878" # Radarr
      - "8989:8989" # Sonarr
      - "32400:32400" # Plex
```

Use the [Service ports](../reference/ports.md) reference and the actual port
saved in DUMB when adding mappings. DUMB can move a service to the next
available port when its preferred port is already in use.

This mode:

- Keeps the container on an isolated Docker network
- Exposes only the ports listed under `ports:`
- Lets the host-side port differ from the container port, such as
  `"17878:7878"`
- Requires updating and recreating the container when you add a direct service
  port

!!! tip "Embedded service UIs"

    If you use service UIs through the DUMB Frontend and its Traefik proxy, you
    may only need to publish `3005`. Publish individual service ports when
    another device or application must connect to those services directly.

!!! warning "DUMB backend port 8000"

    Do not publish port `8000` for normal use. The DUMB Frontend proxies the API
    under `http://<host>:3005/api`, while the native backend listener binds to
    container loopback by default.

## Option 2: Use Host Networking

Host networking makes the DUMB container share the Docker host's network
namespace. Services that listen on non-loopback addresses become reachable on
the same port without adding a Compose mapping for each one.

Replace the entire `ports:` section with `network_mode: host`:

```yaml
services:
  DUMB:
    network_mode: host
```

Do not keep `ports:` alongside `network_mode: host`. Port publishing is not
used in host mode, and current Docker Compose versions reject that combination.

This mode:

- Makes direct access to many DUMB-managed service ports more convenient
- Avoids maintaining a long `ports:` list
- Removes Docker's network isolation for the DUMB container
- Prevents Docker from translating a conflicting host port to a different
  container port
- Can expose more listeners than intended through the Docker host

Use host networking only when you want direct access to most service ports and
are prepared to manage port conflicts and firewall rules. Keep DUMB
authentication enabled. The native DUMB backend still binds to loopback; use
the supported `:3005/api` gateway instead of relying on direct port `8000`
access.

!!! info "Platform support"

    These instructions target Docker Engine on Linux, including Docker Engine
    installed inside WSL. See Docker's
    [host network driver](https://docs.docker.com/engine/network/drivers/host/)
    documentation for platform-specific support and limitations.

## Apply and Verify the Change

After changing `ports:` or `network_mode`, recreate DUMB:

```bash
sudo docker compose down
sudo docker compose up -d
```

Then verify the effective network configuration:

```bash
sudo docker compose config
sudo docker ps
```

If a service is not reachable:

- Confirm its current port in DUMB rather than assuming its default port
- Check the Docker host's firewall
- On WSL, check both Windows Firewall and the Hyper-V firewall
- Confirm that `ports:` contains the current service port, or that host
  networking is active

For Compose syntax details, see Docker's
[`network_mode`](https://docs.docker.com/reference/compose-file/services/#network_mode)
and [`ports`](https://docs.docker.com/reference/compose-file/services/#ports)
documentation.
