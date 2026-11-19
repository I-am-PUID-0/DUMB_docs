#!/usr/bin/env node
// Run from the frontend devcontainer, using an isolated tagged frontend build:
// node capture.mjs --frontend-root /tmp/example/frontend --out /tmp/example/captures
import fs from 'node:fs/promises'
import path from 'node:path'
import { createRequire } from 'node:module'
import { spawn } from 'node:child_process'
import { once } from 'node:events'
import http from 'node:http'
import { setTimeout as delay } from 'node:timers/promises'
import { createFixture, FIXED_TIME, FRONTEND } from './fixture.mjs'

const options = {}
for (let i = 2; i < process.argv.length; i += 2) {
  const key = process.argv[i]
  if (!['--frontend-root', '--out'].includes(key) || !process.argv[i + 1]) {
    throw new Error('Usage: capture.mjs --frontend-root ISOLATED_FRONTEND --out NEW_OUTPUT_DIRECTORY')
  }
  options[key.slice(2)] = process.argv[i + 1]
}
if (!options['frontend-root'] || !options.out) throw new Error('Both --frontend-root and --out are required')
const frontendRoot = await fs.realpath(options['frontend-root'])
const out = path.resolve(options.out)
if (out === frontendRoot || out.startsWith(frontendRoot + path.sep)) throw new Error('Capture output must be outside the frontend source directory')
await fs.mkdir(out, { recursive: true })
if ((await fs.readdir(out)).length) throw new Error('Use an empty capture output directory; existing files will not be overwritten')
const sourcePackage = JSON.parse(await fs.readFile(path.join(frontendRoot, 'package.json'), 'utf8'))
const builtPackage = JSON.parse(await fs.readFile(path.join(frontendRoot, '.output/server/package.json'), 'utf8'))
if (sourcePackage.version !== FRONTEND.version || builtPackage.version !== FRONTEND.version) {
  throw new Error(`Source and packaged frontend must both be ${FRONTEND.tag}`)
}
// Dependencies come from this archive's frozen install, never the active checkout.
const requireFrontend = createRequire(path.join(frontendRoot, 'package.json'))
const { chromium } = requireFrontend('playwright')
const { WebSocketServer } = requireFrontend('ws')
const viewport = { width: 1280, height: 800 }
const recordings = new WeakMap()
const pacing = { menuOpen: 2500, menuChoice: 1600, result: 2200, ordinary: 1400 }
const manifest = {
  schema_version: 1, frontend: FRONTEND, fixed_time: FIXED_TIME, viewport,
  dataset: 'Reserved example data supplied by an isolated in-memory API and WebSocket fixture.',
  scope: 'Actual packaged frontend; example responses, no live DUMB services or installations.',
  source_verification: 'The caller must verify and archive the pinned tag SHA before building. Package and compiled output versions are checked by this runner.',
  captures: [], errors: [], blocked_requests: [], unexpected_fixture_requests: [],
  config_requests: [], api_calls: [], websocket_paths: [], complete: false,
}
let fixture, child, browser, childOutput = ''
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

