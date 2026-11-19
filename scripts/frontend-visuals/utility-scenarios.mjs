// Actual packaged Nuxt specialist panels. Opening and inspection only; no jobs.

export const utilityScenarios = [
  { id: 'database-health', title: 'Database health', route: '/services/Sonarr', profile: 'utility-database-health',
    features: ['features/metrics', 'frontend/metrics'], required_capabilities: ['database_health_metrics'],
    required_frontend_files: ['components/DatabaseHealthPanel.vue'], kinds: ['image'],
    description: 'Review passive database monitoring controls with example disabled-state evidence; do not enable monitoring or request a fresh probe.' },
  { id: 'library-protection', title: 'Media library protection', route: '/services/Plex%20Media%20Server', profile: 'utility-library-protection',
    features: ['features/media-library-protection'], required_capabilities: ['media_library_protection'],
    required_frontend_files: ['components/MediaProtectionPanel.vue'], kinds: ['image'],
    description: 'Review example library protection and Plex settings without changing policy, scanning, or contacting Plex.' },
  { id: 'symlink-tools', title: 'Symlink repair and snapshots', route: '/services/InfiniDysk', profile: 'utility-symlink-tools',
    features: ['features/symlinks'], required_capabilities: ['symlink_repair'], kinds: ['image'],
    description: 'Open the real Symlinks panel and inspect repair, snapshot and schedule controls without running an operation.' },
  { id: 'rclone-optimizer', title: 'Rclone streaming optimizer', route: '/services/Rclone', profile: 'utility-rclone-optimizer',
    features: ['features/rclone-optimizer'], required_capabilities: ['rclone_optimizer_infinidysk'],
    required_frontend_files: ['components/RcloneOptimizerPanel.vue'], kinds: ['image'],
    description: 'Review real optimizer safety limits and example content discovery; no benchmark, provider read, apply or rollback is requested.' },
  { id: 'infinidysk-v2-install', title: 'InfiniDysk 2 installation review', route: '/services/InfiniDysk', profile: 'utility-infinidysk-v2-install',
    features: ['services/core/infinidysk-installation', 'features/infinidysk-v2-migration'],
    required_capabilities: ['infinidysk_v2', 'infinidysk_v2_migration'], required_protocols: { infinidysk_v2_migration_protocol: 1 },
    required_frontend_files: ['components/InfiniDyskV2Panel.vue'], minimum_api_version: '2.24.0', kinds: ['image'],
    description: 'Review fresh-install mount and backup choices in the guarded InfiniDysk 2 panel; no preview, preparation or installation starts.' },
  { id: 'infinidysk-namespace-migration', title: 'Legacy namespace migration review', route: '/services/InfiniDysk', profile: 'utility-namespace-migration',
    features: ['services/core/infinidysk-migration'], required_capabilities: ['infinidysk_migration'],
    required_frontend_files: ['components/InfiniDyskMigrationNotice.vue'], kinds: ['image'],
    description: 'Review legacy identity and full-namespace choices using example eligibility; do not run preflight, migration, playback control or cleanup.' },
  { id: 'postgres-migration', title: 'SQLite to PostgreSQL migration review', route: '/services/Sonarr', profile: 'utility-postgres-migration',
    features: ['features/arr-postgres-migration', 'services/dependent/postgres'], required_capabilities: ['postgres_migration'],
    required_frontend_files: ['components/ArrPostgresMigrationPanel.vue'], kinds: ['image'],
    description: 'Inspect the source-shaped read-only preflight and backup requirements; no rehearsal, cutover or rollback is performed.' },
]

