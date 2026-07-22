---
title: Health Check API
icon: lucide/heart-pulse
---

# Health Check API

The **Health Check API** provides a simple mechanism to verify that the DUMB container and core services are operational.

---

## Endpoint

### `GET /health`
Returns a JSON response indicating whether the container is healthy.

#### Response
```json
{
  "status": "healthy"
}
```

If a tracked process or one of its configured listener ports fails the check, the
response remains HTTP 200 with `"status": "unhealthy"` and a sanitized `details`
field. A health-check timeout returns HTTP 504; an execution failure returns
HTTP 500.

---

!!! tip "Use Cases"
    - Used by orchestrators or monitoring tools to confirm container availability.
    - Use in load balancers or uptime monitoring dashboards.

---

## Implementation
This route executes the container health-check script:
```bash
/healthcheck.py
```
It reads DUMB's tracked process file, confirms each PID is still running, and
tests configured service ports when present. It is a stack/process readiness
signal, not a deep application-data or provider health test.

---

## Related
- [API Overview](index.md)
- [Process Management](process.md)
