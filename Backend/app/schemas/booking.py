from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class BookingBase(BaseModel):
    """Base schema for booking data"""
    user_id: int
    status: str = Field(default="pending")  # pending, confirmed, cancelled
    time: datetime = Field(default_factory=datetime.now)

class BookingCreate(BookingBase):
    """Schema for creating a new booking"""
    pass

class BookingUpdate(BaseModel):
    """Schema for updating a booking"""
    status: Optional[str] = None

class TicketTypeResponse(BaseModel):
    id: int
    name: str
    price: float

    class Config:
        from_attributes = True

class AggregatedBookingDetail(BaseModel):
    ticket_type: TicketTypeResponse
    quantity: int

    class Config:
        from_attributes = True

class BookingResponse(BaseModel):
    """Schema for booking response with aggregated details"""
    id: int
    user_id: int
    status: str
    time: datetime
    booking_details: List[AggregatedBookingDetail] = []

    class Config:
        from_attributes = True

# Request schemas
class SeatRequest(BaseModel):
    """Schema for individual seat request"""
    ticket_type_id: int = Field(..., description="ID of the ticket type")
    quantity: int = Field(gt=0, description="Number of seats requested for this ticket type")

class BookingInitiateRequest(BaseModel):
    """Schema for booking initiation request"""
    user_id: int = Field(..., description="ID of the user making the booking")
    seats_requested: List[SeatRequest] = Field(..., description="List of seat requests")

# Error response schema
class ErrorResponse(BaseModel):
    """Schema for error responses"""
    detail: str = Field(..., description="Error message")

class BookingStatusResponse(BaseModel):
    """Schema for booking status response (confirm/cancel)"""
    id: int
    status: str
    message: str

    class Config:
        from_attributes = True
