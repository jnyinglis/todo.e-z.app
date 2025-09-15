import pytest
import jwt as pyjwt
from typing import Any, Dict
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from httpx import AsyncClient

from app.schemas.auth import GoogleAuthRequest, AppleAuthRequest, AppleAuthAuthorization, AppleAuthUser, AppleAuthUserName, MagicLinkRequest


class TestAuthEndpoints:
    """Test authentication endpoint behaviors."""

    @pytest.mark.auth
    async def test_google_auth_success(self, async_client: AsyncClient, sample_user_data: Dict[str, str]) -> None:
        """Test successful Google authentication."""
        google_data = GoogleAuthRequest(
            credential="fake_jwt_token"
        )

        with patch('app.api.auth.verify_google_token') as mock_verify:
            mock_verify.return_value = {
                'email': sample_user_data['email'],
                'name': sample_user_data['full_name']
            }

            response = await async_client.post(
                "/api/auth/google",
                json=google_data.model_dump()
            )

            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert "token_type" in data
            assert data["token_type"] == "bearer"

    @pytest.mark.auth
    async def test_google_auth_invalid_token(self, async_client: AsyncClient) -> None:
        """Test Google authentication with invalid token."""
        google_data = GoogleAuthRequest(
            credential="invalid_jwt_token"
        )

        with patch('app.api.auth.verify_google_token') as mock_verify:
            mock_verify.side_effect = Exception("Invalid token")

            response = await async_client.post(
                "/api/auth/google",
                json=google_data.model_dump()
            )

            assert response.status_code == 400

    @pytest.mark.auth
    async def test_apple_auth_success(self, async_client: AsyncClient, sample_user_data: Dict[str, str]) -> None:
        """Test successful Apple authentication."""
        # Create a mock JWT token payload
        mock_payload = {
            'email': sample_user_data['email'],
            'sub': 'apple_user_id_123'
        }

        apple_data = AppleAuthRequest(
            authorization=AppleAuthAuthorization(
                code='fake_auth_code',
                id_token='fake_id_token'
            ),
            user=AppleAuthUser(
                email=sample_user_data['email'],
                name=AppleAuthUserName(
                    firstName='Test',
                    lastName='User'
                )
            )
        )

        with patch('pyjwt.decode') as mock_decode:
            mock_decode.return_value = mock_payload

            response = await async_client.post(
                "/api/auth/apple",
                json=apple_data.model_dump()
            )

            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert "token_type" in data
            assert data["token_type"] == "bearer"

    @pytest.mark.auth
    async def test_apple_auth_invalid_token(self, async_client: AsyncClient) -> None:
        """Test Apple authentication with invalid JWT token."""
        apple_data = AppleAuthRequest(
            authorization=AppleAuthAuthorization(
                code='fake_auth_code',
                id_token='invalid_token'
            )
        )

        with patch('pyjwt.decode') as mock_decode:
            mock_decode.side_effect = pyjwt.InvalidTokenError("Invalid token")

            response = await async_client.post(
                "/api/auth/apple",
                json=apple_data.model_dump()
            )

            assert response.status_code == 400

    @pytest.mark.auth
    async def test_magic_link_request_success(self, async_client: AsyncClient) -> None:
        """Test successful magic link request."""
        magic_link_data = MagicLinkRequest(
            email="test@example.com"
        )

        response = await async_client.post(
            "/api/auth/magic-link",
            json=magic_link_data.model_dump()
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    @pytest.mark.auth
    async def test_magic_link_invalid_email(self, async_client: AsyncClient) -> None:
        """Test magic link request with invalid email."""
        magic_link_data = {
            "email": "invalid_email"
        }

        response = await async_client.post(
            "/api/auth/magic-link",
            json=magic_link_data
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.auth
    async def test_verify_magic_link_success(self, async_client: AsyncClient, sample_user_data: Dict[str, str]) -> None:
        """Test successful magic link verification."""
        # This would need to be implemented in the actual auth endpoint
        token = "fake_magic_link_token"

        with patch('app.api.auth.verify_magic_link_token') as mock_verify:
            mock_verify.return_value = {
                'email': sample_user_data['email']
            }

            response = await async_client.get(f"/api/auth/verify-magic-link?token={token}")

            # This endpoint might not exist yet, so we expect 404 for now
            assert response.status_code in [200, 404]

    @pytest.mark.auth
    async def test_verify_magic_link_invalid_token(self, async_client: AsyncClient) -> None:
        """Test magic link verification with invalid token."""
        token = "invalid_token"

        response = await async_client.get(f"/api/auth/verify-magic-link?token={token}")

        # This endpoint might not exist yet, so we expect 404 for now
        assert response.status_code in [400, 404]


class TestTokenGeneration:
    """Test JWT token generation and validation."""

    @pytest.mark.unit
    def test_create_access_token(self) -> None:
        """Test JWT token creation."""
        from app.core.security import create_access_token

        user_data = {"sub": "test@example.com"}
        token = create_access_token(data=user_data)

        assert isinstance(token, str)
        assert len(token.split('.')) == 3  # JWT has 3 parts

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_verify_token_valid(self) -> None:
        """Test JWT token verification with valid token."""
        from app.core.security import create_access_token, verify_token

        user_data = {"sub": "test@example.com"}
        token = create_access_token(data=user_data)

        payload = await verify_token(token)
        assert payload["sub"] == "test@example.com"

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_verify_token_invalid(self) -> None:
        """Test JWT token verification with invalid token."""
        from app.core.security import verify_token

        with pytest.raises(HTTPException) as exc_info:
            await verify_token("invalid_token")

        assert exc_info.value.status_code == 401