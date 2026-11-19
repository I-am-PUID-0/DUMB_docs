#!/usr/bin/env node
// Render an immutable packaged Nuxt frontend against isolated example transports.
import fs from 'node:fs/promises'
import path from 'node:path'
import { createRequire } from 'node:module'
import { spawn } from 'node:child_process'
import { once } from 'node:events'
import http from 'node:http'
import { setTimeout as delay } from 'node:timers/promises'
import { createFixture, FIXED_TIME, EXAMPLE_SONARR_KEY } from './fixture.mjs'
import { readPlan, scenarioById, unavailableReason, sha256 } from './capture-catalog.mjs'
import { runScenario, settingsSectionId, CaptureBlocked } from './scenarios.mjs'
import { createMetricsTrace } from './metrics-trace.mjs'

const options = {}
for (let i = 2; i < process.argv.length; i += 2) {
  const key = process.argv[i]
  if (!['--plan', '--frontend-root', '--out', '--scenarios', '--themes', '--embedded-sonarr-origin'].includes(key)
    || !process.argv[i + 1] || Object.hasOwn(options, key.slice(2))) {
    throw new Error('Usage: capture.mjs --plan PLAN.json --frontend-root ISOLATED_FRONTEND --out EMPTY_DIRECTORY [--scenarios id,...] [--themes dark,light] [--embedded-sonarr-origin LOOPBACK_URL]')
  }
  options[key.slice(2)] = process.argv[i + 1]
}
if (!options.plan || !options['frontend-root'] || !options.out) throw new Error('Plan, isolated frontend root and output are required')
const { plan, planHash } = await readPlan(options.plan)
const selectedIds = options.scenarios ? options.scenarios.split(',') : plan.scenarios
const themes = options.themes ? options.themes.split(',') : plan.themes
if (!selectedIds.length || selectedIds.some(id => !plan.scenarios.includes(id))
  || !themes.length || themes.some(theme => !plan.themes.includes(theme))) throw new Error('Selections must be a nonempty subset of the reviewed plan')
let sonarrOrigin
if (options['embedded-sonarr-origin']) {
  const url = new URL(options['embedded-sonarr-origin'])
  if (url.protocol !== 'http:' || !['localhost', '127.0.0.1', '[::1]'].includes(url.hostname)
    || url.username || url.password || url.search || url.hash) throw new Error('The native Sonarr target must be a credential-free loopback HTTP URL')
  sonarrOrigin = url.href.replace(/\/$/, '')
}
const frontendRoot = await fs.realpath(options['frontend-root'])
const out = path.resolve(options.out)
if (out === frontendRoot || out.startsWith(frontendRoot + path.sep)) throw new Error('Capture output must be outside the frontend source directory')
await fs.mkdir(out, { recursive: true })
if ((await fs.readdir(out)).length) throw new Error('Use an empty capture output directory')
const sourcePackage = JSON.parse(await fs.readFile(path.join(frontendRoot, 'package.json'), 'utf8'))
const builtPackage = JSON.parse(await fs.readFile(path.join(frontendRoot, '.output/server/package.json'), 'utf8'))
if (sourcePackage.version !== plan.frontend.version || builtPackage.version !== plan.frontend.version) throw new Error('Source and compiled frontend versions must match the immutable plan')
const requireFrontend = createRequire(path.join(frontendRoot, 'package.json'))
const { chromium } = requireFrontend('playwright')
const { WebSocketServer, WebSocket } = requireFrontend('ws')
const viewport = { width: 1280, height: 800 }
const recordings = new WeakMap()
const pageDiagnostics = new WeakMap()
const pacing = { menuOpen: 2500, menuChoice: 1600, result: 2200, ordinary: 1400 }
const manifest = {
  schema_version: 2, channel: plan.channel, frontend: plan.frontend, backend: plan.backend,
  captured_at: new Date().toISOString(),
  plan_sha256: planHash, capture_plan_file_sha256: sha256(await fs.readFile(options.plan)),
  catalog_sha256: plan.catalog_sha256, dataset_sha256: plan.dataset_sha256, tooling_sha256: plan.tooling_sha256,
  capability_source_sha256: plan.capability_source_sha256, fixed_time: FIXED_TIME, viewport,
  themes: plan.themes, selected_scenarios: selectedIds,
  dataset: 'Public example API/WebSocket responses; system CPU/memory and task-owned process counters are sampled from the capture container.',
  scope: 'Actual packaged Nuxt application. Example service configuration is isolated; no production DUMB installation or provider account is contacted.',
  source_verification: 'Caller archives verified immutable commits; source and compiled package versions are checked by this runner.',
  native_apps: plan.native_apps || [], coverage: [], captures: [],
  errors: [], blocked_requests: [], unexpected_fixture_requests: [], config_requests: [], api_calls: [], websocket_paths: [],
  complete: false, coverage_complete: false,
}
let fixture, child, browser, metricsTrace, childOutput = ''
let stopping
async function cleanup() {
  if (stopping) return stopping
  stopping = (async () => {
    await browser?.close().catch(() => {})
    if (child && child.exitCode === null && child.signalCode === null) {
      child.kill('SIGTERM')
      const exited = await Promise.race([once(child, 'exit').then(() => true), delay(3000).then(() => false)])
      if (!exited) { child.kill('SIGKILL'); await once(child, 'exit') }
    }
    await fixture?.close()
    await metricsTrace?.close()
  })()
  return stopping
}
for (const signal of ['SIGINT', 'SIGTERM']) process.once(signal, () => {
  void cleanup().finally(() => process.exit(signal === 'SIGINT' ? 130 : 143))
})

