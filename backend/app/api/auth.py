from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from google.oauth2 import id_token
from google.auth.transport import requests
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import jwt as pyjwt
import json
import urllib.request

from app.core.database import get_session
from app.config.auth import auth_config
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_password_hash,
    verify_token
)
from app.core.apple_auth import verify_apple_id_token
from app.core.config import settings
from app.core.logging_config import auth_logger, AuthenticationError, ValidationError
from app.models.user import User
from app.schemas.auth import (
    TokenResponse,
    EmailAuth,
    EmailRegister,
    MagicLinkRequest,
    MagicLinkVerify,
    GoogleAuthRequest,
    AppleAuthRequest,
    TokenRefresh
)
from app.schemas.user import User as UserSchema
from app.schemas.response import MessageResponse

router = APIRouter()


@router.get("/config")
async def get_auth_config() -> Dict[str, Any]:
    """Get current authentication configuration"""
    return {
        "providers": {
            "email_password": {
                "enabled": auth_config.is_provider_enabled("email-password"),
                "allow_registration": auth_config.email_password.allow_registration,
            },
            "google": {
                "enabled": auth_config.is_provider_enabled("google"),
                "client_id": auth_config.google.client_id if auth_config.is_provider_enabled("google") else None,
            },
            "apple": {
                "enabled": auth_config.is_provider_enabled("apple"),
            },
            "magic_link": {
                "enabled": auth_config.is_provider_enabled("magic-link"),
                "allow_new_users": auth_config.magic_link.allow_new_users,
            },
        },
        "enabled_providers": auth_config.get_enabled_providers(),
    }


@router.post("/login/email", response_model=TokenResponse)
async def login_email(
    auth_data: EmailAuth,
    response: Response,
    session: AsyncSession = Depends(get_session)
) -> TokenResponse:
    """Login with email and password"""
    if not auth_config.is_provider_enabled("email-password"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email/password authentication is disabled"
        )
    result = await session.execute(select(User).where(User.email == auth_data.email))
    user = result.scalar_one_or_none()

    if not user or not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not verify_password(auth_data.password, str(user.hashed_password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is disabled"
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    # Set httpOnly cookies for secure token storage
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=settings.access_token_expire_minutes * 60,
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax"
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax"
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60
    )


@router.post("/register/email", response_model=UserSchema)
async def register_email(
    user_data: EmailRegister,
    session: AsyncSession = Depends(get_session)
) -> UserSchema:
    """Register with email and password"""
    if not auth_config.is_provider_enabled("email-password"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email/password authentication is disabled"
        )

    if not auth_config.email_password.allow_registration:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email registration is disabled"
        )
    # Check if user already exists
    result = await session.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        is_verified=False
    )

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return UserSchema.model_validate(new_user)


@router.post("/magic-link/request", response_model=MessageResponse)
async def request_magic_link(
    request_data: MagicLinkRequest,
    session: AsyncSession = Depends(get_session)
) -> MessageResponse:
    """Request magic link for email authentication"""
    if not auth_config.is_provider_enabled("magic-link"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Magic link authentication is disabled"
        )
    # Generate magic link token
    token = secrets.token_urlsafe(32)
    expires = datetime.utcnow() + timedelta(minutes=auth_config.magic_link.token_expire_minutes)

    # Find or create user
    result = await session.execute(select(User).where(User.email == request_data.email))
    user = result.scalar_one_or_none()

    if not user:
        if not auth_config.magic_link.allow_new_users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found and new user registration via magic link is disabled"
            )
        user = User(
            email=request_data.email,
            is_verified=False,
            email_verification_token=token,
            email_verification_expires=expires
        )
        session.add(user)
    else:
        user.email_verification_token = token  # type: ignore
        user.email_verification_expires = expires  # type: ignore

    await session.commit()

    # Send email (mock implementation)
    magic_link = f"{settings.frontend_url}/auth/verify?token={token}"

    # TODO: Implement actual email sending
    print("=" * 80)
    print("🔮 MAGIC LINK GENERATED FOR TESTING")
    print("=" * 80)
    print(f"Email: {request_data.email}")
    print(f"Token: {token}")
    print(f"Magic Link: {magic_link}")
    print(f"Expires: {expires}")
    print("=" * 80)
    print("Copy the TOKEN above and paste it into the Magic Link verify form")
    print("=" * 80)

    return MessageResponse(message="Magic link sent to email")


