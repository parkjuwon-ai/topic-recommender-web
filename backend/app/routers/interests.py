from typing import List, Dict, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.models import InterestCategory
from app.schemas.interest import InterestCategoryNode

router = APIRouter(
    prefix="/interest-categories",
    tags=["interests"],
)


def build_tree(categories: List[InterestCategory]) -> List[InterestCategoryNode]:
    """
    interest_categories 테이블에서 읽어온 레코드들을
    parent_id 기준으로 트리 구조로 변환.
    """
    # parent_id -> [카테고리들] 매핑
    by_parent: Dict[Optional[int], List[InterestCategory]] = {}
    for c in categories:
        by_parent.setdefault(c.parent_id, []).append(c)

    def _build(parent_id: Optional[int]) -> List[InterestCategoryNode]:
        nodes: List[InterestCategoryNode] = []
        for c in by_parent.get(parent_id, []):
            children = _build(c.id)
            nodes.append(
                InterestCategoryNode(
                    id=c.id,
                    name=c.name,
                    children=children or None,
                )
            )
        return nodes

    # parent_id == NULL 인 최상위 노드부터 시작
    return _build(None)


@router.get("/tree", response_model=List[InterestCategoryNode])
def get_interest_tree(db: Session = Depends(get_db)):
    """
    관심사 카테고리 전체 트리를 반환.
    - level 순, id 순으로 정렬 후 트리 변환
    """
    categories = (
        db.query(InterestCategory)
        .order_by(InterestCategory.level, InterestCategory.id)
        .all()
    )
    return build_tree(categories)

