import { onBeforeUnmount, ref } from 'vue'
import { searchLocations } from '@/services/api'
import type { LocationCandidate } from '@/types/api'

export function useLocationSearch() {
  const suggestions = ref<LocationCandidate[]>([])
  const searching = ref(false)
  let timer: ReturnType<typeof setTimeout> | undefined
  let controller: AbortController | undefined
  let sequence = 0

  function clear() {
    sequence += 1
    if (timer) clearTimeout(timer)
    controller?.abort()
    timer = undefined
    controller = undefined
    searching.value = false
    suggestions.value = []
  }

  function schedule(query: string) {
    clear()
    const normalized = query.trim()
    if (normalized.length < 2) return
    const requestSequence = sequence
    searching.value = true
    timer = setTimeout(async () => {
      controller = new AbortController()
      try {
        const result = await searchLocations(normalized, controller.signal)
        if (requestSequence === sequence) suggestions.value = result
      } catch (error) {
        if (!(error instanceof DOMException && error.name === 'AbortError')) suggestions.value = []
      } finally {
        if (requestSequence === sequence) searching.value = false
      }
    }, 250)
  }

  onBeforeUnmount(clear)
  return { suggestions, searching, schedule, clear }
}
