from langchain_community.vectorstores import Chroma

def create_chroma_db(documents, embeddings, persist_directory="./chroma.db"):
    chroma_db = Chroma.from_documents(documents=documents, embedding=embeddings, persist_directory=persist_directory)
    chroma_db.persist()
    return chroma_db