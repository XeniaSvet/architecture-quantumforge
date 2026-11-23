FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install torch --index-url https://pytorch.org && \
    pip install -r requirements.txt

COPY bot.py build_index.py ./
COPY knowledge_base ./knowledge_base
COPY faiss_index ./faiss_index

EXPOSE 8000

CMD ["uvicorn", "bot:app", "--host", "0.0.0.0", "--port", "8000"]
