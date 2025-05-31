from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import traceback
import logging

from database import get_db
from models.seat import Seat
from models.ticket_type import TicketType
from schemas.seat import SeatCreate, SeatUpdate, SeatResponse, SeatCountResponse, TicketTypeSeatCount
from api.auth import verify_token

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[SeatResponse])
async def get_seats(
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    try:
        seats = db.query(Seat).all()
        # Chuyển đổi rõ ràng từ model sang schema
        return [SeatResponse.from_orm(seat) for seat in seats]
    except Exception as e:
        logger.error(f"Error getting seats: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/count", response_model=SeatCountResponse)
async def get_seat_counts(
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    try:
        # Get total counts
        total_seats = db.query(Seat).count()
        available_seats = db.query(Seat).filter(Seat.is_available == True).count()
        not_available_seats = total_seats - available_seats

        # Get counts by ticket type
        ticket_types = db.query(TicketType).all()
        ticket_type_counts = []
        
        for ticket_type in ticket_types:
            total = db.query(Seat).filter(Seat.ticket_type_id == ticket_type.id).count()
            available = db.query(Seat).filter(
                Seat.ticket_type_id == ticket_type.id,
                Seat.is_available == True
            ).count()
            
            ticket_type_counts.append(TicketTypeSeatCount(
                ticket_type_id=ticket_type.id,
                ticket_type_name=ticket_type.name,
                total_seats=total,
                available_seats=available,
                not_available_seats=total - available
            ))

        # Tạo response rõ ràng
        return SeatCountResponse(
            total_seats=total_seats,
            available_seats=available_seats,
            not_available_seats=not_available_seats,
            ticket_type_counts=ticket_type_counts
        )
    except Exception as e:
        logger.error(f"Error getting seat counts: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/", response_model=SeatResponse)
async def create_seat(
    seat: SeatCreate,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    try:
        db_seat = Seat(**seat.dict())
        db.add(db_seat)
        db.commit()
        db.refresh(db_seat)
        return SeatResponse.from_orm(db_seat)
    except Exception as e:
        logger.error(f"Error creating seat: {str(e)}")
        logger.error(traceback.format_exc())
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/{seat_id}", response_model=SeatResponse)
async def update_seat(
    seat_id: int,
    seat_update: SeatUpdate,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    try:
        seat = db.query(Seat).filter(Seat.id == seat_id).first()
        if not seat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Seat not found"
            )

        update_data = seat_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(seat, key, value)

        db.commit()
        db.refresh(seat)
        return SeatResponse.from_orm(seat)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating seat: {str(e)}")
        logger.error(traceback.format_exc())
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete("/{seat_id}")
async def delete_seat(
    seat_id: int,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    try:
        seat = db.query(Seat).filter(Seat.id == seat_id).first()
        if not seat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Seat not found"
            )

        db.delete(seat)
        db.commit()
        return {"message": "Seat deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting seat: {str(e)}")
        logger.error(traceback.format_exc())
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/available", response_model=List[SeatResponse])
async def get_available_seats(
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    try:
        seats = db.query(Seat).filter(Seat.is_available == True).all()
        return seats
    except Exception as e:
        logger.error(f"Error getting available seats: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
