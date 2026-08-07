from sqlalchemy import DateTime, Column, Integer, String, ForeignKey
from database.database import Base
from datetime import datetime
from sqlalchemy.orm import relationship

class DocChunk(Base):
    __tablename__ = "doc_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)  # Foreign key to the Document model
    content = Column(String, nullable=False)
    embedding_reference = Column(String, nullable=False)  # Reference to the embedding in the vector database
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship with Document
    document = relationship(
        "Document",
        back_populates="chunks"
    )