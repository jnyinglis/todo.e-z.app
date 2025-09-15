import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Serve service worker from public directory
    fs: {
      allow: ['..']
    }
  },
  // Ensure service worker is copied to dist
  publicDir: 'public'
})
