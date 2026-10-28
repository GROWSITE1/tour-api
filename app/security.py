import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import get_db
from .models import Admin

SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
TOKEN_HOURS = int(os.getenv("TOKEN_HOURS", "168"))
bearer = HTTPBearer()


def hash_password(p: str) -> str:
    return bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode()


def verify_password(p: str, hashed: str) -> bool:
    return bcrypt.checkpw(p.encode(), hashed.encode())


def create_token(username: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(hours=TOKEN_HOURS)
    return jwt.encode({"sub": username, "exp": exp}, SECRET_KEY, algorithm="HS256")


def get_current_admin(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
) -> Admin:
    try:
        username = jwt.decode(creds.credentials, SECRET_KEY, algorithms=["HS256"])["sub"]
    except jwt.PyJWTError:
        raise HTTPException(401, "Invalid or expired token")
    admin = db.scalar(select(Admin).where(Admin.username == username))
    if not admin:
        raise HTTPException(401, "Admin not found")
    return admin
