from models.doc_chunks import DocChunk
from sqlalchemy.orm import Session

def save_chunks_to_db(chunks, document_id, db: Session):
    for index, chunk in enumerate(chunks):
        new_chunk = DocChunk(
            document_id=document_id,
            content=chunk.page_content,
            embedding_reference = f"doc_{document_id}_chunk_{index}",
        )
        db.add(new_chunk)
    db.commit()