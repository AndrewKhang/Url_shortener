from urllib import request
from app.services.shortener import generate_short_key,get_location
from app.schemas.link import LinkResponse, LinkCreate
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db 
from app.models.link import Link
from app.models.click import Click
from fastapi.responses import RedirectResponse
from datetime import datetime
from app import cache
from fastapi import Request
from user_agents import parse
router = APIRouter(prefix="", tags=["links"])

@router.post("/links",response_model=LinkResponse)
def receive_link(data: LinkCreate, request : Request,db: Session = Depends(get_db)):
      # Get client IP
    ip = request.client.host
    
    # Redis key for this IP
    rate_key = f"rate:{ip}"
    
    # Check how many requests this IP made
    count = cache.connection.get(rate_key)
    if count and int(count) >= 10:
        raise HTTPException(status_code=429, detail="Too many requests")
    pipe = cache.connection.pipeline()
    pipe.incr(rate_key)
    pipe.expire(rate_key, 3600)  # 1 hour
    pipe.execute()
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
def get_link( request:Request, short_key: str, db: Session = Depends(get_db)):
    ua = parse(request.headers.get("user-agent", ""))
    device = f"{ua.browser.family} on {ua.os.family}"
    click = Click(
    short_key=short_key,
    device=device,
    location=get_location(request.client.host)  # tạm thời, sau thêm geolocation
)
    cache_url= cache.connection.get(short_key)
    if cache_url:
        cache.connection.incr(f"clicks:{short_key}")
        db.add(click)
        db.commit()
        return RedirectResponse(cache_url, status_code=301)
    link = db.query(Link).filter(Link.short_key == short_key).first()
    if not link:
        raise HTTPException(status_code=404, detail="Invalid link")
    if link.expire_date and link.expire_date < datetime.utcnow():
     raise HTTPException(status_code=410, detail="Gone")
    else:
     cache.connection.set(short_key, link.original_url, ex=3600)
     cache.connection.set(f"clicks:{short_key}", 0, ex=3600)
     cache.connection.incr(f"clicks:{short_key}")
     db.add(click)
     db.commit()
     return RedirectResponse(link.original_url, status_code=301)

