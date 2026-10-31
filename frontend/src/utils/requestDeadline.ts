/** Bound a request's lifetime even when its transport ignores AbortSignal. */
export function createRequestDeadline(milliseconds: number, onTimeout: () => Error) {
  const controller = new AbortController()
  let rejectPending!: (reason: Error) => void
  let disposed = false
  const stopped = new Promise<never>((_, reject) => { rejectPending = reject })
  const timer = setTimeout(() => {
    rejectPending(onTimeout())
    controller.abort()
  }, milliseconds)

  function dispose() {
    disposed = true
    clearTimeout(timer)
  }

  function cancel() {
    if (disposed) return
    rejectPending(new DOMException('Cancelled', 'AbortError'))
    controller.abort()
    dispose()
  }

  return {
    signal: controller.signal,
    wait: <T>(request: Promise<T>): Promise<T> => Promise.race([request, stopped]),
    cancel,
    dispose,
  }
}
