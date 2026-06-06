from pydantic import BaseModel


class FavoriteCreate(BaseModel):
    news_id: int
