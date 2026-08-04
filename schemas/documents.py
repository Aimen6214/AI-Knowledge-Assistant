from pydantic import BaseModel
from datetime import datetime

class DocumentResponse(BaseModel):
    id: int
    user_id: int
    file_name: str
    file_type: str
    file_path: str
    file_size: int 
    created_at: datetime

    class Config:
        from_attributes = True