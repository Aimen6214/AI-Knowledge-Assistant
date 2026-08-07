from sqlalchemy.orm import Session
from models.messages import Message  # Import here to avoid circular import issues

def save_message(db: Session, conversation_id: int, role: str, content: str):
    new_message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message

def get_messages(db: Session, conversation_id: int):
    return db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at).all()