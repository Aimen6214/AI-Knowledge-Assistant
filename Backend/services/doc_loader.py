import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredWordDocumentLoader

def load_document(file_path: str):
    loader = { ".pdf": PyPDFLoader, ".txt": TextLoader, ".docx": UnstructuredWordDocumentLoader }
    _, file_extension = os.path.splitext(file_path)
    if file_extension.lower() in loader:
        return loader[file_extension.lower()](file_path).load()
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")