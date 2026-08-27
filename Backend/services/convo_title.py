from google import genai

from utils.config import GEMINI_KEY

client = genai.Client(api_key=GEMINI_KEY)


def generate_title(question: str):

    prompt = f"""
Generate a very short conversation title.

Rules:
- Maximum 5 words
- No quotation marks
- No punctuation
- Only return the title

Question:
{question}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text.strip()