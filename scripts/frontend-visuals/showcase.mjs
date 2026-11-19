#!/usr/bin/env node
// Product showcase: photographs of the actual frontend, with minimal motion framing.
import fs from 'node:fs/promises'
import path from 'node:path'
import http from 'node:http'
import { createHash } from 'node:crypto'
import { createRequire } from 'node:module'
import { fileURLToPath } from 'node:url'
import { tmpdir } from 'node:os'
import { spawn } from 'node:child_process'
import { once } from 'node:events'
import { setTimeout as delay } from 'node:timers/promises'

const frame = { width: 1920, height: 1280 }
const sha256 = bytes => createHash('sha256').update(bytes).digest('hex')
const ownChildren = new Set()
const ownTemporaryDirectories = new Set()
let browser, context, server, stopping

function parseArguments() {
  const args = { '--theme': 'both', '--plan': fileURLToPath(new URL('./showcase-scenes.json', import.meta.url)) }
  const supplied = new Set()
  for (let index = 2; index < process.argv.length; index += 2) {
    const name = process.argv[index]
    if (!['--frontend-root', '--media', '--out', '--plan', '--theme'].includes(name) || !process.argv[index + 1] || supplied.has(name)) throw new Error('Usage: showcase.mjs --frontend-root ISOLATED_FRONTEND --media VERIFIED_PACKAGE --out NEW_OUTPUT_DIRECTORY [--plan SCENE_JSON] [--theme dark|light|both]')
    args[name] = process.argv[index + 1]
    supplied.add(name)
  }
  if (!args['--frontend-root'] || !args['--media'] || !args['--out'] || !['dark', 'light', 'both'].includes(args['--theme'])) throw new Error('Frontend root, media package, output and a supported theme are required')
  return args
}

async function regularFile(filename, limit = 64000000) {
  const info = await fs.lstat(filename)
  if (!info.isFile() || info.isSymbolicLink() || !info.size || info.size > limit) throw new Error('Expected a nonempty regular input within the size limit: ' + path.basename(filename))
  return fs.readFile(filename)
}

async function terminate(child) {
  if (child.exitCode !== null || child.signalCode !== null) return
  child.kill('SIGTERM')
  const exited = await Promise.race([once(child, 'close').then(() => true), delay(3000).then(() => false)])
  if (!exited && child.exitCode === null && child.signalCode === null) { child.kill('SIGKILL'); await once(child, 'close') }
}

async function cleanup() {
  if (stopping) return stopping
  stopping = (async () => {
    await context?.close().catch(() => {})
    await browser?.close().catch(() => {})
    if (server?.listening) await new Promise(resolve => server.close(resolve))
    await Promise.all([...ownChildren].map(child => terminate(child).catch(() => {})))
    await Promise.all([...ownTemporaryDirectories].map(directory => fs.rm(directory, { recursive: true, force: true })))
  })()
  return stopping
}
for (const signal of ['SIGINT', 'SIGTERM']) process.once(signal, () => { void cleanup().finally(() => process.exit(signal === 'SIGINT' ? 130 : 143)) })

async function command(program, args, timeoutMs = 600000) {
  const child = spawn(program, args, { stdio: ['ignore', 'pipe', 'pipe'] })
  ownChildren.add(child)
  let stdout = '', stderr = '', timedOut = false
  child.stdout.on('data', chunk => { stdout = (stdout + chunk.toString()).slice(-1048576) })
  child.stderr.on('data', chunk => { stderr = (stderr + chunk.toString()).slice(-131072) })
  const timer = setTimeout(() => { timedOut = true; void terminate(child) }, timeoutMs)
  try {
    const [code] = await once(child, 'close')
    if (code !== 0 || timedOut) throw new Error(`${program} failed${timedOut ? ' (timeout)' : ''}: ${stderr.slice(-1800)}`)
    return stdout
  } finally { clearTimeout(timer); ownChildren.delete(child) }
}

async function probe(filename) {
  return JSON.parse(await command('ffprobe', ['-v', 'error', '-show_entries', 'format=duration:stream=codec_type,codec_name,width,height', '-of', 'json', filename], 30000))
}

