from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import date, datetime
import re

class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    date_of_birth: date
    phone_number: str = Field(..., min_length=10, max_length=15)
    type: str = Field(..., pattern="^(user|admin)$")

    @validator('phone_number')
    def validate_phone_number(cls, v):
        if not re.match(r'^\d{10,15}$', v):
            raise ValueError('Phone number must contain only digits and be between 10-15 characters')
        return v

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=50)

class UserResponse(UserBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "John Doe",
                "email": "john@example.com",
                "date_of_birth": "1990-01-01",
                "phone_number": "1234567890",
                "type": "user",
                "created_at": "2024-03-20T10:00:00"
            }
        }

class Token(BaseModel):
    access_token: str
    token_type: str
    user_type: str

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user_type": "user"
            }
        }

class TokenData(BaseModel):
    email: Optional[str] = None
    type: Optional[str] = None 