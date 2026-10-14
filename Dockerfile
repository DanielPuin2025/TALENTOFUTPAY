FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TALENTOFUTPAY_DATABASE_PATH=/data/talentofutpay.db

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY templates/ ./templates/
COPY static/ ./static/

RUN mkdir -p /data

EXPOSE 5000

CMD ["sh", "-c", "exec gunicorn --workers 2 --bind 0.0.0.0:${PORT:-5000} app:app"]
