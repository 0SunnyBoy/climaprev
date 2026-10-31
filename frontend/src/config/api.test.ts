import { afterEach, describe, expect, it, vi } from 'vitest'
import { normalizeApiOrigin } from './api'

afterEach(() => { vi.unstubAllEnvs(); vi.resetModules() })

describe('independent API deployment', () => {
  it('keeps same-origin default and normalizes external origins', () => {
    expect(normalizeApiOrigin('')).toBe('')
    expect(normalizeApiOrigin(' https://api.example/ ')).toBe('https://api.example')
  })

  it.each(['javascript:alert(1)', 'https://user:pass@api.example', 'https://api.example/path',
    'https://api.example/?token=x', 'https://api.example/#fragment', "https://a'b.example"])('rejects invalid origin %s', (value) => {
    expect(() => normalizeApiOrigin(value)).toThrow()
  })

  it('routes real search requests to the configured API', async () => {
    vi.stubEnv('VITE_API_BASE_URL', 'https://api.example')
    vi.resetModules()
    const fetchMock = vi.fn().mockResolvedValue(new Response('[]'))
    vi.stubGlobal('fetch', fetchMock)
    const { searchLocations } = await import('../services/api')
    await searchLocations('Belém')
    expect(fetchMock.mock.calls[0]?.[0]).toBe('https://api.example/api/v1/locations/search?query=Bel%C3%A9m')
    vi.unstubAllGlobals()
  })
})
