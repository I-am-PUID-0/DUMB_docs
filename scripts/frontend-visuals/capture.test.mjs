import assert from 'node:assert/strict'
import { EventEmitter } from 'node:events'
import http from 'node:http'
import { once } from 'node:events'
import { test } from 'node:test'
import { canonicalPlanHash, catalogHash, datasetHash, validatePlan, unavailableReason } from './capture-catalog.mjs'
import { createFixture } from './fixture.mjs'
import { utilityScenarios } from './utility-scenarios.mjs'

const identity = version => ({ repository: 'https://github.com/example/project', ref: 'dev', version, commit: 'a'.repeat(40) })
const planFor = changes => {
  const plan = { schema_version: 1, channel: 'dev', frontend: identity('1.92.0'), backend: identity('2.24.0'),
    scenarios: ['dashboard'], required_scenarios: ['dashboard'], themes: ['dark', 'light'], capabilities: {},
    catalog_sha256: catalogHash, dataset_sha256: datasetHash, tooling_sha256: 'b'.repeat(64), capability_source_sha256: 'c'.repeat(64), ...changes }
  plan.plan_sha256 = canonicalPlanHash(plan)
  return plan
}
class NoWebSockets extends EventEmitter {
  clients = new Set()
  close(callback) { callback() }
}
const open = async (t, extra = {}) => {
  const fixture = await createFixture({ WebSocketServer: NoWebSockets, plan: planFor(), ...extra })
  t.after(() => fixture.close())
  return fixture
}
const post = (fixture, pathname, body) => fetch(fixture.origin + pathname, {
  method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body),
})

test('shared service polls stay read-only and valid across specialist panels', async t => {
  const fixture = await open(t)
  for (const profile of ['standard', ...utilityScenarios.map(row => row.profile)]) {
    fixture.resetScenario(profile)
    for (const pathname of ['/api/process/rclone-optimizer/instances', '/api/process/symlink-backup-manifests', '/api/process/runtime-log-level']) {
      const response = await fetch(fixture.origin + pathname)
      assert.equal(response.status, 200, profile + ': ' + pathname)
      assert.equal(typeof await response.json(), 'object')
    }
  }
  assert.deepEqual(fixture.state.unexpected, [])
  assert.deepEqual(fixture.state.exampleOperations, [])
})

test('canonical plan identity ignores key order but detects changed source and configuration', () => {
  const first = planFor({ capabilities: { z: false, a: { second: 2, first: 1 } } })
  const reordered = { ...first, capabilities: { a: { first: 1, second: 2 }, z: false } }
  assert.equal(canonicalPlanHash(first), canonicalPlanHash(reordered))
  assert.equal(validatePlan(reordered), reordered)
  assert.throws(() => validatePlan({ ...first, backend: { ...first.backend, commit: 'd'.repeat(40) } }), /canonical SHA-256/)
})

test('source labels cannot present a development archive as a release', () => {
  assert.throws(() => validatePlan(planFor({ frontend: { ...identity('1.92.0'), tag: 'v1.92.0' } })), /Development source/)
  assert.throws(() => validatePlan(planFor({ channel: 'release' })), /exact version tag/)
  const release = planFor({ channel: 'release', frontend: { ...identity('1.91.0'), ref: 'v1.91.0', tag: 'v1.91.0' },
    backend: { ...identity('2.23.0'), ref: '2.23.0', tag: '2.23.0' } })
  assert.equal(validatePlan(release), release)
})

test('plans reject stale datasets and invalid selections before starting applications', () => {
  assert.throws(() => validatePlan(planFor({ dataset_sha256: '0'.repeat(64) })), /hashes differ/)
  assert.throws(() => validatePlan(planFor({ scenarios: ['imaginary-screen'] })), /Invalid scenario/)
  assert.throws(() => validatePlan(planFor({ themes: ['dark', 'dark'] })), /Plan themes/)
  assert.match(unavailableReason({ id: 'ai-overview', required_capabilities: ['ai_diagnostics'] }, planFor()), /ai_diagnostics/)
})

