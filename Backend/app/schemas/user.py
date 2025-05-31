from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

class UserBase(BaseModel):
    name: str
    email: EmailStr
    date_of_birth: date
    phone_number: str
    type: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    hashed_password: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None 