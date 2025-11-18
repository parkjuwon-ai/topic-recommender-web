from sqlalchemy import (
    Column,
    Integer,
    String,
    TIMESTAMP,
    func,
    ForeignKey,
    SmallInteger,
)
from sqlalchemy.orm import relationship

from app.db.base import Base


class InterestCategory(Base):
    __tablename__ = "interest_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)

    parent_id = Column(Integer, ForeignKey("interest_categories.id"), nullable=True)
    level = Column(SmallInteger, nullable=False)  # 1: 대, 2: 중, 3: 소

    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    parent = relationship(
        "InterestCategory",
        remote_side=[id],
        backref="children",
    )

