---
title: Huntarr FAQ
icon: lucide/help-circle
---

# Huntarr FAQ

Common questions and fixes for Huntarr in DUMB.

---

## Why is the Huntarr UI not loading?

Check the following:

- Confirm the service is enabled in `dumb_config.json`.
- Verify the port in the service configuration (default `9705`).
- Review the Huntarr logs for startup errors.

!!! tip "Traefik access"

    If Traefik is enabled, you can access Huntarr at `http://<host>/huntarr/`.

---

## Why doesn't Huntarr see my Arr instances?

Huntarr relies on Arr API access.

- Ensure Sonarr/Radarr/Lidarr are running and reachable.
- Verify API keys are set in the Arr configs.
- Check that `core_service` is set appropriately in your Arr instance configs.

---

## Which Huntarr instance should I use?

DUMB supports multiple Huntarr instances for different workflows.

!!! info "Instance ports"

    - Default instance: `9705`
    - Additional instances: choose unique ports
