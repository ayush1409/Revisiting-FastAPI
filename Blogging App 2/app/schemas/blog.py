from pydantic import BaseModel
from datetime import datetime
from app.schemas.user import UserResponse

class BlogBase(BaseModel):
    title: str
    content: str
    is_draft: bool = True

class BlogCreate(BlogBase):
    pass

class BlogUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    is_draft: bool | None = None

class BlogResponse(BlogBase):
    id: int
    author_id: int
    published_at: datetime | None = None
    created_at: datetime
    updated_at: datetime | None = None
    author: UserResponse

    class Config:
        from_attributes = True
