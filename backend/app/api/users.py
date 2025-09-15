from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.user import User as UserSchema

router = APIRouter()


@router.get("/me", response_model=UserSchema)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
) -> UserSchema:
    """Get current user profile"""
    return UserSchema.model_validate(current_user)


@router.get("/profile", response_model=UserSchema)
async def get_user_profile(
    current_user: User = Depends(get_current_user)
) -> UserSchema:
    """Get user profile (alias for /me)"""
    return UserSchema.model_validate(current_user)