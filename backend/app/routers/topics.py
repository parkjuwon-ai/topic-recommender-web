# app/routers/topics.py
from __future__ import annotations

import logging
from typing import List, Sequence

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.deps.auth import get_current_user
from app.deps.db import get_db
from app.models.user import User
from app.models.interest_category import InterestCategory
from app.models.user_interest import UserInterest
from app.models.topic_candidate import TopicCandidate
from app.schemas.topic import (
    TopicBase,
    TopicRecommendRequest,
    TopicRecommendResponse,
    ResourceBook,
    ResourceContent,
    ResourcePost,
    ResourceBundle,
)
from app.services.retriever import retrieve_resources
from app.services.trends import get_trend_score
from app.services.topic_generator import generate_topics_with_llm

logger = logging.getLogger(__name__)

router = APIRouter(tags=["topics"])

# ---------------------------------------------------------------------------
# 헬퍼 함수들
# ---------------------------------------------------------------------------


def _clamp(x: float, x_min: float, x_max: float) -> float:
    return max(x_min, min(x, x_max))


def pick_trend_keyword(text: str | None, max_tokens: int = 2) -> str | None:
    """
    트렌드용 키워드 추출:
    - 공백 기준으로 최대 max_tokens 단어까지만 사용
    - 예: "AI 출판 트렌드" -> "AI 출판"
    """
    if not text:
        return None
    tokens = text.strip().split()
    if not tokens:
        return None
    return " ".join(tokens[:max_tokens])


def _compute_final_score(
    base_score: float,
    trend_raw: float,
    w_trend: float,
    use_trend: bool,
) -> float:
    """
    최종 점수 계산:
    - base_score: LLM이 준 기본 점수 (0~1 권장, 그래도 다시 클램프)
    - trend_raw: 0~100 (Google Trends 값)
    - w_trend: 0~1 (트렌드 가중치 슬라이더)
    - use_trend: 실제 트렌드를 쓸지 여부
    """
    # 1) base_score 0~1 클램프
    try:
        base = float(base_score)
    except Exception:
        base = 1.0
    base = max(0.0, min(base, 1.0))

    # 2) 트렌드를 사용하지 않으면 base 그대로
    if not use_trend or w_trend <= 0.0:
        return base

    # 3) trend_raw 0~100 → 0~1로 정규화
    try:
        trend_norm = float(trend_raw) / 100.0
    except Exception:
        trend_norm = 0.0
    trend_norm = max(0.0, min(trend_norm, 1.0))

    # 4) 최종 점수
    return (1.0 - w_trend) * base + w_trend * trend_norm


def _generate_mock_topics(
    categories: Sequence[InterestCategory],
    input_keyword: str | None,
    limit: int = 3,
) -> List[dict]:
    """
    LLM 실패 시 사용하는 목업 토픽 생성 로직.
    Day 8에서 쓰던 "관심사 × 키워드 돌아보기" 버전의 심플화.
    """
    if categories:
        main_cat = categories[0].name
    else:
        main_cat = "일반·자기계발"

    keyword = (input_keyword or "요즘 관심사").strip()

    topics: List[dict] = []
    for idx in range(limit):
        title = f"{main_cat} × {keyword} 돌아보기"
        desc = (
            f"'{main_cat}' 관점에서 '{keyword}'에 대해 정리해보는 글입니다. "
            f"내 경험, 배운 점, 앞으로의 계획을 한 번에 묶어서 써보세요."
        )
        topics.append(
            {
                "title": title,
                "description": desc,
                "base_score": 0.7 + 0.05 * idx,  # 대충 0.7, 0.75, 0.8 정도
            }
        )
    return topics


def _build_resource_bundle(
    rag_resources: List[dict],
    use_trend: bool,
    trend_keyword: str | None,
) -> ResourceBundle:
    """
    retriever에서 가져온 리스트를 ResourceBundle 스키마로 변환.
    - kind: "book" | "content" | "post" (없으면 content 취급)
    """
    books: List[ResourceBook] = []
    contents: List[ResourceContent] = []
    posts: List[ResourcePost] = []

    for r in rag_resources:
        kind = (r.get("kind") or r.get("type") or "content").lower()
        title = r.get("title") or "(제목 없음)"
        source = r.get("source") or "unknown"
        thumbnail = r.get("thumbnail_url")
        external_url = r.get("external_url")
        author = r.get("author") or ""
        platform = r.get("platform") or source

        if kind == "book":
            books.append(
                ResourceBook(
                    title=title,
                    author=author,
                    thumbnail_url=thumbnail,
                    external_url=external_url or "",
                    source=source,
                )
            )
        elif kind in ("post", "blog", "community"):
            posts.append(
                ResourcePost(
                    title=title,
                    external_url=external_url,
                    source=source,
                )
            )
        else:
            # 기본은 content 취급
            contents.append(
                ResourceContent(
                    title=title,
                    platform=platform,
                    thumbnail_url=thumbnail,
                    external_url=external_url or "",
                    source=source,
                )
            )

    trends_list: List[str] = []
    if use_trend and trend_keyword:
        trends_list.append(trend_keyword)

    return ResourceBundle(
        books=books,
        contents=contents,
        posts=posts,
        trends=trends_list,
    )


