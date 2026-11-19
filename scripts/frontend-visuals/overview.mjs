#!/usr/bin/env node
// Compose a captioned tour from verified, released frontend captures.
import fs from 'node:fs/promises'
import path from 'node:path'
import http from 'node:http'
import { createHash } from 'node:crypto'
import { createRequire } from 'node:module'
import { spawn } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import { once } from 'node:events'
import { setTimeout as delay } from 'node:timers/promises'
import { FRONTEND } from './fixture.mjs'

const frame = { width: 1920, height: 1080 }
const requiredMedia = ['dashboard.webp', 'service-controls.webp', 'service-logs.webm', 'updates.webm', 'appearance.webp', 'metrics.webp']
const fileNames = ['dumb-overview.mp4', 'poster.webp', 'captions.vtt', 'chapters.vtt']
const sha256 = bytes => createHash('sha256').update(bytes).digest('hex')
const ownChildren = new Set()
let browser, context, server, stopping

function parseArguments() {
  const args = {}
  for (let index = 2; index < process.argv.length; index += 2) {
    const name = process.argv[index]
    if (!['--frontend-root', '--media', '--logo', '--out'].includes(name) || !process.argv[index + 1] || Object.hasOwn(args, name)) {
      throw new Error('Usage: overview.mjs --frontend-root ISOLATED_FRONTEND --media VERIFIED_PACKAGE --logo DUMB_LOGO_PNG --out NEW_OUTPUT_DIRECTORY')
    }
    args[name] = process.argv[index + 1]
  }
  if (Object.keys(args).length !== 4) throw new Error('All four overview arguments are required')
  return args
}

async function regularFile(filename, limit = 64 * 1024 * 1024) {
  const info = await fs.lstat(filename)
  if (!info.isFile() || info.isSymbolicLink() || info.size === 0 || info.size > limit) throw new Error('Expected a nonempty regular input file within its size limit: ' + path.basename(filename))
  return fs.readFile(filename)
}

async function terminate(child) {
  if (child.exitCode !== null || child.signalCode !== null) return
  child.kill('SIGTERM')
  const exited = await Promise.race([once(child, 'close').then(() => true), delay(3000).then(() => false)])
  if (!exited && child.exitCode === null && child.signalCode === null) {
    child.kill('SIGKILL')
    await once(child, 'close')
  }
}

async function cleanup() {
  if (stopping) return stopping
  stopping = (async () => {
    await context?.close().catch(() => {})
    await browser?.close().catch(() => {})
    if (server?.listening) await new Promise(resolve => server.close(resolve))
    await Promise.all([...ownChildren].map(child => terminate(child).catch(() => {})))
  })()
  return stopping
}

for (const signal of ['SIGINT', 'SIGTERM']) process.once(signal, () => {
  void cleanup().finally(() => process.exit(signal === 'SIGINT' ? 130 : 143))
})

async function command(program, args, timeoutMs = 600000) {
  const child = spawn(program, args, { stdio: ['ignore', 'pipe', 'pipe'] })
  ownChildren.add(child)
  let stdout = '', stderr = '', timedOut = false
  child.stdout.on('data', chunk => { stdout = (stdout + chunk.toString()).slice(-1024 * 1024) })
  child.stderr.on('data', chunk => { stderr = (stderr + chunk.toString()).slice(-128 * 1024) })
  const timer = setTimeout(() => { timedOut = true; void terminate(child) }, timeoutMs)
  try {
    const [code] = await once(child, 'close')
    if (code !== 0 || timedOut) throw new Error(`${program} failed${timedOut ? ' (timeout)' : ''}: ${stderr.slice(-2000)}`)
    return stdout
  } finally {
    clearTimeout(timer)
    ownChildren.delete(child)
  }
}

async function probe(filename) {
  return JSON.parse(await command('ffprobe', ['-v', 'error', '-show_entries', 'format=duration:stream=codec_type,codec_name,width,height', '-of', 'json', filename], 30000))
}

