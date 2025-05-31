from pydantic import BaseModel
from typing import Optional

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

    class Config:
        from_attributes = True 