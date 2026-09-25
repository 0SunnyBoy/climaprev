import { fileURLToPath, URL } from 'node:url'

import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [vue()],
  server: {
    strictPort: true,
    watch: { usePolling: true },
    proxy: {
      '/api/v1/risk': { target: 'http://app:8000', changeOrigin: true },
      '/api/v1/locations/search': { target: 'http://app:8000', changeOrigin: true },
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
})
