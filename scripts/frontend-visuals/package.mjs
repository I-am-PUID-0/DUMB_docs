#!/usr/bin/env node
// Package reviewed captures; this command never starts a frontend or backend.
import fs from 'node:fs/promises'
import path from 'node:path'
import { createHash } from 'node:crypto'
import { spawnSync } from 'node:child_process'
import { FRONTEND } from './fixture.mjs'
import { readPlan, scenarioById } from './capture-catalog.mjs'

const viewport = { width: 1280, height: 800 }
const specifications = [
  { input: 'dashboard.png', file: 'dashboard.webp', kind: 'image', scenario: 'dashboard' },
  { input: 'service-controls.png', file: 'service-controls.webp', kind: 'image', scenario: 'service-controls' },
  { input: 'service-logs-poster.png', file: 'service-logs.webp', kind: 'image', scenario: 'service-logs', actionsFrom: 'service-logs.webm' },
  { input: 'updates-check-poster.png', file: 'updates.webp', kind: 'image', scenario: 'updates-review', actionsFrom: 'updates-check.webm' },
  { input: 'appearance-poster.png', file: 'appearance.webp', kind: 'image', scenario: 'appearance-settings', actionsFrom: 'appearance.webm' },
  { input: 'metrics.png', file: 'metrics.webp', kind: 'image', scenario: 'metrics' },
  { input: 'embedded-ui-settings.png', file: 'embedded-ui-settings.webp', kind: 'image', scenario: 'embedded-ui-settings' },
  { input: 'disabled-services.png', file: 'disabled-services.webp', kind: 'image', scenario: 'disabled-services' },
  { input: 'about.png', file: 'about.webp', kind: 'image', scenario: 'about' },
  { input: 'configuration-poster.png', file: 'configuration.webp', kind: 'image', scenario: 'configuration', actionsFrom: 'configuration.webm' },
  { input: 'dependencies-poster.png', file: 'dependencies.webp', kind: 'image', scenario: 'dependencies', actionsFrom: 'dependencies.webm' },
  { input: 'auto-restart-poster.png', file: 'auto-restart.webp', kind: 'image', scenario: 'auto-restart', actionsFrom: 'auto-restart.webm' },
  { input: 'service-logs.webm', file: 'service-logs.webm', kind: 'video', scenario: 'service-logs', poster: 'service-logs.webp' },
  { input: 'updates-check.webm', file: 'updates.webm', kind: 'video', scenario: 'updates-check', poster: 'updates.webp' },
  { input: 'appearance.webm', file: 'appearance.webm', kind: 'video', scenario: 'appearance', poster: 'appearance.webp' },
  { input: 'configuration.webm', file: 'configuration.webm', kind: 'video', scenario: 'configuration', poster: 'configuration.webp' },
  { input: 'dependencies.webm', file: 'dependencies.webm', kind: 'video', scenario: 'dependencies', poster: 'dependencies.webp' },
  { input: 'auto-restart.webm', file: 'auto-restart.webm', kind: 'video', scenario: 'auto-restart', poster: 'auto-restart.webp' },
]
const sha256 = bytes => createHash('sha256').update(bytes).digest('hex')

function parseArguments() {
  const args = {}
  for (let index = 2; index < process.argv.length; index += 2) {
    const name = process.argv[index]
    if (!['--captures', '--out', '--plan', '--scope'].includes(name) || !process.argv[index + 1] || Object.hasOwn(args, name)) {
      throw new Error('Usage: package.mjs --captures CAPTURE_DIRECTORY --out NEW_OUTPUT_DIRECTORY')
    }
    args[name] = process.argv[index + 1]
  }
  if (!args['--captures'] || !args['--out']) throw new Error('Both --captures and --out are required')
  return args
}

async function regularFile(filename) {
  const info = await fs.lstat(filename)
  if (!info.isFile() || info.isSymbolicLink() || info.size === 0) throw new Error('Capture input must be a nonempty regular file')
  return fs.readFile(filename)
}

function validateManifest(manifest) {
  if (manifest.schema_version !== 1 || manifest.complete !== true) throw new Error('Only a completed capture manifest can be packaged')
  for (const name of ['errors', 'blocked_requests', 'unexpected_fixture_requests']) {
    if (!Array.isArray(manifest[name]) || manifest[name].length) throw new Error('Capture manifest contains unresolved or missing ' + name)
  }
  for (const name of ['repository', 'version', 'tag', 'commit']) {
    if (manifest.frontend?.[name] !== FRONTEND[name]) throw new Error('Capture source does not match the pinned released frontend')
  }
  if (manifest.viewport?.width !== viewport.width || manifest.viewport?.height !== viewport.height) {
    throw new Error('Capture viewport must be 1280 by 800')
  }
  if (!Array.isArray(manifest.captures)) throw new Error('Capture manifest has no artifact inventory')
}

