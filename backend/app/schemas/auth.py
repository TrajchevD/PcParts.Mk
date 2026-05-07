from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator


class RegisterIn(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if len(v.encode()) > 72:
            raise ValueError("Password must be 72 characters or fewer")
        return v


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    user_id: int
    email: str
    created_at: datetime


class UserUpdateIn(BaseModel):
    email: EmailStr | None = None
    current_password: str | None = None
    new_password: str | None = None

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str | None) -> str | None:
        if v is not None:
            if len(v) < 8:
                raise ValueError("Password must be at least 8 characters")
            if len(v.encode()) > 72:
                raise ValueError("Password must be 72 characters or fewer")
        return v
