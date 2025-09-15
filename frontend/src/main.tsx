import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { pwaManager } from './utils/pwa'

// Register service worker for PWA functionality
if (import.meta.env.PROD || import.meta.env.DEV) {
  pwaManager.registerServiceWorker().then((registered) => {
    if (registered) {
      console.log('✅ PWA Service Worker registered successfully');
    } else {
      console.log('❌ PWA Service Worker registration failed');
    }
  });
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