async function freePort() {
  const server = http.createServer()
  server.listen(0, '127.0.0.1')
  await once(server, 'listening')
  const port = server.address().port
  await new Promise(resolve => server.close(resolve))
  return port
}

async function contextFor(origin, video = false, theme = 'dark', authenticated = false) {
  const context = await browser.newContext({
    viewport, deviceScaleFactor: 1, timezoneId: 'UTC', locale: 'en-US',
    colorScheme: theme, reducedMotion: 'reduce', serviceWorkers: 'block',
    ...(video ? { recordVideo: { dir: path.join(out, 'raw'), size: viewport } } : {}),
  })
  await context.addInitScript(({ fixed, recording, theme, authenticated }) => {
    const NativeDate = Date
    const epoch = NativeDate.parse(fixed)
    const anchoredAt = performance.now()
    class ExampleDate extends NativeDate {
      constructor(...values) { super(...(values.length ? values : [Math.floor(epoch + performance.now() - anchoredAt)])) }
      static now() { return Math.floor(epoch + performance.now() - anchoredAt) }
    }
    globalThis.Date = ExampleDate
    try { localStorage.setItem('dmbdb.appearance.theme', theme); if (authenticated) localStorage.setItem('dumb_access_token', 'example-capture-token') } catch { /* Initial blank documents have no storage origin. */ }
    if (recording) {
      const mount = () => {
        const pointer = document.createElement('div')
        pointer.setAttribute('aria-hidden', 'true')
        pointer.style.cssText = 'position:fixed;left:0;top:0;width:28px;height:32px;pointer-events:none;z-index:2147483647;display:none;filter:drop-shadow(0 1px 2px #0009)'
        pointer.innerHTML = '<svg viewBox="0 0 28 32" width="28" height="32"><path d="M3 2v23l6-5 6 9 5-3-6-9 9-1Z" fill="white" stroke="#142c3f" stroke-width="2" stroke-linejoin="round"/></svg>'
        const highlight = document.createElement('div')
        highlight.setAttribute('aria-hidden', 'true')
        highlight.style.cssText = 'position:fixed;pointer-events:none;z-index:2147483645;border:3px solid #ffd95a;border-radius:7px;box-shadow:0 0 0 2px #142c3f99;display:none;box-sizing:border-box'
        document.body.append(highlight, pointer)
        document.addEventListener('mousemove', event => {
          pointer.style.left = event.clientX - 3 + 'px'
          pointer.style.top = event.clientY - 2 + 'px'
          pointer.style.display = 'block'
        })
        document.addEventListener('mousedown', event => {
          const pulse = document.createElement('div')
          pulse.setAttribute('aria-hidden', 'true')
          pulse.style.cssText = `position:fixed;left:${event.clientX - 12}px;top:${event.clientY - 12}px;width:24px;height:24px;border:4px solid #ffd95a;border-radius:50%;pointer-events:none;z-index:2147483646;box-sizing:border-box`
          document.body.append(pulse)
          pulse.animate([{ transform: 'scale(.5)', opacity: 1 }, { transform: 'scale(2.1)', opacity: 0 }], { duration: 650 }).finished.finally(() => pulse.remove())
        }, true)
        globalThis.__docsCaptureHighlight = box => {
          if (!box) { highlight.style.display = 'none'; return }
          Object.assign(highlight.style, { display: 'block', left: box.x - 4 + 'px', top: box.y - 4 + 'px', width: box.width + 8 + 'px', height: box.height + 8 + 'px' })
        }
        globalThis.__docsCapturePointerHidden = hidden => {
          pointer.style.visibility = hidden ? 'hidden' : 'visible'
          highlight.style.visibility = hidden ? 'hidden' : 'visible'
        }
      }
      if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount, { once: true })
      else mount()
    }
  }, { fixed: FIXED_TIME, recording: video, theme, authenticated })
  const contributorUrls = new Set([
    'https://api.github.com/repos/I-am-PUID-0/DUMB/contributors',
    'https://api.github.com/repos/nicocapalbo/dmbdb/contributors',
  ])
  // Keep the real Contributors section populated without fetching identities
  // or avatar images from GitHub. An empty list gives its content zero height.
  const exampleContributors = [{
    id: 100000001,
    login: 'example-contributor',
    html_url: 'https://example.com/contributors/example-contributor',
    avatar_url: new URL('/images/dumb-logo.png', origin).href,
  }]
  await context.route('**/*', route => {
    const url = route.request().url()
    if (new URL(url).origin === origin) return route.continue()
    if (contributorUrls.has(url)) return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(exampleContributors) })
    manifest.blocked_requests.push({ transport: 'HTTP', url: new URL(url).origin })
    return route.abort()
  })
  if (typeof context.routeWebSocket !== 'function') throw new Error('This capture requires Playwright WebSocket routing support')
  await context.routeWebSocket(/.*/, socket => {
    const url = new URL(socket.url())
    if (url.host === new URL(origin).host && (['/ws/logs', '/ws/status', '/ws/metrics'].includes(url.pathname)
      || sonarrOrigin && /^\/(?:ui\/sonarr|sonarr|signalr)(?:\/|$)/.test(url.pathname))) {
      socket.connectToServer()
    } else {
      manifest.blocked_requests.push({ transport: 'WS', url: url.origin })
      socket.close({ code: 1008, reason: 'Only the example fixture is allowed' })
    }
  })
  return context
}

