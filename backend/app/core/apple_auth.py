"""
Apple Sign-In JWT verification utilities.

This module handles secure verification of Apple ID tokens using Apple's public keys.
"""

import json
import time
from typing import Dict, Any, Optional
import httpx
import jwt as pyjwt
from jwt import PyJWKClient
from fastapi import HTTPException, status
from app.core.config import settings
from app.schemas.auth import AppleAuthUser


class AppleJWTVerifier:
    """Apple ID token verifier using Apple's public keys."""

    def __init__(self) -> None:
        self.jwks_url = "https://appleid.apple.com/auth/keys"
        self.jwks_client = PyJWKClient(self.jwks_url)
        self._cached_keys: Optional[Dict] = None
        self._cache_expiry: float = 0
        self.cache_duration = 3600  # 1 hour

    async def get_apple_public_keys(self) -> Dict[str, Any]:
        """Fetch Apple's public keys for JWT verification."""
        current_time = time.time()

        # Return cached keys if still valid
        if self._cached_keys and current_time < self._cache_expiry:
            return self._cached_keys

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.jwks_url)
                response.raise_for_status()

                keys_data: Dict[str, Any] = response.json()
                self._cached_keys = keys_data
                self._cache_expiry = current_time + self.cache_duration

                return keys_data

        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to fetch Apple public keys: {str(e)}"
            )
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Invalid response from Apple keys endpoint"
            )

    def verify_development_token(self, token: str) -> Dict[str, Any]:
        """Verify token without signature check (development only)."""
        if settings.environment == "production":
            raise ValueError("Development token verification cannot be used in production")

        try:
            decoded_token: Dict[str, Any] = pyjwt.decode(
                token,
                options={
                    "verify_signature": False,
                    "verify_exp": True,
                    "verify_aud": False,  # Apple audience can be complex
                }
            )
            return decoded_token
        except pyjwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid token: {str(e)}"
            )

    async def verify_production_token(self, token: str) -> Dict[str, Any]:
        """Verify token with full signature and claims validation."""
        try:
            # Get the token header to find the key ID
            unverified_header = pyjwt.get_unverified_header(token)
            key_id = unverified_header.get("kid")

            if not key_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Token missing key ID"
                )

            # Get Apple's public keys
            signing_key = self.jwks_client.get_signing_key_from_jwt(token)

            # Verify the token
            decoded_token: Dict[str, Any] = pyjwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=settings.apple_client_id,  # Verify audience
                issuer="https://appleid.apple.com",  # Verify issuer
                options={
                    "verify_exp": True,
                    "verify_aud": True,
                    "verify_iss": True,
                }
            )

            return decoded_token

        except pyjwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid Apple token: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Token verification failed: {str(e)}"
            )

    async def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify Apple ID token with environment-appropriate validation.

        In development: Basic validation without signature verification
        In production: Full JWT signature and claims validation
        """
        if settings.environment == "development" and settings.debug:
            return self.verify_development_token(token)
        else:
            return await self.verify_production_token(token)

    def extract_user_info(self, decoded_token: Dict[str, Any], user_data: Optional[AppleAuthUser] = None) -> Dict[str, Any]:
        """Extract user information from decoded token and user data."""
        apple_user_id = decoded_token.get("sub")
        email = decoded_token.get("email")
        email_verified = decoded_token.get("email_verified", False)

        if not apple_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing user ID in Apple token"
            )

        # Extract name from user data (only provided on first sign-in)
        full_name = None
        if user_data and user_data.name:
            first_name = user_data.name.firstName or ""
            last_name = user_data.name.lastName or ""
            if first_name or last_name:
                full_name = f"{first_name} {last_name}".strip()

        return {
            "apple_user_id": apple_user_id,
            "email": email,
            "email_verified": email_verified,
            "full_name": full_name,
        }


# Global instance
apple_jwt_verifier = AppleJWTVerifier()


async def verify_apple_id_token(token: str, user_data: Optional[AppleAuthUser] = None) -> Dict[str, Any]:
    """
    Verify Apple ID token and extract user information.

    Args:
        token: Apple ID token (JWT)
        user_data: Additional user data from Apple (first sign-in only)

    Returns:
        Dictionary containing user information

    Raises:
        HTTPException: If token is invalid or verification fails
    """
    decoded_token = await apple_jwt_verifier.verify_token(token)
    return apple_jwt_verifier.extract_user_info(decoded_token, user_data)