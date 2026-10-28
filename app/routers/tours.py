from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Booking, Tour, Vehicle
from ..schemas import (BookingOut, SeatSummary, TourIn, TourOut, TourUpdate,
                       VehicleIn, VehicleOut)
from ..security import get_current_admin
from ..services import seat_summary

router = APIRouter(prefix="/tours", tags=["Tours"], dependencies=[Depends(get_current_admin)])


def get_tour(db: Session, tour_id: int) -> Tour:
    tour = db.get(Tour, tour_id)
    if not tour:
        raise HTTPException(404, "Tour not found")
    return tour


@router.post("", response_model=TourOut, status_code=201)
def create_tour(data: TourIn, db: Session = Depends(get_db)):
    tour = Tour(**data.model_dump())
    db.add(tour)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Tour number already exists")
    return tour


@router.get("", response_model=List[TourOut])
def list_tours(db: Session = Depends(get_db)):
    return db.scalars(select(Tour).order_by(Tour.date.desc())).all()


@router.get("/{tour_id}", response_model=TourOut)
def read_tour(tour_id: int, db: Session = Depends(get_db)):
    return get_tour(db, tour_id)


@router.put("/{tour_id}", response_model=TourOut)
def update_tour(tour_id: int, data: TourUpdate, db: Session = Depends(get_db)):
    tour = get_tour(db, tour_id)
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(tour, k, v)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Tour number already exists")
    return tour


@router.delete("/{tour_id}", status_code=204)
def delete_tour(tour_id: int, db: Session = Depends(get_db)):
    tour = get_tour(db, tour_id)
    if db.scalar(select(Booking.id).where(Booking.tour_id == tour_id).limit(1)):
        raise HTTPException(409, "Tour has bookings; delete or move them first")
    db.delete(tour)
    db.commit()


# ---- vehicles & seats ----
@router.post("/{tour_id}/vehicles", response_model=VehicleOut, status_code=201)
def add_vehicle(tour_id: int, data: VehicleIn, db: Session = Depends(get_db)):
    get_tour(db, tour_id)
    v = Vehicle(tour_id=tour_id, **data.model_dump())
    db.add(v)
    db.commit()
    return v


@router.get("/{tour_id}/vehicles", response_model=List[VehicleOut])
def list_vehicles(tour_id: int, db: Session = Depends(get_db)):
    get_tour(db, tour_id)
    return db.scalars(select(Vehicle).where(Vehicle.tour_id == tour_id)).all()


@router.delete("/{tour_id}/vehicles/{vehicle_id}", status_code=204)
def delete_vehicle(tour_id: int, vehicle_id: int, db: Session = Depends(get_db)):
    v = db.get(Vehicle, vehicle_id)
    if not v or v.tour_id != tour_id:
        raise HTTPException(404, "Vehicle not found")
    db.delete(v)
    db.commit()


@router.get("/{tour_id}/seats", response_model=SeatSummary)
def seats(tour_id: int, db: Session = Depends(get_db)):
    get_tour(db, tour_id)
    return seat_summary(db, tour_id)


@router.get("/{tour_id}/passengers", response_model=List[BookingOut])
def passenger_list(tour_id: int, db: Session = Depends(get_db)):
    """Final list for tour: all confirmed bookings."""
    get_tour(db, tour_id)
    return db.scalars(select(Booking).where(
        Booking.tour_id == tour_id, Booking.status == "booking")
        .order_by(Booking.customer_name)).all()
