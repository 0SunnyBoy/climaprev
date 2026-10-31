import { mount } from '@vue/test-utils'
import { defineComponent } from 'vue'
import { afterEach, expect, it, vi } from 'vitest'
import { queryRisk, QueryTimeoutError } from '@/services/api'
import { CLIENT_QUERY_TIMEOUT_MS, useRiskQuery } from './useRiskQuery'
import type { RiskResponse } from '@/types/api'

vi.mock('@/services/api', async (original) => ({
  ...await original<typeof import('@/services/api')>(), queryRisk: vi.fn(),
}))

afterEach(() => { vi.useRealTimers(); vi.resetAllMocks() })
const payload = { latitude: -1, longitude: -48, start_date: '2026-10-20', temperature_unit: 'celsius' as const }

function setup() {
  let query!: ReturnType<typeof useRiskQuery>
  const wrapper = mount(defineComponent({ setup() { query = useRiskQuery(); return () => null } }))
  return { query, wrapper }
}

function abortableRequest() {
  vi.mocked(queryRisk).mockImplementation((_payload, signal) => new Promise((_resolve, reject) => {
    signal?.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError')), { once: true })
  }))
}

it('successful completion removes its deadline without a later timeout', async () => {
  vi.useFakeTimers()
  const response = { request_id: 'success' } as RiskResponse
  vi.mocked(queryRisk).mockResolvedValue(response)
  const { query, wrapper } = setup()
  try {
    expect(await query.submit(payload)).toEqual(response)
    expect(query.loading.value).toBe(false)
    expect(vi.getTimerCount()).toBe(0)
    await vi.advanceTimersByTimeAsync(CLIENT_QUERY_TIMEOUT_MS + 1)
    expect(query.result.value).toEqual(response)
    expect(query.timedOut.value).toBe(false)
    expect(query.error.value).toBeNull()
  } finally { wrapper.unmount() }
})

it('timeout settles even when transport ignores abort and discards late success', async () => {
  vi.useFakeTimers()
  let resolveLate!: (value: RiskResponse) => void
  vi.mocked(queryRisk).mockImplementation(() => new Promise((resolve) => { resolveLate = resolve }))
  const { query, wrapper } = setup()
  try {
    const pending = query.submit(payload)
    await vi.advanceTimersByTimeAsync(CLIENT_QUERY_TIMEOUT_MS)
    expect(await pending).toBeNull()
    expect(query.loading.value).toBe(false)
    expect(query.error.value).toBeInstanceOf(QueryTimeoutError)
    resolveLate({ request_id: 'late' } as RiskResponse)
    await Promise.resolve()
    expect(query.result.value).toBeNull()
    expect(vi.getTimerCount()).toBe(0)
  } finally { wrapper.unmount() }
})

it('cancel settles a transport that ignores abort without becoming a timeout', async () => {
  vi.useFakeTimers()
  vi.mocked(queryRisk).mockImplementation(() => new Promise(() => {}))
  const { query, wrapper } = setup()
  try {
    const pending = query.submit(payload)
    query.cancel()
    expect(await pending).toBeNull()
    await vi.advanceTimersByTimeAsync(CLIENT_QUERY_TIMEOUT_MS + 1)
    expect(query.loading.value).toBe(false)
    expect(query.timedOut.value).toBe(false)
    expect(query.error.value).toBeNull()
    expect(vi.getTimerCount()).toBe(0)
  } finally { wrapper.unmount() }
})

it('superseded request completion cannot clear the next request deadline', async () => {
  vi.useFakeTimers()
  abortableRequest()
  const { query, wrapper } = setup()
  try {
    const first = query.submit(payload)
    const second = query.submit(payload)
    await first
    await vi.advanceTimersByTimeAsync(CLIENT_QUERY_TIMEOUT_MS)
    await second
    expect(query.error.value).toBeInstanceOf(QueryTimeoutError)
    expect(query.timedOut.value).toBe(true)
    expect(query.loading.value).toBe(false)
  } finally { wrapper.unmount() }
})

it('explicit cancel clears its deadline and does not later become a timeout', async () => {
  vi.useFakeTimers()
  abortableRequest()
  const { query, wrapper } = setup()
  try {
    const pending = query.submit(payload)
    query.cancel()
    await pending
    await vi.advanceTimersByTimeAsync(CLIENT_QUERY_TIMEOUT_MS + 1)
    expect(query.timedOut.value).toBe(false)
    expect(query.error.value).toBeNull()
    expect(query.loading.value).toBe(false)
  } finally { wrapper.unmount() }
})

it('unmount aborts the active request and removes its timer', async () => {
  vi.useFakeTimers()
  abortableRequest()
  const { query, wrapper } = setup()
  const pending = query.submit(payload)
  wrapper.unmount()
  await pending
  expect(vi.getTimerCount()).toBe(0)
})
