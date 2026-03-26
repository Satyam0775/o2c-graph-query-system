import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],

  // ✅ Local dev only (kept)
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },

  // ✅ Fix warning (optional but clean)
  build: {
    chunkSizeWarningLimit: 1000,
  },
})
