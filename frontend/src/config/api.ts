/** Public API origin, compiled into the static bundle; never put secrets here. */
export function normalizeApiOrigin(value: string | undefined): string {
  if (!value?.trim()) return ''
  const url = new URL(value.trim())
  if (!['http:', 'https:'].includes(url.protocol) || url.username || url.password
    || url.pathname !== '/' || url.search || url.hash || /[;'"\s\\]/.test(url.origin)) {
    throw new Error('VITE_API_BASE_URL must be an HTTP(S) origin without credentials or path')
  }
  return url.origin
}

const origin = normalizeApiOrigin(import.meta.env.VITE_API_BASE_URL)
export const apiUrl = (path: string): string => `${origin}${path}`
