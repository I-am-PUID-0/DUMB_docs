---
title: NeutArr FAQ
icon: lucide/help-circle
---

# NeutArr FAQ

Common questions and fixes for NeutArr in DUMB.

---

## Why is the NeutArr UI not loading?

Check the following:

- Confirm the service is enabled in `dumb_config.json`.
- Verify the port in the service configuration (default `9705`).
- Review the NeutArr logs for startup errors.

!!! tip "Traefik access"

    If Traefik is enabled, you can access NeutArr at `http://<host>/neutarr/`.

---

## Why doesn't NeutArr see my Arr instances?

NeutArr relies on Arr API access.

- Ensure Sonarr/Radarr/Lidarr are running and reachable.
- Verify API keys are set in the Arr configs.
- Check that `core_service` is set appropriately in your Arr instance configs.

---

## Which NeutArr instance should I use?

DUMB supports multiple NeutArr instances for different workflows.

!!! info "Instance ports"

    - Default instance: `9705`
    - Additional instances: choose unique ports
