from app.services.shortener import generate_short_key
from app.schemas.link import LinkResponse, LinkCreate
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.link import Link
from fastapi.responses import RedirectResponse
from datetime import datetime
router = APIRouter(prefix="", tags=["links"])
@router.post("/links",response_model=LinkResponse)
def receive_link(data: LinkCreate, db: Session = Depends(get_db)):
    short_key = generate_short_key(db)
    link = Link(
    original_url=data.original_url,
    short_key=short_key,
    custom_alias=data.custom_alias,
    expire_date=data.expire_date
)
    db.add(link)
    db.commit()                                   # only commit after email sent successfully
    db.refresh(link)
    return link

@router.get("/{short_key}")
def get_link( short_key: str, db: Session = Depends(get_db)):
    link = db.query(Link).filter(Link.short_key == short_key).first()
    if not link:
        raise HTTPException(status_code=404, detail="Invalid link")
    if link.expire_date and link.expire_date < datetime.utcnow():
     raise HTTPException(status_code=410, detail="Gone")
    else:
     return RedirectResponse(link.original_url, status_code=301)