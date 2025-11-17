# app/routers/me.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.deps import get_db, get_current_user
from app.models import User, UserInterest, InterestCategory
from app.schemas.user import UserRead
from app.schemas.interest import UserInterestsUpdate

router = APIRouter(prefix="/me", tags=["me"])


@router.get("", response_model=UserRead)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/interests")
def get_my_interests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(UserInterest, InterestCategory)
        .join(InterestCategory, UserInterest.category_id == InterestCategory.id)
        .filter(UserInterest.user_id == current_user.id)
        .all()
    )

    items = [
        {
            "category_id": ic.id,
            "name": ic.name,
            "level": ic.level,
            "weight": ui.weight,
        }
        for ui, ic in rows
    ]
    return {"items": items}


@router.put("/interests")
def update_my_interests(
    payload: UserInterestsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 간단 버전: 기존 거 다 지우고 다시 넣기
    db.query(UserInterest).filter(UserInterest.user_id == current_user.id).delete()

    for item in payload.interests:
        ui = UserInterest(
            user_id=current_user.id,
            category_id=item.category_id,
            weight=item.weight,
        )
        db.add(ui)

    db.commit()
    return {"status": "ok", "count": len(payload.interests)}

