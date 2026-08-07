from pydantic import BaseModel
from datetime import datetime

class MessageCreate(BaseModel):
    conversation_id: int
    content: str
    role: str
    
class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    content: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True