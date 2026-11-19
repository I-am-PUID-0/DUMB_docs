import { setTimeout as delay } from 'node:timers/promises'
import { runUtilityScenario, utilityScenarios } from './utility-scenarios.mjs'

const utilityIds = new Set(utilityScenarios.map(scenario => scenario.id))

export class CaptureBlocked extends Error {}

const settings = {
  'settings-appearance': ['Appearance', 'appearance'],
  'settings-about': ['About', 'about'],
  'settings-tokens': ['Tokens', 'tokens'],
  'settings-log-timestamps': ['Log Timestamp Format', 'log-timestamp'],
  'settings-embedded-uis': ['Embedded UIs', 'embedded-uis'],
  'settings-authentication': ['Authentication', 'authentication'],
  'settings-auth-provider': ['Authentication', 'authentication'],
  'settings-notifications': ['Notifications', 'notifications'],
  'settings-backups': ['Backups and restore', 'backups'],
  'settings-advanced': ['Advanced', 'advanced'],
  'settings-support': ['Support', 'support'],
  'settings-onboarding': ['Onboarding', 'onboarding'],
  'settings-contributors': ['Contributors', 'contributors'],
}
export function settingsSectionId(id) { return settings[id]?.[1] }

async function isolateSettings(page, label, id, ui) {
  const buttons = page.locator('button[aria-controls^="settings-section-"]')
  for (const button of await buttons.all()) {
    if (await button.getAttribute('aria-expanded') === 'true'
      && await button.getAttribute('aria-controls') !== 'settings-section-' + id) await button.click()
  }
  return ui.settingsSection(page, label, id)
}

async function onboardingStage(page) {
  const headings = await page.getByRole('heading', { level: 2 }).allTextContents()
  if (headings.some(text => /Review Configuration|Review your setup/.test(text))) return 'review'
  if (headings.some(text => /Preflight Checks/.test(text))) return 'preflight'
  if (headings.some(text => /Debrid Service/.test(text))) return 'provider'
  if (headings.some(text => /Optional Services|Companion services/.test(text))) return 'companions'
  if (headings.some(text => /Embedded Service iFrames/.test(text))) return 'embedded-uis'
  if (headings.some(text => /Installation choices/.test(text))) return 'installation'
  if (headings.some(text => /Configure.+Options/.test(text))) return 'options'
  return 'services'
}

