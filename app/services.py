from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .models import Booking, Vehicle


def seat_summary(db: Session, tour_id: int, exclude_booking_id: int | None = None) -> dict:
    total = db.scalar(select(func.coalesce(func.sum(Vehicle.total_seats), 0))
                      .where(Vehicle.tour_id == tour_id))
    q = select(func.coalesce(func.sum(Booking.seats), 0)).where(
        Booking.tour_id == tour_id, Booking.status == "booking")
    if exclude_booking_id:
        q = q.where(Booking.id != exclude_booking_id)
    booked = db.scalar(q)
    return {"tour_id": tour_id, "total_seats": int(total),
            "booked_seats": int(booked), "remaining_seats": int(total) - int(booked)}


def ensure_seats(db: Session, tour_id: int, seats: int, exclude_booking_id: int | None = None):
    s = seat_summary(db, tour_id, exclude_booking_id)
    if seats > s["remaining_seats"]:
        raise HTTPException(
            409, f"Not enough seats: {s['remaining_seats']} remaining "
                 f"(add vehicles to the tour if none are set).")
