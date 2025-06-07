from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

class TicketTypeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)

    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()

    @validator('price')
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Price must be greater than 0')
        return round(v, 2)

class TicketTypeCreate(TicketTypeBase):
    pass

class TicketTypeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    price: Optional[float] = Field(None, gt=0)

    @validator('name')
    def name_must_not_be_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip() if v is not None else v

    @validator('price')
    def price_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Price must be greater than 0')
        return round(v, 2) if v is not None else v

class TicketTypeResponse(TicketTypeBase):
    id: int
    available_quantity: int = 0

    class Config:
        from_attributes = True

# AdminBookingListItem - Schema cho danh sách booking
class AdminBookingListItem(BaseModel):
    id: int
    user_name: str
    total_amount: float
    status: str
    created_at: datetime

# AdminBookingDetail - Schema cho chi tiết booking
class AdminBookingDetail(BaseModel):
    id: int
    user_name: str
    user_email: str
    total_amount: float
    status: str
    created_at: datetime
    tickets: List[dict]  # Chi tiết các loại vé 