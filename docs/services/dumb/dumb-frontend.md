---
title: DUMB Frontend
icon: lucide/layout-dashboard
---

The **DUMB Frontend** is the web UI for managing and monitoring the DUMB ecosystem.
It provides service controls, real-time logs, embedded UIs, onboarding, settings,
and metrics in a single interface.

!!! tip "Frontend documentation"

    For detailed guides on using the frontend, see the [Frontend Documentation](../../frontend/index.md) section:

    - [Dashboard](../../frontend/dashboard.md) - Service overview and control
    - [Onboarding](../../frontend/onboarding.md) - Setup wizard guide
    - [Settings](../../frontend/settings.md) - Configuration and preferences
    - [Service pages](../../frontend/service-pages.md) - Per-service controls, logs, and config
    - [Metrics](../../frontend/metrics.md) - System monitoring

---

## Configuration Settings in `dumb_config.json`

```json
"frontend": {
    "enabled": true,
    "process_name": "DUMB Frontend",
    "repo_owner": "nicocapalbo",
    "repo_name": "dmbdb",
    "release_version_enabled": false,
    "release_version": "v1.2.0",
    "branch_enabled": false,
    "branch": "main",
    "suppress_logging": false,
    "log_level": "INFO",            
    "log_file": "/log/dumb_frontend.log",
    "origins": [
        "http://0.0.0.0:3005"
    ],
    "host": "0.0.0.0",
    "port": 3005,            
    "auto_update": false,
    "auto_update_interval": 24,
    "clear_on_update": true,
    "exclude_dirs": [],
    "platforms": ["pnpm"],
    "command": ["node",".output/server/index.mjs"],
    "config_dir": "/dumb/frontend",
    "env": {}            
}
```

### Configuration Key Descriptions

- **`enabled`**: Determines whether the DUMB Frontend service is active.
- **`process_name`**: Name used in logs and process tracking.
- **`repo_owner`** / **`repo_name`**: Specifies the GitHub repository to clone for the frontend.
- **`release_version_enabled`** / **`release_version`**: Indicates if a specific release version should be used.
- **`branch_enabled`** / **`branch`**: Specifies the branch to use if enabled.
- **`suppress_logging`**: If `true`, disables log output for this service.
- **`log_level`**: Logging verbosity level (e.g., `DEBUG`, `INFO`).
- **`host`**: IP address the frontend should bind to.
- **`port`**: Port the frontend is served on.
- **`auto_update`**: Enables automatic self-updates.
- **`auto_update_interval`**: How often (in hours) to check for updates.
- **`clear_on_update`**: Clears build artifacts or cache during updates.
- **`exclude_dirs`**: Prevents specific directories from being affected by updates when using `clear_on_update`
- **`platforms`**: Specifies the runtime environment required (`pnpm`).
- **`command`**: Command to start the frontend service.
- **`config_dir`**: Directory where configuration files are stored.
- **`env`**: Environment variables for the frontend.

---

## Branch / Version Targeting
You can control which version or branch of the frontend is deployed by setting:

- `branch_enabled: true` and specifying a `branch`
- or `release_version_enabled: true` and specifying a `release_version`

---

## Accessing the DUMB Frontend
- Navigate to: `http://<host>:<port>`
    - default port `3005`

## Frontend usage guides

For UI walkthroughs, use the frontend section:

- [Dashboard](../../frontend/dashboard.md) - Service cards, toolbar, and logs
- [Settings](../../frontend/settings.md) - Preferences and config editors
- [Service pages](../../frontend/service-pages.md) - Per-service controls and logs
- [Onboarding](../../frontend/onboarding.md) - Setup wizard
- [Metrics](../../frontend/metrics.md) - System monitoring

---

## Tips

- **Automatic Updates**: Enable `auto_update` to keep the frontend up-to-date with the latest features.
- **Log Monitoring**: Utilize the service logs functionality for effective monitoring and troubleshooting.

---

## Resources

- [DUMB Frontend GitHub Repository](https://github.com/nicocapalbo/dmbdb)
- [DUMB Frontend CHANGELOG](https://github.com/nicocapalbo/dmbdb/blob/main/CHANGELOG.md)
