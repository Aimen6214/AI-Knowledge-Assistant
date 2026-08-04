from sqlalchemy import DateTime, Column, Integer, String, ForeignKey
from database.database import Base
from datetime import datetime
from sqlalchemy.orm import relationship

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Foreign key to the User model  
    title = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship with User
    user = relationship(
        "User",
        back_populates="conversations"
    )

    # Relationship with Message
    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan"
    )
