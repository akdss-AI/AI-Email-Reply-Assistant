from datetime import datetime
from pydantic import BaseModel


class SessionResponse(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime