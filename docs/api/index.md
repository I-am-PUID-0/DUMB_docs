---
title: DUMB API Overview
---

# DUMB API

DUMB includes a built-in REST API and WebSocket server to allow programmatic control of services, logging, and system state.

The API is enabled and configured using the `dumb_config.json` under the `dumb.api_service` section. For example:

```json
"api_service": {
  "enabled": true,
  "process_name": "DUMB API",
  "log_level": "INFO",
  "host": "127.0.0.1",
  "port": 8000
}
```

--- 

## Features
- Health checks
- Process management (start, stop, restart services)
- Real-time log streaming via WebSocket
- Configuration viewing and updates (in-memory and persistent)
- Environment state inspection

---

## Common Endpoints

| Method | Path                      | Description                                |
|--------|---------------------------|--------------------------------------------|
| GET    | `/health`                 | Container health check                     |
| GET    | `/process/processes`      | List all services in `dumb_config.json`    |
| GET    | `/process`                | Get a specific service by `process_name`   |
| POST   | `/process/start-service`  | Start a specific service                   |
| POST   | `/process/stop-service`   | Stop a specific service                    |
| POST   | `/process/restart-service`| Restart a specific service                 |
| GET    | `/process/service-status` | Get the current status of a service        |
| POST   | `/process/start-core-service` | Start core services + dependencies     |
| GET    | `/logs`                   | Read service log chunks                    |
| WS     | `/ws/logs`                | Real-time log streaming                    |

---

## Directory Structure
The DUMB API is split into the following modules:

| File | Purpose |
|------|---------|
| `api_service.py` | Initializes and launches the FastAPI app |
| `api_state.py` | Tracks and updates service runtime state |
| `connection_manager.py` | Manages WebSocket client connections |
| `config.py` | Endpoints for working with `dumb_config.json` and service configs |
| `health.py` | Health check endpoint for validating API status |
| `logs.py` | REST endpoint for reading historical logs |
| `websocket_logs.py` | WebSocket server for streaming real-time logs to frontend |
| `process.py` | Service control for backend processes (start, stop, restart) |

---

## API Documentation

DUMB provides built-in API documentation through two convenient endpoints:

- **FastAPI Swagger UI**  
  Accessible at:  
  `http://<host>:<port>/docs`  
  This interface allows for interactive testing and exploring of all available REST endpoints.

- **Scalar (ReDoc-style) Docs**  
  Accessible at:  
  `http://<host>:<port>/scalar`  
  A clean, read-only view of the full OpenAPI schema for the DUMB API.

These are helpful for development, debugging, and integrating external systems with DUMB.

--- 

## Next Steps
Click on any of the modules in the sidebar to explore endpoint structure, usage examples, and development guidelines for extending the DUMB API:

- [Health Check](health.md)
- [Logs](logs.md)
- [Process Management](process.md)
- [Configuration](config.md)
- [WebSocket Logs](websocket_logs.md)
