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

RUN mkdir -p /data /app/static/img/creadoras /app/initial-creadoras \
    && cp -an /app/static/img/creadoras/. /app/initial-creadoras/ \
    && rm -rf /app/static/img/creadoras \
    && ln -s /data/creadoras /app/static/img/creadoras

EXPOSE 5000

CMD ["sh", "-c", "set -eu; mkdir -p /data/creadoras; cp -an /app/initial-creadoras/. /data/creadoras/; exec gunicorn --workers 2 --bind 0.0.0.0:${PORT:-5000} app:app"]
