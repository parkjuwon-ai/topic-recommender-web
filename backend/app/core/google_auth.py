from typing import Any, Dict

from fastapi import HTTPException, status
from google.oauth2 import id_token
from google.auth.transport import requests

from app.core.config import settings


def verify_google_id_token(id_token_str: str) -> Dict[str, Any]:
    """
    실제 Google ID 토큰을 검증해서 payload를 돌려준다.
    유효하지 않으면 401 에러를 던진다.
    """
    try:
        request = requests.Request()

        # google_client_id가 설정되어 있으면 aud 체크까지 진행
        audience = settings.google_client_id or None

        payload = id_token.verify_oauth2_token(
            id_token_str,
            request,
            audience,
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google ID token",
        )

    issuer = payload.get("iss")
    if issuer not in ("accounts.google.com", "https://accounts.google.com"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token issuer",
        )

    return payload

