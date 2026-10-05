
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy import DateTime
from datetime import datetime
from database import Base
class User(Base):
    __tablename__='users'
    id=Column(Integer,primary_key=True,index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at=Column(DateTime , default= datetime.utcnow)
    sessions=relationship('Session',back_populates='user')