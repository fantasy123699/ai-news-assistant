from typing import Optional

from pydantic import BaseModel, Field


class NewsSummaryRequest(BaseModel):
    news_id: int = Field(gt=0)


class NewsChatRequest(BaseModel):
    news_id: int = Field(gt=0)
    question: str = Field(min_length=1, max_length=1000)


class RecommendRequest(BaseModel):
    limit: Optional[int] = Field(default=5, ge=1, le=10)


class SiteChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    limit: Optional[int] = Field(default=6, ge=1, le=10)
