def get_source_documents(documents):
    source_documents = []
    seen = set()

    for doc in documents:
        document_id = doc.metadata.get("document_id")
        file_name = doc.metadata.get("file_name", "Unknown")
        page = doc.metadata.get("page", 0)

        if document_id not in seen:
            source_documents.append({
                "document_id": document_id,
                "file_name": file_name,
                "page": page
            })
            seen.add(document_id)

    return source_documents