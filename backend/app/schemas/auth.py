from pydantic import BaseModel, EmailStr
from typing import Optional


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenRefresh(BaseModel):
    refresh_token: str


class EmailAuth(BaseModel):
    email: EmailStr
    password: str


class EmailRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class MagicLinkRequest(BaseModel):
    email: EmailStr


class MagicLinkVerify(BaseModel):
    token: str


class GoogleAuthRequest(BaseModel):
    credential: str  # Google ID token


class AppleAuthAuthorization(BaseModel):
    code: str
    id_token: str


class AppleAuthUserName(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None


class AppleAuthUser(BaseModel):
    name: Optional[AppleAuthUserName] = None
    email: Optional[str] = None


class AppleAuthRequest(BaseModel):
    authorization: AppleAuthAuthorization
    user: Optional[AppleAuthUser] = None


class PasswordReset(BaseModel):
    token: str
    new_password: str


class PasswordResetRequest(BaseModel):
    email: EmailStr