import os

import requests

# Headers: configured with Bearer authentication for LinkedIn API calls.
headers = {
    "Authorization": f"Bearer {os.getenv("ACCESS_TOKEN")}"
}


# API request: fetches user profile data from LinkedIn's /me endpoint to derive the URN.
response = requests.get("https://api.linkedin.com/v2/me", headers=headers)


if response.status_code == 200:
    # Success handling: parses the JSON response and constructs the URN from the user ID.
    data = response.json()
    print("LinkedIn URN:", f"urn:li:person:{data['id']}")
else:
    # Error handling: prints status code and response text for debugging API failures.
    print("Error:", response.status_code)
    print(response.text)
