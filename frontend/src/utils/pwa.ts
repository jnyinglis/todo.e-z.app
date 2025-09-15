// PWA utilities for service worker registration and app install prompt
import React from 'react';

interface BeforeInstallPromptEvent extends Event {
  readonly platforms: string[];
  readonly userChoice: Promise<{
    outcome: 'accepted' | 'dismissed';
    platform: string;
  }>;
  prompt(): Promise<void>;
}

declare global {
  interface WindowEventMap {
    beforeinstallprompt: BeforeInstallPromptEvent;
  }
}

class PWAManager {
  private deferredPrompt: BeforeInstallPromptEvent | null = null;
  private isInstallable = false;
  private isInstalled = false;

  constructor() {
    this.init();
  }

  private init() {
    // Check if app is already installed
    this.checkInstallStatus();

    // Listen for beforeinstallprompt event
    window.addEventListener('beforeinstallprompt', (e) => {
      console.log('PWA install prompt available');
      // Prevent the mini-infobar from appearing
      e.preventDefault();
      // Save the event for later use
      this.deferredPrompt = e;
      this.isInstallable = true;

      // Dispatch custom event to notify components
      window.dispatchEvent(new CustomEvent('pwa-installable', {
        detail: { installable: true }
      }));
    });

    // Listen for app installed event
    window.addEventListener('appinstalled', () => {
      console.log('PWA was installed');
      this.isInstalled = true;
      this.isInstallable = false;
      this.deferredPrompt = null;

      // Dispatch custom event
      window.dispatchEvent(new CustomEvent('pwa-installed'));
    });
  }

  private checkInstallStatus() {
    // Check if running in standalone mode (PWA installed)
    if (window.matchMedia('(display-mode: standalone)').matches) {
      this.isInstalled = true;
    }

    // Check for iOS Safari standalone mode
    if ((window.navigator as Navigator & { standalone?: boolean }).standalone === true) {
      this.isInstalled = true;
    }
  }

  async showInstallPrompt(): Promise<boolean> {
    if (!this.deferredPrompt) {
      console.log('No install prompt available');
      return false;
    }

    try {
      // Show the install prompt
      await this.deferredPrompt.prompt();

      // Wait for the user's response
      const choiceResult = await this.deferredPrompt.userChoice;

      if (choiceResult.outcome === 'accepted') {
        console.log('User accepted the install prompt');
        return true;
      } else {
        console.log('User dismissed the install prompt');
        return false;
      }
    } catch (error) {
      console.error('Error showing install prompt:', error);
      return false;
    } finally {
      // Clear the deferred prompt
      this.deferredPrompt = null;
      this.isInstallable = false;
    }
  }

  getInstallable(): boolean {
    return this.isInstallable;
  }

  getInstalled(): boolean {
    return this.isInstalled;
  }

  async registerServiceWorker(): Promise<boolean> {
    if ('serviceWorker' in navigator) {
      try {
        console.log('Registering service worker...');

        const registration = await navigator.serviceWorker.register('/sw.js', {
          scope: '/'
        });

        console.log('Service Worker registered successfully:', registration);

        // Handle updates
        registration.addEventListener('updatefound', () => {
          console.log('New service worker version found');
          const newWorker = registration.installing;

          if (newWorker) {
            newWorker.addEventListener('statechange', () => {
              if (newWorker.state === 'installed') {
                if (navigator.serviceWorker.controller) {
                  // New update available
                  console.log('New content available; please refresh');

                  // Dispatch custom event for UI notification
                  window.dispatchEvent(new CustomEvent('pwa-update-available', {
                    detail: { registration }
                  }));
                } else {
                  // Content is cached for the first time
                  console.log('Content is cached for offline use');

                  // Dispatch custom event
                  window.dispatchEvent(new CustomEvent('pwa-content-cached'));
                }
              }
            });
          }
        });

        return true;
      } catch (error) {
        console.error('Service Worker registration failed:', error);
        return false;
      }
    } else {
      console.log('Service Workers not supported');
      return false;
    }
  }

  async updateServiceWorker(): Promise<void> {
    if ('serviceWorker' in navigator) {
      const registration = await navigator.serviceWorker.getRegistration();
      if (registration) {
        await registration.update();

        // If there's a waiting worker, activate it
        if (registration.waiting) {
          registration.waiting.postMessage({ type: 'SKIP_WAITING' });
        }

        // Reload the page to use the new service worker
        window.location.reload();
      }
    }
  }

  async checkConnectivity(): Promise<boolean> {
    if (!navigator.onLine) {
      return false;
    }

    try {
      // Try to fetch a small resource to verify connectivity
      const response = await fetch('/api/health', {
        method: 'HEAD',
        cache: 'no-cache'
      });
      return response.ok;
    } catch {
      return false;
    }
  }

  // Request persistent storage (for large apps with lots of cached data)
  async requestPersistentStorage(): Promise<boolean> {
    if ('storage' in navigator && 'persist' in navigator.storage) {
      try {
        const granted = await navigator.storage.persist();
        console.log('Persistent storage granted:', granted);
        return granted;
      } catch (error) {
        console.error('Error requesting persistent storage:', error);
        return false;
      }
    }
    return false;
  }

  // Get storage usage (useful for cache management)
  async getStorageEstimate(): Promise<StorageEstimate | null> {
    if ('storage' in navigator && 'estimate' in navigator.storage) {
      try {
        const estimate = await navigator.storage.estimate();
        console.log('Storage estimate:', estimate);
        return estimate;
      } catch (error) {
        console.error('Error getting storage estimate:', error);
        return null;
      }
    }
    return null;
  }
}

// Create singleton instance
export const pwaManager = new PWAManager();

// React hook for PWA functionality
export function usePWA() {
  const [isInstallable, setIsInstallable] = React.useState(pwaManager.getInstallable());
  const [isInstalled, setIsInstalled] = React.useState(pwaManager.getInstalled());
  const [updateAvailable, setUpdateAvailable] = React.useState(false);
  const [isOnline, setIsOnline] = React.useState(navigator.onLine);

  React.useEffect(() => {
    // Listen for PWA events
    const handleInstallable = () => setIsInstallable(true);
    const handleInstalled = () => {
      setIsInstalled(true);
      setIsInstallable(false);
    };
    const handleUpdateAvailable = () => setUpdateAvailable(true);
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('pwa-installable', handleInstallable);
    window.addEventListener('pwa-installed', handleInstalled);
    window.addEventListener('pwa-update-available', handleUpdateAvailable);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('pwa-installable', handleInstallable);
      window.removeEventListener('pwa-installed', handleInstalled);
      window.removeEventListener('pwa-update-available', handleUpdateAvailable);
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const installApp = async () => {
    const success = await pwaManager.showInstallPrompt();
    if (success) {
      setIsInstallable(false);
    }
    return success;
  };

  const updateApp = async () => {
    await pwaManager.updateServiceWorker();
    setUpdateAvailable(false);
  };

  return {
    isInstallable,
    isInstalled,
    updateAvailable,
    isOnline,
    installApp,
    updateApp,
    checkConnectivity: pwaManager.checkConnectivity,
    requestPersistentStorage: pwaManager.requestPersistentStorage,
    getStorageEstimate: pwaManager.getStorageEstimate
  };
}

// Export for non-React usage
export default pwaManager;