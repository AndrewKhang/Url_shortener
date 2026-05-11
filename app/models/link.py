import sqlalchemy as db
from app.database import Base



class Link(Base):
    __tablename__ = 'links'

    id       = db.Column(db.Integer, primary_key=True, autoincrement=True)
    original_url = db.Column(db.String(2048),  nullable=False)
    short_key = db.Column(db.String(50),unique = True,  nullable=False, index = True)
    custom_alias = db.Column(db.String(50),  nullable=True)
    expire_date = db.Column(db.DateTime, nullable=True)
    click_count = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    
