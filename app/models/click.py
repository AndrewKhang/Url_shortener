import sqlalchemy as db
from app.database import Base



class Click(Base):
    __tablename__ = 'clicks'

    id       = db.Column(db.Integer, primary_key=True, autoincrement=True)
    short_key = db.Column(db.String(50),unique = True, nullable=False, index = True)
    location = db.Column(db.String(100), nullable=True)
    device = db.Column(db.String(500), nullable=True)
    clicked_at = db.Column(db.DateTime, server_default=db.func.now())
    