function durationOf(info) {
  const duration = Number(info.format?.duration)
  if (!Number.isFinite(duration) || duration <= 0) throw new Error('Media has no valid measured duration')
  return duration
}

function hasFaststart(bytes) {
  let offset = 0, movie = -1, data = -1
  while (offset + 8 <= bytes.length) {
    let size = bytes.readUInt32BE(offset)
    const type = bytes.toString('ascii', offset + 4, offset + 8)
    if (size === 1) {
      if (offset + 16 > bytes.length) return false
      const extended = bytes.readBigUInt64BE(offset + 8)
      if (extended > BigInt(Number.MAX_SAFE_INTEGER)) return false
      size = Number(extended)
    } else if (size === 0) size = bytes.length - offset
    if (size < 8 || offset + size > bytes.length) return false
    if (type === 'moov') movie = offset
    if (type === 'mdat') data = offset
    offset += size
  }
  return movie >= 0 && data >= 0 && movie < data
}

function validateScenes(document) {
  if (document.schema_version !== 1 || !Array.isArray(document.scenes) || document.scenes.length < 6 || document.scenes.length > 15) throw new Error('Invalid overview scene document')
  let total = 0
  const identities = new Set()
  for (const scene of document.scenes) {
    if (!/^[a-z][a-z0-9-]*$/.test(scene.id) || identities.has(scene.id)) throw new Error('Scene IDs must be unique safe names')
    identities.add(scene.id)
    if (!['card', 'image', 'video'].includes(scene.kind) || typeof scene.title !== 'string' || scene.title.length > 65) throw new Error('Invalid scene type or title')
    if (!Number.isFinite(scene.duration_seconds) || scene.duration_seconds < 7 || scene.duration_seconds > 30) throw new Error('Each readable scene must last 7–30 seconds')
    if (!Array.isArray(scene.caption) || scene.caption.length < 1 || scene.caption.length > 2 || scene.caption.some(line => typeof line !== 'string' || !line.trim() || line.length > 100 || /[\r\n<>]/.test(line))) throw new Error('Captions need one or two plain readable lines')
    if (scene.kind === 'card') {
      if (!['intro', 'workflow', 'steps'].includes(scene.layout) || typeof scene.headline !== 'string') throw new Error('Invalid conceptual card layout')
      if (scene.layout !== 'intro' && (!Array.isArray(scene.steps) || scene.steps.length !== 3 || scene.steps.some(step => typeof step.title !== 'string' || typeof step.detail !== 'string'))) throw new Error('Conceptual steps need three titled explanations')
    } else {
      if (!requiredMedia.includes(scene.media) || !['contain', 'cover-top'].includes(scene.fit)) throw new Error('Scene media and fit must be explicitly allowed')
      if (scene.kind === 'video' && (!Number.isFinite(scene.media_start_seconds) || scene.media_start_seconds < 0)) throw new Error('Videos need a nonnegative source start time')
    }
    total += scene.duration_seconds
  }
  if (total !== document.duration_seconds || total < 90 || total > 120) throw new Error('The complete overview must last 90–120 seconds')
  return total
}

function vttTime(seconds) {
  const milliseconds = Math.round(seconds * 1000)
  return `${String(Math.floor(milliseconds / 3600000)).padStart(2, '0')}:${String(Math.floor(milliseconds / 60000) % 60).padStart(2, '0')}:${String(Math.floor(milliseconds / 1000) % 60).padStart(2, '0')}.${String(milliseconds % 1000).padStart(3, '0')}`
}

function tracks(scenes) {
  let time = 0
  const captions = ['WEBVTT', ''], chapters = ['WEBVTT', '']
  for (const scene of scenes) {
    const cue = `${vttTime(time)} --> ${vttTime(time + scene.duration_seconds)}`
    captions.push(scene.id, cue, ...scene.caption, '')
    chapters.push(scene.id, cue, scene.title, '')
    time += scene.duration_seconds
  }
  return { captions: captions.join('\n').trimEnd() + '\n', chapters: chapters.join('\n').trimEnd() + '\n' }
}

