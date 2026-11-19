// Numeric container/host counters only: no hostname, process list, identifiers,
// command lines, mount inventory, network addresses or service runtime files.
import fs from 'node:fs/promises'
import os from 'node:os'

const numberFile = async filename => {
  try {
    const value = (await fs.readFile(filename, 'utf8')).trim()
    return value !== 'max' && Number.isFinite(Number(value)) ? Number(value) : null
  } catch { return null }
}
const hostCpu = () => os.cpus().reduce((sum, cpu) => {
  sum.idle += cpu.times.idle
  sum.total += Object.values(cpu.times).reduce((total, value) => total + value, 0)
  return sum
}, { idle: 0, total: 0 })

export async function createMetricsTrace({ intervalMs = 500 } = {}) {
  const started = new Date().toISOString()
  const points = []
  const processes = new Map()
  let previous, sampling = false, timer
  let cpuLimit = os.availableParallelism()
  try {
    const [quota, period] = (await fs.readFile('/sys/fs/cgroup/cpu.max', 'utf8')).trim().split(/\s+/)
    if (quota !== 'max' && Number(quota) > 0 && Number(period) > 0) cpuLimit = Number(quota) / Number(period)
  } catch {}
  const memoryLimit = await numberFile('/sys/fs/cgroup/memory.max')
  const memoryTotal = memoryLimit || os.totalmem()
  let source = 'host counters (container has no readable cgroup counters)'
  const sample = async () => {
    if (sampling) return
    sampling = true
    try {
      const tick = performance.now()
      let usage
      try {
        const text = await fs.readFile('/sys/fs/cgroup/cpu.stat', 'utf8')
        usage = Number(/^usage_usec\s+(\d+)$/m.exec(text)?.[1])
      } catch {}
      const host = hostCpu()
      let cpu = null
      if (Number.isFinite(usage)) {
        source = 'Linux cgroup v2 numeric CPU and memory counters'
        if (previous?.usage !== undefined) cpu = (usage - previous.usage) / ((tick - previous.tick) * 1000 * cpuLimit) * 100
      } else if (previous?.host && host.total > previous.host.total) {
        cpu = (1 - (host.idle - previous.host.idle) / (host.total - previous.host.total)) * 100
      }
      const currentMemory = await numberFile('/sys/fs/cgroup/memory.current')
      let memoryUsed = currentMemory ?? os.totalmem() - os.freemem()
      if (currentMemory !== null) {
        try {
          const stat = await fs.readFile('/sys/fs/cgroup/memory.stat', 'utf8')
          const inactive = Number(/^inactive_file\s+(\d+)$/m.exec(stat)?.[1]) || 0
          memoryUsed = Math.max(0, memoryUsed - inactive)
        } catch {}
      }
      previous = { usage: Number.isFinite(usage) ? usage : undefined, tick, host }
      const processRows = []
      for (const [pid, entry] of processes) {
        try {
          const [stat, status] = await Promise.all([
            fs.readFile('/proc/' + pid + '/stat', 'utf8'),
            fs.readFile('/proc/' + pid + '/status', 'utf8'),
          ])
          const fields = stat.slice(stat.lastIndexOf(')') + 2).trim().split(/\s+/)
          const ticks = Number(fields[11]) + Number(fields[12])
          const rss = (Number(/^VmRSS:\s+(\d+)\s+kB$/m.exec(status)?.[1]) || 0) * 1024
          // Linux USER_HZ is 100; report a stable public alias, never the real PID.
          const cpu = entry.previous ? Math.max(0, (ticks - entry.previous.ticks) * 1000 / (tick - entry.previous.tick)) : 0
          entry.previous = { tick, ticks }
          processRows.push({ name: entry.alias, process_name: entry.alias, pid: entry.publicPid,
            status: 'running', cpu_percent: Math.round(cpu * 10) / 10, rss })
        } catch { /* A task-owned process can exit between samples. */ }
      }
      if (cpu !== null) points.push({
        elapsed_ms: Math.round(tick),
        cpu_percent: Math.round(Math.max(0, Math.min(100, cpu)) * 10) / 10,
        memory_percent: Math.round(Math.min(100, memoryUsed / memoryTotal * 100) * 10) / 10,
        memory_total: Math.round(memoryTotal / 1024 ** 2) * 1024 ** 2,
        memory_used: Math.round(memoryUsed / 1024 ** 2) * 1024 ** 2,
        processes: processRows,
      })
      if (points.length > 720) points.shift()
    } finally { sampling = false }
  }
  await sample()
  timer = setInterval(() => { void sample().catch(() => {}) }, intervalMs)
  return {
    points,
    get latest() { return points.at(-1) },
    watchProcess(pid, alias) {
      if (!Number.isSafeInteger(pid) || pid < 1 || !['DUMB Frontend', 'Documentation capture fixture'].includes(alias)) throw new Error('Only task-owned process aliases can be sampled')
      processes.set(pid, { alias, publicPid: alias === 'DUMB Frontend' ? 1001 : 1002 })
    },
    metadata() { return { source, observed_at: started, interval_ms: intervalMs, samples: points.length,
      fields: ['cpu_percent', 'memory_working_set_percent', 'task_owned_process_cpu_percent', 'task_owned_process_rss'],
      scope: 'Sampled capture container counters; example service identities and other API data remain simulated.' } },
    async close() { clearInterval(timer); while (sampling) await new Promise(resolve => setTimeout(resolve, 10)) },
  }
}
