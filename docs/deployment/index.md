---
title: Deployment
icon: lucide/server
---

# Deployment Overview

DUMB can be deployed across a variety of platforms and environments. Whether you're using **Docker**, **Portainer**, **Unraid**, **WSL2**, or other systems like **TrueNAS**, **Synology**, or **QNAP**, this section will guide you through the available options to get DUMB up and running.

All deployment methods provide access to the same integrated services and configurations, with slight differences in how the container is started and managed.

!!! tip "Platform-Specific Instructions"
    **Select your platform from the left navigation** to view detailed, platform-specific deployment instructions. Each platform guide includes step-by-step setup instructions tailored to your environment.

---

## System Requirements

- **Docker or Docker-compatible environment**
- Linux system (WSL on Windows when using `rshared`)
- Minimum 2 vCPU, 2GB RAM, SSD recommended


!!! warning "Docker Desktop" 
    Docker Desktop **CANNOT** be used to run DUMB when using `rshared` mount propagation. 

    Docker Desktop does not support the [mount propagation](https://docs.docker.com/storage/bind-mounts/#configure-bind-propagation) required for rclone mounts.

    ![image](../assets/images/docker_desktop.png)

    See the [deployment options](https://dumbarr.com/deployment/wsl) to run DUMB on Windows through WSL2.
---

## Required Credentials

| Service     | Required Info                                 |
|------------------|------------------------------------------|
| Debrid      | API Key (Real-Debrid)                         |
| GitHub      | Token *(if using the sponsored Zurg repo)*    |

 See [Configuration → Integration Tokens](../features/configuration.md#-integration-tokens--credentials)

---

## Required Directories

You'll need to bind mount the following volumes when running the container:

| Container Mount Path       | Description                                       |
|----------------------------|---------------------------------------------------|
|`/config`                   | Location for configuration files                  |
|`/log`                      | Location for logs                                 |
|`/zurg/RD`                  | Location for Zurg RealDebrid active configuration | 
|`/riven/backend/data`       | Location for Riven Backend data                   |
|`/postgres_data`            | Location for PostgreSQL databases                 |
|`/pgadmin/data`             | Location for pgAdmin 4 data                       |
|`/zilean/app/data`          | Location for Zilean data                          |
|`/plex_debrid/config`       | Location for plex_debrid data                     |
|`/cli_debrid/data`          | Location for cli_debrid data                      |
|`/phalanx_db/data`          | Location for phalanx_db data                      |
|`/decypharr`                | Location for decypharr data                       |
|`/plex`                     | Location for Plex Media Server data               |
|`/mnt/debrid`               | Location for raw debrid files/links and symlinks  |

!!! note "/config"
    If a Zurg config.yml and/or Zurg app is placed here, it will be used to override the default configuration and/or app used at startup.

!!! important "/mnt/debrid:rshared"    
    The `:rshared` must be included in order to support [mount propagation](https://docs.docker.com/storage/bind-mounts/#configure-bind-propagation) for rclone to the host when exposing the raw debrid files/links to an external container; e.g., the arrs or a media server.

    `:rshared` is not required when using the default configuration leveraging the internal media server or when not utilizing [Decypharr](../services/core/decypharr.md).
---

!!! note "Configuration Requirements"
    All deployment methods rely on a valid and accessible `dumb_config.json` file for configuring services.
    
    It is strongly recommended to bind-mount a local `config` directory to persist user data.

!!! example "Example Volume Mount"
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
