import os
from fastapi import APIRouter, Depends, File, HTTPException, status, UploadFile
from sqlalchemy.orm import Session #connection to db (operations:crud)
from database.dependencies import get_db
from models.documents import Document
from auth.dependencies import get_current_user
from models.users import User
from schemas.documents import DocumentResponse
from services.doc_loader import load_document
from services.chunking import chunk_documents
from services.save_chunks import save_chunks_to_db
from services.embedding import get_embeddings
from services.vector_db import create_chroma_db


router = APIRouter(prefix="/documents", tags=["Documents"])
@router.post(
    "/upload",
    response_model=DocumentResponse
)
async def upload_doc(file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    upload_folder="uploads"
    os.makedirs(upload_folder, exist_ok=True)
    file_path=os.path.join(upload_folder, file.filename)
    content = await file.read()
    with open(file_path,"wb") as f:
        f.write(content)
    new_document=Document(user_id=current_user.id, file_name=file.filename, file_type=file.content_type, file_path=file_path, file_size=len(content))
    db.add(new_document)
    db.commit()
    db.refresh(new_document)

    # Load the document
    loaded_docs = load_document(file_path)
    # Chunk the document
    chunks = chunk_documents(loaded_docs)
    #metadata for each chunk
    for index, chunk in enumerate(chunks, start=1):
        chunk.metadata["document_id"] = new_document.id
        chunk.metadata["chunk_id"] = index
        chunk.metadata["user_id"] = current_user.id
        chunk.metadata["file_name"] = file.filename
    # Save chunks to database
    save_chunks_to_db(chunks, new_document.id, db)

    #embedding 
    embeddings = get_embeddings()

    # Create Chroma DB
    create_chroma_db(chunks, embeddings)

    return new_document

@router.get("/list")
def list_documents(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    documents = db.query(Document).filter(Document.user_id == current_user.id).all()
    return documents

@router.get("/{document_id}")
def get_document(document_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    document = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    return document

@router.delete("/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    document = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    if os.path.exists(document.file_path):
        os.remove(document.file_path)
    db.delete(document)
    db.commit()
    return {"detail": "Document deleted successfully."}
