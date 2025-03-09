from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import date
import re


PATTERN_FULL = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%#?&])[A-Za-z\d@$!%#?&]{8,}$'
PATTERN_LITE = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}$'

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=3, max_length=30)
    avatar_url: Optional[str]

    @field_validator('password')
    def password_validator(self, password: str) -> str:
        if re.match(PATTERN_LITE, password) is None:
            raise ValueError('Password must contain at least one digit')
        return password


class UserResponse(BaseModel):
    full_name: str
    avatar_url: Optional[str]
    email: EmailStr
    is_active: bool
    create_at: date