async function openPage(context, origin, route) {
  const page = await context.newPage()
  const requests = []
  pageDiagnostics.set(page, requests)
  page.on('pageerror', error => manifest.errors.push({ scenario: route, message: error.message }))
  page.on('response', response => {
    const url = new URL(response.url())
    if (url.origin === origin) {
      requests.push({ pathname: url.pathname, status: response.status() })
      if (requests.length > 100) requests.shift()
    }
    if (url.origin === origin && response.status() >= 400 && !fixture?.expectedFailure(url.pathname, response.status())) {
      manifest.errors.push({ pathname: url.pathname, status: response.status() })
    }
  })
  page.on('dialog', dialog => { manifest.errors.push({ scenario: route, message: 'Unexpected dialog: ' + dialog.type() }); void dialog.dismiss() })
  const response = await page.goto(origin + route, { waitUntil: 'networkidle' })
  if (!response?.ok()) throw new Error('Example frontend navigation failed: ' + route)
  await page.locator('body').waitFor()
  await page.evaluate(() => document.fonts.ready)
  await delay(500)
  return page
}

async function serviceReady(page) {
  await page.getByRole('button', { name: /\bRestart(?:\s+.+)?$/i }).first().waitFor()
  await page.getByText('DUMB Config', { exact: true }).first().waitFor()
}
async function logsTab(page) {
  await page.getByText('Service Logs', { exact: true }).first().click()
  await page.getByPlaceholder('Enter text to filter logs', { exact: true }).waitFor()
  await page.getByText('Example Series S01E01 imported successfully', { exact: false }).first().waitFor()
}
function chapter(page, label) {
  const recording = recordings.get(page)
  if (recording) recording.chapters.push({ label, at_seconds: Math.round((performance.now() - recording.started) / 100) / 10 })
}
async function focusControl(page, locator, hold = pacing.ordinary) {
  await locator.scrollIntoViewIfNeeded()
  const box = await locator.boundingBox()
  if (box) {
    await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2, { steps: 18 })
    await page.evaluate(box => globalThis.__docsCaptureHighlight?.(box), box)
  }
  await delay(recordings.has(page) ? hold : 100)
}
async function hoverClick(page, locator, { before = pacing.ordinary, after = pacing.result } = {}) {
  await focusControl(page, locator, before)
  await locator.click()
  await page.evaluate(() => globalThis.__docsCaptureHighlight?.(null))
  await delay(recordings.has(page) ? after : 150)
}
async function serviceTool(page, label) {
  const tools = page.getByRole('button', { name: 'Service tools', exact: true })
  chapter(page, 'Open Service tools')
  await hoverClick(page, tools, { after: pacing.menuOpen })
  const item = page.getByRole('menuitem').filter({ hasText: label }).first()
  const choice = await item.count() ? item : page.getByText(label, { exact: true }).last()
  chapter(page, 'Choose ' + label)
  await hoverClick(page, choice, { before: pacing.menuChoice })
}
async function updatesPanel(page) {
  await serviceTool(page, 'Updates')
  await page.getByRole('button', { name: /Check for updates\b/i }).waitFor()
}
async function settingsSection(page, label, id) {
  const toggle = page.getByRole('button', { name: new RegExp('^' + label + '\\b') }).first()
  await toggle.waitFor()
  if (await toggle.getAttribute('aria-expanded') === 'false') await hoverClick(page, toggle)
  const section = page.locator('#settings-section-' + id)
  await section.waitFor()
  // Showing only the already-visible toggle can leave most of the form below
  // the viewport. Use the application's native scroll container and retain its
  // real section heading at the top of the capture.
  await toggle.evaluate(element => element.scrollIntoView({ block: 'start', inline: 'nearest' }))
  return section
}
async function dependencyPanel(page, flow = false) {
  await serviceTool(page, 'Dependencies')
  await page.getByText('Startup order:', { exact: true }).waitFor()
  if (flow) {
    chapter(page, 'Read the dependency flow')
    await hoverClick(page, page.getByRole('button', { name: 'Flow', exact: true }))
    const panel = page.getByTitle('Close Dependency graph panel.', { exact: true }).locator('..')
    await panel.locator('svg').first().waitFor()
  }
}
async function autoRestartPanel(page) {
  await serviceTool(page, 'Auto-restart')
  await page.getByRole('heading', { name: 'Auto-restart Settings', exact: true }).waitFor()
}
async function screenshot(page, file, scenario, steps, theme = 'dark') {
  await page.evaluate(() => globalThis.__docsCapturePointerHidden?.(true))
  await page.screenshot({ path: path.join(out, file), animations: 'disabled' })
  await page.evaluate(() => globalThis.__docsCapturePointerHidden?.(false))
  manifest.captures.push({ kind: 'image', file, scenario, steps, viewport, theme, route: new URL(page.url()).pathname })
}

