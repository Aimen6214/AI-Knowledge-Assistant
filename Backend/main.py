from fastapi import FastAPI, APIRouter

from api.autentication import router as auth_router
from api.documents import router as documents_router
from api.chat import router as chat_router

from database.database import Base, engine

from models.users import User
from models.documents import Document
from models.doc_chunks import DocChunk
from models.conversation import Conversation
from models.messages import Message


Base.metadata.create_all(bind=engine)

app=FastAPI(
    title="AI Knowledge Assistant",
    description="An AI-powered knowledge assistant that allows users to upload documents, ask questions, and receive answers based on the content of those documents.",
    version="1.0.0"
)

app.include_router(auth_router)
app.include_router(documents_router)    
app.include_router(chat_router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Knowledge Assistant API!"}

# To activate venv on PowerShell:
# .\venv\Scripts\Activate.ps1

# To run the project:
# uvicorn main:app --reload