#Model (models/admin.py) → How data is stored in the database.
from sqlalchemy import DateTime, Column, Integer, String
from database.database import Base
from datetime import datetime
from sqlalchemy.orm import relationship

class User(Base): #Base class represents a database table. #Base is the parent class for all database models.
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # One user can own many documents
    documents = relationship(
        "Document",
        back_populates="owner", 
        cascade="all, delete-orphan"  # Ensure that when a user is deleted, their documents are also deleted
    )

    # One user can have many conversations
    conversations = relationship(
        "Conversation",
        back_populates="user",
        cascade="all, delete-orphan"  # Ensure that when a user is deleted, their conversations are also deleted
    )
