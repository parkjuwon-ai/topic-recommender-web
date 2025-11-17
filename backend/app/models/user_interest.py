import uuid

from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, func, Float
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base


class UserInterest(Base):
    __tablename__ = "user_interests"

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
    category_id = Column(
        Integer,
        ForeignKey("interest_categories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    weight = Column(Float, nullable=False, default=1.0)

    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

