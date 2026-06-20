from pydantic import BaseModel, ConfigDict, EmailStr, Field
from uuid import UUID


class   UserProfileUpdate(BaseModel):
    name: str
    email: EmailStr

class UserResponse(UserProfileUpdate):

    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    image: str | None

class PasswordChangeRequest(BaseModel):

    current_password: str
    new_password: str = Field(min_length=8, max_length=20)