function faststart(bytes) {
  let offset = 0, movie = -1, data = -1
  while (offset + 8 <= bytes.length) {
    let size = bytes.readUInt32BE(offset)
    const type = bytes.toString('ascii', offset + 4, offset + 8)
    if (size === 1) {
      if (offset + 16 > bytes.length) return false
      const extended = bytes.readBigUInt64BE(offset + 8)
      if (extended > BigInt(Number.MAX_SAFE_INTEGER)) return false
      size = Number(extended)
    } else if (!size) size = bytes.length - offset
    if (size < 8 || offset + size > bytes.length) return false
    if (type === 'moov') movie = offset
    if (type === 'mdat') data = offset
    offset += size
  }
  return movie >= 0 && data > movie
}

function animationInfo(bytes) {
  if (bytes.toString('ascii', 0, 4) !== 'RIFF' || bytes.toString('ascii', 8, 12) !== 'WEBP') throw new Error('Animated preview is not a WebP file')
  let offset = 12, frames = 0, milliseconds = 0
  while (offset + 8 <= bytes.length) {
    const size = bytes.readUInt32LE(offset + 4)
    if (offset + 8 + size > bytes.length) throw new Error('Animated WebP has an invalid chunk')
    if (bytes.toString('ascii', offset, offset + 4) === 'ANMF') {
      if (size < 16) throw new Error('Animated WebP frame header is incomplete')
      frames += 1
      milliseconds += bytes.readUIntLE(offset + 20, 3)
    }
    offset += 8 + size + (size % 2)
  }
  return { frames, duration_seconds: milliseconds / 1000 }
}

function validatePlan(plan) {
  if (plan.schema_version !== 1 || !Array.isArray(plan.scenes) || plan.scenes.length < 4 || plan.scenes.length > 10) throw new Error('Expected a supported product-showcase plan')
  let duration = 0
  const ids = new Set()
  for (const scene of plan.scenes) {
    if (!/^[a-z][a-z0-9-]*$/.test(scene.id) || ids.has(scene.id) || !/^[a-z][a-z0-9-]*$/.test(scene.scenario)) throw new Error('Showcase scene IDs and scenario names must be safe and unique')
    ids.add(scene.id)
    if (typeof scene.label !== 'string' || scene.label.length > 55 || typeof scene.description !== 'string' || scene.description.length > 110 || /[<>\r\n]/.test(scene.label + scene.description)) throw new Error('Each showcase beat needs short plain feature text')
    if (!Number.isFinite(scene.duration_seconds) || scene.duration_seconds < 3 || scene.duration_seconds > 7) throw new Error('Each showcase beat must last 3–7 seconds')
    if (!['image', 'video'].includes(scene.kind)) throw new Error('Use an actual screenshot or recorded application clip')
    if (scene.kind === 'video') {
      if (typeof scene.chapter !== 'string' || !scene.chapter || !Number.isFinite(scene.chapter_offset_seconds) || scene.chapter_offset_seconds < 0) throw new Error('An action scene requires a recorded chapter and a nonnegative offset')
    } else for (const camera of [scene.camera?.from, scene.camera?.to]) {
      if (!Array.isArray(camera) || camera.length !== 3 || camera.some(value => !Number.isFinite(value)) || Math.abs(camera[0]) > 5 || Math.abs(camera[1]) > 5 || camera[2] < 1 || camera[2] > 1.015) throw new Error('Camera framing must preserve screen legibility')
    }
    duration += scene.duration_seconds
  }
  if (duration !== plan.duration_seconds || duration < 20 || duration > 30) throw new Error('The product loop must last 20–30 seconds')
  return duration
}

function timestamp(seconds) {
  const milliseconds = Math.round(seconds * 1000)
  return `00:${String(Math.floor(milliseconds / 60000)).padStart(2, '0')}:${String(Math.floor(milliseconds / 1000) % 60).padStart(2, '0')}.${String(milliseconds % 1000).padStart(3, '0')}`
}

function textArtifacts(plan) {
  let start = 0
  const captions = ['WEBVTT', ''], chapters = ['WEBVTT', ''], transcript = [`# ${plan.title}`, '', 'Real DUMB frontend screens with reserved example data. Feature labels only; no narration.', '']
  for (const scene of plan.scenes) {
    const cue = `${timestamp(start)} --> ${timestamp(start + scene.duration_seconds)}`
    captions.push(scene.id, cue, scene.label, scene.description, '')
    chapters.push(scene.id, cue, scene.label, '')
    transcript.push(`## ${timestamp(start).slice(3, 8)} — ${scene.label}`, '', scene.description, '')
    start += scene.duration_seconds
  }
  return { captions: captions.join('\n') + '\n', chapters: chapters.join('\n') + '\n', transcript: transcript.join('\n') + '\n' }
}

