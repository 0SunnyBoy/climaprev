export type TemperatureUnit = 'celsius' | 'fahrenheit'
export type RiskLevel = 'low' | 'moderate' | 'high'
export type DataCompleteness = 'complete' | 'partial' | 'unavailable'
export type OfficialAlertsStatus = 'available' | 'not_configured' | 'unavailable'

export interface RiskQueryPayload {
  location_text?: string
  latitude?: number
  longitude?: number
  start_date: string
  end_date?: string
  temperature_unit: TemperatureUnit
}

export interface LocationCandidate {
  name: string
  latitude: number
  longitude: number
  timezone: string
  source: string
}

export interface Location {
  name: string
  latitude: number
  longitude: number
  timezone: string
  source: string
}

export interface ForecastPeriod {
  start_date: string
  end_date: string
}

export interface ForecastDay {
  date: string
  temperature_min: number | null
  temperature_max: number | null
  temperature_mean: number | null
  humidity_mean_pct: number | null
  precipitation_sum_mm: number | null
  precipitation_probability_max_pct: number | null
  precipitation_max_hourly_mm: number | null
  wind_max_kmh: number | null
  wind_gust_max_kmh: number | null
  weather_code: number | null
}

export interface RiskCondition {
  type: string
  severity: 'moderate' | 'high'
  value: number
  unit: string
  reason: string
}

export interface ForecastRisk {
  level: RiskLevel
  method: string
  policy_version: string
  conditions: RiskCondition[]
  peak_days: string[]
  daily: RiskDayAssessment[]
}

export interface RiskDayAssessment {
  date: string
  level: RiskLevel
  conditions: RiskCondition[]
}

export interface RiskOverview {
  level: RiskLevel
  source: 'forecast_heuristic' | 'official_alert'
  peak_days: string[]
}

export interface DataQuality {
  is_stale: boolean
  missing_fields: string[]
  completeness: DataCompleteness
}

export interface ForecastSource {
  provider: string
  fetched_at: string
}

export interface OfficialAlert {
  source: string
  event: string
  severity: string
  effective_at: string
  expires_at: string | null
  geographic_scope: string
  source_url: string | null
}

export interface OfficialAlerts {
  status: OfficialAlertsStatus
  items: OfficialAlert[]
}

export interface RiskResponse {
  request_id: string
  location: Location
  period: ForecastPeriod
  temperature_unit: TemperatureUnit
  days: ForecastDay[]
  forecast_risk: ForecastRisk
  risk_overview: RiskOverview
  data_quality: DataQuality
  source: ForecastSource
  official_alerts: OfficialAlerts
  disclaimer: string
}

export interface ErrorEnvelope {
  error?: {
    code?: unknown
    request_id?: unknown
  }
}
