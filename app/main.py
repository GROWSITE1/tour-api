import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from .database import Base, SessionLocal, engine
from .models import Admin
from .routers import auth, bookings, expenses, tours, vehicle_bookings
from .security import hash_password


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)                       # creates tables on first run
    with SessionLocal() as db:                             # first admin from env vars
        if not db.scalar(select(Admin).limit(1)):
            pw = os.getenv("ADMIN_PASSWORD")
            if pw:
                db.add(Admin(username=os.getenv("ADMIN_USERNAME", "admin"),
                             password_hash=hash_password(pw)))
                db.commit()
    yield


app = FastAPI(title="Tour & Travel Management API", version="1.0.0", lifespan=lifespan)

origins = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "*").split(",")]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["*"], allow_headers=["*"])

for r in (auth, tours, bookings, expenses, vehicle_bookings):
    app.include_router(r.router)


@app.get("/", tags=["Health"])
def health():
    return {"status": "ok"}
