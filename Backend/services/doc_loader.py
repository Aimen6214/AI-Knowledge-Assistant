import os
from langchain_community.document_loaders import (
    PyMuPDFLoader,  # Replaced PyPDFLoader
    TextLoader,
    UnstructuredWordDocumentLoader,
)

def load_document(file_path: str):
    # PyMuPDFLoader uses MuPDF under the hood (far superior font & layout parsing)
    loader = {
        ".pdf": PyMuPDFLoader,
        ".txt": TextLoader,
        ".docx": UnstructuredWordDocumentLoader,
    }
    
    _, file_extension = os.path.splitext(file_path)
    ext = file_extension.lower()
    
    if ext in loader:
        return loader[ext](file_path).load()
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")