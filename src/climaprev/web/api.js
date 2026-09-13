const fields = ['location_text', 'latitude', 'longitude', 'start_date', 'end_date', 'temperature_unit'];

export class QueryError extends Error {
  constructor(code, {status = 0, requestId = '', retryAfter = 60} = {}) {
    super(code);
    this.code = code;
    this.status = status;
    this.requestId = requestId;
    this.retryAfter = retryAfter;
  }
}

export function queryParameters(formData) {
  const query = new URLSearchParams();
  for (const field of fields) {
    const value = formData.get(field);
    if (typeof value === 'string' && value.trim()) query.set(field, value.trim());
  }
  return query;
}

const record = value => value !== null && typeof value === 'object' && !Array.isArray(value);
const text = value => typeof value === 'string';
const number = value => typeof value === 'number' && Number.isFinite(value);
const nullableNumber = value => value === null || number(value);
const timestamp = value => text(value) && Number.isFinite(Date.parse(value));
const strings = value => Array.isArray(value) && value.every(text);
const dayNumbers = ['temperature_min', 'temperature_max', 'temperature_mean', 'humidity_mean_pct', 'precipitation_sum_mm', 'precipitation_probability_max_pct', 'precipitation_max_hourly_mm', 'wind_max_kmh', 'wind_gust_max_kmh', 'weather_code'];

function validResult(data) {
  return record(data) && text(data.request_id) && text(data.disclaimer)
    && record(data.location) && ['name','timezone','source'].every(key => text(data.location[key]))
    && number(data.location.latitude) && number(data.location.longitude)
    && record(data.period) && timestamp(data.period.start_date) && timestamp(data.period.end_date)
    && ['celsius','fahrenheit'].includes(data.temperature_unit)
    && Array.isArray(data.days) && data.days.length > 0 && data.days.every(day => record(day) && timestamp(day.date) && dayNumbers.every(key => nullableNumber(day[key])))
    && record(data.forecast_risk) && ['low','moderate','high'].includes(data.forecast_risk.level)
    && text(data.forecast_risk.method) && text(data.forecast_risk.policy_version)
    && Array.isArray(data.forecast_risk.conditions) && data.forecast_risk.conditions.every(item => record(item) && ['type','severity','unit','reason'].every(key => text(item[key])) && number(item.value))
    && record(data.data_quality) && typeof data.data_quality.is_stale === 'boolean'
    && ['complete','partial','unavailable'].includes(data.data_quality.completeness) && strings(data.data_quality.missing_fields)
    && record(data.source) && text(data.source.provider) && timestamp(data.source.fetched_at)
    && record(data.official_alerts) && ['available','not_configured','unavailable'].includes(data.official_alerts.status)
    && Array.isArray(data.official_alerts.items) && data.official_alerts.items.every(item => record(item) && ['source','event','severity','geographic_scope'].every(key => text(item[key])) && timestamp(item.effective_at) && (item.expires_at === null || timestamp(item.expires_at)) && (item.source_url === null || text(item.source_url)));
}

export async function queryRisk(formData, {signal} = {}) {
  let response;
  try {
    response = await fetch(`/api/v1/risk?${queryParameters(formData)}`, {
      method: 'GET', signal, cache: 'no-store', credentials: 'omit', headers: {Accept: 'application/json'},
    });
  } catch (error) {
    if (error.name === 'AbortError') throw error;
    throw new QueryError('NETWORK_ERROR');
  }
  const headerId = response.headers.get('X-Request-ID') || '';
  const rawRetry = response.headers.get('Retry-After');
  const seconds = rawRetry && /^\d+$/.test(rawRetry) ? Number(rawRetry) : NaN;
  const retryAfter = Number.isSafeInteger(seconds) && seconds >= 0 ? seconds : 60;
  let data;
  try { data = await response.json(); }
  catch { throw new QueryError('MALFORMED_RESPONSE', {status: response.status, requestId: headerId, retryAfter}); }
  if (!response.ok) {
    const envelope = record(data) && record(data.error) && text(data.error.code) && text(data.error.request_id);
    throw new QueryError(envelope ? data.error.code : 'MALFORMED_RESPONSE', {
      status: response.status, requestId: envelope ? data.error.request_id : headerId,
      retryAfter,
    });
  }
  if (!validResult(data)) throw new QueryError('MALFORMED_RESPONSE', {status: response.status, requestId: headerId});
  return data;
}
