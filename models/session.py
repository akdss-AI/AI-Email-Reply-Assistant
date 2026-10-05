from sqlalchemy import Column,Integer,String,ForeignKey
from datetime import datetime
from sqlalchemy import DateTime
from sqlalchemy.orm import relationship
from database import Base
class Session(Base):
    __tablename__='sessions'
    id=Column(Integer,primary_key=True,index=True)
    user_id=Column(Integer,ForeignKey('users.id') , nullable=False)
    created_at=Column(DateTime , default= datetime.utcnow)
    updated_at=Column(DateTime , default= datetime.utcnow, onupdate=datetime.utcnow)
    user=relationship('User',back_populates='sessions')
    messages = relationship('Message', back_populates='session')