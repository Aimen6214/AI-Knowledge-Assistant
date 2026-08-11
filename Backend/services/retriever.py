from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

def retrieve_documents(
    question,
    user_id,
    document_id=None,
    vector_db="./chroma.db",
    k=10
):
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vector_db = Chroma(
        persist_directory=vector_db,
        embedding_function=embeddings
    )

    if document_id is not None:
        results = vector_db.similarity_search(
            question,
            k=k,
            filter={
                "user_id": user_id,
                "document_id": document_id
            }
        )
    else:
        results = vector_db.similarity_search(
            question,
            k=k,
            filter={
                "user_id": user_id
            }
        )
        

    print("\n========== RETRIEVED CHUNKS ==========")

    for i, doc in enumerate(results):
        print(f"\n--- CHUNK {i + 1} ---")
        print("METADATA:", doc.metadata)
        print("CONTENT:")
        print(doc.page_content[:1500])

    print("======================================\n")



    return results