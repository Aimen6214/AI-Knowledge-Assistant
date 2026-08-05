from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from database.dependencies import get_db

from models.users import User

from schemas.chat import ChatRequest, ChatResponse
from schemas.conversation import ConversationSummaryResponse
from schemas.messages import MessageResponse

from services.retriever import retrieve_documents
from services.chat_service import generate_response
from services.conversation import save_conversation, get_conversation_by_id, get_conversations_by_user, delete_conversation
from services.message_service import save_message, get_messages
from services.source_docs import get_source_documents

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)

@router.post(
    "/new",
    response_model=ChatResponse
)
def new_chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Create conversation
    conversation = save_conversation(
        db=db,
        user_id=current_user.id,
        title=request.question[:40]
    )

    # Save user's first message
    save_message(
        db=db,
        conversation_id=conversation.id,
        role="user",
        content=request.question
    )

    # Retrieve relevant document chunks
    documents = retrieve_documents(
        question=request.question,
        user_id=current_user.id
    )

    # Load chat history
    chat_history = get_messages(
        db=db,
        conversation_id=conversation.id
    )

    # Generate AI response
    answer = generate_response(
        question=request.question,
        documents=documents,
        chat_history=chat_history
    )

    if isinstance(answer, list):
        answer = answer[0]["text"]

    # Save assistant reply
    save_message(
        db=db,
        conversation_id=conversation.id,
        role="assistant",
        content=answer
    )

    # Extract source documents
    source_documents = get_source_documents(documents)
    return ChatResponse(
        answer=answer,
        source_documents=source_documents
    )

#Continue Existing Conversation

@router.post(
    "/{conversation_id}",
    response_model=ChatResponse
)
def continue_chat(
    conversation_id: int,
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    conversation = get_conversation_by_id(
        db=db,
        conversation_id=conversation_id
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found."
        )

    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Access denied."
        )

    # Save user's message
    save_message(
        db=db,
        conversation_id=conversation.id,
        role="user",
        content=request.question
    )

    # Retrieve document chunks
    documents = retrieve_documents(
        question=request.question,
        user_id=current_user.id
    )

    # Load previous messages
    chat_history = get_messages(
        db=db,
        conversation_id=conversation.id
    )

    # Generate response
    try:
        answer = generate_response(
            question=request.question,
            documents=documents,
            chat_history=chat_history
        )
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="The AI service is currently experiencing high traffic. Please try again in a few moments."
        )

    # Save assistant response
    save_message(
        db=db,
        conversation_id=conversation.id,
        role="assistant",
        content=answer
    )

    source_documents = get_source_documents(documents)

    return ChatResponse(
        answer=answer,
        source_documents=source_documents
    )

#HISTORY OF CONVERSATIONS
@router.get(
    "/history",
    response_model=list[ConversationSummaryResponse]
)
def history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conversations = get_conversations_by_user(
        db=db,
        user_id=current_user.id
    )
    return conversations

#get messages of a conversation
@router.get(
    "/{conversation_id}",
    response_model=list[MessageResponse]
)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conversation = get_conversation_by_id(
        db=db,
        conversation_id=conversation_id
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found."
        )

    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Access denied."
        )

    messages=get_messages(
        db=db,
        conversation_id=conversation.id
    )
    return messages

#Delete a conversation
@router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_conversation_endpoint(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    success = delete_conversation(
        db=db,
        conversation_id=conversation_id,
        user_id=current_user.id
    )

    if not success:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found or access denied."
        )

    



