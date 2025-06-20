Zilean is a service that enables users to search for content sourced by [Debrid Media Manager](https://github.com/debridmediamanager/) and shared by others. It can be configured as a Torznab indexer in various content applications, allowing seamless integration and content discovery. Additionally, Zilean can scrape data from a running Zurg instance and other Zilean instances. 

---

## ⚙️ Configuration Settings in `dmb_config.json`

Below is a sample configuration for Zilean within the `dmb_config.json` file:

```json
"zilean": {
  "enabled": true,
  "process_name": "Zilean",
  "repo_owner": "iPromKnight",
  "repo_name": "zilean",
  "release_version_enabled": false,
  "release_version": "v3.3.0",
  "branch_enabled": false,
  "branch": "main",
  "suppress_logging": false,
  "log_level": "INFO",
  "host": "127.0.0.1",
  "port": 8182,
  "auto_update": false,
  "auto_update_interval": 24,
  "clear_on_update": true,
  "exclude_dirs": ["/zilean/app/data"],
  "env_copy": {
    "source": "/zilean/app/data/.env",
    "destination": "/zilean/app/src/.env"
  },
  "platforms": ["python", "dotnet"],
  "command": ["/zilean/app/zilean-api"],
  "config_dir": "/zilean",
  "config_file": "/zilean/app/data/settings.json",
  "env": {
    "DOTNET_RUNNING_IN_CONTAINER": "true",
    "DOTNET_gcServer": "1",
    "DOTNET_GCDynamicAdaptationMode": "1",
    "DOTNET_SYSTEM_GLOBALIZATION_INVARIANT": "false",
    "PYTHONUNBUFFERED": "1",
    "ASPNETCORE_URLS": "http://+:{port}",
    "PYTHONPATH": "/zilean/venv/lib/python3.11/site-packages",
    "PATH": "/zilean/venv/bin:${PATH}",
    "ZILEAN_PYTHON_PYLIB": "/usr/local/lib/libpython3.11.so.1.0",
    "Zilean__Database__ConnectionString": "Host={postgres_host};Port={postgres_port};Database=zilean;Username={postgres_user};Password={postgres_password};Timeout=300;CommandTimeout=3600;"
  }
},
```

### 🔍 Configuration Key Descriptions

- **`enabled`**: Whether to start the Zilean service.
- **`process_name`**: Used in logs and process tracking.
- **`repo_owner`** / **`repo_name`**: GitHub repo to pull from.
- **`release_version_enabled`** / **`release_version`**: Use a tagged release if enabled.
- **`branch_enabled`** / **`branch`**: Use a specific branch if enabled.
- **`suppress_logging`**: If `true`, disables log output for this service.
- **`log_level`**: Logging verbosity (e.g., `DEBUG`, `INFO`).
- **`host`**: IP address for the Zilean service to bind to.
- **`port`**: Port the Zilean API is exposed on.
- **`auto_update`**: Enables automatic self-updates.
- **`auto_update_interval`**: How often (in hours) to check for updates.
- **`clear_on_update`**: Clears build artifacts or cache during updates.
- **`exclude_dirs`**: Prevents specific directories from being affected by updates when using `clear_on_update`
- **`env_copy`**: Paths to copy a `.env` file from source to destination for runtime support.
- **`platforms`**: Required environments—Zilean uses both .NET and Python.
- **`command`**: The binary or command used to launch Zilean.
- **`config_dir`** / **`config_file`**: Where configuration files are stored and loaded.
- **`env`**: Dictionary of environment variables passed at runtime, including:
  - **`DOTNET_RUNNING_IN_CONTAINER`**: Informs .NET that it is containerized.
  - **`DOTNET_gcServer`**: Enables server-mode garbage collection.
  - **`DOTNET_GCDynamicAdaptationMode`**: Adjusts GC behavior adaptively.
  - **`DOTNET_SYSTEM_GLOBALIZATION_INVARIANT`**: Controls globalization features.
  - **`PYTHONUNBUFFERED`**: Ensures Python output is unbuffered.
  - **`ASPNETCORE_URLS`**: Specifies ASP.NET Core server bind address.
  - **`PYTHONPATH`**: Adds Python libraries to runtime path.
  - **`PATH`**: Prepends Python virtual environment binaries.
  - **`ZILEAN_PYTHON_PYLIB`**: Full path to the Python shared object.
  - **`Zilean__Database__ConnectionString`**: Connection string for PostgreSQL.

---

## ⚙️ Branch / Version Targeting
You can control which version or branch of Zilean is deployed by setting:

- `branch_enabled: true` and specifying a `branch`
- or `release_version_enabled: true` and specifying a `release_version`

---

## 🧠 Tips
- The first-time run of Zilean can take a long time; see the [Zilean FAQ](../faq/zilean.md#why-is-zilean-spamming-my-logs) for more info.
- Logs from Zilean can be accessed via DMB’s Frontend or directly from `/log/zilean.log`.
- If Zilean fails to bind, check for existing services on port `8182`.
- Use the `clear_on_update` and `exclude_dirs` settings to preserve persistent data.

---

## 📚 Resources
- [Zilean GitHub Repository](https://github.com/iPromKnight/zilean)
