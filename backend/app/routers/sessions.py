from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.deps.db import get_db
from app.deps.auth import get_current_user
from app.models import User, TopicCandidate, UserTopicSession
from app.schemas.session import SessionCreate, SessionRead

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionRead, status_code=status.HTTP_201_CREATED)
def create_session(
    payload: SessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    topic = (
        db.query(TopicCandidate)
        .filter(TopicCandidate.id == payload.topic_id)
        .first()
    )
    if topic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found",
        )

    session = UserTopicSession(
        user_id=current_user.id,
        topic_id=topic.id,
        input_keyword=payload.input_keyword,
        use_trend=payload.use_trend,
        selected_format=payload.selected_format,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/me", response_model=List[SessionRead])
def list_my_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sessions = (
        db.query(UserTopicSession)
        .join(TopicCandidate, UserTopicSession.topic_id == TopicCandidate.id)
        .filter(UserTopicSession.user_id == current_user.id)
        .order_by(UserTopicSession.created_at.desc())
        .all()
    )
    return sessions

