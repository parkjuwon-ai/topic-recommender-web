# app/routers/__init__.py
"""
라우터 모듈 진입점.

from app.routers import auth, me, interest_categories, topics, sessions

처럼 가져다 쓸 수 있도록 alias를 정리한다.
"""

from .auth import router as auth
from .me import router as me
from .interests import router as interest_categories  # 파일 이름이 interests.py인 경우
from .topics import router as topics
from .sessions import router as sessions

__all__ = [
    "auth",
    "me",
    "interest_categories",
    "topics",
    "sessions",
]

