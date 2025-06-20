---
title: DMB API
---

# DMB API
The **DMB API** is the central communication layer between the DMB Frontend and the backend service. It handles requests for logs, service management (start/stop), configuration updates, and health checks.

---

## ⚙️ Configuration Settings in `dmb_config.json`
Located in `dmb.api_service`:
```json
"enabled": true,
"process_name": "DMB API",
"log_level": "INFO",
"host": "127.0.0.1",
"port": 8000
```

### 🔍 Configuration Key Descriptions
- **`enabled`** – Whether the API service should run.
- **`process_name`** – Used in process management and logs.
- **`log_level`** – Logging verbosity for the API.
- **`host`**: IP address for API to listen on.

    !!! note "`0.0.0.0` allows access to the API from all addresses"

- **`port`**: Port exposed for the API.

---