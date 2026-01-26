---
title: Tautulli FAQ
icon: lucide/help-circle
---

# Tautulli FAQ

Common questions and fixes for Tautulli in DUMB.

---

## Why is the Tautulli UI not loading?

- Confirm Tautulli is enabled in `dumb_config.json`.
- Ensure port `8181` is available.
- Review the Tautulli log for startup errors.

!!! tip "Traefik access"

    If Traefik is enabled, you can access Tautulli at `http://<host>/tautulli/`.

---

## Tautulli cannot connect to Plex

- Confirm Plex Media Server is running.
- Check the Plex URL and token in Tautulli settings.
- Verify that the Plex port (`32400`) is reachable from the container.

---

## Tautulli data is missing or incomplete

- Make sure your Plex libraries have been scanned recently.
- Check that Tautulli has permission to access Plex history and metadata.
