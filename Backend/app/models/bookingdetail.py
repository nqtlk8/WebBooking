from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base


class BookingDetail(Base):
    __tablename__ = "booking_details"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    seat_id = Column(Integer, ForeignKey("seats.id"), nullable=False)
    ticket_type_id = Column(Integer, ForeignKey("ticket_types.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint('seat_id', name='uix_seat_booking'),
    )

    booking = relationship("Booking", back_populates="booking_details")
    seat = relationship("Seat", back_populates="booking_details")
    ticket_type = relationship("TicketType", back_populates="booking_details")