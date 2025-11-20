# app/services/topic_generator.py
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Sequence

import requests
from requests import Timeout, RequestException 

from app.core.config import get_settings
from app.models.interest_category import InterestCategory
from app.models.user import User

logger = logging.getLogger(__name__)
settings = get_settings()


SYSTEM_PROMPT = """
너는 글감 추천 전문가다.

[언어]
- 모든 title과 description은 반드시 한국어로 작성한다.

[역할]
- 사용자의 관심사 태그, 입력 키워드, 참고 자료 리스트, (선택) 트렌드 정보를 보고
- 블로그·에세이·학습용 글 주제를 추천한다.

[출력 형식 규칙]
- 반드시 JSON 배열만 출력한다.
- 코드블록, 자연어 설명, 앞뒤 코멘트는 절대 쓰지 않는다.
- 각 요소는 {"title": string, "description": string, "base_score": float} 형식이다.
- title: 1줄
- description: 2~4문장
- base_score: 0~1 사이 점수 (너가 중요도/재미를 판단해서 넣는다)
""".strip()

def _build_prompt_payload(
    user: User,
    categories: Sequence[InterestCategory],
    input_keyword: str | None,
    resources: List[Dict[str, Any]],
    trend_info: Dict[str, Any],
    num_topics: int = 3,
) -> Dict[str, Any]:
    interest_names = [c.name for c in categories if getattr(c, "name", None)]
    keyword = input_keyword or ""

    # 리소스는 최대 5개, 한 줄 요약
    items: List[str] = []
    for r in resources[:5]:
        title = (r.get("title") or "(제목 없음)").strip()
        source = (r.get("source") or r.get("platform") or "").strip()
        kind = (r.get("kind") or r.get("type") or "resource").lower()
        items.append(f"- [{kind}] {title} ({source})")

    trend_line = ""
    if trend_info.get("keyword") and trend_info.get("score", 0) > 0 and trend_info.get("w_trend", 0) > 0:
        trend_line = (
            f'"{trend_info["keyword"]}" 키워드는 최근 트렌드 점수 '
            f'{trend_info["score"]:.1f}/100 으로, 글감 선택에 참고하면 좋다.'
        )

    return {
        "user_interests": interest_names,
        "input_keyword": keyword,
        "trend_comment": trend_line,
        "resources_summary": "\n".join(items),
        "requirements": {
            "num_topics": num_topics,
            "schema_hint": 'JSON 배열: [{"title": "...", "description": "...", "base_score": 0.8}, ...]',
        },
    }


def _build_ollama_prompt(payload: Dict[str, Any]) -> str:
    """
    Ollama /api/generate 에 전달할 최종 프롬프트 문자열 생성.
    - SYSTEM_PROMPT 설명 뒤에 JSON payload를 붙여준다.
    """
    user_context = json.dumps(payload, ensure_ascii=False, indent=2)
    prompt = (
        SYSTEM_PROMPT
        + "\n\n[입력 데이터]\n"
        + user_context
        + "\n\n위 정보를 참고해서 JSON 배열만 출력해라."
        + '\n예시 형식: '
        + '[{"title": "...", "description": "...", "base_score": 0.9}]'
    )
    return prompt


def _call_ollama_generate(prompt: str, timeout: int = 30) -> str:
    """
    Ollama /api/generate 호출 래퍼.
    - timeout: 30초 (첫 로딩 감안해서 넉넉하게)
    - num_predict: 768 (3개 토픽 + 설명 충분히 나오게)
    """
    base_url = settings.OLLAMA_BASE_URL.rstrip("/")
    url = f"{base_url}/api/generate"

    payload: Dict[str, Any] = {
        "model": settings.OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        # "format": "json",  # ← 버전 따라 이 옵션이 애매해서 일단 빼두자
        "options": {
            "temperature": 0.2,
            "num_predict": 768,
        },
    }

    try:
        resp = requests.post(url, json=payload, timeout=timeout)
        resp.raise_for_status()
    except Timeout:
        logger.warning("Ollama generate timeout (>%ss)", timeout)
        raise
    except RequestException as e:
        logger.error("Ollama generate error: %s", e)
        raise

    data = resp.json()
    content = data.get("response", "")

    return str(content or "")