export async function runUtilityScenario({ page, scenario, ui }) {
  await ui.serviceReady(page)
  switch (scenario.id) {
    case 'database-health':
      await ui.serviceTool(page, 'Database Health')
      await page.getByRole('heading', { name: /^Database Health/ }).waitFor()
      await page.getByText('Loading database health…', { exact: true }).waitFor({ state: 'hidden' })
      await page.getByRole('button', { name: 'Enable monitoring', exact: true }).waitFor()
      return
    case 'library-protection':
      await ui.serviceTool(page, 'Library Protection')
      await page.getByRole('heading', { name: /^Media Library Protection/ }).waitFor()
      await page.getByRole('heading', { name: 'Protection policy', exact: true }).waitFor()
      return
    case 'symlink-tools':
      await ui.serviceTool(page, 'Symlinks')
      await page.getByTitle('Close Symlinks panel.', { exact: true }).waitFor()
      await page.getByTitle('Symlink tools.', { exact: true }).waitFor()
      return
    case 'rclone-optimizer':
      await ui.hoverClick(page, page.getByText('Rclone Optimizer', { exact: true }).first())
      await page.getByRole('heading', { name: /InfiniDysk rclone streaming optimizer/ }).waitFor()
      await page.getByPlaceholder('Filter available media paths', { exact: true }).waitFor()
      return
    case 'infinidysk-v2-install':
      await ui.serviceTool(page, 'InfiniDysk 2 migration')
      await page.getByRole('dialog', { name: 'InfiniDysk 2 migration', exact: true }).waitFor()
      await page.getByText('Fresh installation:', { exact: false }).first().waitFor()
      return
    case 'infinidysk-namespace-migration': {
      const review = page.getByRole('button', { name: 'Review migration', exact: true })
      const manual = page.getByRole('button', { name: 'InfiniDysk namespace migration', exact: true })
      await review.or(manual).first().waitFor()
      await ui.hoverClick(page, await review.isVisible() ? review : manual)
      await page.getByRole('heading', { name: 'Migrate NzbDAV to InfiniDysk', exact: true }).waitFor()
      const fullNamespace = page.locator('input[type="radio"][value="full_namespace"]')
      if (await fullNamespace.count()) await fullNamespace.check()
      await page.getByText('Back up your stack before continuing.', { exact: true }).waitFor()
      return
    }
    case 'postgres-migration':
      await ui.serviceTool(page, 'Database Migration')
      await page.getByRole('heading', { name: 'SQLite → PostgreSQL migration', exact: true }).waitFor()
      await page.getByText('Running preflight checks…', { exact: true }).waitFor({ state: 'hidden' })
      await page.getByText('1. Preflight', { exact: true }).waitFor()
      return
    default:
      throw new Error('Unknown specialist review scenario: ' + scenario.id)
  }
}

const plexSettings = Object.fromEntries([
  ['autoEmptyTrash', false], ['fSEventLibraryUpdatesEnabled', false],
  ['fSEventLibraryPartialScanEnabled', true], ['scheduledLibraryUpdatesEnabled', false],
  ['scheduledLibraryUpdateInterval', 12],
].map(([key, value]) => [key, { value }]))

