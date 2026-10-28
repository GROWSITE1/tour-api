import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

url = os.getenv("DATABASE_URL", "sqlite:///./local.db")
if url.startswith("postgres://"):
    url = url.replace("postgres://", "postgresql+psycopg2://", 1)
elif url.startswith("postgresql://"):
    url = url.replace("postgresql://", "postgresql+psycopg2://", 1)

engine = create_engine(
    url,
    pool_pre_ping=True,   # needed: Neon free DB sleeps when idle
    pool_recycle=300,
    connect_args={"check_same_thread": False} if url.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
