from pydantic import BaseModel, Field
from typing import List, Optional

class SeatBase(BaseModel):
    ticket_type_id: int = Field(..., description="ID of the ticket type associated with this seat")
    is_available: bool = Field(default=True, description="Whether the seat is available for booking")

class SeatCreate(SeatBase):
    pass

class SeatUpdate(BaseModel):
    ticket_type_id: Optional[int] = Field(None, description="ID of the ticket type to update")
    is_available: Optional[bool] = Field(None, description="New availability status of the seat")

class SeatResponse(SeatBase):
    id: int = Field(..., description="Unique identifier of the seat")

    class Config:
        orm_mode = True
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "ticket_type_id": 1,
                "is_available": True
            }
        }

class TicketTypeSeatCount(BaseModel):
    ticket_type_id: int = Field(..., description="ID of the ticket type")
    ticket_type_name: str = Field(..., description="Name of the ticket type")
    total_seats: int = Field(..., description="Total number of seats for this ticket type")
    available_seats: int = Field(..., description="Number of available seats for this ticket type")
    not_available_seats: int = Field(..., description="Number of booked/unavailable seats for this ticket type")

    class Config:
        json_schema_extra = {
            "example": {
                "ticket_type_id": 1,
                "ticket_type_name": "Standard",
                "total_seats": 50,
                "available_seats": 40,
                "not_available_seats": 10
            }
        }

class SeatCountResponse(BaseModel):
    total_seats: int = Field(..., description="Total number of seats in the system")
    available_seats: int = Field(..., description="Total number of available seats")
    not_available_seats: int = Field(..., description="Total number of booked/unavailable seats")
    ticket_type_counts: List[TicketTypeSeatCount] = Field(..., description="List of seat counts per ticket type")

    class Config:
        json_schema_extra = {
            "example": {
                "total_seats": 100,
                "available_seats": 80,
                "not_available_seats": 20,
                "ticket_type_counts": [
                    {
                        "ticket_type_id": 1,
                        "ticket_type_name": "Standard",
                        "total_seats": 50,
                        "available_seats": 40,
                        "not_available_seats": 10
                    }
                ]
            }
        } 