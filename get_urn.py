import requests
from config import ACCESS_TOKEN

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

response = requests.get("https://api.linkedin.com/v2/me", headers=headers)

if response.status_code == 200:
    data = response.json()
    print("линкедин URN:", f"urn:li:person:{data['id']}")
else:
    print("Ошибка:", response.status_code)
    print(response.text)