# Backend/services/chat_service.py
from fastapi import HTTPException
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai.chat_models import ChatGoogleGenerativeAIError
from services.prompt import build_prompt
from utils.config import GEMINI_KEY
def generate_response(question, documents, chat_history):
    try:
        chat_model = ChatGoogleGenerativeAI(
            model="gemini-3.5-flash",
            google_api_key=GEMINI_KEY,
            temperature=0.2
        )

        prompt=build_prompt(question,documents, chat_history)
        response = chat_model.invoke(prompt)
        return response.content
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