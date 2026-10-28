from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import VehicleBooking
from ..schemas import VehicleBookingIn, VehicleBookingOut
from ..security import get_current_admin

router = APIRouter(prefix="/vehicle-bookings", tags=["Vehicle booking"],
                   dependencies=[Depends(get_current_admin)])


def get_vb(db: Session, vb_id: int) -> VehicleBooking:
    vb = db.get(VehicleBooking, vb_id)
    if not vb:
        raise HTTPException(404, "Vehicle booking not found")
    return vb


@router.post("", response_model=VehicleBookingOut, status_code=201)
def create(data: VehicleBookingIn, db: Session = Depends(get_db)):
    vb = VehicleBooking(**data.model_dump())
    db.add(vb)
    db.commit()
    return vb


@router.get("", response_model=List[VehicleBookingOut])
def list_all(db: Session = Depends(get_db)):
    return db.scalars(select(VehicleBooking).order_by(VehicleBooking.travel_date.desc())).all()


@router.get("/{vb_id}", response_model=VehicleBookingOut)
def read(vb_id: int, db: Session = Depends(get_db)):
    return get_vb(db, vb_id)


@router.put("/{vb_id}", response_model=VehicleBookingOut)
def update(vb_id: int, data: VehicleBookingIn, db: Session = Depends(get_db)):
    vb = get_vb(db, vb_id)
    for k, v in data.model_dump().items():
        setattr(vb, k, v)
    db.commit()
    return vb


@router.delete("/{vb_id}", status_code=204)
def delete(vb_id: int, db: Session = Depends(get_db)):
    db.delete(get_vb(db, vb_id))
    db.commit()
