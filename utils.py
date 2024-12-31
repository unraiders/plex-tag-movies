import logging
import os
from colorama import Fore, Style, init
from dotenv import load_dotenv

# Inicializar colorama
init(strip=False)  # Asegura que los códigos ANSI no se eliminen en macOS

# Cargar las variables del archivo .env
load_dotenv()

# Leer la variable DEBUG del archivo .env
DEBUG = os.getenv("DEBUG", "0") == "1"

# Definir colores para cada nivel de logging
COLORS = {
    logging.DEBUG: Fore.GREEN,
    logging.INFO: Fore.WHITE,
    logging.WARNING: Fore.YELLOW,
    logging.ERROR: Fore.RED,
    logging.CRITICAL: Fore.RED + Style.BRIGHT,
}

class ColoredFormatter(logging.Formatter):
    def format(self, record):
        # Aplicar color según el nivel del log
        color = COLORS.get(record.levelno, Fore.WHITE)
        record.msg = f"{color}{record.msg}{Style.RESET_ALL}"
        return super().format(record)

def setup_logger(name: str):
    """
    Configura un logger con soporte de colores.
    :param name: Nombre del logger.
    :return: Objeto logger configurado.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)

    # Configurar el handler y el formatter
    handler = logging.StreamHandler()
    formatter = ColoredFormatter("[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)

    # Añadir el handler al logger
    if not logger.hasHandlers():
        logger.addHandler(handler)

    return logger