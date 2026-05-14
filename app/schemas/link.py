from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, AnyHttpUrl
# Schema for incoming request — what user sends
class LinkCreate(BaseModel):
    original_url: AnyHttpUrl
    custom_alias: Optional[str] = None  # user can customize short key
    expire_date: Optional[datetime] = None  # optional expiry

# Schema for response — what we return to user
class LinkResponse(BaseModel):
    short_key: str
    original_url: AnyHttpUrl
    expire_date: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True  # allows reading from SQLAlchemy model
