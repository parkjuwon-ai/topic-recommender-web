# app/models/topic_candidate.py
import uuid

from sqlalchemy import Column, String, Integer, TIMESTAMP, ForeignKey, func, Float  # 🔹 Float 추가
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base


class TopicCandidate(Base):
    __tablename__ = "topic_candidates"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    title = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)

    # 관심사 카테고리 (선택)
    category_id = Column(
        Integer,
        ForeignKey("interest_categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # trend | bookend | munch | mock 등
    source_type = Column(String(50), nullable=False, default="mock")

    # 예: Google Trends / Bookend / Munch 연동 정보 등
    source_meta = Column(JSONB, nullable=True)

    # 🔹 Day7: 트렌드 점수(0~100 원본)
    trend_score = Column(Float, nullable=True)

    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    sessions = relationship(
        "UserTopicSession",
        back_populates="topic",
        cascade="all, delete-orphan",
    )

