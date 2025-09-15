import pytest
from unittest.mock import patch
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.schemas.auth import GoogleAuthRequest, AppleAuthRequest, AppleAuthAuthorization, AppleAuthUser, AppleAuthUserName, MagicLinkRequest


class TestAuthenticationFlow:
    """Integration tests for complete authentication flows."""

    @pytest.mark.integration
    @pytest.mark.auth
    async def test_google_auth_new_user_flow(self, async_client: AsyncClient, async_session: AsyncSession) -> None:
        """Test complete Google auth flow for a new user."""
        # Ensure user doesn't exist
        result = await async_session.execute(
            select(User).where(User.email == "newuser@example.com")
        )
        existing_user = result.scalar_one_or_none()
        assert existing_user is None

        google_data = GoogleAuthRequest(
            credential="fake_jwt_token",
                    )

        # Mock Google token verification
        with patch('app.api.auth.verify_google_token') as mock_verify:
            mock_verify.return_value = {
                'email': 'newuser@example.com',
                'name': 'New User'
            }

            # Authenticate
            response = await async_client.post(
                "/api/auth/google",
                json=google_data.model_dump()
            )

            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data

            # Verify user was created in database
            result = await async_session.execute(
                select(User).where(User.email == "newuser@example.com")
            )
            created_user = result.scalar_one_or_none()
            assert created_user is not None
            assert created_user.full_name == "New User"
            assert created_user.google_id is not None

    @pytest.mark.integration
    @pytest.mark.auth
    async def test_google_auth_existing_user_flow(self, async_client: AsyncClient, async_session: AsyncSession) -> None:
        """Test Google auth flow for an existing user."""
        # Create existing user
        existing_user = User(
            email="existing@example.com",
            full_name="Existing User",
            google_id="google_123"
        )
        async_session.add(existing_user)
        await async_session.commit()

        google_data = GoogleAuthRequest(
            credential="fake_jwt_token",
                    )

        with patch('app.api.auth.verify_google_token') as mock_verify:
            mock_verify.return_value = {
                'email': 'existing@example.com',
                'name': 'Existing User Updated'
            }

            response = await async_client.post(
                "/api/auth/google",
                json=google_data.model_dump()
            )

            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data

            # Verify user count didn't increase
            result = await async_session.execute(
                select(User).where(User.email == "existing@example.com")
            )
            users = result.scalars().all()
            assert len(users) == 1

    @pytest.mark.integration
    @pytest.mark.auth
    async def test_apple_auth_new_user_flow(self, async_client: AsyncClient, async_session: AsyncSession) -> None:
        """Test complete Apple auth flow for a new user."""
        apple_data = AppleAuthRequest(
            authorization=AppleAuthAuthorization(
                code='fake_auth_code',
                id_token='fake_id_token'
            ),
            user=AppleAuthUser(
                email='appleuser@example.com',
                name=AppleAuthUserName(
                    firstName='Apple',
                    lastName='User'
                )
            )
        )

        mock_payload = {
            'email': 'appleuser@example.com',
            'sub': 'apple_user_123'
        }

        with patch('pyjwt.decode') as mock_decode:
            mock_decode.return_value = mock_payload

            response = await async_client.post(
                "/api/auth/apple",
                json=apple_data.model_dump()
            )

            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data

            # Verify user was created
            result = await async_session.execute(
                select(User).where(User.email == "appleuser@example.com")
            )
            created_user = result.scalar_one_or_none()
            assert created_user is not None
            assert created_user.full_name == "Apple User"
            assert created_user.apple_id == "apple_user_123"

    @pytest.mark.integration
    @pytest.mark.auth
    async def test_apple_auth_without_user_data(self, async_client: AsyncClient, async_session: AsyncSession) -> None:
        """Test Apple auth flow without user data (subsequent logins)."""
        # Create existing user
        existing_user = User(
            email="existingapple@example.com",
            full_name="Existing Apple User",
            apple_id="apple_existing_123"
        )
        async_session.add(existing_user)
        await async_session.commit()

        apple_data = AppleAuthRequest(
            authorization=AppleAuthAuthorization(
                code='fake_auth_code',
                id_token='fake_id_token'
            )
            # No user data - Apple only provides this on first login
        )

        mock_payload = {
            'email': 'existingapple@example.com',
            'sub': 'apple_existing_123'
        }

        with patch('pyjwt.decode') as mock_decode:
            mock_decode.return_value = mock_payload

            response = await async_client.post(
                "/api/auth/apple",
                json=apple_data.model_dump()
            )

            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data

    @pytest.mark.integration
    @pytest.mark.auth
    async def test_magic_link_complete_flow(self, async_client: AsyncClient, async_session: AsyncSession) -> None:
        """Test complete magic link authentication flow."""
        magic_link_data = MagicLinkRequest(
            email="magiclink@example.com"
        )

        # Step 1: Request magic link
        response = await async_client.post(
            "/api/auth/magic-link",
            json=magic_link_data.model_dump()
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data

        # In a real implementation, we would:
        # 1. Check that an email was sent
        # 2. Extract the token from the email
        # 3. Use that token to complete authentication

        # For now, we just verify the endpoint accepts the request
        # The actual magic link verification would be tested separately
        # when that endpoint is implemented

    @pytest.mark.integration
    @pytest.mark.auth
    async def test_cross_provider_user_handling(self, async_client: AsyncClient, async_session: AsyncSession) -> None:
        """Test handling of users who authenticate with different providers."""
        # Create user with Google
        google_user = User(
            email="crossuser@example.com",
            full_name="Cross Provider User",
            google_id="google_cross_123"
        )
        async_session.add(google_user)
        await async_session.commit()

        # Try to authenticate same email with Apple
        apple_data = AppleAuthRequest(
            authorization=AppleAuthAuthorization(
                code='fake_auth_code',
                id_token='fake_id_token'
            ),
            user=AppleAuthUser(
                email='crossuser@example.com',
                name=AppleAuthUserName(
                    firstName='Cross',
                    lastName='User'
                )
            )
        )

        mock_payload = {
            'email': 'crossuser@example.com',
            'sub': 'apple_cross_123'
        }

        with patch('pyjwt.decode') as mock_decode:
            mock_decode.return_value = mock_payload

            response = await async_client.post(
                "/api/auth/apple",
                json=apple_data.model_dump()
            )

            # This should either:
            # 1. Return existing user (current behavior)
            # 2. Or handle provider conflict appropriately
            assert response.status_code in [200, 409]  # 409 for conflict if implemented

    @pytest.mark.integration
    @pytest.mark.database
    async def test_user_persistence_after_auth(self, async_client: AsyncClient, async_session: AsyncSession) -> None:
        """Test that user data persists correctly after authentication."""
        google_data = GoogleAuthRequest(
            credential="fake_jwt_token",
                    )

        with patch('app.api.auth.verify_google_token') as mock_verify:
            mock_verify.return_value = {
                'email': 'persistent@example.com',
                'name': 'Persistent User'
            }

            # Authenticate
            response = await async_client.post(
                "/api/auth/google",
                json=google_data.model_dump()
            )

            assert response.status_code == 200

            # Verify user exists and has correct data
            result = await async_session.execute(
                select(User).where(User.email == "persistent@example.com")
            )
            user = result.scalar_one_or_none()

            assert user is not None
            assert user.email == "persistent@example.com"
            assert user.full_name == "Persistent User"
            assert user.google_id is not None
            assert user.created_at is not None
            assert user.updated_at is not None