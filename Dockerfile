FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# HF Spaces exécute le conteneur en user non-root (uid 1000) :
# /app doit être écrivable (ChromaDB) et HOME défini (cache sentence-transformers)
RUN chmod -R 777 /app
ENV HOME=/app

# Le port 8000 est exposé pour le backend FastAPI
EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
