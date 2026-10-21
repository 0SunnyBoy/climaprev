import type {
  LocationCandidate,
  RiskQueryPayload,
  RiskResponse,
} from '@/types/api'
import { apiUrl } from '@/config/api'
import { isLocationCandidates, isRecord, isRiskResponse, isText } from './responseValidation'

export { isRiskResponse } from './responseValidation'

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
    response = await fetch(apiUrl('/api/v1/risk'), {
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
  const response = await fetch(apiUrl(`/api/v1/locations/search?query=${encodeURIComponent(query)}`), {
    headers: { Accept: 'application/json' },
    cache: 'no-store',
    credentials: 'omit',
    signal,
  })
  if (!response.ok) throw new QueryError('SEARCH_UNAVAILABLE', { status: response.status })
  const data: unknown = await response.json()
  if (!isLocationCandidates(data)) throw new QueryError('MALFORMED_RESPONSE')
  return data
}