async function contextFor(origin, video = false) {
  const context = await browser.newContext({
    viewport, deviceScaleFactor: 1, timezoneId: 'UTC', locale: 'en-US',
    colorScheme: 'dark', reducedMotion: 'reduce', serviceWorkers: 'block',
    ...(video ? { recordVideo: { dir: path.join(out, 'raw'), size: viewport } } : {}),
  })
  await context.addInitScript(({ fixed, recording }) => {
    const NativeDate = Date
    const epoch = NativeDate.parse(fixed)
    class ExampleDate extends NativeDate {
      constructor(...values) { super(...(values.length ? values : [epoch])) }
      static now() { return epoch }
    }
    globalThis.Date = ExampleDate
    try { localStorage.setItem('dmbdb.appearance.theme', 'dark') } catch { /* Initial blank documents have no storage origin. */ }
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
  }, { fixed: FIXED_TIME, recording: video })
  const contributorUrls = new Set([
    'https://api.github.com/repos/I-am-PUID-0/DUMB/contributors',
    'https://api.github.com/repos/nicocapalbo/dmbdb/contributors',
  ])
  await context.route('**/*', route => {
    const url = route.request().url()
    if (new URL(url).origin === origin) return route.continue()
    if (contributorUrls.has(url)) return route.fulfill({ status: 200, contentType: 'application/json', body: '[]' })
    manifest.blocked_requests.push({ transport: 'HTTP', url: new URL(url).origin })
    return route.abort()
  })
  if (typeof context.routeWebSocket !== 'function') throw new Error('This capture requires Playwright WebSocket routing support')
  await context.routeWebSocket(/.*/, socket => {
    const url = new URL(socket.url())
    if (url.host === new URL(origin).host && ['/ws/logs', '/ws/status', '/ws/metrics'].includes(url.pathname)) {
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
  page.on('pageerror', error => manifest.errors.push({ scenario: route, message: error.message }))
  page.on('response', response => {
    const url = new URL(response.url())
    if (url.origin === origin && response.status() >= 400) {
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
  await page.getByRole('button', { name: /\bRestart(?:\s+Sonarr)?$/i }).first().waitFor()
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
  await toggle.scrollIntoViewIfNeeded()
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
async function record(origin, { id, route = '/services/Sonarr', theme = 'dark', actions, prepare = serviceReady, run }) {
  fixture.resetPreferences()
  const context = await contextFor(origin, true)
  let page
  try {
    const started = performance.now()
    page = await openPage(context, origin, route)
    const recording = { started, chapters: [] }
    recordings.set(page, recording)
    if (prepare) await prepare(page)
    await delay(1500)
    await run(page, origin)
    await screenshot(page, id + '-poster.png', id + '-poster', actions, theme)
    await delay(pacing.result)
    const finalRoute = new URL(page.url()).pathname
    const video = page.video()
    await context.close()
    const file = id + '.webm'
    await video.saveAs(path.join(out, file))
    manifest.captures.push({ kind: 'video', file, poster: id + '-poster.png', scenario: id, viewport, theme,
      start_route: route.split('#')[0], route: finalRoute, format: 'webm', actions,
      chapters: recording.chapters, pointer_emphasis: true,
      pacing: { tools_menu_ms: pacing.menuOpen, menu_choice_ms: pacing.menuChoice, result_ms: pacing.result } })
    await video.delete()
  } finally { await context.close().catch(() => {}) }
}

try {
  fixture = await createFixture({ WebSocketServer })
  const port = await freePort()
  const origin = 'http://127.0.0.1:' + port
  child = spawn(process.execPath, [path.join(frontendRoot, '.output/server/index.mjs')], {
    cwd: frontendRoot,
    env: { PATH: process.env.PATH, NODE_ENV: 'production', NITRO_HOST: '127.0.0.1', NITRO_PORT: String(port),
      DMB_API_URL: fixture.origin, DUMB_API_URL: fixture.origin,
      DMB_TRAEFIK_URL: fixture.origin, DUMB_TRAEFIK_URL: fixture.origin },
    stdio: ['ignore', 'pipe', 'pipe'],
  })
  for (const stream of [child.stdout, child.stderr]) stream.on('data', chunk => { childOutput = (childOutput + chunk).slice(-5000) })
  let ready = false
  for (let attempt = 0; attempt < 150; attempt++) {
    if (child.exitCode !== null) throw new Error('The isolated frontend exited before becoming ready')
    try { if ((await fetch(origin + '/api/health')).ok) { ready = true; break } } catch {}
    await delay(100)
  }
  if (!ready) throw new Error('The isolated frontend did not become ready')
  browser = await chromium.launch({ headless: true })
  const context = await contextFor(origin)
  try {
    const page = await openPage(context, origin, '/')
    await page.locator('[data-service-name="Sonarr"]').waitFor()
    await screenshot(page, 'dashboard.png', 'dashboard', ['Review example service states on the dashboard'])
    await page.goto(origin + '/services/Sonarr', { waitUntil: 'networkidle' })
    await serviceReady(page)
    await screenshot(page, 'service-controls.png', 'service-controls', ['Open Sonarr', 'Review status and Start, Stop, Restart controls without changing them'])
    await logsTab(page)
    await page.getByPlaceholder('Enter text to filter logs', { exact: true }).fill('Example Series')
    await screenshot(page, 'service-logs.png', 'service-logs-filter', ['Open Service Logs', 'Filter by Example Series'])
    await page.goto(origin + '/services/Sonarr', { waitUntil: 'networkidle' })
    await serviceReady(page)
    await updatesPanel(page)
    await page.getByRole('button', { name: /Check for updates\b/i }).click()
    await page.getByText('4.0.1', { exact: true }).waitFor()
    await screenshot(page, 'updates.png', 'updates-review', ['Open Updates', 'Check for updates', 'Review the example available version without installing'])
    await page.goto(origin + '/settings#appearance', { waitUntil: 'networkidle' })
    const appearance = await settingsSection(page, 'Appearance', 'appearance')
    await appearance.getByRole('button', { name: 'Light', exact: true }).click()
    await screenshot(page, 'appearance-settings.png', 'appearance-settings', ['Open Settings', 'Expand Appearance', 'Select Light'], 'light')
    await appearance.getByRole('button', { name: 'Dark', exact: true }).click()

    // The remaining stills show read-only views, not completed operations.
    await page.goto(origin + '/metrics', { waitUntil: 'networkidle' })
    await page.getByRole('heading', { name: 'Metrics', exact: true }).waitFor()
    await page.getByText('12.4%', { exact: true }).first().waitFor()
    await delay(1000)
    await screenshot(page, 'metrics.png', 'metrics', ['Open Metrics', 'Review example CPU, memory, disk and history measurements'])

    await page.goto(origin + '/settings#embedded-uis', { waitUntil: 'networkidle' })
    const embedded = await settingsSection(page, 'Embedded UIs', 'embedded-uis')
    await embedded.getByLabel('Enable embedded service iFrames', { exact: true }).waitFor()
    await screenshot(page, 'embedded-ui-settings.png', 'embedded-ui-settings', ['Open Settings', 'Find Embedded UIs', 'Review the disabled embedded-service setting without changing it'])

    await page.goto(origin + '/settings#about', { waitUntil: 'networkidle' })
    const about = await settingsSection(page, 'About', 'about')
    await about.getByText('v1.91.0', { exact: true }).waitFor()
    await screenshot(page, 'about.png', 'about', ['Open Settings', 'Find About', 'Compare the separate example DUMB and frontend version rows'])

    await page.goto(origin + '/', { waitUntil: 'networkidle' })
    const sidebarTools = page.getByRole('button', { name: /Sidebar tools/ }).first()
    const showDisabled = page.getByText('Show Disabled', { exact: true }).locator('..').locator('input[type=checkbox]')
    if (!await showDisabled.isVisible()) await sidebarTools.click()
    await showDisabled.check()
    const serviceFilter = page.getByPlaceholder('Filter services...', { exact: true })
    await serviceFilter.fill('Tautulli')
    await page.getByText('Tautulli', { exact: true }).first().waitFor()
    await screenshot(page, 'disabled-services.png', 'disabled-services', ['Open Sidebar tools', 'Enable Show Disabled', 'Filter the sidebar to the disabled example Tautulli service; no service state is changed'])
    await serviceFilter.clear()
    await showDisabled.uncheck()
    await sidebarTools.click()
  } finally { await context.close() }

  fixture.resetChecks()
  await record(origin, {
    id: 'service-logs',
    actions: ['Open Service Logs', 'Filter by Example Series', 'Review Warning and All levels', 'Choose Every 5s, then Off', 'Disable Follow tail'],
    run: async page => {
      chapter(page, 'Open Service Logs')
      await hoverClick(page, page.getByText('Service Logs', { exact: true }).first())
      const filter = page.getByPlaceholder('Enter text to filter logs', { exact: true })
      await filter.waitFor()
      chapter(page, 'Filter the displayed lines')
      await hoverClick(page, filter)
      await filter.pressSequentially('Example Series', { delay: 100 })
      await delay(pacing.result)
      const levels = page.locator('select').filter({ has: page.locator('option[value="WARNING"]') }).first()
      chapter(page, 'Review a log level')
      await focusControl(page, levels)
      await levels.selectOption('WARNING')
      await delay(pacing.result)
      await levels.selectOption('')
      await delay(pacing.result)
      const refresh = page.locator('select').filter({ has: page.locator('option[value="5000"]') }).first()
      chapter(page, 'Pause automatic refresh')
      await focusControl(page, refresh)
      await refresh.selectOption('5000')
      await delay(pacing.result)
      await refresh.selectOption('0')
      await delay(pacing.result)
      const follow = page.getByLabel('Follow tail', { exact: true })
      await focusControl(page, follow)
      await follow.uncheck()
      await page.evaluate(() => globalThis.__docsCaptureHighlight?.(null))
      await delay(pacing.result)
    },
  })
  fixture.resetChecks()
  await record(origin, {
    id: 'updates-check',
    actions: ['Open Service tools', 'Choose Updates', 'Check for updates', 'Review example version 4.0.1 without installing it'],
    run: async page => {
      await updatesPanel(page)
      chapter(page, 'Check the example update status')
      await hoverClick(page, page.getByRole('button', { name: /Check for updates\b/i }))
      await page.getByText('4.0.1', { exact: true }).waitFor()
      chapter(page, 'Review the available version; do not install')
      await focusControl(page, page.getByText('4.0.1', { exact: true }), pacing.result)
    },
  })
  await record(origin, {
    id: 'appearance', route: '/settings#appearance', theme: 'light', prepare: null,
    actions: ['Open Settings', 'Find Appearance', 'Select Light', 'Review the changed appearance'],
    run: async page => {
      chapter(page, 'Find Appearance settings')
      const section = await settingsSection(page, 'Appearance', 'appearance')
      chapter(page, 'Choose the Light appearance')
      await hoverClick(page, section.getByRole('button', { name: 'Light', exact: true }))
      await page.evaluate(() => globalThis.__docsCaptureHighlight?.(null))
    },
  })
  await record(origin, {
    id: 'dependencies',
    actions: ['Open Service tools', 'Choose Dependencies', 'Read the example dependency details and startup order', 'Switch to Flow to review the same relationships'],
    run: async page => {
      await dependencyPanel(page)
      chapter(page, 'Read dependencies before the dependent service')
      await focusControl(page, page.getByText('Startup order:', { exact: true }), pacing.result)
      chapter(page, 'Switch to the dependency flow')
      await hoverClick(page, page.getByRole('button', { name: 'Flow', exact: true }))
      await page.getByTitle('Close Dependency graph panel.', { exact: true }).locator('..').locator('svg').first().waitFor()
      await delay(pacing.result)
    },
  })
  await record(origin, {
    id: 'auto-restart',
    actions: ['Open Service tools', 'Choose Auto-restart', 'Review the global switch and healthcheck guardrails', 'Review the separate Sonarr switch; do not apply or save'],
    run: async page => {
      await autoRestartPanel(page)
      const panel = page.getByRole('heading', { name: 'Auto-restart Settings', exact: true }).locator('../../..')
      chapter(page, 'Review the global recovery switch')
      await focusControl(page, panel.getByLabel('Enable auto-restart', { exact: true }), pacing.result)
      chapter(page, 'Review thresholds and the restart window')
      await focusControl(page, panel.getByText('Healthcheck threshold', { exact: true }).first(), pacing.result)
      await focusControl(page, panel.getByText('Max restarts (window)', { exact: true }).first(), pacing.result)
      chapter(page, 'Review the separate service switch without saving')
      await focusControl(page, panel.getByLabel('Enable auto-restart for Sonarr', { exact: true }), pacing.result)
      await page.evaluate(() => globalThis.__docsCaptureHighlight?.(null))
    },
  })
  await record(origin, {
    id: 'configuration',
    actions: ['Open Sonarr', 'Review DUMB Config', 'Switch to Service Config', 'Return to DUMB Config', 'Locate Save to File without clicking or editing'],
    run: async page => {
      chapter(page, 'Review settings managed by DUMB')
      await focusControl(page, page.getByText('DUMB Config', { exact: true }).first(), pacing.result)
      chapter(page, 'Find the application configuration')
      await hoverClick(page, page.getByText('Service Config', { exact: true }).first())
      chapter(page, 'Return to DUMB configuration')
      await hoverClick(page, page.getByText('DUMB Config', { exact: true }).first())
      chapter(page, 'Locate the save action; leave settings unchanged')
      await focusControl(page, page.getByRole('button', { name: /Save to File\b/ }).first(), pacing.result)
      await page.evaluate(() => globalThis.__docsCaptureHighlight?.(null))
    },
  })
  manifest.unexpected_fixture_requests = fixture.state.unexpected
  manifest.api_calls = fixture.state.calls
  manifest.websocket_paths = [...new Set(fixture.state.websocketPaths)]
  manifest.complete = !manifest.errors.length && !manifest.unexpected_fixture_requests.length && !manifest.blocked_requests.length
  if (!manifest.complete) throw new Error('Capture needs review: unexpected requests or browser errors are recorded in manifest.json')
  console.log(JSON.stringify({ complete: true, frontend: FRONTEND, captures: manifest.captures.map(row => row.file) }))
} catch (error) {
  manifest.errors.push({ scenario: 'runner', message: error.message })
  manifest.unexpected_fixture_requests = fixture?.state.unexpected || []
  console.error('Frontend capture failed; inspect manifest.json. No live backend was used.')
  process.exitCode = 1
} finally {
  try { await cleanup() } catch (error) {
    manifest.errors.push({ scenario: 'cleanup', message: error.message })
    process.exitCode = 1
  }
  manifest.api_calls = fixture?.state.calls || []
  manifest.config_requests = fixture?.state.configRequests || []
  manifest.websocket_paths = [...new Set(fixture?.state.websocketPaths || [])]
  manifest.unexpected_fixture_requests = fixture?.state.unexpected || []
  manifest.complete = manifest.complete && !manifest.errors.length
    && !manifest.unexpected_fixture_requests.length && !manifest.blocked_requests.length
  await fs.writeFile(path.join(out, 'manifest.json'), JSON.stringify(manifest, null, 2) + '\n')
}
