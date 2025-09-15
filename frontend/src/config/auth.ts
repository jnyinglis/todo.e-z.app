export interface AuthConfig {
  providers: {
    emailPassword: {
      enabled: boolean;
      allowRegistration: boolean;
    };
    google: {
      enabled: boolean;
      clientId?: string;
    };
    apple: {
      enabled: boolean;
      clientId?: string;
      redirectUri?: string;
    };
    magicLink: {
      enabled: boolean;
      allowNewUsers: boolean;
    };
  };
  ui: {
    showProviderLogos: boolean;
    compactMode: boolean;
    theme: 'light' | 'dark' | 'auto';
  };
}

const getAuthConfig = (): AuthConfig => {
  return {
    providers: {
      emailPassword: {
        enabled: import.meta.env.VITE_AUTH_EMAIL_PASSWORD_ENABLED !== 'false',
        allowRegistration: import.meta.env.VITE_AUTH_EMAIL_REGISTRATION_ENABLED !== 'false',
      },
      google: {
        enabled: import.meta.env.VITE_AUTH_GOOGLE_ENABLED === 'true',
        clientId: import.meta.env.VITE_GOOGLE_CLIENT_ID,
      },
      apple: {
        enabled: import.meta.env.VITE_AUTH_APPLE_ENABLED === 'true',
        clientId: import.meta.env.VITE_APPLE_CLIENT_ID,
        redirectUri: import.meta.env.VITE_APPLE_REDIRECT_URI,
      },
      magicLink: {
        enabled: import.meta.env.VITE_AUTH_MAGIC_LINK_ENABLED !== 'false',
        allowNewUsers: import.meta.env.VITE_AUTH_MAGIC_LINK_NEW_USERS_ENABLED !== 'false',
      },
    },
    ui: {
      showProviderLogos: import.meta.env.VITE_AUTH_SHOW_PROVIDER_LOGOS !== 'false',
      compactMode: import.meta.env.VITE_AUTH_COMPACT_MODE === 'true',
      theme: (import.meta.env.VITE_AUTH_THEME as 'light' | 'dark' | 'auto') || 'light',
    },
  };
};

export const authConfig = getAuthConfig();

// Helper functions for checking enabled providers
export const isEmailPasswordEnabled = () => authConfig.providers.emailPassword.enabled;
export const isGoogleEnabled = () => authConfig.providers.google.enabled && authConfig.providers.google.clientId;
export const isAppleEnabled = () => authConfig.providers.apple.enabled && authConfig.providers.apple.clientId;
export const isMagicLinkEnabled = () => authConfig.providers.magicLink.enabled;

// Get enabled providers count for UI layout
export const getEnabledProvidersCount = (): number => {
  let count = 0;
  if (isEmailPasswordEnabled()) count++;
  if (isGoogleEnabled()) count++;
  if (isAppleEnabled()) count++;
  if (isMagicLinkEnabled()) count++;
  return count;
};

// Get list of enabled providers for debugging
export const getEnabledProviders = (): string[] => {
  const enabled: string[] = [];
  if (isEmailPasswordEnabled()) enabled.push('email-password');
  if (isGoogleEnabled()) enabled.push('google');
  if (isAppleEnabled()) enabled.push('apple');
  if (isMagicLinkEnabled()) enabled.push('magic-link');
  return enabled;
};