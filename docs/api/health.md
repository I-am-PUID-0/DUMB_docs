---
title: Health Check API
---

# 🌊 Health Check API

The **Health Check API** provides a simple mechanism to verify that the DMB container and core services are operational.

---

## 🔍 Endpoint

### `GET /health`
Returns a JSON response indicating whether the container is healthy.

#### Response
```json
{
  "status": "healthy"
}
```

If the check fails, the status will be `"unhealthy"` and include diagnostic output.

---

## 📊 Use Case
- Used by orchestrators or monitoring tools to confirm container availability.
- Can be used to gate traffic in load balancers or uptime monitoring dashboards.

---

## ✨ Implementation
This route executes a background health check script in the container:
```bash
/healthcheck.py
```
It runs within the same virtual environment as DMB and ensures all critical files, paths, and subprocesses are functional.

---

## 🔗 Related
- [API Overview](index.md)
- [Process Management](process.md)

