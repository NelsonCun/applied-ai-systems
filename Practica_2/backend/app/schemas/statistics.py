from pydantic import BaseModel, Field


class StatisticsSummaryResponse(BaseModel):
    total_queries: int
    answered_queries: int
    unanswered_queries: int
    unique_users: int
    unique_chats: int
    total_categories: int
    total_questions: int
    total_answers: int
    answer_rate: float = Field(ge=0, le=100)


class TopQuestionItem(BaseModel):
    question_id: int
    question_text: str
    category_name: str
    query_count: int


class TopQueryItem(BaseModel):
    normalized_query: str
    sample_query: str
    query_count: int
    answered_count: int
    unanswered_count: int


class CategoryStatisticsItem(BaseModel):
    category_id: int
    category_name: str
    query_count: int
