# app/services/topic_generator.py
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Sequence

import requests

from app.core.config import get_settings
from app.models.interest_category import InterestCategory
from app.models.user import User

logger = logging.getLogger(__name__)
settings = get_settings()


SYSTEM_PROMPT = """
너는 글감 추천 전문가다.
사용자의 관심사, 입력 키워드, 그리고 관련 자료 리스트를 보고
블로그·에세이·학습 콘텐츠에 적합한 글 주제(제목)와 설명을 제안한다.

- 사용자가 글을 쓸 때 바로 사용할 수 있을 만큼 구체적으로 작성한다.
- 제목은 1줄, 설명은 2~4문장 정도로 쓴다.
- 설명에는 "왜 지금 이 주제가 의미 있는지"와
  "어떤 관점/구조로 쓰면 좋은지"를 포함한다.
- 반드시 JSON 배열 형식만 출력한다. 자연어 코멘트는 절대 추가하지 않는다.
- 각 항목은 {"title": string, "description": string, "base_score": float} 형식이다.
""".strip()


def _build_prompt_payload(
    user: User,
    categories: Sequence[InterestCategory],
    input_keyword: str | None,
    resources: List[Dict[str, Any]],
    trend_info: Dict[str, Any],
    num_topics: int = 3,
) -> Dict[str, Any]:
    """LLM에 넘길 유저 메시지용 JSON payload 구성."""
    interest_names = [c.name for c in categories if getattr(c, "name", None)]

    # RAG 리소스 요약 (너무 길어지지 않게 상위 몇 개만)
    def _summarize_resources(rs: List[Dict[str, Any]], limit: int = 6) -> Dict[str, Any]:
        items = []
        for r in rs[:limit]:
            title = r.get("title") or "(제목 없음)"
            source = r.get("source") or "bookend"
            desc = r.get("description") or ""
            kind = (r.get("kind") or r.get("type") or "resource").lower()
            platform = r.get("platform") or source
            items.append(
                {
                    "title": title,
                    "source": source,
                    "platform": platform,
                    "kind": kind,
                    "description": desc,
                }
            )
        return {"items": items}

    return {
        "user_profile": {
            "id": str(user.id),
            "email": user.email,
            "interests": interest_names,
        },
        "input_keyword": input_keyword or "",
        "trend": {
            "keyword": trend_info.get("keyword") or "",
            "score": float(trend_info.get("score") or 0.0),
            "w_trend": float(trend_info.get("w_trend") or 0.0),
        },
        "resources": _summarize_resources(resources),
        "requirements": {
            "num_topics": num_topics,
            "output_schema": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "base_score": {"type": "number"},
                    },
                    "required": ["title", "description"],
                },
            },
        },
    }


def _call_ollama_chat(messages: List[Dict[str, str]], timeout: int = 20) -> str:
    """Ollama /api/chat 호출 (non-stream) → assistant content 문자열 반환."""
    base_url = settings.OLLAMA_BASE_URL.rstrip("/")
    url = f"{base_url}/api/chat"

    payload = {
        "model": settings.OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
    }

    resp = requests.post(url, json=payload, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    message = data.get("message") or {}
    content = message.get("content") or ""
    return str(content)


def _parse_topics_json(raw: str) -> List[Dict[str, Any]]:
    """LLM이 반환한 문자열을 JSON 배열로 파싱하고 최소한으로 정규화."""
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError as e:
        logger.warning("LLM JSON decode 실패: %s | raw=%r", e, raw[:300])
        raise ValueError("Invalid JSON from LLM") from e

    if not isinstance(obj, list):
        raise ValueError("LLM output is not a list")

    topics: List[Dict[str, Any]] = []
    for item in obj:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title") or "").strip()
        desc = str(item.get("description") or "").strip()
        if not title:
            continue
        base_score = item.get("base_score", 1.0)
        try:
            base_score = float(base_score)
        except Exception:  # noqa: BLE001
            base_score = 1.0
        topics.append(
            {
                "title": title,
                "description": desc,
                "base_score": base_score,
            }
        )
    return topics


def generate_topics_with_llm(
    user: User,
    categories: Sequence[InterestCategory],
    input_keyword: str | None,
    resources: List[Dict[str, Any]],
    trend_info: Dict[str, Any],
    num_topics: int = 3,
) -> List[Dict[str, Any]]:
    """
    LLM을 호출해 글감 리스트를 생성한다.

    반환 형식:
    [
      {"title": "...", "description": "...", "base_score": 1.0},
      ...
    ]
    """
    payload = _build_prompt_payload(
        user=user,
        categories=categories,
        input_keyword=input_keyword,
        resources=resources,
        trend_info=trend_info,
        num_topics=num_topics,
    )

    user_message = json.dumps(payload, ensure_ascii=False, indent=2)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    raw = _call_ollama_chat(messages)
    topics = _parse_topics_json(raw)

    if not topics:
        raise ValueError("LLM returned empty topic list")

    return topics

