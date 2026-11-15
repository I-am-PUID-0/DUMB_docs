---
title: Reference
description: Look up DUMB service ports, environment overrides, configuration schema, instance settings, and workflow routing without reading setup guides.
icon: lucide/book-open
---

# Geek reference { #reference }

Use the [frontend guides](../frontend/index.md) for everyday tasks. This reference
is for understanding the internals or using a different method: configuration
files, environment variables, APIs, networking, and process dependencies.

The frontend workflow remains the main path. These references explain the
settings and behavior behind it; they do not add extra required setup steps.

Use these pages to look up exact names and defaults. For a procedure, start with [Deployment](../deployment/index.md), [Features](../features/index.md), or the relevant [service guide](../services/index.md).

| Look up | Reference |
|---|---|
| Listener defaults and direct access | [Service ports](ports.md) |
| Environment variables, Docker secrets, and precedence | [Environment variables](environment-variables.md) |
| DUMB's configuration format and validation | [Configuration schema](config-schema.md) |
| Multiple copies of a supported service | [Multi-instance configuration](instances.md) |
| Which workflow an Arr instance belongs to | [Core service routing](core-service.md) |
| HTTP and WebSocket endpoints | [API reference](../api/index.md) |

Defaults describe a fresh configuration. The values saved in `/config/dumb_config.json` and shown in the dashboard take precedence when diagnosing a running installation.
