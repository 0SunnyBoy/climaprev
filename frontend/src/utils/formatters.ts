import type { ForecastDay, TemperatureUnit } from '@/types/api'
import type { Locale } from '@/composables/useLocale'

export const riskLevels: Record<string, string> = { low: 'Baixo', moderate: 'Moderado', high: 'Alto' }
export const units: Record<string, string> = { celsius: '°C', fahrenheit: '°F', 'mm/day': 'mm/dia' }
export const conditionNames: Record<string, string> = {
  heavy_rain_proxy: 'Chuva intensa',
  flooding_risk_proxy: 'Sinal de risco de alagamento',
  strong_wind_proxy: 'Vento forte',
  temperature_extreme_proxy: 'Temperatura extrema',
}

export type ForecastMetricKey = Exclude<keyof ForecastDay, 'date'> & string

export const measurements: Array<[ForecastMetricKey, string, string]> = [
  ['temperature_min', 'Temperatura mínima', 'temperature'],
  ['temperature_max', 'Temperatura máxima', 'temperature'],
  ['temperature_mean', 'Temperatura média', 'temperature'],
  ['humidity_mean_pct', 'Umidade média', '%'],
  ['precipitation_sum_mm', 'Chuva acumulada', 'mm'],
  ['precipitation_probability_max_pct', 'Probabilidade de chuva', '%'],
  ['precipitation_max_hourly_mm', 'Chuva máxima por hora', 'mm/h'],
  ['wind_max_kmh', 'Vento máximo', 'km/h'],
  ['wind_gust_max_kmh', 'Rajada máxima', 'km/h'],
  ['weather_code', 'Código meteorológico', ''],
]

function numberFormat(locale: Locale): Intl.NumberFormat {
  return new Intl.NumberFormat(locale, { maximumFractionDigits: 1 })
}

export function formatDate(value: string, locale: Locale = 'pt-BR'): string {
  return new Intl.DateTimeFormat(locale, { timeZone: 'UTC' }).format(new Date(`${value}T12:00:00Z`))
}

export function formatWeekday(value: string, locale: Locale = 'pt-BR'): string {
  return new Intl.DateTimeFormat(locale, { weekday: 'long', timeZone: 'UTC' })
    .format(new Date(`${value}T12:00:00Z`))
}

export function formatDateTime(value: string, zone: string, locale: Locale = 'pt-BR'): string {
  return new Intl.DateTimeFormat(locale, { dateStyle: 'short', timeStyle: 'short', timeZone: zone })
    .format(new Date(value))
}

export function formatValue(number: number | null, unit = '', locale: Locale = 'pt-BR'): string {
  return number === null ? (locale === 'en' ? 'Not available' : 'Não disponível') : `${numberFormat(locale).format(number)}${unit ? ` ${unit}` : ''}`
}

export function temperatureUnit(unit: TemperatureUnit): string {
  return units[unit]
}

export function missingLabel(field: string, locale: Locale = 'pt-BR'): string {
  const day = field.match(/\d{4}-\d{2}-\d{2}/)?.[0]
  const normalizedField = field.replace(/_c$/, '')
  const measure = measurements.find(([key]) => normalizedField.endsWith(key))
  const label = field.includes('precipitation.coverage') ? 'Cobertura horária de chuva' : measure?.[1] ?? field
  return `${label}${day ? ` · ${formatDate(day, locale)}` : ''}`
}
