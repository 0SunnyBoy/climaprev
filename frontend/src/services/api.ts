import type {
  LocationCandidate,
  RiskQueryPayload,
  RiskResponse,
} from '@/types/api'

export class QueryError extends Error {
  readonly code: string
  readonly status: number
  readonly requestId: string
  readonly retryAfter: number

  constructor(code: string, options: { status?: number; requestId?: string; retryAfter?: number } = {}) {
    super(code)
    this.name = 'QueryError'
    this.code = code
    this.status = options.status ?? 0
    this.requestId = options.requestId ?? ''
    this.retryAfter = options.retryAfter ?? 60
  }
}

export class QueryTimeoutError extends Error {
  constructor() {
    super('QUERY_TIMEOUT')
    this.name = 'QueryTimeoutError'
  }
}

const isRecord = (value: unknown): value is Record<string, unknown> =>
  value !== null && typeof value === 'object' && !Array.isArray(value)
const isText = (value: unknown): value is string => typeof value === 'string'
const isNumber = (value: unknown): value is number => typeof value === 'number' && Number.isFinite(value)
const isNullableNumber = (value: unknown): value is number | null => value === null || isNumber(value)
const isTimestamp = (value: unknown): value is string => isText(value) && Number.isFinite(Date.parse(value))
const isStringArray = (value: unknown): value is string[] => Array.isArray(value) && value.every(isText)
const isRiskLevel = (value: unknown): value is 'low' | 'moderate' | 'high' =>
  ['low', 'moderate', 'high'].includes(String(value))

function isRiskCondition(value: unknown): boolean {
  return isRecord(value)
    && ['type', 'severity', 'unit', 'reason'].every((key) => isText(value[key]))
    && ['moderate', 'high'].includes(String(value.severity))
    && isNumber(value.value)
}

function isRiskDayAssessment(value: unknown): boolean {
  return isRecord(value)
    && isTimestamp(value.date)
    && isRiskLevel(value.level)
    && Array.isArray(value.conditions)
    && value.conditions.every(isRiskCondition)
}

const dayFields = [
  'temperature_min', 'temperature_max', 'temperature_mean', 'humidity_mean_pct',
  'precipitation_sum_mm', 'precipitation_probability_max_pct',
  'precipitation_max_hourly_mm', 'wind_max_kmh', 'wind_gust_max_kmh', 'weather_code',
] as const

export function isRiskResponse(data: unknown): data is RiskResponse {
  if (!isRecord(data)) return false
  const location = data.location
  const period = data.period
  const days = data.days
  const risk = data.forecast_risk
  const quality = data.data_quality
  const source = data.source
  const alerts = data.official_alerts
  return isText(data.request_id) && isText(data.disclaimer)
    && isRecord(location) && ['name', 'timezone', 'source'].every((key) => isText(location[key]))
    && isNumber(location.latitude) && isNumber(location.longitude)
    && isRecord(period) && isTimestamp(period.start_date) && isTimestamp(period.end_date)
    && ['celsius', 'fahrenheit'].includes(String(data.temperature_unit))
    && Array.isArray(days) && days.length > 0 && days.every((day) => isRecord(day)
      && isTimestamp(day.date) && dayFields.every((field) => isNullableNumber(day[field])))
    && isRecord(risk) && isRiskLevel(risk.level)
    && isText(risk.method) && isText(risk.policy_version)
    && Array.isArray(risk.conditions) && risk.conditions.every(isRiskCondition)
    && isStringArray(risk.peak_days)
    && Array.isArray(risk.daily) && risk.daily.every(isRiskDayAssessment)
    && isRecord(data.risk_overview)
    && isRiskLevel(data.risk_overview.level)
    && ['forecast_heuristic', 'official_alert'].includes(String(data.risk_overview.source))
    && isStringArray(data.risk_overview.peak_days)
    && isRecord(quality) && typeof quality.is_stale === 'boolean'
    && ['complete', 'partial', 'unavailable'].includes(String(quality.completeness))
    && isStringArray(quality.missing_fields)
    && isRecord(source) && isText(source.provider) && isTimestamp(source.fetched_at)
    && isRecord(alerts) && ['available', 'not_configured', 'unavailable'].includes(String(alerts.status))
    && Array.isArray(alerts.items) && alerts.items.every((item) => isRecord(item)
      && ['source', 'event', 'severity', 'geographic_scope'].every((key) => isText(item[key]))
      && isTimestamp(item.effective_at)
      && (item.expires_at === null || isTimestamp(item.expires_at))
      && (item.source_url === null || isText(item.source_url)))
}

function retryAfter(response: Response): number {
  const value = response.headers.get('Retry-After')
  const seconds = value && /^\d+$/.test(value) ? Number(value) : Number.NaN
  return Number.isSafeInteger(seconds) && seconds >= 0 ? seconds : 60
}

async function readJson(response: Response): Promise<unknown> {
  try {
    return await response.json()
  } catch {
    return undefined
  }
}

function errorFromResponse(response: Response, data: unknown): QueryError {
  const headerId = response.headers.get('X-Request-ID') ?? ''
  const error = isRecord(data) && isRecord(data.error) ? data.error : undefined
  const envelope = isText(error?.code) && isText(error?.request_id)
  return new QueryError(envelope ? String(error?.code) : 'MALFORMED_RESPONSE', {
    status: response.status,
    requestId: envelope ? String(error?.request_id) : headerId,
    retryAfter: retryAfter(response),
  })
}

export async function queryRisk(payload: RiskQueryPayload, signal?: AbortSignal): Promise<RiskResponse> {
  let response: Response
  try {
    response = await fetch('/api/v1/risk', {
      method: 'POST',
      signal,
      cache: 'no-store',
      credentials: 'omit',
      headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') throw error
    throw new QueryError('NETWORK_ERROR')
  }
  const data = await readJson(response)
  if (!response.ok) throw errorFromResponse(response, data)
  if (!isRiskResponse(data)) {
    throw new QueryError('MALFORMED_RESPONSE', {
      status: response.status,
      requestId: response.headers.get('X-Request-ID') ?? '',
    })
  }
  return data
}

export async function searchLocations(query: string, signal?: AbortSignal): Promise<LocationCandidate[]> {
  const response = await fetch(`/api/v1/locations/search?query=${encodeURIComponent(query)}`, {
    headers: { Accept: 'application/json' },
    cache: 'no-store',
    credentials: 'omit',
    signal,
  })
  if (!response.ok) return []
  const data: unknown = await response.json()
  if (!Array.isArray(data)) return []
  return data.filter((item): item is LocationCandidate => isRecord(item)
    && isText(item.name) && isNumber(item.latitude) && isNumber(item.longitude)
    && isText(item.timezone) && isText(item.source))
}
