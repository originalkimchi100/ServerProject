import requests
import json


def login(email: str, password: str):
    body = {
        "email": email,
        "password": password
    }
    print(body)
    response = requests.post(url="http://127.0.0.1:8000/login", json=body)
    print("dfasf",response.text)
    return json.loads(response.text)["token"]


print(login("originalkimchi100@gmail.com", "gkstjd02@"))



