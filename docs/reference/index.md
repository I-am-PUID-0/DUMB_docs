---
title: Reference
icon: lucide/book-open
---

# Reference

Technical reference documentation for DUMB configuration, ports, and environment variables.

---

## Available references

<div class="grid cards" markdown>

-   :material-network:{ .lg .middle } **Service ports**

    ---

    Complete list of all ports used by DUMB services, including web UIs, APIs, and databases.

    [:material-arrow-right: View ports reference](ports.md)

-   :material-cog:{ .lg .middle } **Environment variables**

    ---

    All environment variables supported by DUMB for configuration and customization.

    [:material-arrow-right: View environment variables](environment-variables.md)

-   :material-file-code:{ .lg .middle } **Config schema**

    ---

    JSON schema reference for `dumb_config.json`, useful for validation and tooling.

    [:material-arrow-right: View config schema](config-schema.md)

-   :material-layers:{ .lg .middle } **Multi-instance setup**

    ---

    Guidance for configuring multiple instances of Arr services, rclone, and other tools.

    [:material-arrow-right: View instance guide](instances.md)

-   :material-route:{ .lg .middle } **Core service routing**

    ---

    How `core_service` routes automation between Debrid and Usenet workflows.

    [:material-arrow-right: View core service guide](core-service.md)

</div>

---

## Quick links

| Reference | Description |
|-----------|-------------|
| [Service Ports](ports.md) | Port assignments for all services |
| [Environment Variables](environment-variables.md) | Docker and runtime configuration |
| [Config Schema](config-schema.md) | JSON schema for `dumb_config.json` |
| [Multi-instance Setup](instances.md) | Pattern for services that support instances |
| [Core Service Routing](core-service.md) | How `core_service` drives automation |

---

## Related documentation

- [Configuration Guide](../features/configuration.md) - How to configure DUMB
- [Deployment Overview](../deployment/index.md) - Deployment options
- [API Reference](../api/index.md) - REST API documentation
