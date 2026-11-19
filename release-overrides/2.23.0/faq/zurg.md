---
title: Zurg FAQ
description: Investigate Zurg and rclone HTTP 423 errors by checking provider readiness, request activity, and the source logs before changing limits.
icon: lucide/zap
---

# Zurg FAQ

**Visual guide:** [Distinguish provider throttling from mount problems](rclone.md#separate-provider-throttling-from-mount-visibility).

## `ERROR - rclone w/ RealDebrid subprocess: : IO error: File is temporarily unavailable: 423 Locked`

The remote WebDAV source returned `423 Locked`. Read the accompanying Zurg/provider logs to distinguish unavailable or preparing content from provider throttling. The status code alone does not prove a rate limit.

If background library work is generating excessive requests:

1. Review [Plex analysis and scan settings](plex.md#recommended-library-settings).
2. Check how many clients and scans use the same provider account.
3. Consider a conservative rclone transaction limit using `RCLONE_TPSLIMIT` and observe the result.

See the [rclone FAQ](rclone.md#i-think-i-might-be-rate-limited-by-the-debrid-service-seeing-423-errors) for the correct variable and its limits.

## Related pages

- [Zurg configuration](../services/dependent/zurg.md)
- [rclone configuration](../services/dependent/rclone.md)
