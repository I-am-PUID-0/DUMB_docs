---
title: FFprobe Monitor
description: Monitor and recover stuck ffprobe processes from Sonarr or Radarr so media analysis and library import workflows do not remain blocked.
icon: lucide/activity
---

# FFprobe monitor

The monitor finds eligible `ffprobe` processes beneath DUMB-managed Sonarr or Radarr and runs a bounded probe of the same input. This can release a stalled media read, but it does not repair an unavailable mount or provider.

---

## When it runs

The monitor activates only when at least one Sonarr or Radarr instance is enabled. If neither service is running, the worker stays idle.

---

## How it works

1. Collects running Sonarr/Radarr process IDs.
2. Finds descendant `ffprobe` processes.
3. Selects processes in uninterruptible sleep (`D`) whose total process age exceeds the configured minimum.
4. Runs `ffprobe` on the same input within the configured timeout and per-cycle limits.

---

## Configuration in `dumb_config.json`

```json
"dumb": {
  "ffprobe_monitor": {
    "enabled": true,
    "interval_sec": 10,
    "min_process_age_sec": 30,
    "min_poke_interval_sec": 60,
    "poke_timeout_sec": 30,
    "max_pokes_per_cycle": 3,
    "cache_ttl_sec": 3600,
    "ffprobe_path": "ffprobe"
  }
}
```

### Settings reference

| Setting | Description |
|---------|-------------|
| `enabled` | Turns the monitor on or off. |
| `interval_sec` | Poll interval between checks. |
| `min_process_age_sec` | Minimum age for an ffprobe process before it is considered stuck. |
| `min_poke_interval_sec` | Minimum time between pokes for the same file path. |
| `poke_timeout_sec` | Timeout for the probe used to nudge the stuck process. |
| `max_pokes_per_cycle` | Maximum number of ffprobe pokes per polling cycle. |
| `cache_ttl_sec` | How long to cache recently poked file paths. |
| `ffprobe_path` | Path or command for ffprobe. |

---

## Operational notes

!!! warning "Scope"

    The monitor only targets ffprobe processes spawned under Sonarr/Radarr. It does not touch other ffprobe instances on the host.

!!! tip "Custom ffprobe binary"

    If your media stack uses a bundled ffprobe, set `ffprobe_path` to the full binary path.

---

## Troubleshooting

- If ffprobe checks never trigger, verify Sonarr/Radarr instances are enabled and visible to the DUMB process handler.
- If the monitor logs repeated timeouts, lower `max_pokes_per_cycle` or increase `poke_timeout_sec`.
