from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    pool_size=10 if "sqlite" not in settings.database_url else 0,
    max_overflow=20 if "sqlite" not in settings.database_url else 0,
    pool_pre_ping=True,
    pool_recycle=3600  # Recycle connections after 1 hour
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()