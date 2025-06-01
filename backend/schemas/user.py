from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional, Self
from datetime import date
import re

from core.settings import PATTERN_LITE
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=3, max_length=30)
    avatar_url: Optional[str] = None

    @field_validator('password')
    @classmethod
    def password_validator(cls, password: str) -> str:
        if re.match(PATTERN_LITE, password) is None:
            raise ValueError('Password must contain at least one digit')
        return password


class UserResponse(BaseModel):
    id: int
    full_name: str
    avatar: Optional[str]
    email: EmailStr
    is_active: bool
    is_staff: bool
    created_at: date

    model_config = ConfigDict(from_attributes=True)

class UserForEmail(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=3, max_length=30)

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    avatar: Optional[str] = None
    password: Optional[str] = None
    is_staff: Optional[bool] = None


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None
