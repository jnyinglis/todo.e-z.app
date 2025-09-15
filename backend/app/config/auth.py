from typing import Dict, List
import os
from pydantic import BaseModel


class AuthProviderConfig(BaseModel):
    enabled: bool = False


class EmailPasswordConfig(AuthProviderConfig):
    allow_registration: bool = True
    require_email_verification: bool = False


class GoogleConfig(AuthProviderConfig):
    client_id: str | None = None
    client_secret: str | None = None


class AppleConfig(AuthProviderConfig):
    client_id: str | None = None
    team_id: str | None = None
    key_id: str | None = None
    private_key_path: str | None = None
    redirect_uri: str | None = None


class MagicLinkConfig(AuthProviderConfig):
    allow_new_users: bool = True
    token_expire_minutes: int = 15


class SMTPConfig(BaseModel):
    host: str = "localhost"
    port: int = 587
    username: str | None = None
    password: str | None = None
    from_email: str | None = None
    from_name: str = "Template App"
    use_tls: bool = True


class AuthConfig(BaseModel):
    email_password: EmailPasswordConfig
    google: GoogleConfig
    apple: AppleConfig
    magic_link: MagicLinkConfig
    smtp: SMTPConfig

    def get_enabled_providers(self) -> List[str]:
        """Get list of enabled authentication providers"""
        enabled = []
        if self.email_password.enabled:
            enabled.append("email-password")
        if self.google.enabled and self.google.client_id:
            enabled.append("google")
        if self.apple.enabled and self.apple.client_id:
            enabled.append("apple")
        if self.magic_link.enabled:
            enabled.append("magic-link")
        return enabled

    def is_provider_enabled(self, provider: str) -> bool:
        """Check if a specific provider is enabled and configured"""
        if provider == "email-password":
            return self.email_password.enabled
        elif provider == "google":
            return self.google.enabled and bool(self.google.client_id)
        elif provider == "apple":
            return self.apple.enabled and bool(self.apple.client_id)
        elif provider == "magic-link":
            return self.magic_link.enabled
        return False


def get_auth_config() -> AuthConfig:
    """Load authentication configuration from environment variables"""
    return AuthConfig(
        email_password=EmailPasswordConfig(
            enabled=os.getenv("VITE_AUTH_EMAIL_PASSWORD_ENABLED", "true").lower() != "false",
            allow_registration=os.getenv("VITE_AUTH_EMAIL_REGISTRATION_ENABLED", "true").lower() != "false",
            require_email_verification=os.getenv("AUTH_REQUIRE_EMAIL_VERIFICATION", "false").lower() == "true"
        ),
        google=GoogleConfig(
            enabled=os.getenv("VITE_AUTH_GOOGLE_ENABLED", "false").lower() == "true",
            client_id=os.getenv("GOOGLE_CLIENT_ID"),
            client_secret=os.getenv("GOOGLE_CLIENT_SECRET")
        ),
        apple=AppleConfig(
            enabled=os.getenv("VITE_AUTH_APPLE_ENABLED", "false").lower() == "true",
            client_id=os.getenv("APPLE_CLIENT_ID"),
            team_id=os.getenv("APPLE_TEAM_ID"),
            key_id=os.getenv("APPLE_KEY_ID"),
            private_key_path=os.getenv("APPLE_PRIVATE_KEY_PATH"),
            redirect_uri=os.getenv("VITE_APPLE_REDIRECT_URI")
        ),
        magic_link=MagicLinkConfig(
            enabled=os.getenv("VITE_AUTH_MAGIC_LINK_ENABLED", "true").lower() != "false",
            allow_new_users=os.getenv("VITE_AUTH_MAGIC_LINK_NEW_USERS_ENABLED", "true").lower() != "false",
            token_expire_minutes=int(os.getenv("MAGIC_LINK_EXPIRE_MINUTES", "15"))
        ),
        smtp=SMTPConfig(
            host=os.getenv("SMTP_HOST", "localhost"),
            port=int(os.getenv("SMTP_PORT", "587")),
            username=os.getenv("SMTP_USERNAME"),
            password=os.getenv("SMTP_PASSWORD"),
            from_email=os.getenv("SMTP_FROM_EMAIL"),
            from_name=os.getenv("SMTP_FROM_NAME", "Template App"),
            use_tls=os.getenv("SMTP_USE_TLS", "true").lower() == "true"
        )
    )


# Global auth configuration instance
auth_config = get_auth_config()