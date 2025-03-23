from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field



class ArticleCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=10)

class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class ArticleResponse(BaseModel):
    id: int
    title: str
    content: str
    author_name: str
    created_at: datetime
    update_at: Optional[datetime] = None