# Yangi Samarqand — Telegram bot (aiogram 2)
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app
RUN useradd --create-home --uid 1000 bot

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY --chown=bot:bot . .
USER bot

CMD ["python", "app.py"]
