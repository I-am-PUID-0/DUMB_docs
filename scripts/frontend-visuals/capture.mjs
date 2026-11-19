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
  await context.addInitScript(({ fixed }) => {
    const NativeDate = Date
    const epoch = NativeDate.parse(fixed)
    class ExampleDate extends NativeDate {
      constructor(...values) { super(...(values.length ? values : [epoch])) }
      static now() { return epoch }
    }
    globalThis.Date = ExampleDate
    try { localStorage.setItem('dmbdb.appearance.theme', 'dark') } catch { /* Initial blank documents have no storage origin. */ }
  }, { fixed: FIXED_TIME })
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
async function updatesPanel(page) {
  const tools = page.getByRole('button', { name: 'Service tools', exact: true })
  await tools.click()
  const item = page.getByRole('menuitem').filter({ hasText: 'Updates' })
  if (await item.count()) await item.first().click()
  else await page.getByText('Updates', { exact: true }).last().click()
  await page.getByRole('button', { name: /Check for updates\b/i }).waitFor()
}
async function screenshot(page, file, scenario, steps, theme = 'dark') {
  await page.screenshot({ path: path.join(out, file), animations: 'disabled' })
  manifest.captures.push({ kind: 'image', file, scenario, steps, viewport, theme, route: new URL(page.url()).pathname })
}
async function hoverClick(page, locator) {
  const box = await locator.boundingBox()
  if (box) await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2, { steps: 8 })
  await delay(400)
  await locator.click()
  await delay(650)
}
async function record(origin, id, routine) {
  const context = await contextFor(origin, true)
  let page
  try {
    page = await openPage(context, origin, '/services/Sonarr')
    await serviceReady(page)
    await delay(1000)
    await routine(page)
    await screenshot(page, id + '-poster.png', id + '-poster', ['Final frame of the recorded example workflow'])
    await delay(1600)
    const video = page.video()
    await context.close()
    const file = id + '.webm'
    await video.saveAs(path.join(out, file))
    manifest.captures.push({ kind: 'video', file, poster: id + '-poster.png', scenario: id, viewport, theme: 'dark', route: '/services/Sonarr', format: 'webm', actions: id === 'service-logs' ? ['Open Service Logs', 'Filter Example Series', 'Choose Warning level', 'Clear level', 'Enable Every 5s refresh', 'Pause refresh with Off', 'Stop following the tail'] : ['Open Service tools', 'Open Updates', 'Check for updates', 'Review available version; do not install'] })
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
    const toggle = page.getByRole('button', { name: /^Appearance\b/ }).first()
    if (await toggle.getAttribute('aria-expanded') === 'false') await toggle.click()
    const appearance = page.locator('#settings-section-appearance')
    await appearance.getByRole('button', { name: 'Light', exact: true }).click()
    await screenshot(page, 'appearance-settings.png', 'appearance-settings', ['Open Settings', 'Expand Appearance', 'Select Light'], 'light')
  } finally { await context.close() }

  fixture.resetChecks()
  await record(origin, 'service-logs', async page => {
    await hoverClick(page, page.getByText('Service Logs', { exact: true }).first())
    const filter = page.getByPlaceholder('Enter text to filter logs', { exact: true })
    await filter.waitFor()
    await hoverClick(page, filter)
    await filter.pressSequentially('Example Series', { delay: 70 })
    await delay(900)
    const levels = page.locator('select').filter({ has: page.locator('option[value="WARNING"]') }).first()
    await levels.selectOption('WARNING')
    await delay(1000)
    await levels.selectOption('')
    const refresh = page.locator('select').filter({ has: page.locator('option[value="5000"]') }).first()
    await refresh.selectOption('5000')
    await delay(900)
    await refresh.selectOption('0')
    await page.getByLabel('Follow tail', { exact: true }).uncheck()
  })
  fixture.resetChecks()
  await record(origin, 'updates-check', async page => {
    await updatesPanel(page)
    await delay(900)
    await hoverClick(page, page.getByRole('button', { name: /Check for updates\b/i }))
    await page.getByText('4.0.1', { exact: true }).waitFor()
    await delay(1600)
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