test('versioned UI requires exact verified protocol support; unknown source gates fail closed', () => {
  const scenario = { id: 'a-future-versioned-panel', required_capabilities: ['example_feature'], required_protocols: { example_protocol: 2 } }
  assert.equal(unavailableReason(scenario, planFor({ capabilities: { example_feature: true, example_protocol: 2 } })), null)
  for (const capabilities of [{ example_feature: true }, { example_feature: true, example_protocol: 1 }]) {
    assert.match(unavailableReason(scenario, planFor({ capabilities })), /example_protocol=2/)
  }
  const unresolved = planFor({ scenarios: ['infinidysk-v2-install'], required_scenarios: ['infinidysk-v2-install'],
    unresolved_capabilities: ['infinidysk_v2_migration_protocol'], capabilities: { infinidysk_v2: true, infinidysk_v2_migration: true } })
  assert.throws(() => validatePlan(unresolved), /could not be resolved from source/)
})

test('fixture rejects operational service writes and malformed requests without recording values', async t => {
  const fixture = await open(t)
  const denied = await post(fixture, '/api/process/start-service', { process_name: 'Sonarr' })
  assert.equal(denied.status, 405)
  await denied.arrayBuffer()
  const malformed = await fetch(fixture.origin + '/api/config/?example=do-not-record-query', { method: 'POST', body: '{example-invalid-private-value' })
  assert.equal(malformed.status, 400)
  await malformed.arrayBuffer()
  assert.deepEqual(fixture.state.unexpected, [
    { method: 'POST', path: '/api/process/start-service' }, { method: 'POST', path: '/api/config/' },
  ])
  assert.doesNotMatch(JSON.stringify(fixture.state), /do-not-record-query|example-invalid-private-value/)
})

test('a completed update check supplies the timestamps consumed by the real frontend', async t => {
  const fixture = await open(t)
  const response = await post(fixture, '/api/process/update-check', { process_name: 'Sonarr' })
  assert.equal(response.status, 200)
  const checked = await response.json()
  assert.equal(checked.status, 'update_available')
  assert.equal(typeof checked.checked_at, 'number')
  assert.equal(checked.next_check_at, null)
  const status = await fetch(fixture.origin + '/api/process/update-status?process_name=Sonarr').then(value => value.json())
  assert.equal(status.update_status.checked_at, checked.checked_at)
  assert.deepEqual(fixture.state.exampleOperations, [])
})

test('retained walkthrough rechecks stay scoped to the known unverified example action', async t => {
  const fixture = await open(t)
  const path = '/api/process/setup/runs/example-run/actions/review-provider'
  const body = { operation: 'recheck', values: {} }
  assert.equal((await post(fixture, path, body)).status, 405)
  fixture.resetScenario('setup-connections')
  const response = await post(fixture, path, body)
  assert.equal(response.status, 200)
  const run = await response.json()
  assert.equal(run.status, 'waiting_input')
  assert.equal(run.actions[0].verification, 'unchecked')
  for (const operation of ['apply', 'confirm', 'retry']) {
    assert.equal((await post(fixture, path, { ...body, operation })).status, 405)
  }
  assert.equal((await post(fixture, path.replace('review-provider', 'unknown-action'), body)).status, 405)
  assert.equal((await post(fixture, path, { operation: 'recheck', values: { api_key: 'not-accepted-example' } })).status, 405)
  assert.equal(fixture.state.exampleOperations.length, 1)
})

test('only harmless UI preferences may be saved in the isolated configuration', async t => {
  const fixture = await open(t)
  const accepted = await post(fixture, '/api/config/', { updates: { dumb: { ui: { sidebar: { show_all_services: true } } } } })
  assert.equal(accepted.status, 200)
  await accepted.arrayBuffer()
  const config = await fetch(fixture.origin + '/api/config/').then(response => response.json())
  assert.equal(config.dumb.ui.sidebar.show_all_services, true)
  const denied = await post(fixture, '/api/config/', { updates: { sonarr: { enabled: false } }, persist: true })
  assert.equal(denied.status, 405)
  await denied.arrayBuffer()
  assert.equal(fixture.state.configRequests[0].accepted, 'example_ui_preferences')
})

test('empty setup lookup uses the exact backend absence contract and creates no run', async t => {
  const fixture = await open(t)
  const response = await fetch(fixture.origin + '/api/process/setup/runs/latest')
  assert.equal(response.status, 404)
  assert.deepEqual(await response.json(), { detail: 'No setup run has been created.' })
  assert.equal(fixture.expectedFailure('/api/process/setup/runs/latest', 404), true)
  assert.deepEqual(fixture.state.exampleOperations, [])
  assert.deepEqual(fixture.state.unexpected, [])
})

