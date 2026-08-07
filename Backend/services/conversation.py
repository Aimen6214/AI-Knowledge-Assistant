from sqlalchemy.orm import Session
from sqlalchemy import or_
from models.conversation import Conversation  # Import here to avoid circular import issues
from models.messages import Message
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


def search_conversations(
        db:Session,
        user_id:int,
        query:str
):
    try:
        # Search in conversation titles OR message content
        conversations = (
            db.query(Conversation)
            .filter(Conversation.user_id == user_id)
            .filter(
                or_(
                    Conversation.title.ilike(f"%{query}%"),
                    Conversation.messages.any(Message.content.ilike(f"%{query}%"))
                )
            )
            .order_by(Conversation.created_at.desc())
            .all()
        )
        
        return conversations
    except Exception as e:
        print(f"Search error: {e}")
        # Fallback: just search by title if message search fails
        conversations = (
            db.query(Conversation)
            .filter(
                Conversation.user_id == user_id,
                Conversation.title.ilike(f"%{query}%")
            )
            .order_by(Conversation.created_at.desc())
            .all()
        )
        return conversations