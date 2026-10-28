from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Booking, Payment, Tour
from ..schemas import (BookingIn, BookingOut, BookingUpdate, PaymentIn,
                       PaymentOut, PaymentSummary)
from ..security import get_current_admin
from ..services import ensure_seats

router = APIRouter(prefix="/bookings", tags=["Bookings"], dependencies=[Depends(get_current_admin)])


def get_booking(db: Session, booking_id: int) -> Booking:
    b = db.get(Booking, booking_id)
    if not b:
        raise HTTPException(404, "Booking not found")
    return b


@router.post("", response_model=BookingOut, status_code=201)
def create_booking(data: BookingIn, db: Session = Depends(get_db)):
    if not db.get(Tour, data.tour_id):
        raise HTTPException(404, "Tour not found")
    if data.status == "booking":
        ensure_seats(db, data.tour_id, data.seats)
    b = Booking(**data.model_dump())
    db.add(b)
    db.flush()                                    # get the id
    b.booking_code = f"TR-{date.today().year}-{b.id:04d}"
    db.commit()
    return b


@router.get("", response_model=List[BookingOut])
def list_bookings(tour_id: Optional[int] = None, status: Optional[str] = Query(None, pattern="^(enquiry|booking)$"),
                  db: Session = Depends(get_db)):
    q = select(Booking).order_by(Booking.id.desc())
    if tour_id:
        q = q.where(Booking.tour_id == tour_id)
    if status:
        q = q.where(Booking.status == status)
    return db.scalars(q).all()


@router.get("/{booking_id}", response_model=BookingOut)
def read_booking(booking_id: int, db: Session = Depends(get_db)):
    return get_booking(db, booking_id)


@router.put("/{booking_id}", response_model=BookingOut)
def update_booking(booking_id: int, data: BookingUpdate, db: Session = Depends(get_db)):
    b = get_booking(db, booking_id)
    changes = data.model_dump(exclude_unset=True)
    if changes.get("status", b.status) == "booking":
        ensure_seats(db, b.tour_id, changes.get("seats", b.seats), exclude_booking_id=b.id)
    for k, v in changes.items():
        setattr(b, k, v)
    db.commit()
    return b


@router.delete("/{booking_id}", status_code=204)
def delete_booking(booking_id: int, db: Session = Depends(get_db)):
    db.delete(get_booking(db, booking_id))
    db.commit()


# ---- payments / invoice ----
@router.post("/{booking_id}/payments", response_model=PaymentOut, status_code=201)
def add_payment(booking_id: int, data: PaymentIn, db: Session = Depends(get_db)):
    get_booking(db, booking_id)
    values = data.model_dump()
    values["paid_on"] = values["paid_on"] or date.today()
    p = Payment(booking_id=booking_id, **values)
    db.add(p)
    db.commit()
    return p


@router.get("/{booking_id}/payments", response_model=PaymentSummary)
def list_payments(booking_id: int, db: Session = Depends(get_db)):
    b = get_booking(db, booking_id)
    tour = db.get(Tour, b.tour_id)
    paid = sum(float(p.amount) for p in b.payments)
    total = float(tour.rate) * b.seats
    return PaymentSummary(booking_code=b.booking_code, total_amount=total,
                          total_paid=paid, balance_due=total - paid, payments=b.payments)
