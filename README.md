# plex-tag-movies
Actualiza la etiqueta de la película en Plex con información del códec de vídeo.

Mediante una programación de hora definida añadimos o actualizamos el campo "etiquetas" de nuestras películas en Plex a través del acceso API, así podemos realizar un filtro y generar una colección inteligente o una lista de reproducción inteligente por cada uno de los codec de video que tengamos en nuestra biblioteca de Plex.

### Generar colección o lista inteligente en Plex
Para generar la colección o lista nos dirigimos a la biblioteca de Plex y en el desplegable "Todo" vamos a la última opción "Filtros avanzados", seleccionamos etiqueta y es, en el desplegable nos tiene que aparecer las etiquetas disponibles que ha generado el script después de su ejecución, todas ellas empiezan por Codec-

IMPORTANTE: 

- Este script solo funciona con las bibliotecas de Plex que son películas, las series no tienen el campo etiquetas disponible.
- La primera ejecucción dependiendo del tamaño de nuestra biblioteca de Plex se puede alargar en su ejecucción, ten paciencia el acceso mediante API no es un acceso directo a una base de datos donde modificar miles de lineas tomaría un par de segundos.
- Las siguientes ejecuciones ya tardará menos pero igualmente requiere de una comprobación de cada metadato de la película porque la que ayer era Codec-H264 hoy puede ser Codec-AV1 si hemos actualizado la película.
- Te recomiendo dejar programado el script para que se ejecute de madrugada, todo lo nuevo o modificado hoy lo tendrás mañana en tu colección o lista inteligente, Plex inició sus andaduras en el 2010 y todavía a día de hoy no tenemos esa opción disponible, estando ese metadato dentro de la base de datos o en el propio fichero de vídeo. 

## Configuración variables de entorno en fichero .env (renombrar el env-example a .env)

| CLAVE  | NECESARIO | VALOR |
|:------------- |:---------------:| :-------------|
|PLEX_IP |✅| IP Servidor Plex |
|PLEX_PORT |✅| Puerto Servidor Plex |
|PLEX_TOKEN |✅| Plex Autenticación Token, [como obtenerlo](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/) |
|DEBUG |✅| Habilita el modo Debug en el log. (0 = No / 1 = Si) |
|PRUEBA |✅| Habilita el modo Prueba, no realiza ninguna modificación. (0 = No / 1 = Si) |
|BIBLIOTECAS |✅| El nombre de las librerías de Plex separadas por una coma. Ejemplo: Películas,Otros vídeos |
|BORRAR_TAGS |❌| Borrar etiquetas de las películas, colocar el nombre de las etiquetas separadas por una coma. Ejemplo: Codec-H264,Codec-HEVC,Codec-VC1,Codec-AV1 |
|HORA |✅| Hora de ejecución del script|



## Ejemplo docker-compose.yml
```yaml
services:
  plex-tag-movies:
    image: unraiders/plex-tag-movies
    container_name: plex-tag-movies
    restart: unless-stopped
    environment:
      - TZ=Europe/Madrid
    env_file:
      - .env
```

- Recuerda descargar el fichero env-example y renombrarlo a .env para definir las variables de entorno allí.
- Recuerda colocar el fichero .env en la misma ubicación que el fichero docker-compose.yml.

Si quieres saber como se genera un contenedor Docker en Synology [aquí tienes un buen vídeo de como hacerlo](https://youtu.be/iEJGtYO0q70?si=QnlA5Qd17TxfRU0B)

### Instalación plantilla en Unraid.
- Nos vamos a una ventana de terminal en nuestro Unraid, pegamos esta línea y enter:
```sh
wget -O /boot/config/plugins/dockerMan/templates-user/my-plex-tag-movies.xml https://raw.githubusercontent.com/unraiders/plex-tag-movies/refs/heads/main/my-plex-tag-movies.xml
```
- Nos vamos a DOCKER y abajo a la izquierda tenemos el botón "AGREGAR CONTENEDOR" hacemos click y en seleccionar plantilla seleccionamos plex-tag-movies y rellenamos las variables de entrono necesarias, tienes una explicación en cada variable.

---
---

Este es un script desarrollado a carácter personal haciendo uso de la IA, puedes hacer uso de el y modificarlo a tu antojo pero recuerda tener copias de seguridad de tu Plex antes de realizar la primera ejecución, te recomiendo lanzar el script en horario nocturno ya que cuando la biblioteca es extensa se puede alargar su ejecucción, podrás ver cuando ha acabado, en el log del contenedor (no es necesario el modo debug) tendrás un resumen como este.

```log
[Sat Dec 21 13:47:55 CET 2024] Starting entrypoint.sh
[Sat Dec 21 13:47:55 CET 2024] Timezone set to: Europe/Madrid
[Sat Dec 21 13:47:55 CET 2024] Scheduled time set to: 13:50
[Sat Dec 21 13:47:55 CET 2024] Debug: 0
[Sat Dec 21 13:50:25 CET 2024] Time match! Running plex-tag-movies.py at scheduled time: 13:50

=== RESUMEN ===
Total películas procesadas: 3541

Códecs de Video:
H264: 2580
HEVC: 874
VC1: 58
MPEG2VIDEO: 28
AV1: 1
MPEG4: 1
```
