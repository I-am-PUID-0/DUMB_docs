import http from 'node:http'
import { once } from 'node:events'
import { dataset } from './capture-catalog.mjs'
import { utilityFixtureReply, utilityFixtureProfile } from './utility-scenarios.mjs'

export const FIXED_TIME = '2026-11-19T12:00:00.000Z'
// Obvious public documentation-demo value used only by the isolated Sonarr.
export const EXAMPLE_SONARR_KEY = '0123456789abcdef0123456789abcdef'
export const FRONTEND = Object.freeze({
  version: '1.91.0',
  tag: 'v1.91.0',
  commit: '66c90b93ea35abe546c07cbf643dc00a184bbd7f',
  repository: 'https://github.com/nicocapalbo/dmbdb',
})

// Every response is example data. Nothing is read from a DUMB installation.
export async function createFixture({ WebSocketServer, WebSocket, plan, metricsTrace, sonarrOrigin }) {
  const frontend = plan?.frontend || FRONTEND
  const backendVersion = plan?.backend?.version || '2.23.0'
  const timestamp = Date.parse(FIXED_TIME) / 1000
  const state = { checked: false, calls: [], configRequests: [], unexpected: [], websocketPaths: [], exampleOperations: [], expectedFailures: [] }
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
  const capabilities = plan?.capabilities ? structuredClone(plan.capabilities) : {
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
    ['DUMB API', 'dumb', backendVersion, 8000],
    ['DUMB Frontend', 'dumb_frontend', frontend.version, 3005],
    ['InfiniDysk', 'infinidysk', '1.2.0', 3000],
    ['Plex Media Server', 'plex', '1.0.0', 32400],
    ['Prowlarr', 'prowlarr', '1.0.0', 9696],
    ['Radarr', 'radarr', '5.0.0', 7878],
    ['Riven', 'riven_backend', '1.0.0', 8080],
    ['Zurg', 'zurg', '1.0.0', 9999],
    ['Rclone', 'rclone', '1.0.0', 5572],
    ['PostgreSQL', 'postgres', '1.0.0', 5432],
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
    checked_at: state.checked ? timestamp : null,
    next_check_at: null,
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
      ...structuredClone(utilityFixtureProfile(profile)?.serviceConfigs?.[key] || {}),
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
  let profile = 'standard'
  let setupStarted = false
  const nativeSuffix = requestPath => {
    const raw = requestPath.replace(/^\/service\/ui\/sonarr/, '') || '/'
    const base = new URL(sonarrOrigin).pathname.replace(/\/$/, '')
    return base && (raw === base || raw.startsWith(base + '/')) ? raw.slice(base.length) || '/' : raw
  }
  const setupExample = () => ({ ...structuredClone(dataset.setup_plan), protocol: 1,
    run_id: 'example-run', status: profile === 'onboarding-result' ? 'waiting_input' : profile === 'onboarding-error' ? 'failed' : 'running',
    message: 'Simulated documentation setup example. No application was installed or started.',
    created_at: timestamp, updated_at: timestamp })
  const sonarrService = () => ({ name: 'sonarr', config_key: 'sonarr', process_name: 'Sonarr', port: 8989, path: '/',
    url: '/ui/sonarr/', direct_url: '/ui/sonarr/', enabled: true })
  const defaultUi = () => ({ log_timestamp: { dateOrder: 'MDY', hourFormat: '24', zeroPad: true },
    sidebar: { auto_hide_on_navigation: false, geek_mode: false, show_all_services: false } })
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
    dumb_managed: [], external: [],
  }
  metrics.system.filesystems = ['/data', '/config'].map(containerPath => ({
    ...metrics.system.disk, path: containerPath, mount_point: containerPath,
    fs_type: 'ext4', available: true, inode: metrics.system.inode,
  }))
  const measuredSnapshot = point => {
    const result = structuredClone(metrics)
    if (point) {
      result.system.cpu_percent = point.cpu_percent
      result.system.mem = { total: point.memory_total, used: point.memory_used,
        available: Math.max(0, point.memory_total - point.memory_used), percent: point.memory_percent }
      result.dumb_managed = (point.processes || []).filter(row => row.name === 'DUMB Frontend')
      result.external = (point.processes || []).filter(row => row.name !== 'DUMB Frontend')
    } else {
      result.system.cpu_percent = null
      result.system.mem.percent = null
    }
    return result
  }
  const history = () => {
    const points = metricsTrace?.points || []
    const lastTick = points.at(-1)?.elapsed_ms || 0
    return points.map(point => ({ ...measuredSnapshot(point), timestamp: timestamp - (lastTick - point.elapsed_ms) / 1000 }))
  }
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
      if (sonarrOrigin && /^\/service\/ui\/sonarr(?:\/|$)/.test(url.pathname)) {
        const suffix = nativeSuffix(url.pathname)
        const negotiate = method === 'POST' && /^\/signalr\/[A-Za-z0-9/_-]*negotiate$/.test(suffix)
        if (!['GET', 'HEAD'].includes(method) && !negotiate) {
          state.unexpected.push({ method, path: '/service/ui/sonarr' + suffix })
          response.writeHead(405).end('Native example is read-only')
          return
        }
        const upstream = new URL(sonarrOrigin + suffix + url.search)
        const headers = {}
        for (const name of ['accept', 'accept-language', 'range', 'if-none-match', 'if-modified-since', 'content-type']) {
          if (request.headers[name]) headers[name] = request.headers[name]
        }
        headers['x-api-key'] = EXAMPLE_SONARR_KEY
        const result = await fetch(upstream, { method, headers, redirect: 'manual' })
        for (const name of ['content-type', 'cache-control', 'content-range', 'accept-ranges', 'etag', 'last-modified']) {
          if (result.headers.has(name)) response.setHeader(name, result.headers.get(name))
        }
        const location = result.headers.get('location')
        if (location) {
          const target = new URL(location, upstream)
          if (target.origin !== upstream.origin) throw new Error('Native example attempted an external redirect')
          const rootPath = new URL(sonarrOrigin).pathname.replace(/\/$/, '')
          response.setHeader('location', '/ui/sonarr' + target.pathname.replace(new RegExp('^' + rootPath.replace(/[.*+?^\x24{}()|[\]\\]/g, '\\$&')), '') + target.search)
        }
        response.statusCode = result.status
        response.end(method === 'HEAD' ? undefined : Buffer.from(await result.arrayBuffer()))
        return
      }
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
      // Specialist panels inspect profile-scoped public example state. No
      // operational write or wildcard fallback is introduced by these replies.
      const utilityReply = utilityFixtureReply(profile, method, path)
      if (utilityReply !== undefined) return send(utilityReply)
      if (get && path === '/api/process/rclone-optimizer/instances') return send({ instances: [] })
      if (get && path === '/api/process/symlink-backup-manifests') return send({ process_name: url.searchParams.get('process_name') || 'InfiniDysk', manifests: [] })
      if (get && path === '/api/process/runtime-log-level') return send({ configured_level: 'INFO', configured_uvicorn_level: 'INFO', effective_level: 'INFO', debug_enabled: false, override_active: false, temporary: false, resets_on_restart: true })
      if (get && path === '/api/health') return send({ status: 'healthy' })
      if (get && path === '/api/auth/status') return send({ enabled: ['login', 'authenticated'].includes(profile), has_users: profile !== 'account-setup', mode: 'local', setup_skipped: false })
      if (method === 'POST' && path === '/api/auth/verify' && profile === 'authenticated') return send({ valid: true, username: 'example' })
      if (get && path === '/api/auth/users') return send({ users: [{ username: 'example', disabled: false }] })
      if (get && path === '/api/auth/provider') return send({ mode: 'local', oidc: { enabled: false } })
      if (get && path === '/api/process/capabilities') return send(capabilities)
      // Source-shaped idle poll responses. No migration, backup or repair job
      // has run in this example; unknown routes and every operational write
      // outside the scoped in-memory onboarding simulation still fail closed.
      if (get && path === '/api/process/infinidysk-v2/status') return send({ protocol: 1,
        job_type: 'infinidysk_v2_migration', runtime_generation: '1', mode: 'fresh',
        current: { mount_backend: 'rclone', mount_path: '/mnt/debrid/example', database_provider: 'sqlite', import_strategy: 'preserve' },
        supported_mount_backends: ['rclone', 'fuse'], job: null, blocking_job_count: 0,
        capabilities: {}, blockers: ['Documentation example: no migration executor is connected.'], preview_task: null })
      if (get && path === '/api/process/infinidysk-migration/status') return send({ eligible: false, enabled: true,
        notice_due: false, status: 'not_needed', selected_mode: null, cleanup_available: false,
        rollback_artifacts_available: false, legacy: { repository: false, brand: false, service_key: false, paths: [], attached_services: [] },
        blockers: [], modes: [] })
      if (get && path === '/api/process/infinidysk-migration/job-status') return send({ job: null })
      if (get && path === '/api/process/rclone-optimizer/jobs') return send({ jobs: [] })
      if (get && path === '/api/process/backup-storage') return send({ protocol: 1, default_destination_id: '', destinations: [] })
      if (get && path === '/api/process/media-protection/status') return send({ enabled: false,
        recovery_stabilization_seconds: 30, recovery_timeout_seconds: 180, monitor_interval_seconds: 5, active: [], recent: [] })
      if (get && ['/api/process/postgres-migration/latest', '/api/process/arr-postgres-migration/latest'].includes(path)) return send({ job: null })
      if (get && path === '/api/process/symlink-backup-status') return send({ process_name: url.searchParams.get('process_name'), symlink_backup_status: null })
      if (get && path === '/api/process/symlink-job-latest') return send({ job: null })
      if (get && path === '/api/process/core-services') return send({ core_services: dataset.core_services })
      if (get && path === '/api/process/optional-services') return send({ optional_services: dataset.optional_services })
      if (get && ['/api/process/setup/runs/latest', '/api/process/setup/runs/example-run'].includes(path)) {
        if (profile === 'setup-connections') return send({ ...setupExample(), status: 'waiting_input' })
        if (setupStarted) return send(setupExample())
        state.expectedFailures.push({ method, path, status: 404, profile, reason: 'Source contract: no example setup run exists before the simulated start.' })
        return send({ detail: path.endsWith('/latest') ? 'No setup run has been created.' : 'The requested setup record was not found.' }, 404)
      }
      const exampleAction = /^\/api\/process\/setup\/runs\/example-run\/actions\/([^/]+)$/.exec(path)
      if (method === 'POST' && profile === 'setup-connections' && exampleAction
        && dataset.setup_plan.actions.some(action => action.id === decodeURIComponent(exampleAction[1]))
        && onlyKeys(body, ['operation', 'values']) && body.operation === 'recheck'
        && object(body.values) && keys(body.values).length === 0) {
        state.exampleOperations.push({ method, path, profile, operation: 'in_memory_example_recheck' })
        return send({ ...setupExample(), status: 'waiting_input' })
      }
      if (method === 'POST' && path === '/api/process/setup/plan') return send({ ...structuredClone(dataset.setup_plan), values: body.arrangement?.values || {} })
      if (method === 'POST' && path === '/api/process/setup/runs' && /^onboarding-(progress|result|error)$/.test(profile)
        && onlyKeys(body, ['plan_id', 'idempotency_key']) && body.plan_id === dataset.setup_plan.plan_id) {
        state.exampleOperations.push({ method, path, profile, operation: 'in_memory_simulated_setup_run' })
        setupStarted = true
        return send(setupExample())
      }
      if (method === 'POST' && path === '/api/process/start-core-service' && /^onboarding-(progress|result|error)$/.test(profile)
        && onlyKeys(body, ['core_services', 'optional_services', 'optional_service_options']) && Array.isArray(body.core_services)
        && (!Object.hasOwn(body, 'optional_service_options') || object(body.optional_service_options) && !keys(body.optional_service_options).length)) {
        const simulatedProfile = profile
        state.exampleOperations.push({ method, path, profile, operation: 'in_memory_simulated_legacy_setup' })
        setupStarted = true
        if (simulatedProfile === 'onboarding-progress') await new Promise(resolve => setTimeout(resolve, 6000))
        if (simulatedProfile === 'onboarding-error') {
          state.expectedFailures.push({ method, path, status: 400, profile })
          return send({ detail: 'Simulated example: provider connection needs attention. No application was installed.' }, 400)
        }
        return send({ results: [{ process_name: 'Riven', status: 'example_only', message: 'Simulated documentation example; no installation was performed.' }] })
      }
      if (get && path === '/api/process/installation-backups/status') return send(dataset.backup_status)
      if (get && path === '/api/process/installation-backups/services') return send({
        protocol: 1,
        // Public identities only, matching the protocol-1 service-choice list.
        // A capture never checks persistence ownership or backup eligibility.
        services: definitions.filter(([, key]) => !['dumb', 'dumb_frontend'].includes(key)).map(([name, key, , , enabled]) => ({
          id: key, key, instance_name: null, name, enabled: enabled !== false,
          available: false, required_service_ids: [],
          blocking_reasons: ['Backup availability has not been checked for this example.'],
        })),
      })
      if (get && path === '/api/process/installation-backups/catalog') return send({ protocol: 1, archives: [], items: [] })
      if (get && path === '/api/process/installation-backups/preview/status') return send({ protocol: 1, controller_session: 'example-session', preview: null })
      if (get && path === '/api/process/backup-storage/catalog') return send({ protocol: 1, default_destination_id: '', destinations: [] })
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
      if (method === 'POST' && path === '/api/config/onboarding-completed' && /^onboarding-(progress|result|error)$/.test(profile)) {
        state.exampleOperations.push({ method, path, profile, operation: 'in_memory_example_navigation_flag' })
        return send({ completed: true, example_only: true })
      }
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
      if (get && path === '/api/config/service-ui') return send({ enabled: profile === 'embedded' && Boolean(sonarrOrigin), services: sonarrOrigin ? [sonarrService()] : [] })
      if (get && path === '/api/config/service-ui-map') return send(sonarrOrigin ? { sonarr: 'sonarr' } : {})
      if (get && path === '/api/metrics') return send(measuredSnapshot(metricsTrace?.latest))
      if (get && ['/api/metrics/history', '/api/metrics/history_series'].includes(path)) return send({ items: history(), truncated: false, bucket_seconds: 1 })
      if (get && path === '/api/metrics/filesystems') return send({ filesystems: metrics.system.filesystems, candidates: metrics.system.filesystems })
      if (get && path === '/api/metrics/network-interfaces') return send({ interfaces: metrics.system.network_interfaces, candidates: metrics.system.network_interfaces })
      if (get && path === '/api/metrics/history/storage') return send({ configured_provider: 'sqlite', active_provider: 'sqlite', fallback_active: false,
        sqlite: { path: '/config/metrics/metrics.sqlite', sample_count: history().length, size_bytes: 2 * 1024 ** 2 },
        legacy: { files: 0, imported: 0, skipped: 0 } })
      if (get && path === '/api/logs') {
        const text = url.searchParams.get('process_name') === 'DUMB' ? controllerLogs : logs
        if (!url.searchParams.has('tail_bytes')) return send({ log: text })
        const cursor = Buffer.byteLength(text)
        return send({ chunk: Number(url.searchParams.get('cursor')) === cursor ? '' : text,
          cursor, size: cursor, file_id: 'example-log', reset: !url.searchParams.has('cursor') })
      }
      if (get && path === '/api/notifications/config') return send(dataset.notification_config)
      if (get && path === '/api/notifications/events') return send({ event_types: ['service_unhealthy', 'update_available', 'backup_completed'] })
      if (get && path === '/api/notifications/history') return send({ items: [], total: 0 })
      if (get && path === '/api/ai/settings') return send(dataset.ai_settings)
      if (get && path === '/api/ai/presets') return send({ service: [], stack: [{ id: 'overview', label: 'Stack overview', description: 'Review example service evidence.' }] })
      if (get && path === '/api/integrations/authelia/status') return send({ enabled: false, configured: false, installed: false })
      if (get && path === '/api/integrations/authelia/tpa-domains') return send({ domains: [] })
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
    if (sonarrOrigin && WebSocket && /^\/service\/ui\/sonarr(?:\/|$)/.test(path)) {
      const nativeUrl = new URL(request.url, 'http://127.0.0.1')
      const suffix = nativeSuffix(nativeUrl.pathname) + nativeUrl.search
      const upstream = new WebSocket(sonarrOrigin.replace(/^http/, 'ws') + suffix)
      sockets.handleUpgrade(request, socket, head, client => {
        const pending = []
        client.on('message', (data, binary) => { if (upstream.readyState === 1) upstream.send(data, { binary }); else pending.push([data, binary]) })
        upstream.on('open', () => { for (const [data, binary] of pending) upstream.send(data, { binary }); pending.length = 0 })
        upstream.on('message', (data, binary) => { if (client.readyState === 1) client.send(data, { binary }) })
        client.once('close', () => upstream.close())
        upstream.once('close', () => client.close())
        upstream.once('error', () => { upstream.terminate(); client.close() })
      })
      return
    }
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
        if (path === '/ws/metrics') ws.send(JSON.stringify({ type: 'snapshot', data: measuredSnapshot(metricsTrace?.latest) }))
        if (path === '/ws/logs' && profile === 'realtime-logs') ws.send('2026-11-19 11:59:00 - INFO - DUMB: Documentation example: capture transport is isolated; no production services were contacted.\n')
        if (path === '/ws/logs' && setupStarted && /^onboarding-(progress|result|error)$/.test(profile)) {
          ws.send('2026-11-19 11:59:01 - INFO - DUMB: Simulated setup example: reviewing Riven dependencies; no installation is running.\n')
          ws.send('2026-11-19 11:59:02 - WARNING - DUMB: Provider connections and example storage access remain unverified.\n')
        }
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
    async waitForMetrics() {
      for (let attempt = 0; attempt < 40 && (metricsTrace?.points.length || 0) < 12; attempt++) await new Promise(resolve => setTimeout(resolve, 500))
      if (!metricsTrace?.latest) throw new Error('No measured capture-container counters are available')
    },
    expectedFailure(pathname, status) { return state.expectedFailures.some(row => row.path === pathname && row.status === status && row.profile === profile) },
    resetChecks() { state.checked = false },
    resetScenario(nextProfile) { profile = nextProfile; setupStarted = false; state.checked = false; configuration.dumb.ui = defaultUi() },
    resetPreferences() {
      configuration.dumb.ui = defaultUi()
    },
    async close() {
      for (const socket of sockets.clients) socket.terminate()
      await new Promise(resolve => sockets.close(resolve))
      await new Promise(resolve => { server.close(resolve); server.closeAllConnections() })
    },
  }
}
