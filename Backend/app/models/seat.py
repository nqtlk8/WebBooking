from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Seat(Base):
    __tablename__ = "seats"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ticket_type_id = Column(Integer, ForeignKey("ticket_types.id"), nullable=False)
    is_available = Column(Boolean, default=True)

    ticket_type = relationship("TicketType")
    booking_details = relationship("BookingDetail", back_populates="seat", cascade="all, delete-orphan")