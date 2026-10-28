from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Admin(Base):                      # "Admin login"
    __tablename__ = "admins"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(100))


class Tour(Base):                       # "Tour details"
    __tablename__ = "tours"
    id: Mapped[int] = mapped_column(primary_key=True)
    tour_no: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    place: Mapped[str] = mapped_column(String(120))
    days: Mapped[int] = mapped_column(Integer)
    date: Mapped[date] = mapped_column(Date)
    rate: Mapped[float] = mapped_column(Numeric(12, 2))   # price per seat
    vehicles = relationship("Vehicle", cascade="all, delete-orphan")
    expenses = relationship("Expense", cascade="all, delete-orphan")


class Vehicle(Base):                    # "Vehicle seat option"
    __tablename__ = "vehicles"
    id: Mapped[int] = mapped_column(primary_key=True)
    tour_id: Mapped[int] = mapped_column(ForeignKey("tours.id"), index=True)
    type: Mapped[str] = mapped_column(String(10))          # tempo | bus
    total_seats: Mapped[int] = mapped_column(Integer)      # tempo 14/17/20/26, bus 49


class Booking(Base):                    # "Booking details"
    __tablename__ = "bookings"
    id: Mapped[int] = mapped_column(primary_key=True)
    tour_id: Mapped[int] = mapped_column(ForeignKey("tours.id"), index=True)
    customer_name: Mapped[str] = mapped_column(String(120))
    age: Mapped[Optional[int]] = mapped_column(Integer)
    gender: Mapped[Optional[str]] = mapped_column(String(10))
    seats: Mapped[int] = mapped_column(Integer)
    rooms: Mapped[int] = mapped_column(Integer, default=0)
    contact_no: Mapped[str] = mapped_column(String(20))
    email: Mapped[Optional[str]] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(10), default="enquiry")   # enquiry | booking
    booking_code: Mapped[Optional[str]] = mapped_column(String(30), unique=True)
    remark: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    payments = relationship("Payment", cascade="all, delete-orphan")


class Payment(Base):                    # "Invoice" + "Payment mode"
    __tablename__ = "payments"
    id: Mapped[int] = mapped_column(primary_key=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id"), index=True)
    kind: Mapped[str] = mapped_column(String(10))          # advance | balance
    amount: Mapped[float] = mapped_column(Numeric(12, 2))
    mode: Mapped[str] = mapped_column(String(10))          # cash | card | cheque | upi
    paid_on: Mapped[date] = mapped_column(Date, server_default=func.current_date())
    note: Mapped[Optional[str]] = mapped_column(String(200))


class Expense(Base):                    # "Expense record"
    __tablename__ = "expenses"
    id: Mapped[int] = mapped_column(primary_key=True)
    tour_id: Mapped[int] = mapped_column(ForeignKey("tours.id"), index=True)
    category: Mapped[str] = mapped_column(String(20))
    amount: Mapped[float] = mapped_column(Numeric(12, 2))
    expense_date: Mapped[date] = mapped_column(Date)
    note: Mapped[Optional[str]] = mapped_column(String(200))


class VehicleBooking(Base):             # "Vehicle booking (BRA)"
    __tablename__ = "vehicle_bookings"
    id: Mapped[int] = mapped_column(primary_key=True)
    from_place: Mapped[str] = mapped_column(String(120))
    to_place: Mapped[str] = mapped_column(String(120))
    travel_date: Mapped[date] = mapped_column(Date)
    purpose: Mapped[Optional[str]] = mapped_column(String(200))
    invoice_code: Mapped[Optional[str]] = mapped_column(String(30))
    customer_name: Mapped[str] = mapped_column(String(120))
    customer_contact: Mapped[Optional[str]] = mapped_column(String(20))
    vehicle_type: Mapped[str] = mapped_column(String(30))
