import { mount } from '@vue/test-utils'
import { defineComponent } from 'vue'
import { afterEach, expect, it, vi } from 'vitest'
import { queryRisk, QueryTimeoutError } from '@/services/api'
import { CLIENT_QUERY_TIMEOUT_MS, useRiskQuery } from './useRiskQuery'

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
