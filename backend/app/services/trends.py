# app/services/trends.py
from functools import lru_cache
import logging
import time
import threading

from pytrends.request import TrendReq

logger = logging.getLogger(__name__)

# 전역 pytrends 인스턴스 + 락
pytrends_lock = threading.Lock()
pytrends = TrendReq(hl="ko-KR", tz=540)


@lru_cache(maxsize=256)
def get_trend_score(
    keyword: str,
    geo: str = "KR",
    # 'today 1-m' : 지난 30일 기준
    timeframe: str = "today 1-m",
) -> float:
    """
    Google Trends에서 keyword의 최근 관심도(0~100)를 반환.

    - 빈 키워드, 에러, 데이터 없음: 0.0
    - LRU 캐시로 중복 요청 최소화
    - 429 에러 방지를 위해 Lock + sleep(2) 적용
    """
    keyword = (keyword or "").strip()
    if not keyword:
        return 0.0

    with pytrends_lock:
        try:
            # 요청 간 간격 확보
            time.sleep(2)

            pytrends.build_payload(
                [keyword],
                cat=0,
                timeframe=timeframe,
                geo=geo,
                gprop="",  # 웹 검색
            )
            df = pytrends.interest_over_time()
            if df is None or df.empty or keyword not in df.columns:
                return 0.0

            series = df[keyword].dropna()
            if series.empty:
                return 0.0

            value = float(series.iloc[-1])
            value = max(0.0, min(100.0, value))
            return value
        except Exception as e:
            logger.warning("get_trend_score error for %s: %s", keyword, e)
            return 0.0