function tourHtml(document) {
  const payload = JSON.stringify(document).replace(/</g, '\\u003c')
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:,"><title>Meet DUMB — captioned overview</title><style>
  *{box-sizing:border-box}html,body{margin:0;width:1920px;height:1080px;overflow:hidden;background:#101923;color:#eff7fb;font-family:Arial,Helvetica,sans-serif}header{position:absolute;left:80px;right:80px;top:22px;height:68px;display:flex;align-items:center;gap:20px}header img{width:62px;height:62px}header strong{font-size:38px;letter-spacing:-1px}.chapter{margin-left:30px;font-size:30px;color:#c8d9e5}.example{margin-left:auto;font-size:23px;color:#b6cbd7}.stage{position:absolute;left:80px;top:112px;width:1760px;height:760px;overflow:hidden;border:1px solid #3a5161;border-radius:20px;background:#142432;box-shadow:0 16px 45px #0004}.stage>img,.stage>video{width:100%;height:100%;object-fit:contain;display:block}.stage>.cover-top{object-fit:cover;object-position:50% 0}.captions{position:absolute;left:80px;right:80px;top:900px;height:150px;display:flex;flex-direction:column;justify-content:center;align-items:center;gap:12px;font-size:34px;line-height:1.35;text-align:center}.caption-line{margin:0;max-width:1740px}.caption-line+*{color:#c8d9e5}.progress{position:absolute;left:80px;right:80px;bottom:10px;height:4px;background:#304655}.progress span{display:block;height:100%;background:#67d6d5;transform-origin:left}.card{height:100%;padding:72px 76px;display:flex;flex-direction:column;justify-content:center;background:radial-gradient(ellipse at 100% 0,#224a55 0,transparent 60%),#142432}.card h1{font-size:65px;line-height:1.1;letter-spacing:-2px;margin:0 0 42px}.card-intro{padding-left:112px}.card-intro img{width:150px;height:150px;margin-bottom:34px}.card-intro h1{font-size:76px;max-width:1200px;margin-bottom:30px}.card p{font-size:34px;line-height:1.5;color:#c5d7e2;max-width:1420px;margin:0}.steps{display:flex;gap:32px;align-items:stretch}.step{position:relative;flex:1;min-width:0;padding:38px 30px 36px;border:1px solid #537a88;border-radius:16px;background:#132531}.step-index{display:block;color:#83dfd9;font-size:28px;font-weight:bold;margin-bottom:22px}.step h2{font-size:38px;line-height:1.2;margin:0 0 24px;letter-spacing:-.7px}.step p{font-size:29px;line-height:1.45}.workflow .step:not(:last-child):after{content:'→';position:absolute;right:-31px;top:45%;font-size:38px;z-index:1;color:#83dfd9}.card .note{font-size:29px;margin-top:34px;color:#c5d7e2}.card-steps h1{margin-bottom:48px}
  </style></head><body><header><img src="/logo.png" alt=""><strong>DUMB</strong><span class="chapter" id="chapter"></span><span class="example">Frontend ${FRONTEND.version} · Example data</span></header><main class="stage" id="stage"></main><div class="captions" id="captions" aria-live="polite"></div><div class="progress"><span id="progress"></span></div><script>
  const tour=${payload};
  const loaded=new Map();
  const stage=document.getElementById('stage');
  const text=(tag,value,className)=>{const el=document.createElement(tag);if(className)el.className=className;el.textContent=value;return el};
  const mediaReady=(element)=>new Promise((resolve,reject)=>{const event=element.tagName==='VIDEO'?'loadeddata':'load';if(element.tagName==='IMG'&&element.complete&&element.naturalWidth)return resolve();element.addEventListener(event,resolve,{once:true});element.addEventListener('error',()=>reject(new Error('Media preload failed')), {once:true})});
  window.__tourReady=(async()=>{for(const scene of tour.scenes){if(scene.kind==='card')continue;const el=document.createElement(scene.kind==='image'?'img':'video');el.src='/media/'+scene.media;el.className=scene.fit==='cover-top'?'cover-top':'';if(scene.kind==='video'){el.muted=true;el.playsInline=true;el.preload='auto';el.playbackRate=1}else el.alt='Released DUMB frontend with example data';loaded.set(scene.id,el);await mediaReady(el)}await document.fonts.ready;return true})();
  window.__showScene=async(id)=>{await window.__tourReady;const scene=tour.scenes.find(item=>item.id===id);for(const el of loaded.values())if(el.tagName==='VIDEO')el.pause();stage.replaceChildren();document.getElementById('chapter').textContent=scene.title;const captions=document.getElementById('captions');captions.replaceChildren(...scene.caption.map(line=>text('p',line,'caption-line')));if(scene.kind==='card'){const card=text('section','','card card-'+scene.layout);if(scene.layout==='intro'){const logo=document.createElement('img');logo.src='/logo.png';logo.alt='';card.append(logo)}card.append(text('h1',scene.headline));if(scene.description)card.append(text('p',scene.description));if(scene.steps){const steps=text('div','','steps '+(scene.layout==='workflow'?'workflow':''));scene.steps.forEach((step,index)=>{const item=text('div','','step');item.append(text('span',String(index+1).padStart(2,'0'),'step-index'),text('h2',step.title),text('p',step.detail));steps.append(item)});card.append(steps)}if(scene.note)card.append(text('p',scene.note,'note'));stage.append(card)}else{const el=loaded.get(id);stage.append(el);if(scene.kind==='video'){el.currentTime=scene.media_start_seconds;if(Math.abs(el.currentTime-scene.media_start_seconds)>.02||el.seeking)await new Promise(resolve=>el.addEventListener('seeked',resolve,{once:true}));await el.play()}}document.getElementById('progress').style.transform='scaleX(0)';return true};
  window.__sceneProgress=(value)=>document.getElementById('progress').style.transform='scaleX('+value+')';
  </script></body></html>`
}

async function startServer(html, media, logo, failures) {
  const resources = new Map([['/', { bytes: Buffer.from(html), type: 'text/html; charset=utf-8' }], ['/logo.png', { bytes: logo, type: 'image/png' }], ['/favicon.ico', { bytes: logo, type: 'image/png' }]])
  for (const [file, bytes] of media) resources.set('/media/' + file, { bytes, type: file.endsWith('.webm') ? 'video/webm' : 'image/webp' })
  server = http.createServer((request, response) => {
    const item = resources.get(request.url)
    if (!item || !['GET', 'HEAD'].includes(request.method)) {
      failures.push({ type: 'unexpected_local_request', method: request.method, route: request.url })
      response.writeHead(404).end()
      return
    }
    const headers = { 'Content-Type': item.type, 'Accept-Ranges': 'bytes', 'Cache-Control': 'no-store' }
    const range = request.headers.range?.match(/^bytes=(\d+)-(\d*)$/)
    let start = 0, end = item.bytes.length - 1
    if (request.headers.range) {
      if (!range) { response.writeHead(416, { 'Content-Range': 'bytes */' + item.bytes.length }).end(); return }
      start = Number(range[1]); end = range[2] ? Math.min(Number(range[2]), end) : end
      if (!Number.isSafeInteger(start) || start < 0 || start > end) { response.writeHead(416, { 'Content-Range': 'bytes */' + item.bytes.length }).end(); return }
      headers['Content-Range'] = `bytes ${start}-${end}/${item.bytes.length}`
    }
    headers['Content-Length'] = end - start + 1
    response.writeHead(range ? 206 : 200, headers)
    response.end(request.method === 'HEAD' ? undefined : item.bytes.subarray(start, end + 1))
  })
  server.listen(0, '127.0.0.1')
  await once(server, 'listening')
  return { origin: `http://127.0.0.1:${server.address().port}`, allowed: new Set(resources.keys()) }
}

async function main() {
  const args = parseArguments()
  const frontendRoot = await fs.realpath(args['--frontend-root'])
  const mediaRoot = await fs.realpath(args['--media'])
  const out = path.resolve(args['--out'])
  for (const input of [frontendRoot, mediaRoot]) {
    if (out === input || out.startsWith(input + path.sep) || input.startsWith(out + path.sep)) throw new Error('Output must be separate from frontend source and input media')
  }
  const sourcePackage = JSON.parse((await regularFile(path.join(frontendRoot, 'package.json'))).toString('utf8'))
  const builtPackage = JSON.parse((await regularFile(path.join(frontendRoot, '.output/server/package.json'))).toString('utf8'))
  if (sourcePackage.version !== FRONTEND.version || builtPackage.version !== FRONTEND.version) throw new Error('The isolated source and build must match the pinned released frontend')
  const rawManifest = await regularFile(path.join(mediaRoot, 'manifest.json'))
  const sourceManifest = JSON.parse(rawManifest.toString('utf8'))
  if (sourceManifest.schema_version !== 1 || sourceManifest.complete !== true || !Array.isArray(sourceManifest.files)) throw new Error('A complete packaged capture manifest is required')
  for (const key of ['repository', 'version', 'tag', 'commit']) if (sourceManifest.frontend?.[key] !== FRONTEND[key]) throw new Error('Media does not match the pinned released frontend identity')
  for (const key of ['errors', 'blocked_requests', 'unexpected_fixture_requests']) {
    if (Object.hasOwn(sourceManifest, key) && (!Array.isArray(sourceManifest[key]) || sourceManifest[key].length)) throw new Error('Input manifest has unresolved ' + key)
  }
  if (sourceManifest.viewport?.width !== 1280 || sourceManifest.viewport?.height !== 800) throw new Error('Packaged source viewport must be 1280 by 800')
  const media = new Map(), inputRows = []
  for (const file of requiredMedia) {
    const rows = sourceManifest.files.filter(row => row.file === file)
    if (rows.length !== 1) throw new Error('Missing or duplicate packaged media: ' + file)
    const row = rows[0], bytes = await regularFile(path.join(mediaRoot, file))
    if (bytes.length !== row.bytes || sha256(bytes) !== row.sha256) throw new Error('Packaged artifact hash or size mismatch: ' + file)
    const expectedKind = file.endsWith('.webm') ? 'video' : 'image'
    if (row.kind !== expectedKind || row.viewport?.width !== 1280 || row.viewport?.height !== 800) throw new Error('Unexpected media kind or dimensions: ' + file)
    const input = { file, kind: row.kind, bytes: row.bytes, sha256: row.sha256, scenario: row.scenario, actions: row.actions }
    if (expectedKind === 'video') input.duration_seconds = durationOf(await probe(path.join(mediaRoot, file)))
    inputRows.push(input)
    media.set(file, bytes)
  }
  const logo = await regularFile(args['--logo'], 4 * 1024 * 1024)
  if (logo.length < 8 || !logo.subarray(0, 8).equals(Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]))) throw new Error('Use the existing public DUMB PNG logo')
  const scenesPath = fileURLToPath(new URL('./overview-scenes.json', import.meta.url))
  const scenesBytes = await regularFile(scenesPath)
  const document = JSON.parse(scenesBytes.toString('utf8'))
  const duration = validateScenes(document)
  for (const scene of document.scenes) if (scene.kind === 'video') {
    const source = inputRows.find(row => row.file === scene.media)
    if (scene.media_start_seconds >= source.duration_seconds - .1) throw new Error('Video source start is outside the captured clip: ' + scene.id)
  }
  try {
    const existing = await fs.lstat(out)
    if (!existing.isDirectory() || existing.isSymbolicLink() || (await fs.readdir(out)).length) throw new Error('Use a new or empty overview output directory')
  } catch (error) {
    if (error.code !== 'ENOENT') throw error
    await fs.mkdir(out, { recursive: true })
  }
  const rawDirectory = path.join(out, 'raw')
  await fs.mkdir(rawDirectory)
  const failures = []
  const html = tourHtml(document)
  const endpoint = await startServer(html, media, logo, failures)
  const requireFrontend = createRequire(path.join(frontendRoot, 'package.json'))
  const { chromium } = requireFrontend('playwright')
  browser = await chromium.launch({ headless: true })
  context = await browser.newContext({ viewport: frame, deviceScaleFactor: 1, locale: 'en-US', timezoneId: 'UTC', colorScheme: 'dark', reducedMotion: 'reduce', serviceWorkers: 'block', recordVideo: { dir: rawDirectory, size: frame } })
  await context.route('**/*', route => {
    const url = new URL(route.request().url())
    if (url.origin === endpoint.origin && endpoint.allowed.has(url.pathname) && !url.search && ['GET', 'HEAD'].includes(route.request().method())) return route.continue()
    failures.push({ type: 'blocked_request', origin: url.origin })
    return route.abort()
  })
  await context.routeWebSocket(/.*/, socket => {
    failures.push({ type: 'blocked_websocket' })
    socket.close({ code: 1008, reason: 'The overview uses only local verified media' })
  })
  const page = await context.newPage()
  page.on('pageerror', error => failures.push({ type: 'browser_error', message: error.message }))
  page.on('response', response => { if (response.status() >= 400) failures.push({ type: 'http_error', status: response.status() }) })
  await page.goto(endpoint.origin + '/', { waitUntil: 'networkidle' })
  await page.evaluate(() => window.__tourReady)
  const timings = []
  let targetStart = performance.now()
  const recordingStart = targetStart
  for (let index = 0; index < document.scenes.length; index++) {
    const scene = document.scenes[index]
    await page.evaluate(async id => {
      await window.__showScene(id)
      await Promise.all([...document.querySelectorAll('#stage img')].map(image => image.decode()))
      await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))
    }, scene.id)
    const actualStart = performance.now()
    if (index === 0) {
      await page.screenshot({ path: path.join(rawDirectory, 'poster.png') })
      targetStart = actualStart
    }
    timings.push({ id: scene.id, start_seconds: (actualStart - recordingStart) / 1000, planned_duration_seconds: scene.duration_seconds })
    const ends = targetStart + scene.duration_seconds * 1000
    while (performance.now() < ends) {
      const fraction = Math.min(1, (performance.now() - targetStart) / (scene.duration_seconds * 1000))
      await page.evaluate(value => window.__sceneProgress(value), fraction)
      await delay(Math.min(250, Math.max(1, ends - performance.now())))
    }
    targetStart = ends
  }
  const video = page.video()
  await context.close(); context = undefined
  await browser.close(); browser = undefined
  await new Promise(resolve => server.close(resolve)); server = undefined
  if (failures.length) throw new Error('Overview capture had browser or network errors: ' + JSON.stringify(failures))
  const rawVideo = await video.path()
  const rawDuration = durationOf(await probe(rawVideo))
  const trimStart = Math.max(0, rawDuration - duration)
  if (rawDuration < duration - .25 || trimStart > 15) throw new Error('Recorded timing is outside the expected tour window')
  const mp4 = path.join(out, 'dumb-overview.mp4')
  await command('ffmpeg', ['-v', 'error', '-nostdin', '-i', rawVideo, '-ss', trimStart.toFixed(3), '-t', String(duration), '-an', '-c:v', 'libx264', '-preset', 'medium', '-crf', '22', '-maxrate', '1600k', '-bufsize', '3200k', '-r', '30', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', mp4])
  const info = await probe(mp4)
  const videoStreams = info.streams.filter(stream => stream.codec_type === 'video')
  const measuredDuration = durationOf(info)
  if (videoStreams.length !== 1 || videoStreams[0].codec_name !== 'h264' || videoStreams[0].width !== frame.width || videoStreams[0].height !== frame.height || info.streams.some(stream => stream.codec_type === 'audio') || Math.abs(measuredDuration - duration) > .25) throw new Error('The encoded overview has unexpected codec, dimensions, audio or duration')
  if ((await fs.stat(mp4)).size > 25000000) throw new Error('The overview exceeds the 25 MB publication limit')
  if (!hasFaststart(await regularFile(mp4))) throw new Error('The MP4 does not place its metadata before media data for fast playback startup')
  await command('convert', [path.join(rawDirectory, 'poster.png'), '-strip', '-quality', '90', path.join(out, 'poster.webp')], 30000)
  const posterDimensions = await command('convert', [path.join(out, 'poster.webp'), '-format', '%w %h', 'info:'], 30000)
  if (posterDimensions.trim() !== '1920 1080') throw new Error('The overview poster dimensions changed during conversion')
  const generatedTracks = tracks(document.scenes)
  await fs.writeFile(path.join(out, 'captions.vtt'), generatedTracks.captions, { flag: 'wx' })
  await fs.writeFile(path.join(out, 'chapters.vtt'), generatedTracks.chapters, { flag: 'wx' })
  const files = []
  for (const file of fileNames) {
    const bytes = await regularFile(path.join(out, file))
    files.push({ file, bytes: bytes.length, sha256: sha256(bytes), media_type: file.endsWith('.mp4') ? 'video/mp4' : file.endsWith('.webp') ? 'image/webp' : 'text/vtt' })
  }
  let start = 0
  const scenes = document.scenes.map(scene => {
    const result = { ...scene, start_seconds: start, end_seconds: start + scene.duration_seconds }
    if (scene.kind === 'video') {
      const source = inputRows.find(row => row.file === scene.media)
      result.source_end_seconds = Math.min(source.duration_seconds, scene.media_start_seconds + scene.duration_seconds)
      result.end_frame_hold_seconds = Math.max(0, scene.duration_seconds - (source.duration_seconds - scene.media_start_seconds))
      result.playback_rate = 1
    }
    start += scene.duration_seconds
    return result
  })
  const manifest = {
    schema_version: 1, complete: true, frontend: FRONTEND,
    scope: 'Captioned conceptual introduction and actual released frontend stills/clips rendered with reserved example data. No narration, live backend, provider account, media library or installation.',
    source_verification: 'The renderer checks the pinned packaged source identity and every used input hash. Immutable release-tag verification belongs to the capture procedure.',
    viewport: frame, duration_seconds: measuredDuration, planned_duration_seconds: duration,
    input_package_manifest_sha256: sha256(rawManifest), scene_document_sha256: sha256(scenesBytes), renderer_sha256: sha256(await fs.readFile(fileURLToPath(import.meta.url))), logo_sha256: sha256(logo),
    inputs: inputRows, scenes, files,
    recording: { raw_duration_seconds: rawDuration, leading_trim_seconds: trimStart, scene_timing: timings },
    encoding: { codec: 'h264', pixel_format: 'yuv420p', fps: 30, audio: false, faststart: true, maxrate_kbps: 1600 },
    errors: failures,
  }
  await fs.writeFile(path.join(out, 'manifest.json'), JSON.stringify(manifest, null, 2) + '\n', { flag: 'wx' })
  console.log(JSON.stringify({ complete: true, duration_seconds: measuredDuration, frontend: FRONTEND, files }, null, 2))
}

try { await main() } catch (error) {
  console.error('DUMB overview generation failed: ' + error.message)
  process.exitCode = 1
} finally { await cleanup() }
