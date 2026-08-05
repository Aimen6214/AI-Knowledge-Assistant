from datetime import datetime

from pydantic import BaseModel
class SourceDocument(BaseModel):
    document_id: int
    file_name: str
    page: int
    
class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str
    source_documents: list[SourceDocument]

