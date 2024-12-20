import os
import urllib.parse
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
                                codec_tag = f"Codec-{media.videoCodec.upper()}"
                                existing_tags = [tag.tag for tag in movie.labels]
                                
                                # Si ya existe el codec tag correcto, no hacer nada
                                if codec_tag in existing_tags:
                                    debug_log(f"Etiqueta {codec_tag} ya existe en {movie.title}, saltando...")
                                    continue
                                    
                                # Solo si no existe el codec tag correcto, eliminar viejos y añadir nuevo
                                codec_tags = [tag for tag in existing_tags if tag.startswith('Codec-')]
                                for old_tag in codec_tags:
                                    movie.removeLabel(old_tag)
                                movie.addLabel(codec_tag)
                                debug_log(f"Actualizada etiqueta a {codec_tag} en {movie.title}")
                
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
