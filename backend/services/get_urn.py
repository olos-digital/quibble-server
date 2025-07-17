import requests
from backend.config.config import ACCESS_TOKEN

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

response = requests.get("https://api.linkedin.com/v2/me", headers=headers)

if response.status_code == 200:
    data = response.json()
    print("LinkedIn URN:", f"urn:li:person:{data['id']}")
else:
    print("Error:", response.status_code)
    print(response.text)