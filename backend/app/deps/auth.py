# app/deps/auth.py
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError

from app.core.security import decode_token
from app.deps.db import get_db
from app.models.user import User


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    """
    Authorization: Bearer <token> 헤더에서 JWT를 꺼내서
    현재 로그인한 User 객체를 반환하는 dependency.
    """
    # 1) 헤더 확인
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    token = authorization.split(" ", 1)[1].strip()

    # 2) 토큰 디코드
    try:
        payload = decode_token(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token subject missing",
        )

    # 3) DB에서 사용자 조회
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user

