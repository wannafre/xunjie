from sqlalchemy import Column, Integer, String, JSON
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    roles = Column(JSON, nullable=False, default=list)
    avatar = Column(String(255), nullable=True)
    introduction = Column(String(255), nullable=True)
