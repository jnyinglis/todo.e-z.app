from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    password: Optional[str] = None


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: Optional[bool] = None


class User(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class UserInDB(User):
    hashed_password: Optional[str] = None
    google_id: Optional[str] = None
    apple_id: Optional[str] = None
    email_verification_token: Optional[str] = None
    email_verification_expires: Optional[datetime] = None