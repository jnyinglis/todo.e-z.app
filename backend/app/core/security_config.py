"""
Production security configuration and hardening utilities.

This module provides security configurations and utilities for production deployments.
"""

from typing import List, Dict, Any, Callable, Awaitable, Optional
from fastapi import Request, HTTPException, status, FastAPI
from app.schemas.config import CorsConfig
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
import secrets
from app.core.config import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        response = await call_next(request)

        # Security headers
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        }

        # Add CSP for production
        if settings.environment == "production":
            security_headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' https://appleid.cdn-apple.com https://accounts.google.com; "
                "style-src 'self' 'unsafe-inline' https://accounts.google.com; "
                "img-src 'self' data: https:; "
                "font-src 'self' https:; "
                "connect-src 'self' https://appleid.apple.com https://accounts.google.com; "
                "frame-src https://appleid.apple.com https://accounts.google.com; "
                "object-src 'none'; "
                "base-uri 'self';"
            )

        for header, value in security_headers.items():
            response.headers[header] = value

        return response


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware."""

    def __init__(self, app: Any, calls: int = 100, period: int = 60) -> None:
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients: Dict[str, List[float]] = {}

    def get_client_ip(self, request: Request) -> str:
        """Get client IP address, considering proxy headers."""
        # Check for real IP in common proxy headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        return request.client.host if request.client else "unknown"

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        # Skip rate limiting in development
        if settings.environment == "development":
            return await call_next(request)

        client_ip = self.get_client_ip(request)
        current_time = time.time()

        # Clean old entries
        if client_ip in self.clients:
            self.clients[client_ip] = [
                timestamp for timestamp in self.clients[client_ip]
                if current_time - timestamp < self.period
            ]

        # Check rate limit
        if client_ip not in self.clients:
            self.clients[client_ip] = []

        if len(self.clients[client_ip]) >= self.calls:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )

        # Add current request
        self.clients[client_ip].append(current_time)

        return await call_next(request)


def get_cors_config() -> CorsConfig:
    """Get CORS configuration based on environment."""
    if settings.environment == "production":
        # Production CORS - restrictive
        return CorsConfig(
            allow_origins=[settings.frontend_url],
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            allow_headers=[
                "Authorization",
                "Content-Type",
                "X-Requested-With",
                "Accept",
                "Origin",
                "User-Agent",
            ],
            expose_headers=["X-Request-ID"],
            max_age=86400,  # 24 hours
        )
    else:
        # Development CORS - permissive
        return CorsConfig(
            allow_origins=["http://localhost:5173", "http://localhost:3000"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
            max_age=600,  # 10 minutes
        )


def get_trusted_hosts() -> List[str]:
    """Get trusted host list based on environment."""
    if settings.environment == "production":
        # Extract host from URLs
        hosts = []
        for url in [settings.frontend_url, settings.backend_url]:
            if url.startswith("http://"):
                hosts.append(url[7:].split("/")[0])
            elif url.startswith("https://"):
                hosts.append(url[8:].split("/")[0])
        return hosts
    else:
        # Development hosts
        return ["localhost", "127.0.0.1", "0.0.0.0", "testserver"]


class SecureHTTPBearer(HTTPBearer):
    """Enhanced HTTP Bearer with additional security checks."""

    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[HTTPAuthorizationCredentials]:
        credentials = await super().__call__(request)

        if not credentials:
            return None

        # Additional security checks
        token = credentials.credentials

        # Check token format (basic validation)
        if not token or len(token) < 10:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token format",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return None

        # Check for common attack patterns
        suspicious_patterns = ["<", ">", "script", "javascript:", "data:"]
        if any(pattern in token.lower() for pattern in suspicious_patterns):
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token content",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return None

        return credentials


def generate_secure_secret_key() -> str:
    """Generate a cryptographically secure secret key."""
    return secrets.token_urlsafe(64)


def validate_security_config() -> List[str]:
    """Validate security configuration for production."""
    issues = []

    # Check secret key strength
    if settings.environment == "production":
        if settings.secret_key == "your-secret-key-change-this-in-production":
            issues.append("SECRET_KEY must be changed in production")

        if len(settings.secret_key) < 32:
            issues.append("SECRET_KEY should be at least 32 characters long")

        if settings.debug:
            issues.append("DEBUG should be False in production")

        if "localhost" in settings.frontend_url.lower():
            issues.append("FRONTEND_URL should not use localhost in production")

        if settings.database_url and "localhost" in settings.database_url:
            issues.append("DATABASE_URL should not use localhost in production")

    return issues


# Security middleware instances
security_headers_middleware = SecurityHeadersMiddleware
rate_limiting_middleware = RateLimitingMiddleware
secure_bearer = SecureHTTPBearer()


def apply_security_middleware(app: FastAPI) -> FastAPI:
    """Apply all security middleware to the FastAPI app."""
    # Add security headers
    app.add_middleware(SecurityHeadersMiddleware)

    # Add rate limiting for production
    if settings.environment == "production":
        app.add_middleware(RateLimitingMiddleware, calls=1000, period=3600)  # 1000 calls per hour

    # Add trusted host middleware
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=get_trusted_hosts())

    # Add CORS middleware
    cors_config = get_cors_config()
    app.add_middleware(CORSMiddleware, **cors_config.model_dump())

    return app