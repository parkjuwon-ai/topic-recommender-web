# app/deps/db.py
from collections.abc import Generator

from sqlalchemy.orm import Session

from app.db.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    요청마다 DB 세션을 하나 열고,
    요청 끝나면 반드시 닫아주는 FastAPI dependency.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