async function walkOnboarding(page, target, ui, frontendVersion, fixture) {
  await page.getByRole('heading', { name: 'Onboarding Wizard', exact: true }).waitFor()
  let selectedService = 'riven_backend'
  if (target === 'companions' && frontendVersion === '1.91.0') {
    // The released 1.91 wizard's provider watcher advances again when its old
    // provider component loses the selected entry. Use its real provider-free
    // workflow to show the otherwise skipped companion step, without changing
    // the application, its DOM, or the required capture coverage.
    selectedService = 'infinidysk'
  }
  let chosen = false
  for (let step = 0; step < 24; step++) {
    await page.getByText('Loading step…', { exact: true }).waitFor({ state: 'hidden' })
    const stage = await onboardingStage(page)
    ui.chapter(page, 'Onboarding: ' + stage)
    if (stage === 'services' && !chosen) {
      const expand = page.getByRole('button', { name: 'Expand all', exact: true })
      if (await expand.count()) await expand.click()
      const service = page.locator('input[type="checkbox"][value="' + selectedService + '"]').first()
      await service.waitFor()
      if (selectedService === 'infinidysk') ui.chapter(page, 'Choose InfiniDysk for the released companion-service example')
      await ui.focusControl(page, service)
      await service.check()
      chosen = true
    }
    if (stage === 'provider') {
      await page.getByRole('radio', { name: 'RealDebrid', exact: true }).check()
      await page.getByPlaceholder('Enter API key', { exact: true }).fill('EXAMPLE-NOT-A-REAL-KEY')
    }
    if (stage === target || stage === 'review' && ['progress', 'result', 'error'].includes(target)) {
      if (['progress', 'result', 'error'].includes(target)) {
        let start = page.getByRole('button', { name: 'Start services', exact: true })
        // The released legacy wizard advances from Review to its log view
        // before exposing Start. Follow its actual controls and timer.
        if (!await start.count()) await ui.hoverClick(page, page.getByRole('button', { name: 'Next', exact: true }))
        start = page.getByRole('button', { name: 'Start services', exact: true })
        await start.waitFor()
        ui.chapter(page, 'Show the simulated setup ' + target + ' state')
        const operationStart = fixture.state.exampleOperations.length
        await start.click()
        // The Review screen can still contain words such as "failed" while
        // its asynchronous submit is starting. Require the intended isolated
        // operation before accepting any terminal UI state.
        const deadline = performance.now() + 15000
        let operation
        while (performance.now() < deadline && !operation) {
          operation = fixture.state.exampleOperations.slice(operationStart).find(row => row.profile === 'onboarding-' + target
            && ['in_memory_simulated_setup_run', 'in_memory_simulated_legacy_setup'].includes(row.operation))
          if (!operation) await delay(100)
        }
        if (!operation) throw new Error('The intended in-memory setup simulation was not accepted; an arbitrary error view is not a successful capture')
        if (target === 'result') {
          if (operation.operation === 'in_memory_simulated_setup_run') {
            await page.locator('[data-setup-status]').getByRole('status').filter({ hasText: /^Needs your input$/ }).waitFor({ timeout: 45000 })
          } else {
            await page.getByRole('heading', { name: /All set|Startup request finished/i }).first().waitFor({ timeout: 45000 })
          }
        } else if (target === 'error') {
          if (operation.operation === 'in_memory_simulated_setup_run') {
            await page.locator('[data-setup-status]').getByRole('status').filter({ hasText: /^Setup failed$/ }).waitFor()
          } else {
            await page.getByRole('heading', { name: 'Something went wrong', exact: true }).waitFor()
          }
        } else {
          await delay(2100)
        }
        if (target === 'error' && operation.path === '/api/process/start-core-service'
          && !fixture.state.expectedFailures.some(row => row.profile === 'onboarding-error' && row.path === operation.path && row.status === 400)) {
          throw new Error('The legacy error view did not come from the intended simulated400 response')
        }
      }
      await page.getByRole('heading', { name: 'Onboarding Wizard', exact: true }).scrollIntoViewIfNeeded()
      await delay(500)
      return
    }
    if (stage === 'review') throw new CaptureBlocked('The selected immutable frontend does not expose onboarding stage: ' + target)
    const next = page.getByRole('button', { name: /^(Next|Review setup|Continue setup)$/ }).first()
    await next.waitFor()
    if (!await next.isEnabled()) throw new Error('The real onboarding wizard blocked Next at ' + stage + '; example data or choices need review')
    const previousHeadings = (await page.locator('main').getByRole('heading', { level: 2 }).allTextContents()).map(text => text.replace(/\s+/g, ' ').trim()).join('\n')
    await ui.hoverClick(page, next)
    // Suspense can retain the previous async component while the next loads.
    // A fixed delay could click Next twice and silently skip a required view.
    await page.waitForFunction(previous => {
      const visible = element => element.getClientRects().length > 0 && getComputedStyle(element).visibility !== 'hidden'
      const headings = [...document.querySelectorAll('main h2')].filter(visible).map(element => element.textContent.replace(/\s+/g, ' ').trim()).join('\n')
      const loading = [...document.querySelectorAll('main p, main div')].some(element => visible(element) && element.textContent.trim() === 'Loading step…')
      return Boolean(headings) && headings !== previous && !loading
    }, previousHeadings, { timeout: 20000 })
  }
  throw new Error('The real onboarding wizard did not reach ' + target)
}

