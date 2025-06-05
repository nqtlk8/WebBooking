from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List, Dict
from datetime import datetime
from pydantic import BaseModel

from database import get_db
from models.booking import Booking
from models.bookingdetail import BookingDetail
from models.seat import Seat
from models.ticket_type import TicketType
from models.user import User
from schemas.booking import (
    BookingInitiateRequest,
    BookingResponse,
    ErrorResponse,
    BookingUpdate,
    AggregatedBookingDetail,
    TicketTypeResponse,
    BookingStatusResponse,
    AdminBookingListItem,
    AdminBookingDetail
)
from api.auth import verify_token

router = APIRouter(
)

# User endpoints
@router.post(
    "/initiate",
    response_model=BookingResponse,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def initiate_booking(
    request: BookingInitiateRequest,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    try:
        # Calculate total amount (chỉ để kiểm tra)
        total_amount = 0
        for seat_request in request.seats_requested:
            ticket_type = db.query(TicketType).filter(TicketType.id == seat_request.ticket_type_id).first()
            if not ticket_type:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Ticket type {seat_request.ticket_type_id} not found"
                )
            total_amount += ticket_type.price * seat_request.quantity

        # Create new booking
        new_booking = Booking(
            user_id=request.user_id,
            status="pending",
            time=datetime.now()
        )
        db.add(new_booking)
        db.flush()

        # Process each seat request and create BookingDetail for each seat
        for seat_request in request.seats_requested:
            available_seats = db.query(Seat).filter(
                Seat.ticket_type_id == seat_request.ticket_type_id,
                Seat.is_available == True
            ).order_by(Seat.id).limit(seat_request.quantity).all()

            if len(available_seats) < seat_request.quantity:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Not enough available seats for ticket type {seat_request.ticket_type_id}"
                )

            for seat in available_seats:
                booking_detail = BookingDetail(
                    booking_id=new_booking.id,
                    seat_id=seat.id,
                    ticket_type_id=seat_request.ticket_type_id # Store ticket_type_id here
                    # No quantity needed in BookingDetail model as per instruction
                )
                db.add(booking_detail)
                seat.is_available = False

        db.commit()
        
        # Refresh to get the newly created booking details
        db.refresh(new_booking)

        # Aggregate booking details for the response
        aggregated_details = db.query(
            BookingDetail.ticket_type_id,
            func.count(BookingDetail.id).label('quantity'),
            TicketType.name,
            TicketType.price
        ).join(TicketType).filter(BookingDetail.booking_id == new_booking.id)
        
        # Group by ticket_type_id, name, and price
        aggregated_details = aggregated_details.group_by(
            BookingDetail.ticket_type_id,
            TicketType.name,
            TicketType.price
        ).all()

        # Construct the response in the new schema format
        booking_response_data = {
            "id": new_booking.id,
            "user_id": new_booking.user_id,
            "status": new_booking.status,
            "time": new_booking.time,
            "booking_details": []
        }
        
        for detail in aggregated_details:
            booking_response_data["booking_details"].append(
                AggregatedBookingDetail(
                    ticket_type=TicketTypeResponse(
                        id=detail.ticket_type_id,
                        name=detail.name,
                        price=float(detail.price)
                    ),
                    quantity=detail.quantity
                ).dict()
            )

        return booking_response_data

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get(
    "/{booking_id}",
    response_model=BookingResponse,
    responses={
        404: {"model": ErrorResponse},
        401: {"model": ErrorResponse}
    }
)
async def get_booking_details(
    booking_id: int,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )

    # Aggregate booking details for the response
    aggregated_details_query = db.query(
        BookingDetail.ticket_type_id,
        func.count(BookingDetail.id).label('quantity'),
        TicketType.name,
        TicketType.price
    ).join(TicketType).filter(BookingDetail.booking_id == booking_id)
    
    # Group by ticket_type_id, name, and price
    aggregated_details = aggregated_details_query.group_by(
        BookingDetail.ticket_type_id,
        TicketType.name,
        TicketType.price
    ).all()

    # Construct the list of AggregatedBookingDetail Pydantic models
    booking_details_list = []
    for detail in aggregated_details:
        booking_details_list.append(
            AggregatedBookingDetail(
                ticket_type=TicketTypeResponse(
                    id=detail.ticket_type_id,
                    name=detail.name,
                    price=float(detail.price)
                ),
                quantity=detail.quantity
            )
        )

    # Construct and return the BookingResponse Pydantic model
    return BookingResponse(
        id=booking.id,
        user_id=booking.user_id,
        status=booking.status,
        time=booking.time,
        booking_details=booking_details_list
    )

