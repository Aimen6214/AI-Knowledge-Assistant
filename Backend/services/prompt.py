
def build_prompt(question, documents, chat_history=None):
    context = ""
    for doc in documents:
        context+=doc.page_content + "\n"

    history_text = ""
    for message in chat_history:
        history_text += f"{message.role}: {message.content}\n"
    prompt=f"""
        You are an AI Knowledge Assistant.

Answer the user's question ONLY using the provided context.

Whenever the user upload documents, you should retrieve the name of the author and date of the publication of the document and include it in your answer.

If the answer is not available in the context, reply:

"I couldn't find that information in the uploaded documents."

Always give a clear and concise answer.

Do not hallucinate or make up information.

Previous conversation history:
{history_text}

Context:
{context}

Question:
{question}

Answer:
"""

    return prompt