export async function runScenario({ page, scenario, theme, ui, fixture, prerequisites, plan }) {
  const id = scenario.id
  if (utilityIds.has(id)) return runUtilityScenario({ page, scenario, ui })
  if (settings[id]) {
    const [label, sectionId] = settings[id]
    const section = await isolateSettings(page, label, sectionId, ui)
    ui.chapter(page, 'Review ' + label)
    if (id === 'settings-auth-provider') {
      const provider = section.getByRole('heading', { name: 'Sign-in provider', exact: true })
      await provider.waitFor()
      const mode = section.getByLabel(/^Authentication mode/)
      const hybrid = mode.locator('option[value="hybrid"]')
      await mode.selectOption(await hybrid.count() ? 'hybrid' : 'oidc')
      await provider.evaluate(element => element.scrollIntoView({ block: 'start', inline: 'nearest' }))
    } else if (id === 'settings-appearance') {
      await ui.hoverClick(page, section.getByRole('button', { name: theme === 'light' ? /^Light(?:\s+check)?$/ : /^Dark(?:\s+check)?$/ }))
    }
    return
  }
  if (id.startsWith('onboarding-')) return walkOnboarding(page, id.slice('onboarding-'.length), ui, plan.frontend.version, fixture)
  if (id.startsWith('ai-provider')) {
    const summary = page.locator('summary').filter({ hasText: 'Provider settings' }).first()
    await summary.waitFor()
    if (!await summary.locator('..').evaluate(element => element.open)) await ui.hoverClick(page, summary)
    const provider = id.slice('ai-provider-'.length)
    const select = summary.locator('..').locator('select')
      .filter({ has: page.locator('option[value="ollama"]') })
      .filter({ has: page.locator('option[value="openai"]') })
      .filter({ has: page.locator('option[value="gemini"]') })
    await select.waitFor({ state: 'visible' })
    if (['openai', 'gemini'].includes(provider)) {
      await select.selectOption(provider)
    }
    if (provider === 'openai') {
      // Switching the real form retains the example Ollama model. Leave this
      // unsaved provider-specific draft empty rather than imply it is valid
      // for OpenAI or invent a remotely verified model selection.
      await summary.locator('..').getByPlaceholder('Model name', { exact: true }).fill('')
    }
    // Align the real provider form, rather than the disclosure summary above
    // the saved-profile controls, so endpoint/model/key fields remain legible.
    await select.evaluate(element => element.closest('label').scrollIntoView({ block: 'start', inline: 'nearest' }))
    return
  }
  switch (id) {
    case 'dashboard':
      await page.getByRole('heading', { name: 'Service Dashboard', exact: true }).waitFor()
      await page.locator('div[data-service-name="Sonarr"]').first().waitFor()
      return
    case 'realtime-logs':
      await page.getByRole('heading', { name: 'Real-Time Logs', exact: true }).waitFor()
      await page.getByText('Documentation example: capture transport is isolated; no production services were contacted.', { exact: false }).first().waitFor()
      {
        const hideSidebar = page.getByRole('button', { name: 'Hide sidebar', exact: true })
        if (await hideSidebar.isVisible()) await ui.hoverClick(page, hideSidebar)
      }
      return
    case 'settings-overview':
      for (const button of await page.locator('button[aria-controls^="settings-section-"]').all()) {
        if (await button.getAttribute('aria-expanded') === 'true') await button.click()
      }
      await page.getByRole('button', { name: /^Appearance\b/ }).first().scrollIntoViewIfNeeded()
      return
    case 'service-controls':
      await ui.serviceReady(page)
      return
    case 'api-configuration':
      await page.getByText('DUMB Config', { exact: true }).first().waitFor()
      return
    case 'configuration':
      await ui.serviceReady(page)
      ui.chapter(page, 'Review settings managed by DUMB')
      await ui.focusControl(page, page.getByText('DUMB Config', { exact: true }).first())
      await ui.hoverClick(page, page.getByText('Service Config', { exact: true }).first())
      ui.chapter(page, 'Return to DUMB configuration')
      await ui.hoverClick(page, page.getByText('DUMB Config', { exact: true }).first())
      await ui.focusControl(page, page.getByRole('button', { name: /Save to File\b/ }).first())
      return
    case 'service-logs': {
      await ui.serviceReady(page)
      ui.chapter(page, 'Open Service Logs')
      await ui.hoverClick(page, page.getByText('Service Logs', { exact: true }).first())
      const filter = page.getByPlaceholder('Enter text to filter logs', { exact: true })
      await filter.waitFor()
      await ui.focusControl(page, filter)
      await filter.pressSequentially('Example Series', { delay: 100 })
      await delay(1200)
      const levels = page.locator('select').filter({ has: page.locator('option[value="WARNING"]') }).first()
      await ui.focusControl(page, levels)
      await levels.selectOption('WARNING')
      await delay(1800)
      await levels.selectOption('')
      const refresh = page.locator('select').filter({ has: page.locator('option[value="5000"]') }).first()
      ui.chapter(page, 'Pause automatic refresh')
      await ui.focusControl(page, refresh)
      await refresh.selectOption('5000')
      await delay(1600)
      await refresh.selectOption('0')
      const follow = page.getByLabel('Follow tail', { exact: true })
      await ui.focusControl(page, follow)
      await follow.uncheck()
      return
    }
    case 'updates':
      await ui.serviceReady(page)
      await ui.serviceTool(page, 'Updates')
      ui.chapter(page, 'Check for updates without installing')
      await ui.hoverClick(page, page.getByRole('button', { name: /Check for updates\b/i }))
      await page.getByText('4.0.1', { exact: true }).waitFor()
      await ui.focusControl(page, page.getByText('4.0.1', { exact: true }), 2200)
      return
    case 'dependencies':
      await ui.serviceReady(page)
      await ui.serviceTool(page, 'Dependencies')
      await page.getByText('Startup order:', { exact: true }).waitFor()
      await ui.focusControl(page, page.getByText('Startup order:', { exact: true }), 2200)
      await ui.hoverClick(page, page.getByRole('button', { name: 'Flow', exact: true }))
      await page.getByTitle('Close Dependency graph panel.', { exact: true }).locator('..').locator('svg').first().waitFor()
      return
    case 'auto-restart': {
      await ui.serviceReady(page)
      await ui.serviceTool(page, 'Auto-restart')
      const panel = page.getByRole('heading', { name: 'Auto-restart Settings', exact: true }).locator('../../..')
      await panel.waitFor()
      await ui.focusControl(page, panel.getByLabel('Enable auto-restart', { exact: true }), 2200)
      await ui.focusControl(page, panel.getByText('Healthcheck threshold', { exact: true }).first(), 2200)
      const serviceToggle = panel.getByLabel('Enable auto-restart for Sonarr', { exact: true })
      await serviceToggle.evaluate(element => element.closest('label').scrollIntoView({ block: 'center', inline: 'nearest' }))
      await ui.focusControl(page, serviceToggle, 2200)
      return
    }
    case 'disabled-services': {
      const tools = page.getByRole('button', { name: /Sidebar tools/ }).first()
      const disabled = page.getByText('Show Disabled', { exact: true }).locator('..').locator('input[type=checkbox]')
      if (!await disabled.isVisible()) await tools.click()
      await disabled.check()
      await page.getByPlaceholder('Filter services...', { exact: true }).fill('Tautulli')
      await page.getByText('Tautulli', { exact: true }).first().waitFor()
      return
    }
    case 'metrics':
      await page.getByRole('heading', { name: 'Metrics', exact: true }).waitFor()
      await fixture.waitForMetrics()
      await page.reload({ waitUntil: 'networkidle' })
      await page.getByLabel('History', { exact: true }).uncheck()
      await page.getByText('DUMB Frontend', { exact: true }).last().waitFor()
      return
    case 'ai-overview':
      await page.getByRole('heading', { name: 'Stack AI Assist', exact: true }).waitFor()
      await page.getByRole('button', { name: /Preview evidence/ }).waitFor()
      return
    case 'login':
      await page.getByRole('button', { name: /Sign [Ii]n|Log [Ii]n/ }).first().waitFor()
      return
    case 'account-setup':
      await page.getByRole('button', { name: /Create Account/ }).waitFor()
      return
    case 'setup-connections':
      await page.locator('[data-setup-walkthrough], [data-setup-checklist], [data-setup-status]').first().waitFor()
      return
    case 'embedded-sonarr': {
      if (!prerequisites.sonarr) throw new CaptureBlocked('Actual isolated Sonarr application was not supplied; no replacement screen will be used')
      await ui.serviceReady(page)
      await ui.hoverClick(page, page.getByText('Embedded UI', { exact: true }).first())
      const iframe = page.frameLocator('iframe').first()
      await iframe.getByText('Series', { exact: true }).first().waitFor()
      return
    }
    default:
      throw new CaptureBlocked('No reviewed packaged-frontend scenario handler exists for ' + id)
  }
}