@router.post(
    "/{booking_id}/confirm",
    response_model=BookingStatusResponse,
    responses={
        404: {"model": ErrorResponse},
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse}
    }
)
async def confirm_booking_payment(
    booking_id: int,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )

    if booking.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking is not pending and cannot be confirmed"
        )

    booking.status = "paid"
    db.commit()
    
    return BookingStatusResponse(
        id=booking.id,
        status=booking.status,
        message="Payment confirmed successfully"
    )

@router.post(
    "/{booking_id}/cancel",
    response_model=BookingStatusResponse,
    responses={
        404: {"model": ErrorResponse},
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse}
    }
)
async def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )

    if booking.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending bookings can be canceled"
        )

    # Update booking status to canceled
    booking.status = "canceled"
    
    # Release the seats back to available
    booking_details = db.query(BookingDetail).filter(BookingDetail.booking_id == booking_id).all()
    for detail in booking_details:
        seat = db.query(Seat).filter(Seat.id == detail.seat_id).first()
        if seat:
            seat.is_available = True
    
    db.commit()
    
    return BookingStatusResponse(
        id=booking.id,
        status=booking.status,
        message="Booking canceled successfully"
    )

# Admin endpoints
@router.get(
    "/admin/list",
    response_model=List[AdminBookingListItem],
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def get_admin_booking_list(
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    """Get list of all bookings for admin dashboard"""
    try:
        # Verify admin role
        if token_data.get("type") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin can access this endpoint"
            )

        # Query bookings with user information and calculate total amount
        bookings = db.query(
            Booking,
            User.name.label('user_name'),
            func.sum(TicketType.price).label('total_amount')
        ).join(
            User, Booking.user_id == User.id
        ).join(
            BookingDetail, Booking.id == BookingDetail.booking_id
        ).join(
            TicketType, BookingDetail.ticket_type_id == TicketType.id
        ).group_by(
            Booking.id, User.name
        ).all()

        return [
            AdminBookingListItem(
                id=booking.Booking.id,
                user_name=booking.user_name,
                total_amount=float(booking.total_amount),
                status=booking.Booking.status,
                created_at=booking.Booking.time
            )
            for booking in bookings
        ]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get(
    "/admin/{booking_id}",
    response_model=AdminBookingDetail,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def get_admin_booking_detail(
    booking_id: int,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    """Get detailed information of a booking for admin dashboard"""
    try:
        # Verify admin role
        if token_data.get("type") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin can access this endpoint"
            )

        # Query booking with all related information
        booking = db.query(
            Booking,
            User.name.label('user_name'),
            User.email.label('user_email'),
            func.sum(TicketType.price).label('total_amount')
        ).join(
            User, Booking.user_id == User.id
        ).join(
            BookingDetail, Booking.id == BookingDetail.booking_id
        ).join(
            TicketType, BookingDetail.ticket_type_id == TicketType.id
        ).filter(
            Booking.id == booking_id
        ).group_by(
            Booking.id, User.name, User.email
        ).first()

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )

        # Get ticket details
        ticket_details = db.query(
            TicketType.name,
            TicketType.price,
            func.count(BookingDetail.id).label('quantity')
        ).join(
            BookingDetail, TicketType.id == BookingDetail.ticket_type_id
        ).filter(
            BookingDetail.booking_id == booking_id
        ).group_by(
            TicketType.name, TicketType.price
        ).all()

        return AdminBookingDetail(
            id=booking.Booking.id,
            user_name=booking.user_name,
            user_email=booking.user_email,
            total_amount=float(booking.total_amount),
            status=booking.Booking.status,
            created_at=booking.Booking.time,
            tickets=[
                {
                    "ticket_type": detail.name,
                    "quantity": detail.quantity,
                    "price": float(detail.price)
                }
                for detail in ticket_details
            ]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put(
    "/admin/{booking_id}/status",
    response_model=BookingStatusResponse,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def update_booking_status(
    booking_id: int,
    status_update: BookingUpdate,
    db: Session = Depends(get_db),
    token_data: dict = Depends(verify_token)
):
    """Update booking status (admin only)"""
    try:
        # Verify admin role
        if token_data.get("type") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin can access this endpoint"
            )

        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )

        # Update status
        booking.status = status_update.status
        db.commit()
        db.refresh(booking)

        return BookingStatusResponse(
            id=booking.id,
            status=booking.status,
            message="Booking status updated successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
