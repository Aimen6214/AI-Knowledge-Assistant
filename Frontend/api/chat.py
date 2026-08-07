import requests

from config import BASE_URL


def get_headers(token):
    return {"Authorization": f"Bearer {token}"}


def new_chat(question, token):
    return requests.post(
        f"{BASE_URL}/chat/new",
        json={"question": question},
        headers=get_headers(token)
    )


def continue_chat(conversation_id, question, token):
    return requests.post(
        f"{BASE_URL}/chat/{conversation_id}",
        json={"question": question},
        headers=get_headers(token)
    )


def get_history(token):
    return requests.get(f"{BASE_URL}/chat/history", headers=get_headers(token))


def get_conversation(conversation_id, token):
    return requests.get(f"{BASE_URL}/chat/{conversation_id}", headers=get_headers(token))


def delete_conversation(conversation_id, token):
    return requests.delete(f"{BASE_URL}/chat/{conversation_id}", headers=get_headers(token))


def search_conversations(query, token):
    return requests.get(
        f"{BASE_URL}/chat/search",
        params={"query": query},
        headers=get_headers(token)
    )


def rename_conversation(conversation_id, title, token):
    return requests.post(
        f"{BASE_URL}/chat/{conversation_id}/title",
        params={"title": title},
        headers=get_headers(token)
    )