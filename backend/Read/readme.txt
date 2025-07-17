🔐 What you need for config.py:
ACCESS_TOKEN = "your_long_lived_Access_Token"
AUTHOR_URN = "urn:li:person:your_LinkedIn_ID"

📌 1. ACCESS_TOKEN — your access token
🔹 Where to get it:
Register an app on LinkedIn Developers.

Enable the following products:
✅ Sign In with LinkedIn
✅ Share on LinkedIn

In the Auth section, find your Client ID and Client Secret, and use them to obtain an OAuth access token.

💡 Easy way to get a token manually:
Use Postman or a site like OAuth 2.0 Playground.

First, get a code, then request the access_token via:
https://www.linkedin.com/oauth/v2/accessToken

📌 Required scopes (permissions) when requesting the token:

w_member_social — permission to post content

r_liteprofile — to get your LinkedIn ID (URN)

r_emailaddress — if you need the email address

🆔 2. AUTHOR_URN — your LinkedIn URN (ID)
How to get it:
Run the file get_urn.py:
python get_urn.py
You’ll get something like:
Your LinkedIn URN: urn:li:person:AbCDeFgHiJK12345
That’s what you need to paste into config.py.