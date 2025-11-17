# app/schemas/interest.py
from typing import List

from pydantic import BaseModel, ConfigDict


class InterestCategoryNode(BaseModel):
    id: int
    name: str
    children: list["InterestCategoryNode"] | None = None

    model_config = ConfigDict(from_attributes=True)


# 순환 참조 재빌드
InterestCategoryNode.model_rebuild()


class UserInterestItem(BaseModel):
    category_id: int
    weight: float = 1.0


class UserInterestsUpdate(BaseModel):
    interests: List[UserInterestItem]

