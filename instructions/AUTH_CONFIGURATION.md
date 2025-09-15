# Authentication Configuration Guide

This template supports multiple authentication providers that can be enabled/disabled via environment variables. This makes it easy to customize the authentication flow for different deployment scenarios.

## Supported Authentication Methods

### 1. Email/Password Authentication
Traditional email and password authentication with optional registration.

**Environment Variables:**
```bash
VITE_AUTH_EMAIL_PASSWORD_ENABLED=true        # Enable/disable email auth
VITE_AUTH_EMAIL_REGISTRATION_ENABLED=true   # Allow new user registration
AUTH_REQUIRE_EMAIL_VERIFICATION=false       # Require email verification (future feature)
```

### 2. Google OAuth
Google Sign-In integration using OAuth 2.0.

**Environment Variables:**
```bash
VITE_AUTH_GOOGLE_ENABLED=false              # Enable/disable Google auth
VITE_GOOGLE_CLIENT_ID=your-client-id         # Frontend Google client ID
GOOGLE_CLIENT_ID=your-client-id              # Backend Google client ID
GOOGLE_CLIENT_SECRET=your-client-secret      # Backend Google client secret
```

**Setup Steps:**
1. Create a project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the Google+ API
3. Create OAuth 2.0 credentials
4. Add your domain to authorized origins
5. Set the client ID and secret in environment variables

### 3. Apple Sign-In
Apple Sign-In integration for iOS and web applications.

**Environment Variables:**
```bash
VITE_AUTH_APPLE_ENABLED=false               # Enable/disable Apple auth
VITE_APPLE_CLIENT_ID=your.apple.client.id   # Apple service ID
VITE_APPLE_REDIRECT_URI=http://localhost:5173/auth/apple/callback
APPLE_CLIENT_ID=your-apple-client-id         # Backend Apple client ID
APPLE_TEAM_ID=YOUR_TEAM_ID                  # Apple Developer Team ID
APPLE_KEY_ID=YOUR_KEY_ID                    # Apple Key ID
APPLE_PRIVATE_KEY_PATH=./certs/apple-private-key.p8
```

**Setup Steps:**
1. Create an App ID in [Apple Developer Console](https://developer.apple.com/)
2. Enable Sign In with Apple capability
3. Create a Services ID for web authentication
4. Generate a private key for server-side verification
5. Configure authorized domains and return URLs
6. Set up the environment variables

**Important Notes:**
- Apple Sign-In requires HTTPS in production
- Users only provide name/email on first sign-up
- The backend currently uses development mode (no JWT signature verification)
- For production, implement proper JWT verification using Apple's public keys

### 4. Magic Link Authentication
Passwordless authentication via email links.

**Environment Variables:**
```bash
VITE_AUTH_MAGIC_LINK_ENABLED=true           # Enable/disable magic links
VITE_AUTH_MAGIC_LINK_NEW_USERS_ENABLED=true # Allow new user creation via magic links
MAGIC_LINK_EXPIRE_MINUTES=15                # Token expiration time
```

**Email Configuration (required for magic links):**
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=Your App Name
SMTP_USE_TLS=true
```

## UI Configuration

Control the appearance and behavior of the authentication interface:

```bash
VITE_AUTH_SHOW_PROVIDER_LOGOS=true          # Show provider logos/buttons
VITE_AUTH_COMPACT_MODE=false                # Use compact layout
VITE_AUTH_THEME=light                       # Theme: light, dark, auto
```

## Configuration Examples

### Example 1: Email + Magic Link Only
Perfect for B2B applications or MVP launches:
```bash
VITE_AUTH_EMAIL_PASSWORD_ENABLED=true
VITE_AUTH_EMAIL_REGISTRATION_ENABLED=true
VITE_AUTH_GOOGLE_ENABLED=false
VITE_AUTH_APPLE_ENABLED=false
VITE_AUTH_MAGIC_LINK_ENABLED=true
```

### Example 2: Social Auth Only
For consumer applications with streamlined onboarding:
```bash
VITE_AUTH_EMAIL_PASSWORD_ENABLED=false
VITE_AUTH_GOOGLE_ENABLED=true
VITE_AUTH_APPLE_ENABLED=true
VITE_AUTH_MAGIC_LINK_ENABLED=false

# Required for Google
VITE_GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-secret

# Required for Apple (when implemented)
VITE_APPLE_CLIENT_ID=your-apple-client-id
```

### Example 3: Enterprise Setup
All methods enabled with strict controls:
```bash
VITE_AUTH_EMAIL_PASSWORD_ENABLED=true
VITE_AUTH_EMAIL_REGISTRATION_ENABLED=false  # Admin-only user creation
VITE_AUTH_GOOGLE_ENABLED=true
VITE_AUTH_APPLE_ENABLED=false
VITE_AUTH_MAGIC_LINK_ENABLED=true
VITE_AUTH_MAGIC_LINK_NEW_USERS_ENABLED=false  # Existing users only
```

## Runtime Configuration API

The backend exposes the current configuration via API:

```bash
GET /api/auth/config
```

Response:
```json
{
  "providers": {
    "email_password": {
      "enabled": true,
      "allow_registration": true
    },
    "google": {
      "enabled": false,
      "client_id": null
    },
    "apple": {
      "enabled": false
    },
    "magic_link": {
      "enabled": true,
      "allow_new_users": true
    }
  },
  "enabled_providers": ["email-password", "magic-link"]
}
```

## Security Considerations

1. **Always use HTTPS in production** - OAuth and Magic Links require secure connections
2. **Rotate secrets regularly** - Especially JWT secrets and OAuth client secrets
3. **Configure CORS properly** - Limit frontend domains that can access your API
4. **Use strong JWT secrets** - Generate cryptographically secure secrets
5. **Monitor authentication logs** - Track failed login attempts and unusual patterns

## Troubleshooting

### Google OAuth Issues
- Verify `GOOGLE_CLIENT_ID` matches in both frontend and backend
- Check that your domain is whitelisted in Google Cloud Console
- Ensure the client ID is for a web application, not mobile

### Magic Link Issues
- Verify SMTP credentials are correct
- Check spam folders for magic link emails
- Ensure `VITE_FRONTEND_URL` is correctly set for link generation

### UI Not Showing Expected Options
- Clear browser cache after changing environment variables
- Check browser console for configuration errors
- Verify Docker containers are using latest environment variables

## Development vs Production

For development, you can use `.env.local` files:
```bash
# .env.local (development)
VITE_AUTH_GOOGLE_ENABLED=false  # Disable OAuth in dev
VITE_AUTH_MAGIC_LINK_ENABLED=true  # Use magic links for testing
```

For production, use proper secret management:
- Azure Key Vault
- AWS Secrets Manager
- HashiCorp Vault
- Kubernetes Secrets