const ui = { chapter, focusControl, hoverClick, serviceTool, serviceReady, settingsSection }
const exists = async relative => fs.stat(path.join(frontendRoot, relative)).then(info => info.isFile()).catch(() => false)
const settingsSource = await fs.readFile(path.join(frontendRoot, 'pages/settings.vue'), 'utf8')
async function sourceUnavailable(scenario) {
  for (const filename of scenario.required_frontend_files || []) {
    if (!await exists(filename)) return 'The immutable frontend source has no file: ' + filename
  }
  const sectionId = scenario.settings_section || settingsSectionId(scenario.id)
  if (sectionId) {
    const text = scenario.settings_source && scenario.settings_source !== 'pages/settings.vue'
      ? await fs.readFile(path.join(frontendRoot, scenario.settings_source), 'utf8').catch(() => '') : settingsSource
    if (!text.includes('section-id="' + sectionId + '"')) return 'The immutable frontend source has no Settings section: ' + sectionId
  }
  return null
}
async function captureScenario(origin, scenario, theme, row) {
  fixture.resetScenario(scenario.profile)
  const recording = scenario.kinds.includes('video')
  const authenticated = ['settings-authentication', 'settings-auth-provider'].includes(scenario.id)
  const context = await contextFor(origin, recording, theme, authenticated)
  let page
  try {
    const started = performance.now()
    page = await openPage(context, origin, scenario.route)
    const chapters = { started, chapters: [] }
    if (recording) recordings.set(page, chapters)
    await runScenario({ page, scenario, theme, plan, ui, fixture, prerequisites: { sonarr: Boolean(sonarrOrigin) } })
    await page.evaluate(() => globalThis.__docsCaptureHighlight?.(null))
    await delay(recording ? pacing.result : 500)
    const basename = theme + '/' + scenario.id
    const actions = [scenario.description, ...chapters.chapters.map(chapter => chapter.label)]
    await screenshot(page, basename + '.png', scenario.id, actions, theme)
    row.artifacts.push(basename + '.png')
    if (recording) {
      await delay(pacing.result)
      const route = new URL(page.url()).pathname
      const video = page.video()
      await context.close()
      const file = basename + '.webm'
      await video.saveAs(path.join(out, file))
      manifest.captures.push({ file, kind: 'video', scenario: scenario.id, theme, viewport,
        route, start_route: scenario.route.split('#')[0], poster: basename + '.png', actions,
        chapters: chapters.chapters, pointer_emphasis: true,
        pacing: { tools_menu_ms: pacing.menuOpen, menu_choice_ms: pacing.menuChoice, result_ms: pacing.result } })
      row.artifacts.push(file)
      await video.delete()
    }
    row.status = 'captured'
  } catch (error) {
    row.status = 'blocked'
    row.reason = error.message
    console.error(JSON.stringify({ scenario: scenario.id, theme, status: 'blocked', reason: error.message }))
    if (page && !page.isClosed()) {
      const directory = path.join(out, 'diagnostics')
      await fs.mkdir(directory, { recursive: true })
      const diagnostic = { scenario: scenario.id, theme, final_url: page.url(),
        body_excerpt: await page.locator('body').innerText({ timeout: 3000 }).then(text => text.slice(0, 16000)).catch(() => ''),
        frames: await Promise.all(page.frames().filter(frame => frame !== page.mainFrame()).map(async frame => ({
          pathname: new URL(frame.url(), page.url()).pathname,
          body_excerpt: await frame.locator('body').innerText({ timeout: 1500 }).then(text => text.slice(0, 6000)).catch(() => ''),
        }))),
        requests: pageDiagnostics.get(page),
        reason: error.message, local_only: true }
      await fs.writeFile(path.join(directory, theme + '-' + scenario.id + '.json'), JSON.stringify(diagnostic, null, 2) + '\n')
      await page.screenshot({ path: path.join(directory, theme + '-' + scenario.id + '.png'), animations: 'disabled', timeout: 3000 }).catch(() => {})
    }
    if (!(error instanceof CaptureBlocked)) manifest.errors.push({ scenario: scenario.id, theme, message: error.message })
  } finally { await context.close().catch(() => {}) }
}
try {
  if (sonarrOrigin) {
    const response = await fetch(sonarrOrigin + '/api/v3/system/status', { headers: { 'X-Api-Key': EXAMPLE_SONARR_KEY } })
    if (!response.ok) throw new Error('The isolated Sonarr status could not be verified')
    const observed = await response.json()
    const expected = Array.isArray(plan.native_apps) ? plan.native_apps.find(app => app.id === 'sonarr') : plan.native_apps?.sonarr
    if (!expected?.version || observed.version !== expected.version || observed.appName !== 'Sonarr') throw new Error('The actual isolated Sonarr version differs from the immutable capture plan')
    manifest.native_app_observations = { sonarr: { application: 'Sonarr', version: observed.version, image: expected.image, verified: true,
      version_verification: 'Observed from the isolated application API.', image_verification: 'Pinned image attested by the demo-service launcher and capture plan.' } }
  }
  metricsTrace = await createMetricsTrace()
  metricsTrace.watchProcess(process.pid, 'Documentation capture fixture')
  fixture = await createFixture({ WebSocketServer, WebSocket, plan, metricsTrace, sonarrOrigin })
  const port = await freePort()
  const origin = 'http://127.0.0.1:' + port
  child = spawn(process.execPath, [path.join(frontendRoot, '.output/server/index.mjs')], {
    cwd: frontendRoot,
    env: { PATH: process.env.PATH, NODE_ENV: 'production', NITRO_HOST: '127.0.0.1', NITRO_PORT: String(port),
      DMB_API_URL: fixture.origin, DUMB_API_URL: fixture.origin,
      DMB_TRAEFIK_URL: fixture.origin, DUMB_TRAEFIK_URL: fixture.origin },
    stdio: ['ignore', 'pipe', 'pipe'],
  })
  metricsTrace.watchProcess(child.pid, 'DUMB Frontend')
  for (const stream of [child.stdout, child.stderr]) stream.on('data', chunk => { childOutput = (childOutput + chunk).slice(-5000) })
  let ready = false
  for (let attempt = 0; attempt < 150; attempt++) {
    if (child.exitCode !== null) throw new Error('The isolated frontend exited before becoming ready')
    try { if ((await fetch(origin + '/api/health')).ok) { ready = true; break } } catch {}
    await delay(100)
  }
  if (!ready) throw new Error('The isolated frontend did not become ready')
  browser = await chromium.launch({ headless: true })
  for (const theme of plan.themes) {
    await fs.mkdir(path.join(out, theme), { recursive: true })
    for (const id of plan.scenarios) {
      const scenario = scenarioById.get(id)
      const row = { id, theme, status: 'skipped', required: plan.required_scenarios.includes(id), features: scenario.features, artifacts: [] }
      manifest.coverage.push(row)
      const unresolved = (scenario.required_capabilities || []).filter(key => plan.unresolved_capabilities?.includes(key))
      if (unresolved.length) { row.status = 'blocked'; row.reason = 'Backend capability source could not be resolved: ' + unresolved.join(', '); continue }
      const unavailable = unavailableReason(scenario, plan) || await sourceUnavailable(scenario)
      if (unavailable) { row.availability = 'unavailable'; row.reason = unavailable; continue }
      if (!themes.includes(theme) || !selectedIds.includes(id)) { row.reason = 'Not selected in this iteration'; continue }
      if ((scenario.required_prerequisites || []).includes('sonarr') && !sonarrOrigin) {
        row.status = 'blocked'; row.reason = 'Actual isolated Sonarr prerequisite is missing; no substitute screen was used'; continue
      }
      await captureScenario(origin, scenario, theme, row)
      console.log(JSON.stringify({ scenario: id, theme, status: row.status, artifacts: row.artifacts }))
    }
  }
  const satisfied = row => row.status === 'captured' || row.availability === 'unavailable'
  manifest.coverage_complete = manifest.coverage.filter(row => row.required).every(satisfied)
  manifest.complete = manifest.coverage.filter(row => row.required && themes.includes(row.theme) && selectedIds.includes(row.id)).every(satisfied)
} catch (error) {
  manifest.errors.push({ scenario: 'runner', message: error.message })
  process.exitCode = 1
} finally {
  try { await cleanup() } catch (error) { manifest.errors.push({ scenario: 'cleanup', message: error.message }); process.exitCode = 1 }
  manifest.api_calls = fixture?.state.calls || []
  manifest.config_requests = fixture?.state.configRequests || []
  manifest.websocket_paths = [...new Set(fixture?.state.websocketPaths || [])]
  manifest.unexpected_fixture_requests = fixture?.state.unexpected || []
  manifest.measurements = metricsTrace?.metadata()
  manifest.simulated_operations = fixture?.state.exampleOperations || []
  manifest.expected_example_failures = fixture?.state.expectedFailures || []
  for (const capture of manifest.captures) {
    const bytes = await fs.readFile(path.join(out, capture.file))
    capture.bytes = bytes.length
    capture.sha256 = sha256(bytes)
  }
  const transportClean = !manifest.errors.length && !manifest.unexpected_fixture_requests.length && !manifest.blocked_requests.length
  manifest.complete = manifest.complete && transportClean
  manifest.coverage_complete = manifest.coverage_complete && transportClean
  if (!manifest.complete) process.exitCode = 1
  await fs.writeFile(path.join(out, 'manifest.json'), JSON.stringify(manifest, null, 2) + '\n')
  console.log(JSON.stringify({ complete: manifest.complete, coverage_complete: manifest.coverage_complete,
    channel: plan.channel, captured: manifest.coverage.filter(row => row.status === 'captured').length,
    skipped: manifest.coverage.filter(row => row.status === 'skipped').length,
    blocked: manifest.coverage.filter(row => row.status === 'blocked').length }))
}
