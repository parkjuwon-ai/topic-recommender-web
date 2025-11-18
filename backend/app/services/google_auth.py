# app/services/google_auth.py
from __future__ import annotations

from pydantic import BaseModel


class GoogleUser(BaseModel):
    sub: str
    email: str
    name: str | None = None
    picture: str | None = None


def verify_google_id_token(id_token_str: str) -> GoogleUser:
    """
    실제 운영에서는 여기서 구글에 ID 토큰 검증을 요청해야 한다.
    지금은 아직 연동 전이라, 이 함수가 호출되면 NotImplementedError를 던진다.

    로컬 개발에서는 /auth/login 에서 id_token == "debug" 일 때
    이 함수 자체를 아예 호출하지 않는다.
    """
    raise NotImplementedError("Google ID token verification is not implemented yet.")

