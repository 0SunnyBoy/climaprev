/** Real cross-origin browser gate. Only the upstream weather provider is synthetic. */
import assert from 'node:assert/strict'
import { execFileSync } from 'node:child_process'
import { createHash, X509Certificate } from 'node:crypto'
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { get } from 'node:https'
import process from 'node:process'
import { pathToFileURL } from 'node:url'

const modulePath = process.env.PLAYWRIGHT_MODULE
const { chromium } = await import(modulePath ? pathToFileURL(modulePath).href : 'playwright')
const ca = readFileSync('.homolog/decoupling/ca.crt')
function tlsStatus(url, options = {}) {
  return new Promise((resolve, reject) => {
    get(url, options, response => { response.resume(); resolve(response.statusCode) }).on('error', reject)
  })
}
for (const url of ['https://localhost:8445/', 'https://localhost:8446/health/live']) {
  await assert.rejects(tlsStatus(url), /certificate|issuer|self.signed/i)
  assert.equal(await tlsStatus(url, { ca }), 200)
  await assert.rejects(tlsStatus(url, { ca, servername: 'wrong.invalid' }), /altname|hostname/i)
}
const cert = new X509Certificate(readFileSync('.homolog/decoupling/server.crt'))
const pin = createHash('sha256').update(cert.publicKey.export({ type: 'spki', format: 'der' })).digest('base64')
// Trust exactly this test leaf key in this temporary browser process. No global
// trust change or blanket ignoreHTTPSErrors. Chain/hostname checks above use Node TLS.
const browser = await chromium.launch({
  executablePath: process.env.BROWSER_EXECUTABLE,
  headless: true,
  args: [`--ignore-certificate-errors-spki-list=${pin}`],
})
const compose = ['compose', '-f', 'tests/docker/decoupling/compose.yaml']
const docker = (...args) => execFileSync('docker', [...compose, ...args], { encoding: 'utf8' })
const checks = []
let providerStopped = false
let apiStopped = false
try {
  const context = await browser.newContext()
  const page = await context.newPage()
  const requests = []
  const errors = []
  page.on('request', request => requests.push({ url: request.url(), method: request.method() }))
  page.on('pageerror', error => errors.push(String(error)))
  const day = new Date(Date.now() + 86400000).toISOString().slice(0, 10)
  async function prepare(latitude = '-1.4558') {
    const response = await page.goto('https://localhost:8445/', { waitUntil: 'networkidle' })
    assert.equal(response.status(), 200)
    assert.match(response.headers()['content-security-policy'], /connect-src 'self' https:\/\/localhost:8446/)
    await page.selectOption('#location-mode', 'coordinates')
    await page.fill('#latitude', latitude)
    await page.fill('#longitude', '-48.4902')
    await page.fill('#start_date', day)
  }
  docker('exec', '-T', 'redis', 'redis-cli', 'FLUSHDB')
  await prepare()
  const bounds = await page.locator('#start_date').evaluate(input => ({ first: input.min, last: input.max }))
  const expectedLast = new Date(`${bounds.first}T00:00:00Z`)
  expectedLast.setUTCDate(expectedLast.getUTCDate() + 6)
  assert.equal(bounds.last, expectedLast.toISOString().slice(0, 10))
  const invalid = await page.evaluate(async ({ first, last }) => {
    const dates = [new Date(`${first}T00:00:00Z`), new Date(`${last}T00:00:00Z`)]
    dates[0].setUTCDate(dates[0].getUTCDate() - 1)
    dates[1].setUTCDate(dates[1].getUTCDate() + 1)
    const statuses = []
    for (const date of dates) {
      const response = await fetch('https://localhost:8446/api/v1/risk', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ latitude: -1, longitude: -48, start_date: date.toISOString().slice(0, 10) }),
      })
      statuses.push({ status: response.status, code: (await response.json()).error.code })
    }
    return statuses
  }, bounds)
  assert.deepEqual(invalid, [{ status: 422, code: 'INVALID_PERIOD' }, { status: 422, code: 'INVALID_PERIOD' }])
  checks.push('UI date bounds match seven-date UTC window; API rejects past/outside dates as 422')
  // Exercise geocoding through the actual FastAPI endpoint too.
  await page.selectOption('#location-mode', 'city')
  await page.fill('#location_text', 'Belem')
  await page.locator('.location-suggestion').first().waitFor()
  await page.locator('#location_text').press('ArrowDown')
  assert(await page.locator('#location_text').getAttribute('aria-activedescendant'))
  await page.locator('#location_text').press('Escape')
  assert.equal(await page.locator('#location_text').getAttribute('aria-expanded'), 'false')
  assert.equal(await page.locator('#location_text').getAttribute('aria-activedescendant'), null)
  await page.fill('#location_text', 'Belem Para')
  await page.locator('.location-suggestion').first().waitFor()
  await page.locator('#location_text').press('ArrowDown')
  await page.locator('#location_text').press('Enter')
  assert.equal(await page.locator('#location_text').getAttribute('aria-expanded'), 'false')
  checks.push('city suggestions support arrow/Enter/Escape with valid ARIA state')
  await page.selectOption('#location-mode', 'coordinates')
  await page.fill('#latitude', '-1.4558')
  await page.fill('#longitude', '-48.4902')
  const success = page.waitForResponse(r => r.url() === 'https://localhost:8446/api/v1/risk'
    && r.request().method() === 'POST')
  await page.click('button[type=submit]')
  const successful = await success
  assert.equal(successful.status(), 200)
  const result = await successful.json()
  assert.equal(result.forecast_risk.policy_version, 'reference-v1')
  await page.locator('#result').waitFor()
  checks.push('real API geocoding + POST risk + visible result across HTTPS origins')
  await page.click('.emergency-nav-link')
  await page.waitForFunction(() => document.activeElement?.id === 'emergencia')
  await page.click('.brand')
  await page.waitForFunction(() => document.activeElement?.id === 'consulta')
  assert.equal(await page.inputValue('#start_date'), day)
  assert.equal(await page.inputValue('#latitude'), '-1.4558')
  assert(await page.locator('#result').isVisible())
  checks.push('emergency navigation preserves form/result and restores keyboard focus')
  for (const theme of ['light', 'dark']) {
    if (await page.locator('html').getAttribute('data-theme') !== theme) await page.click('.theme-toggle')
    await page.waitForFunction(theme => document.documentElement.dataset.theme === theme, theme)
    const contrast = await page.evaluate(() => {
      const style = getComputedStyle(document.documentElement)
      function luminance(variable) {
        const color = style.getPropertyValue(variable).trim().replace('#', '')
        const rgb = [0, 2, 4].map(index => parseInt(color.slice(index, index + 2), 16) / 255)
        const linear = rgb.map(value => value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4)
        return linear[0] * 0.2126 + linear[1] * 0.7152 + linear[2] * 0.0722
      }
      return [['--ink', '--paper'], ['--muted', '--paper'], ['--danger', '--surface'],
        ['--low-ink', '--low-bg'], ['--moderate-ink', '--moderate-bg'], ['--high-ink', '--high-bg']]
        .map(([front, back]) => {
          const a = luminance(front), b = luminance(back)
          return { front, back, ratio: (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05) }
        })
    })
    assert(contrast.every(pair => pair.ratio >= 4.5), JSON.stringify(contrast))
    await page.reload({ waitUntil: 'networkidle' })
    assert.equal(await page.locator('html').getAttribute('data-theme'), theme)
  }
  await page.click('.locale-toggle')
  assert.equal(await page.locator('html').getAttribute('lang'), 'en')
  await page.reload({ waitUntil: 'networkidle' })
  assert.equal(await page.locator('html').getAttribute('lang'), 'en')
  await page.click('.locale-toggle')
  for (const width of [320, 375, 768, 1280]) {
    await page.setViewportSize({ width, height: 900 })
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth))
  }
  await page.locator('.skip-link').focus()
  await page.keyboard.press('Enter')
  assert.equal(await page.evaluate(() => document.activeElement.id), 'consulta')
  checks.push('theme and locale persist; semantic text contrast >=4.5; keyboard skip and 320–1280px layout pass')
  assert(requests.some(r => r.url.startsWith('https://localhost:8446/api/v1/locations/search')))
  assert(!requests.some(r => r.url.startsWith('https://localhost:8445/api/')))
  const exposed = await page.evaluate(async () => {
    const response = await fetch('https://localhost:8446/health/live')
    return { id: response.headers.get('x-request-id'), status: response.status }
  })
  assert.equal(exposed.status, 200)
  assert(exposed.id)
  checks.push('CORS exposes request ID to JavaScript')
  const forbidden = await context.newPage()
  await forbidden.goto('https://localhost:8447/')
  const blocked = await forbidden.evaluate(async () => {
    try { await fetch('https://localhost:8446/health/live'); return false } catch { return true }
  })
  assert(blocked)
  await forbidden.close()
  checks.push('browser blocks API reads from an origin outside the CORS allowlist')

  docker('stop', '-t', '1', 'provider')
  providerStopped = true
  await prepare('-2.1234')
  const failed = page.waitForResponse(r => r.url() === 'https://localhost:8446/api/v1/risk'
    && r.request().method() === 'POST')
  await page.click('button[type=submit]')
  assert.equal((await failed).status(), 503)
  await page.locator('#query-status[role=alert]').waitFor()
  assert.match(await page.locator('#query-status').innerText(), /Referência:/)
  checks.push('provider failure travels through actual API as 503 and visible error/reference')
  docker('start', 'provider')
  providerStopped = false
  docker('exec', '-T', 'redis', 'redis-cli', 'FLUSHDB')
  const limited = await page.evaluate(async (date) => {
    for (let index = 0; index < 20; index++) {
      const response = await fetch('https://localhost:8446/api/v1/risk', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ latitude: -1.4558, longitude: -48.4902,
          start_date: date, end_date: date, temperature_unit: 'celsius' }),
      })
      if (response.status === 429) return {
        status: response.status, retry: response.headers.get('retry-after'),
        id: response.headers.get('x-request-id'),
      }
    }
    return null
  }, day)
  assert.equal(limited?.status, 429)
  assert(Number(limited.retry) > 0)
  assert(limited.id)
  await prepare()
  await page.click('button[type=submit]')
  await page.locator('.cooldown-countdown').waitFor()
  checks.push('real 429 exposes Retry-After/request ID and activates UI cooldown')
  docker('stop', '-t', '1', 'api')
  apiStopped = true
  await prepare()
  await page.click('button[type=submit]')
  await page.locator('#query-status[role=alert]').waitFor()
  assert((await page.locator('#query-status').innerText()).trim())
  checks.push('frontend remains available and shows an error while the API process is stopped')
  docker('start', 'api')
  apiStopped = false
  assert.deepEqual(errors, [])
  assert.deepEqual(await context.cookies(), [])
  mkdirSync('docs/operacoes/evidence', { recursive: true })
  writeFileSync('docs/operacoes/evidence/desacoplamento-browser-2026-10-20.json', JSON.stringify({
    status: 'passed', checks, origins: ['https://localhost:8445', 'https://localhost:8446'],
    untrustedOrigin: 'https://localhost:8447', browserVersion: browser.version(),
    tlsBrowserTrust: 'process-scoped explicit leaf SPKI pin; Node checks chain/hostname separately',
    tlsCaRejectionAndHostnameChecksPassed: true,
    apiMocked: false, upstreamWeatherProvider: 'deterministic synthetic fixture',
    externalProductionDeploymentValidated: false,
    sourceSha256: Object.fromEntries([
      'tests/docker/check_decoupled_browser.mjs', 'tests/docker/decoupling/compose.yaml',
      'tests/docker/decoupling/nginx.conf', 'tests/docker/decoupling/package-lock.json',
      'frontend/src/config/api.ts', 'frontend/src/services/api.ts', 'src/climaprev/main.py',
      'frontend/src/components/QueryForm.vue', 'frontend/src/utils/forecastWindow.ts',
      'src/climaprev/api/forecast_window.py', 'src/climaprev/api/routes/risk.py',
      'frontend/src/App.vue', 'frontend/styles.css', 'frontend/src/components/LocationAutocomplete.vue',
      'frontend/src/composables/useRiskQuery.ts',
    ].map(path => [path, createHash('sha256').update(readFileSync(path)).digest('hex')])),
  }, null, 2) + '\n')
  console.log(JSON.stringify({ checks, browser: browser.version() }))
  await context.close()
} finally {
  if (providerStopped) docker('start', 'provider')
  if (apiStopped) docker('start', 'api')
  await browser.close()
}
