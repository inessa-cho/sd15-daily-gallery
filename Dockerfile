FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    HF_HOME=/app/model-cache/huggingface \
    TRANSFORMERS_CACHE=/app/model-cache/huggingface \
    TZ=Asia/Seoul
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 tzdata && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY config.py generator.py subjects.json ./
CMD ["python", "generator.py"]
