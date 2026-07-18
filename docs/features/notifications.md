---
title: Notifications
icon: lucide/bell-ring
---

# Notifications

DUMB includes an optional backend notification utility for sending health and operational events even when no browser is open. It is separate from the browser-local alert banners on the Metrics page.

Notifications are disabled by default.

## What it provides

- Multiple named notification destinations
- [Apprise](https://appriseit.com/) URLs for Discord, ntfy, Gotify, Telegram, email, Slack, Home Assistant, and other supported services
- Generic JSON webhooks
- Per-destination event, severity, and service routing
- Persistent queued delivery and history under `/config/notifications`
- Exponential retry with a configurable attempt limit
- Per-event cooldown suppression
- Recovery notifications when monitored pressure clears
- Manual messages and destination tests from **Settings → Notifications**
- Redacted API responses and logs for destination URLs and request headers

## Configure a destination

1. Open **Settings → Notifications**.
2. Select **Add destination**.
3. Give the destination a recognizable name.
4. Choose **Apprise URL** or **Generic JSON webhook**.
5. Enter the destination URL.
6. Select the minimum severity, cooldown, event types, and optional service filters.
7. Select **Save & test**.
8. Enable outbound notifications after the test succeeds.

An empty event list matches every event. The service-filter dropdown is populated only from services currently enabled in DUMB and supports selecting more than one service. Disabled template services are not offered, and names that are not currently enabled are removed from the editable filter instead of being retained as hidden routing values. If enabled-service discovery is temporarily unavailable, destination saving and testing are paused until Settings is refreshed. Leaving every service unchecked matches all events, including events for any enabled service; selected entries use the exact process names shown by DUMB.

!!! important "Minimum severity is evaluated first"

    The default minimum is **Warning**. It excludes `Info` and `Success` events even when those events are selected—or when the empty event list matches everything. Set the minimum to **Success** to include successful Auto-restarts, successful updates, and successful symlink jobs. Set it to **Info** to also include update-available notices.

**Save & test** saves the destination and then bypasses the global switch, destination switch, severity/event/service filters, and cooldown for that one test. This is why a disabled destination can still be tested safely before normal delivery is enabled.

!!! warning "Destination URLs are credentials"

    Apprise URLs and webhook URLs commonly contain tokens, passwords, or unguessable paths. Do not post them in logs, screenshots, issues, or chat. DUMB stores them in its protected configuration and returns only `configured` state to the notification settings UI.

## Apprise destinations

DUMB uses the embedded Apprise Python library. It normally connects directly from the DUMB container to the provider named in the notification URL. Messages are not relayed through appriseit.com, and you do not need an Apprise account, hosted relay, separate Apprise API container, or sidecar.

!!! note "The optional Apprise API is different"

    An `apprise://` or `apprises://` notification URL explicitly targets an Apprise API server. DUMB uses that server only when you intentionally configure one of those URLs. Provider URLs such as `discord://`, `ntfy://`, `tgram://`, and `mailto://` are handled locally by the embedded library and sent directly to that provider.

Examples of URL families include:

- `discord://...`
- `ntfy://...`
- `tgram://...`
- `mailto://...`
- `gotify://...`
- `slack://...`

Use the official [Apprise URL Builder](https://appriseit.com/url-builder/) or [notification service documentation](https://appriseit.com/services/) to construct the URL for a provider. DUMB never displays a saved URL after it has been stored. Leave the field blank to preserve the existing secret or enter a new URL to replace it.

Apprise's provider cache is kept in `/config/notifications/apprise`.

## Generic webhook payload

Generic webhooks receive an HTTP `POST` with JSON shaped like:

```json
{
  "source": "DUMB",
  "event_id": "generated-event-id",
  "event_type": "service.auto_restart.failed",
  "severity": "critical",
  "title": "Auto-restart failed for Sonarr",
  "body": "Redacted failure summary",
  "service_name": "Sonarr",
  "timestamp": 1784300000.0
}
```

Optional request headers can be entered as a JSON object. Leave the headers field blank after saving to preserve existing secret headers.

TLS certificate verification is enabled by default. Disable it only for a deliberately trusted private endpoint using a self-signed certificate.

## Event sources

### Service and startup events

| Event | Severity | Trigger and prerequisites |
|-------|----------|---------------------------|
| Degraded DUMB startup | Critical | Startup completes with one or more failed service preinstalls while the API and frontend remain available |
| Service preinstall failure | Critical | One service fails its preinstall phase |
| Service start failure | Critical | Setup fails, the process exits during startup, or DUMB otherwise cannot start it |
| Service unhealthy | Critical | Requires [Auto-restart](auto-restart.md) health monitoring for the exact service; emitted after the configured consecutive unhealthy-check threshold |
| Unexpected service stop | Critical | A managed process exits unexpectedly; emitted before any eligible restart is scheduled |
| Automatic restart attempt | Warning | Requires Auto-restart for the service; emitted immediately before the restart attempt |
| Automatic restart succeeded | Success | Requires Auto-restart for the service; this is a separate event and is not controlled by **Recovery messages** |
| Automatic restart failed | Critical | Requires Auto-restart for the service; DUMB could not restart the process |
| Automatic restart suppressed | Critical | Requires Auto-restart for the service; its restart limit was reached |

!!! note "What counts as down"

    Notifications do not poll the dashboard's displayed `Stopped` state as a generic down alarm. A deliberately disabled service or a service intentionally stopped by an operator is not a generic service-down event. Unexpected process exits notify immediately. Health-based unhealthy and restart events require Auto-restart to be enabled globally and for the exact service.

### Update events

- Update available when a service first enters the available state or the available version changes; unchanged scheduled checks do not resend it
- Update succeeded
- Update failed

### Symlink operations

- Repair, backup, or restore job succeeded
- Repair, backup, or restore job failed

### Persistent conditions

- CPU pressure
- Memory pressure
- Disk-capacity pressure
- Inode pressure
- Database pressure
- Database-health probe failure
- Recovery after the condition clears

Persistent conditions must remain active for `duration_sec` before DUMB sends them. This prevents a short spike from producing a notification.

Database events require Database Health collection to be enabled for the relevant service. Notification monitoring does not silently enable Database Health.

## Severity and routing

Severities are ordered as:

1. `info`
2. `success`
3. `warning`
4. `critical`

A destination receives events at or above its selected minimum. Recovery messages are controlled separately by **Recovery messages**, so a success recovery can still follow a warning or critical condition.

The routing order is:

1. Destination enabled state
2. Minimum severity
3. Event selection
4. Exact service-name filter
5. Recovery preference and cooldown

`Automatic restart succeeded`, `Update succeeded`, and `Symlink job succeeded` are normal `Success` events and are filtered by a `Warning` minimum. A `recovery` event is different: it represents a resource or Database Health threshold returning to normal, bypasses the minimum-severity check, and requires **Recovery messages** to be enabled.

Manual destination tests bypass normal routing plus the global and destination enable switches. This allows configuration testing before outbound notifications are enabled. A normal manual message bypasses the global switch and routing filters but still skips disabled destinations. If a destination is disabled after an automatic event has already been queued, DUMB keeps that record queued without consuming a retry attempt and resumes delivery only after the destination is enabled again.

## Cooldowns, retries, and history

Cooldowns are evaluated independently for each destination, event type, and service. Repeated matching events during the cooldown are recorded as `suppressed` but are not delivered.

Failed delivery uses exponential backoff starting at `retry_base_sec`. A delivery becomes `failed` after `max_attempts`.

Delivery history statuses are:

| Status | Meaning |
|--------|---------|
| `queued` | Waiting for the delivery worker |
| `retrying` | A prior attempt failed and another is scheduled |
| `sent` | Provider confirmed delivery |
| `failed` | Attempt limit was reached |
| `suppressed` | A matching cooldown prevented delivery |

History is stored in `/config/notifications/notifications.sqlite`. Completed records older than `history_retention_days` are removed automatically. Clearing history from the UI does not delete queued or retrying deliveries.

## What it cannot guarantee

- A provider accepting a message does not guarantee a phone, email client, or chat application displayed it.
- DUMB cannot recover provider-side messages deleted or rejected after a successful API response.
- Notifications cannot be sent while the container, host, network, DNS, or destination provider is unavailable. Queued/retrying records survive a normal container recreation when `/config` is persistent.
- Resource thresholds are diagnostic signals, not proof that a service is failing.
- Database pressure does not predict the performance improvement from changing database providers.

## Compatibility

The frontend checks the backend `notifications` capability. When connected to an older DUMB backend, the Notifications section is hidden and other Settings functions continue to work.

## Troubleshooting

### A test fails

1. Open **Delivery history** and inspect the redacted error.
2. Confirm the URL syntax using the provider's Apprise documentation.
3. Confirm the DUMB container can resolve and reach the destination.
4. Verify certificates and system time for HTTPS endpoints.
5. For generic webhooks, confirm the endpoint accepts `POST` JSON.

### Health events do not arrive

1. Confirm outbound notifications are enabled globally.
2. Confirm the destination is enabled.
3. Check minimum severity, event selections, and exact service filters.
4. Check whether the event was recorded as `suppressed` by a cooldown.
5. For database events, confirm Database Health is enabled for that service.
6. For `Service unhealthy` and Auto-restart events, confirm Auto-restart is enabled globally and for the exact service.
7. To receive successful Auto-restart/update/symlink events, set minimum severity to **Success** or **Info**.

## Related pages

- [Settings](../frontend/settings.md)
- [Metrics](metrics.md)
- [Auto-restart](auto-restart.md)
- [Auto-update](auto-update.md)
- [Symlink Operations](symlinks.md)
- [Notifications API](../api/notifications.md)