# ---------------------------------------------------------------------------
# 메인 엔드포인트: /topics/recommend
# ---------------------------------------------------------------------------


@router.post("/recommend", response_model=TopicRecommendResponse)
def recommend_topics(
    payload: TopicRecommendRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    관심 카테고리 + 입력 키워드 + RAG + (선택) 트렌드를 기반으로
    글감 3개(또는 limit 개)를 추천한다.
    1) LLM 시도
    2) 실패 시 mock fallback
    """

    # 1) 카테고리 결정
    categories: List[InterestCategory] = []

    if payload.category_ids:
        categories = (
            db.query(InterestCategory)
            .filter(InterestCategory.id.in_(payload.category_ids))
            .all()
        )
    else:
        # 유저 관심사 상위 N개 (예: 3개)
        user_interests: List[UserInterest] = (
            db.query(UserInterest)
            .join(InterestCategory, UserInterest.category_id == InterestCategory.id)
            .filter(UserInterest.user_id == current_user.id)
            .order_by(UserInterest.weight.desc())
            .limit(3)
            .all()
        )
        categories = [ui.category for ui in user_interests if ui.category]

    if not categories:
        raise HTTPException(
            status_code=400,
            detail="추천에 사용할 관심 카테고리가 없습니다. category_ids를 보내거나, 먼저 관심사를 설정해주세요.",
        )

    # 2) 트렌드 비중 (슬라이더) → 0~1
    w_trend = (payload.trend_weight or 0) / 100.0
    w_trend = _clamp(w_trend, 0.0, 1.0)

    # trend_weight가 0이면 실제로는 트렌드 사용 X
    use_trend = payload.use_trend and w_trend > 0.0

    # 3) 트렌드 키워드 & 점수 1번만 계산
    raw_for_trend = (payload.input_keyword or "").strip()
    if not raw_for_trend and categories:
        raw_for_trend = categories[0].name

    trend_keyword_main = pick_trend_keyword(raw_for_trend)
    if use_trend and trend_keyword_main:
        trend_raw = get_trend_score(trend_keyword_main)
    else:
        trend_raw = 0.0

    trend_info = {
        "keyword": trend_keyword_main or "",
        "score": trend_raw,
        "w_trend": w_trend,
    }

    # 4) RAG 리소스 조회
    category_ids = [c.id for c in categories]
    rag_resources = retrieve_resources(
        category_ids=category_ids,
        input_keyword=payload.input_keyword,
        top_k=10,
    )

    # 5) LLM 시도 + 실패 시 mock fallback
    used_llm = True
    try:
        llm_topics = generate_topics_with_llm(
            user=current_user,
            categories=categories,
            input_keyword=payload.input_keyword,
            resources=rag_resources,
            trend_info=trend_info,
            num_topics=payload.limit or 3,
        )
        raw_topics = llm_topics
    except Exception as e:
        logger.warning("LLM topic generation failed, fallback to mock: %s", e)
        used_llm = False
        raw_topics = _generate_mock_topics(
            categories=categories,
            input_keyword=payload.input_keyword,
            limit=payload.limit or 3,
        )

    # 6) TopicCandidate 저장 + 응답용 TopicBase 생성
    topics_response: List[TopicBase] = []

    # 대표 카테고리: 일단 첫 번째 카테고리 기준
    if categories:
        main_category_id = categories[0].id
    elif payload.category_ids:
        main_category_id = payload.category_ids[0]
    else:
        main_category_id = 1  # 안전용 기본값

    for item in raw_topics:
        title = (item.get("title") or "").strip()
        description = (item.get("description") or "").strip()
        if not title:
            continue

        base_score = item.get("base_score", 1.0)

        final_score = _compute_final_score(
            base_score=base_score,
            trend_raw=trend_raw,
            w_trend=w_trend,
            use_trend=use_trend,
        )

        # DB에 저장될 trend_score: raw 0~100 그대로 사용
        trend_score_value = trend_raw if use_trend else None

        source_type = "llm" if used_llm else "mock"

        source_meta = {
            "trend": {
                "keyword": trend_keyword_main,
                "score": trend_raw,
                "weight": w_trend,
                "used": use_trend,
            },
            "rag": {
                "resource_count": len(rag_resources),
            },
        }

        topic_row = TopicCandidate(
            title=title,
            description=description,
            category_id=main_category_id,
            source_type=source_type,
            trend_score=trend_score_value,
            source_meta=source_meta,
        )
        db.add(topic_row)
        db.flush()  # id 확보용

        topics_response.append(
            TopicBase(
                id=topic_row.id,
                title=topic_row.title,
                description=topic_row.description,
                category_id=topic_row.category_id,
                source_type=topic_row.source_type,
                score=final_score,            # 최종 점수
                trend_score=trend_score_value,  # 0~100 or null
            )
        )

    db.commit()

    # 7) 리소스 번들 + 최종 응답
    resource_bundle = _build_resource_bundle(
        rag_resources=rag_resources,
        use_trend=use_trend,
        trend_keyword=trend_keyword_main,
    )

    return TopicRecommendResponse(
        topics=topics_response,
        resources=resource_bundle,
    )

