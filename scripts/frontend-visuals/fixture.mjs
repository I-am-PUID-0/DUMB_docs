import http from 'node:http'
import { once } from 'node:events'

export const FIXED_TIME = '2026-11-19T12:00:00.000Z'
export const FRONTEND = Object.freeze({
  version: '1.91.0',
  tag: 'v1.91.0',
  commit: '66c90b93ea35abe546c07cbf643dc00a184bbd7f',
  repository: 'https://github.com/nicocapalbo/dmbdb',
})

// Every response is example data. Nothing is read from a DUMB installation.
export async function createFixture({ WebSocketServer }) {
  const timestamp = Date.parse(FIXED_TIME) / 1000
  const state = { checked: false, calls: [], configRequests: [], unexpected: [], websocketPaths: [] }
  const object = value => value !== null && typeof value === 'object' && !Array.isArray(value)
  const keys = value => object(value) ? Object.keys(value) : []
  const onlyKeys = (value, allowed) => object(value) && keys(value).every(key => allowed.includes(key))
  const sidebarTypes = {
    show_all_services: 'boolean', compact_mode: 'boolean', tools_open: 'boolean',
    auto_hide_on_navigation: 'boolean', geek_mode: 'boolean', quick_filter: 'string',
    service_search: 'string', active_saved_view_id: 'string', service_order: 'array',
    saved_views: 'array', service_shortcuts: 'object',
  }
  const sidebarPreference = value => onlyKeys(value, Object.keys(sidebarTypes)) && keys(value).every(key => {
    if (sidebarTypes[key] === 'array') return Array.isArray(value[key])
    if (sidebarTypes[key] === 'object') return object(value[key])
    return typeof value[key] === sidebarTypes[key]
  })
  const timestampPreference = value => onlyKeys(value, ['dateOrder', 'hourFormat', 'zeroPad'])
    && (!Object.hasOwn(value, 'dateOrder') || ['MDY', 'DMY'].includes(value.dateOrder))
    && (!Object.hasOwn(value, 'hourFormat') || ['12', '24'].includes(value.hourFormat))
    && (!Object.hasOwn(value, 'zeroPad') || typeof value.zeroPad === 'boolean')
  const uiPreferences = body => {
    if (!onlyKeys(body, ['updates', 'persist']) || (Object.hasOwn(body, 'persist') && typeof body.persist !== 'boolean')) return null
    const updates = body.updates
    if (!onlyKeys(updates, ['dumb']) || !onlyKeys(updates.dumb, ['ui'])) return null
    const ui = updates.dumb.ui
    if (!onlyKeys(ui, ['sidebar', 'log_timestamp']) || !keys(ui).length) return null
    if (Object.hasOwn(ui, 'sidebar') && !sidebarPreference(ui.sidebar)) return null
    if (Object.hasOwn(ui, 'log_timestamp') && !timestampPreference(ui.log_timestamp)) return null
    return ui
  }
  const capabilities = {
    startup_lifecycle: true,
    dashboard_bulk_updates: true,
    auto_update_mode: true,
    auto_update_start_time: true,
    metrics_history_storage: true,
    metrics_filesystem_selection: true,
    metrics_network_interface_selection: true,
    installation_backup: false,
    notifications: false,
    ai_assistant: false,
    media_library_protection: false,
    symlink_repair: false,
    database_health: false,
    setup_arrangements: false,
    seerr_sync: false,
    infinidysk_v2_migration: false,
    authelia_integration: false,
  }
  const definitions = [
    ['DUMB API', 'dumb', '2.23.0', 8000],
    ['DUMB Frontend', 'dumb_frontend', FRONTEND.version, 3005],
    ['InfiniDysk', 'infinidysk', '1.2.0', 3000],
    ['Plex Media Server', 'plex', '1.0.0', 32400],
    ['Prowlarr', 'prowlarr', '1.0.0', 9696],
    ['Radarr', 'radarr', '5.0.0', 7878],
    ['Sonarr', 'sonarr', '4.0.0', 8989],
    ['Tautulli', 'tautulli', '2.0.0', 8181, false],
  ]
  const status = name => ({
    process_name: name,
    status: definitions.find(row => row[0] === name)?.[4] === false ? 'stopped' : 'running',
    healthy: definitions.find(row => row[0] === name)?.[4] === false ? null : true,
    health_status: definitions.find(row => row[0] === name)?.[4] === false ? null : 'healthy',
    health_reason: definitions.find(row => row[0] === name)?.[4] === false ? 'Disabled in the example configuration.' : 'Example application is reachable.',
    health_details: { process: true, ports: true },
  })
  const update = name => ({
    process_name: name,
    status: state.checked && name === 'Sonarr' ? 'update_available' : 'up_to_date',
    current_version: name === 'Sonarr' ? '4.0.0' : '1.0.0',
    available_version: state.checked && name === 'Sonarr' ? '4.0.1' : null,
    last_checked: state.checked ? timestamp : null,
    next_check: null,
    message: state.checked ? 'Example update check completed. No update was installed.' : 'Ready to check for updates.',
    release_url: 'https://github.com/Sonarr/Sonarr/releases',
  })
  const processes = () => definitions.map(([name, key, version, port, enabled = true]) => ({
    process_name: name, name, config_key: key, version,
    enabled,
    supports_manual_update: ['sonarr', 'radarr', 'prowlarr'].includes(key),
    repo_url: key.startsWith('dumb') ? FRONTEND.repository : 'https://github.com/Sonarr/Sonarr',
    config: {
      enabled, process_name: name, onboarding_completed: true, port,
      log_file: `/log/${key}.log`, log_level: 'INFO',
      auto_update: false, auto_update_mode: 'check_only',
      auto_update_interval: 24, auto_update_start_time: '04:00',
      ...(key === 'sonarr' ? { config_dir: '/data/sonarr', core_service: 'infinidysk', wait_for_url: ['http://127.0.0.1:3000/health'] } : {}),
    },
    ...status(name),
    update_status: update(name),
  }))
  const configuration = {
    dumb: {
      onboarding_completed: true,
      plex_token: '', github_token: '', github_username: '',
      auto_restart: { enabled: false, restart_on_unhealthy: true, healthcheck_interval: 30,
        unhealthy_threshold: 3, grace_period_seconds: 30, max_restarts: 3,
        window_seconds: 300, backoff_seconds: [5, 15, 45, 120], services: [] },
      metrics: { system_scope: 'auto', filesystem_paths: ['/data', '/config'], network_interfaces: ['eth0'],
        history_enabled: true, history_interval_sec: 5, history_retention_days: 7,
        history_max_total_mb: 100, storage: { provider: 'sqlite', sqlite_path: '/config/metrics/metrics.sqlite' } },
      ui: {
        log_timestamp: { dateOrder: 'MDY', hourFormat: '24', zeroPad: true },
        sidebar: { auto_hide_on_navigation: false, geek_mode: false, show_all_services: false },
      },
    },
  }
  const logs = [
    '2026-11-19 11:59:10.0|INFO|ImportListSyncService|Checking Example Series for new episodes',
    '2026-11-19 11:59:12.0|INFO|DownloadDecisionMaker|Example Series S01E01 is available',
    '2026-11-19 11:59:15.0|WARNING|DownloadService|Example Series: waiting for the download client connection',
    '2026-11-19 11:59:20.0|INFO|DownloadService|Example Series: connection restored',
    '2026-11-19 11:59:24.0|INFO|DownloadedEpisodesImportService|Example Series S01E01 imported successfully',
    '2026-11-19 11:59:30.0|INFO|RefreshSeriesService|Example Series library refresh completed',
    '2026-11-19 11:59:35.0|INFO|MediaCoverService|Example Movie artwork refreshed',
  ].join('\n') + '\n'
  const controllerLogs = '2026-11-19 11:59:00 - INFO - DUMB: Example services are ready.\n'
  const metrics = {
    timestamp,
    system: {
      cpu_percent: 12.4, cpu_count: 4, uptime: 3600, scope_effective: 'cgroup',
      hostname: 'example', platform: 'Linux', load_avg: [0.38, 0.42, 0.36],
      mem: { total: 8 * 1024 ** 3, used: 2 * 1024 ** 3, available: 6 * 1024 ** 3, percent: 25 },
      swap: { total: 1024 ** 3, used: 0, free: 1024 ** 3, percent: 0 },
      disk: { path: '/data', total: 500 * 1024 ** 3, used: 125 * 1024 ** 3, free: 375 * 1024 ** 3, percent: 25 },
      inode: { total: 1000000, used: 120000, free: 880000, percent: 12 },
      disk_io: { read_bytes: 8 * 1024 ** 3, write_bytes: 2 * 1024 ** 3 },
      net_io: { sent_bytes: 2 * 1024 ** 3, recv_bytes: 12 * 1024 ** 3 },
      filesystems: [], network_interfaces: [{ name: 'eth0', available: true, isup: true,
        bytes_sent: 2 * 1024 ** 3, bytes_recv: 12 * 1024 ** 3, speed_mbps: 1000, mtu: 1500 }],
    },
    dumb_managed: definitions.filter(row => row[4] !== false).map(([name], index) => ({
      name, process_name: name, pid: 1000 + index, status: 'running', uptime: 3600,
      cpu_percent: 1.2 + index * 0.4, rss: (90 + index * 20) * 1024 ** 2,
      num_threads: 4, disk_io: { read_bytes: index * 1024 ** 2, write_bytes: index * 256 * 1024 },
    })), external: [],
  }
  metrics.system.filesystems = ['/data', '/config'].map(containerPath => ({
    ...metrics.system.disk, path: containerPath, mount_point: containerPath,
    fs_type: 'ext4', available: true, inode: metrics.system.inode,
  }))
  const history = Array.from({ length: 72 }, (_, index) => ({
    ...structuredClone(metrics), timestamp: timestamp - (71 - index) * 300,
    system: { ...structuredClone(metrics.system), cpu_percent: 18 + Math.sin(index / 4) * 7,
      mem: { ...metrics.system.mem, percent: 25 + Math.sin(index / 9) * 3 },
      net_io: { sent_bytes: (index + 1) * 25 * 1024 ** 2, recv_bytes: (index + 1) * 100 * 1024 ** 2 },
      disk_io: { read_bytes: (index + 1) * 90 * 1024 ** 2, write_bytes: (index + 1) * 10 * 1024 ** 2 } },
  }))
  const dependencyGraph = scope => ({
    scope, updated_at: FIXED_TIME,
    context: { mode: 'core', key: 'sonarr', core: { key: 'sonarr', name: 'Sonarr', dependencies: ['infinidysk'] } },
    core_services: [{ key: 'sonarr', name: 'Sonarr', dependencies: ['infinidysk'] }, { key: 'infinidysk', name: 'InfiniDysk', dependencies: [] }],
    processes: processes(), statuses: Object.fromEntries(definitions.map(row => [row[0], status(row[0]).status])),
    startup_order: [{ key: 'infinidysk', label: 'InfiniDysk', state: 'running' }, { key: 'sonarr', label: 'Sonarr', state: 'running' }],
    dependency_rows: [{ key: 'infinidysk', label: 'InfiniDysk', state: 'running', process_count: 1,
      starter_process_name: 'InfiniDysk', signals: ['core_service_fields', 'wait_for_url'] }],
    dependent_rows: [], linked_outgoing_rows: [{ key: 'infinidysk', process_name: 'InfiniDysk',
      label: 'InfiniDysk', signals: ['wait_for_url'], classification: 'hard_configured' }], linked_incoming_rows: [],
    nodes: ['InfiniDysk', 'Sonarr'].map(name => ({ key: name.toLowerCase(), process_name: name, label: name, state: 'running' })),
    edges: [{ source: 'InfiniDysk', target: 'Sonarr', strength: 'hard_configured', signals: ['wait_for_url'] }],
    parallel_groups: [], dependency_truth_table: [],
  })
  const globalSchema = { type: 'object', properties: { dumb: { type: 'object', properties: { auto_restart: { type: 'object' } } } } }
  const processSchema = { type: 'object', additionalProperties: true, properties: {
    enabled: { type: 'boolean' }, process_name: { type: 'string' }, port: { type: 'integer' },
    config_dir: { type: 'string' }, core_service: { type: 'string' },
  } }
  let origin
  const server = http.createServer(async (request, response) => {
    const method = String(request.method || 'UNKNOWN').replace(/[^A-Z]/g, '').slice(0, 16) || 'UNKNOWN'
    let path = '/invalid-request'
    try {
      const url = new URL(request.url, 'http://127.0.0.1')
      const prefix = /^\/(auth|process|config|logs|metrics|health|notifications|ai|integrations)(?:\/|$)/
      path = prefix.test(url.pathname) ? '/api' + url.pathname : url.pathname
      const call = { method, path }
      state.calls.push(call)
      let raw = ''
      for await (const chunk of request) {
        raw += chunk
        if (raw.length > 128 * 1024) throw new Error('Example request exceeded its limit')
      }
      const body = raw ? JSON.parse(raw) : {}
      if (method === 'POST' && path === '/api/config/' && body && typeof body === 'object') {
        // Key names explain transport differences without recording any values.
        const diagnostic = {
          body_keys: keys(body), updates_keys: keys(body.updates),
          dumb_keys: keys(body.updates?.dumb), ui_keys: keys(body.updates?.dumb?.ui),
          sidebar_keys: keys(body.updates?.dumb?.ui?.sidebar),
          log_timestamp_keys: keys(body.updates?.dumb?.ui?.log_timestamp), accepted: false,
        }
        state.configRequests.push(diagnostic)
        call.body_keys = diagnostic.body_keys
      }
      response.setHeader('content-type', 'application/json; charset=utf-8')
      response.setHeader('cache-control', 'no-store')
      const send = (data, code = 200) => { response.statusCode = code; response.end(JSON.stringify(data)) }
      const get = method === 'GET'
      if (get && path === '/api/health') return send({ status: 'healthy' })
      if (get && path === '/api/auth/status') return send({ enabled: false, has_users: true, mode: 'local', setup_skipped: false })
      if (get && path === '/api/auth/users') return send({ users: [{ username: 'example', disabled: false }] })
      if (get && path === '/api/auth/provider') return send({ mode: 'local', oidc: { enabled: false } })
      if (get && path === '/api/process/capabilities') return send(capabilities)
      if (get && path === '/api/process/dependency-graph') return send(dependencyGraph(url.searchParams.get('scope') || 'runtime'))
      if (get && path === '/api/process/processes') return send({ processes: processes() })
      if (get && path === '/api/process/') {
        const service = processes().find(row => row.process_name === url.searchParams.get('process_name'))
        return send(service || { detail: 'Unknown example service' }, service ? 200 : 404)
      }
      if (get && path === '/api/process/service-status') return send(status(url.searchParams.get('process_name') || 'Sonarr'))
      if (get && path === '/api/process/startup-status') return send({ phase: 'ready', terminal: true, expected_services: definitions.map(row => row[0]), services: {} })
      if (get && path === '/api/process/update-notices') return send({ available: [], notices: [] })
      if (get && path === '/api/process/update-status') return send({ update_status: update(url.searchParams.get('process_name') || 'Sonarr') })
      if (get && path === '/api/process/symlink-manifest-files') return send({ files: [], count: 0, directory: '/config/symlink-repair/snapshots' })
      if (method === 'POST' && path === '/api/process/update-check' && body.process_name === 'Sonarr') {
        await new Promise(resolve => setTimeout(resolve, 700))
        state.checked = true
        return send(update('Sonarr'))
      }
      if (get && path === '/api/config/onboarding-status') return send({ needs_onboarding: false, completed: true, onboarding_completed: true })
      if (get && path === '/api/config/') {
        const name = url.searchParams.get('process_name')
        if (!name) return send(configuration)
        const service = processes().find(row => row.process_name === name)
        return send(service?.config || { detail: 'Unknown example service' }, service ? 200 : 404)
      }
      if (method === 'POST' && path === '/api/config/') {
        const preferences = uiPreferences(body)
        if (preferences) {
          for (const [key, value] of Object.entries(preferences)) {
            configuration.dumb.ui[key] = { ...configuration.dumb.ui[key], ...structuredClone(value) }
          }
          state.configRequests[state.configRequests.length - 1].accepted = 'example_ui_preferences'
          return send({ message: 'Example UI preferences saved in memory.', config: configuration, persisted: false })
        }
      }
      // Permit only a value-free legacy read request. Any write-shaped body,
      // except the explicitly whitelisted UI preferences above, remains refused.
      if (method === 'POST' && path === '/api/config/' && body && typeof body === 'object'
        && !Array.isArray(body) && Object.keys(body).every(key => key === 'process_name')) {
        if (!body.process_name) return send(configuration)
        const service = processes().find(row => row.process_name === body.process_name)
        return send(service?.config || { detail: 'Unknown example service' }, service ? 200 : 404)
      }
      if (get && path === '/api/config/schema') return send(globalSchema)
      if (method === 'POST' && path === '/api/config/process-config/schema') return send(processSchema)
      // This POST reads application configuration. An update payload is refused.
      if (method === 'POST' && path === '/api/config/service-config' && !Object.hasOwn(body, 'updates')) return send({ config: { InstanceName: 'Example Sonarr', Port: 8989, LogLevel: 'Info' }, config_format: 'json' })
      if (get && path === '/api/config/service-ui') return send({ enabled: false, services: [] })
      if (get && path === '/api/config/service-ui-map') return send({})
      if (get && path === '/api/metrics') return send(metrics)
      if (get && ['/api/metrics/history', '/api/metrics/history_series'].includes(path)) return send({ items: history, truncated: false, bucket_seconds: 300 })
      if (get && path === '/api/metrics/filesystems') return send({ filesystems: metrics.system.filesystems, candidates: metrics.system.filesystems })
      if (get && path === '/api/metrics/network-interfaces') return send({ interfaces: metrics.system.network_interfaces, candidates: metrics.system.network_interfaces })
      if (get && path === '/api/metrics/history/storage') return send({ configured_provider: 'sqlite', active_provider: 'sqlite', fallback_active: false,
        sqlite: { path: '/config/metrics/metrics.sqlite', sample_count: history.length, size_bytes: 2 * 1024 ** 2 },
        legacy: { files: 0, imported: 0, skipped: 0 } })
      if (get && path === '/api/logs') {
        const text = url.searchParams.get('process_name') === 'DUMB' ? controllerLogs : logs
        if (!url.searchParams.has('tail_bytes')) return send({ log: text })
        const cursor = Buffer.byteLength(text)
        return send({ chunk: Number(url.searchParams.get('cursor')) === cursor ? '' : text,
          cursor, size: cursor, file_id: 'example-log', reset: !url.searchParams.has('cursor') })
      }
      if (get && path === '/api/notifications/config') return send({ enabled: false, destinations: [] })
      if (get && path === '/api/notifications/events') return send({ events: [] })
      if (get && path === '/api/notifications/history') return send({ items: [], total: 0 })
      if (get && path === '/api/ai/settings') return send({ enabled: false, provider: 'ollama', profiles: [] })
      if (get && path === '/api/ai/presets') return send({ service: [] })
      state.unexpected.push({ method, path })
      return send({ detail: 'This operation is not part of the example capture.' }, 405)
    } catch {
      state.unexpected.push({ method, path })
      response.statusCode = 400
      response.setHeader('content-type', 'application/json; charset=utf-8')
      response.end(JSON.stringify({ detail: 'Invalid example request' }))
    }
  })
  const sockets = new WebSocketServer({ noServer: true })
  server.on('upgrade', (request, socket, head) => {
    const path = new URL(request.url, 'http://127.0.0.1').pathname
    if (!['/ws/status', '/ws/logs', '/ws/metrics'].includes(path)) {
      state.unexpected.push({ method: 'WS', path })
      socket.destroy()
      return
    }
    state.websocketPaths.push(path)
    sockets.handleUpgrade(request, socket, head, ws => {
      const transmit = () => {
        if (ws.readyState !== 1) return
        if (path === '/ws/status') ws.send(JSON.stringify({ type: 'status', timestamp, processes: definitions.map(row => status(row[0])) }))
        if (path === '/ws/metrics') ws.send(JSON.stringify({ type: 'snapshot', data: metrics }))
      }
      ws.on('message', () => {
        if (ws.readyState === 1) ws.send(path === '/ws/logs' ? 'pong' : JSON.stringify({ type: 'pong' }))
      })
      transmit()
      const timer = setInterval(transmit, 2000)
      ws.once('close', () => clearInterval(timer))
      ws.once('error', () => clearInterval(timer))
    })
  })
  server.listen(0, '127.0.0.1')
  await once(server, 'listening')
  origin = 'http://127.0.0.1:' + server.address().port
  return {
    origin, state,
    resetChecks() { state.checked = false },
    resetPreferences() {
      configuration.dumb.ui = {
        log_timestamp: { dateOrder: 'MDY', hourFormat: '24', zeroPad: true },
        sidebar: { auto_hide_on_navigation: false, geek_mode: false, show_all_services: false },
      }
    },
    async close() {
      for (const socket of sockets.clients) socket.terminate()
      await new Promise(resolve => sockets.close(resolve))
      await new Promise(resolve => { server.close(resolve); server.closeAllConnections() })
    },
  }
}
