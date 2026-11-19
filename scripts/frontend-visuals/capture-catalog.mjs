import fs from 'node:fs/promises'
import { createHash } from 'node:crypto'

export const sha256 = bytes => createHash('sha256').update(bytes).digest('hex')
const catalogBytes = await fs.readFile(new URL('./capture-catalog.json', import.meta.url))
const datasetBytes = await fs.readFile(new URL('./dataset.json', import.meta.url))
export const catalog = JSON.parse(catalogBytes)
export const dataset = JSON.parse(datasetBytes)
export const catalogHash = sha256(catalogBytes)
export const datasetHash = sha256(datasetBytes)
export const scenarioById = new Map(catalog.scenarios.map(scenario => [scenario.id, scenario]))
const canonical = value => Array.isArray(value) ? value.map(canonical)
  : value && typeof value === 'object' ? Object.fromEntries(Object.keys(value).sort().map(key => [key, canonical(value[key])])) : value
export function canonicalPlanHash(plan) {
  const { plan_sha256, ...unsigned } = plan
  return sha256(JSON.stringify(canonical(unsigned)))
}

export function validatePlan(plan) {
  if (plan.plan_sha256 !== canonicalPlanHash(plan)) throw new Error('Capture plan canonical SHA-256 does not match its contents')
  if (plan.schema_version !== 1 || !['release', 'dev'].includes(plan.channel)) throw new Error('A versioned release/dev capture plan is required')
  for (const component of ['frontend', 'backend']) {
    const identity = plan[component]
    if (!identity || !/^[0-9a-f]{40}$/.test(identity.commit || '')
      || !/^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$/.test(identity.version || '')
      || typeof identity.ref !== 'string' || !identity.ref
      || typeof identity.repository !== 'string' || !identity.repository.startsWith('https://github.com/')) {
      throw new Error('The plan needs an immutable ' + component + ' source identity')
    }
    if (plan.channel === 'release' && (typeof identity.tag !== 'string' || identity.tag.replace(/^v/, '') !== identity.version)) throw new Error('Released source needs an exact version tag')
    if (plan.channel === 'dev' && identity.tag) throw new Error('Development source must not be presented as a released tag')
  }
  if (plan.catalog_sha256 !== catalogHash || plan.dataset_sha256 !== datasetHash) throw new Error('Capture catalog/dataset hashes differ from the reviewed plan')
  for (const field of ['tooling_sha256', 'capability_source_sha256']) {
    if (!/^[0-9a-f]{64}$/.test(plan[field] || '')) throw new Error('Missing source fingerprint: ' + field)
  }
  if (!plan.capabilities || typeof plan.capabilities !== 'object' || Array.isArray(plan.capabilities)) throw new Error('Verified backend capabilities are required')
  for (const field of ['scenarios', 'required_scenarios']) {
    if (!Array.isArray(plan[field]) || new Set(plan[field]).size !== plan[field].length
      || plan[field].some(id => !scenarioById.has(id))) throw new Error('Invalid scenario list: ' + field)
  }
  if (!plan.scenarios.length || plan.required_scenarios.some(id => !plan.scenarios.includes(id))) throw new Error('Required scenarios must belong to the capture plan')
  for (const id of plan.scenarios) {
    const scenario = scenarioById.get(id)
    const gates = [...(scenario.required_capabilities || []), ...Object.keys(scenario.required_protocols || {})]
    if (gates.some(key => plan.unresolved_capabilities?.includes(key))) throw new Error('A required backend capability or protocol could not be resolved from source')
  }
  if (!Array.isArray(plan.themes) || !plan.themes.length || new Set(plan.themes).size !== plan.themes.length
    || plan.themes.some(theme => !['light', 'dark'].includes(theme))) throw new Error('Plan themes must be light and/or dark')
  return plan
}

export async function readPlan(filename) {
  const bytes = await fs.readFile(filename)
  const plan = validatePlan(JSON.parse(bytes))
  return { plan, planHash: plan.plan_sha256 }
}

export function unavailableReason(scenario, plan) {
  const unavailable = (scenario.required_capabilities || []).filter(key => plan.capabilities[key] !== true)
  for (const [key, expected] of Object.entries(scenario.required_protocols || {})) {
    if (plan.capabilities[key] !== expected) unavailable.push(key + '=' + JSON.stringify(expected))
  }
  if (unavailable.length) return 'Verified backend source does not advertise: ' + unavailable.join(', ')
  return null
}
