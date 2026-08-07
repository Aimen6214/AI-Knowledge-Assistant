import requests
import streamlit as st

from config import API_URL




# Authentication


def register(name, email, password):
    url = f"{BASE_URL}/auth/register"

    data = {
        "name": name,
        "email": email,
        "password": password
    }

    return requests.post(url, json=data)


def login(email, password):
    url = f"{BASE_URL}/auth/login"

    data = {
        "username": email,
        "password": password
    }

    return requests.post(url, data=data)


# ---------------------------
# Headers
# ---------------------------

def get_headers():
    return {
        "Authorization": f"Bearer {st.session_state.token}"
    }


# ---------------------------
# Documents
# ---------------------------

def upload_document(file):
    url = f"{BASE_URL}/documents/upload"

    files = {
        "file": (
            file.name,
            file.getvalue(),
            file.type
        )
    }

    return requests.post(
        url,
        headers=get_headers(),
        files=files
    )


def get_documents():
    url = f"{BASE_URL}/documents"

    return requests.get(
        url,
        headers=get_headers()
    )


def delete_document(document_id):
    url = f"{BASE_URL}/documents/{document_id}"

    return requests.delete(
        url,
        headers=get_headers()
    )


# ---------------------------
# Chat
# ---------------------------

def new_chat(question):
    url = f"{BASE_URL}/chat/new"

    return requests.post(
        url,
        headers=get_headers(),
        json={
            "question": question
        }
    )


def continue_chat(conversation_id, question):
    url = f"{BASE_URL}/chat/{conversation_id}"

    return requests.post(
        url,
        headers=get_headers(),
        json={
            "question": question
        }
    )


def get_history():
    url = f"{BASE_URL}/chat/history"

    return requests.get(
        url,
        headers=get_headers()
    )


def get_messages(conversation_id):
    url = f"{BASE_URL}/chat/{conversation_id}"

    return requests.get(
        url,
        headers=get_headers()
    )


def delete_chat(conversation_id):
    url = f"{BASE_URL}/chat/{conversation_id}"

    return requests.delete(
        url,
        headers=get_headers()
    )


def rename_chat(conversation_id, title):
    url = f"{BASE_URL}/chat/{conversation_id}/title"

    return requests.post(
        url,
        headers=get_headers(),
        params={
            "title": title
        }
    )


def search_chat(query):
    url = f"{BASE_URL}/chat/search"

    return requests.get(
        url,
        headers=get_headers(),
        params={
            "query": query
        }
    )