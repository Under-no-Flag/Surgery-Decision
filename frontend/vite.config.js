import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0', // Ensure vite listens on all interfaces in container
    proxy: {
      '/api': {
        target: process.env.API_TARGET || 'http://backend:5000',
        changeOrigin: true
      }
    }
  }
})
