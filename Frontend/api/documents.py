import requests

from config import BASE_URL


def get_headers(token):
    return {"Authorization": f"Bearer {token}"}


def upload_document(file, token):
    return requests.post(
        f"{BASE_URL}/documents/upload",
        files={"file": (file.name, file.getvalue(), file.type)},
        headers=get_headers(token)
    )


def get_documents(token):
    return requests.get(f"{BASE_URL}/documents/list", headers=get_headers(token))


def delete_document(document_id, token):
    return requests.delete(f"{BASE_URL}/documents/{document_id}", headers=get_headers(token))