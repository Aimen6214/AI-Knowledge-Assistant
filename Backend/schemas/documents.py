from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class DocumentResponse(BaseModel):
    id: int
    user_id: int
    file_name: str
    file_type: str
    file_path: str
    file_size: Optional[str] = "Unknown"  # <-- Allows null/missing values safely
    created_at: Optional[datetime] = None  # <-- Optional to prevent date parsing crashes

    model_config = ConfigDict(from_attributes=True)