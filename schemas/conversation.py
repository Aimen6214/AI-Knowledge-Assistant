from pydantic import BaseModel
from datetime import datetime

from schemas.messages import MessageResponse


class ConversationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    created_at: datetime
    messages: list[MessageResponse]  # List of messages associated with the conversation

    class Config:
        from_attributes = True

class ConversationSummaryResponse(BaseModel):
    id: int
    title: str
    created_at: datetime

    class Config:
        from_attributes = True