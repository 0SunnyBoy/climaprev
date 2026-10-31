import { onBeforeUnmount, ref } from 'vue'
import { searchLocations } from '@/services/api'
import type { LocationCandidate } from '@/types/api'
import { createRequestDeadline } from '@/utils/requestDeadline'

export function useLocationSearch() {
  const suggestions = ref<LocationCandidate[]>([])
  const searching = ref(false)
  const failed = ref(false)
  const completed = ref(false)
  let timer: ReturnType<typeof setTimeout> | undefined
  let activeRequest: ReturnType<typeof createRequestDeadline> | undefined
  let sequence = 0

  function clear({ preserveFailure = false }: { preserveFailure?: boolean } = {}) {
    sequence += 1
    if (timer) clearTimeout(timer)
    activeRequest?.cancel()
    activeRequest = undefined
    timer = undefined
    searching.value = false
    suggestions.value = []
    failed.value = preserveFailure && failed.value
    completed.value = false
  }

  function schedule(query: string) {
    clear()
    const normalized = query.trim()
    if (normalized.length < 2) return
    const requestSequence = sequence
    searching.value = true
    timer = setTimeout(async () => {
      const request = createRequestDeadline(5000, () => new Error('Location search timed out'))
      activeRequest = request
      try {
        const result = await request.wait(searchLocations(normalized, request.signal))
        if (requestSequence === sequence) {
          suggestions.value = result
          completed.value = true
        }
      } catch (error) {
        if (requestSequence === sequence
          && !(error instanceof DOMException && error.name === 'AbortError')) {
          suggestions.value = []
          failed.value = true
        }
      } finally {
        request.dispose()
        if (requestSequence === sequence) {
          searching.value = false
          activeRequest = undefined
        }
      }
    }, 250)
  }

  onBeforeUnmount(clear)
  return { suggestions, searching, failed, completed, schedule, clear }
}