function html(plan, theme, frontend) {
  const payload = JSON.stringify(plan).replace(/</g, '\\u003c')
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Inside DUMB</title><link rel="icon" href="data:,"><style>
  *{box-sizing:border-box}html,body{margin:0;width:1920px;height:1280px;overflow:hidden;font-family:Arial,Helvetica,sans-serif;background:${theme === 'dark' ? '#101923' : '#eef3f6'};color:${theme === 'dark' ? '#eff7fb' : '#142c3f'}}header{position:absolute;top:0;left:0;right:0;height:72px;display:flex;align-items:center;padding:0 30px;gap:25px;border-bottom:1px solid ${theme === 'dark' ? '#35505e' : '#cad9e1'}}.brand{font-weight:800;font-size:26px;letter-spacing:1px}.divider{height:25px;width:1px;background:${theme === 'dark' ? '#3e5c6b' : '#b6c9d4'}}#feature{font-size:31px;font-weight:600;letter-spacing:-.4px}.identity{margin-left:auto;font-size:20px;color:${theme === 'dark' ? '#b4cbd7' : '#4e6676'}}main{position:absolute;left:0;top:72px;width:1920px;height:1200px;overflow:hidden;isolation:isolate;background:${theme === 'dark' ? '#111b28' : '#f8fafc'}}main img,main video{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;opacity:0;transition:opacity 650ms ease;transform-origin:50% 35%;will-change:transform,opacity}.progress{position:absolute;bottom:0;left:0;right:0;height:8px;background:${theme === 'dark' ? '#263d4c' : '#d6e3e9'}}.progress span{display:block;height:100%;width:100%;transform-origin:left;background:${theme === 'dark' ? '#67d6d5' : '#087f8c'}}
  </style></head><body><header><span class="brand">DUMB</span><span class="divider"></span><span id="feature"></span><span class="identity">${theme === 'dark' ? 'Dark' : 'Light'} · Frontend ${frontend.version} · Example data</span></header><main id="screens"></main><div class="progress"><span id="progress"></span></div><script>
  const plan=${payload};const media=new Map();let first=true;
  const event=(element,name)=>new Promise((resolve,reject)=>{const timeout=setTimeout(()=>reject(new Error('Timed out waiting for '+name)),12000);element.addEventListener(name,()=>{clearTimeout(timeout);resolve()},{once:true});element.addEventListener('error',()=>{clearTimeout(timeout);reject(new Error('Actual capture media failed to load'))},{once:true})});
  window.__ready=(async()=>{for(const scene of plan.scenes){const element=document.createElement(scene.kind==='video'?'video':'img');if(scene.kind==='video'){element.muted=true;element.playsInline=true;element.preload='auto';element.playbackRate=1;element.src='/media/'+scene.scenario+'.webm';document.getElementById('screens').append(element);await event(element,'loadeddata');if(Math.abs(element.currentTime-scene.source_start_seconds)>.02){const seeked=event(element,'seeked');element.currentTime=scene.source_start_seconds;await seeked}}else{element.alt=scene.description;element.src='/media/'+scene.scenario+'.webp';document.getElementById('screens').append(element);await element.decode()}media.set(scene.id,element)}await document.fonts.ready;return true})();
  window.__scene=async(id)=>{await window.__ready;const scene=plan.scenes.find(row=>row.id===id);for(const element of media.values()){element.style.opacity='0';if(element.tagName==='VIDEO')element.pause()}const element=media.get(id);if(first){element.style.transition='none';first=false}element.style.opacity='1';document.getElementById('feature').textContent=scene.label;if(scene.kind==='video'){element.playbackRate=1;await element.play()}else{const transform=value=>'translate3d('+value[0]+'px,'+value[1]+'px,0) scale('+value[2]+')';element.animate([{transform:transform(scene.camera.from)},{transform:transform(scene.camera.to)}],{duration:scene.duration_seconds*1000,easing:'linear',fill:'forwards'})}await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));element.style.transition='opacity 650ms ease';return true};
  window.__observed=id=>{const element=media.get(id);return element.tagName==='VIDEO'?{current_time:element.currentTime,playback_rate:element.playbackRate,ended:element.ended}:null};
  window.__progress=value=>document.getElementById('progress').style.transform='scaleX('+value+')';
  </script></body></html>`
}

async function startServer(content, inputs, errors) {
  const resources = new Map([['/', { bytes: Buffer.from(content), type: 'text/html; charset=utf-8' }], ['/favicon.ico', { bytes: Buffer.from([0]), type: 'image/x-icon' }]])
  for (const [scenario, input] of inputs) resources.set('/media/' + scenario + (input.kind === 'video' ? '.webm' : '.webp'), { bytes: input.bytes, type: input.kind === 'video' ? 'video/webm' : 'image/webp' })
  server = http.createServer((request, response) => {
    const resource = resources.get(request.url)
    if (!resource || !['GET', 'HEAD'].includes(request.method)) { errors.push({ type: 'unexpected_request', route: request.url }); response.writeHead(404).end(); return }
    const headers = { 'Content-Type': resource.type, 'Cache-Control': 'no-store', 'Accept-Ranges': 'bytes' }
    const range = request.headers.range?.match(/^bytes=(\d+)-(\d*)$/)
    let start = 0, end = resource.bytes.length - 1
    if (request.headers.range) {
      if (!range) { response.writeHead(416, { 'Content-Range': 'bytes */' + resource.bytes.length }).end(); return }
      start = Number(range[1]); end = range[2] ? Math.min(Number(range[2]), end) : end
      if (!Number.isSafeInteger(start) || start < 0 || start > end) { response.writeHead(416, { 'Content-Range': 'bytes */' + resource.bytes.length }).end(); return }
      headers['Content-Range'] = `bytes ${start}-${end}/${resource.bytes.length}`
    }
    headers['Content-Length'] = end - start + 1
    response.writeHead(range ? 206 : 200, headers)
    response.end(request.method === 'HEAD' ? undefined : resource.bytes.subarray(start, end + 1))
  })
  server.listen(0, '127.0.0.1')
  await once(server, 'listening')
  return { origin: `http://127.0.0.1:${server.address().port}`, resources }
}

