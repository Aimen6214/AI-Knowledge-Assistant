from langchain_community.vectorstores import Chroma
from services.embedding import get_embeddings

def create_chroma_db(chunks, embeddings, persist_directory="./chroma.db"):
    # 1. Initialize Chroma with Cosine Similarity metric
    chroma_db = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings,
        collection_metadata={"hnsw:space": "cosine"}
    )
    
    # 2. Build IDs that match the SQL embedding_reference (doc_{id}_chunk_{chunk_id})
    ids = [
        f"doc_{chunk.metadata['document_id']}_chunk_{chunk.metadata['chunk_id']}"
        for chunk in chunks
    ]
    
    # 3. Add documents with explicit IDs (automatically persisted in modern Chroma)
    chroma_db.add_documents(documents=chunks, ids=ids)
    
    return chroma_db

def delete_from_chroma_db(document_id, persist_directory="./chroma.db"):
    embeddings = get_embeddings()
    chroma_db = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    
    # Deletes all chunks matching the document_id metadata
    chroma_db.delete(where={"document_id": document_id})

def search_chroma_db(query: str, document_id: int = None, k: int = 4, persist_directory="./chroma.db"):
    """
    Helper function to search Chroma with optional document filtering.
    """
    embeddings = get_embeddings()
    chroma_db = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    
    # Filter by specific document if needed
    search_kwargs = {"k": k}
    if document_id:
        search_kwargs["filter"] = {"document_id": document_id}
        
    return chroma_db.similarity_search(query, **search_kwargs)