test('simulated setup start is restricted to terminal example scenarios and produces no real operation', async t => {
  const fixture = await open(t)
  const payload = { plan_id: 'example-plan', idempotency_key: 'example-idempotency' }
  const denied = await post(fixture, '/api/process/setup/runs', payload)
  assert.equal(denied.status, 405)
  await denied.arrayBuffer()
  fixture.resetScenario('onboarding-result')
  const accepted = await post(fixture, '/api/process/setup/runs', payload)
  assert.equal(accepted.status, 200)
  const run = await accepted.json()
  assert.equal(run.status, 'waiting_input')
  assert.match(run.message, /Simulated documentation setup example/)
  assert.deepEqual(fixture.state.exampleOperations.map(row => row.operation), ['in_memory_simulated_setup_run'])
})

test('legacy terminal simulation accepts only the released empty optional-options shape', async t => {
  const fixture = await open(t)
  fixture.resetScenario('onboarding-result')
  const payload = { core_services: [{ name: 'riven_backend' }], optional_services: [], optional_service_options: {} }
  const accepted = await post(fixture, '/api/process/start-core-service', payload)
  assert.equal(accepted.status, 200)
  await accepted.arrayBuffer()
  assert.equal(fixture.state.exampleOperations[0].operation, 'in_memory_simulated_legacy_setup')
  const denied = await post(fixture, '/api/process/start-core-service', { ...payload, optional_service_options: { unrelated_service: { enabled: true } } })
  assert.equal(denied.status, 405)
  await denied.arrayBuffer()
})

test('Metrics preserves irregular sampled counters and reports only measured task process rows', async t => {
  const points = [4.1, 16.8, 3.7, 9.2].map((cpu, index) => ({ elapsed_ms: index * 500,
    cpu_percent: cpu, memory_percent: 31.2 + index / 10, memory_total: 1024, memory_used: 320 + index,
    processes: [{ name: 'DUMB Frontend', process_name: 'DUMB Frontend', pid: 1001, rss: 120000, cpu_percent: cpu / 2 }],
  }))
  const fixture = await open(t, { metricsTrace: { points, latest: points.at(-1) } })
  const history = await fetch(fixture.origin + '/api/metrics/history_series').then(response => response.json())
  assert.deepEqual(history.items.map(point => point.system.cpu_percent), [4.1, 16.8, 3.7, 9.2])
  assert.equal(history.items.at(-1).dumb_managed[0].name, 'DUMB Frontend')
  assert.equal(history.items.at(-1).dumb_managed.length, 1)
  const snapshot = await fetch(fixture.origin + '/api/metrics').then(response => response.json())
  assert.equal(snapshot.system.cpu_percent, 9.2)
  assert.equal(snapshot.system.mem.percent, 31.5)
})

test('native proxy removes a repeated Sonarr UrlBase and refuses application writes', async t => {
  const upstream = http.createServer((request, response) => {
    response.setHeader('content-type', 'application/json')
    response.end(JSON.stringify({ pathname: request.url, key: request.headers['x-api-key'] }))
  })
  upstream.listen(0, '127.0.0.1')
  await once(upstream, 'listening')
  t.after(() => new Promise(resolve => { upstream.close(resolve); upstream.closeAllConnections() }))
  const fixture = await open(t, { sonarrOrigin: 'http://127.0.0.1:' + upstream.address().port + '/sonarr' })
  const response = await fetch(fixture.origin + '/service/ui/sonarr/sonarr/Content/styles.css', { headers: { 'X-Api-Key': 'not-forwarded-example' } })
  assert.deepEqual(await response.json(), { pathname: '/sonarr/Content/styles.css', key: '0123456789abcdef0123456789abcdef' })
  const denied = await post(fixture, '/service/ui/sonarr/api/v3/series', { title: 'Example Series' })
  assert.equal(denied.status, 405)
  await denied.arrayBuffer()
  assert.deepEqual(fixture.state.unexpected, [{ method: 'POST', path: '/service/ui/sonarr/api/v3/series' }])
})
