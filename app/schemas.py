from datetime import date
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

Status = Literal["enquiry", "booking"]
PayMode = Literal["cash", "card", "cheque", "upi"]
PayKind = Literal["advance", "balance"]
Category = Literal["vehicle_rent", "diesel", "food", "hotels", "police_entry",
                   "taxes", "manager_payment", "fare", "tip", "other"]


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class LoginIn(BaseModel):
    username: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TourIn(BaseModel):
    tour_no: str
    place: str
    days: int = Field(gt=0)
    date: date
    rate: float = Field(ge=0)


class TourUpdate(BaseModel):
    tour_no: Optional[str] = None
    place: Optional[str] = None
    days: Optional[int] = Field(default=None, gt=0)
    date: Optional[date] = None
    rate: Optional[float] = Field(default=None, ge=0)


class TourOut(TourIn, ORM):
    id: int


class VehicleIn(BaseModel):
    type: Literal["tempo", "bus"]
    total_seats: int = Field(gt=0)


class VehicleOut(VehicleIn, ORM):
    id: int
    tour_id: int


class SeatSummary(BaseModel):
    tour_id: int
    total_seats: int
    booked_seats: int
    remaining_seats: int


class BookingIn(BaseModel):
    tour_id: int
    customer_name: str
    age: Optional[int] = Field(default=None, gt=0, lt=120)
    gender: Optional[Literal["male", "female", "other"]] = None
    seats: int = Field(gt=0)
    rooms: int = Field(default=0, ge=0)
    contact_no: str
    email: Optional[str] = None
    status: Status = "enquiry"
    remark: Optional[str] = None


class BookingUpdate(BaseModel):
    customer_name: Optional[str] = None
    age: Optional[int] = Field(default=None, gt=0, lt=120)
    gender: Optional[Literal["male", "female", "other"]] = None
    seats: Optional[int] = Field(default=None, gt=0)
    rooms: Optional[int] = Field(default=None, ge=0)
    contact_no: Optional[str] = None
    email: Optional[str] = None
    status: Optional[Status] = None
    remark: Optional[str] = None


class BookingOut(BookingIn, ORM):
    id: int
    booking_code: Optional[str]


class PaymentIn(BaseModel):
    kind: PayKind
    amount: float = Field(gt=0)
    mode: PayMode
    paid_on: Optional[date] = None
    note: Optional[str] = None


class PaymentOut(PaymentIn, ORM):
    id: int
    booking_id: int
    paid_on: date


class PaymentSummary(BaseModel):
    booking_code: Optional[str]
    total_amount: float      # tour rate x seats
    total_paid: float
    balance_due: float
    payments: List[PaymentOut]


class ExpenseIn(BaseModel):
    category: Category
    amount: float = Field(gt=0)
    expense_date: date
    note: Optional[str] = None


class ExpenseOut(ExpenseIn, ORM):
    id: int
    tour_id: int


class ExpenseSummary(BaseModel):
    tour_id: int
    by_category: dict
    total: float


class VehicleBookingIn(BaseModel):
    from_place: str
    to_place: str
    travel_date: date
    purpose: Optional[str] = None
    invoice_code: Optional[str] = None
    customer_name: str
    customer_contact: Optional[str] = None
    vehicle_type: str


class VehicleBookingOut(VehicleBookingIn, ORM):
    id: int
