from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schemas.topic import TopicBase


class SessionCreate(BaseModel):
    topic_id: UUID
    input_keyword: str | None = None
    use_trend: bool = False
    selected_format: str | None = None


class SessionRead(BaseModel):
    id: UUID
    topic: TopicBase
    input_keyword: str | None = None
    use_trend: bool = False
    selected_format: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

