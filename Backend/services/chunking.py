from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_documents(documents, chunk_size=1000, chunk_overlap=200):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    # 1. Split documents into chunks
    chunks = text_splitter.split_documents(documents)

    # 2. Enrich chunk content with contextual metadata
    for chunk in chunks:
        # Get page number (PyMuPDFLoader uses 0-indexed page numbers)
        raw_page = chunk.metadata.get("page", 0)
        page_num = raw_page + 1 if isinstance(raw_page, int) else raw_page
        
        # Get filename or source path
        source = chunk.metadata.get("file_name", chunk.metadata.get("source", "Document"))
        
        # Prepend context header directly into the text for vector search
        header = f"[Document: {source} | Page {page_num}]\n"
        if hasattr(chunk, "page_content"):
            chunk.page_content = header + chunk.page_content
        else:
            chunk.page_content = header

    return chunks