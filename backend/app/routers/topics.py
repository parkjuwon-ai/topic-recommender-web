# app/routers/topics.py
from __future__ import annotations

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.deps.auth import get_current_user
from app.deps.db import get_db
from app.models.interest_category import InterestCategory
from app.models.topic_candidate import TopicCandidate
from app.models.user import User
from app.models.user_interest import UserInterest
from app.schemas.topic import (
    ResourceBook,
    ResourceBundle,
    ResourceContent,
    ResourcePost,
    TopicBase,
    TopicRecommendRequest,
    TopicRecommendResponse,
)
from app.services.retriever import retrieve_resources
from app.services.topic_generator import generate_topics_with_llm
from app.services.trends import get_trend_score

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()


def pick_trend_keyword(raw: str) -> str:
    """
    너무 긴 문장을 넣으면 0.0만 나와서,
    앞의 1~2 단어 정도로 잘라주는 헬퍼.
    """
    raw = (raw or "").strip()
    if not raw:
        return ""
    tokens = raw.split()
    if len(tokens) >= 2:
        return " ".join(tokens[:2])
    return tokens[0]


def _clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(max_value, value))


def _build_resource_bundle(
    rag_resources: list[dict],
    use_trend: bool,
    trend_keyword_main: str,
) -> ResourceBundle:
    """retriever 결과를 ResourceBundle로 대략 매핑."""
    books: list[ResourceBook] = []
    contents: list[ResourceContent] = []
    posts: list[ResourcePost] = []

    for r in rag_resources[:10]:
        title = r.get("title") or "(제목 없음)"
        source = r.get("source") or "bookend"
        thumbnail_url = r.get("thumbnail_url")
        external_url = r.get("external_url") or r.get("url")
        platform = r.get("platform") or source
        kind = (r.get("kind") or r.get("type") or "").lower()

        if kind == "book":
            books.append(
                ResourceBook(
                    title=title,
                    author=r.get("author") or "",
                    thumbnail_url=thumbnail_url,
                    external_url=external_url,
                    source=source,
                )
            )
        elif kind in {"content", "video", "article"}:
            contents.append(
                ResourceContent(
                    title=title,
                    platform=platform,
                    thumbnail_url=thumbnail_url,
                    external_url=external_url,
                    source=source,
                )
            )
        else:
            posts.append(
                ResourcePost(
                    title=title,
                    external_url=external_url,
                    source=source,
                )
            )

    # RAG 결과가 전혀 없을 때는 Day 8 더미 리소스 유지
    if not (books or contents or posts):
        books.append(
            ResourceBook(
                title="(더미) 글감을 찾는 법",
                author="Bookend 팀",
                thumbnail_url=None,
                external_url="https://book-end.tech",
                source="bookend",
            )
        )
        contents.append(
            ResourceContent(
                title="(더미) 오늘 뭐 쓸지 모를 때",
                platform="munch",
                thumbnail_url=None,
                external_url="https://munch.press",
                source="munch",
            )
        )

    trends = [trend_keyword_main] if use_trend and trend_keyword_main else []

    return ResourceBundle(
        books=books,
        contents=contents,
        posts=posts,
        trends=trends,
    )


def _generate_mock_topics(
    category_ids: List[int],
    cat_by_id: dict[int, InterestCategory],
    payload: TopicRecommendRequest,
    trend_raw: float,
    w_trend: float,
    db: Session,
) -> List[TopicBase]:
    """Day 8에서 쓰던 목업 로직을 fallback으로 분리."""
    limit = max(1, payload.limit or 3)
    topic_schema_list: List[TopicBase] = []

    trend_norm = trend_raw / 100.0 if trend_raw > 0 else 0.0
    base_norm = 1.0  # mock은 일단 1.0 고정

    for i in range(limit):
        cat_id = category_ids[i % len(category_ids)]
        cat = cat_by_id.get(cat_id)

        base_title = cat.name if cat else "관심사"
        keyword_part = (payload.input_keyword or "").strip()

        if keyword_part:
            title = f"{base_title} × {keyword_part} 돌아보기"
            desc = f"'{base_title}' 관점에서 '{keyword_part}'에 대해 정리해보는 글입니다."
        else:
            title = f"{base_title}에 대한 오늘의 글감"
            desc = f"'{base_title}'를 주제로 최근 경험이나 생각을 정리해보는 글입니다."

        final_score = (1 - w_trend) * base_norm + w_trend * trend_norm

        t = TopicCandidate(
            title=title,
            description=desc,
            category_id=cat_id,
            source_type="mock",
            source_meta={
                "from_category_ids": category_ids,
                "use_trend": payload.use_trend,
                "input_keyword": payload.input_keyword,
            },
            trend_score=trend_raw or None,
        )
        db.add(t)
        db.flush()

        topic_schema_list.append(
            TopicBase(
                id=t.id,
                title=t.title,
                description=t.description,
                category_id=t.category_id,
                source_type=t.source_type,
                score=final_score,
                trend_score=trend_raw or None,
            )
        )

    return topic_schema_list