async function recordTheme(frontendRoot, source, inputs, plan, theme, destination) {
  const errors = [], timings = []
  await fs.mkdir(destination)
  const raw = await fs.mkdtemp(path.join(tmpdir(), 'dumb-docs-showcase-'))
  ownTemporaryDirectories.add(raw)
  const resolvedPlan = { ...plan, scenes: plan.scenes.map(scene => ({ ...scene, ...(scene.kind === 'video' ? { source_start_seconds: inputs.get(scene.scenario).source_start_seconds } : {}) })) }
  const endpoint = await startServer(html(resolvedPlan, theme, source.frontend), inputs, errors)
  context = await browser.newContext({ viewport: frame, deviceScaleFactor: 1, locale: 'en-US', timezoneId: 'UTC', colorScheme: theme, reducedMotion: 'reduce', serviceWorkers: 'block', recordVideo: { dir: raw, size: frame } })
  await context.route('**/*', route => {
    const url = new URL(route.request().url())
    if (url.origin === endpoint.origin && endpoint.resources.has(url.pathname) && !url.search && ['GET', 'HEAD'].includes(route.request().method())) return route.continue()
    errors.push({ type: 'blocked_request', origin: url.origin }); return route.abort()
  })
  await context.routeWebSocket(/.*/, socket => { errors.push({ type: 'blocked_websocket' }); socket.close({ code: 1008, reason: 'Only verified local screenshots are used' }) })
  const page = await context.newPage()
  page.on('pageerror', error => errors.push({ type: 'browser_error', message: error.message }))
  page.on('response', response => { if (response.status() >= 400) errors.push({ type: 'http_error', status: response.status() }) })
  await page.goto(endpoint.origin + '/', { waitUntil: 'networkidle' })
  await page.evaluate(() => window.__ready)
  let boundary = performance.now(), start = boundary
  for (let index = 0; index < plan.scenes.length; index++) {
    const scene = plan.scenes[index]
    await page.evaluate(id => window.__scene(id), scene.id)
    if (!index) {
      boundary = performance.now(); start = boundary
      await page.screenshot({ path: path.join(raw, 'poster.png') })
    }
    timings.push({ id: scene.id, at_seconds: (performance.now() - start) / 1000 })
    const end = boundary + scene.duration_seconds * 1000
    while (performance.now() < end) {
      await page.evaluate(value => window.__progress(value), Math.min(1, (performance.now() - start) / (plan.duration_seconds * 1000)))
      await delay(Math.min(200, Math.max(1, end - performance.now())))
    }
    if (scene.kind === 'video') {
      const observed = await page.evaluate(id => window.__observed(id), scene.id)
      const sourceStart = inputs.get(scene.scenario).source_start_seconds
      const played = observed?.current_time - sourceStart
      if (observed?.playback_rate !== 1 || observed.ended || played < scene.duration_seconds - .45 || played > scene.duration_seconds + .3) throw new Error('Recorded action did not play through at its captured speed: ' + scene.id)
      timings[timings.length - 1].source_start_seconds = sourceStart
      timings[timings.length - 1].source_end_seconds = observed.current_time
      timings[timings.length - 1].playback_rate = observed.playback_rate
    }
    boundary = end
  }
  const video = page.video()
  await context.close(); context = undefined
  await new Promise(resolve => server.close(resolve)); server = undefined
  if (errors.length) throw new Error('Showcase browser or network errors: ' + JSON.stringify(errors))
  const rawVideo = await video.path(), rawInfo = await probe(rawVideo), rawDuration = Number(rawInfo.format?.duration)
  const trim = rawDuration - plan.duration_seconds
  if (!Number.isFinite(trim) || trim < -.2 || trim > 15) throw new Error('Recorded showcase timing is outside its expected window')
  const movie = path.join(destination, 'hero.mp4')
  await command('ffmpeg', ['-v', 'error', '-nostdin', '-i', rawVideo, '-ss', Math.max(0, trim).toFixed(3), '-t', String(plan.duration_seconds), '-an', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-maxrate', '2500k', '-bufsize', '5000k', '-r', '30', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', movie])
  const movieInfo = await probe(movie), videoStreams = movieInfo.streams.filter(row => row.codec_type === 'video'), duration = Number(movieInfo.format?.duration)
  if (videoStreams.length !== 1 || videoStreams[0].codec_name !== 'h264' || videoStreams[0].width !== frame.width || videoStreams[0].height !== frame.height || movieInfo.streams.some(row => row.codec_type === 'audio') || Math.abs(duration - plan.duration_seconds) > .2 || !faststart(await regularFile(movie))) throw new Error('Encoded showcase codec, dimensions, duration or faststart is invalid')
  if ((await fs.stat(movie)).size > 12000000) throw new Error('The product showcase exceeds 12 MB')
  await command('convert', [path.join(raw, 'poster.png'), '-strip', '-quality', '92', path.join(destination, 'poster.webp')], 30000)
  const posterSize = await command('convert', [path.join(destination, 'poster.webp'), '-format', '%w %h', 'info:'], 30000)
  if (posterSize.trim() !== '1920 1280') throw new Error('The showcase poster dimensions changed')
  await command('ffmpeg', ['-v', 'error', '-nostdin', '-i', movie, '-an', '-vf', 'fps=6,scale=1280:-2:flags=lanczos', '-c:v', 'libwebp_anim', '-lossless', '0', '-q:v', '65', '-compression_level', '4', '-loop', '0', '-fps_mode', 'passthrough', path.join(destination, 'animated.webp')])
  if ((await fs.stat(path.join(destination, 'animated.webp'))).size > 12000000) throw new Error('The animated README preview exceeds 12 MB')
  const animation = animationInfo(await regularFile(path.join(destination, 'animated.webp')))
  const animationSize = await command('convert', [path.join(destination, 'animated.webp') + '[0]', '-format', '%w %h', 'info:'], 30000)
  if (animationSize.trim() !== '1280 854' || animation.frames < 2 || Math.abs(animation.duration_seconds - plan.duration_seconds) > .5) throw new Error('The animated preview dimensions or duration are invalid')
  return { theme, duration_seconds: duration, raw_duration_seconds: rawDuration, leading_trim_seconds: Math.max(0, trim), animation, scene_timing: timings, errors }
}

