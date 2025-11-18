# app/schemas/auth.py
from pydantic import BaseModel


class GoogleLoginRequest(BaseModel):
    """
    클라이언트가 Google ID 토큰을 보낼 때 사용하는 스키마.
    - /auth/login 에서 사용
    """
    id_token: str


class Token(BaseModel):
    """
    단순 토큰 응답용 스키마.
    - access_token: JWT 문자열
    - token_type: "bearer" 고정
    """
    access_token: str
    token_type: str = "bearer"

