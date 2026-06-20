from pydantic import BaseModel, EmailStr, Field
from uuid import UUID


class CreateUser(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    image: str | None = Field(default=None)
    password: str = Field(min_length=8)

class RefreshTokenRequest(BaseModel):
    refresh_token: str 

class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(RefreshTokenRequest, RefreshTokenResponse):
    pass

class TokenData(BaseModel):
    sub: UUID
    email: EmailStr
    type: str
