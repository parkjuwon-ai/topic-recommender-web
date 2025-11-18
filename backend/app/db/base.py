# app/db/base.py
"""
SQLAlchemy Base 정의.

- 다른 모듈에서는 `from app.db.base import Base`로 import 해서 사용.
"""

from sqlalchemy.orm import declarative_base

Base = declarative_base()

