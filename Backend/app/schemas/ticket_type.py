from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class TicketTypeBase(BaseModel):
    name: str
    price: float

class TicketTypeCreate(TicketTypeBase):
    pass

class TicketTypeUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None

class TicketTypeResponse(TicketTypeBase):
    id: int
    available_quantity: int

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