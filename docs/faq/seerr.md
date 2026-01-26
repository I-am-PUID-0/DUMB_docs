---
title: Seerr FAQ
icon: lucide/help-circle
---

# Seerr FAQ

Common questions and fixes for Seerr in DUMB.

---

## Why is the Seerr UI not loading?

- Confirm the service is enabled in `dumb_config.json`.
- Ensure port `5055` is available and not blocked.
- Check logs at the configured log path for startup errors.

!!! tip "Traefik access"

    If Traefik is enabled, you can access Seerr at `http://<host>/seerr/`.

---

## Seerr cannot connect to my media server

Seerr needs API access to Plex/Jellyfin/Emby.

- Verify the media server is running and reachable.
- Confirm the API key/token is correct in Seerr settings.
- If using Traefik, make sure the base URL matches the proxy path.

---

## Why are requests failing to import into Arr?

- Ensure Sonarr/Radarr are enabled and accessible.
- Verify API keys in Seerr match the Arr instances.
- Confirm the Arr instances are on the correct ports.
