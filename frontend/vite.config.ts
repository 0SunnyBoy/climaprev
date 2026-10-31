import { fileURLToPath, URL } from 'node:url'

import vue from '@vitejs/plugin-vue'
import { defineConfig, loadEnv } from 'vite'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const target = env.API_PROXY_TARGET || 'http://127.0.0.1:8000'
  return {
  plugins: [vue()],
  server: {
    strictPort: true,
    watch: { usePolling: true },
    proxy: {
      '/api/v1/risk': { target, changeOrigin: true },
      '/api/v1/locations/search': { target, changeOrigin: true },
    },
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    sourcemap: false,
  },
  }
})
