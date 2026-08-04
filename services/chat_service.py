from langchain_google_genai import ChatGoogleGenerativeAI
from services.prompt import build_prompt

def generate_response(question, documents, chat_history=None):
    model="gemini-3.5-flash"
    chat_model = ChatGoogleGenerativeAI(model=model)
    prompt = build_prompt(question, documents, chat_history)
    response = chat_model.invoke(prompt)
    return response.content