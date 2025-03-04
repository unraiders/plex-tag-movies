FROM python:3.11-alpine

LABEL maintainer="unraiders"
LABEL description="Actualiza la etiqueta de la película en Plex con información del códec de vídeo"

ARG VERSION=2.1.0
ENV VERSION=${VERSION}

# Instalar cron y otros paquetes
RUN apk add --no-cache dcron mc

WORKDIR /app

COPY entrypoint.sh .
RUN chmod +x /app/entrypoint.sh

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY utils.py .

COPY plex-tag-movies.py .

ENTRYPOINT ["/app/entrypoint.sh"]
