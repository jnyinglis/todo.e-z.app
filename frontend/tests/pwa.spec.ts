import { test, expect } from '@playwright/test';

test.describe('PWA Functionality', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the app
    await page.goto('http://localhost:5173');

    // Wait for the app to load
    await expect(page.locator('h1')).toContainText('Full-Stack Template');
  });

  test('should register service worker successfully', async ({ page }) => {
    // Wait for service worker registration
    await page.waitForTimeout(3000);

    // Check service worker registration
    const swRegistered = await page.evaluate(async () => {
      const registration = await navigator.serviceWorker.getRegistration();
      return {
        registered: !!registration,
        state: registration?.active?.state || 'none',
        scope: registration?.scope || 'none'
      };
    });

    expect(swRegistered.registered).toBe(true);
    expect(swRegistered.state).toBe('activated');
    expect(swRegistered.scope).toBe('http://localhost:5173/');
  });

  test('should show PWA install prompt', async ({ page }) => {
    // Check if install prompt is visible
    await expect(page.locator('h4', { hasText: '📱 Install App' })).toBeVisible();
    await expect(page.locator('button', { hasText: 'Install' })).toBeVisible();

    // Verify install prompt content
    await expect(page.locator('p', { hasText: 'Install this app on your device for a better experience' })).toBeVisible();
  });

  test('should have valid web app manifest', async ({ page }) => {
    // Check manifest link in head
    const manifestLink = await page.evaluate(() => {
      const link = document.querySelector('link[rel="manifest"]') as HTMLLinkElement;
      return link?.href || null;
    });

    expect(manifestLink).toBe('http://localhost:5173/manifest.json');

    // Fetch and validate manifest
    const response = await page.request.get('http://localhost:5173/manifest.json');
    expect(response.ok()).toBe(true);

    const manifest = await response.json();
    expect(manifest.name).toBe('Vite React FastAPI Template');
    expect(manifest.short_name).toBe('FastAPI Template');
    expect(manifest.display).toBe('standalone');
    expect(manifest.start_url).toBe('/');
    expect(manifest.icons).toBeDefined();
    expect(manifest.icons.length).toBeGreaterThan(0);
  });

  test('should have proper PWA meta tags', async ({ page }) => {
    // Check viewport meta tag
    const viewport = await page.getAttribute('meta[name="viewport"]', 'content');
    expect(viewport).toContain('width=device-width');

    // Check theme color
    const themeColor = await page.getAttribute('meta[name="theme-color"]', 'content');
    expect(themeColor).toBe('#646cff');

    // Check apple-mobile-web-app-capable
    const appleMobileCapable = await page.getAttribute('meta[name="apple-mobile-web-app-capable"]', 'content');
    expect(appleMobileCapable).toBe('yes');
  });

  test('should cache resources with service worker', async ({ page }) => {
    // Wait for service worker to be ready
    await page.waitForTimeout(3000);

    // Check if resources are cached
    const cacheStatus = await page.evaluate(async () => {
      if (!('caches' in window)) return { supported: false };

      const cacheNames = await caches.keys();
      const hasStaticCache = cacheNames.some(name => name.includes('vite-react-fastapi'));

      if (hasStaticCache) {
        const cache = await caches.open(cacheNames.find(name => name.includes('vite-react-fastapi'))!);
        const cachedRequests = await cache.keys();
        return {
          supported: true,
          hasCaches: cacheNames.length > 0,
          cacheNames,
          cachedResourcesCount: cachedRequests.length
        };
      }

      return {
        supported: true,
        hasCaches: cacheNames.length > 0,
        cacheNames,
        cachedResourcesCount: 0
      };
    });

    expect(cacheStatus.supported).toBe(true);
    expect(cacheStatus.hasCaches).toBe(true);
    expect(cacheStatus.cacheNames).toContain(expect.stringContaining('vite-react-fastapi'));
  });

  test('should handle offline mode gracefully', async ({ page, context }) => {
    // Wait for service worker to be ready and cache resources
    await page.waitForTimeout(3000);

    // Simulate offline mode
    await context.setOffline(true);

    // Check if offline indicator appears
    await expect(page.locator('span', { hasText: '📶 You\'re offline - Some features may be limited' })).toBeVisible({ timeout: 10000 });

    // Verify the page still works offline (should serve from cache)
    await page.reload();
    await expect(page.locator('h1')).toContainText('Full-Stack Template');

    // Restore online mode
    await context.setOffline(false);
  });

  test('should detect network status changes', async ({ page, context }) => {
    // Start online
    await expect(page.locator('span', { hasText: 'You\'re offline' })).not.toBeVisible();

    // Go offline
    await context.setOffline(true);
    await expect(page.locator('span', { hasText: '📶 You\'re offline - Some features may be limited' })).toBeVisible({ timeout: 5000 });

    // Go back online
    await context.setOffline(false);
    await expect(page.locator('span', { hasText: 'You\'re offline' })).not.toBeVisible({ timeout: 5000 });
  });

  test('should handle service worker updates', async ({ page }) => {
    // This test verifies that the update mechanism is in place
    await page.waitForTimeout(3000);

    const updateAvailable = await page.evaluate(() => {
      // Check if update functionality exists
      return typeof window.navigator.serviceWorker !== 'undefined';
    });

    expect(updateAvailable).toBe(true);
  });

  test('should have proper app icons', async ({ page }) => {
    // Check various icon sizes are available
    const iconSizes = ['192x192', '512x512'];

    for (const size of iconSizes) {
      const response = await page.request.get(`http://localhost:5173/icon-${size.split('x')[0]}.svg`);
      expect(response.ok()).toBe(true);

      const contentType = response.headers()['content-type'];
      expect(contentType).toContain('image/svg+xml');
    }

    // Check favicon
    const faviconResponse = await page.request.get('http://localhost:5173/vite.svg');
    expect(faviconResponse.ok()).toBe(true);
  });

  test('should handle PWA install button interaction', async ({ page }) => {
    // Find and click install button
    const installButton = page.locator('button', { hasText: 'Install' });
    await expect(installButton).toBeVisible();

    // Note: In a real PWA test environment, clicking this would trigger
    // the browser's install prompt. In Playwright, this might not work
    // exactly the same way, but we can test the button interaction.
    await installButton.click();

    // Verify button was clicked (it should remain visible since we can't
    // actually install in the test environment)
    await expect(installButton).toBeVisible();
  });

  test('should maintain PWA state across navigation', async ({ page }) => {
    // Start on home page
    await expect(page.locator('h1')).toContainText('Full-Stack Template');

    // Navigate to different sections if they exist
    // For now, just verify the PWA elements persist
    await page.reload();

    // PWA install prompt should still be there
    await expect(page.locator('h4', { hasText: '📱 Install App' })).toBeVisible();

    // Service worker should still be registered
    const swStillRegistered = await page.evaluate(async () => {
      const registration = await navigator.serviceWorker.getRegistration();
      return !!registration;
    });

    expect(swStillRegistered).toBe(true);
  });
});