// These payloads follow the selected source's existing API shape. They are
// public example state, not results from a real probe or completed operation.
export function utilityFixtureProfile(profile) {
  const replies = {}
  const serviceConfigs = {}
  if (profile === 'utility-database-health') {
    replies['/api/metrics/database-health'] = { services: [{
      id: 'sonarr', config_key: 'sonarr', instance_name: null, process_name: 'Sonarr', provider: 'sqlite',
      monitoring_enabled: false, mode: 'standard', pressure: 'disabled', score: 0,
      recommendation: 'Database Health Monitoring is disabled for this service.', databases: [],
    }] }
  } else if (profile === 'utility-library-protection') {
    replies['/api/process/media-protection/policy'] = { process_name: 'Plex Media Server', enabled: false,
      api_key_configured: false, api_key: '', stop_when_idle_on_outage: true, protected_mounts: ['/mnt/debrid/example'] }
    replies['/api/process/media-protection/status'] = { enabled: false, recovery_stabilization_seconds: 30,
      recovery_timeout_seconds: 180, monitor_interval_seconds: 5, active: [], recent: [] }
    replies['/api/process/media-protection/plex-library-settings'] = { process_name: 'Plex Media Server', settings: plexSettings,
      warnings: ['Public example settings; no Plex account or real library was contacted.'] }
  } else if (profile === 'utility-symlink-tools') {
    replies['/api/process/symlink-backup-manifests'] = { process_name: 'InfiniDysk', manifests: [] }
    replies['/api/process/symlink-manifest-files'] = { directory: '/config/symlink-repair/snapshots', count: 0, files: [] }
  } else if (profile === 'utility-rclone-optimizer') {
    serviceConfigs.rclone = { key_type: 'infinidysk', core_service: 'infinidysk', mount_path: '/mnt/debrid/example', enabled: true }
    replies['/api/process/rclone-optimizer/instances'] = { instances: [{ process_name: 'Rclone', key_type: 'infinidysk', mount_path: '/mnt/debrid/example' }] }
    replies['/api/process/rclone-optimizer/latest'] = { job: null }
    replies['/api/process/rclone-optimizer/content'] = { process_name: 'Rclone', mount_path: '/mnt/debrid/example',
      content_base: '/mnt/debrid/example/content', discovery_mode: 'active_arr_categories',
      active_categories: [], scanned: 0, truncated: false, automatic_selection: [], files: [],
      selection_note: 'Public example only; no media paths were enumerated and no provider data was read.' }
  } else if (profile === 'utility-infinidysk-v2-install') {
    serviceConfigs.infinidysk = { enabled: true, runtime_generation: '1', mount_backend: 'rclone', mount_path: '/mnt/debrid/example' }
    replies['/api/process/infinidysk-v2/status'] = { protocol: 1, job_type: 'infinidysk_v2_migration',
      runtime_generation: '1', mode: 'fresh', current: { mount_backend: 'rclone', mount_path: '/mnt/debrid/example',
        database_provider: 'sqlite', import_strategy: 'preserve' }, supported_mount_backends: ['rclone', 'fuse'],
      job: null, blocking_job_count: 0, capabilities: {}, preview_task: null,
      eligibility: { ready: false, blockers: ['Documentation example only: no existing data or installation eligibility has been inspected.'] } }
  } else if (profile === 'utility-namespace-migration') {
    replies['/api/process/infinidysk-migration/status'] = { eligible: true, enabled: true, notice_due: true,
      status: 'pending', selected_mode: null, cleanup_available: false, cleanup_finalized: false,
      rollback_artifacts_available: false, legacy: { repository: true, brand: true, service_key: true, paths: [], attached_services: [] },
      blockers: [], modes: [
        { id: 'retain_legacy_namespace', title: 'Switch to InfiniDysk and keep existing paths', recommended: true, available: true,
          description: 'Use the canonical identity and retain existing example mount paths.' },
        { id: 'full_namespace', title: 'Migrate the complete InfiniDysk namespace', recommended: false, available: true,
          description: 'Review the guarded full-namespace path; preflight has not run.' },
      ] }
    replies['/api/process/infinidysk-migration/job-status'] = { job: null }
  } else if (profile === 'utility-postgres-migration') {
    replies['/api/process/postgres-migration/preflight'] = { process_name: 'Sonarr', service_key: 'sonarr',
      instance_name: null, supported: true, ready: false, running: true, postgres_enabled: false, service_version: '4.0.0',
      sqlite: { main: { path: '/data/sonarr/sonarr.db', display_size: 'Not inspected in this example' } },
      postgres: { main_database: 'example_sonarr_main', log_database: 'example_sonarr_log' },
      checks: [{ id: 'source_inventory', status: 'failed', message: 'Documentation example: no live database, schema or target access has been verified.' }],
      failure_count: 1, warning_count: 0, confirmation_text: 'MIGRATE Sonarr', supports_log_migration: false,
      rehearsal_required: true, backup_root: '/config/arr-postgres-migration',
      migration_notice: 'Keep an independent backup. This review does not rehearse, import, validate or change any database.' }
    replies['/api/process/arr-postgres-migration/preflight'] = replies['/api/process/postgres-migration/preflight']
  } else return null
  return { serviceConfigs, replies }
}

export function utilityFixtureReply(profile, method, pathname) {
  if (method !== 'GET') return undefined
  const definition = utilityFixtureProfile(profile)
  return definition && Object.hasOwn(definition.replies, pathname) ? structuredClone(definition.replies[pathname]) : undefined
}
