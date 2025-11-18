# app/core/security.py
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import jwt, JWTError

from app.core.config import get_settings

# ✅ Settings 인스턴스는 이렇게 가져오기
settings = get_settings()


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    user.id 같은 식별자를 받아 JWT 토큰 생성
    - subject: 보통 str(user.id)
    - expires_delta: 없으면 Settings.ACCESS_TOKEN_EXPIRE_MINUTES 사용
    """
    if expires_delta is None:
        # ⚠️ Settings 필드 이름은 config.py 기준으로 대문자 버전
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    expire = datetime.now(timezone.utc) + expires_delta

    to_encode: dict[str, Any] = {
        "sub": str(subject),
        "exp": expire,
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def decode_token(token: str) -> dict:
    """JWT 문자열을 디코딩해서 payload(dict)로 반환"""
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )


class TokenDecodeError(JWTError):
    """JWT 디코딩 관련 에러 래핑용 (필요 시 사용)"""

    pass

