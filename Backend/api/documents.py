import os
from typing import List
from fastapi import APIRouter, Depends, File, HTTPException, status, UploadFile
from sqlalchemy.orm import Session

from database.dependencies import get_db
from models.documents import Document
from auth.dependencies import get_current_user
from models.users import User
from schemas.documents import DocumentResponse

from services.doc_loader import load_document
from services.chunking import chunk_documents
from services.save_chunks import save_chunks_to_db
from services.embedding import get_embeddings
from services.vector_db import create_chroma_db, delete_from_chroma_db
from services.format_filesize import format_size
from utils.hash import calculate_file_hash

router = APIRouter(prefix="/documents", tags=["Documents"])


# =============================================================================
# 1. GET ALL USER DOCUMENTS (FIXES 404 NOT FOUND)
# =============================================================================
@router.get(
    "/list",
    response_model=List[DocumentResponse]
)
async def list_docs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns all uploaded documents for the authenticated user.
    """
    documents = (
        db.query(Document)
        .filter(Document.user_id == current_user.id)
        .order_by(Document.id.desc())
        .all()
    )
    return documents


# =============================================================================
# 2. UPLOAD & INDEX DOCUMENT
# =============================================================================
@router.post(
    "/upload",
    response_model=DocumentResponse
)
async def upload_doc(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    file_bytes = await file.read()
    
    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty (0 bytes)."
        )

    file_hash = calculate_file_hash(file_bytes)

    # 1. Check for existing duplicate document in DB
    existing_document = (
        db.query(Document)
        .filter(
            Document.user_id == current_user.id,
            Document.file_hash == file_hash
        )
        .first()
    )
    
    # NOTE: If file exists, return 409 Conflict or existing doc
    if existing_document:
        return existing_document

    upload_folder = "uploads"
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, file.filename)

    # Save file temporarily to disk
    with open(file_path, "wb") as f:
        f.write(file_bytes)

    formatted_size = format_size(len(file_bytes))

    # 2. Stage new document in SQL (Flush to get ID)
    new_document = Document(
        user_id=current_user.id,
        file_name=file.filename,
        file_type=file.content_type or "application/octet-stream",
        file_path=file_path,
        file_size=formatted_size,
        file_hash=file_hash
    )
    db.add(new_document)
    db.flush()  # Generates new_document.id without committing to DB

    try:
        # 3. Load & Validate Document Text Content
        loaded_docs = load_document(file_path)

        if not loaded_docs:
            raise ValueError("No text could be extracted from this document. (Is it a scanned image PDF?)")

        doc_author = "Unknown"
        if loaded_docs:
            doc_author = (
                loaded_docs[0].metadata.get("author")
                or loaded_docs[0].metadata.get("pdf:author")
                or "Unknown"
            )

        chunks = chunk_documents(loaded_docs)

        if not chunks:
            raise ValueError("Document yielded 0 text chunks during processing.")

        for index, chunk in enumerate(chunks, start=1):
            chunk.metadata["document_id"] = new_document.id
            chunk.metadata["chunk_id"] = index
            chunk.metadata["user_id"] = current_user.id
            chunk.metadata["file_name"] = file.filename
            chunk.metadata["file_type"] = file.content_type
            chunk.metadata["file_size"] = formatted_size

            raw_page = chunk.metadata.get("page")
            chunk.metadata["page"] = (raw_page + 1) if isinstance(raw_page, int) else 1
            chunk.metadata["author"] = (
                chunk.metadata.get("author")
                or chunk.metadata.get("pdf:author")
                or doc_author
            )

        # 4. Save chunks to SQL DB
        save_chunks_to_db(chunks, new_document.id, db)

        # 5. Generate Embeddings & Save to Vector Store
        embeddings = get_embeddings()
        create_chroma_db(chunks, embeddings)

        # 6. ALL STEPS SUCCEEDED -> Commit transaction
        db.commit()
        db.refresh(new_document)

        return new_document

    except Exception as err:
        # ROLLBACK ON FAILURE: Delete broken SQL record and disk file
        db.rollback()
        if os.path.exists(file_path):
            os.remove(file_path)

        err_msg = str(err)
        print(f"DOCUMENT UPLOAD ERROR: {err_msg}")

        # Rate limit handling
        if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg or "quota" in err_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Embedding API rate limit reached. Please wait 60 seconds before re-uploading."
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process document: {err_msg}"
        )


# =============================================================================
# 3. DELETE DOCUMENT BY ID
# =============================================================================
@router.delete("/{document_id}", status_code=status.HTTP_200_OK)
async def delete_doc(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = (
        db.query(Document)
        .filter(Document.id == document_id, Document.user_id == current_user.id)
        .first()
    )

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete physical file
    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    # Delete from ChromaDB vector store
    try:
        delete_from_chroma_db(document_id)
    except Exception as e:
        print(f"ChromaDB Deletion Warning: {e}")

    # Delete from SQL
    db.delete(doc)
    db.commit()

    return {"message": "Document deleted successfully"}