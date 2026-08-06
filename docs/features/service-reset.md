---
title: Service Reset and Removal
description: Safely reset one DUMB service or instance to defaults, or remove only its scoped DUMB-managed files after a reviewed preview.
icon: lucide/trash-2
---

# Service Reset and Removal

DUMB can reset one previously configured service or instance without requiring a full stack reset. When the backend advertises `service_reset`, open the service page and select **Reset / Remove**.

The workflow always:

1. builds a read-only preview;
2. shows the exact configuration action and every managed path eligible for cleanup;
3. stops the selected process;
4. cancels its automatic-update and scheduled symlink-backup jobs;
5. writes a private backup of the complete DUMB configuration; and
6. applies the selected reset or removal.

You must type the exact process name before DUMB accepts either operation.

## Choose an operation

### Reset DUMB configuration

This option keeps the service's application files and data. DUMB disables the selected service/instance and restores its DUMB configuration fields to the current defaults.

- A single-instance service returns to its disabled default block.
- A built-in/default instance returns to its disabled instance template.
- A custom instance keeps its identity, port, and instance-specific paths, but other DUMB settings and generated secrets return to template values.

Use this when DUMB configuration is wrong but the application's own database, settings, and runtime files should remain available.

### Remove service files

This option performs the configuration reset and also clears the previewed DUMB-owned config/runtime/data paths.

- A custom instance is removed from the service's `instances` object. If it was the last instance, DUMB writes the disabled default template in the same operation instead of temporarily saving an empty `instances` object.
- A required default instance or single-instance service is reset to its disabled template. DUMB keeps that template because config loading would recreate it anyway.
- Only paths attributed exclusively to the selected process are eligible.

Removed application files are not backed up and cannot be restored by DUMB. Review the path list carefully.

## Safety boundary

DUMB intentionally retains:

- `/mnt` content, mountpoints, media roots, and symlink libraries;
- shared install/dependency caches;
- PostgreSQL databases and other external data stores;
- directories shared by another configured DUMB service;
- custom paths outside the selected service's known DUMB-managed root; and
- configuration belonging to other services.

For example, CLI Debrid and CLI Battery share parts of the CLI Debrid tree, while rclone instances share an rclone configuration file. The preview keeps those shared locations and explains why. PostgreSQL is a stack dependency, so resetting its DUMB block never deletes the shared database cluster.

!!! warning "Database-backed services"

    Removing a service's files does not drop its PostgreSQL database. A later reinstall may reconnect to existing database state. Drop or archive a database separately only after confirming that no other service uses it.

!!! warning "Dependent services"

    DUMB warns when another configured service references the target, but it does not rewrite that other service's `core_service`, `core_services`, URL, mount, or application integration settings. Review dependencies before starting the remaining stack.

## Configuration backup and recovery

Before changing `dumb_config.json`, DUMB writes a mode-`0600` full-config backup under:

```text
/config/service-reset-backups/
```

The API response includes the exact backup path. The backup can recover DUMB configuration, including a removed custom instance, but it does not contain deleted service files.

If an operation reports failure, the selected process remains stopped. Check the DUMB log and the backup directory before retrying. Restore configuration only while DUMB is stopped, then restart the container so configuration is reloaded consistently.

## API

The frontend uses two capability-gated endpoints:

```http
GET /api/process/service-reset/preview?process_name=Sonarr%20Movies&action=remove
```

```http
POST /api/process/service-reset
Content-Type: application/json

{
  "process_name": "Sonarr Movies",
  "action": "remove",
  "confirmation": "Sonarr Movies"
}
```

Supported actions are `reset` and `remove`. Use the preview returned immediately before the POST; DUMB recalculates and validates the plan again when applying it.

The DUMB API and DUMB Frontend control-plane services cannot be reset through this workflow.

## Related pages

- [Service pages](../frontend/service-pages.md)
- [Configuration](configuration.md)
- [Multi-instance setup](../reference/instances.md)
- [Process Management API](../api/process.md)
