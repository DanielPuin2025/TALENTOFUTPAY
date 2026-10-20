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
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

RUN mkdir -p /data /app/initial-uploads \
    && cp -an /app/static/img/. /app/initial-uploads/ \
    && rm -rf /app/static/img/* \
    && chmod 755 /usr/local/bin/docker-entrypoint.sh

EXPOSE 5000

ENTRYPOINT ["sh", "/usr/local/bin/docker-entrypoint.sh"]
