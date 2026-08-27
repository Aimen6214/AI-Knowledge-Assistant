
def build_prompt(question, documents, chat_history=None):
    context = ""
    for doc in documents:
        # print(doc)
        # if hasattr(doc, "page_content"):
        #     context+=doc.page_content + "\n"
        # else:
        #     context+= "\n"
        context+=doc

    history_text = ""
    for message in chat_history:
        history_text += f"{message.role}: {message.content}\n"
    prompt=f"""
        You are an AI Knowledge Assistant.

Answer the user's question ONLY using from the provided document.

Use your own knowledge also, like use common sense if user asks something similar to the context of the documents.

See for yourself the author and publish date of the documents incase user asks for it. Author name and publish date of doc is usually writen below the title and on frist page of the document.

If user specifies source doc then answer only from the specified document.

If the answer is not available in the context, reply:

"I couldn't find that information in the uploaded documents."

Always give a clear and complete answer.



Previous conversation history:
{history_text}

Context:
{context}

Question:
{question}

Answer:
"""

    return prompt
