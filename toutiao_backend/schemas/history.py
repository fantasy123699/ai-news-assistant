from pydantic import BaseModel


class HistoryCreate(BaseModel):
    news_id: int
