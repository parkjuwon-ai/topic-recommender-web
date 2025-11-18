# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings

settings = get_settings()

# echo=True 로 하면 SQL 로그 다 찍혀서 디버깅할 때 좋음
engine = create_engine(
    settings.DATABASE_URL,
    future=True,
    echo=False,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

