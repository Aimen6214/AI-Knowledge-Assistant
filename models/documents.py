#Model (models/document.py) → How data is stored in the database.
from sqlalchemy import DateTime, Column, Integer, String, ForeignKey
from database.database import Base
from datetime import datetime
from sqlalchemy.orm import relationship
class Document(Base): #Base class represents a database table. #Base is the parent class for all database models.
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Foreign key to the User model
    file_name = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)  
    file_path = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    # Relationship with User
    owner = relationship(
        "User",
        back_populates="documents"
    )

    chunks = relationship(
        "DocChunk",
        back_populates="document",
        cascade="all, delete-orphan",
        lazy="noload"  # Prevents automatic loading of chunks when querying documents
    )
