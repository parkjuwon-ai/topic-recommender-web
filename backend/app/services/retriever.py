# app/services/retriever.py
from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict, Any, Sequence

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "resources_bookend.json"


def _load_resources() -> List[Dict[str, Any]]:
    if not DATA_PATH.exists():
        return []
    with DATA_PATH.open(encoding="utf-8") as f:
        return json.load(f)


RESOURCES: List[Dict[str, Any]] = _load_resources()


def retrieve_resources(
    category_ids: Sequence[int] | None,
    input_keyword: str | None,
    top_k: int = 10,
) -> List[Dict[str, Any]]:
    """
    Day 8용 심플 버전:
    - category_ids가 있으면 해당 카테고리 포함 리소스 우선
    - input_keyword가 있으면 title/description에 포함된 정도로 점수 가산
    - 아직 임베딩은 안 쓰고, 단순 문자열 매칭만 사용
    """
    kw = (input_keyword or "").strip().lower()
    cats = set(category_ids or [])

    scored: List[tuple[float, Dict[str, Any]]] = []

    for r in RESOURCES:
        score = 0.0

        # 카테고리 겹치면 점수 +1
        r_cats = set(r.get("category_ids") or [])
        if cats and r_cats & cats:
            score += 1.0

        # 키워드가 title/description에 들어가면 +1.0
        if kw:
            text = f"{r.get('title','')} {r.get('description','')}".lower()
            if kw in text:
                score += 1.0
            else:
                # 단어 단위 일부라도 겹치면 +0.5
                for token in kw.split():
                    if token and token in text:
                        score += 0.5
                        break

        if score > 0:
            scored.append((score, r))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [r for _, r in scored[:top_k]]

