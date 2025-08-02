FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY .env .

EXPOSE 8000

# Run alembic migrations first, then start uvicorn
CMD alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000 --env-file .env
