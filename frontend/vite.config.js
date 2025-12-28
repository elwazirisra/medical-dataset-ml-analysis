import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5001',
        changeOrigin: true,
        // Backend is running on port 5002
        // Using 127.0.0.1 instead of localhost to force IPv4
      }
    }
  }
})

