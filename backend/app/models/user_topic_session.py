import uuid

from sqlalchemy import (
    Column,
    String,
    Boolean,
    TIMESTAMP,
    ForeignKey,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class UserTopicSession(Base):
    __tablename__ = "user_topic_sessions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    topic_id = Column(
        UUID(as_uuid=True),
        ForeignKey("topic_candidates.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    input_keyword = Column(String(1000), nullable=True)
    use_trend = Column(Boolean, nullable=False, default=False)
    selected_format = Column(String(50), nullable=True)  # blog | newsletter 등

    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    topic = relationship("TopicCandidate", back_populates="sessions")

