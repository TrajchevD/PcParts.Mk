from pydantic import BaseModel, EmailStr


class UserRegisterIn(BaseModel):
    email: EmailStr
    password: str


class UserLoginIn(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    user_id: int
    email: EmailStr
