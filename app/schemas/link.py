from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Schema for incoming request — what user sends
class LinkCreate(BaseModel):
    original_url: str
    custom_alias: Optional[str] = None  # user can customize short key
    expire_date: Optional[datetime] = None  # optional expiry

# Schema for response — what we return to user
class LinkResponse(BaseModel):
    short_key: str
    original_url: str
    expire_date: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True  # allows reading from SQLAlchemy model