function pngDimensions(bytes) {
  if (bytes.length < 24 || !bytes.subarray(0, 8).equals(Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]))
    || bytes.toString('ascii', 12, 16) !== 'IHDR') throw new Error('A still capture is not a PNG image')
  return { width: bytes.readUInt32BE(16), height: bytes.readUInt32BE(20) }
}

function convertImage(input, output) {
  const result = spawnSync('convert', [input, '-strip', '-quality', '90', output], { encoding: 'utf8', maxBuffer: 128 * 1024 })
  if (result.error || result.status !== 0) throw new Error('ImageMagick convert failed; install WebP support and review the capture input')
  const measured = spawnSync('convert', [output, '-format', '%w %h', 'info:'], { encoding: 'utf8', maxBuffer: 128 * 1024 })
  if (measured.error || measured.status !== 0 || measured.stdout.trim() !== '1280 800') {
    throw new Error('The converted WebP did not preserve the 1280 by 800 viewport')
  }
}

async function legacyMain() {
  const args = parseArguments()
  const captures = await fs.realpath(args['--captures'])
  const out = path.resolve(args['--out'])
  if (out === captures || out.startsWith(captures + path.sep) || captures.startsWith(out + path.sep)) {
    throw new Error('The package output must be separate from the raw capture directory')
  }
  const rawManifest = await regularFile(path.join(captures, 'manifest.json'))
  const manifest = JSON.parse(rawManifest.toString('utf8'))
  validateManifest(manifest)

  // Validate every input before creating any output. Only listed basenames are read.
  const inputs = []
  for (const specification of specifications) {
    const rows = manifest.captures.filter(row => row.file === specification.input && row.kind === specification.kind)
    if (rows.length !== 1) throw new Error('Missing or ambiguous capture inventory entry: ' + specification.input)
    const row = rows[0]
    if (row.viewport?.width !== viewport.width || row.viewport?.height !== viewport.height) throw new Error('An artifact has an unexpected viewport')
    const actionsRow = specification.actionsFrom
      ? manifest.captures.find(item => item.kind === 'video' && item.file === specification.actionsFrom)
      : row
    const actions = actionsRow?.actions || actionsRow?.steps
    if (!Array.isArray(actions) || !actions.length || actions.some(value => typeof value !== 'string')) throw new Error('An artifact is missing its captured actions')
    if (!['light', 'dark'].includes(row.theme) || typeof row.route !== 'string' || !row.route.startsWith('/') || row.route.startsWith('//') || /[?#]/.test(row.route)) {
      throw new Error('An artifact has invalid theme or route metadata')
    }
    const filename = path.join(captures, specification.input)
    const bytes = await regularFile(filename)
    if (specification.kind === 'image') {
      const dimensions = pngDimensions(bytes)
      if (dimensions.width !== viewport.width || dimensions.height !== viewport.height) throw new Error('A still capture is not 1280 by 800')
    } else if (bytes.length < 4 || !bytes.subarray(0, 4).equals(Buffer.from([0x1a, 0x45, 0xdf, 0xa3]))) {
      throw new Error('A recorded video is not a WebM/EBML file')
    }
    inputs.push({ specification, row, actions, filename, bytes })
  }

  try {
    const info = await fs.lstat(out)
    if (!info.isDirectory() || info.isSymbolicLink() || (await fs.readdir(out)).length) throw new Error('Use a new or empty output directory')
  } catch (error) {
    if (error.code !== 'ENOENT') throw error
    await fs.mkdir(out, { recursive: true })
  }

  const packaged = {
    schema_version: 1,
    complete: true,
    frontend: FRONTEND,
    series: 'tour-2',
    source_verification: 'The caller verified the immutable release tag and archived its full commit before building. This packager validates that pinned capture identity.',
    scope: 'Real released frontend rendered with public example HTTP and WebSocket responses. No live backend, provider account, media library or installation was used.',
    fixed_time: manifest.fixed_time,
    viewport,
    capture_manifest_sha256: sha256(rawManifest),
    files: [],
  }
  for (const { specification, row, actions, filename, bytes } of inputs) {
    const destination = path.join(out, specification.file)
    if (specification.kind === 'image') convertImage(filename, destination)
    else await fs.writeFile(destination, bytes, { flag: 'wx' })
    const artifact = await regularFile(destination)
    packaged.files.push({
      file: specification.file, kind: specification.kind,
      media_type: specification.kind === 'image' ? 'image/webp' : 'video/webm',
      sha256: sha256(artifact), bytes: artifact.length,
      scenario: specification.scenario, captured_from: specification.input,
      viewport, theme: row.theme, route: row.route, actions,
      ...(specification.poster ? { poster: specification.poster } : {}),
      ...(specification.kind === 'image' ? { quality: 90 } : {}),
      ...(specification.kind === 'video' ? {
        start_route: row.start_route,
        chapters: row.chapters,
        pointer_emphasis: row.pointer_emphasis === true,
        pacing: row.pacing,
      } : {}),
    })
  }
  await fs.writeFile(path.join(out, 'manifest.json'), JSON.stringify(packaged, null, 2) + '\n', { flag: 'wx' })
  console.log(JSON.stringify({ complete: true, frontend: FRONTEND, files: packaged.files.map(row => ({ file: row.file, bytes: row.bytes, sha256: row.sha256 })) }))
}


async function packagePlannedCaptures() {
  const args = parseArguments()
  if (!args['--plan']) throw new Error('Schema-2 captures require --plan for immutable source and coverage verification')
  const { plan } = await readPlan(args['--plan'])
  const captures = await fs.realpath(args['--captures'])
  const out = path.resolve(args['--out'])
  if (out === captures || out.startsWith(captures + path.sep) || captures.startsWith(out + path.sep)) throw new Error('Package output must be separate from raw captures')
  const rawManifest = await regularFile(path.join(captures, 'manifest.json'))
  const manifest = JSON.parse(rawManifest)
  if (manifest.schema_version !== 2 || manifest.complete !== true) throw new Error('Only completed schema-2 captures can be packaged')
  for (const key of ['errors', 'blocked_requests', 'unexpected_fixture_requests']) {
    if (!Array.isArray(manifest[key]) || manifest[key].length) throw new Error('Capture contains missing or unresolved ' + key)
  }
  for (const key of ['channel', 'plan_sha256', 'catalog_sha256', 'dataset_sha256', 'tooling_sha256', 'capability_source_sha256']) {
    if (manifest[key] !== plan[key]) throw new Error('Capture plan identity mismatch: ' + key)
  }
  for (const key of ['frontend', 'backend']) {
    if (JSON.stringify(manifest[key]) !== JSON.stringify(plan[key])) throw new Error('Capture source identity mismatch: ' + key)
  }
  if (manifest.viewport?.width !== viewport.width || manifest.viewport?.height !== viewport.height) throw new Error('Unexpected capture viewport')
  if (!Array.isArray(manifest.coverage) || !Array.isArray(manifest.captures)) throw new Error('Capture needs explicit scenario coverage and artifact inventory')
  const partial = args['--scope'] === 'partial'
  if (args['--scope'] && !['partial', 'complete'].includes(args['--scope'])) throw new Error('Scope is complete or partial')
  if (!partial && manifest.coverage_complete !== true) throw new Error('Full planned coverage is required; use --scope partial only for local review')
  for (const id of plan.required_scenarios) {
    for (const theme of plan.themes) {
      const rows = manifest.coverage.filter(row => row.id === id && row.theme === theme)
      if (rows.length !== 1) throw new Error('Missing or ambiguous scenario coverage: ' + id + '/' + theme)
      if (!partial && rows[0].status !== 'captured' && rows[0].availability !== 'unavailable') throw new Error('Required scenario was not captured: ' + id + '/' + theme)
    }
  }
  const claimed = new Map()
  for (const row of manifest.coverage.filter(row => row.status === 'captured')) {
    if (!scenarioById.has(row.id) || !plan.scenarios.includes(row.id) || !plan.themes.includes(row.theme)
      || !Array.isArray(row.artifacts)) throw new Error('Invalid captured scenario coverage')
    const expected = scenarioById.get(row.id).kinds.map(kind => row.theme + '/' + row.id + (kind === 'image' ? '.png' : '.webm'))
    if (JSON.stringify([...row.artifacts].sort()) !== JSON.stringify(expected.sort())) throw new Error('Scenario artifact inventory is incomplete: ' + row.id)
    for (const filename of row.artifacts) {
      if (claimed.has(filename)) throw new Error('A capture artifact is claimed twice')
      claimed.set(filename, row)
    }
  }
  if (!claimed.size || claimed.size !== manifest.captures.length) throw new Error('Capture artifacts and coverage do not agree')
  const inputs = []
  for (const row of manifest.captures) {
    const coverage = claimed.get(row.file)
    if (!coverage || !/^(dark|light)\/[a-z][a-z0-9-]*\.(png|webm)$/.test(row.file)
      || row.scenario !== coverage.id || row.theme !== coverage.theme
      || !['image', 'video'].includes(row.kind)) throw new Error('Invalid artifact identity')
    if (row.viewport?.width !== viewport.width || row.viewport?.height !== viewport.height) throw new Error('Artifact viewport mismatch')
    const actions = row.actions || row.steps
    if (!Array.isArray(actions) || !actions.length || actions.some(value => typeof value !== 'string')) throw new Error('Missing artifact actions')
    if (typeof row.route !== 'string' || !row.route.startsWith('/') || row.route.startsWith('//') || /[?#]/.test(row.route)) throw new Error('Invalid captured route')
    const filename = path.join(captures, row.file)
    const bytes = await regularFile(filename)
    if (row.sha256 !== sha256(bytes) || row.bytes !== bytes.length) throw new Error('Capture bytes changed after the runner recorded them')
    if (row.kind === 'image') {
      const dimensions = pngDimensions(bytes)
      if (dimensions.width !== viewport.width || dimensions.height !== viewport.height || !row.file.endsWith('.png')) throw new Error('Invalid captured PNG')
    } else if (!row.file.endsWith('.webm') || !bytes.subarray(0, 4).equals(Buffer.from([0x1a, 0x45, 0xdf, 0xa3]))) throw new Error('Invalid captured WebM')
    inputs.push({ row, actions, filename, bytes, output: row.file.replace(/\.png$/, '.webp') })
  }
  try {
    const info = await fs.lstat(out)
    if (!info.isDirectory() || info.isSymbolicLink() || (await fs.readdir(out)).length) throw new Error('Use a new or empty output directory')
  } catch (error) {
    if (error.code !== 'ENOENT') throw error
    await fs.mkdir(out, { recursive: true })
  }
  const packaged = {
    schema_version: 2, channel: plan.channel, frontend: plan.frontend, backend: plan.backend,
    plan_sha256: plan.plan_sha256, catalog_sha256: plan.catalog_sha256, dataset_sha256: plan.dataset_sha256,
    tooling_sha256: plan.tooling_sha256, capability_source_sha256: plan.capability_source_sha256,
    complete: true, coverage_complete: manifest.coverage_complete === true, scope: manifest.scope,
    captured_at: manifest.captured_at,
    dataset: manifest.dataset, fixed_time: manifest.fixed_time, viewport, themes: plan.themes,
    native_apps: manifest.native_apps, native_app_observations: manifest.native_app_observations, measurements: manifest.measurements,
    capture_manifest_sha256: sha256(rawManifest),
    simulated_operations: manifest.simulated_operations || [],
    coverage: manifest.coverage.map(row => ({ ...row, artifacts: row.artifacts.map(filename => filename.replace(/\.png$/, '.webp')) })),
    files: [],
  }
  for (const { row, actions, filename, bytes, output } of inputs) {
    const destination = path.join(out, output)
    await fs.mkdir(path.dirname(destination), { recursive: true })
    if (row.kind === 'image') convertImage(filename, destination)
    else await fs.writeFile(destination, bytes, { flag: 'wx' })
    const result = await regularFile(destination)
    packaged.files.push({
      path: output, sha256: sha256(result), bytes: result.length, kind: row.kind,
      media_type: row.kind === 'image' ? 'image/webp' : 'video/webm',
      scenario: row.scenario, theme: row.theme, viewport, route: row.route, actions,
      ...(row.kind === 'image' ? { quality: 90 } : { poster: row.poster.replace(/\.png$/, '.webp'), chapters: row.chapters, pointer_emphasis: row.pointer_emphasis, pacing: row.pacing }),
    })
  }
  await fs.writeFile(path.join(out, 'manifest.json'), JSON.stringify(packaged, null, 2) + '\n', { flag: 'wx' })
  console.log(JSON.stringify({ complete: true, coverage_complete: packaged.coverage_complete, channel: plan.channel, files: packaged.files.map(row => row.path) }))
}
async function main() {
  const args = parseArguments()
  const raw = JSON.parse(await regularFile(path.join(await fs.realpath(args['--captures']), 'manifest.json')))
  if (raw.schema_version === 2) return packagePlannedCaptures()
  return legacyMain()
}

try { await main() } catch (error) {
  console.error('Frontend media packaging failed: ' + error.message)
  process.exitCode = 1
}