@router.post("/magic-link/verify", response_model=TokenResponse)
async def verify_magic_link(
    verify_data: MagicLinkVerify,
    response: Response,
    session: AsyncSession = Depends(get_session)
) -> TokenResponse:
    """Verify magic link token"""
    if not auth_config.is_provider_enabled("magic-link"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Magic link authentication is disabled"
        )
    result = await session.execute(
        select(User).where(User.email_verification_token == verify_data.token)
    )
    user = result.scalar_one_or_none()

    if not user or not user.email_verification_expires:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )

    if datetime.utcnow() > user.email_verification_expires:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token has expired"
        )

    # Mark user as verified and clear token
    user.is_verified = True  # type: ignore
    user.email_verification_token = None  # type: ignore
    user.email_verification_expires = None  # type: ignore
    user.is_active = True  # type: ignore

    await session.commit()

    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    # Set httpOnly cookies for secure token storage
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=settings.access_token_expire_minutes * 60,
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax"
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax"
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60
    )


@router.post("/google", response_model=TokenResponse)
async def google_auth(
    auth_data: GoogleAuthRequest,
    response: Response,
    session: AsyncSession = Depends(get_session)
) -> TokenResponse:
    """Authenticate with Google OAuth"""
    if not auth_config.is_provider_enabled("google"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Google authentication is disabled"
        )
    try:
        # Verify Google ID token
        idinfo = id_token.verify_oauth2_token(
            auth_data.credential,
            requests.Request(),
            auth_config.google.client_id
        )

        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        google_id = idinfo['sub']
        email = idinfo['email']
        name = idinfo.get('name')
        picture = idinfo.get('picture')

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid Google token: {str(e)}"
        )

    # Find or create user
    result = await session.execute(select(User).where(User.google_id == google_id))
    user = result.scalar_one_or_none()

    if not user:
        # Check if user exists with same email
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if user:
            # Link Google account to existing user
            user.google_id = google_id
        else:
            # Create new user
            user = User(
                email=email,
                full_name=name,
                avatar_url=picture,
                google_id=google_id,
                is_verified=True,
                is_active=True
            )
            session.add(user)

    await session.commit()
    await session.refresh(user)

    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    # Set httpOnly cookies for secure token storage
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=settings.access_token_expire_minutes * 60,
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax"
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax"
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60
    )


@router.post("/apple", response_model=TokenResponse)
async def apple_auth(
    auth_data: AppleAuthRequest,
    response: Response,
    session: AsyncSession = Depends(get_session)
) -> TokenResponse:
    """Authenticate with Apple Sign-In"""
    if not auth_config.is_provider_enabled("apple"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apple authentication is disabled"
        )

    try:
        # Extract identity token from authorization
        id_token_str = auth_data.authorization.id_token

        # Verify Apple ID token with environment-appropriate security
        user_info = await verify_apple_id_token(
            token=id_token_str,
            user_data=auth_data.user
        )

        apple_user_id = user_info["apple_user_id"]
        email = user_info["email"]
        name = user_info["full_name"]

    except HTTPException:
        # Re-raise HTTPExceptions from verification
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Apple authentication failed: {str(e)}"
        )

    # Find or create user
    result = await session.execute(select(User).where(User.apple_id == apple_user_id))
    user = result.scalar_one_or_none()

    if not user:
        # Check if user exists with same email
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if user:
            # Link Apple account to existing user
            user.apple_id = apple_user_id
        else:
            # Create new user
            user = User(
                email=email,
                full_name=name,
                apple_id=apple_user_id,
                is_verified=True,  # Apple emails are pre-verified
                is_active=True
            )
            session.add(user)

    await session.commit()
    await session.refresh(user)

    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    # Set httpOnly cookies for secure token storage
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=settings.access_token_expire_minutes * 60,
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax"
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax"
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token_data: TokenRefresh,
    response: Response,
    session: AsyncSession = Depends(get_session)
) -> TokenResponse:
    """Refresh access token"""
    try:
        payload = await verify_token(token_data.refresh_token)
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        # Verify user still exists and is active
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )

        access_token = create_access_token(data={"sub": str(user.id)})
        new_refresh_token = create_refresh_token(data={"sub": str(user.id)})

        # Set httpOnly cookies for secure token storage
        response.set_cookie(
            key="access_token",
            value=access_token,
            max_age=settings.access_token_expire_minutes * 60,
            httponly=True,
            secure=settings.environment == "production",
            samesite="lax"
        )
        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
            httponly=True,
            secure=settings.environment == "production",
            samesite="lax"
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            expires_in=settings.access_token_expire_minutes * 60
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.post("/logout", response_model=MessageResponse)
async def logout(response: Response) -> MessageResponse:
    """Logout user by clearing httpOnly cookies"""
    # Clear authentication cookies
    response.delete_cookie(key="access_token", httponly=True, samesite="lax")
    response.delete_cookie(key="refresh_token", httponly=True, samesite="lax")

    return MessageResponse(message="Successfully logged out")