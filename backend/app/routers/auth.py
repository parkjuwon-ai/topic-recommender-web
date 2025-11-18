# app/routers/auth.py
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.deps.db import get_db
from app.models import User
from app.schemas.auth import GoogleLoginRequest, Token
from app.services.google_auth import GoogleUser, verify_google_id_token

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=Token, summary="Google Login (debug 지원)")
def google_login(
    payload: GoogleLoginRequest,
    db: Session = Depends(get_db),
) -> Token:
    """
    1) 로컬: id_token == 'debug' 이면 구글 검증 없이 디버그 유저로 로그인
    2) (향후) 실제 id_token이 오면 verify_google_id_token()으로 검증
    3) users 테이블 upsert
    4) 우리 서비스용 JWT 발급
    """
    now = datetime.now(timezone.utc)

    # 1) 로컬 디버그 모드: 구글 없이 바로 통과
    if payload.id_token == "debug":
        google_data = {
            "sub": "debug-sub",
            "email": "debug@example.com",
            "name": "디버그 유저",
            "picture": None,
        }
    else:
        # 2) (향후) 실제 구글 토큰 검증 – 아직 구현 안 되어 있음
        try:
            google_user: GoogleUser = verify_google_id_token(payload.id_token)
        except NotImplementedError:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Google login is not configured yet.",
            )
        google_data = google_user.model_dump()

    sub = google_data["sub"]
    email = google_data.get("email")
    name = google_data.get("name")
    picture = google_data.get("picture")

    # 3) provider_user_id 기준으로 사용자 조회
    user: User | None = (
        db.query(User)
        .filter(
            User.auth_provider == "google",
            User.provider_user_id == sub,
        )
        .first()
    )

    # 4) 없으면 새로 생성, 있으면 정보 업데이트
    if user is None:
        user = User(
            email=email,
            name=name,
            avatar_url=picture,
            auth_provider="google",
            provider_user_id=sub,
            last_login_at=now,
        )
        db.add(user)
    else:
        if email:
            user.email = email
        if name:
            user.name = name
        if picture:
            user.avatar_url = picture
        user.last_login_at = now

    db.commit()
    db.refresh(user)

    # 5) JWT 발급 (sub = user.id)
    access_token = create_access_token(str(user.id))

    return Token(access_token=access_token, token_type="bearer")

