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
        new_ticket_type = TicketType(**ticket_type.dict())
        db.add(new_ticket_type)
        db.commit()
        db.refresh(new_ticket_type)
        return {
            "id": new_ticket_type.id,
            "name": new_ticket_type.name,
            "price": new_ticket_type.price
        }
    except Exception as e:
        logger.error(f"Error creating ticket type: {str(e)}")
        logger.error(traceback.format_exc())
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
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
        ticket_type = db.query(TicketType).filter(TicketType.id == ticket_type_id).first()
        if not ticket_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket type not found"
            )

        update_data = ticket_type_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(ticket_type, key, value)

        db.commit()
        db.refresh(ticket_type)
        return {
            "id": ticket_type.id,
            "name": ticket_type.name,
            "price": ticket_type.price
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating ticket type: {str(e)}")
        logger.error(traceback.format_exc())
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete("/{ticket_type_id}")
async def delete_ticket_type(
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

        db.delete(ticket_type)
        db.commit()
        return {"message": "Ticket type deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting ticket type: {str(e)}")
        logger.error(traceback.format_exc())
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
