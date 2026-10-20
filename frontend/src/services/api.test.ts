import { afterEach, describe, expect, it, vi } from 'vitest'
import { isRiskResponse, searchLocations } from './api'
import { emptyQueryForm, toRiskQueryPayload } from '@/types/query'

afterEach(() => vi.unstubAllGlobals())

describe('frontend API contract', () => {
  it('builds a city query without putting the location in a URL', () => {
    const form = emptyQueryForm()
    form.locationText = 'Belém, Pará'
    form.startDate = '2030-01-01'
    form.endDate = '2030-01-03'
    expect(toRiskQueryPayload(form)).toEqual({
      location_text: 'Belém, Pará',
      start_date: '2030-01-01',
      end_date: '2030-01-03',
      temperature_unit: 'celsius',
    })
  })

  it('validates the public risk response shape at the network boundary', () => {
    const response = {
      request_id: 'synthetic',
      disclaimer: 'Orientação',
      location: { name: 'Belém', latitude: -1.45, longitude: -48.49, timezone: 'America/Belem', source: 'geocoder' },
      period: { start_date: '2030-01-01', end_date: '2030-01-01' },
      temperature_unit: 'celsius',
      days: [{
        date: '2030-01-01', temperature_min: 20, temperature_max: 30, temperature_mean: 25,
        humidity_mean_pct: 70, precipitation_sum_mm: 0, precipitation_probability_max_pct: 10,
        precipitation_max_hourly_mm: 0, wind_max_kmh: 15, wind_gust_max_kmh: 20, weather_code: 1,
      }],
      forecast_risk: { level: 'low', method: 'forecast_heuristic', policy_version: 'reference-v1', conditions: [], peak_days: [], daily: [{ date: '2030-01-01', level: 'low', conditions: [] }] },
      risk_overview: { level: 'low', source: 'forecast_heuristic', peak_days: [] },
      data_quality: { is_stale: false, completeness: 'complete', missing_fields: [] },
      source: { provider: 'open-meteo', fetched_at: '2030-01-01T12:00:00Z' },
      official_alerts: { status: 'not_configured', items: [] },
    }
    expect(isRiskResponse(response)).toBe(true)
    expect(isRiskResponse({ ...response, request_id: 42 })).toBe(false)
  })

  it('não apresenta falha HTTP como busca sem resultados', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('unavailable', { status: 503 })))
    await expect(searchLocations('Belém')).rejects.toMatchObject({ status: 503 })
  })

  it('rejeita resposta inválida e aceita uma lista vazia válida', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify({ error: true })))
      .mockResolvedValueOnce(new Response('[]'))
    vi.stubGlobal('fetch', fetchMock)
    await expect(searchLocations('Belém')).rejects.toThrow()
    await expect(searchLocations('Belém')).resolves.toEqual([])
  })
})