@router.post("/recommend", response_model=TopicRecommendResponse)
def recommend_topics(
    payload: TopicRecommendRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 1) 사용할 카테고리 결정 (D8과 동일)
    if payload.category_ids:
        category_ids = payload.category_ids
    else:
        interests = (
            db.query(UserInterest)
            .filter(UserInterest.user_id == current_user.id)
            .order_by(UserInterest.weight.desc())
            .limit(3)
            .all()
        )
        category_ids = [ui.category_id for ui in interests]

    if not category_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No interest categories available for recommendation.",
        )

    categories = (
        db.query(InterestCategory)
        .filter(InterestCategory.id.in_(category_ids))
        .all()
    )
    cat_by_id = {c.id: c for c in categories}

    limit = max(1, payload.limit or 3)

    # 2) 트렌드 비중 (슬라이더) → 0~1
    w_trend = (payload.trend_weight or 0) / 100.0
    w_trend = _clamp(w_trend, 0.0, 1.0)

    # 3) 트렌드 키워드 & 점수 1번만 계산
    #    - 입력 키워드가 있으면 그걸 우선
    #    - 없으면 첫 번째 카테고리 이름 사용
    raw_for_trend = (payload.input_keyword or "").strip()
    if not raw_for_trend and categories:
        raw_for_trend = categories[0].name

    trend_keyword_main = pick_trend_keyword(raw_for_trend)
    if payload.use_trend and trend_keyword_main:
        trend_raw = get_trend_score(trend_keyword_main)
    else:
        trend_raw = 0.0

    # 4) RAG 리소스 조회 (Day 8 retriever 사용)
    rag_resources = retrieve_resources(
        category_ids=category_ids,
        input_keyword=payload.input_keyword,
        top_k=10,
    )

    topic_schema_list: List[TopicBase] = []

    # 5) LLM 시도
    try:
        llm_topics = generate_topics_with_llm(
            user=current_user,
            categories=categories,
            input_keyword=payload.input_keyword,
            resources=rag_resources,
            trend_info={
                "keyword": trend_keyword_main,
                "score": trend_raw,
                "w_trend": w_trend,
            },
            num_topics=limit,
        )

        trend_norm = trend_raw / 100.0 if trend_raw > 0 else 0.0

        for i, t_data in enumerate(llm_topics[:limit]):
            cat_id = category_ids[i % len(category_ids)]

            base_score = float(t_data.get("base_score", 1.0) or 1.0)
            base_norm = _clamp(base_score, 0.0, 1.0)
            final_score = (1 - w_trend) * base_norm + w_trend * trend_norm

            t = TopicCandidate(
                title=t_data["title"],
                description=t_data["description"],
                category_id=cat_id,
                source_type="llm",
                source_meta={
                    "from_category_ids": category_ids,
                    "use_trend": payload.use_trend,
                    "input_keyword": payload.input_keyword,
                    "llm_model": settings.OLLAMA_MODEL,
                    "trend": {
                        "keyword": trend_keyword_main,
                        "score": trend_raw,
                        "w_trend": w_trend,
                    },
                    "rag_resource_titles": [
                        r.get("title") for r in rag_resources if r.get("title")
                    ],
                },
                trend_score=trend_raw or None,
            )
            db.add(t)
            db.flush()

            topic_schema_list.append(
                TopicBase(
                    id=t.id,
                    title=t.title,
                    description=t.description,
                    category_id=t.category_id,
                    source_type=t.source_type,
                    score=final_score,
                    trend_score=trend_raw or None,
                )
            )
    except Exception as e:  # noqa: BLE001
        logger.warning("LLM topic generation failed, fallback to mock: %s", e)
        topic_schema_list = []

    # 6) LLM 결과가 없으면 fallback(mock) 사용
    if not topic_schema_list:
        topic_schema_list = _generate_mock_topics(
            category_ids=category_ids,
            cat_by_id=cat_by_id,
            payload=payload,
            trend_raw=trend_raw,
            w_trend=w_trend,
            db=db,
        )

    # 7) DB 반영
    db.flush()
    db.commit()

    # 정렬: 최종 score 기준 내림차순
    topic_schema_list.sort(
        key=lambda x: (x.score or 0.0),
        reverse=True,
    )

    # 8) 리소스 번들 구성 (RAG + 트렌드 키워드)
    resources = _build_resource_bundle(
        rag_resources=rag_resources,
        use_trend=payload.use_trend,
        trend_keyword_main=trend_keyword_main,
    )

    return TopicRecommendResponse(
        topics=topic_schema_list,
        resources=resources,
    )

