from datetime import datetime

from pydantic import BaseModel, ConfigDict


class QueryLogResponse(BaseModel):
    id: int
    telegram_user_id: int | None
    telegram_username: str | None
    telegram_first_name: str | None
    telegram_chat_id: int | None
    original_query: str
    normalized_query: str
    question_id: int | None
    category_id: int | None
    response_text: str
    was_answered: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QueryLogListResponse(BaseModel):
    items: list[QueryLogResponse]
    total: int
    page: int
    page_size: int
