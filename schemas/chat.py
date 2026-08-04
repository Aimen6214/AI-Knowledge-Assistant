from pydantic import BaseModel
class SourceDocument(BaseModel):
    document_id: int
    file_name: str
    
class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str
    source_documents: list[SourceDocument]