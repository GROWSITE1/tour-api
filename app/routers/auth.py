from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Admin
from ..schemas import LoginIn, TokenOut
from ..security import create_token, verify_password

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenOut)
def login(data: LoginIn, db: Session = Depends(get_db)):
    admin = db.scalar(select(Admin).where(Admin.username == data.username))
    if not admin or not verify_password(data.password, admin.password_hash):
        raise HTTPException(401, "Wrong username or password")
    return TokenOut(access_token=create_token(admin.username))
