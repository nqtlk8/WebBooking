from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class TicketType(Base):
    __tablename__ = "ticket_types"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)

    seats = relationship("Seat", back_populates="ticket_type")
    booking_details = relationship("BookingDetail", back_populates="ticket_type", cascade="all, delete-orphan") 