from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from database.dependencies import get_db

from models.users import User

from schemas.chat import ChatRequest, ChatResponse
from schemas.conversation import ConversationSummaryResponse, ConversationResponse
from schemas.messages import MessageResponse

from services.convo_title import generate_title
from services.retriever import retrieve_documents
from services.chat_service import generate_response
from services.conversation import save_conversation, get_conversation_by_id, get_conversations_by_user, delete_conversation, search_conversations
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
    try:
        update_title = generate_title(request.question)
    except Exception as e:
        print("TITLE GENERATION ERROR:", e)
        update_title = "New Chat"
    # Create conversation
    conversation = save_conversation(
        db=db,
        user_id=current_user.id,
        title=update_title
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
        conversation_id=conversation.id,
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

    if isinstance(answer, list):
        answer = answer[0]["text"]
    # Save assistant response
    save_message(
        db=db,
        conversation_id=conversation.id,
        role="assistant",
        content=answer
    )

    source_documents = get_source_documents(documents)

    return ChatResponse(
        conversation_id=conversation.id,
        answer=answer,
        source_documents=source_documents
    )

#rename conversation title
@router.post(
    "/{conversation_id}/title",
    response_model=ConversationResponse
)
def rename_chat(
    conversation_id: int,
    title : str,
    db : Session=Depends(get_db),
    current_user:User= Depends(get_current_user)
):
    conversation = get_conversation_by_id(db,conversation_id)

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found."
        )

    if conversation.user_id!=current_user.id:
        raise HTTPException(
                    status_code=403,
                    detail="Access denied."
                )

    conversation.title=title
    db.commit()
    return conversation


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

#search messages
@router.get(
    "/search",
    response_model=list[ConversationSummaryResponse]
)
def search_messages(
    query:str,
    db:Session=Depends(get_db),
    current_user:User=Depends(get_current_user)
):
    conversation=search_conversations(
        db,
        current_user.id,
        query
    )

    return conversation

#get messages of a conversation
@router.get(
    "/{conversation_id}",
    response_model=ConversationResponse
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

#    messages=get_messages(
#        db=db,
#        conversation_id=conversation.id
#   )
    return conversation



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

    

