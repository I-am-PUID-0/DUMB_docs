---
title: Health Check API
description: Check DUMB process and listener readiness through GET /health, and interpret unhealthy payloads, timeouts, and execution failures correctly.
icon: lucide/heart-pulse
---

# Health Check API

`GET /health` runs DUMB's health-check script and reports tracked process/listener readiness.

```bash
curl http://localhost:3005/api/health
```

**Visual guide:** [See the backend request and control flow](../architecture/backend.md#request-flow).

## Responses

| HTTP status | Body | Meaning |
|---|---|---|
| `200` | `{"status":"healthy"}` | The health-check script passed |
| `200` | `{"status":"unhealthy","details":"..."}` | A tracked PID or configured listener failed its check |
| `504` | Error detail | The script exceeded its eight-second timeout |
| `500` | Error detail | DUMB could not execute the check |

**Read the JSON `status` value. HTTP 200 alone does not mean the stack is healthy.** An HTTP-only uptime check can miss an unhealthy response.

## Scope of the check

The script reads the tracked process manifest, checks PIDs, and tests configured listener ports where present. It does not verify provider credentials, application data, imports, or playback.

The Docker runtime uses `/healthcheck.py`; native deployments resolve the script through DUMB's runtime paths. For per-service state and startup progress, use the [process endpoints](process.md).
