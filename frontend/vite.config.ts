import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Serve service worker from public directory
    fs: {
      allow: ['..']
    },
    proxy: {
      // Proxy SEO-related requests to backend
      '/robots.txt': {
        target: 'http://backend:8000',
        changeOrigin: true,
        headers: {
          'Host': 'localhost:8000'
        }
      },
      '/sitemap.xml': {
        target: 'http://backend:8000',
        changeOrigin: true,
        headers: {
          'Host': 'localhost:8000'
        }
      },
      '/.well-known': {
        target: 'http://backend:8000',
        changeOrigin: true,
        headers: {
          'Host': 'localhost:8000'
        }
      },
      // API requests
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
        headers: {
          'Host': 'localhost:8000'
        }
      }
    }
  },
  // Ensure service worker is copied to dist
  publicDir: 'public'
})
