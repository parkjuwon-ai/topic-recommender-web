from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    """공통 Base 모델"""
    pass


engine = create_engine(
    settings.database_url,
    echo=False,   # 디버깅용으로 보고 싶으면 True로
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

