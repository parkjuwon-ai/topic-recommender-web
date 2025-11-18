# app/schemas/topic.py
from typing import List
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TopicBase(BaseModel):
    id: UUID
    title: str
    description: str | None = None
    category_id: int | None = None
    source_type: str | None = None

    # 점수 관련 필드
    score: float | None = None        # 최종 점수 (base + trend 가중치)
    trend_score: float | None = None  # 원본 트렌드 점수 (0~100)

    model_config = ConfigDict(from_attributes=True)


# 리소스(도서, 콘텐츠, 포스트 등) – 목업용
class ResourceBook(BaseModel):
    title: str
    author: str | None = None
    thumbnail_url: str | None = None
    external_url: str | None = None
    source: str | None = None  # "bookend" 등


class ResourceContent(BaseModel):
    title: str
    platform: str | None = None  # "munch" 등
    thumbnail_url: str | None = None
    external_url: str | None = None
    source: str | None = None


class ResourcePost(BaseModel):
    title: str
    external_url: str | None = None
    source: str | None = None


class ResourceBundle(BaseModel):
    books: List[ResourceBook] = Field(default_factory=list)
    contents: List[ResourceContent] = Field(default_factory=list)
    posts: List[ResourcePost] = Field(default_factory=list)
    trends: List[str] = Field(default_factory=list)


class TopicRecommendRequest(BaseModel):
    category_ids: List[int] | None = None
    input_keyword: str | None = None
    use_trend: bool = True
    trend_weight: int = 50   # 0~100 슬라이더 값
    limit: int = 3


class TopicRecommendResponse(BaseModel):
    topics: List[TopicBase]
    resources: ResourceBundle

