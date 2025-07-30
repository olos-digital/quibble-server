# Quibble AI Backend README

## Overview

Quibble AI is a FastAPI-based backend application designed for media content generation, automatisation and seamless integrations with social media platforms such as LinkedIn and X (Twitter).

For interactive exploration, access the OpenAPI docs at `/docs` or `/redoc` once the server is running.

## Prerequisites

- Python 3.12+
- pip for installing dependencies
- A `.env` file for environment variables (see below)
- Optional: Docker for containerized deployment


## Installation

1. Clone the repository:

```
git clone <repository-url>
cd quibble-ai-backend
```

2. Create a virtual environment:

```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```
pip install -r requirements.txt
```


## Running the Application

- Development mode (with auto-reload):

```
uvicorn main:app --reload --env-file .env
```


The server will be available at `http://127.0.0.1:8000`.

## Environment Variables

Environment variables are loaded from a `.env` file (use `python-dotenv` if needed). They configure database connections, security, and social media integrations. Below is a brief explanation of each:

- **SECRET_KEY**: A unique secret for JWT signing (e.g., a random string). Required for token security; generate with `openssl rand -hex 32`.
- **DATABASE_URL**: Database connection string (e.g., `sqlite:///./app.db` for SQLite, or `postgresql://user:pass@localhost/db` for Postgres). Defaults to local SQLite.
- **X_CONSUMER_KEY**: X (Twitter) API consumer key for app authentication.
- **X_CONSUMER_SECRET**: X (Twitter) API consumer secret.
- **X_ACCESS_TOKEN**: X (Twitter) access token for user-level actions.
- **X_ACCESS_TOKEN_SECRET**: X (Twitter) access token secret.
- **X_BEARER_TOKEN**: X (Twitter) bearer token for certain API calls (optional for some endpoints).
- **LI_CLIENT_ID**: LinkedIn app client ID for OAuth.
- **LI_CLIENT_SECRET**: LinkedIn app client secret.
- **LI_ACCESS_TOKEN**: Initial LinkedIn access token (for testing; refreshed automatically).
- **LI_REFRESH_TOKEN**: LinkedIn refresh token for long-lived access.
- **LI_ACCESS_TOKEN_EXPIRES**: Timestamp (epoch seconds) when the access token expires.
- **LI_REDIRECT_URI**: Callback URL for LinkedIn OAuth (e.g., `http://127.0.0.1:8000/linkedin/callback`).
- **LI_OWNER_URN**: LinkedIn owner's URN (e.g., `urn:li:person:ID`) for post authorship.

**Note**: Never commit `.env` to version control. Use secure secret management (e.g., AWS Secrets Manager) in production.

### Base URL

- Development: `http://127.0.0.1:8000`
- Production: (Configure as needed)


### Error Responses

Common errors:

- 400 Bad Request: Invalid input or duplicate data.
- 401 Unauthorized: Missing or invalid token.
- 403 Forbidden: Insufficient permissions (e.g., not post owner).
- 404 Not Found: Resource not available.
- 500 Internal Server Error: Unexpected issues (check logs).