from pydantic import BaseModel, ConfigDict
from datetime import datetime

class DocumentResponse(BaseModel):
    id: int
    user_id: int
    file_name: str
    file_type: str
    file_path: str
    file_size: str 
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)