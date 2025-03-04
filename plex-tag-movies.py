import os
import time
from collections import Counter
from plexapi.server import PlexServer
from dotenv import load_dotenv
from utils import setup_logger
from datetime import datetime

load_dotenv()

# Inicializar el logger
logger = setup_logger(__name__)

# Configuration
PLEX_IP = os.getenv('PLEX_IP')
PLEX_PORT = os.getenv('PLEX_PORT')
PLEX_TOKEN = os.getenv('PLEX_TOKEN')
DEBUG = os.getenv('DEBUG') == '1'
PRUEBA = os.getenv('PRUEBA') == '1'
BIBLIOTECAS= os.getenv('BIBLIOTECAS')
BORRAR_TAGS= os.getenv('BORRAR_TAGS')

# Leer y procesar las bibliotecas desde variables de entorno
bibliotecas = []

if BIBLIOTECAS:
    # Manejar correctamente las comillas y espacios
    bibliotecas = [
        lib.strip().strip('"\'') 
        for lib in BIBLIOTECAS.split(',')
        if lib.strip()
    ]

logger.debug(f"Leyendo bibliotecas del .env: {bibliotecas}")

# Parse tags to delete
tags_to_delete = []
if BORRAR_TAGS:
    tags_to_delete = [
        tag.strip().strip('"\'') 
        for tag in BORRAR_TAGS.split(',')
        if tag.strip()
    ]
    logger.debug(f"Tags a borrar: {tags_to_delete}")

baseurl = f'http://{PLEX_IP}:{PLEX_PORT}'

def delete_tags_from_movie(movie, tags):
    """Delete specified tags from a movie"""
    try:
        existing_tags = [tag.tag for tag in movie.labels]
        for tag in tags:
            if tag in existing_tags:
                movie.removeLabel(tag)
                logger.debug(f"Eliminada etiqueta '{tag}' de la película: {movie.title}")
    except Exception as e:
        logger.error(f"Error borrando etiquetas de {movie.title}: {str(e)}")

def process_libraries():
    start_time = datetime.now()  # Guardar el tiempo inicial
    try:
        plex = PlexServer(baseurl, PLEX_TOKEN)
        logger.debug(f"Conectado a Plex server en {baseurl}")
        
        if not bibliotecas:
            logger.error("Error: No hay bibliotecas configuradas en BIBLIOTECAS")
            return
            
        # Add validation of configured libraries
        available_libraries = [lib.title for lib in plex.library.sections()]
        logger.debug(f"Bibliotecas configuradas para procesar: {bibliotecas}")
        
        invalid_libraries = [lib for lib in bibliotecas if lib not in available_libraries]
        if invalid_libraries:
            logger.error(f"Error: Las siguientes bibliotecas no están disponibles en Plex: {invalid_libraries}")
            return
            
        video_codecs = Counter()
        total_movies = 0
        
        for library_name in bibliotecas:
            library = plex.library.section(library_name.strip())
            logger.debug(f"Procesando biblioteca: {library_name}\n")
            
            all_items = library.all()
            movies_in_library = 0
            
            for movie in all_items:
                if movie.type != 'movie':
                    continue
                
                movies_in_library += 1
                total_movies += 1
                
                try:
                    if tags_to_delete:
                        # Solo ejecutar el borrado de etiquetas
                        delete_tags_from_movie(movie, tags_to_delete)
                    else:
                        # Ejecutar la función original de añadir etiquetas de codec
                        for media in movie.media:
                            video_codecs[media.videoCodec.upper()] += 1
                            
                            if PRUEBA:
                                logger.debug(f"Video codec for {movie.title}: {media.videoCodec.upper()}")
                            else:
                                # Obtener el codec actual y las etiquetas existentes
                                current_codec_tag = f"Codec-{media.videoCodec.upper()}"
                                movie.reload()  # Forzar actualización de datos
                                existing_tags = [tag.tag for tag in movie.labels]
                                codec_tags = [tag for tag in existing_tags if tag.startswith('Codec-')]
                                
                                logger.debug("=====================================")
                                logger.debug(f"Película: {movie.title}")
                                logger.debug(f"Codec detectado: {media.videoCodec.upper()}")
                                logger.debug(f"Etiqueta necesaria: {current_codec_tag}")
                                logger.debug(f"Etiquetas existentes: {codec_tags}")
                                
                                # Gestión de etiquetas
                                try:
                                    if not codec_tags:
                                        movie.addLabel(current_codec_tag)
                                        logger.debug(f"ACCIÓN: Añadida primera etiqueta -> {current_codec_tag}")
                                    elif current_codec_tag not in codec_tags:
                                        # Eliminar etiquetas antiguas una por una
                                        for tag in codec_tags:
                                            logger.debug(f"ACCIÓN: Eliminando etiqueta -> {tag}")
                                            movie.removeLabel(tag)
                                            time.sleep(1)  # Pequeña pausa
                                            movie.reload()  # Recargar el estado
                                            
                                            # Verificar que la etiqueta se eliminó
                                            current_tags = [t.tag for t in movie.labels if t.tag.startswith('Codec-')]
                                            if tag in current_tags:
                                                logger.error(f"ERROR: No se pudo eliminar la etiqueta {tag}")
                                                continue
                                                
                                        # Añadir nueva etiqueta solo si se eliminaron las anteriores
                                        current_tags = [t.tag for t in movie.labels if t.tag.startswith('Codec-')]
                                        if not current_tags:
                                            movie.addLabel(current_codec_tag)
                                            logger.debug(f"ACCIÓN: Añadida nueva etiqueta -> {current_codec_tag}")
                                        else:
                                            logger.error(f"ERROR: No se pudieron eliminar todas las etiquetas antiguas: {current_tags}")
                                    else:
                                        logger.debug("ACCIÓN: Ninguna - Etiqueta correcta")
                                    
                                    # Verificación final
                                    time.sleep(1)  # Pequeña pausa
                                    movie.reload()
                                    final_tags = [tag.tag for tag in movie.labels if tag.tag.startswith('Codec-')]
                                    logger.debug(f"Estado final: {final_tags}")
                                    logger.debug("=====================================\n")
                                    
                                except Exception as e:
                                    logger.error(f"ERROR en {movie.title}: {str(e)}")
                
                except Exception as e:
                    logger.error(f"Error procesando película: {str(e)}")
                    continue
            
            logger.info(f"Total películas en {library_name}: {movies_in_library}")
        
        logger.info("======= RESUMEN =======")
        logger.info(f"Total películas procesadas: {total_movies}")
        
        if not tags_to_delete:
            logger.info("Códecs de Video:")
            for codec, count in video_codecs.most_common():
                logger.info(f"{codec}: {count}")
        
        logger.info("=======================\n")

        end_time = datetime.now()  # Guardar el tiempo final
        elapsed_time = end_time - start_time # Calcular y registrar la diferencia de tiempo
        elapsed_time_str = str(elapsed_time).split('.')[0]  # Quitar la parte de los microsegundos

        logger.info(f"[{time.strftime('%d/%m/%Y %H:%M:%S')}] Proceso finalizado, tiempo empleado {elapsed_time_str} seg.")
        logger.info(f"[{time.strftime('%d/%m/%Y %H:%M:%S')}] Esperando siguiente ejecución...")

    except Exception as e:
        logger.error(f"Error: {str(e)}")

if __name__ == "__main__":
    process_libraries()
