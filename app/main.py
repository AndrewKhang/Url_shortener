from fastapi import FastAPI
from app.database import engine, Base
from app.models import link
from app.routes import link

app = FastAPI()
Base.metadata.create_all(bind=engine)

app.include_router(link.router)
@app.get("/")
def root():
    return {"Message":"URL Shortener API"}