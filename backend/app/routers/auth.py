from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.google_auth import verify_google_id_token
from app.core.security import create_access_token
from app.db.deps import get_db
from app.models import User
from app.schemas.auth import GoogleLoginRequest, LoginResponse
from app.schemas.user import UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse, summary="Google Login")
def google_login(
    payload: GoogleLoginRequest,
    db: Session = Depends(get_db),
):
    """
    1) Google ID 토큰 검증
    2) users 테이블에 upsert
    3) 우리 서비스용 JWT(access_token) 발급
    """

    # 🔹 로컬 디버그용: id_token이 "debug"면 진짜 구글 없이 바로 통과
    if settings.environment == "local" and payload.id_token == "debug":
        google_data = {
            "sub": "debug-sub",
            "email": "debug@example.com",
            "name": "디버그 유저",
            "picture": None,
        }
    else:
        # 실제 구글 토큰 검증
        google_data = verify_google_id_token(payload.id_token)

    sub = google_data.get("sub")
    email = google_data.get("email")
    name = google_data.get("name")
    picture = google_data.get("picture")

    now = datetime.now(timezone.utc)

    # 1) provider_user_id 기준으로 사용자 찾기
    user = (
        db.query(User)
        .filter(
            User.auth_provider == "google",
            User.provider_user_id == sub,
        )
        .first()
    )

    # 2) 없으면 새로 만들고, 있으면 정보 업데이트
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
        user.email = email or user.email
        user.name = name or user.name
        user.avatar_url = picture or user.avatar_url
        user.last_login_at = now

    db.commit()
    db.refresh(user)

    # 3) 우리 API용 JWT 발급 (sub = user.id)
    access_token = create_access_token(str(user.id))

    return LoginResponse(
        user=UserRead.model_validate(user),
        access_token=access_token,
    )

