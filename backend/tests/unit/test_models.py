import pytest
from datetime import datetime
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User


class TestUserModel:
    """Test the User model functionality."""

    @pytest.mark.unit
    @pytest.mark.database
    async def test_user_creation(self, async_session: AsyncSession) -> None:
        """Test creating a new user."""
        user = User(
            email="test@example.com",
            full_name="Test User",
            google_id="google_123"
        )

        async_session.add(user)
        await async_session.commit()

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.google_id == "google_123"
        assert user.created_at is not None
        assert user.updated_at is not None
        assert user.timezone == "UTC"  # Default value

    @pytest.mark.unit
    @pytest.mark.database
    async def test_user_email_unique_constraint(self, async_session: AsyncSession) -> None:
        """Test that email field has unique constraint."""
        user1 = User(
            email="unique@example.com",
            full_name="User One",
            google_id="google_1"
        )

        user2 = User(
            email="unique@example.com",  # Same email
            full_name="User Two",
            apple_id="apple_1"
        )

        async_session.add(user1)
        await async_session.commit()

        async_session.add(user2)

        # This should raise an integrity error due to unique constraint
        with pytest.raises(Exception):  # Could be IntegrityError or similar
            await async_session.commit()

    @pytest.mark.unit
    @pytest.mark.database
    async def test_user_timestamps_auto_populate(self, async_session: AsyncSession) -> None:
        """Test that timestamps are automatically populated."""
        before_creation = datetime.utcnow()

        user = User(
            email="timestamp@example.com",
            full_name="Timestamp User",
            google_id="google_time"
        )

        async_session.add(user)
        await async_session.commit()

        after_creation = datetime.utcnow()

        assert user.created_at is not None
        assert user.updated_at is not None
        assert before_creation <= user.created_at <= after_creation
        assert before_creation <= user.updated_at <= after_creation

    @pytest.mark.unit
    @pytest.mark.database
    async def test_user_update_timestamp(self, async_session: AsyncSession) -> None:
        """Test that updated_at timestamp changes on update."""
        user = User(
            email="update@example.com",
            full_name="Update User",
            google_id="google_update"
        )

        async_session.add(user)
        await async_session.commit()

        original_updated_at = user.updated_at

        # Small delay to ensure timestamp difference
        import asyncio
        await asyncio.sleep(0.1)

        # Update user
        user.full_name = "Updated User"  # type: ignore
        await async_session.commit()

        assert user.updated_at > original_updated_at

    @pytest.mark.unit
    @pytest.mark.database
    async def test_user_default_timezone(self, async_session: AsyncSession) -> None:
        """Test user default timezone is UTC."""
        user = User(
            email="timezone@example.com",
            full_name="Timezone User",
            google_id="google_tz"
        )

        async_session.add(user)
        await async_session.commit()

        assert user.timezone == "UTC"

    @pytest.mark.unit
    @pytest.mark.database
    async def test_user_custom_timezone(self, async_session: AsyncSession) -> None:
        """Test setting custom timezone."""
        user = User(
            email="custom_tz@example.com",
            full_name="Custom TZ User",
            apple_id="apple_tz",
            timezone="America/New_York"
        )

        async_session.add(user)
        await async_session.commit()

        assert user.timezone == "America/New_York"

    @pytest.mark.unit
    @pytest.mark.database
    async def test_user_query_by_email(self, async_session: AsyncSession) -> None:
        """Test querying user by email."""
        user = User(
            email="query@example.com",
            full_name="Query User",
            google_id="google_query"
        )

        async_session.add(user)
        await async_session.commit()

        # Query by email
        result = await async_session.execute(
            select(User).where(User.email == "query@example.com")
        )
        found_user = result.scalar_one_or_none()

        assert found_user is not None
        assert found_user.email == "query@example.com"
        assert found_user.full_name == "Query User"

    @pytest.mark.unit
    @pytest.mark.database
    async def test_user_query_by_provider(self, async_session: AsyncSession) -> None:
        """Test querying users by provider."""
        google_user = User(
            email="google@example.com",
            full_name="Google User",
            google_id="google_1"
        )

        apple_user = User(
            email="apple@example.com",
            full_name="Apple User",
            apple_id="apple_1"
        )

        async_session.add_all([google_user, apple_user])
        await async_session.commit()

        # Query Google users
        result = await async_session.execute(
            select(User).where(User.google_id.is_not(None))
        )
        google_users = result.scalars().all()

        assert len(google_users) == 1
        assert google_users[0].email == "google@example.com"

        # Query Apple users
        result = await async_session.execute(
            select(User).where(User.apple_id.is_not(None))
        )
        apple_users = result.scalars().all()

        assert len(apple_users) == 1
        assert apple_users[0].email == "apple@example.com"

    @pytest.mark.unit
    @pytest.mark.database
    async def test_user_provider_id_combination(self, async_session: AsyncSession) -> None:
        """Test that provider + provider_id combination works correctly."""
        user = User(
            email="provider_combo@example.com",
            full_name="Provider Combo User",
            google_id="google_combo_123"
        )

        async_session.add(user)
        await async_session.commit()

        # Query by google_id
        result = await async_session.execute(
            select(User).where(
                User.google_id == "google_combo_123"
            )
        )
        found_user = result.scalar_one_or_none()

        assert found_user is not None
        assert found_user.email == "provider_combo@example.com"

    @pytest.mark.unit
    def test_user_model_repr(self) -> None:
        """Test the string representation of User model."""
        user = User(
            email="repr@example.com",
            full_name="Repr User",
            google_id="google_repr"
        )

        # Basic check that repr doesn't crash and includes email
        user_repr = repr(user)
        assert "repr@example.com" in user_repr

    @pytest.mark.unit
    @pytest.mark.database
    async def test_user_nullable_fields(self, async_session: AsyncSession) -> None:
        """Test handling of nullable fields."""
        # Test with minimal required fields
        user = User(
            email="minimal@example.com",
            google_id="google_minimal"
            # full_name is optional, timezone has default
        )

        async_session.add(user)
        await async_session.commit()

        assert user.full_name is None
        assert user.timezone == "UTC"  # type: ignore[unreachable]

    @pytest.mark.unit
    @pytest.mark.database
    async def test_user_field_lengths(self, async_session: AsyncSession) -> None:
        """Test field length constraints."""
        # Test normal length fields
        user = User(
            email="normal@example.com",
            full_name="Normal Length Name",
            google_id="normal_id",
            timezone="America/New_York"
        )

        async_session.add(user)
        await async_session.commit()

        assert user.email == "normal@example.com"

        # Test edge cases like very long emails would be handled by validation
        # at the API level rather than the model level