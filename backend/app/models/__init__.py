# app/models/__init__.py
"""
모델 모듈 진입점.

- Base: SQLAlchemy declarative base
- User, InterestCategory, UserInterest, TopicCandidate, UserTopicSession: 개별 모델들
"""

from app.db.base import Base  # Base를 여기서도 노출
from app.models.user import User
from app.models.interest_category import InterestCategory
from app.models.user_interest import UserInterest
from app.models.topic_candidate import TopicCandidate
from app.models.user_topic_session import UserTopicSession

__all__ = [
    "Base",
    "User",
    "InterestCategory",
    "UserInterest",
    "TopicCandidate",
    "UserTopicSession",
]

