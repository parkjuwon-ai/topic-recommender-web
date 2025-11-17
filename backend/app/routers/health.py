from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import SessionLocal

router = APIRouter(prefix="/health", tags=["health"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", summary="Health check")
def health_check(db: Session = Depends(get_db)):
    """
    - API 살아있는지
    - DB 연결 가능한지 간단히 체크
    """
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "db": "ok"}
    except Exception as e:
        return {"status": "degraded", "db": "error", "detail": str(e)}

