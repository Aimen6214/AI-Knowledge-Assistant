# Backend/services/chat_service.py
from fastapi import HTTPException
from langchain_google_genai.chat_models import ChatGoogleGenerativeAIError

def generate_response(question, documents, chat_history):
    try:
        response = chat_model.invoke(prompt)
        return response
    except ChatGoogleGenerativeAIError as e:
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            raise HTTPException(
                status_code=429,
                detail="Gemini API rate limit reached. Please wait 30 seconds and try again."
            )
        raise HTTPException(
            status_code=500,
            detail=f"Error generating AI response: {str(e)}"
        )