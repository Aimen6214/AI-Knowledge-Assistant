from sqlalchemy.orm import Session
from models.conversation import Conversation  # Import here to avoid circular import issues

def save_conversation(db: Session, user_id: int, title:str):

    new_conversation = Conversation(
        user_id=user_id,
        title=title
    )
    db.add(new_conversation)
    db.commit()
    db.refresh(new_conversation)
    return new_conversation

def get_conversation_by_id(db: Session, conversation_id: int):
    return db.query(Conversation).filter(Conversation.id == conversation_id).first()

def get_conversations_by_user(db: Session, user_id: int):
    return db.query(Conversation).filter(Conversation.user_id == user_id).all()

def delete_conversation(
    db: Session,
    conversation_id: int,
    user_id: int
):
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        .first()
    )

    if not conversation:
        return False

    db.delete(conversation)
    db.commit()

    return True