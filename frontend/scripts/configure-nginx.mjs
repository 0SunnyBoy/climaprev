import { readFileSync, writeFileSync } from 'node:fs'
import process from 'node:process'
import { URL } from 'node:url'

const value = process.env.VITE_API_BASE_URL?.trim() || ''
let config = readFileSync('nginx.conf', 'utf8')
if (value) {
  const url = new URL(value)
  if (!['http:', 'https:'].includes(url.protocol) || url.username || url.password
    || url.pathname !== '/' || url.search || url.hash || /[;'"\s\\]/.test(url.origin)) {
    throw new Error('VITE_API_BASE_URL must be an HTTP(S) origin without credentials or path')
  }
  config = config.replace("connect-src 'self'", `connect-src 'self' ${url.origin}`)
  // Direct API calls need no Docker backend name or reverse-proxy routes.
  config = config.replace(/ {8}location = \/(?:api\/v1\/(?:risk|locations\/search)|health\/(?:live|ready)) \{[\s\S]*?\n {8}\}/g, '')
  if (config.includes('proxy_pass')) throw new Error('Unexpected proxy remains in standalone configuration')
}
writeFileSync('nginx.generated.conf', config)
