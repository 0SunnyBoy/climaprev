import type { RiskQueryPayload, TemperatureUnit } from './api'

export type LocationMode = 'city' | 'coordinates'

export interface QueryFormState {
  locationMode: LocationMode
  locationText: string
  latitude: string
  longitude: string
  startDate: string
  endDate: string
  temperatureUnit: TemperatureUnit
}

export function emptyQueryForm(): QueryFormState {
  return {
    locationMode: 'city',
    locationText: '',
    latitude: '',
    longitude: '',
    startDate: '',
    endDate: '',
    temperatureUnit: 'celsius',
  }
}

export function toRiskQueryPayload(form: QueryFormState): RiskQueryPayload {
  const payload: RiskQueryPayload = {
    start_date: form.startDate,
    temperature_unit: form.temperatureUnit,
  }
  if (form.locationMode === 'city') payload.location_text = form.locationText.trim()
  else {
    payload.latitude = Number(form.latitude)
    payload.longitude = Number(form.longitude)
  }
  if (form.endDate.trim()) payload.end_date = form.endDate
  return payload
}
