---
title: Deployment
icon: lucide/server
---

# Deployment Overview

DUMB can be deployed across a variety of platforms and environments. Whether you're using **Docker**, **Portainer**, **Unraid**, **WSL2**, or other systems like **TrueNAS**, **Synology**, or **QNAP**, this section will guide you through the available options to get DUMB up and running.

All deployment methods provide access to the same integrated services and configurations, with slight differences in how the container is started and managed.

---

## Available Deployment Guides

### Docker Compose
Quickest way to get started using Docker CLI and `docker-compose.yml`.

- [Deploy with Docker](docker.md)

### Dockge
Deploy using the lightweight Dockge container manager.

- [Deploy with Dockge](dockge.md)

### Portainer
Deploy using the Portainer web interface.

- [Deploy with Portainer](portainer.md)

### Unraid
Deploy using the Unraid Community Applications plugin and container template.

- [Deploy with Unraid](unraid.md)

### WSL2 (Windows Subsystem for Linux)
Deploy DUMB in a WSL2 environment on Windows 11.

- [Deploy with WSL](wsl.md)

### Proxmox
Deploy inside a lightweight container or VM using Proxmox VE.

- [Deploy with Proxmox](proxmox.md)

### QNAP
Deploy using Container Station or Docker on supported QNAP NAS devices.

- [Deploy with QNAP](qnap.md)

### Synology
Deploy using Synology Docker and DSM's GUI or CLI.

- [Deploy with Synology](synology.md)

### TrueNAS
Deploy on TrueNAS SCALE using Docker or native Apps.

- [Deploy with TrueNAS](truenas.md)

---


## Additional Notes

- All methods rely on a valid and accessible `dumb_config.json` file for configuring services.
- It is strongly recommended to bind-mount a local `config` directory to persist user data.

Example:
```yaml
dumb:
  image: iampuid0/dumb:latest
  volumes:
    - ./config:/config
```

For more about configuring services, see the [Configuration](../features/configuration.md) page.

---

## Related Pages
- [Service Overview](../services/index.md)
- [Features](../features/index.md)
