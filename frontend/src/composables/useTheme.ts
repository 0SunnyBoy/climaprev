import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

export type Theme = 'light' | 'dark'

const STORAGE_KEY = 'climaprev-theme'

function readStoredTheme(): Theme | null {
  if (typeof window === 'undefined') return null
  try {
    const stored = window.localStorage.getItem(STORAGE_KEY)
    return stored === 'light' || stored === 'dark' ? stored : null
  } catch {
    return null
  }
}

function systemTheme(): Theme {
  return typeof window !== 'undefined'
    && typeof window.matchMedia === 'function'
    && window.matchMedia('(prefers-color-scheme: dark)').matches
    ? 'dark'
    : 'light'
}

function applyTheme(theme: Theme) {
  if (typeof document === 'undefined') return
  document.documentElement.dataset.theme = theme
}

export function useTheme() {
  const theme = ref<Theme>(readStoredTheme() ?? systemTheme())
  let mediaQuery: MediaQueryList | undefined
  let transitionTimer: ReturnType<typeof setTimeout> | undefined

  applyTheme(theme.value)

  function setTheme(nextTheme: Theme, persist = true, animate = false) {
    theme.value = nextTheme
    if (animate && typeof document !== 'undefined' && typeof window !== 'undefined') {
      document.documentElement.classList.add('theme-transition')
      window.requestAnimationFrame(() => applyTheme(nextTheme))
      if (transitionTimer) clearTimeout(transitionTimer)
      transitionTimer = setTimeout(() => {
        document.documentElement.classList.remove('theme-transition')
        transitionTimer = undefined
      }, 380)
    } else {
      applyTheme(nextTheme)
    }
    if (!persist || typeof window === 'undefined') return
    try {
      window.localStorage.setItem(STORAGE_KEY, nextTheme)
    } catch {
      // A blocked storage should not prevent the theme from changing.
    }
  }

  function toggleTheme() {
    setTheme(theme.value === 'dark' ? 'light' : 'dark', true, true)
  }

  function followSystemTheme(event: MediaQueryListEvent) {
    if (!readStoredTheme()) setTheme(event.matches ? 'dark' : 'light', false)
  }

  onMounted(() => {
    if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') return
    mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    mediaQuery.addEventListener('change', followSystemTheme)
  })

  onBeforeUnmount(() => {
    mediaQuery?.removeEventListener('change', followSystemTheme)
    if (transitionTimer) clearTimeout(transitionTimer)
  })

  return {
    theme,
    isDark: computed(() => theme.value === 'dark'),
    toggleTheme,
  }
}
