from sqlalchemy import Column,Integer,String,ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy import DateTime
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
class Message(Base):
    __tablename__='messages'
    id=Column(Integer,primary_key=True,index=True)
    session_id=Column(Integer,ForeignKey('sessions.id'),nullable=False)
    content=Column(JSONB,nullable=False)
    role=Column(String,nullable=False)
    created_at=Column(DateTime , default= datetime.utcnow)
    
    session=relationship('Session',back_populates='messages')