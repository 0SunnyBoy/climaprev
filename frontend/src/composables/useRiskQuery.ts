import { onBeforeUnmount, ref } from 'vue'
import { queryRisk, QueryTimeoutError } from '@/services/api'
import type { RiskQueryPayload, RiskResponse } from '@/types/api'
import { createRequestDeadline } from '@/utils/requestDeadline'

export const CLIENT_QUERY_TIMEOUT_MS = 10_000

export function useRiskQuery() {
  const result = ref<RiskResponse | null>(null)
  const loading = ref(false)
  const timedOut = ref(false)
  const error = ref<unknown>(null)
  let activeRequest: ReturnType<typeof createRequestDeadline> | undefined
  let sequence = 0

  async function submit(payload: RiskQueryPayload): Promise<RiskResponse | null> {
    const requestSequence = ++sequence
    activeRequest?.cancel()
    loading.value = true
    timedOut.value = false
    error.value = null
    result.value = null
    const request = createRequestDeadline(CLIENT_QUERY_TIMEOUT_MS, () => {
      timedOut.value = true
      return new QueryTimeoutError()
    })
    activeRequest = request
    try {
      const response = await request.wait(queryRisk(payload, request.signal))
      if (requestSequence !== sequence) return null
      result.value = response
      return response
    } catch (caught) {
      if (requestSequence !== sequence) return null
      if (timedOut.value) error.value = new QueryTimeoutError()
      else if (caught instanceof DOMException && caught.name === 'AbortError') return null
      else error.value = caught
      return null
    } finally {
      request.dispose()
      if (requestSequence === sequence) {
        activeRequest = undefined
        loading.value = false
      }
    }
  }

  function cancel() {
    sequence += 1
    activeRequest?.cancel()
    activeRequest = undefined
    loading.value = false
  }

  onBeforeUnmount(cancel)
  return { result, loading, timedOut, error, submit, cancel }
}
