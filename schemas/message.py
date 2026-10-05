from typing import Optional

from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
    incoming_email: str = Field(min_length=1, max_length=3000)
    instruction: str = Field(min_length=1, max_length=1000)
    tone: str = Field(min_length=1, max_length=50)




class EmailReply(BaseModel):
    in_scope: bool
    subject: str 
    greeting: str 
    body: str 
    closing: str 
    refusal: str 
class AIEmailResult(BaseModel):
    in_scope: Optional[bool] = None
    subject: str | None
    greeting: str | None
    body: str | None
    closing: str | None
    refusal: Optional[str] = None