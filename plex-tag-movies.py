import os
import urllib.parse
import time
from collections import Counter
from plexapi.server import PlexServer
from dotenv import load_dotenv

load_dotenv()

# Configuration
PLEX_IP = os.getenv('PLEX_IP')
PLEX_PORT = os.getenv('PLEX_PORT')
PLEX_TOKEN = os.getenv('PLEX_TOKEN')
DEBUG = os.getenv('DEBUG') == '1'
PRUEBA = os.getenv('PRUEBA') == '1'
BIBLIOTECAS= os.getenv('BIBLIOTECAS')
BORRAR_TAGS= os.getenv('BORRAR_TAGS')

def debug_log(message):
    if DEBUG:
        print(f"DEBUG: {message}")

# Leer y procesar las bibliotecas desde variables de entorno
bibliotecas = []
if BIBLIOTECAS:
    # Manejar correctamente las comillas y espacios
    bibliotecas = [
        lib.strip().strip('"\'') 
        for lib in BIBLIOTECAS.split(',')
        if lib.strip()
    ]

debug_log(f"Leyendo bibliotecas del .env: {bibliotecas}")

# Parse tags to delete
tags_to_delete = []
if BORRAR_TAGS:
    tags_to_delete = [
        tag.strip().strip('"\'') 
        for tag in BORRAR_TAGS.split(',')
        if tag.strip()
    ]
    debug_log(f"Tags a borrar: {tags_to_delete}")

baseurl = f'http://{PLEX_IP}:{PLEX_PORT}'

def delete_tags_from_movie(movie, tags):
    """Delete specified tags from a movie"""
    try:
        existing_tags = [tag.tag for tag in movie.labels]
        for tag in tags:
            if tag in existing_tags:
                movie.removeLabel(tag)
                debug_log(f"Eliminada etiqueta '{tag}' de la película: {movie.title}")
    except Exception as e:
        debug_log(f"Error borrando etiquetas de {movie.title}: {str(e)}")

def process_libraries():
    try:
        plex = PlexServer(baseurl, PLEX_TOKEN)
        debug_log(f"Conectado a Plex server en {baseurl}")
        
        if not bibliotecas:
            print("Error: No hay bibliotecas configuradas en BIBLIOTECAS")
            return
            
        # Add validation of configured libraries
        available_libraries = [lib.title for lib in plex.library.sections()]
        debug_log(f"Bibliotecas configuradas para procesar: {bibliotecas}")
        
        invalid_libraries = [lib for lib in bibliotecas if lib not in available_libraries]
        if invalid_libraries:
            print(f"Error: Las siguientes bibliotecas no están disponibles en Plex: {invalid_libraries}")
            return
            
        video_codecs = Counter()
        total_movies = 0
        
        for library_name in bibliotecas:
            library = plex.library.section(library_name.strip())
            debug_log(f"Procesando biblioteca: {library_name}")
            
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
                                debug_log(f"Video codec for {movie.title}: {media.videoCodec.upper()}")
                            else:
                                # Obtener el codec actual y las etiquetas existentes
                                current_codec_tag = f"Codec-{media.videoCodec.upper()}"
                                movie.reload()  # Forzar actualización de datos
                                existing_tags = [tag.tag for tag in movie.labels]
                                codec_tags = [tag for tag in existing_tags if tag.startswith('Codec-')]
                                
                                debug_log(f"\n=====================================")
                                debug_log(f"Película: {movie.title}")
                                debug_log(f"Codec detectado: {media.videoCodec.upper()}")
                                debug_log(f"Etiqueta necesaria: {current_codec_tag}")
                                debug_log(f"Etiquetas existentes: {codec_tags}")
                                
                                # Gestión de etiquetas
                                try:
                                    if not codec_tags:
                                        movie.addLabel(current_codec_tag)
                                        debug_log(f"ACCIÓN: Añadida primera etiqueta -> {current_codec_tag}")
                                    elif current_codec_tag not in codec_tags:
                                        # Eliminar etiquetas antiguas una por una
                                        for tag in codec_tags:
                                            debug_log(f"ACCIÓN: Eliminando etiqueta -> {tag}")
                                            movie.removeLabel(tag)
                                            time.sleep(1)  # Pequeña pausa
                                            movie.reload()  # Recargar el estado
                                            
                                            # Verificar que la etiqueta se eliminó
                                            current_tags = [t.tag for t in movie.labels if t.tag.startswith('Codec-')]
                                            if tag in current_tags:
                                                debug_log(f"ERROR: No se pudo eliminar la etiqueta {tag}")
                                                continue
                                                
                                        # Añadir nueva etiqueta solo si se eliminaron las anteriores
                                        current_tags = [t.tag for t in movie.labels if t.tag.startswith('Codec-')]
                                        if not current_tags:
                                            movie.addLabel(current_codec_tag)
                                            debug_log(f"ACCIÓN: Añadida nueva etiqueta -> {current_codec_tag}")
                                        else:
                                            debug_log(f"ERROR: No se pudieron eliminar todas las etiquetas antiguas: {current_tags}")
                                    else:
                                        debug_log(f"ACCIÓN: Ninguna - Etiqueta correcta")
                                    
                                    # Verificación final
                                    time.sleep(1)  # Pequeña pausa
                                    movie.reload()
                                    final_tags = [tag.tag for tag in movie.labels if tag.tag.startswith('Codec-')]
                                    debug_log(f"Estado final: {final_tags}")
                                    debug_log(f"=====================================\n")
                                    
                                except Exception as e:
                                    debug_log(f"ERROR en {movie.title}: {str(e)}")
                
                except Exception as e:
                    debug_log(f"Error procesando película: {str(e)}")
                    continue
            
            debug_log(f"Total películas en {library_name}: {movies_in_library}")
        
        print("\n=== RESUMEN ===")
        print(f"Total películas procesadas: {total_movies}")
        
        if not tags_to_delete:
            print("\nCódecs de Video:")
            for codec, count in video_codecs.most_common():
                print(f"{codec}: {count}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    process_libraries()
