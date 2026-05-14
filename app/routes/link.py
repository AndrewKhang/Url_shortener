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
from datetime import datetime, timedelta
from fastapi import BackgroundTasks


router = APIRouter(prefix="", tags=["links"])

@router.post("/links",response_model=LinkResponse)
def receive_link(data: LinkCreate, request : Request,db: Session = Depends(get_db)):
      # Get client IP
    ip = request.client.host
    
    # Redis key for this IP
    rate_key = f"rate:{ip}"
    
# Atomic rate limit check using Lua script
    lua_script = """
    local count = redis.call('INCR', KEYS[1])
    if count == 1 then
    redis.call('EXPIRE', KEYS[1], 3600)
    end
    return count
    """
    count = cache.connection.eval(lua_script, 1, rate_key)
    if count > 10:
        raise HTTPException(status_code=429, detail="Too many requests")
    # Check how many requests this IP made
    if data.custom_alias:
        existing = db.query(Link).filter(Link.short_key == data.custom_alias).first()
        if existing:
             raise HTTPException(status_code=409, detail="Alias already exists")
        short_key = data.custom_alias
    else:
        short_key = generate_short_key(db)
    if not data.expire_date:
        expire_date = datetime.utcnow() + timedelta(days=30)
    else:
        expire_date = data.expire_date
    link = Link(
        original_url=str(data.original_url),
        short_key=short_key,
        custom_alias=data.custom_alias,
        expire_date=expire_date
    )
    db.add(link)
    db.commit()                               # only commit after email sent successfully
    db.refresh(link)
    return link

def sync_click_count(short_key:str,db: Session):
    count = cache.connection.get(f"clicks:{short_key}")
    if count:
        db.query(Link).filter(Link.short_key == short_key).update(
                {"click_count": int(count)}
        )
        db.commit()
@router.get("/{short_key}")
def get_link(request: Request, short_key: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    ua = parse(request.headers.get("user-agent", ""))
    device = f"{ua.browser.family} on {ua.os.family}"
    click = Click(
    short_key=short_key,
    device=device,
    location=get_location(request.client.host)  
)
    cache_url= cache.connection.get(short_key)
    if cache_url:
        cache.connection.incr(f"clicks:{short_key}")
        db.add(click)
        db.commit()
        background_tasks.add_task(sync_click_count,short_key,db)
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
     background_tasks.add_task(sync_click_count,short_key,db)
     return RedirectResponse(link.original_url, status_code=301)

