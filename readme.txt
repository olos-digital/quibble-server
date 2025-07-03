🔐 Что нужно для config.py:
ACCESS_TOKEN = "ваш_долгоживущий_Access_Token"
AUTHOR_URN = "urn:li:person:ваш_LinkedIn_ID"
📌 1. ACCESS_TOKEN — ваш токен доступа
🔹 Где взять:
Зарегистрируйте приложение на LinkedIn Developers.

Включите продукты:
✅ Sign In with LinkedIn
✅ Share on LinkedIn

В разделе Auth найдите Client ID, Client Secret, и используйте их для получения OAuth Access Token.

💡 Удобный способ получить токен (вручную):
Перейди в Postman или на сайт вроде OAuth 2.0 Playground.

Получи code, затем запроси access_token через https://www.linkedin.com/oauth/v2/accessToken.

📌 Scopes (права), которые нужно указать при получении токена:

w_member_social — разрешение на публикации

r_liteprofile — получить LinkedIn ID (URN)

r_emailaddress — если нужно email

🆔 2. AUTHOR_URN — ваш LinkedIn URN (ID)
Как получить:
Запусти файл get_urn.py:

python get_urn.py
Ты получишь что-то вроде:

Ваш LinkedIn URN: urn:li:person:AbCDeFgHiJK12345
Это и нужно вставить в config.py.