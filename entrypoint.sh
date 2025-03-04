#!/bin/sh

# Validar que HORA esté definida
if [ -z "$HORA" ]; then
    echo "La variable HORA no está definida en el archivo .env"
    exit 1
fi

# Confirmación de configuración de cron
echo "$(date +'%d-%m-%Y %H:%M:%S') $VERSION - Arrancando entrypoint.sh"
echo "$(date +'%d-%m-%Y %H:%M:%S') Zona horaria: $TZ"
echo "$(date +'%d-%m-%Y %H:%M:%S') Programación cron: $HORA"
echo "$(date +'%d-%m-%Y %H:%M:%S') Debug: $DEBUG"

# Crear una línea para el crontab
CRON_JOB="$HORA python3 /app/plex-tag-movies.py >> /proc/1/fd/1 2>> /proc/1/fd/2"

# Agregar el trabajo al crontab
echo "$CRON_JOB" > /etc/crontabs/root

# Asegurarse de que el archivo de logs existe
touch /var/log/cron.log

# Iniciar cron en segundo plano
echo "Starting cron..."
crond -f -l 2 || { echo "Error starting cron"; exit 1; }