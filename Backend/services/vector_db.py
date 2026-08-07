from langchain_community.vectorstores import Chroma

from services.embedding import get_embeddings

def create_chroma_db(documents, embeddings, persist_directory="./chroma.db"):



    chroma_db = Chroma.from_documents(documents=documents, embedding=embeddings, persist_directory=persist_directory)
    chroma_db.persist()
    return chroma_db

def delete_from_chroma_db(document_id, persist_directory="./chroma.db"):
    embeddings = get_embeddings()
    chroma_db = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    chroma_db.delete(where={"document_id": document_id})
