import { onBeforeUnmount, ref } from 'vue'
import { queryRisk, QueryTimeoutError } from '@/services/api'
import type { RiskQueryPayload, RiskResponse } from '@/types/api'

export function useRiskQuery() {
  const result = ref<RiskResponse | null>(null)
  const loading = ref(false)
  const timedOut = ref(false)
  const error = ref<unknown>(null)
  let controller: AbortController | undefined
  let timeout: ReturnType<typeof setTimeout> | undefined
  let sequence = 0

  async function submit(payload: RiskQueryPayload): Promise<RiskResponse | null> {
    const requestSequence = ++sequence
    controller?.abort()
    if (timeout) clearTimeout(timeout)
    controller = new AbortController()
    loading.value = true
    timedOut.value = false
    error.value = null
    result.value = null
    const activeController = controller
    timeout = setTimeout(() => {
      timedOut.value = true
      activeController.abort()
    }, 10_000)
    try {
      const response = await queryRisk(payload, activeController.signal)
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
      if (timeout) clearTimeout(timeout)
      if (requestSequence === sequence) loading.value = false
    }
  }

  function cancel() {
    sequence += 1
    controller?.abort()
    if (timeout) clearTimeout(timeout)
    loading.value = false
  }

  onBeforeUnmount(cancel)
  return { result, loading, timedOut, error, submit, cancel }
}
