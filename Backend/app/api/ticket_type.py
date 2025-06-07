from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import traceback
import logging

from database import get_db
from models.ticket_type import TicketType
from schemas.ticket_type import TicketTypeCreate, TicketTypeUpdate, TicketTypeResponse
from api.auth import verify_token
from core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[TicketTypeResponse])
async def get_ticket_types(
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    try:
        ticket_types = db.query(TicketType).all()
        return [
            {
                "id": ticket_type.id,
                "name": ticket_type.name,
                "price": ticket_type.price,
                "available_quantity": sum(1 for seat in ticket_type.seats if seat.is_available)
            }
            for ticket_type in ticket_types
        ]
    except Exception as e:
        logger.error(f"Error getting ticket types: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/", response_model=TicketTypeResponse)
async def create_ticket_type(
    ticket_type: TicketTypeCreate,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    try:
        # Validate input
        if not ticket_type.name or not ticket_type.name.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ticket type name cannot be empty"
            )

        if len(ticket_type.name) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ticket type name must be less than 100 characters"
            )

        if ticket_type.price <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Price must be greater than 0"
            )

        # Check if ticket type with same name already exists
        existing_ticket_type = db.query(TicketType).filter(TicketType.name == ticket_type.name).first()
        if existing_ticket_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A ticket type with this name already exists"
            )

        try:
            # Create new ticket type
            new_ticket_type = TicketType(
                name=ticket_type.name.strip(),
                price=round(ticket_type.price, 2)
            )
            db.add(new_ticket_type)
            db.commit()
            db.refresh(new_ticket_type)

            return {
                "id": new_ticket_type.id,
                "name": new_ticket_type.name,
                "price": new_ticket_type.price,
                "available_quantity": 0
            }
        except Exception as e:
            db.rollback()
            logger.error(f"Database error while creating ticket type: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create ticket type in database"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating ticket type: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create ticket type"
        )

@router.get("/{ticket_type_id}", response_model=TicketTypeResponse)
async def get_ticket_type(
    ticket_type_id: int,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    try:
        ticket_type = db.query(TicketType).filter(TicketType.id == ticket_type_id).first()
        if not ticket_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket type not found"
            )
        return {
            "id": ticket_type.id,
            "name": ticket_type.name,
            "price": ticket_type.price
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting ticket type: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.put("/{ticket_type_id}", response_model=TicketTypeResponse)
async def update_ticket_type(
    ticket_type_id: int,
    ticket_type_update: TicketTypeUpdate,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    try:
        # Check if ticket type exists
        ticket_type = db.query(TicketType).filter(TicketType.id == ticket_type_id).first()
        if not ticket_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket type not found"
            )

        # If name is being updated, check for duplicates
        if ticket_type_update.name and ticket_type_update.name != ticket_type.name:
            existing_ticket_type = db.query(TicketType).filter(
                TicketType.name == ticket_type_update.name,
                TicketType.id != ticket_type_id
            ).first()
            if existing_ticket_type:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A ticket type with this name already exists"
                )

        # Update ticket type
        update_data = ticket_type_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(ticket_type, key, value)

        try:
            db.commit()
            db.refresh(ticket_type)
        except Exception as e:
            db.rollback()
            logger.error(f"Database error while updating ticket type: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update ticket type in database"
            )

        return {
            "id": ticket_type.id,
            "name": ticket_type.name,
            "price": ticket_type.price,
            "available_quantity": sum(1 for seat in ticket_type.seats if seat.is_available)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating ticket type: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update ticket type"
        )

@router.delete("/{ticket_type_id}")
async def delete_ticket_type(
    ticket_type_id: int,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    try:
        # Check if ticket type exists
        ticket_type = db.query(TicketType).filter(TicketType.id == ticket_type_id).first()
        if not ticket_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket type not found"
            )

        # Check if ticket type has associated seats
        if ticket_type.seats:
            # Check if any seats are booked
            booked_seats = [seat for seat in ticket_type.seats if not seat.is_available]
            if booked_seats:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot delete ticket type with booked seats"
                )

        try:
            # Delete associated seats first
            for seat in ticket_type.seats:
                db.delete(seat)
            
            # Delete ticket type
            db.delete(ticket_type)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Database error while deleting ticket type: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete ticket type from database"
            )

        return {"message": "Ticket type and associated seats deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting ticket type: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete ticket type"
        )
