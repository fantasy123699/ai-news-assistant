from typing import Optional

from pydantic import BaseModel


class NewsSummaryRequest(BaseModel):
    news_id: int


class NewsChatRequest(BaseModel):
    news_id: int
    question: str


class RecommendRequest(BaseModel):
    limit: Optional[int] = 5


class SiteChatRequest(BaseModel):
    message: str
    limit: Optional[int] = 6
