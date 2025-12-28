import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL?.replace('/api', '') || 'http://127.0.0.1:5000',
        changeOrigin: true,
        // In development, proxy to local backend
        // In production, VITE_API_URL should point to deployed backend
      }
    }
  },
  build: {
    outDir: 'dist',
  }
})

