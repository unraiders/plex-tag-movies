FROM python:3.11-alpine

LABEL maintainer="unraiders"
LABEL version="1.0.0"
LABEL description="Actualiza la etiqueta de la película en Plex con información del códec de vídeo"

# Create non-root user
RUN addgroup -S plexapp && adduser -S plexapp -G plexapp

WORKDIR /app

COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY plex-tag-movies.py .

# Change ownership
RUN chown -R plexapp:plexapp /app

USER plexapp

ENTRYPOINT ["/app/entrypoint.sh"]
