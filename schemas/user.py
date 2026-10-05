from pydantic import BaseModel , Field , EmailStr
from datetime import datetime
class UserCreate(BaseModel):
    email: EmailStr = Field(min_length=1, max_length=128)
    password: str = Field(min_length=1, max_length=72)
class LoginRequest(BaseModel):
    email: EmailStr = Field(min_length=1, max_length=128)
    password: str = Field(min_length=1, max_length=72)
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
