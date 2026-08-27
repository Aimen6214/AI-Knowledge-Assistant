from fastapi import HTTPException
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai.chat_models import ChatGoogleGenerativeAIError
from services.prompt import build_prompt
from utils.config import GEMINI_KEY


def format_documents_with_metadata(documents) -> str:
    """
    Formats retrieved documents (LangChain Document objects, dicts, or strings)
    into a unified context string with clear metadata headers for the LLM.
    """
    if not documents:
        return "No relevant context found."

    if isinstance(documents, str):
        return documents

    formatted_chunks = []

    for i, doc in enumerate(documents, start=1):
        # Case 1: LangChain Document Object
        if hasattr(doc, "page_content"):
            content = doc.page_content
            metadata = getattr(doc, "metadata", {}) or {}

            source = (
                metadata.get("file_name")
                or metadata.get("source")
                or "Unknown Document"
            )
            author = (
                metadata.get("author")
                or metadata.get("pdf:author")
                or "Not Specified"
            )
            page = metadata.get("page") or metadata.get("page_number") or "N/A"
            file_size = metadata.get("file_size") or ""

            size_str = f" | Size: {file_size}" if file_size else ""

            chunk_text = (
                f"[Document Chunk {i}]\n"
                f"• Source File: {source}{size_str}\n"
                f"• Author: {author}\n"
                f"• Page: {page}\n"
                f"• Content:\n{content}"
            )
            formatted_chunks.append(chunk_text)

        # Case 2: Plain String Chunk
        elif isinstance(doc, str):
            formatted_chunks.append(f"[Document Chunk {i}]\n{doc}")

        # Case 3: Dictionary Chunk
        elif isinstance(doc, dict):
            content = doc.get("page_content") or doc.get("content") or str(doc)
            metadata = doc.get("metadata", {}) or {}
            source = metadata.get("file_name") or metadata.get("source") or "Unknown Document"
            author = metadata.get("author") or "Not Specified"
            page = metadata.get("page") or "N/A"

            chunk_text = (
                f"[Document Chunk {i}]\n"
                f"• Source File: {source}\n"
                f"• Author: {author}\n"
                f"• Page: {page}\n"
                f"• Content:\n{content}"
            )
            formatted_chunks.append(chunk_text)

        else:
            formatted_chunks.append(str(doc))

    return "\n\n---\n\n".join(formatted_chunks)


def generate_response(question, documents, chat_history):
    try:
        chat_model = ChatGoogleGenerativeAI(
            model="gemini-3.5-flash-lite",
            google_api_key=GEMINI_KEY,
            temperature=0.2
        )

        # 1. Format documents context safely into a single string
        formatted_context = format_documents_with_metadata(documents)

        # 2. Build system prompt with context
        prompt = build_prompt(question, formatted_context, chat_history)

        # 3. Invoke LLM
        #print(prompt)
        response = chat_model.invoke(prompt)
        #print(response)
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
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error generating response: {str(e)}"
        )