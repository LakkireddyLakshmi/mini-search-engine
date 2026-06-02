FROM python:3.12-slim

WORKDIR /app

# Install dependencies first so Docker layer caching speeds up rebuilds.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY searchengine ./searchengine
COPY data ./data
COPY static ./static

# Hosts inject the port via $PORT; default to 8000 for local `docker run`.
ENV PORT=8000
# Serve the 5k-article Wikipedia corpus in production.
ENV CORPUS_PATH=/app/data/wiki.jsonl
EXPOSE 8000

CMD ["sh", "-c", "uvicorn searchengine.api:app --host 0.0.0.0 --port ${PORT}"]
