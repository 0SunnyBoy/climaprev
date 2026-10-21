import type { LocationCandidate, RiskResponse } from '@/types/api'

export const isRecord = (value: unknown): value is Record<string, unknown> =>
  value !== null && typeof value === 'object' && !Array.isArray(value)
export const isText = (value: unknown): value is string => typeof value === 'string'
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

export function isLocationCandidates(data: unknown): data is LocationCandidate[] {
  return Array.isArray(data) && data.every((item) => isRecord(item)
    && isText(item.name) && isNumber(item.latitude) && isNumber(item.longitude)
    && isText(item.timezone) && isText(item.source))
}