def _extract_json_segment(raw: str) -> str:
    """
    LLM이 앞뒤로 코멘트를 붙여도, 그 안에서 JSON 덩어리만 잘라내는 헬퍼.
    1순위: 배열 [...] 범위를 찾고
    2순위: 객체 {...} 범위를 찾는다.
    """
    # 배열 먼저
    start = raw.find("[")
    end = raw.rfind("]")
    if start != -1 and end != -1 and end > start:
        return raw[start : end + 1]

    # 객체
    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1 and end > start:
        return raw[start : end + 1]

    raise ValueError("No JSON segment found in LLM output")


def _parse_topics_json(raw: str) -> List[Dict[str, Any]]:
    # 1차: 그대로 파싱 시도
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError as e:
        logger.warning("LLM JSON decode 실패 1차: %s | raw_head=%r", e, raw[:300])
        # 2차: JSON 덩어리만 잘라서 다시 파싱
        try:
            segment = _extract_json_segment(raw)
            obj = json.loads(segment)
        except Exception as e2:
            logger.warning("LLM JSON decode 실패 2차: %s | raw_head=%r", e2, raw[:300])
            raise ValueError("Invalid JSON from LLM") from e2

    # dict 형태로 오면 {"topics": [...]} 같이 감싸진 케이스 처리
    if isinstance(obj, dict):
        if "topics" in obj and isinstance(obj["topics"], list):
            obj = obj["topics"]
        else:
            raise ValueError("JSON object does not contain 'topics' list")

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
        except Exception:
            base_score = 1.0

        topics.append(
            {
                "title": title,
                "description": desc,
                "base_score": base_score,
            }
        )
    return topics

    def _load_with_fallback(s: str) -> Any:
        try:
            return json.loads(s)
        except json.JSONDecodeError:
            # fallback: 첫 번째 완전한 객체만 잘라서 시도
            start = s.find("{")
            if start == -1:
                raise

            brace = 0
            in_string = False
            escape = False
            end = None

            for i, ch in enumerate(s[start:], start):
                if escape:
                    escape = False
                    continue
                if ch == "\\":
                    escape = True
                    continue
                if ch == '"':
                    in_string = not in_string
                    continue
                if in_string:
                    continue
                if ch == "{":
                    brace += 1
                elif ch == "}":
                    brace -= 1
                    if brace == 0:
                        end = i
                        break

            if end is None:
                raise

            single = s[start : end + 1]
            return json.loads(single)

    try:
        obj = _load_with_fallback(cleaned)
    except Exception as e:  # noqa: BLE001
        logger.warning("LLM JSON decode 실패: %s | raw=%r", e, raw[:300])
        raise ValueError("Invalid JSON from LLM") from e

    # dict 래퍼 대응
    if isinstance(obj, dict):
        if isinstance(obj.get("items"), list):
            obj = obj["items"]
        elif isinstance(obj.get("topics"), list):
            obj = obj["topics"]
        else:
            # 단일 객체인 경우 리스트로 감싸서 처리
            obj = [obj]

    if not isinstance(obj, list):
        raise ValueError("LLM output is not a list")

    topics: List[Dict[str, Any]] = []
    for item in obj:
        if not isinstance(item, dict):
            continue

        title = str(item.get("title") or "").strip()
        if not title:
            continue

        desc = str(
            item.get("description")
            or item.get("summary")
            or ""
        ).strip()

        if "base_score" in item:
            base_score_raw = item.get("base_score", 1.0)
        else:
            base_score_raw = item.get("score", 1.0)

        try:
            base_score = float(base_score_raw)
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
    payload = _build_prompt_payload(
        user=user,
        categories=categories,
        input_keyword=input_keyword,
        resources=resources,
        trend_info=trend_info,
        num_topics=num_topics,
    )

    user_message = json.dumps(payload, ensure_ascii=False, indent=2)

    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"아래 JSON 정보를 참고해서 글감 {num_topics}개를 만들어라.\n"
        "- 반드시 JSON 배열만 출력해라.\n"
        "- 코드블록, 설명, 앞뒤 자연어를 절대 쓰지 마라.\n\n"
        f"{user_message}"
    )

    raw = _call_ollama_generate(prompt, timeout=30)
    topics = _parse_topics_json(raw)

    if not topics:
        raise ValueError("LLM returned empty topic list")

    return topics

