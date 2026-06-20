from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database.connection import Base

class User(Base):
    __tablename__ = "users"
    id         = Column(Integer, primary_key=True)
    username   = Column(String(50), unique=True)
    email      = Column(String(100), unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
