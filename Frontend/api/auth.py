import requests

from config import BASE_URL


def login(email, password):
    return requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": email, "password": password}
    )


def register(username, email, password):
    return requests.post(
        f"{BASE_URL}/auth/register",
        json={"username": username, "email": email, "password": password}
    )