async function main() {
  const args = parseArguments(), frontendRoot = await fs.realpath(args['--frontend-root']), mediaRoot = await fs.realpath(args['--media']), out = path.resolve(args['--out'])
  for (const input of [frontendRoot, mediaRoot]) if (out === input || out.startsWith(input + path.sep) || input.startsWith(out + path.sep)) throw new Error('Output must be separate from isolated source and input media')
  const rawManifest = await regularFile(path.join(mediaRoot, 'manifest.json')), source = JSON.parse(rawManifest.toString('utf8'))
  if (source.schema_version !== 2 || source.complete !== true || source.coverage_complete !== true || !Array.isArray(source.files) || !/^[a-f0-9]{40}$/.test(source.frontend?.commit || '') || !/^[a-f0-9]{40}$/.test(source.backend?.commit || '') || !['release', 'dev'].includes(source.channel)) throw new Error('A completed source-pinned schema-2 channel media package with full coverage is required')
  if (typeof source.captured_at !== 'string' || !Number.isFinite(Date.parse(source.captured_at))) throw new Error('Input package needs its actual capture timestamp')
  for (const name of ['plan_sha256', 'catalog_sha256', 'dataset_sha256', 'tooling_sha256']) if (!/^[a-f0-9]{64}$/.test(source[name] || '')) throw new Error('Input package has no valid ' + name)
  for (const name of ['errors', 'blocked_requests', 'unexpected_fixture_requests']) if (Object.hasOwn(source, name) && (!Array.isArray(source[name]) || source[name].length)) throw new Error('Input package has unresolved ' + name)
  const frontendPackage = JSON.parse((await regularFile(path.join(frontendRoot, 'package.json'))).toString('utf8'))
  const builtPackage = JSON.parse((await regularFile(path.join(frontendRoot, '.output/server/package.json'))).toString('utf8'))
  if (frontendPackage.version !== source.frontend.version || builtPackage.version !== source.frontend.version) throw new Error('Isolated source/build versions differ from the verified media package')
  const planBytes = await regularFile(args['--plan']), plan = JSON.parse(planBytes.toString('utf8'))
  validatePlan(plan)
  const themes = args['--theme'] === 'both' ? ['dark', 'light'] : [args['--theme']], media = new Map(), inputRows = []
  for (const theme of themes) {
    const inputs = new Map()
    for (const scene of plan.scenes) {
      const candidates = source.files.filter(row => row.scenario === scene.scenario && row.kind === scene.kind && row.theme === theme)
      if (candidates.length !== 1) throw new Error(`Missing or ambiguous actual ${theme} ${scene.kind} for ${scene.scenario}`)
      const row = candidates[0]
      const extension = scene.kind === 'video' ? 'webm' : 'webp'
      if (!new RegExp(`^${theme}/[a-z][a-z0-9-]*\\.${extension}$`).test(row.path)) throw new Error('Only known theme-relative media paths are allowed')
      const bytes = await regularFile(path.join(mediaRoot, row.path))
      if (bytes.length !== row.bytes || sha256(bytes) !== row.sha256 || !Number.isInteger(row.viewport?.width) || !Number.isInteger(row.viewport?.height) || row.viewport.width < 1000 || row.viewport.height < 650) throw new Error('Used screenshot hash, size or viewport does not match its package')
      const input = { kind: scene.kind, bytes }, inventory = { path: row.path, scenario: row.scenario, kind: scene.kind, theme, sha256: row.sha256, bytes: row.bytes, viewport: row.viewport }
      if (scene.kind === 'video') {
        const chapters = row.chapters?.filter(chapter => chapter.label === scene.chapter)
        if (!Array.isArray(chapters) || chapters.length !== 1 || !Number.isFinite(chapters[0].at_seconds) || chapters[0].at_seconds < 0) throw new Error('Action scene has no unique recorded chapter: ' + scene.id)
        const mediaInfo = await probe(path.join(mediaRoot, row.path)), duration = Number(mediaInfo.format?.duration)
        const streams = mediaInfo.streams.filter(stream => stream.codec_type === 'video')
        const sourceStart = chapters[0].at_seconds + scene.chapter_offset_seconds
        if (!Number.isFinite(duration) || streams.length !== 1 || streams[0].width !== row.viewport.width || streams[0].height !== row.viewport.height || mediaInfo.streams.some(stream => stream.codec_type === 'audio') || sourceStart + scene.duration_seconds > duration - .1) throw new Error('Action source dimensions, duration or chapter window is invalid: ' + scene.id)
        Object.assign(input, { source_start_seconds: sourceStart })
        Object.assign(inventory, { chapter: scene.chapter, chapter_offset_seconds: scene.chapter_offset_seconds, source_start_seconds: sourceStart, source_end_seconds: sourceStart + scene.duration_seconds, source_duration_seconds: duration, playback_rate: 1 })
      }
      inputs.set(scene.scenario, input)
      inputRows.push(inventory)
    }
    media.set(theme, inputs)
  }
  try {
    const existing = await fs.lstat(out)
    if (!existing.isDirectory() || existing.isSymbolicLink() || (await fs.readdir(out)).length) throw new Error('Use a new or empty showcase output directory')
  } catch (error) { if (error.code !== 'ENOENT') throw error; await fs.mkdir(out, { recursive: true }) }
  const requireFrontend = createRequire(path.join(frontendRoot, 'package.json')), { chromium } = requireFrontend('playwright')
  browser = await chromium.launch({ headless: true })
  const recordings = []
  for (const theme of themes) recordings.push(await recordTheme(frontendRoot, source, media.get(theme), plan, theme, path.join(out, theme)))
  await browser.close(); browser = undefined
  const artifacts = textArtifacts(plan)
  for (const [file, bytes] of [['captions.vtt', artifacts.captions], ['chapters.vtt', artifacts.chapters], ['transcript.txt', artifacts.transcript]]) await fs.writeFile(path.join(out, file), bytes, { flag: 'wx' })
  const files = []
  for (const theme of themes) for (const [file, role, kind] of [['hero.mp4', 'video', 'video'], ['poster.webp', 'poster', 'image'], ['animated.webp', 'animated', 'image']]) {
    const relative = theme + '/' + file, bytes = await regularFile(path.join(out, relative))
    files.push({ path: relative, theme, role, kind, media_type: file.endsWith('.mp4') ? 'video/mp4' : 'image/webp', sha256: sha256(bytes), bytes: bytes.length, ...(role === 'video' ? { duration_seconds: plan.duration_seconds } : {}), viewport: role === 'animated' ? { width: 1280, height: 854 } : frame })
  }
  for (const [file, role] of [['captions.vtt', 'captions'], ['chapters.vtt', 'chapters'], ['transcript.txt', 'transcript']]) {
    const bytes = await regularFile(path.join(out, file))
    files.push({ path: file, role, kind: 'text', media_type: file.endsWith('.vtt') ? 'text/vtt' : 'text/plain', sha256: sha256(bytes), bytes: bytes.length })
  }
  const manifest = {
    schema_version: 2, complete: true, kind: 'product-showcase', channel: source.channel, frontend: source.frontend, backend: source.backend, captured_at: source.captured_at,
    scope: 'Actual source-pinned frontend screenshots and recorded log/dependency actions with example API data. Action clips play at their captured speed. Minimal image camera motion and transitions; no reconstructed UI, AI imagery, narration or implied live operation.',
    viewport: frame, duration_seconds: plan.duration_seconds, themes,
    input_package_manifest_sha256: sha256(rawManifest), plan_sha256: source.plan_sha256, showcase_plan_sha256: sha256(planBytes), catalog_sha256: source.catalog_sha256, dataset_sha256: source.dataset_sha256, tooling_sha256: source.tooling_sha256, renderer_sha256: sha256(await fs.readFile(fileURLToPath(import.meta.url))),
    scenes: plan.scenes, inputs: inputRows, recordings, files, errors: [],
  }
  await fs.writeFile(path.join(out, 'manifest.json'), JSON.stringify(manifest, null, 2) + '\n', { flag: 'wx' })
  console.log(JSON.stringify({ complete: true, channel: source.channel, duration_seconds: plan.duration_seconds, themes, files }, null, 2))
}

try { await main() } catch (error) { console.error('DUMB showcase failed: ' + error.message); process.exitCode = 1 } finally { await cleanup() }
